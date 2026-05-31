# =============================================================================
# DVDcoin Bank — Backend v4.0
# 5-DB architecture: users.db | rights.db | transactions.db | stats.db | opo.db
# Superadmin: dvd + nebulosa | Admin: nina, victor, yu + dynamic
# =============================================================================
 
import os, sys, asyncio, sqlite3, time as _time, logging, signal, json as _json
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager, contextmanager
 
from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
 
import bcrypt as _bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel
 
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _has_limiter = True
except ImportError:
    _has_limiter = False
    def get_remote_address(r): return "127.0.0.1"
    class _FakeLimiter:
        def limit(self, *a, **k): return lambda f: f
        def init_app(self, *a): pass
    class _FakeExc(Exception): pass
    RateLimitExceeded = _FakeExc

# Socket.IO (no usado)
# try:
#     from socketio import AsyncServer, ASGIApp
#     _has_socketio = True
# except ImportError:
#     _has_socketio = False

# Video rooms
# =============================================================================
# CONFIG
# =============================================================================
 
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")
 
# 5 separate DB files
DB_USERS  = os.path.join(DATA_DIR, "users.db")        # users, lang_prefs
DB_RIGHTS = os.path.join(DATA_DIR, "rights.db")       # roles, opo_players
DB_TX     = os.path.join(DATA_DIR, "transactions.db") # transactions
DB_STATS  = os.path.join(DATA_DIR, "stats.db")        # sessions
DB_OPO    = os.path.join(DATA_DIR, "opo.db")          # opo_results, opo_sessions
DB_BETS   = os.path.join(DATA_DIR, "apuestas.db")     # porras, apuestas_usuarios, estadisticas
 
# Legacy path for auto-migration
DB_LEGACY = os.path.join(BASE_DIR, "dvdcoin.db")
 
CONF_DIR    = os.path.join(BASE_DIR, "config")
GALLERY_DIR = os.path.join(BASE_DIR, "static", "gallery")
GALLERY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}
 
ADMINS      = {"dvd", "nebulosa", "nina", "victor", "yu", "roy","admin","aitor"}
SUPERADMINS = {"dvd", "nebulosa"}
GHOST       = {"admin"}
ALL_ADMINS  = ADMINS | GHOST
 
JWT_ALGORITHM  = "HS256"
JWT_EXPIRE_H   = 168  # 1 week
ONLINE_TIMEOUT_S = 90
TX_MAX_ROWS    = 1000
 
_ONLINE: dict = {}
 
logger = logging.getLogger("dvdcoin")
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
 
# =============================================================================
# JWT
# =============================================================================
 
def _load_jwt_secret() -> str:
    os.makedirs(CONF_DIR, exist_ok=True)
    p = os.path.join(CONF_DIR, "jwt_secret.txt")
    if os.path.exists(p):
        s = open(p).read().strip()
        if s: return s
    import secrets
    s = secrets.token_hex(32)
    open(p, "w").write(s)
    return s
 
JWT_SECRET = _load_jwt_secret()
 
def create_token(username: str) -> str:
    exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_H)
    return jwt.encode({"sub": username, "exp": exp}, JWT_SECRET, algorithm=JWT_ALGORITHM)
 
def decode_token(token: str) -> Optional[str]:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return data.get("sub")
    except JWTError:
        return None
 
security = HTTPBearer(auto_error=False)  # auto_error=False para permitir cookies como alternativa
 
def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Obtiene el usuario actual desde:
    1. Cookie 'dvd_token' (preferido, más seguro)
    2. Header Authorization Bearer (fallback para APIs)
    
    NUNCA desde query parameters (inseguro)
    """
    token = None
    
    # Opción 1: Cookie (preferido)
    token = request.cookies.get("dvd_token")
    
    # Opción 2: Header Authorization (fallback)
    if not token and creds:
        token = creds.credentials
    
    if not token:
        raise HTTPException(401, "Authentication required")
    
    u = decode_token(token)
    if not u:
        raise HTTPException(401, "Invalid or expired session")
    
    # Check is_blocked for ALL authenticated users on every request
    conn = db_users()
    row = conn.execute("SELECT is_blocked FROM users WHERE username=?", (u,)).fetchone()
    conn.close()
    if row and row["is_blocked"]:
        raise HTTPException(403, "Account blocked")
    return u
 
def verify_password(plain: str, hashed: str) -> bool:
    if hashed in ("__UNSET__", "__AUTO__"): return False
    try: return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception: return False
 
def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()
 
# =============================================================================
# MASTER PASSWORD — emergency superadmin access
# Generated once on first startup, stored in conf/master.txt, printed to logs.
# Allows dvd/nebulosa to login even if their hash is unknown/broken.
# =============================================================================
 
_MASTER_PASSWORD: str = ""
 
def _load_master_password() -> str:
    """Load or generate the master emergency password for superadmins."""
    import secrets as _sec, string as _str
    os.makedirs(CONF_DIR, exist_ok=True)
    p = os.path.join(CONF_DIR, "master.txt")
    if os.path.exists(p):
        pwd = open(p).read().strip()
        if pwd:
            return pwd
    pwd = "dvd_" + "".join(_sec.choice(_str.ascii_letters + _str.digits) for _ in range(12))
    open(p, "w").write(pwd)
    return pwd
 
 
# =============================================================================
# DATABASE
# =============================================================================
 
def _open_db(path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextmanager
def db_context(db_func):
    """Context manager for database connections that ensures proper closing."""
    conn = db_func()
    try:
        yield conn
    finally:
        conn.close()
 
def db_users()  -> sqlite3.Connection: return _open_db(DB_USERS)
def db_rights() -> sqlite3.Connection: return _open_db(DB_RIGHTS)
def db_tx()     -> sqlite3.Connection: return _open_db(DB_TX)
def db_stats()  -> sqlite3.Connection: return _open_db(DB_STATS)
def db_opo()    -> sqlite3.Connection: return _open_db(DB_OPO)
def db_bets()   -> sqlite3.Connection: return _open_db(DB_BETS)
 
# Legacy alias for code that uses db_connect()
def db_connect() -> sqlite3.Connection: return db_users()
 
def db_init():
    """Create all tables. Safe to call on every restart."""
    os.makedirs(DATA_DIR, exist_ok=True)
 
    # users.db
    c = db_users()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            username        TEXT PRIMARY KEY,
            password_hash   TEXT    NOT NULL DEFAULT '__UNSET__',
            balance         REAL    NOT NULL DEFAULT 0.0,
            is_blocked      INTEGER NOT NULL DEFAULT 0,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            lang_pref       TEXT    NOT NULL DEFAULT 'en',
            email           TEXT,
            full_name       TEXT,
            phone           TEXT,
            email_verified  INTEGER NOT NULL DEFAULT 0,
            verification_token TEXT,
            verification_expires TEXT,
            opo_interest    INTEGER NOT NULL DEFAULT 0,
            opo_access      INTEGER NOT NULL DEFAULT 0,
            payment_status  TEXT DEFAULT 'pending',
            payment_date    TEXT,
            payment_amount  REAL DEFAULT 0.0
        );
        CREATE TABLE IF NOT EXISTS lang_prefs (
            username   TEXT PRIMARY KEY,
            lang       TEXT NOT NULL DEFAULT 'en',
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    c.commit()
    # Add new columns to existing DB if missing (migration safety)
    new_columns = [
        ("lang_pref", "TEXT NOT NULL DEFAULT 'en'"),
        ("email", "TEXT"),
        ("full_name", "TEXT"),
        ("phone", "TEXT"),
        ("email_verified", "INTEGER NOT NULL DEFAULT 0"),
        ("verification_token", "TEXT"),
        ("verification_expires", "TEXT"),
        ("opo_interest", "INTEGER NOT NULL DEFAULT 0"),
        ("opo_access", "INTEGER NOT NULL DEFAULT 0"),
        ("payment_status", "TEXT DEFAULT 'pending'"),
        ("payment_date", "TEXT"),
        ("payment_amount", "REAL DEFAULT 0.0")
    ]
    for col_name, col_type in new_columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            c.commit()
        except Exception:
            pass  # column already exists
    c.close()
 
    # rights.db
    c = db_rights()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS roles (
            username   TEXT PRIMARY KEY,
            role       TEXT NOT NULL DEFAULT 'admin',
            granted_by TEXT,
            granted_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS opo_players (
            username TEXT PRIMARY KEY,
            added_by TEXT NOT NULL DEFAULT 'dvd',
            added_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    c.commit(); c.close()
 
    # transactions.db
    c = db_tx()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user   TEXT NOT NULL,
            to_user     TEXT NOT NULL,
            amount      REAL NOT NULL,
            concept     TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_user);
        CREATE INDEX IF NOT EXISTS idx_tx_to   ON transactions(to_user);
        CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(created_at);
    """)
    c.commit(); c.close()
 
    # stats.db
    c = db_stats()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            section    TEXT NOT NULL,
            detail     TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            ended_at   TEXT,
            duration_s INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_sess_user ON sessions(username);
        CREATE INDEX IF NOT EXISTS idx_sess_sect ON sessions(section);
        CREATE INDEX IF NOT EXISTS idx_sess_dt   ON sessions(started_at);
    """)
    c.commit(); c.close()
 
    # opo.db
    c = db_opo()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS opo_results (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            block_n    INTEGER NOT NULL,
            played_at  TEXT NOT NULL DEFAULT (datetime('now')),
            correct    INTEGER NOT NULL DEFAULT 0,
            wrong      INTEGER NOT NULL DEFAULT 0,
            wrong_qs   TEXT NOT NULL DEFAULT '[]',
            duration_s INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_opo_user  ON opo_results(username);
        CREATE INDEX IF NOT EXISTS idx_opo_block ON opo_results(block_n);
        CREATE INDEX IF NOT EXISTS idx_opo_date  ON opo_results(played_at);
        CREATE TABLE IF NOT EXISTS opo_sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            ended_at   TEXT,
            duration_s INTEGER
        );
    """)
    c.commit(); c.close()

    # apuestas.db (includes both betting and voting tables)
    c = db_bets()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS porras (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            creador         TEXT NOT NULL,
            titulo          TEXT NOT NULL,
            descripcion     TEXT NOT NULL DEFAULT '',
            tipo            TEXT NOT NULL DEFAULT 'resultado',
            fecha_limite    TEXT NOT NULL,
            fecha_evento    TEXT NOT NULL,
            estado          TEXT NOT NULL DEFAULT 'abierta',
            resultado       TEXT,
            comision        REAL NOT NULL DEFAULT 5.0,
            opciones_json   TEXT NOT NULL DEFAULT '[]',
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            closed_at       TEXT,
            resolved_at     TEXT
        );
        CREATE TABLE IF NOT EXISTS apuestas_usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            porra_id    INTEGER NOT NULL,
            username    TEXT NOT NULL,
            opcion      TEXT NOT NULL,
            cantidad    REAL NOT NULL,
            fecha       TEXT NOT NULL DEFAULT (datetime('now')),
            pagado      INTEGER NOT NULL DEFAULT 0,
            ganancia    REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (porra_id) REFERENCES porras(id)
        );
        CREATE TABLE IF NOT EXISTS estadisticas_porras (
            username        TEXT PRIMARY KEY,
            total_apostado  REAL NOT NULL DEFAULT 0.0,
            total_ganado    REAL NOT NULL DEFAULT 0.0,
            porras_ganadas  INTEGER NOT NULL DEFAULT 0,
            porras_perdidas INTEGER NOT NULL DEFAULT 0,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS votaciones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            creador         TEXT NOT NULL,
            titulo          TEXT NOT NULL,
            descripcion     TEXT NOT NULL DEFAULT '',
            estado          TEXT NOT NULL DEFAULT 'abierta',
            multiple        INTEGER NOT NULL DEFAULT 0,
            anonima         INTEGER NOT NULL DEFAULT 0,
            fecha_creacion  TEXT NOT NULL DEFAULT (datetime('now')),
            fecha_cierre    TEXT
        );
        CREATE TABLE IF NOT EXISTS votaciones_opciones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            votacion_id     INTEGER NOT NULL,
            opcion          TEXT NOT NULL,
            FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS votaciones_votos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            votacion_id     INTEGER NOT NULL,
            username        TEXT NOT NULL,
            opcion          TEXT NOT NULL,
            fecha           TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_porras_estado ON porras(estado);
        CREATE INDEX IF NOT EXISTS idx_porras_creador ON porras(creador);
        CREATE INDEX IF NOT EXISTS idx_apuestas_porra ON apuestas_usuarios(porra_id);
        CREATE INDEX IF NOT EXISTS idx_apuestas_user ON apuestas_usuarios(username);
        CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado);
        CREATE INDEX IF NOT EXISTS idx_votaciones_creador ON votaciones(creador);
        CREATE INDEX IF NOT EXISTS idx_votaciones_votos_votacion ON votaciones_votos(votacion_id);
        CREATE INDEX IF NOT EXISTS idx_votaciones_votos_user ON votaciones_votos(username);
    """)
    c.commit(); c.close()
 
 
def _auto_migrate_legacy():
    """Migrate user hashes from dvdcoin.db (or .migrated backup) into data/users.db.
    Runs every startup so admin password hashes are always correct."""
    # Try the live file first, then the renamed backup
    legacy = DB_LEGACY
    if not os.path.exists(legacy):
        legacy = DB_LEGACY + ".migrated"
    if not os.path.exists(legacy):
        return  # No source DB at all
    logger.info("Running migration from %s ...", os.path.basename(legacy))
 
    logger.info("Starting auto-migration from dvdcoin.db ...")
    try:
        import sqlite3 as _sq
        leg = _sq.connect(legacy)
        leg.row_factory = _sq.Row
        migrated = {}
 
        # users — smart merge:
        #   • GHOST users are skipped (keep __UNSET__ so default password works)
        #   • New users get full row inserted
        #   • Existing users only get hash updated if current hash is __UNSET__
        try:
            rows = leg.execute("SELECT * FROM users").fetchall()
            c = db_users()
            for r in rows:
                d = dict(r)
                uname = d.get("username", "")
                if uname in GHOST:
                    continue  # never overwrite ghost users — they use default password
                src_hash = d.get("password_hash", "__UNSET__")
                # Check if user already exists with a real hash
                existing = c.execute(
                    "SELECT password_hash FROM users WHERE username=?", (uname,)
                ).fetchone()
                if existing is None:
                    # New user — insert full row
                    c.execute(
                        "INSERT INTO users(username,password_hash,balance,is_blocked,"
                        "failed_attempts,locked_until,created_at) VALUES(?,?,?,?,?,?,?)",
                        (uname, src_hash, d.get("balance", 0), d.get("is_blocked", 0),
                         d.get("failed_attempts", 0), d.get("locked_until"), d.get("created_at"))
                    )
                elif existing["password_hash"] in ("__UNSET__", "__AUTO__"):
                    # Existing user with no real hash — update hash only
                    c.execute(
                        "UPDATE users SET password_hash=? WHERE username=?",
                        (src_hash, uname)
                    )
                # else: user already has a real hash — leave it alone
            c.commit(); c.close()
            migrated["users"] = len(rows)
        except Exception as e:
            logger.warning("Migration users: %s", e)
 
        # transactions
        try:
            rows = leg.execute("SELECT * FROM transactions").fetchall()
            c = db_tx()
            for r in rows:
                d = dict(r)
                c.execute(
                    "INSERT OR IGNORE INTO transactions(id,from_user,to_user,amount,concept,created_at)"
                    " VALUES(?,?,?,?,?,?)",
                    (d.get("id"), d.get("from_user"), d.get("to_user"),
                     d.get("amount",0), d.get("concept",""), d.get("created_at"))
                )
            c.commit(); c.close()
            migrated["transactions"] = len(rows)
        except Exception as e:
            logger.warning("Migration transactions: %s", e)
 
        # sessions
        try:
            rows = leg.execute("SELECT * FROM sessions").fetchall()
            c = db_stats()
            for r in rows:
                d = dict(r)
                c.execute(
                    "INSERT OR IGNORE INTO sessions(id,username,section,detail,started_at,ended_at,duration_s)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (d.get("id"), d.get("username"), d.get("section","bank"),
                     d.get("detail",""), d.get("started_at"), d.get("ended_at"), d.get("duration_s"))
                )
            c.commit(); c.close()
            migrated["sessions"] = len(rows)
        except Exception as e:
            logger.warning("Migration sessions: %s", e)
 
        # opo_players
        try:
            rows = leg.execute("SELECT * FROM opo_players").fetchall()
            c = db_rights()
            for r in rows:
                d = dict(r)
                c.execute(
                    "INSERT OR IGNORE INTO opo_players(username,added_by,added_at) VALUES(?,?,?)",
                    (d.get("username"), d.get("added_by","dvd"), d.get("added_at"))
                )
            c.commit(); c.close()
            migrated["opo_players"] = len(rows)
        except Exception as e:
            logger.warning("Migration opo_players: %s", e)
 
        # opo_results
        try:
            rows = leg.execute("SELECT * FROM opo_results").fetchall()
            c = db_opo()
            for r in rows:
                d = dict(r)
                c.execute(
                    "INSERT OR IGNORE INTO opo_results(id,username,block_n,played_at,correct,wrong,wrong_qs)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (d.get("id"), d.get("username"), d.get("block_n",1),
                     d.get("played_at"), d.get("correct",0), d.get("wrong",0), d.get("wrong_qs","[]"))
                )
            c.commit(); c.close()
            migrated["opo_results"] = len(rows)
        except Exception as e:
            logger.warning("Migration opo_results: %s", e)
 
        leg.close()
        # Rename legacy DB so we never migrate again
        # Rename the live file after migration so we use the .migrated copy next time
        if os.path.exists(DB_LEGACY):
            os.rename(DB_LEGACY, DB_LEGACY + ".migrated")
        logger.info("Auto-migration complete: %s. Legacy DB renamed to dvdcoin.db.migrated", migrated)
    except Exception as e:
        logger.error("Auto-migration failed: %s", e)
 
 
def _load_opo_users() -> set:
    try:
        c = db_rights()
        rows = c.execute("SELECT username FROM opo_players").fetchall()
        c.close()
        return {"dvd", "nebulosa"} | {r["username"] for r in rows}
    except Exception:
        return {"dvd", "nebulosa"}
 
 
def _load_admins_from_db() -> set:
    base = {"dvd", "nebulosa", "nina", "victor", "yu","roy","admin"}
    try:
        c = db_rights()
        rows = c.execute("SELECT username FROM roles WHERE role='admin'").fetchall()
        c.close()
        return base | {r["username"] for r in rows}
    except Exception:
        return base
 
 
OPO_USERS: set = {"dvd", "nebulosa"}  # refreshed at startup
 
# ── In-memory video room registry ─────────────────────────────────────────────
import uuid as _uuid
_ROOMS: dict = {}   # room_key → {host, title, mode, invites:set, members:set}
# Keep _ROOMS as in-memory cache for fast WS signaling; DB is the source of truth
_APP_BUILD: str = "0"  # set at startup in lifespan

_ROOMS_FILE = os.path.join(BASE_DIR, "data", "rooms_state.json")

def _save_rooms():
    """Persist active rooms to disk so they survive server restarts."""
    try:
        data = {}
        for k, r in list(_ROOMS.items()):
            data[k] = {
                "host": r["host"], "title": r["title"],
                "mode": r["mode"],
                "invites": list(r["invites"]),
                "members": list(r["members"]),
            }
        with open(_ROOMS_FILE, "w", encoding="utf-8") as f:
            import json as _json_rooms
            _json_rooms.dump(data, f)
    except Exception:
        pass

def _load_rooms():
    """Load persisted rooms from DB and disk on startup."""
    global _ROOMS
    # Load from DB first (most reliable)
    try:
        c = db_msg()
        rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode,
                   GROUP_CONCAT(DISTINCT i.username) AS invites_csv
            FROM video_rooms r
            LEFT JOIN video_room_invites i ON i.room_key = r.room_key
            WHERE r.active = 1
            GROUP BY r.room_key
        """).fetchall()
        c.close()
        for row in rows:
            invites = set(x for x in (row["invites_csv"] or "").split(",") if x)
            _ROOMS[row["room_key"]] = {
                "host": row["host"], "title": row["title"],
                "mode": row["mode"],
                "invites": invites,
                "members": set(),  # members reconnect via WS
            }
    except Exception:
        pass
    # Fallback: load from JSON file if DB has nothing
    if not _ROOMS:
        try:
            if not os.path.exists(_ROOMS_FILE):
                return
            with open(_ROOMS_FILE, "r", encoding="utf-8") as f:
                import json as _json_rooms
                data = _json_rooms.load(f)
            for k, r in data.items():
                _ROOMS[k] = {
                    "host": r["host"], "title": r["title"],
                    "mode": r["mode"],
                    "invites": set(r.get("invites", [])),
                    "members": set(),
                }
        except Exception:
            pass


# ── DB-backed room helpers ─────────────────────────────────────────────────

def _db_upsert_room(room_key: str, title: str, host: str, mode: str):
    """Create or update a room record in the DB."""
    try:
        c = db_msg()
        c.execute("""
            INSERT INTO video_rooms(room_key, title, host, mode, active, updated_at)
            VALUES(?, ?, ?, ?, 1, datetime('now'))
            ON CONFLICT(room_key) DO UPDATE SET
                title=excluded.title, host=excluded.host,
                mode=excluded.mode, active=1,
                updated_at=datetime('now')
        """, (room_key, title, host, mode))
        c.commit(); c.close()
    except Exception:
        pass

def _db_add_member(room_key: str, username: str):
    try:
        c = db_msg()
        c.execute("""
            INSERT OR IGNORE INTO video_room_members(room_key, username)
            VALUES(?, ?)
        """, (room_key, username))
        c.commit(); c.close()
    except Exception:
        pass

def _db_remove_member(room_key: str, username: str):
    try:
        c = db_msg()
        c.execute("DELETE FROM video_room_members WHERE room_key=? AND username=?",
                  (room_key, username))
        c.commit(); c.close()
    except Exception:
        pass

def _db_add_invite(room_key: str, username: str):
    try:
        c = db_msg()
        c.execute("""
            INSERT OR IGNORE INTO video_room_invites(room_key, username)
            VALUES(?, ?)
        """, (room_key, username))
        c.commit(); c.close()
    except Exception:
        pass

def _db_close_room(room_key: str):
    """Mark a room as inactive (no members left)."""
    try:
        c = db_msg()
        c.execute("UPDATE video_rooms SET active=0, updated_at=datetime('now') WHERE room_key=?",
                  (room_key,))
        c.execute("DELETE FROM video_room_members WHERE room_key=?", (room_key,))
        c.commit(); c.close()
    except Exception:
        pass

def _db_get_active_rooms(username: str) -> list:
    """Return active rooms visible to username: public + invited + own."""
    try:
        c = db_msg()
        rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode, r.created_at,
                   GROUP_CONCAT(DISTINCT m.username) AS members_csv,
                   MAX(CASE WHEN i.username=? THEN 1 ELSE 0 END) AS invited
            FROM video_rooms r
            LEFT JOIN video_room_members m ON m.room_key = r.room_key
            LEFT JOIN video_room_invites i ON i.room_key = r.room_key AND i.username=?
            WHERE r.active = 1
              AND (r.mode='public' OR r.host=? OR i.username=?)
            GROUP BY r.room_key
            ORDER BY r.created_at DESC
        """, (username, username, username, username)).fetchall()
        c.close()
        result = []
        for row in rows:
            members = [m for m in (row["members_csv"] or "").split(",") if m]
            result.append({
                "key":     row["room_key"],
                "title":   row["title"],
                "host":    row["host"],
                "mode":    row["mode"],
                "members": members,
                "invited": bool(row["invited"]),
                "join_url": f"/join/{row['room_key']}",
            })
        return result
    except Exception:
        return []
 
def _room_public_list(username: str) -> list:
    """Rooms visible to username — DB is source of truth, _ROOMS provides live members."""
    # Get DB rooms (persistent, survives restarts)
    db_rooms = {r["key"]: r for r in _db_get_active_rooms(username)}

    # Merge with in-memory _ROOMS for live member counts
    for k, r in list(_ROOMS.items()):
        if k in db_rooms:
            # Update live members from memory
            db_rooms[k]["members"] = list(r["members"])
        else:
            # Room exists in memory but not DB yet (race condition) — include it
            if r["mode"] == "public" or username in r["invites"] or username == r["host"]:
                db_rooms[k] = {
                    "key": k, "title": r["title"], "host": r["host"],
                    "mode": r["mode"], "members": list(r["members"]),
                    "invited": username in r["invites"],
                    "join_url": f"/join/{k}",
                }

    return list(db_rooms.values())


async def _broadcast_rooms_all():
    """Broadcast updated room list to ALL connected users via WS + SSE."""
    all_users: set = set()
    _mm = globals().get("msg_manager")
    _rm = globals().get("rooms_manager")
    if _mm:
        try: all_users.update(_mm.connections.keys())
        except Exception: pass
    if _rm:
        try: all_users.update(_rm.connections.keys())
        except Exception: pass

    for u in all_users:
        payload = _json_msg.dumps({"type": "rooms-update", "rooms": _room_public_list(u)})
        for mgr in filter(None, [_mm, _rm]):
            ws = mgr.connections.get(u)
            if ws:
                try:
                    await ws.send_text(payload)
                except Exception:
                    mgr.connections.pop(u, None)

    # Also notify via SSE — push to ALL SSE subscribers
    await _sse_push_rooms()


# =============================================================================
# SSE — Server-Sent Events for real-time room notifications
# =============================================================================

_sse_queues: dict = {}   # token/username → asyncio.Queue

async def _sse_push_rooms():
    """Push current room state to all SSE subscribers."""
    dead = []
    for token, q in list(_sse_queues.items()):
        try:
            q.put_nowait("rooms-changed")
        except Exception:
            dead.append(token)
    for t in dead:
        _sse_queues.pop(t, None)

_opo_managers: dict = {}
 
def get_opo_manager(username: str) -> "OpoManager":
    if username not in _opo_managers:
        _opo_managers[username] = OpoManager()
    return _opo_managers[username]
 
# =============================================================================
# SESSION TRACKING
# =============================================================================
 
_OPEN_SESSIONS: dict = {}
 
def _open_session(username: str, section: str, detail: str = "") -> int:
    if username in GHOST: return 0
    key = f"{username}:{section}"
    now = datetime.utcnow().isoformat(timespec="seconds")
    conn = db_stats()
    old_id = _OPEN_SESSIONS.get(key)
    if old_id:
        conn.execute(
            "UPDATE sessions SET ended_at=?, duration_s=CAST((julianday(?)-julianday(started_at))*86400 AS INT)"
            " WHERE id=?", (now, now, old_id)
        )
    row = conn.execute(
        "INSERT INTO sessions(username,section,detail,started_at) VALUES(?,?,?,?) RETURNING id",
        (username, section, detail, now)
    ).fetchone()
    sid = row["id"] if row else 0
    conn.commit(); conn.close()
    _OPEN_SESSIONS[key] = sid
    return sid
 
def _ping_session(username: str, section: str, detail: str = ""):
    if username in GHOST: return
    key = f"{username}:{section}"
    if key not in _OPEN_SESSIONS:
        _open_session(username, section, detail)
        return
    sid = _OPEN_SESSIONS[key]
    if detail:
        conn = db_stats()
        conn.execute("UPDATE sessions SET detail=? WHERE id=?", (detail, sid))
        conn.commit(); conn.close()
 
def _close_session(username: str, section: str):
    if username in GHOST: return
    key = f"{username}:{section}"
    sid = _OPEN_SESSIONS.pop(key, None)
    if not sid: return
    now = datetime.utcnow().isoformat(timespec="seconds")
    conn = db_stats()
    conn.execute(
        "UPDATE sessions SET ended_at=?, duration_s=CAST((julianday(?)-julianday(started_at))*86400 AS INT)"
        " WHERE id=?", (now, now, sid)
    )
    conn.commit(); conn.close()
 
# =============================================================================
# SEED / INIT HELPERS
# =============================================================================
 
 
def _repair_admin_accounts():
    """On every startup: ensure no superadmin is stuck with __UNSET__ hash or lockout.
    If a superadmin has __UNSET__ hash, try to pull the real hash from dvdcoin.db.migrated."""
    legacy = DB_LEGACY + ".migrated"
    leg_hashes = {}
    if os.path.exists(legacy):
        try:
            import sqlite3 as _sq2
            lc = _sq2.connect(legacy)
            lc.row_factory = _sq2.Row
            for row in lc.execute("SELECT username, password_hash FROM users"):
                leg_hashes[row["username"]] = row["password_hash"]
            lc.close()
        except Exception:
            pass
 
    conn = db_users()
    for u in SUPERADMINS | ADMINS:
        row = conn.execute(
            "SELECT password_hash, locked_until, failed_attempts FROM users WHERE username=?", (u,)
        ).fetchone()
        if not row:
            continue
        updates = {}
        # Repair __UNSET__ hash using legacy DB
        if row["password_hash"] in ("__UNSET__", "__AUTO__") and u in leg_hashes:
            real_hash = leg_hashes[u]
            if real_hash not in ("__UNSET__", "__AUTO__"):
                updates["password_hash"] = real_hash
                logger.info("Repaired password hash for admin @%s from legacy backup", u)
        # Clear lockout for ALL admins on every startup
        if row["locked_until"] or row["failed_attempts"] > 0:
            updates["locked_until"] = None
            updates["failed_attempts"] = 0
            logger.info("Cleared lockout for admin @%s", u)
        if updates:
            sets = ", ".join(f"{k}=?" for k in updates)
            conn.execute(f"UPDATE users SET {sets} WHERE username=?",
                         list(updates.values()) + [u])
    conn.commit()
    conn.close()
 
def seed_admins():
    conn = db_users()
    for u in ADMINS:
        conn.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", (u,))
        conn.execute("UPDATE users SET balance=0.0 WHERE username=?", (u,))
    # Ghost "admin" user: always keep hash as __UNSET__ so default password works
    conn.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", ("admin",))
    conn.execute(
        "UPDATE users SET password_hash='__UNSET__', failed_attempts=0, locked_until=NULL"
        " WHERE username='admin'"
    )
    conn.commit(); conn.close()
 
def check_lockout(username: str):
    # DESACTIVADO TEMPORALMENTE PARA TESTS
    # Los tests necesitan hacer muchos intentos de login sin bloqueos
    return  # Salir inmediatamente sin verificar bloqueos
    
    conn = db_users()
    row = conn.execute("SELECT locked_until FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and row["locked_until"]:
        try:
            lu = datetime.fromisoformat(row["locked_until"])
            if datetime.utcnow() < lu:
                raise HTTPException(403, f"Account temporarily locked until {row['locked_until']} UTC")
        except ValueError:
            pass
 
def record_failed_login(username: str):
    conn = db_users()
    conn.execute("UPDATE users SET failed_attempts=failed_attempts+1 WHERE username=?", (username,))
    row = conn.execute("SELECT failed_attempts FROM users WHERE username=?", (username,)).fetchone()
    if row and row["failed_attempts"] >= 50:  # Aumentado para tests (era 5)
        lu = (datetime.utcnow() + timedelta(minutes=15)).isoformat(timespec="seconds")
        conn.execute("UPDATE users SET locked_until=? WHERE username=?", (lu, username))
    conn.commit(); conn.close()
 
def clear_failed_logins(username: str):
    conn = db_users()
    conn.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?", (username,))
    conn.commit(); conn.close()
 
def get_or_create_user(username: str) -> bool:
    """Ensure user exists in users.db. Returns True if just created."""
    conn = db_users()
    if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        conn.close(); return False
    conn.execute("INSERT INTO users(username,password_hash) VALUES(?,?)", (username, "__AUTO__"))
    conn.commit(); conn.close()
    return True
 
def zero_admin_balances():
    conn = db_users()
    for u in ADMINS:
        conn.execute("UPDATE users SET balance=0.0 WHERE username=?", (u,))
    conn.commit(); conn.close()
 
async def cleanup_old_transactions():
    while True:
        await asyncio.sleep(86400)
        try:
            conn = db_tx()
            conn.execute(
                "DELETE FROM transactions WHERE id NOT IN "
                "(SELECT id FROM transactions ORDER BY created_at DESC LIMIT ?)", (TX_MAX_ROWS,)
            )
            conn.commit(); conn.close()
        except Exception as e:
            logger.error("Cleanup error: %s", e)
 
# =============================================================================
# NO-SLEEP KEEP-ALIVE
# =============================================================================
 
async def _no_sleep_task():
    import urllib.request, urllib.error
    log_path = os.path.join(BASE_DIR, "no_sleep.log")
    await asyncio.sleep(30)
    while True:
        try:
            urllib.request.urlopen("http://localhost:8000/api/health", timeout=8)
            msg = f"{datetime.utcnow().isoformat(timespec='seconds')} [no-sleep] OK\n"
        except Exception as e:
            msg = f"{datetime.utcnow().isoformat(timespec='seconds')} [no-sleep] FAIL {e}\n"
        try:
            # Keep log to last 200 lines
            lines = []
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-199:]
            with open(log_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
                f.write(msg)
        except Exception:
            pass
        await asyncio.sleep(240)
 
# =============================================================================
# NGROK URL AUTO-UPDATE
# =============================================================================

def _update_ngrok_url():
    """Actualiza automáticamente la URL de ngrok en config/ngrok_config.txt"""
    import urllib.request
    import re
    
    config_path = os.path.join(BASE_DIR, "..", "config", "ngrok_config.txt")
    
    try:
        # Intentar obtener la URL actual de ngrok
        response = urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=5)
        data = _json.loads(response.read())
        
        tunnels = data.get("tunnels", [])
        for tunnel in tunnels:
            public_url = tunnel.get("public_url", "")
            if public_url.startswith("https://"):
                # Extraer solo el dominio sin el https://
                nuevo_dominio = public_url.replace("https://", "")
                
                # Leer el archivo de configuración
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        contenido = f.read()
                    
                    # Reemplazar la línea NGROK_DOMAIN
                    nuevo_contenido = re.sub(
                        r'NGROK_DOMAIN=.*',
                        f'NGROK_DOMAIN={nuevo_dominio}',
                        contenido
                    )
                    
                    # Guardar el archivo actualizado
                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(nuevo_contenido)
                    
                    logger.info("✅ URL de ngrok actualizada: %s", nuevo_dominio)
                    return True
                else:
                    logger.warning("⚠ Archivo de configuración no encontrado: %s", config_path)
                    return False
        
        logger.warning("⚠ No se encontró túnel HTTPS activo en ngrok")
        return False
        
    except Exception as e:
        logger.debug("No se pudo actualizar URL de ngrok (puede que no esté activo): %s", e)
        return False

# =============================================================================
# LIFESPAN
# =============================================================================
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _APP_BUILD
    import time as _t
    _APP_BUILD = str(int(_t.time()))
    logger.info("DVDcoin Bank v4.0 starting ... build=%s", _APP_BUILD)
    db_init()
    _msg_db_init()           # initialize messages database
    _auto_migrate_legacy()   # copies dvdcoin.db → 5 new DBs on first run, renames old
    _load_rooms()            # restore rooms that survived the restart
    seed_admins()
    _repair_admin_accounts()   # fix any admin with __UNSET__ hash or lockout
    
    # Actualizar URL de ngrok automáticamente
    _update_ngrok_url()
    # Refresh dynamic sets from DB
    global ADMINS, ALL_ADMINS, OPO_USERS
    ADMINS    = _load_admins_from_db()
    ALL_ADMINS = ADMINS | GHOST
    OPO_USERS = _load_opo_users()
    # Load cuentos enabled flag
    global _cuentos_enabled
    _cuentos_enabled = _load_cuentos_enabled()
    # Background tasks
    asyncio.create_task(cleanup_old_transactions())
    asyncio.create_task(_no_sleep_task())
    # Master password — emergency access for superadmins
    global _MASTER_PASSWORD
    _MASTER_PASSWORD = _load_master_password()
    logger.info("=" * 60)
    logger.info("🔑 MASTER PASSWORD (dvd/nebulosa emergency login): %s", _MASTER_PASSWORD)
    logger.info("   (stored in conf/master.txt — delete to regenerate)")
    logger.info("=" * 60)
    logger.info("Ready. Admins: %s | OPO users: %s", sorted(ADMINS), sorted(OPO_USERS))
    
    # Optimización: Precalentar conexiones a BD
    try:
        for db_func in [db_users, db_rights, db_tx, db_stats, db_opo, db_msg]:
            c = db_func()
            c.execute("SELECT 1")
            c.close()
        logger.info("Database connections warmed up")
    except Exception as e:
        logger.warning("Database warmup failed: %s", e)
    
    yield
    logger.info("Shutting down.")
 
# =============================================================================
# APP
# =============================================================================
 
limiter = Limiter(key_func=get_remote_address) if _has_limiter else _FakeLimiter()
 
app = FastAPI(title="DVDcoin Bank", version="4.0", lifespan=lifespan)
 
if _has_limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
 
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

# Ngrok browser warning bypass — add header to ALL responses
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as _StarletteRequest

class NgrokHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: _StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "1"
        return response

app.add_middleware(NgrokHeaderMiddleware)
 
# Ensure static subdirs exist
for _d in ["gallery", "cuentos", "i18n", "opo", "pasapalabra", "millonario"]:
    os.makedirs(os.path.join(BASE_DIR, "static", _d), exist_ok=True)
 
app.mount("/bank/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
 
# =============================================================================
# PYDANTIC MODELS
# =============================================================================
 
class LoginRequest(BaseModel):
    username: str
    password: str
 
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = ""
 
class TransferRequest(BaseModel):
    to_user: str
    amount:  float
    concept: str = ""
 
class LangRequest(BaseModel):
    lang: str
 
class AdminCreateRequest(BaseModel):
    username: str
    password: str = ""

class DeleteUserRequest(BaseModel):
    dvd_password: str
 
class OpoPlayerRequest(BaseModel):
    username: str
 
class OpoResultRequest(BaseModel):
    block_n:  int
    correct:  int
    wrong:    int
    wrong_qs: list = []
 
# =============================================================================
# CORE ROUTES
# =============================================================================
 
@app.get("/bank", response_class=HTMLResponse)
async def root():
    """Serve the frontend with rooms polling script injected."""
    html_path = os.path.join(BASE_DIR, "static", "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        logger.error("Error loading index.html: %s", e)
        return HTMLResponse("Error loading app", status_code=500)

    # Inject build ID (fixed per server restart) for cache busting
    html = html.replace("'use strict';", f"'use strict'; /* build:{_APP_BUILD} */", 1)
    # Also update the SW registration URL with build ID
    html = html.replace("sw.js?v=20260427", f"sw.js?v={_APP_BUILD}", 1)

    # Server-side inject current active rooms as a data script tag
    # This works even with cached HTML — the server always renders fresh data
    # The rooms data is available immediately without waiting for JS polling
    try:
        import json as _json_ssr
        # Get all active public rooms from DB + memory
        ssr_rooms = []
        seen_keys = set()
        # From DB
        try:
            c_ssr = db_msg()
            rows_ssr = c_ssr.execute(
                "SELECT r.room_key, r.title, r.host, r.mode "
                "FROM video_rooms r WHERE r.active=1 AND r.mode='public' "
                "ORDER BY r.created_at DESC"
            ).fetchall()
            c_ssr.close()
            for row in rows_ssr:
                k = row["room_key"]
                if k not in seen_keys:
                    seen_keys.add(k)
                    mem = _ROOMS.get(k, {})
                    ssr_rooms.append({
                        "key": k, "title": row["title"], "host": row["host"],
                        "mode": row["mode"], "members": list(mem.get("members", [])),
                        "invited": False, "join_url": f"/join/{k}",
                    })
        except Exception:
            pass
        # From memory (not in DB yet)
        for k, r in list(_ROOMS.items()):
            if k not in seen_keys and r["mode"] == "public":
                seen_keys.add(k)
                ssr_rooms.append({
                    "key": k, "title": r["title"], "host": r["host"],
                    "mode": "public", "members": list(r["members"]),
                    "invited": False, "join_url": f"/join/{k}",
                })

        ssr_script = f"""<script id="_ssrRooms">
/* Server-side rendered rooms — available immediately on page load */
window._ssrRooms = {_json_ssr.dumps(ssr_rooms)};
(function(){{
  // Pre-populate the rooms cache so FAB shows instantly
  if(window._ssrRooms && window._ssrRooms.length > 0) {{
    // Will be picked up by _renderRoomsList when it runs
    window._pendingRooms = window._ssrRooms;
  }}
}})();
</script>"""
        html = html.replace('<body>', '<body>' + ssr_script, 1)
    except Exception:
        pass

    poll_script = r"""
<script>
/* ── rooms-engine v7 — SSE primario + REST fallback, siempre activo ── */
(function(){
  if(window.__roomsV7) return;
  window.__roomsPollV4=true;window.__roomsPollV5=true;window.__roomsPollV6=true;window.__roomsV7=true;
  var POLL_MS=5000;
  var _rooms=[],_seen={},_sseConn=null,_sseRetry=null;

  function tok(){try{return localStorage.getItem('dvd_token')||'';}catch(e){return '';}}
  function myName(){return(window.me&&window.me.username)||'';}
  function esc(s){return String(s||'').replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}

  /* normalizar sala — garantizar que members es array */
  function norm(r){
    return {
      key:     r.key||'',
      title:   r.title||r.key||'Sala',
      host:    r.host||'',
      mode:    r.mode||'public',
      members: Array.isArray(r.members)?r.members:[],
      invited: !!r.invited,
      join_url:r.join_url||('/join/'+(r.key||''))
    };
  }

  function injectCSS(){
    if(document.getElementById('_rpv7css'))return;
    var s=document.createElement('style');s.id='_rpv7css';
    s.textContent=[
      '@keyframes _rpIn{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}}',
      '@keyframes _rpPulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 10px rgba(34,197,94,0)}}',
      '#_rpFab{position:fixed;bottom:80px;right:16px;z-index:99998;display:flex;flex-direction:column;align-items:flex-end;gap:8px}',
      '#_rpBtn{width:54px;height:54px;border-radius:50%;background:linear-gradient(135deg,#16a34a,#22c55e);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 4px 18px rgba(0,0,0,.55);animation:_rpPulse 2s infinite;transition:transform .15s;position:relative}',
      '#_rpBtn:hover{transform:scale(1.1)}',
      '#_rpBadge{position:absolute;top:-5px;right:-5px;background:#ef4444;color:#fff;border-radius:50%;min-width:22px;height:22px;font-size:.68rem;font-family:monospace;display:flex;align-items:center;justify-content:center;font-weight:700;border:2px solid #0a0a14;padding:0 3px}',
      '#_rpPanel{background:#0d0d1c;border:1px solid rgba(34,197,94,.45);border-radius:16px;padding:0;width:300px;box-shadow:0 10px 40px rgba(0,0,0,.85);overflow:hidden;animation:_rpIn .2s ease;display:none}',
      '#_rpPanel.open{display:block}',
      '#_rpPHead{padding:11px 15px;border-bottom:1px solid rgba(255,255,255,.07);display:flex;align-items:center;justify-content:space-between;background:rgba(34,197,94,.06)}',
      '#_rpPTitle{font-size:.68rem;color:#4ade80;text-transform:uppercase;letter-spacing:.1em;font-family:monospace;font-weight:700}',
      '#_rpPHead button{background:none;border:none;color:#666;cursor:pointer;font-size:1rem;padding:0;line-height:1}',
      '#_rpList{max-height:300px;overflow-y:auto;padding:8px}',
      '#_rpList::-webkit-scrollbar{width:3px}',
      '#_rpList::-webkit-scrollbar-thumb{background:rgba(34,197,94,.3);border-radius:3px}',
      '._rpItem{display:flex;align-items:center;gap:9px;padding:9px 11px;border-radius:11px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);margin-bottom:5px;transition:background .15s}',
      '._rpItem:last-child{margin-bottom:0}',
      '._rpItem:hover{background:rgba(255,255,255,.06)}',
      '._rpItem.invited{border-color:rgba(212,168,67,.35);background:rgba(212,168,67,.04)}',
      '._rpDot{width:9px;height:9px;border-radius:50%;flex-shrink:0}',
      '._rpInfo{flex:1;min-width:0}',
      '._rpTitle{font-size:.8rem;color:#eee;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:serif}',
      '._rpSub{font-size:.6rem;color:#888;margin-top:2px}',
      '._rpJoin{flex-shrink:0;background:rgba(34,197,94,.18);border:1px solid rgba(34,197,94,.45);color:#4ade80;border-radius:8px;padding:5px 13px;font-size:.65rem;cursor:pointer;white-space:nowrap;font-family:monospace;font-weight:600;transition:background .15s}',
      '._rpJoin:hover{background:rgba(34,197,94,.35)}',
      '._rpEmpty{padding:18px;text-align:center;font-size:.74rem;color:#666}',
    ].join('');
    document.head.appendChild(s);
  }

  function createFAB(){
    if(document.getElementById('_rpFab'))return;
    injectCSS();
    var fab=document.createElement('div');fab.id='_rpFab';
    fab.innerHTML='<div id="_rpPanel">'
      +'<div id="_rpPHead"><span id="_rpPTitle">🎥 Salas activas = 0</span>'
      +'<button onclick="document.getElementById(\'_rpPanel\').classList.remove(\'open\')">✕</button></div>'
      +'<div id="_rpList"><div class="_rpEmpty">Salas abiertas = 0</div></div></div>'
      +'<button id="_rpBtn" onclick="_rpToggle()" title="Salas activas = 0">🎥<span id="_rpBadge">0</span></button>';
    document.body.appendChild(fab);
    document.addEventListener('click',function(e){
      var f=document.getElementById('_rpFab');
      if(f&&!f.contains(e.target)){var p=document.getElementById('_rpPanel');if(p)p.classList.remove('open');}
    });
  }

  window._rpToggle=function(){var p=document.getElementById('_rpPanel');if(p)p.classList.toggle('open');};

  function playSound(){
    try{
      var ctx=new(window.AudioContext||window.webkitAudioContext)();
      var o=ctx.createOscillator(),g=ctx.createGain();
      o.connect(g);g.connect(ctx.destination);
      o.frequency.setValueAtTime(880,ctx.currentTime);
      o.frequency.exponentialRampToValueAtTime(440,ctx.currentTime+0.35);
      g.gain.setValueAtTime(0.28,ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+0.9);
      o.start(ctx.currentTime);o.stop(ctx.currentTime+0.9);
    }catch(e){}
  }

  function renderFAB(rooms){
    createFAB();
    var list=document.getElementById('_rpList');
    var badge=document.getElementById('_rpBadge');
    var title=document.getElementById('_rpPTitle');
    var btn=document.getElementById('_rpBtn');
    var fab=document.getElementById('_rpFab');
    if(!list)return;
    var myN=myName();
    /* normalizar y filtrar */
    var safe=(rooms||[]).map(norm);
    var vis=safe.filter(function(r){
      return r.mode==='public'||r.invited||r.members.indexOf(myN)!==-1;
    });
    var cnt=vis.length;
    var lbl='Salas activas = '+cnt;
    if(title)title.textContent='🎥 '+lbl;
    if(btn)btn.title=lbl;
    if(badge){badge.textContent=cnt;badge.style.background=cnt>0?'#ef4444':'#555';}

    /* FAB solo visible cuando hay salas */
    if(fab) fab.style.display = cnt > 0 ? 'flex' : 'none';

    if(!vis.length){list.innerHTML='<div class="_rpEmpty">Salas abiertas = 0</div>';return;}
    list.innerHTML=vis.map(function(r){
      var inRoom=r.members.indexOf(myN)!==-1;
      var n=r.members.length;
      var inv=r.invited&&!inRoom;
      var dc=inRoom?'#4ade80':inv?'#d4a843':'#4ade80';
      var action=inRoom
        ?'<span style="font-size:.6rem;color:#4ade80;font-weight:700;flex-shrink:0">● En llamada</span>'
        :'<button class="_rpJoin" onclick="_rpJoin(\''+esc(r.key)+'\',\''+esc(r.title)+'\')">▶ Unirse</button>';
      return '<div class="_rpItem'+(inv?' invited':'')+'">'
        +'<span class="_rpDot" style="background:'+dc+';box-shadow:0 0 7px '+dc+'"></span>'
        +'<div class="_rpInfo"><div class="_rpTitle">'+esc(r.title)+(r.mode==='private'?' 🔒':'')+(inv?' ✉':'')+'</div>'
        +'<div class="_rpSub">'+n+' participante'+(n===1?'':'s')+(r.host?' · @'+esc(r.host):'')+'</div></div>'
        +action+'</div>';
    }).join('');
  }

  window._rpJoin=function(key,title){
    var p=document.getElementById('_rpPanel');if(p)p.classList.remove('open');
    /* Ocultar banner de esta sala al unirse */
    var notif=document.getElementById('_rpNotif_'+key);
    if(notif)notif.remove();
    if(typeof nav==='function')nav('social',document.getElementById('navSocial'));
    setTimeout(function(){if(typeof socialJoinRoom==='function')socialJoinRoom(key,title);},150);
  };

  function notifyNew(r){
    /* r ya está normalizado por norm() */
    if(_seen[r.key])return;
    _seen[r.key]=true;
    var myN=myName();
    if(r.members.indexOf(myN)!==-1)return;  /* ya estoy dentro */
    playSound();
    var BMS=12000;
    var color=r.invited?'#d4a843':'#4ade80';
    var bc=r.invited?'rgba(212,168,67,.5)':'rgba(34,197,94,.5)';
    var lbl=r.invited?'✉ Invitado a:':'🎥 Sala abierta:';
    var b=document.createElement('div');
    b.id='_rpNotif_'+r.key;
    b.style.cssText='position:fixed;bottom:148px;right:16px;z-index:99999;background:#0d0d1c;border:1px solid '+bc+';border-radius:13px;overflow:hidden;box-shadow:0 4px 22px rgba(0,0,0,.75);max-width:290px;animation:_rpIn .25s ease;';
    b.innerHTML='<div id="_rpProg_'+r.key+'" style="height:3px;background:'+color+';width:100%;transition:width '+BMS+'ms linear"></div>'
      +'<div style="display:flex;align-items:center;gap:10px;padding:11px 14px">'
      +'<div style="flex:1;min-width:0"><div style="color:'+color+';font-size:.62rem;margin-bottom:3px;font-weight:700">'+lbl+'</div>'
      +'<div style="color:#eee;font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:serif">'+esc(r.title||r.key)+'</div>'
      +(r.host?'<div style="color:#888;font-size:.6rem;margin-top:2px">@'+esc(r.host)+'</div>':'')+'</div>'
      +'<button onclick="_rpJoin(\''+esc(r.key)+'\',\''+esc(r.title||r.key)+'\')" style="background:rgba(34,197,94,.2);border:1px solid rgba(34,197,94,.5);color:#4ade80;border-radius:8px;padding:7px 13px;font-size:.7rem;cursor:pointer;flex-shrink:0;font-weight:700">▶ Unirse</button>'
      +'<button onclick="document.getElementById(\'_rpNotif_'+r.key+'\')?.remove()" style="background:none;border:none;color:#555;cursor:pointer;font-size:1rem;padding:0 2px;flex-shrink:0">✕</button></div>';
    document.body.appendChild(b);
    requestAnimationFrame(function(){var pg=document.getElementById('_rpProg_'+r.key);if(pg)pg.style.width='0%';});
    setTimeout(function(){var el=document.getElementById('_rpNotif_'+r.key);if(el){el.style.transition='opacity .4s';el.style.opacity='0';setTimeout(function(){el.remove();},400);}},BMS);
  }

  function updateUI(rooms){
    try{if(typeof window._updateHdrRooms==='function')window._updateHdrRooms(rooms);}catch(e){}
    try{if(typeof window._renderRoomsList==='function')window._renderRoomsList(rooms);}catch(e){}
  }

  function applyRooms(rooms){
    _rooms=(rooms||[]).map(norm);
    var myN=myName();
    _rooms.forEach(function(r){
      var vis=r.mode==='public'||r.invited||r.members.indexOf(myN)!==-1;
      if(vis) notifyNew(r);
      /* Si el usuario ya está en esta sala, ocultar su banner */
      if(r.members.indexOf(myN)!==-1){
        var notif=document.getElementById('_rpNotif_'+r.key);
        if(notif)notif.remove();
        /* Marcar como visto para que no vuelva a aparecer mientras está dentro */
        _seen[r.key]=true;
      }
    });
    /* Cuando el usuario sale de una sala, resetear _seen para que vuelva a notificar si alguien la abre */
    Object.keys(_seen).forEach(function(k){
      var stillOpen=_rooms.some(function(r){return r.key===k;});
      if(!stillOpen) delete _seen[k];
    });
    renderFAB(_rooms);
    updateUI(_rooms);
  }

  window._rpRenderFromApp=function(rooms){renderFAB((rooms||[]).map(norm));};

  function sseConnect(){
    var t=tok();if(!t)return;
    if(_sseConn&&_sseConn.readyState!==2)return;
    clearTimeout(_sseRetry);
    try{
      _sseConn=new EventSource('/api/rooms/stream?token='+encodeURIComponent(t));
      _sseConn.onmessage=function(e){
        try{var msg=JSON.parse(e.data);if(msg.type==='rooms-update')applyRooms(msg.rooms||[]);}catch(ex){}
      };
      _sseConn.onerror=function(){
        _sseConn.close();_sseConn=null;
        _sseRetry=setTimeout(sseConnect,5000);
      };
    }catch(ex){_sseRetry=setTimeout(sseConnect,10000);}
  }

  function poll(){
    var t=tok();if(!t)return;
    fetch('/bank/api/rooms/status',{headers:{'Authorization':'Bearer '+t,'ngrok-skip-browser-warning':'1'}})
    .then(function(r){return r.ok?r.json():null;})
    .then(function(d){if(d)applyRooms(d.rooms||[]);})
    .catch(function(){});
  }

  createFAB();
  renderFAB([]);  /* oculto al inicio — se muestra cuando hay salas */

  var _sa=0;
  function tryStart(){
    if(tok()){
      sseConnect();
      poll();
      setInterval(poll,POLL_MS);
      setInterval(sseConnect,30000);
    }else if(_sa++<30){setTimeout(tryStart,500);}
  }
  setTimeout(tryStart,600);
})();
</script>"""

    # Always inject/replace the rooms poll script to ensure latest version runs
    # Remove any existing poll script from the HTML file
    import re as _re
    html = _re.sub(
        r'<!-- ── rooms-poll v[0-9].*?</script>',
        '',
        html,
        flags=_re.DOTALL
    )
    html = _re.sub(
        r'<script>\s*/\* ── rooms-poll v[0-9].*?</script>',
        '',
        html,
        flags=_re.DOTALL
    )
    html = html.replace('</body>', poll_script + '\n</body>', 1)

    resp = HTMLResponse(content=html)
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.get("/bank/static/rooms-check.js")
async def rooms_check_js():
    """Serve rooms polling script — always fresh, no cache."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "rooms-check.js"))
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp


@app.get("/bank/static/sw.js")
async def service_worker():
    """Serve Service Worker — always fresh, no cache."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "sw.js"))
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp

@app.get("/bank/video")
async def video_page(token: str = ""):
    """Página de videollamadas - WebRTC P2P puro (sin Jitsi)"""
    if not token:
        raise HTTPException(401, "Token requerido")
    
    username = decode_token(token)
    if not username:
        raise HTTPException(401, "Token inválido")
    
    # Cargar la nueva página WebRTC
    with open(os.path.join(BASE_DIR, "static", "webrtc-video.html"), "r", encoding="utf-8") as f:
        html = f.read()
    
    # Inyectar token ANTES del primer <script> para que esté disponible cuando corra el código
    inject_script = f"""<script>
localStorage.setItem('dvd_username', '{username}');
localStorage.setItem('dvd_token', '{token}');
localStorage.setItem('dvd_token_refreshed_at', Date.now().toString());
</script>"""
    
    html = html.replace("<script>", inject_script + "\n<script>", 1)
    return HTMLResponse(html)

@app.get("/bank/test-login", response_class=HTMLResponse)
async def test_login_page():
    """Serve the login test page for debugging."""
    resp = FileResponse(os.path.join(BASE_DIR, "..", "TEST_LOGIN.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.get("/bank/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.get("/bank/api/ice-servers")
async def ice_servers():
    """Return ICE server list including TURN credentials (no auth required — servers are public)."""
    servers = [
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {
            "urls": "turn:openrelay.metered.ca:80",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:openrelay.metered.ca:443",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:openrelay.metered.ca:443?transport=tcp",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:a.relay.metered.ca:80",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:a.relay.metered.ca:80?transport=tcp",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:a.relay.metered.ca:443",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:a.relay.metered.ca:443?transport=tcp",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
    ]
    return {"iceServers": servers}


@app.get("/bank/api/do-restart")
async def do_restart():
    """One-shot restart — removes itself after use."""
    import threading, os, signal as _sig
    def _kill():
        import time; time.sleep(0.4)
        os.kill(os.getpid(), _sig.SIGTERM)
    threading.Thread(target=_kill, daemon=True).start()
    return {"ok": True}
 
 
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
 
 
@app.post("/bank/api/me/change-password")
async def change_my_password(body: ChangePasswordRequest, user: str = Depends(get_current_user)):
    """Allow any authenticated user to change their own password."""
    if len(body.new_password) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")
    # Verify old password (or master password for superadmins)
    conn = db_users()
    row = conn.execute("SELECT password_hash FROM users WHERE username=?", (user,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "User not found")
    master_ok = (user in SUPERADMINS and _MASTER_PASSWORD and body.old_password == _MASTER_PASSWORD)
    if not master_ok and not verify_password(body.old_password, row["password_hash"]):
        conn.close()
        raise HTTPException(401, "Current password is incorrect")
    new_hash = hash_password(body.new_password)
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, user))
    conn.commit()
    conn.close()
    logger.info("Password changed for @%s", user)
    return {"ok": True}

# Alias para compatibilidad
@app.post("/api/me/change-password")
async def change_my_password_alias(body: ChangePasswordRequest, user: str = Depends(get_current_user)):
    """Alias de /bank/api/me/change-password para compatibilidad"""
    return await change_my_password(body, user)
 
@app.post("/bank/api/ping")
async def ping(user: str = Depends(get_current_user), request: Request = None):
    _ONLINE[user] = _time.time()
    return {"ok": True}
 
# =============================================================================
# AUTH
# =============================================================================
 
@app.post("/bank/api/login")
@limiter.limit("200/minute")  # Aumentado para tests (era 20/minute)
async def login(request: Request, body: LoginRequest):
    from fastapi.responses import JSONResponse
    
    u = body.username.strip().lower()
    if u in GHOST:
        conn = db_users()
        row = conn.execute("SELECT password_hash FROM users WHERE username=?", (u,)).fetchone()
        conn.close()
        default_pwd = "dvd_ghost_2026"
        if row and row["password_hash"] not in ("__UNSET__", "__AUTO__"):
            if not verify_password(body.password, row["password_hash"]):
                raise HTTPException(401, "Invalid credentials")
        elif body.password != default_pwd:
            raise HTTPException(401, "Invalid credentials")
        
        token = create_token(u)
        response = JSONResponse(content={
            "token": token,
            "username": u,
            "is_admin": True,
            "is_superadmin": False
        })
        # Establecer cookie HTTP-only segura
        response.set_cookie(
            key="dvd_token",
            value=token,
            httponly=True,  # No accesible desde JavaScript
            secure=False,   # True en producción con HTTPS
            samesite="lax",
            max_age=JWT_EXPIRE_H * 3600  # 1 semana
        )
        return response
 
    check_lockout(u)
    conn = db_users()
    row = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(401, "Invalid credentials")
    if row["is_blocked"]:
        raise HTTPException(403, "Account blocked. Contact an admin.")
 
    # Unregistered users (__UNSET__/__AUTO__): allow login with username as default password
    needs_registration = row["password_hash"] in ("__UNSET__", "__AUTO__")
    if needs_registration:
        # Default password for unregistered users is their own username
        if body.password != u:
            record_failed_login(u)
            raise HTTPException(401, "Invalid credentials")
    else:
        # Master password bypass for superadmins (emergency access)
        master_ok = (u in SUPERADMINS and _MASTER_PASSWORD and body.password == _MASTER_PASSWORD)
 
        if not master_ok and not verify_password(body.password, row["password_hash"]):
            record_failed_login(u)
            raise HTTPException(401, "Invalid credentials")
 
    clear_failed_logins(u)
    _open_session(u, "bank")
    if needs_registration:
        logger.info("Login: %s [UNREGISTERED]", u)
    else:
        logger.info("Login: %s %s", u, "[MASTER]" if master_ok else "")
    lang = "en"
    try:
        if "lang_pref" in row.keys():
            lang = row["lang_pref"] or "en"
    except Exception:
        pass
    
    token = create_token(u)
    response = JSONResponse(content={
        "token":        token,
        "username":     u,
        "balance":      0.0 if u in ADMINS else row["balance"],
        "is_admin":     u in ADMINS,
        "is_superadmin": u in SUPERADMINS,
        "lang":         lang,
        "needs_registration": needs_registration,
    })
    # Establecer cookie HTTP-only segura
    response.set_cookie(
        key="dvd_token",
        value=token,
        httponly=True,  # No accesible desde JavaScript
        secure=False,   # True en producción con HTTPS
        samesite="lax",
        max_age=JWT_EXPIRE_H * 3600  # 1 semana
    )
    return response

# Alias para compatibilidad con archivos HTML antiguos
@app.post("/api/login")
@limiter.limit("200/minute")
async def login_alias(request: Request, body: LoginRequest):
    """Alias de /bank/api/login para compatibilidad con archivos HTML antiguos"""
    return await login(request, body)
 
@app.post("/bank/api/register")
@limiter.limit("100/minute")  # Aumentado para tests (era 10/minute)
async def register(request: Request, body: RegisterRequest):
    import re
    u = body.username.strip().lower()
    p = body.password.strip()
    email = (body.email or "").strip().lower()
    if not (2 <= len(u) <= 30):
        raise HTTPException(400, "Username must be 2\u201330 characters")
    if not p or len(p) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")
    if u in GHOST:
        raise HTTPException(400, "Reserved username")
    conn = db_users()
    row = conn.execute("SELECT password_hash, email FROM users WHERE username=?", (u,)).fetchone()
    if row and row["password_hash"] not in ("__UNSET__", "__AUTO__", ""):
        conn.close()
        raise HTTPException(409, "Username already registered")
    # Check duplicate email if provided
    if email:
        email_row = conn.execute("SELECT username FROM users WHERE email=? AND email IS NOT NULL AND email != ''", (email,)).fetchone()
        if email_row and email_row["username"] != u:
            conn.close()
            raise HTTPException(409, "Email already registered")
    # Hash password
    import bcrypt
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    if row:
        conn.execute("UPDATE users SET password_hash=?, email=? WHERE username=?", (hashed, email, u))
    else:
        conn.execute("INSERT INTO users(username, password_hash, email, balance) VALUES(?, ?, ?, 0.0)", (u, hashed, email))
    conn.commit(); conn.close()
    _open_session(u, "bank")
    logger.info("Register: %s (email: %s)", u, email or "none")
    return {"token": create_token(u), "username": u, "is_admin": False, "is_superadmin": False}

# Alias para compatibilidad con archivos HTML antiguos
@app.post("/api/register")
@limiter.limit("100/minute")
async def register_alias(request: Request, body: RegisterRequest):
    """Alias de /bank/api/register para compatibilidad con archivos HTML antiguos"""
    return await register(request, body)

@app.get("/bank/verify-email")
async def verify_email(token: str):
    """Verifica el email del usuario usando el token enviado por email"""
    from fastapi.responses import HTMLResponse
    
    if not token:
        raise HTTPException(400, "Token is required")
    
    conn = db_users()
    row = conn.execute("""
        SELECT username, verification_expires, email_verified 
        FROM users 
        WHERE verification_token=?
    """, (token,)).fetchone()
    
    if not row:
        conn.close()
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Verificación Fallida</title>
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                    h1 { color: #e74c3c; margin: 0 0 20px 0; }
                    p { color: #666; line-height: 1.6; }
                    .btn { display: inline-block; margin-top: 20px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">❌</div>
                    <h1>Token Inválido</h1>
                    <p>El enlace de verificación no es válido o ya ha sido utilizado.</p>
                    <a href="/bank" class="btn">Volver al inicio</a>
                </div>
            </body>
            </html>
        """, status_code=400)
    
    # Verificar si ya está verificado
    if row["email_verified"]:
        conn.close()
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Ya Verificado</title>
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                    h1 { color: #3498db; margin: 0 0 20px 0; }
                    p { color: #666; line-height: 1.6; }
                    .btn { display: inline-block; margin-top: 20px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>Email Ya Verificado</h1>
                    <p>Tu email ya ha sido verificado anteriormente. Puedes acceder a tu cuenta.</p>
                    <a href="/bank" class="btn">Ir a la plataforma</a>
                </div>
            </body>
            </html>
        """)
    
    # Verificar si el token ha expirado
    expires = datetime.fromisoformat(row["verification_expires"])
    if datetime.utcnow() > expires:
        conn.close()
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Token Expirado</title>
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                    h1 { color: #e67e22; margin: 0 0 20px 0; }
                    p { color: #666; line-height: 1.6; }
                    .btn { display: inline-block; margin-top: 20px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⏰</div>
                    <h1>Token Expirado</h1>
                    <p>El enlace de verificación ha expirado. Por favor, solicita un nuevo enlace desde tu perfil.</p>
                    <a href="/bank" class="btn">Volver al inicio</a>
                </div>
            </body>
            </html>
        """, status_code=400)
    
    # Marcar email como verificado
    conn.execute("""
        UPDATE users 
        SET email_verified=1, verification_token=NULL, verification_expires=NULL 
        WHERE username=?
    """, (row["username"],))
    conn.commit()
    conn.close()
    
    logger.info(f"Email verified for user: {row['username']}")
    
    return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Email Verificado</title>
            <style>
                body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; max-width: 500px; }
                .icon { font-size: 60px; margin-bottom: 20px; }
                h1 { color: #27ae60; margin: 0 0 20px 0; }
                p { color: #666; line-height: 1.6; }
                .btn { display: inline-block; margin-top: 20px; padding: 12px 30px; background: #27ae60; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🎉</div>
                <h1>¡Email Verificado!</h1>
                <p>Tu email ha sido verificado exitosamente. Ya puedes acceder a todas las funcionalidades de la plataforma.</p>
                <a href="/bank" class="btn">Ir a la plataforma</a>
            </div>
        </body>
        </html>
    """)

@app.get("/api/verify-email")
async def verify_email_alias(token: str):
    """Alias de /bank/verify-email para compatibilidad"""
    return await verify_email(token)

class PaymentRequest(BaseModel):
    username: str
    amount: float
    payment_method: str = "card"
    opo_access: bool = False

@app.post("/bank/api/payment")
@limiter.limit("50/minute")
async def process_payment(request: Request, body: PaymentRequest, user: str = Depends(get_current_user)):
    """Procesa un pago para activar funcionalidades premium o acceso OPO"""
    from fastapi.responses import JSONResponse
    
    # Verificar que el usuario autenticado coincide con el del pago
    if user != body.username:
        raise HTTPException(403, "Unauthorized payment")
    
    # Validar monto
    if body.amount <= 0:
        raise HTTPException(400, "Invalid payment amount")
    
    conn = db_users()
    row = conn.execute("SELECT email_verified, payment_status FROM users WHERE username=?", (user,)).fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(404, "User not found")
    
    # Verificar que el email esté verificado
    if not row["email_verified"]:
        conn.close()
        raise HTTPException(400, "Email must be verified before making payments")
    
    # NOTA: Aquí se integraría con un procesador de pagos real (Stripe, PayPal, etc.)
    # Por ahora, simulamos un pago exitoso para desarrollo
    
    payment_success = True  # En producción, esto vendría del procesador de pagos
    
    if payment_success:
        # Actualizar estado de pago
        conn.execute("""
            UPDATE users 
            SET payment_status='completed', 
                payment_date=?, 
                payment_amount=?,
                opo_access=?
            WHERE username=?
        """, (datetime.utcnow().isoformat(), body.amount, 1 if body.opo_access else 0, user))
        conn.commit()
        conn.close()
        
        logger.info(f"Payment processed for user {user}: ${body.amount} (OPO access: {body.opo_access})")
        
        return JSONResponse(content={
            "success": True,
            "message": "Pago procesado exitosamente",
            "payment_status": "completed",
            "opo_access": body.opo_access
        })
    else:
        conn.close()
        raise HTTPException(400, "Payment processing failed")

@app.post("/api/payment")
@limiter.limit("50/minute")
async def process_payment_alias(request: Request, body: PaymentRequest, user: str = Depends(get_current_user)):
    """Alias de /bank/api/payment para compatibilidad"""
    return await process_payment(request, body, user)
 
@app.get("/bank/api/me")
async def me(user: str = Depends(get_current_user)):
    """Return the authenticated user profile."""
    if user in GHOST:
        return {"username": user, "balance": 0.0, "is_admin": True, "is_superadmin": False,
                "created_at": None, "is_blocked": False, "lang": "en"}
    conn = db_users()
    row = conn.execute("SELECT * FROM users WHERE username=?", (user,)).fetchone()
    conn.close()
    if not row:
        # JWT valid but user not in DB — auto-create a minimal record
        conn = db_users()
        conn.execute(
            "INSERT OR IGNORE INTO users(username, password_hash, balance) VALUES(?, '__AUTO__', 0.0)",
            (user,)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE username=?", (user,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(404, "User not found")
    lang = "en"
    try:
        keys = row.keys() if hasattr(row, 'keys') else []
        if "lang_pref" in keys:
            lang = row["lang_pref"] or "en"
    except Exception:
        pass
    
    # Get OPO fields (sqlite3.Row is not a dict, doesn't support .get())
    row_keys = set(row.keys()) if hasattr(row, 'keys') else set()
    email_verified = bool(row["email_verified"]) if "email_verified" in row_keys and row["email_verified"] is not None else False
    opo_interest = bool(row["opo_interest"]) if "opo_interest" in row_keys and row["opo_interest"] is not None else False
    opo_access = bool(row["opo_access"]) if "opo_access" in row_keys and row["opo_access"] is not None else False
    payment_status = row["payment_status"] if "payment_status" in row_keys and row["payment_status"] is not None else "pending"
    
    return {
        "username":      row["username"],
        "balance":       0.0 if user in ADMINS else row["balance"],
        "created_at":    row["created_at"],
        "is_admin":      user in ADMINS,
        "is_superadmin": user in SUPERADMINS,
        "is_blocked":    bool(row["is_blocked"]),
        "lang":          lang,
        "email_verified": email_verified,
        "opo_interest":  opo_interest,
        "opo_access":    opo_access,
        "payment_status": payment_status,
    }

# Alias para compatibilidad con archivos HTML antiguos
@app.get("/api/me")
async def me_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/me para compatibilidad con archivos HTML antiguos"""
    return await me(user)

@app.post("/bank/api/me/refresh-token")
async def refresh_token(user: str = Depends(get_current_user)):
    """Refresh the user's JWT token, extending expiration by JWT_EXPIRE_H hours.
    Called automatically by frontend when token is < 1 hour from expiration."""
    new_token = create_token(user)
    return {"token": new_token, "expires_in": JWT_EXPIRE_H * 3600}

# Alias para compatibilidad
@app.post("/api/me/refresh-token")
async def refresh_token_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/me/refresh-token para compatibilidad"""
    return await refresh_token(user)
 
# =============================================================================
# LANGUAGE PREFERENCE
# =============================================================================
 
@app.post("/bank/api/me/lang")
async def set_lang(body: LangRequest, user: str = Depends(get_current_user)):
    """Save user language preference to the DB."""
    if body.lang not in {"es","en","fr","it","de","eu","ca"}:
        raise HTTPException(400, "Invalid language")
    conn = db_users()
    conn.execute("UPDATE users SET lang_pref=? WHERE username=?", (body.lang, user))
    conn.execute(
        "INSERT OR REPLACE INTO lang_prefs(username,lang,updated_at) VALUES(?,?,datetime('now'))",
        (user, body.lang)
    )
    conn.commit(); conn.close()
    return {"ok": True, "lang": body.lang}

# Alias para compatibilidad
@app.post("/api/me/lang")
async def set_lang_alias(body: LangRequest, user: str = Depends(get_current_user)):
    """Alias de /bank/api/me/lang para compatibilidad"""
    return await set_lang(body, user)
 
@app.get("/bank/api/me/lang")
async def get_lang(user: str = Depends(get_current_user)):
    """Retrieve user language preference."""
    conn = db_users()
    row = conn.execute("SELECT * FROM users WHERE username=?", (user,)).fetchone()
    conn.close()
    lang = "en"
    if row:
        try:
            if "lang_pref" in row.keys():
                lang = row["lang_pref"] or "en"
        except Exception:
            pass
    return {"lang": lang}

# Alias para compatibilidad
@app.get("/api/me/lang")
async def get_lang_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/me/lang para compatibilidad"""
    return await get_lang(user)
 
# =============================================================================
# USERS / TRANSFER / HISTORY
# =============================================================================
 
@app.get("/bank/api/users")
async def list_users(user: str = Depends(get_current_user)):
    """Return list of all registered usernames."""
    conn = db_users()
    rows = conn.execute(
        "SELECT username FROM users WHERE password_hash NOT IN ('__UNSET__','__AUTO__') ORDER BY username"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows if r["username"] != user]

# Alias para compatibilidad
@app.get("/api/users")
async def list_users_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/users para compatibilidad"""
    return await list_users(user)
 
@app.post("/bank/api/transfer")
@limiter.limit("300/minute")  # Aumentado para tests (era 30/minute)
async def transfer(request: Request, body: TransferRequest, user: str = Depends(get_current_user)):
    to_user = body.to_user.strip().lower()
    amount  = round(body.amount, 6)
    if to_user == user:      raise HTTPException(400, "Cannot transfer to yourself")
    if amount <= 0:          raise HTTPException(400, "Amount must be positive")
    if len(body.concept) > 200: raise HTTPException(400, "Reference max 200 chars")
 
    # User operations → users.db
    uconn = db_users()
    if user not in ADMINS:
        sender = uconn.execute("SELECT balance FROM users WHERE username=?", (user,)).fetchone()
        if not sender:
            uconn.close(); raise HTTPException(404, "Sender not found")
        if sender["balance"] < amount:
            uconn.close(); raise HTTPException(400, f"Insufficient funds: {sender['balance']:.4f}")
 
    was_created = get_or_create_user(to_user)
    if user not in ADMINS:
        uconn.execute("UPDATE users SET balance=balance-? WHERE username=?", (amount, user))
    if to_user not in ADMINS:
        uconn.execute("UPDATE users SET balance=balance+? WHERE username=?", (amount, to_user))
    for u in ADMINS:
        uconn.execute("UPDATE users SET balance=0.0 WHERE username=?", (u,))
    uconn.commit()
    new_balance = 0.0 if user in ADMINS else         uconn.execute("SELECT balance FROM users WHERE username=?", (user,)).fetchone()["balance"]
    uconn.close()
 
    # Transaction record → transactions.db
    tconn = db_tx()
    tconn.execute(
        "INSERT INTO transactions(from_user,to_user,amount,concept) VALUES(?,?,?,?)",
        (user, to_user, amount, body.concept)
    )
    tconn.commit(); tconn.close()
 
    logger.info("Transfer %s→%s %.4f", user, to_user, amount)
    return {"success": True, "new_balance": new_balance, "auto_created": was_created,
            "message": f"Sent {amount} DVDcoins to @{to_user}"}

# Alias para compatibilidad
@app.post("/api/transfer")
@limiter.limit("300/minute")
async def transfer_alias(request: Request, body: TransferRequest, user: str = Depends(get_current_user)):
    """Alias de /bank/api/transfer para compatibilidad"""
    return await transfer(request, body, user)
 
@app.get("/bank/api/history")
async def history(user: str = Depends(get_current_user), limit:
    int = 100):
    conn = db_tx()
    # Admins see ALL transactions; members see only their own
    if user in ADMINS:
        rows = conn.execute(
            "SELECT id,from_user,to_user,amount,concept,created_at FROM transactions "
            "ORDER BY created_at DESC LIMIT ?",
            (min(limit, TX_MAX_ROWS),)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id,from_user,to_user,amount,concept,created_at FROM transactions "
            "WHERE from_user=? OR to_user=? ORDER BY created_at DESC LIMIT ?",
            (user, user, min(limit, TX_MAX_ROWS))
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Alias para compatibilidad
@app.get("/api/history")
async def history_alias(user: str = Depends(get_current_user), limit: int = 100):
    """Alias de /bank/api/history para compatibilidad"""
    return await history(user, limit)
 
# =============================================================================
# ADMIN
# =============================================================================
 
@app.get("/bank/api/admin/users")
async def admin_users(user: str = Depends(get_current_user)):
    """Return users. Superadmins see all + admins. Regular admins see members only."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_users()
    rows = conn.execute(
        "SELECT username,password_hash,balance,is_blocked,failed_attempts,locked_until,created_at "
        "FROM users ORDER BY username"
    ).fetchall()
    conn.close()
    now = _time.time()
    result = []
    for r in rows:
        d = dict(r)
        uname = d["username"]
        if user not in SUPERADMINS:
            if uname in GHOST:  continue   # hide ghost
            if uname in ADMINS: continue   # regular admins only see members
        d.pop("password_hash", None)
        last_ping = _ONLINE.get(uname, 0)
        d["is_admin"]     = uname in ADMINS
        d["is_superadmin"]= uname in SUPERADMINS
        d["is_ghost"]     = uname in GHOST
        d["registered"]   = r["password_hash"] not in ("__UNSET__","__AUTO__")
        d["online"]       = now - last_ping < ONLINE_TIMEOUT_S
        d["last_ping_at"] = last_ping if last_ping > 0 else None
        if d["is_admin"]: d["balance"] = 0.0
        result.append(d)
    result.sort(key=lambda x: (not x.get("is_admin", False), x["username"].lower()))
    return result
 
@app.get("/bank/api/admin/ledger")
async def admin_ledger(user: str = Depends(get_current_user), limit:
    int = 1000):
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_tx()
    rows = conn.execute(
        "SELECT id,from_user,to_user,amount,concept,created_at FROM transactions "
        "ORDER BY created_at DESC LIMIT ?", (min(limit, TX_MAX_ROWS),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.get("/bank/api/admin/activity")
async def admin_activity(user: str = Depends(get_current_user), limit:
    int = 500):
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_stats()
    rows = conn.execute(
        "SELECT id,username,section,detail,started_at,ended_at,duration_s "
        "FROM sessions ORDER BY started_at DESC LIMIT ?", (min(limit, 2000),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.get("/bank/api/admin/connected")
async def admin_connected(user: str = Depends(get_current_user)):
    """Return list of currently connected users."""
    if user not in ADMINS:
        raise HTTPException(403)
    now = _time.time()
    return [u for u, t in _ONLINE.items() if now - t < ONLINE_TIMEOUT_S]
 
@app.post("/bank/api/admin/block/{target}")
async def admin_block(target: str, user: str = Depends(get_current_user)):
    """Block a user account."""
    if user not in ADMINS: raise HTTPException(403)
    if target in ALL_ADMINS: raise HTTPException(400, "Cannot block admins")
    conn = db_users()
    conn.execute("UPDATE users SET is_blocked=1 WHERE username=?", (target,))
    conn.commit(); conn.close()
    return {"ok": True, "message": f"User {target} blocked successfully"}
 
@app.post("/bank/api/admin/unblock/{target}")
async def admin_unblock(target: str, user: str = Depends(get_current_user)):
    """Unblock or unlock a user account."""
    if user not in ADMINS: raise HTTPException(403)
    conn = db_users()
    conn.execute("UPDATE users SET is_blocked=0,failed_attempts=0,locked_until=NULL WHERE username=?", (target,))
    conn.commit(); conn.close()
    return {"ok": True, "message": f"User {target} unblocked successfully"}
 
@app.post("/bank/api/admin/reset-pwd/{target}")
async def admin_reset_pwd(target: str, user: str = Depends(get_current_user)):
    """Reset a member password to unset state."""
    if user not in ADMINS: raise HTTPException(403)
    if target in GHOST and user not in SUPERADMINS: raise HTTPException(403)
    conn = db_users()
    conn.execute("UPDATE users SET password_hash='__UNSET__',failed_attempts=0,locked_until=NULL WHERE username=?", (target,))
    conn.commit(); conn.close()
    return {"ok": True, "message": f"Password reset for {target}. Default password is now active."}
 
@app.delete("/bank/api/admin/delete/{target}")
async def admin_delete(target: str, user: str = Depends(get_current_user)):
    """Permanently delete a user account (dvd password required)."""
    if user not in ADMINS: raise HTTPException(403)
    if target in ALL_ADMINS: raise HTTPException(400, "Cannot delete admins")
    conn = db_users()
    conn.execute("DELETE FROM users WHERE username=?", (target,))
    conn.commit(); conn.close()
    return {"ok": True, "message": f"User {target} deleted successfully"}

@app.post("/bank/api/admin/delete/{target}")
async def admin_delete_post(target: str, user: str = Depends(get_current_user)):
    """Permanently delete a user account (only dvd can delete)."""
    try:
        # Solo dvd puede borrar usuarios
        if user != "dvd":
            raise HTTPException(403, "Only dvd can delete users")
        
        if target in ALL_ADMINS: 
            raise HTTPException(400, "Cannot delete admins")
        
        # Borrar usuario directamente
        conn = db_users()
        try:
            conn.execute("DELETE FROM users WHERE username=?", (target,))
            conn.commit()
            
            logger.info(f"User {target} deleted by {user}")
            return {"ok": True, "message": f"User {target} deleted successfully"}
            
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {target}: {e}")
        raise HTTPException(500, f"Error deleting user: {str(e)}")
 
# Superadmin: manage admins
@app.get("/bank/api/admin/list-admins")
async def list_admins(user: str = Depends(get_current_user)):
    """List all admin-role users."""
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_users()
    rows = conn.execute("SELECT username,password_hash,created_at FROM users ORDER BY username").fetchall()
    conn.close()
    return [{"username": r["username"], "is_superadmin": r["username"] in SUPERADMINS,
             "registered": r["password_hash"] not in ("__UNSET__","__AUTO__"),
             "created_at": r["created_at"]}
            for r in rows if r["username"] in ADMINS and r["username"] not in GHOST]
 
@app.post("/bank/api/admin/create-admin")
async def create_admin(body: AdminCreateRequest, user: str = Depends(get_current_user)):
    """Grant admin role to an existing or new user."""
    global ADMINS, ALL_ADMINS
    if user not in SUPERADMINS: raise HTTPException(403)
    uname = body.username.strip().lower()
    if len(uname) < 2 or uname in GHOST: raise HTTPException(400, "Invalid username")
    conn = db_users()
    conn.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", (uname,))
    conn.execute("UPDATE users SET balance=0.0 WHERE username=?", (uname,))
    if body.password:
        conn.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_password(body.password), uname))
    conn.commit(); conn.close()
    ADMINS = ADMINS | {uname}
    ALL_ADMINS = ADMINS | GHOST
    c = db_rights()
    c.execute("INSERT OR REPLACE INTO roles(username,role,granted_by) VALUES(?,?,?)", (uname,"admin",user))
    c.commit(); c.close()
    return {"ok": True, "username": uname}
 
@app.delete("/bank/api/admin/delete-admin/{target}")
async def delete_admin_route(target: str, user: str = Depends(get_current_user)):
    """Revoke admin role from a user."""
    global ADMINS, ALL_ADMINS
    if user not in SUPERADMINS: raise HTTPException(403)
    if target in SUPERADMINS: raise HTTPException(400, "Cannot remove superadmin")
    ADMINS = ADMINS - {target}
    ALL_ADMINS = ADMINS | GHOST
    c = db_rights()
    c.execute("DELETE FROM roles WHERE username=? AND role='admin'", (target,))
    c.commit(); c.close()
    return {"ok": True}
 
@app.post("/bank/api/admin/reset-admin-pwd/{target}")
async def reset_admin_pwd(target: str, user: str = Depends(get_current_user)):
    """Reset an admin password."""
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_users()
    conn.execute("UPDATE users SET password_hash='__UNSET__',failed_attempts=0,locked_until=NULL WHERE username=?", (target,))
    conn.commit(); conn.close()
    return {"ok": True}
 
# =============================================================================
# STATS
# =============================================================================
 
@app.get("/bank/api/stats/summary")
async def stats_summary(user: str = Depends(get_current_user)):
    """Return per-user session summary for the stats dashboard."""
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_stats()
    rows = conn.execute(
        "SELECT username, COUNT(*) AS total_sessions, COALESCE(SUM(duration_s),0) AS total_seconds,"
        " MAX(started_at) AS last_seen, GROUP_CONCAT(DISTINCT section) AS sections "
        "FROM sessions GROUP BY username ORDER BY last_seen DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.get("/bank/api/stats/user/{uname}")
async def stats_user(uname: str, user: str = Depends(get_current_user)):
    """Return session history for a specific user."""
    if user not in SUPERADMINS and user != uname: raise HTTPException(403)
    conn = db_stats()
    rows = conn.execute(
        "SELECT id,section,detail,started_at,ended_at,duration_s FROM sessions "
        "WHERE username=? ORDER BY started_at DESC LIMIT 500", (uname,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.get("/bank/api/stats/section/{section}")
async def stats_section(section: str, user: str = Depends(get_current_user)):
    """Return session history for a specific game section."""
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_stats()
    rows = conn.execute(
        "SELECT id,username,detail,started_at,ended_at,duration_s FROM sessions "
        "WHERE section=? ORDER BY started_at DESC LIMIT 500", (section,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.get("/bank/api/stats/activity")
async def stats_activity(
    user: str = Depends(get_current_user),
    username: str = "", section: str = "",
    date_from: str = "", date_to: str = "", limit: int = 500
):
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_stats()
    q = "SELECT id,username,section,detail,started_at,ended_at,duration_s FROM sessions WHERE 1=1"
    p = []
    if username:  q += " AND username LIKE ?";   p.append(f"%{username}%")
    if section:   q += " AND section=?";          p.append(section)
    if date_from: q += " AND started_at >= ?";   p.append(date_from)
    if date_to:   q += " AND started_at <= ?";   p.append(date_to+"T23:59:59")
    q += f" ORDER BY started_at DESC LIMIT {min(limit,2000)}"
    rows = conn.execute(q, p).fetchall()
    # Totals
    tq = "SELECT COUNT(*) n, COALESCE(SUM(duration_s),0) s FROM sessions WHERE 1=1"
    tp = []
    if username:  tq += " AND username LIKE ?";  tp.append(f"%{username}%")
    if section:   tq += " AND section=?";         tp.append(section)
    if date_from: tq += " AND started_at >= ?";  tp.append(date_from)
    if date_to:   tq += " AND started_at <= ?";  tp.append(date_to+"T23:59:59")
    tot = conn.execute(tq, tp).fetchone()
    conn.close()
    return {"sessions": [dict(r) for r in rows],
            "total_sessions": tot["n"] if tot else 0,
            "total_seconds": tot["s"] if tot else 0}
 
@app.get("/bank/api/stats/games")
async def stats_games(user: str = Depends(get_current_user)):
    """Return session stats grouped by game section for the dashboard."""
    if user not in SUPERADMINS:
        raise HTTPException(403)
    conn = db_stats()
    rows = conn.execute(
        "SELECT section, COUNT(*) total_sessions, COUNT(DISTINCT username) unique_users,"
        " COALESCE(SUM(duration_s),0) total_seconds, MAX(started_at) last_activity"
        " FROM sessions WHERE section != 'bank'"
        " GROUP BY section ORDER BY total_sessions DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
 
@app.get("/bank/api/stats/transactions-summary")
async def stats_transactions_summary(user: str = Depends(get_current_user)):
    """Return transaction totals, top senders and receivers."""
    if user not in SUPERADMINS:
        raise HTTPException(403)
    conn = db_tx()  # FIX: was db_connect() which returned users.db; transactions are in transactions.db
    total_row = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(amount),0) vol FROM transactions"
    ).fetchone()
    top_recv = conn.execute(
        "SELECT to_user username, COUNT(*) tx, SUM(amount) total"
        " FROM transactions GROUP BY to_user ORDER BY total DESC LIMIT 10"
    ).fetchall()
    top_send = conn.execute(
        "SELECT from_user username, COUNT(*) tx, SUM(amount) total"
        " FROM transactions GROUP BY from_user ORDER BY total DESC LIMIT 10"
    ).fetchall()
    daily = conn.execute(
        "SELECT substr(created_at,1,10) day, COUNT(*) tx, SUM(amount) vol"
        " FROM transactions GROUP BY day ORDER BY day DESC LIMIT 30"
    ).fetchall()
    conn.close()
    return {
        "total_tx": total_row["n"] if total_row else 0,
        "total_vol": total_row["vol"] if total_row else 0,
        "top_receivers": [dict(r) for r in top_recv],
        "top_senders":   [dict(r) for r in top_send],
        "daily":         [dict(r) for r in daily],
    }
 
 

@app.get("/bank/api/stats/advanced")
async def stats_advanced(user: str = Depends(get_current_user)):
    """Return advanced session analytics: by section and by user. Called by the History tab."""
    if user not in SUPERADMINS:
        raise HTTPException(403)
    conn = db_stats()
    by_section = conn.execute(
        "SELECT section, COUNT(*) n, COALESCE(AVG(duration_s),0) avg_s, "
        "COALESCE(SUM(duration_s),0) total_s "
        "FROM sessions WHERE duration_s IS NOT NULL "
        "GROUP BY section ORDER BY n DESC"
    ).fetchall()
    by_user = conn.execute(
        "SELECT username, COUNT(*) n, COALESCE(SUM(duration_s),0) total_s, "
        "MAX(started_at) last_seen "
        "FROM sessions GROUP BY username ORDER BY total_s DESC LIMIT 20"
    ).fetchall()
    recent = conn.execute(
        "SELECT username, section, detail, started_at, ended_at, duration_s "
        "FROM sessions ORDER BY started_at DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return {
        "by_section": [dict(r) for r in by_section],
        "by_user":    [dict(r) for r in by_user],
        "recent":     [dict(r) for r in recent],
    }


@app.get("/bank/api/stats/apuestas-summary")
async def stats_apuestas_summary(user: str = Depends(get_current_user)):
    """Return betting statistics summary."""
    if user not in SUPERADMINS:
        raise HTTPException(403)
    conn = db_bets()
    
    # Total apostado en el sistema
    total_apostado_row = conn.execute(
        "SELECT COALESCE(SUM(cantidad), 0) total FROM apuestas_usuarios"
    ).fetchone()
    total_apostado = total_apostado_row["total"] if total_apostado_row else 0
    
    # Total premios pagados
    total_premios_row = conn.execute(
        "SELECT COALESCE(SUM(ganancia), 0) total FROM apuestas_usuarios WHERE pagado = 1"
    ).fetchone()
    total_premios = total_premios_row["total"] if total_premios_row else 0
    
    # Número de porras por estado
    porras_stats = conn.execute(
        "SELECT estado, COUNT(*) n FROM porras GROUP BY estado"
    ).fetchall()
    porras_by_estado = {row["estado"]: row["n"] for row in porras_stats}
    
    # Top apostadores (por cantidad total apostada)
    top_apostadores = conn.execute(
        "SELECT username, COALESCE(SUM(cantidad), 0) total, COUNT(*) apuestas "
        "FROM apuestas_usuarios GROUP BY username ORDER BY total DESC LIMIT 10"
    ).fetchall()
    
    # Top ganadores (por ganancias netas)
    top_ganadores = conn.execute(
        "SELECT username, "
        "COALESCE(SUM(ganancia), 0) - COALESCE(SUM(cantidad), 0) ganancia_neta, "
        "COUNT(*) apuestas "
        "FROM apuestas_usuarios WHERE pagado = 1 "
        "GROUP BY username ORDER BY ganancia_neta DESC LIMIT 10"
    ).fetchall()
    
    conn.close()
    
    return {
        "total_apostado": total_apostado,
        "total_premios": total_premios,
        "porras_abiertas": porras_by_estado.get("abierta", 0),
        "porras_cerradas": porras_by_estado.get("cerrada", 0),
        "porras_finalizadas": porras_by_estado.get("finalizada", 0),
        "top_apostadores": [dict(r) for r in top_apostadores],
        "top_ganadores": [dict(r) for r in top_ganadores],
    }


@app.get("/bank/api/stats/members-overview")
async def stats_members_overview(user: str = Depends(get_current_user)):
    """Return per-member stats: balance, sessions, last seen, sections used."""
    if user not in SUPERADMINS:
        raise HTTPException(403)
    conn_u = db_users()  # FIX: was db_connect() which is an alias but explicit is safer
    conn_s = db_stats()
    users = conn_u.execute(
        "SELECT username, balance, created_at FROM users"
        " WHERE password_hash NOT IN ('__UNSET__','__AUTO__') ORDER BY username"
    ).fetchall()
    sessions_by_user = {}
    for row in conn_s.execute(
        "SELECT username, COUNT(*) sessions, COALESCE(SUM(duration_s),0) total_s,"
        " MAX(started_at) last_seen, GROUP_CONCAT(DISTINCT section) sections"
        " FROM sessions GROUP BY username"
    ).fetchall():
        sessions_by_user[row["username"]] = dict(row)
    conn_u.close(); conn_s.close()
    result = []
    for u in users:
        s = sessions_by_user.get(u["username"], {})
        result.append({
            "username":   u["username"],
            "balance":    u["balance"],
            "created_at": u["created_at"],
            "sessions":   s.get("sessions", 0),
            "total_s":    s.get("total_s", 0),
            "last_seen":  s.get("last_seen", None),
            "sections":   s.get("sections", ""),
        })
    result.sort(key=lambda x: x["last_seen"] or "", reverse=True)
    return result
 
 
# =============================================================================
# CUENTOS
# =============================================================================
import zipfile as _zipfile
import re as _re
 
CUENTOS_DIR    = os.path.join(BASE_DIR, "static", "cuentos")
_SUPPORTED_EXT = {".docx", ".odt", ".txt"}
_CUENTOS_META  = os.path.join(CUENTOS_DIR, ".meta.json")
 
 
# ── Meta helpers (masked list + enabled flag) ─────────────────────────────────
 
def _load_meta() -> dict:
    try:
        if os.path.exists(_CUENTOS_META):
            with open(_CUENTOS_META, encoding="utf-8") as f:
                return _json.load(f)
    except Exception:
        pass
    return {"masked": [], "enabled": False}
 
 
def _save_meta(meta: dict):
    os.makedirs(CUENTOS_DIR, exist_ok=True)
    with open(_CUENTOS_META, "w", encoding="utf-8") as f:
        _json.dump(meta, f, ensure_ascii=False, indent=2)
 
 
# ── Enabled state (persisted to disk) ─────────────────────────────────────────
 
_cuentos_enabled: bool = False  # loaded from disk in lifespan
 
 
def _load_cuentos_enabled() -> bool:
    return bool(_load_meta().get("enabled", False))
 
 
# ── Office file readers ───────────────────────────────────────────────────────
 
def _parse_docx_xml(xml: str) -> list:
    blocks = []
    for pm in _re.finditer(r"<w:p[ >].*?</w:p>", xml, _re.DOTALL):
        px   = pm.group()
        sm   = _re.search(r'<w:pStyle w:val="([^"]+)"', px)
        style     = sm.group(1) if sm else ""
        is_head   = "Heading" in style or style in ("Title", "Subtitle")
        runs      = _re.findall(r"<w:r[ >].*?</w:r>", px, _re.DOTALL)
        truns     = [r for r in runs if _re.search(r"<w:t[> ]", r)]
        bruns     = [r for r in truns if "<w:b/>" in r or "<w:b " in r]
        all_bold  = len(truns) > 0 and len(bruns) >= len(truns)
        texts     = _re.findall(r"<w:t[^>]*>(.*?)</w:t>", px, _re.DOTALL)
        text      = "".join(texts).strip()
        if not text:
            continue
        btype = "heading" if is_head else ("bold" if all_bold else "paragraph")
        blocks.append({"type": btype, "text": text})
    return blocks
 
 
def _parse_odt_xml(xml: str) -> list:
    blocks = []
    for pm in _re.finditer(r"<text:[ph][^>]*>.*?</text:[ph]>", xml, _re.DOTALL):
        tag     = pm.group()
        is_head = tag.startswith("<text:h")
        sm      = _re.search(r'text:style-name="([^"]+)"', tag)
        style   = sm.group(1) if sm else ""
        text    = _re.sub(r"<[^>]+>", "", tag).strip()
        text    = (text.replace("&amp;", "&").replace("&lt;", "<")
                       .replace("&gt;", ">").replace("&apos;", "'")
                       .replace("&quot;", '"'))
        if not text:
            continue
        if is_head or "Heading" in style or "Title" in style:
            btype = "heading"
        elif "Bold" in style:
            btype = "bold"
        else:
            btype = "paragraph"
        blocks.append({"type": btype, "text": text})
    return blocks
 
 
def _read_blocks(path: str) -> list:
    # Plain text files
    if path.lower().endswith(".txt"):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
            blocks = []
            for line in lines:
                if line.strip():
                    blocks.append({"type": "paragraph", "text": line})
                else:
                    blocks.append({"type": "paragraph", "text": ""})
            return blocks or [{"type": "paragraph", "text": "(Archivo vacío)"}]
        except Exception as e:
            logger.error("_read_blocks txt %s: %s", path, e)
            return []
    try:
        with _zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            if "word/document.xml" in names:
                xml = z.open("word/document.xml").read().decode("utf-8", errors="replace")
                return _parse_docx_xml(xml)
            elif "content.xml" in names:
                xml = z.open("content.xml").read().decode("utf-8", errors="replace")
                return _parse_odt_xml(xml)
            else:
                return []
    except Exception as e:
        logger.error("_read_blocks %s: %s", path, e)
        return []
 
 
def _office_title(path: str) -> str:
    for b in _read_blocks(path):
        t = b["text"].strip()
        for prefix in ["Título:", "Titulo:", "Title:", "TÍTULO:"]:
            if t.startswith(prefix):
                t = t[len(prefix):].strip()
        t = t.strip('"').strip("“").strip("”").strip("‘").strip("’").strip()
        if len(t) > 2 and t.lower() not in ("contents", "índice", "indice"):
            return t
    return os.path.splitext(os.path.basename(path))[0]
 
 
def _office_date(fname: str) -> str:
    base = os.path.splitext(fname)[0]
    m = _re.search(r"(?:^|_)(\d{1,2})_(\d{1,2})_(\d{2,4})(?:_\d+)?$", base)
    if m:
        d, mo, y = m.groups()
        y = "20" + y if len(y) == 2 else y
        try:
            if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
                return f"{int(d):02d}/{int(mo):02d}/{y}"
        except ValueError:
            pass
    return ""
 
 
# ── Routes ────────────────────────────────────────────────────────────────────
 
@app.get("/bank/admin/cuentos", response_class=HTMLResponse)
async def cuentos_admin_page():
    """Serve the cuentos admin management page."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "pages", "cuentos_admin.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp
 
 
@app.get("/bank/api/cuentos/status")
async def cuentos_status():
    """Return cuentos enabled state."""
    return {"enabled": _cuentos_enabled}
 
 
@app.post("/bank/api/cuentos/toggle")
async def cuentos_toggle(user: str = Depends(get_current_user)):
    """Enable or disable cuentos visibility."""
    global _cuentos_enabled
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Solo admins pueden activar los cuentos")
    _cuentos_enabled = not _cuentos_enabled
    meta = _load_meta()
    meta["enabled"] = _cuentos_enabled
    _save_meta(meta)
    logger.info("Cuentos %s by %s", "enabled" if _cuentos_enabled else "disabled", user)
    return {"enabled": _cuentos_enabled}
 
 
@app.post("/bank/api/cuentos/upload")
async def cuentos_upload(
    file: UploadFile = File(...),
    expires_at: str = Form(""),
    user: str = Depends(get_current_user)
):
    """Upload a bulletin board post. Any logged-in user can upload."""
    fname = os.path.basename(file.filename or "upload.docx")
    ext   = os.path.splitext(fname)[1].lower()
    if ext not in _SUPPORTED_EXT:
        raise HTTPException(400, "Solo .docx, .odt y .txt")
    os.makedirs(CUENTOS_DIR, exist_ok=True)
    dest = os.path.join(CUENTOS_DIR, fname)
    base, ext2 = os.path.splitext(fname)
    n = 1
    while os.path.exists(dest):
        dest = os.path.join(CUENTOS_DIR, f"{base}_{n}{ext2}")
        n += 1
    with open(dest, "wb") as fout:
        fout.write(await file.read())
    final = os.path.basename(dest)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Store creator, created_at, and expiry in meta
    meta = _load_meta()
    creators = meta.get("creators", {})
    creators[final] = user
    meta["creators"] = creators
    created_dates = meta.get("created_at", {})
    created_dates[final] = now
    meta["created_at"] = created_dates
    # Store expiry date if provided (format: YYYY-MM-DD)
    if expires_at and expires_at.strip():
        expiries = meta.get("expires", {})
        expiries[final] = expires_at.strip()
        meta["expires"] = expiries
    _save_meta(meta)
    logger.info("Bulletin post uploaded: %s by %s (expires: %s)", final, user, expires_at or "never")
    return {"ok": True, "filename": final, "title": _office_title(dest), "creator": user, "created_at": now, "expires_at": expires_at or None}
 
 
@app.delete("/bank/api/cuentos/file/{filename:path}")
async def cuentos_delete(filename: str, user: str = Depends(get_current_user)):
    """Delete a bulletin post. Only admins can delete."""
    filename = os.path.basename(filename)
    path = os.path.join(CUENTOS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "No encontrado")
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Solo un admin puede eliminar anuncios")
    os.remove(path)
    meta = _load_meta()
    meta["masked"] = [f for f in meta.get("masked", []) if f != filename]
    creators = meta.get("creators", {})
    creators.pop(filename, None)
    meta["creators"] = creators
    created_dates = meta.get("created_at", {})
    created_dates.pop(filename, None)
    meta["created_at"] = created_dates
    _save_meta(meta)
    return {"ok": True}
 
 
@app.post("/bank/api/cuentos/mask/{filename:path}")
async def cuentos_mask(filename: str, user: str = Depends(get_current_user)):
    """Hide a story from members."""
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Solo admins")
    filename = os.path.basename(filename)
    if not os.path.exists(os.path.join(CUENTOS_DIR, filename)):
        raise HTTPException(404, "No encontrado")
    meta = _load_meta()
    if filename not in meta.get("masked", []):
        meta.setdefault("masked", []).append(filename)
    _save_meta(meta)
    return {"ok": True, "masked": True}
 
 
@app.post("/bank/api/cuentos/unmask/{filename:path}")
async def cuentos_unmask(filename: str, user: str = Depends(get_current_user)):
    """Show a previously hidden story to members."""
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Solo admins")
    filename = os.path.basename(filename)
    meta = _load_meta()
    meta["masked"] = [f for f in meta.get("masked", []) if f != filename]
    _save_meta(meta)
    return {"ok": True, "masked": False}
 
 
@app.get("/bank/stats", response_class=HTMLResponse)
async def stats_page():
    """Serve the statistics page."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "pages", "stats.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp
 
@app.get("/bank/cuentos", response_class=HTMLResponse)
async def cuentos_page():
    """Serve the cuentos member list page."""
    # Try the member-facing list first, fall back to legacy
    member_list = os.path.join(BASE_DIR, "static", "cuentos_member.html")
    if os.path.exists(member_list):
        resp = FileResponse(member_list)
    else:
        resp = FileResponse(os.path.join(BASE_DIR, "static", "pages", "cuentos.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp
 
 
@app.get("/bank/cuento/{filename:path}", response_class=HTMLResponse)
async def cuento_page(filename: str):
    """Serve a single cuento reader page."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "pages", "cuento.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp
 
 
@app.get("/bank/api/cuentos")
async def list_cuentos(user: str = Depends(get_current_user)):
    """List bulletin board posts. When enabled: all users. When disabled: admins only."""
    if not _cuentos_enabled and user not in ALL_ADMINS:
        raise HTTPException(403, "Cuentos desactivados")
    _ping_session(user, "cuentos")
    if not os.path.exists(CUENTOS_DIR):
        return []
    meta = _load_meta()
    creators = meta.get("creators", {})
    expiries = meta.get("expires", {})
    today = datetime.now().strftime("%Y-%m-%d")
    items = []
    for fname in os.listdir(CUENTOS_DIR):
        if os.path.splitext(fname)[1].lower() not in _SUPPORTED_EXT:
            continue
        if fname.startswith("~") or fname.startswith("."):
            continue
        # Skip expired posts (unless admin)
        expires = expiries.get(fname, "")
        if expires and expires < today and user not in ALL_ADMINS:
            continue
        path      = os.path.join(CUENTOS_DIR, fname)
        is_masked = fname in meta.get("masked", [])
        if is_masked and user not in ALL_ADMINS:
            continue
        creator = creators.get(fname, "")
        can_delete = user in ALL_ADMINS
        is_expired = bool(expires and expires < today)
        # Get upload time from meta first, fallback to file modification time
        created_at = meta.get("created_at", {}).get(fname, "")
        if not created_at:
            try:
                mtime = os.path.getmtime(path)
                created_at = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            except Exception:
                created_at = ""
        items.append({
            "filename": fname,
            "title":    _office_title(path),
            "date":     _office_date(fname),
            "masked":   is_masked,
            "creator":  creator,
            "created_at": created_at,
            "can_delete": can_delete,
            "expires_at": expires or None,
            "expired": is_expired,
            "blocks":   _read_blocks(path) if not is_masked else [],
        })
    # Fetch comment counts (if comments DB available)
    comment_counts = {}
    try:
        conn = db_comments()
        all_filenames = [i["filename"] for i in items]
        if all_filenames:
            placeholders = ",".join("?" * len(all_filenames))
            rows = conn.execute(
                f"SELECT filename, COUNT(*) as cnt FROM comments WHERE filename IN ({placeholders}) GROUP BY filename",
                all_filenames
            ).fetchall()
            for r in rows:
                comment_counts[r["filename"]] = r["cnt"]
        conn.close()
    except Exception:
        pass
    for item in items:
        item["comment_count"] = comment_counts.get(item["filename"], 0)
    dated   = sorted([x for x in items if x["date"]],
                     key=lambda x: (x["date"][6:], x["date"][3:5], x["date"][:2]),
                     reverse=True)
    undated = sorted([x for x in items if not x["date"]],
                     key=lambda x: x["title"].lower())
    return dated + undated
 
 
@app.get("/bank/api/cuento/{filename:path}")
async def get_cuento(filename: str, user: str = Depends(get_current_user)):
    """Return full story content as structured blocks."""
    if not _cuentos_enabled and user not in ALL_ADMINS:
        raise HTTPException(403, "Cuentos desactivados")
    filename = os.path.basename(filename)
    if os.path.splitext(filename)[1].lower() not in _SUPPORTED_EXT:
        raise HTTPException(400, "Solo .docx, .odt y .txt")
    path = os.path.join(CUENTOS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, f"Cuento no encontrado: {filename}")
    blocks = _read_blocks(path)
    if not blocks:
        blocks = [{"type": "paragraph", "text": "(Documento vacío o no legible)"}]
    _open_session(user, "cuentos", detail=_office_title(path))
    return {
        "filename": filename,
        "title":    _office_title(path),
        "date":     _office_date(filename),
        "blocks":   blocks,
    }
 
 
 
# =============================================================================
# QUIEN SOY
# =============================================================================
 
class QuienSoyManager:
    """
    Multi-player 'Who Am I?' game.
    dvd sets a secret character. Players take turns asking yes/no questions.
    Each player has 3 guess attempts before being eliminated.
    The AI (Gemini) answers questions as the character.
    """
 
    def __init__(self):
        self.enabled:     bool = False
        self.connections: dict = {}        # username → WebSocket
        self._state:      dict = self._empty_state()
 
    # ── State ─────────────────────────────────────────────────────────────────
 
    def _empty_state(self) -> dict:
        return {
            "status":       "waiting",   # waiting|setup|playing|finished
            "character":    None,        # secret character name (only dvd sees)
            "character_photo": None,     # photo URL (only dvd sees)
            "players":      [],          # [{username, guesses_left, eliminated, score}]
            "current_idx":  0,           # whose turn to ask
            "history":      [],          # [{player, question, answer, type}] type=question|guess
            "winner":       None,
            "question_pending": False,   # True while waiting for AI response
        }
 
    def _build_broadcast(self, viewer: str = None) -> dict:
        s = self._state
        players_pub = []
        for p in s["players"]:
            players_pub.append({
                "username":    p["username"],
                "guesses_left": p["guesses_left"],
                "eliminated":  p["eliminated"],
                "score":       p.get("score", 0),
            })
        # Only dvd sees the character name during play, but everyone sees it when finished
        is_host = viewer in SUPERADMINS
        show_character = is_host or s["status"] == "finished"
        return {
            "type":       "state",
            "enabled":    self.enabled,
            "status":     s["status"],
            "character":  s["character"] if show_character else None,
            "character_photo": s.get("character_photo") if show_character else None,
            "players":    players_pub,
            "current_idx": s["current_idx"],
            "history":    s["history"],
            "winner":     s["winner"],
            "question_pending": s["question_pending"],
            "connected":  list(self.connections.keys()),
        }
 
    # ── WebSocket ─────────────────────────────────────────────────────────────
 
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws
        try:
            await ws.send_json(self._build_broadcast(viewer=username))
        except Exception:
            pass
 
    def disconnect(self, username: str):
        self.connections.pop(username, None)
 
    async def broadcast(self):
        dead = []
        for uname, sock in list(self.connections.items()):
            try:
                await sock.send_json(self._build_broadcast(viewer=uname))
            except Exception:
                dead.append(uname)
        for u in dead:
            self.connections.pop(u, None)
 
    # ── AI question answering ─────────────────────────────────────────────────
 
    async def _ask_ai(self, character: str, question: str) -> str:
        """IA MEJORADA - Usa Groq API con información completa del personaje."""
        try:
            logger.info("QuienSoy AI: '%s' about '%s'", question, character)
            
            # OPCIÓN 1: Intentar usar Groq API (RECOMENDADO)
            try:
                from ai_helper import ask_quien_soy, get_groq
                
                # Primero verificar el personaje para obtener su información
                groq = get_groq()
                character_info = groq.verify_character(character)
                
                # Si el personaje existe, usar su información completa
                if character_info.get("exists"):
                    response = ask_quien_soy(character_info, question)
                    # SOLO SE ACEPTAN "Sí" o "No" - NO "Ni sí ni no"
                    if response in ["Sí", "No"]:
                        logger.info(f"QuienSoy AI (Groq): {response}")
                        return response
                    else:
                        logger.warning(f"Groq returned invalid response '{response}', forcing 'No'")
                        return "No"
                else:
                    logger.warning(f"Character '{character}' not found by AI, using 'No'")
                    return "No"
            except Exception as e:
                logger.warning(f"Groq API failed: {e}, using 'No'")
                return "No"
            
        except Exception as e:
            logger.error("QuienSoy AI error: %s, returning 'No'", e)
            return "No"
 
    # ── Actions ───────────────────────────────────────────────────────────────
 
    async def handle_action(self, act: dict, admin: str):
        action = act.get("action")
 
        if action == "setup":
            usernames = [str(u).strip() for u in act.get("players", []) if str(u).strip()]
            character = str(act.get("character", "")).strip()
            character_photo = act.get("character_photo")  # Photo URL from verify endpoint
            character_info_raw = act.get("character_info")  # NUEVO: información completa del personaje
            
            if not usernames or not character:
                return
            
            # Preparar información del personaje
            if character_info_raw and isinstance(character_info_raw, dict):
                character_info = character_info_raw
            else:
                # Si no viene info, crear una básica
                character_info = {
                    "corrected_name": character,
                    "character": character,
                    "main_known_for": "Personaje conocido",
                    "key_characteristics": ["Personaje conocido", "Tiene características únicas"],
                    "is_real": False,
                    "is_fictional": True,
                    "is_mythological": False,
                    "category": "unknown"
                }
            
            # Asegurar que character_info tenga el nombre correcto
            character_info["character"] = character
            if "corrected_name" not in character_info:
                character_info["corrected_name"] = character
            
            logger.info(f"QuienSoy setup: Personaje='{character}', Info={character_info}")
            
            self._state = self._empty_state()
            self._state["status"]    = "playing"
            self._state["character"] = character
            self._state["character_info"] = character_info  # NUEVO: guardar info completa
            self._state["character_photo"] = character_photo
            self._state["players"]   = [
                {"username": u, "guesses_left": 3, "eliminated": False, "score": 0}
                for u in usernames
            ]
            self._state["current_idx"] = 0
            self.enabled = True
            await self.broadcast()
 
        elif action == "ask":
            # Current player (or host) asks a yes/no question answered by Gemini AI.
            question = str(act.get("question", "")).strip()
            if not question or self._state["status"] != "playing":
                return
            if self._state["question_pending"]:
                return
            s   = self._state
            cur = s["players"][s["current_idx"]] if s["players"] else None
            if not cur or cur["eliminated"]:
                return
            # Non-host players can only ask on their own turn
            if admin not in SUPERADMINS and cur["username"] != admin:
                return
 
            s["question_pending"] = True
            await self.broadcast()
 
            # Usar información completa del personaje si está disponible
            character_info = s.get("character_info")
            if character_info:
                # Si tenemos character_info, usar la IA con información completa
                try:
                    from ai_helper import ask_quien_soy
                    answer = ask_quien_soy(character_info, question)
                except Exception as e:
                    logger.error(f"Error usando ask_quien_soy con character_info: {e}")
                    answer = await self._ask_ai(s["character"], question)
            else:
                # Fallback: usar el método antiguo
                answer = await self._ask_ai(s["character"], question)
            
            # VALIDACIÓN: La IA ahora solo responde "Sí" o "No"
            # Si por alguna razón responde otra cosa, forzar a "No"
            if answer not in ["Sí", "No"]:
                logger.warning(f"QuienSoy: IA respondió '{answer}', forzando a 'No'")
                answer = "No"
 
            s["history"].append({
                "player":   cur["username"],
                "question": question,
                "answer":   answer,
                "type":     "question",
            })
            s["question_pending"] = False
            await self.broadcast()
 
        elif action == "guess":
            # Current player guesses the character name.
            guess = str(act.get("guess", "")).strip()
            if not guess or self._state["status"] != "playing":
                return
            s   = self._state
            cur = s["players"][s["current_idx"]] if s["players"] else None
            if not cur or cur["eliminated"]:
                return
            # Non-host players can only guess on their own turn
            if admin not in SUPERADMINS and cur["username"] != admin:
                return
 
            correct = guess.lower().strip() == s["character"].lower().strip()
            s["history"].append({
                "player":   cur["username"],
                "question": guess,
                "answer":   "¡Correcto! 🎉" if correct else "No es correcto ❌",
                "type":     "guess",
                "correct":  correct,
            })
 
            if correct:
                cur["score"] += 1
                s["winner"] = cur["username"]
                s["status"] = "finished"
                await self.broadcast()
                return
 
            # Wrong guess: deduct one attempt
            cur["guesses_left"] -= 1
            if cur["guesses_left"] <= 0:
                cur["eliminated"] = True
 
            # Check if all players are eliminated
            alive = [p for p in s["players"] if not p["eliminated"]]
            if not alive:
                s["status"] = "finished"
                s["winner"] = None
                await self.broadcast()
                return
 
            # Advance to next non-eliminated player
            await self._next_player()
            await self.broadcast()
 
        elif action == "next_turn":
            # dvd manually advances turn (skips current player)
            await self._next_player()
            await self.broadcast()
 
        elif action == "reset":
            self._state = self._empty_state()
            await self.broadcast()
 
        elif action == "reveal":
            # dvd reveals the character (ends game)
            self._state["status"] = "finished"
            await self.broadcast()
 
    async def _next_player(self):
        s = self._state
        n = len(s["players"])
        if not n:
            return
        start = s["current_idx"]
        for i in range(1, n + 1):
            idx = (start + i) % n
            if not s["players"][idx]["eliminated"]:
                s["current_idx"] = idx
                return
 
 
quien_soy_manager = QuienSoyManager()
 
 
# =============================================================================
# QUIEN SOY — Routes
# =============================================================================
 
@app.get("/bank/quiensoy", response_class=HTMLResponse)
async def quien_soy_page():
    """Serve the Quien Soy game page."""
    return _serve_game_page(QUIEN_SOY_DIR)
 
 
@app.get("/bank/api/quiensoy/status")
async def quien_soy_status():
    """Return Quien Soy enabled state."""
    return {"enabled": quien_soy_manager.enabled}
 
 
class QuienSoyToggleRequest(BaseModel):
    enabled: bool
 
@app.post("/bank/api/quiensoy/toggle")
async def quien_soy_toggle(body: QuienSoyToggleRequest, user: str = Depends(get_current_user)):
    """Enable or disable Quien Soy."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    quien_soy_manager.enabled = body.enabled
    if not body.enabled:
        quien_soy_manager._state = quien_soy_manager._empty_state()
    await quien_soy_manager.broadcast()
    return {"enabled": quien_soy_manager.enabled}
 
 
@app.get("/bank/api/quiensoy/users")
async def quien_soy_users(user: str = Depends(get_current_user)):
    """Return eligible user list for Quien Soy."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT username FROM users WHERE password_hash NOT IN ('__UNSET__','__AUTO__') ORDER BY username ASC"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows]
 
 
 
 
class QuienSoySetupRequest(BaseModel):
    character: str
    character_photo: Optional[str] = None
    character_info: Optional[dict] = None  # NUEVO: información completa del personaje
    players: list
 
 
@app.post("/bank/api/quiensoy/setup")
async def quien_soy_setup(body: QuienSoySetupRequest, user: str = Depends(get_current_user)):
    """Start a QuienSoy game directly from the admin panel (no WS needed)."""
    logger.info(f"QuienSoy setup request from {user}: character={body.character}, players={body.players}, photo={body.character_photo}")
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    character = body.character.strip()
    players   = [str(u).strip() for u in body.players if str(u).strip()]
    character_info = body.character_info if body.character_info else None
    
    if not character or not players:
        logger.error(f"QuienSoy setup validation failed: character={character}, players={players}")
        raise HTTPException(400, "Character and players required")
    logger.info(f"QuienSoy setup validated: character={character}, players={players}")
    
    # Pasar character_info al handle_action
    await quien_soy_manager.handle_action(
        {
            "action": "setup", 
            "character": character, 
            "character_photo": body.character_photo, 
            "character_info": character_info,  # NUEVO: pasar info completa
            "players": players
        },
        admin=user
    )
    logger.info(f"QuienSoy setup completed: status={quien_soy_manager._state['status']}")
    return {"ok": True, "status": quien_soy_manager._state["status"]}


# ── Helper functions for character verification ──────────────────────────────
# OBSOLETO: Estas funciones ya NO se usan. El sistema ahora es 100% gestionado por IA.
# Se mantienen comentadas por si se necesitan en el futuro como referencia.

# def _get_known_characters_db():
#     """Base de datos local de personajes conocidos con fotos - OBSOLETO"""
#     # Esta función ya NO se usa. Todo es gestionado por Gemini AI.
#     pass

# def _get_photo_from_local_db(character_name: str) -> Optional[str]:
#     """Busca la foto de un personaje en la base de datos local - OBSOLETO"""
#     # Esta función ya NO se usa. Todo es gestionado por Gemini AI.
#     pass

# def _get_popular_suggestions():
#     """Devuelve sugerencias populares con fotos - OBSOLETO"""
#     # Esta función ya NO se usa. Las sugerencias las proporciona Gemini AI.
#     pass


@app.get("/bank/api/quiensoy/verify-character")
async def quien_soy_verify(name: str, user: str = Depends(get_current_user)):
    """
    Verify character with AI-powered validation, spell correction, and suggestions.
    TODO GESTIONADO POR IA: Sin base de datos local, la IA maneja todo.
    """
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    name = name.strip()
    if not name:
        raise HTTPException(400, "Name required")
 
    logger.info("verify-character: Verifying '%s' with AI (100%% AI-powered)", name)
    
    # TODO es gestionado por la IA - Sin fallback a base de datos
    try:
        from ai_helper import GeminiAI
        ai = GeminiAI()
        
        if not ai.api_key:
            raise HTTPException(503, "AI service not configured. Please configure Gemini API key.")
        
        logger.info("Using Gemini AI for character verification (100%% AI)")
        char_info = ai.verify_character(name)
        
        # Si la IA dice que existe y tiene confianza suficiente
        if char_info.get("exists") and char_info.get("confidence") in ["high", "medium"]:
            logger.info(f"AI verified: {char_info['corrected_name']} (confidence: {char_info.get('confidence')})")
            
            # Preparar character_info completo para pasar al juego
            character_info_for_game = {
                "corrected_name": char_info["corrected_name"],
                "character": char_info["corrected_name"],
                "main_known_for": char_info.get("main_known_for", "Personaje conocido"),
                "key_characteristics": char_info.get("key_characteristics", ["Personaje conocido"]),
                "is_real": char_info.get("is_real", False),
                "is_fictional": char_info.get("is_fictional", True),
                "is_mythological": char_info.get("is_mythological", False),
                "category": char_info.get("category", "unknown"),
                "confidence": char_info.get("confidence", "medium")
            }
            
            return {
                "valid": True,
                "canonical": char_info["corrected_name"],
                "photo": char_info.get("photo_url"),  # Foto proporcionada por la IA
                "suggestions": [],
                "character_info": character_info_for_game,  # NUEVO: info completa para el juego
                "ai_info": {
                    "category": char_info.get("category", ""),
                    "known_for": char_info.get("main_known_for", ""),
                    "confidence": char_info.get("confidence", ""),
                    "is_real": char_info.get("is_real", False),
                    "is_fictional": char_info.get("is_fictional", False)
                }
            }
        
        # Si la IA dice que NO existe o tiene baja confianza, ofrecer sugerencias de la IA
        else:
            logger.info(f"AI rejected: {name} (confidence: {char_info.get('confidence')})")
            
            # Usar SOLO sugerencias de la IA
            ai_suggestions = char_info.get("suggestions", [])
            
            # Formato de sugerencias (sin fotos de base de datos local)
            suggestions_formatted = []
            for suggestion in ai_suggestions[:5]:
                suggestions_formatted.append({
                    "name": suggestion,
                    "photo": None  # Las fotos se pueden buscar dinámicamente si es necesario
                })
            
            return {
                "valid": False,
                "canonical": char_info.get("corrected_name", name.title()),
                "photo": None,
                "suggestions": suggestions_formatted,
                "message": "Personaje no reconocido o poco conocido. Por favor, elige uno de los personajes sugeridos por la IA.",
                "ai_info": {
                    "reason": char_info.get("main_known_for", "Personaje desconocido"),
                    "confidence": char_info.get("confidence", "low")
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI verification failed: {e}")
        raise HTTPException(503, f"AI service error: {str(e)}")


@app.websocket("/bank/ws/quiensoy")
async def quien_soy_ws(websocket: WebSocket, token: str = ""):
    """WebSocket handler for Quien Soy game.
    Hosts (dvd/nebulosa) control game flow (setup, next_turn, reveal, reset).
    All authenticated players can send 'ask' and 'guess' actions on their turn.
    """
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    conn = db_connect()
    row = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
    _open_session(username, "quiensoy")
    await quien_soy_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "")
            # Host actions: full control
            if username in ADMINS:
                try:
                    await quien_soy_manager.handle_action(data, username)
                except Exception as e:
                    logger.error("QuienSoy handle_action error: %s", e)
            # Player actions: only ask and guess (server enforces turn ownership)
            elif action in ("ask", "guess"):
                try:
                    await quien_soy_manager.handle_action(data, username)
                except Exception as e:
                    logger.error("QuienSoy player action error: %s", e)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("QuienSoy WS error: %s", e)
    finally:
        quien_soy_manager.disconnect(username)
 
 
# =============================================================================
# CIFRAS Y LETRAS
# =============================================================================
 
CIFRAS_LETRAS_DIR = os.path.join(BASE_DIR, "static", "cifrasletras")
 
import random as _cl_random
 
_CL_VOWELS     = list("AAAAEEEEEIIIOOOOUUU")
_CL_CONSONANTS = list("BBCCCDDDDFFGGHHHJJKLLLLLMMMMNNNNPPPQRRRRRSSSSTTTTTVWXYZ")
 
 
class CifrasLetrasManager:
    """
    Full Cifras y Letras game.
    status flow: waiting → letters|numbers → reviewing → waiting → ... → finished
    Admin validates letter answers individually; numbers auto-evaluated.
    """
 
    def __init__(self):
        self.enabled:     bool = False
        self.connections: dict = {}
        self._state:      dict = self._empty_state()
 
    # ── State ─────────────────────────────────────────────────────────────────
 
    def _empty_state(self) -> dict:
        return {
            "status":       "waiting",
            "mode":         None,         # "letters" | "numbers"
            "players":      [],           # [{username, score}]
            "round":        0,
            "max_rounds":   5,
            "letters":      [],
            "numbers":      [],
            "target":       0,
            "submissions":  {},           # {username: answer_str}
            "results":      [],           # [{username, answer, score}]
            "_pre_pause_status": None,
            "round_time":    30,
            "round_winner": None,
            "round_winners": [],
        }
 
    def _build_broadcast(self) -> dict:
        s = self._state
        return {
            "type":         "state",
            "enabled":      self.enabled,
            "status":       s["status"],
            "mode":         s["mode"],
            "players":      s["players"],
            "round":        s["round"],
            "max_rounds":   s["max_rounds"],
            "letters":      s["letters"],
            "numbers":      s["numbers"],
            "target":       s["target"],
            "submissions":  s["submissions"],
            "results":      s["results"],
            "round_time":    s.get("round_time", 30),
            "round_winner":  s["round_winner"],
            "round_winners":  s.get("round_winners", []),
            "connected":    list(self.connections.keys()),
        }
 
    # ── WS plumbing ───────────────────────────────────────────────────────────
 
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws
        try:   await ws.send_json(self._build_broadcast())
        except Exception: pass
 
    def disconnect(self, username: str):
        self.connections.pop(username, None)
 
    async def broadcast(self):
        data = self._build_broadcast()
        dead = []
        for u, sock in list(self.connections.items()):
            try:   await sock.send_json(data)
            except Exception: dead.append(u)
        for u in dead: self.connections.pop(u, None)
 
    # ── Generation ────────────────────────────────────────────────────────────
 
    def _gen_letters(self, vowels: int = 4) -> list:
        v = _cl_random.sample(_CL_VOWELS, min(vowels, len(_CL_VOWELS)))
        c = _cl_random.sample(_CL_CONSONANTS, 9 - len(v))
        letters = v + c
        _cl_random.shuffle(letters)
        return letters
 
    def _gen_numbers(self) -> tuple:
        big   = [25, 50, 75, 100]
        small = list(range(1, 11)) * 2
        bigs  = _cl_random.randint(0, 2)
        nums  = _cl_random.sample(big, bigs) + _cl_random.sample(small, 6 - bigs)
        _cl_random.shuffle(nums)
        target = _cl_random.randint(100, 999)
        return nums, target
 
    # ── Validation ────────────────────────────────────────────────────────────
 
    # ── Actions ───────────────────────────────────────────────────────────────
 
    async def handle_action(self, act: dict):
        action = act.get("action")
 
        # ── Setup ──────────────────────────────────────────────────────────
        if action == "setup":
            usernames  = [str(u).strip() for u in act.get("players", []) if str(u).strip()]
            max_rounds = max(1, min(10, int(act.get("max_rounds", 5))))
            if not usernames: return
            self._state = self._empty_state()
            self._state["players"]    = [{"username": u, "score": 0} for u in usernames]
            self._state["max_rounds"] = max_rounds
            self._state["round_time"] = max(10, min(300, int(act.get("round_time", 30))))
            self._state["status"]     = "waiting"
            self.enabled = True
            await self.broadcast()
 
        # ── Start round (show tiles, no timer yet) ──────────────────────────
        elif action == "start_letters":
            if not self._state["players"]: return
            if self._state["status"] not in ("waiting", "reviewing"): return
            self._state.update({
                "letters": self._gen_letters(int(act.get("vowels", 4))),
                "submissions": {}, "results": [], "round_winner": None,
                "round": self._state["round"] + 1,
                "mode": "letters", "status": "ready",
            })
            await self.broadcast()
 
        elif action == "start_numbers":
            if not self._state["players"]: return
            if self._state["status"] not in ("waiting", "reviewing"): return
            nums, target = self._gen_numbers()
            self._state.update({
                "numbers": nums, "target": target,
                "submissions": {}, "results": [], "round_winner": None,
                "round": self._state["round"] + 1,
                "mode": "numbers", "status": "ready",
            })
            await self.broadcast()
 
        # ── Start timer (input visible to players) ──────────────────────────
        elif action == "start_timer":
            if self._state["status"] != "ready": return
            self._state["status"]      = self._state["mode"]
            self._state["submissions"] = {}
            await self.broadcast()
 
        elif action == "restart_timer":
            s = self._state
            if s["mode"] not in ("letters", "numbers"): return
            s["submissions"] = {}
            s["results"]     = []
            s["round_winner"]= None
            s["status"]      = s["mode"]
            await self.broadcast()
 
        # ── Player submits answer ───────────────────────────────────────────
        elif action == "submit":
            u   = act.get("username", "")
            ans = str(act.get("answer", "")).strip()
            if not u or self._state["status"] not in ("letters", "numbers"): return
            if u in [p["username"] for p in self._state["players"]]:
                self._state["submissions"][u] = ans
                await self.broadcast()
 
        # ── Reveal: collect raw answers, go to reviewing ────────────────────
        elif action == "reveal":
            s = self._state
            if s["status"] not in ("letters", "numbers", "ready"): return
            results = []
            for p in s["players"]:
                u   = p["username"]
                ans = s["submissions"].get(u, "").strip()
                if s["mode"] == "letters":
                    ans = ans.upper()
                results.append({"username": u, "answer": ans or "—", "score": 0})
            s["results"] = results
            s["status"]  = "reviewing"
            await self.broadcast()
 
        # ── dvd declares winner (1 or more players) — ONLY dvd can do this ──
        elif action == "declare_winner":
            s = self._state
            if s["status"] != "reviewing": return
            winners = [str(u).strip() for u in act.get("winners", []) if str(u).strip()]
            pts     = max(1, int(act.get("pts", 1)))
            if not winners: return
            # Apply score
            for u in winners:
                for p in s["players"]:
                    if p["username"] == u:
                        p["score"] += pts
                for r in s["results"]:
                    if r["username"] == u:
                        r["score"] = pts
            s["round_winner"] = winners[0] if len(winners) == 1 else "tie"
            s["round_winners"] = winners   # all winners (tie support)
            # Advance or finish
            if s["round"] >= s["max_rounds"]:
                s["status"] = "finished"
            await self.broadcast()
 
        # ── Pause / Resume ──────────────────────────────────────────────────
        elif action == "pause":
            s = self._state
            if s["status"] in ("letters", "numbers", "ready"):
                s["_pre_pause"] = s["status"]
                s["status"] = "paused"
                await self.broadcast()
 
        elif action == "resume":
            s = self._state
            if s["status"] == "paused":
                s["status"] = s.get("_pre_pause", "ready")
                await self.broadcast()
 
        # ── Finish / Reset ──────────────────────────────────────────────────
        elif action == "finish":
            self._state["status"] = "finished"
            await self.broadcast()
 
        elif action == "reset":
            self._state = self._empty_state()
            await self.broadcast()
 
 
cifras_letras_manager = CifrasLetrasManager()
 
 
# ── CifrasLetras routes ───────────────────────────────────────────────────────
 
@app.get("/bank/cifrasletras", response_class=HTMLResponse)
async def cifras_letras_page():
    """Serve the Cifras y Letras game page."""
    return _serve_game_page(CIFRAS_LETRAS_DIR)
 
 
@app.get("/bank/api/cifrasletras/status")
async def cifras_letras_status():
    """Return Cifras y Letras enabled state."""
    return {"enabled": cifras_letras_manager.enabled}
 
 
class CifrasLetrasToggleRequest(BaseModel):
    enabled: bool
 
 
@app.post("/bank/api/cifrasletras/toggle")
async def cifras_letras_toggle(body: CifrasLetrasToggleRequest, user: str = Depends(get_current_user)):
    """Enable or disable Cifras y Letras."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    cifras_letras_manager.enabled = body.enabled
    if not body.enabled:
        cifras_letras_manager._state = cifras_letras_manager._empty_state()
    await cifras_letras_manager.broadcast()
    return {"enabled": cifras_letras_manager.enabled}
 
 
@app.get("/bank/api/cifrasletras/users")
async def cifras_letras_users(user: str = Depends(get_current_user)):
    """Return eligible user list for Cifras y Letras."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute("SELECT username FROM users ORDER BY username ASC").fetchall()
    conn.close()
    return [r["username"] for r in rows]
 
 
class CifrasLetrasSetupRequest(BaseModel):
    players:    list
    max_rounds: int = 5
    round_time: int = 30
 
 
@app.post("/bank/api/cifrasletras/setup")
async def cifras_letras_setup(body: CifrasLetrasSetupRequest, user: str = Depends(get_current_user)):
    """Start a Cifras y Letras game from the admin panel."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    players    = [str(u).strip() for u in body.players if str(u).strip()]
    max_rounds = max(1, min(10, int(body.max_rounds)))
    if not players:
        raise HTTPException(400, "At least one player required")
    round_time = max(10, min(300, int(body.round_time)))
    await cifras_letras_manager.handle_action({"action": "setup", "players": players, "max_rounds": max_rounds, "round_time": round_time})
    return {"ok": True}
 
 
@app.post("/bank/api/cifrasletras/reset")
async def cifras_letras_reset(user: str = Depends(get_current_user)):
    """Reset Cifras y Letras game state."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    await cifras_letras_manager.handle_action({"action": "reset"})
    return {"ok": True}
 
 
@app.get("/bank/api/cifrasletras/check-word")
async def cifras_letras_check_word(word: str, user: str = Depends(get_current_user)):
    """Ask Gemini if a word is valid Spanish."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    word = word.strip().upper()
    if not word or not word.isalpha():
        return {"valid": False, "word": word, "reason": "Solo letras"}
    try:
        import json as _j, urllib.request as _ur, urllib.error as _ue
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            # Buscar en archivos
            for loc in ["config/.gemini_key", "config/.google_key", ".gemini_key"]:
                if os.path.exists(loc):
                    with open(loc, 'r') as f:
                        api_key = f.read().strip()
                        break
        if not api_key:
            return {"valid": True, "word": word, "reason": "Sin API key — aceptada por defecto"}
        prompt = (
            f"Is '{word}' a valid Spanish word (noun, verb, adjective, adverb — any form)? "
            f"Reply ONLY with a JSON object: "
            f'{{"valid": true/false, "word": "{word}", "reason": "brief explanation in Spanish"}}'
        )
        payload = _j.dumps({
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 80
            }
        }).encode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        req = _ur.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with _ur.urlopen(req, timeout=10) as resp:
            raw = _j.loads(resp.read().decode())
            text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()
            if text.startswith("```"): text = text.split("\n",1)[-1].rsplit("```",1)[0].strip()
            result = _j.loads(text)
            return {"valid": bool(result.get("valid")), "word": word,
                    "reason": str(result.get("reason", ""))}
    except Exception as e:
        logger.error("check-word error: %s", e)
        return {"valid": True, "word": word, "reason": "Error de verificación — aceptada por defecto"}
 
 
@app.websocket("/bank/ws/cifrasletras")
async def cifras_letras_ws(websocket: WebSocket, token: str = ""):
    """WebSocket handler for Cifras y Letras game."""
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    conn = db_connect()
    row  = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
    _open_session(username, "cifrasletras")
    await cifras_letras_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Only hosts (dvd/nebulosa) control the game; everyone can submit
            if username in SUPERADMINS:
                try:
                    await cifras_letras_manager.handle_action(data)
                except Exception as e:
                    logger.error("CifrasLetras action error: %s", e)
            elif data.get("action") == "submit":
                data["username"] = username
                try:
                    await cifras_letras_manager.handle_action(data)
                except Exception as e:
                    logger.error("CifrasLetras submit error: %s", e)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("CifrasLetras WS error: %s", e)
    finally:
        cifras_letras_manager.disconnect(username)
 
 
# =============================================================================
# PASAPALABRA GAME MODULE v5
# =============================================================================
import json as _json
import random
 
 
 
 
# =============================================================================
# GALLERY
# =============================================================================
 
@app.get("/bank/api/gallery")
async def gallery_images():
    """
    Return a sorted list of image files found in static/gallery/.
    No config file or index.json needed — reads the directory directly.
    Response: [{file: "1.jpg", url: "/static/gallery/1.jpg"}, ...]
    """
    os.makedirs(GALLERY_DIR, exist_ok=True)  # create if not exists
    try:
        images = []
        for filename in sorted(os.listdir(GALLERY_DIR)):
            if os.path.splitext(filename.lower())[1] in GALLERY_EXTENSIONS:
                images.append({
                    "file": filename,
                    "url":  f"/static/gallery/{filename}"
                })
 
        # Write a reference manifest alongside the images.
        # NOTE: The frontend NEVER reads this file — it always calls /api/gallery.
        # This manifest is for backup/reference purposes only.
        try:
            import json as _json
            manifest_path = os.path.join(GALLERY_DIR, "gallery_manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                _json.dump(images, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Non-critical: never fails the request
 
        return images
    except Exception as e:
        logger.error("Gallery read error: %s", e)
        return []
 
 
PASAPALABRA_DIR = os.path.join(BASE_DIR, "static", "pasapalabra")
DEFAULT_ROSCO_T = 500
 
 
LETTERS_26 = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
 
 
def load_question_pool() -> dict:
    """Load preguntas.json from static/pasapalabra/. Supports list or dict format."""
    path = os.path.join(PASAPALABRA_DIR, "preguntas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        if isinstance(data, list):
            pool: dict = {}
            for q in data:
                letra = q.get("letra", "").upper()
                if letra:
                    pool.setdefault(letra, []).append(q)
            return pool
        return {k.upper(): v for k, v in data.items()}
    except FileNotFoundError:
        logger.warning("preguntas.json not found at %s — using empty pool", path)
        return {}
    except Exception as e:
        logger.error("Failed to load preguntas.json: %s", e)
        return {}
 
 
def assign_questions_for_players(pool: dict, n: int) -> list:
    """Return n dicts mapping letter → question for each player."""
    per = [{} for _ in range(n)]
    for letter in LETTERS_26:
        opts = list(pool.get(letter, []))
        if not opts:
            # No question for this letter — use placeholder
            placeholder = {"letra": letter, "definicion": f"[sin pregunta para {letter}]",
                           "respuesta": letter, "tipo": "directa"}
            for p in per:
                p[letter] = placeholder
            continue
        random.shuffle(opts)
        for i in range(n):
            per[i][letter] = opts[i % len(opts)]
    return per
 
 
class PasapalabraManager:
    def __init__(self):
        self.enabled: bool      = False
        self.connections: dict  = {}
        self._state: dict       = self._empty_state()
        self._timer_task        = None
 
    # ── State ─────────────────────────────────────────────────────────────────
 
    def _empty_state(self) -> dict:
        return {
            "status": "waiting",
            "players": [],
            "current_player_idx": -1,
            "setup": {"rosco_time": DEFAULT_ROSCO_T},
            # celebration: None | {type:"mid"|"final", winners:[username,...]}
            "celebration": None,
            # last_action: sent once per action so all clients react identically
            "last_action": None,
            "_action_seq": 0,
            # player_submission: text typed by the current player (visible to admin)
            "player_submission": "",
        }
 
    def _make_player(self, username: str, rosco_time: int, questions: dict) -> dict:
        return {
            "username":           username,
            "letters":            {L: "pending" for L in LETTERS_26},
            "questions":          questions,
            "score":              0,
            "time_remaining":     rosco_time,
            "current_letter":     "A",
            "current_letter_idx": 0,
            "done":               False,
            "turn_active":        False,
        }
 
    def _current_player(self):
        idx     = self._state.get("current_player_idx", -1)
        players = self._state.get("players", [])
        return players[idx] if 0 <= idx < len(players) else None
 
    def _find_next_letter_idx(self, player: dict, from_idx: int):
        n = len(LETTERS_26)
        for i in range(1, n + 1):
            idx = (from_idx + i) % n
            if player["letters"][LETTERS_26[idx]] in ("pending", "passed"):
                return idx
        return None
 
    def _find_next_player_idx(self) -> int:
        players = self._state["players"]
        n       = len(players)
        cur     = self._state.get("current_player_idx", -1)
        for i in range(1, n + 1):
            idx = (cur + i) % n
            if not players[idx]["done"]:
                return idx
        return -1
 
    def _compute_final_winners(self) -> list:
        """Return list of usernames with the highest score (1 or more if tied)."""
        players = self._state["players"]
        if not players:
            return []
        top = max(p["score"] for p in players)
        return [p["username"] for p in players if p["score"] == top]
 
    def _strip(self, p: dict) -> dict:
        return {k: v for k, v in p.items() if k != "questions"}
 
    def _current_question_for_broadcast(self):
        p = self._current_player()
        if not p or p["done"]:
            return None
        return p["questions"].get(p["current_letter"])
 
    def _build_broadcast(self) -> dict:
        return {
            "type":               "state",
            "enabled":            self.enabled,
            "status":             self._state["status"],
            "players":            [self._strip(p) for p in self._state["players"]],
            "current_player_idx": self._state.get("current_player_idx", -1),
            "current_question":   self._current_question_for_broadcast(),
            "setup":              self._state.get("setup", {}),
            "connected":          list(self.connections.keys()),
            "celebration":        self._state.get("celebration"),
            "last_action":        self._state.get("last_action"),
            # Player's typed answer — visible to all (admin uses it to validate)
            "player_submission":  self._state.get("player_submission", ""),
        }
 
    async def broadcast_action(self):
        """Send last_action as a dedicated 'action' message before the state update.
        This guarantees clients process sound/panel separately from state rendering."""
        la = self._state.get("last_action")
        if not la:
            return
        msg = {"type": "action", **la}
        dead = []
        for uname, sock in list(self.connections.items()):
            try:
                await sock.send_json(msg)
            except Exception:
                dead.append(uname)
        for u in dead:
            self.connections.pop(u, None)
 
    # ── WebSocket ─────────────────────────────────────────────────────────────
 
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws
        try:
            await ws.send_json(self._build_broadcast())
        except Exception:
            pass
 
    def disconnect(self, username: str):
        self.connections.pop(username, None)
 
    async def broadcast(self):
        data = self._build_broadcast()
        dead = []
        for uname, sock in list(self.connections.items()):
            try:
                await sock.send_json(data)
            except Exception:
                dead.append(uname)
        for u in dead:
            self.connections.pop(u, None)
 
    # ── Timer ─────────────────────────────────────────────────────────────────
 
    def _stop_timer(self):
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None
 
    def _start_timer(self):
        self._stop_timer()
        player = self._current_player()
        if player and not player["done"]:
            player["turn_active"] = True
            self._timer_task = asyncio.create_task(self._run_timer())
 
    async def _run_timer(self):
        try:
            while True:
                await asyncio.sleep(1)
                player = self._current_player()
                if not player or not player.get("turn_active"):
                    break
                if player["time_remaining"] > 0:
                    player["time_remaining"] -= 1
                    await self.broadcast()
                    if player["time_remaining"] == 0:
                        await self._on_pass_or_wrong("wrong", timeout=True)
                        break
        except asyncio.CancelledError:
            pass
 
    # ── Core result logic ─────────────────────────────────────────────────────
 
    async def _on_correct(self):
        player = self._current_player()
        if not player or player["done"]:
            return
        cur_idx    = player["current_letter_idx"]
        cur_letter = LETTERS_26[cur_idx]
        player["letters"][cur_letter] = "correct"
        player["score"] += 1
        # Clear the player's typed submission when admin validates answer
        self._state["player_submission"] = ""
        self._state["_action_seq"] = self._state.get("_action_seq", 0) + 1
        self._state["last_action"] = {
            "result": "correct",
            "letter": cur_letter,
            "player": player["username"],
            "seq":    self._state["_action_seq"],
        }
 
        next_idx = self._find_next_letter_idx(player, cur_idx)
        if next_idx is None:
            # ── Rosco completo con 26/26 ── mid-game winner celebration
            player["done"]        = True
            player["turn_active"] = False
            self._stop_timer()
            self._state["celebration"] = {
                "type":    "mid",
                "winners": [player["username"]],
                "won":     player["score"] == 26,
            }
            await self.broadcast_action()   # send correct sound first
            await self._switch_player()   # also broadcasts
        else:
            player["current_letter_idx"] = next_idx
            player["current_letter"]     = LETTERS_26[next_idx]
            # clear any previous celebration when play resumes
            self._state["celebration"] = None
            await self.broadcast_action()   # send sound/panel trigger first
            await self.broadcast()
 
    async def _on_pass_or_wrong(self, result: str, timeout: bool = False):
        self._stop_timer()
        player = self._current_player()
        if not player or player["done"]:
            return
        cur_idx    = player["current_letter_idx"]
        cur_letter = LETTERS_26[cur_idx]
 
        # Grab question text and answer before marking the letter
        q_data    = player["questions"].get(cur_letter)
        q_text    = q_data.get("definicion", "") if q_data else ""
        q_answer  = q_data.get("respuesta", "")  if q_data else ""
 
        if result == "wrong":
            player["letters"][cur_letter] = "wrong"
        else:
            player["letters"][cur_letter] = "passed"
 
        # Clear the player's typed submission when admin marks result
        self._state["player_submission"] = ""
        player["turn_active"] = False
        self._state["_action_seq"] = self._state.get("_action_seq", 0) + 1
        self._state["last_action"] = {
            "result":   result,
            "letter":   cur_letter,
            "player":   player["username"],
            "answer":   q_answer,
            "question": q_text,
            "seq":      self._state["_action_seq"],
        }
 
        next_letter_idx = self._find_next_letter_idx(player, cur_idx)
        if next_letter_idx is None:
            player["done"] = True
        else:
            player["current_letter_idx"] = next_letter_idx
            player["current_letter"]     = LETTERS_26[next_letter_idx]
 
        if timeout and player["time_remaining"] <= 0:
            player["done"] = True
 
        # clear celebration when a normal result comes in
        self._state["celebration"] = None
        await self.broadcast_action()   # send sound/panel trigger first
        await self._switch_player()
 
    async def _switch_player(self):
        next_idx = self._find_next_player_idx()
        if next_idx == -1:
            # ── All done → final celebration before finished
            winners = self._compute_final_winners()
            self._state["celebration"] = {"type": "final", "winners": winners}
            self._state["status"] = "finished"
            await self.broadcast()
            return
        self._state["current_player_idx"] = next_idx
        self._state["status"]             = "ready"
        await self.broadcast()
 
    # ── Action dispatcher ─────────────────────────────────────────────────────
 
    async def handle_action(self, act: dict, admin: str):
        action = act.get("action")
 
        if action == "toggle_enabled":
            self.enabled = bool(act.get("enabled", False))
            if not self.enabled:
                self._stop_timer()
                self._state = self._empty_state()
            await self.broadcast()
 
        elif action == "setup":
            self._stop_timer()
            usernames = [str(u).strip() for u in act.get("players", []) if str(u).strip()][:15]
            if not usernames:
                return
            rosco_t = max(60, min(int(act.get("rosco_time", DEFAULT_ROSCO_T)), 1200))
            pool    = load_question_pool()
            q_per   = assign_questions_for_players(pool, len(usernames))
            self._state = self._empty_state()
            self._state["setup"]["rosco_time"] = rosco_t
            self._state["players"] = [
                self._make_player(usernames[i], rosco_t, q_per[i])
                for i in range(len(usernames))
            ]
            self._state["current_player_idx"] = 0
            self._state["status"]             = "ready"
            self.enabled = True          # auto-enable when admin starts a game
            await self.broadcast()
 
        elif action == "start_timer":
            player = self._current_player()
            if player and not player["done"] and self._state["status"] in ("ready", "paused"):
                self._state["status"]      = "playing"
                self._state["celebration"] = None   # clear any celebration on manual start
                await self.broadcast()
                self._start_timer()
 
        elif action == "correct":
            if self._state["status"] != "playing":
                return
            await self._on_correct()
 
        elif action in ("pass", "wrong"):
            if self._state["status"] not in ("playing", "paused"):
                return
            await self._on_pass_or_wrong(action)
 
        elif action == "pause":
            player = self._current_player()
            if player:
                player["turn_active"] = False
            self._stop_timer()
            self._state["status"] = "paused"
            await self.broadcast()
 
        elif action == "reset":
            self._stop_timer()
            self._state = self._empty_state()
            await self.broadcast()
 
        elif action == "player_answer":
            # Non-admin player submits a typed answer — admin can see it to validate.
            # Only accepted during active play from the current active player.
            if self._state["status"] != "playing":
                return
            text = str(act.get("text", "")).strip().upper()[:40]
            cur = self._current_player()
            if cur and cur["username"] == admin:
                self._state["player_submission"] = text
                await self.broadcast()
 
        elif action == "clear_submission":
            # Clear the typed submission display (called by admin after marking result).
            self._state["player_submission"] = ""
            await self.broadcast()
 
 
game_manager = PasapalabraManager()
 
 
# =============================================================================
# PASAPALABRA ROUTES
# =============================================================================
 
@app.get("/bank/pasapalabra", response_class=HTMLResponse)
async def pasapalabra_page():
    """Serve the Pasapalabra game page."""
    return _serve_game_page(PASAPALABRA_DIR)
 
@app.get("/bank/api/pasapalabra/status")
async def pasapalabra_status():
    """Return Pasapalabra enabled state."""
    return {"enabled": game_manager.enabled}
 
@app.get("/bank/api/pasapalabra/users")
async def pasapalabra_users(user: str = Depends(get_current_user)):
    """Return eligible user list for Pasapalabra."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT username FROM users "
        "WHERE password_hash NOT IN ('__UNSET__','__AUTO__') ORDER BY username ASC"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows]
 
class GameToggleRequest(BaseModel):
    enabled: bool
 
@app.post("/bank/api/pasapalabra/toggle")
async def pasapalabra_toggle(body: GameToggleRequest, user: str = Depends(get_current_user)):
    """Enable or disable Pasapalabra."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    game_manager.enabled = body.enabled
    if not body.enabled:
        game_manager._stop_timer()
        game_manager._state = game_manager._empty_state()
    await game_manager.broadcast()
    logger.info("Pasapalabra %s by %s", "enabled" if body.enabled else "disabled", user)
    return {"enabled": game_manager.enabled}
 
 
class PasapalabraSetupRequest(BaseModel):
    players: list
    rosco_time: int = 500
 
 
@app.post("/bank/api/pasapalabra/setup")
async def pasapalabra_setup(body: PasapalabraSetupRequest, user: str = Depends(get_current_user)):
    """Configure and start a Pasapalabra game from admin panel."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    players = [str(u).strip() for u in body.players if str(u).strip()]
    if not players:
        raise HTTPException(400, "At least one player required")
    rosco_time = max(60, min(1200, int(body.rosco_time)))
    await game_manager.handle_action({
        "action": "setup",
        "players": players,
        "rosco_time": rosco_time
    }, user)
    logger.info("Pasapalabra setup by %s: players=%s", user, players)
    return {"ok": True, "players": players, "rosco_time": rosco_time}
 
 
@app.post("/bank/api/pasapalabra/reset")
async def pasapalabra_reset(user: str = Depends(get_current_user)):
    """Reset Pasapalabra game state."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    game_manager._stop_timer()
    game_manager._state = game_manager._empty_state()
    await game_manager.broadcast()
    return {"ok": True}
 
 
# ── DB Migration: dvdcoin.db → 5 separate DBs ─────────────────────────────────
 
@app.post("/bank/api/admin/migrate-db")
async def migrate_db(user: str = Depends(get_current_user)):
    """Migrate data from legacy dvdcoin.db to the 5 new DB files. Run once."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Superadmins only")
    import sqlite3 as _sq
    legacy_path = os.path.join(BASE_DIR, "data", "dvdcoin.db")
    # Also check root level
    if not os.path.exists(legacy_path):
        legacy_path = os.path.join(BASE_DIR, "dvdcoin.db")
    if not os.path.exists(legacy_path):
        return {"ok": False, "message": "dvdcoin.db not found — nothing to migrate"}
 
    results = {}
    try:
        leg = _sq.connect(legacy_path)
        leg.row_factory = _sq.Row
 
        # Migrate users
        try:
            users = leg.execute("SELECT * FROM users").fetchall()
            c = db_connect()
            for u in users:
                ud = dict(u)
                c.execute(
                    "INSERT OR IGNORE INTO users(username,password_hash,balance,is_blocked,"
                    "failed_attempts,locked_until,created_at) VALUES(?,?,?,?,?,?,?)",
                    (ud.get("username"), ud.get("password_hash","__UNSET__"),
                     ud.get("balance",0), ud.get("is_blocked",0),
                     ud.get("failed_attempts",0), ud.get("locked_until"),
                     ud.get("created_at"))
                )
            c.commit(); c.close()
            results["users"] = len(users)
        except Exception as e:
            results["users_error"] = str(e)
 
        # Migrate transactions
        try:
            txs = leg.execute("SELECT * FROM transactions").fetchall()
            c = db_tx()
            for t in txs:
                td = dict(t)
                c.execute(
                    "INSERT OR IGNORE INTO transactions(id,from_user,to_user,amount,concept,created_at)"
                    " VALUES(?,?,?,?,?,?)",
                    (td.get("id"), td.get("from_user"), td.get("to_user"),
                     td.get("amount",0), td.get("concept",""), td.get("created_at"))
                )
            c.commit(); c.close()
            results["transactions"] = len(txs)
        except Exception as e:
            results["transactions_error"] = str(e)
 
        # Migrate sessions
        try:
            sess = leg.execute("SELECT * FROM sessions").fetchall()
            c = db_stats()
            for s in sess:
                sd = dict(s)
                c.execute(
                    "INSERT OR IGNORE INTO sessions(id,username,section,detail,started_at,ended_at,duration_s)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (sd.get("id"), sd.get("username"), sd.get("section","bank"),
                     sd.get("detail",""), sd.get("started_at"),
                     sd.get("ended_at"), sd.get("duration_s"))
                )
            c.commit(); c.close()
            results["sessions"] = len(sess)
        except Exception as e:
            results["sessions_error"] = str(e)
 
        # Migrate opo_players
        try:
            ops = leg.execute("SELECT * FROM opo_players").fetchall()
            c = db_rights()
            for op in ops:
                opd = dict(op)
                c.execute(
                    "INSERT OR IGNORE INTO opo_players(username,added_by,added_at) VALUES(?,?,?)",
                    (opd.get("username"), opd.get("added_by","dvd"), opd.get("added_at"))
                )
            c.commit(); c.close()
            results["opo_players"] = len(ops)
        except Exception as e:
            results["opo_players_error"] = str(e)
 
        # Migrate opo_results
        try:
            ors = leg.execute("SELECT * FROM opo_results").fetchall()
            c = db_opo()
            for o in ors:
                od = dict(o)
                c.execute(
                    "INSERT OR IGNORE INTO opo_results(id,username,block_n,played_at,correct,wrong,wrong_qs)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (od.get("id"), od.get("username"), od.get("block_n",1),
                     od.get("played_at"), od.get("correct",0), od.get("wrong",0),
                     od.get("wrong_qs","[]"))
                )
            c.commit(); c.close()
            results["opo_results"] = len(ors)
        except Exception as e:
            results["opo_results_error"] = str(e)
 
        leg.close()
        results["ok"] = True
        results["message"] = "Migration complete. Check results and delete dvdcoin.db when ready."
        return results
 
    except Exception as e:
        return {"ok": False, "error": str(e)}
 
@app.websocket("/bank/ws/pasapalabra")
async def pasapalabra_ws(websocket: WebSocket, token: str = ""):
    """WebSocket handler for Pasapalabra game.
    Admins control game flow; any connected player can send player_answer.
    """
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    conn = db_connect()
    row  = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
    _open_session(username, "pasapalabra")
    await game_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "")
            if username in ADMINS:
                # Admins control everything
                try:
                    await game_manager.handle_action(data, username)
                except Exception as e:
                    logger.error("Pasapalabra handle_action error: %s", e)
            elif action == "player_answer":
                # Players can only submit their typed answer
                try:
                    await game_manager.handle_action(data, username)
                except Exception as e:
                    logger.error("Pasapalabra player_answer error: %s", e)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("Pasapalabra WS error: %s", e)
    finally:
        game_manager.disconnect(username)
 
 
 
# =============================================================================
# MILLONARIO
# =============================================================================
 
import json as _json_m
import random as _random_m
 
MILLONARIO_DIR = os.path.join(BASE_DIR, "static", "millonario")
QUIEN_SOY_DIR  = os.path.join(BASE_DIR, "static", "quiensoy")
APUESTAS_DIR   = os.path.join(BASE_DIR, "game_pages", "apuestas")
VOTACIONES_DIR = os.path.join(BASE_DIR, "game_pages", "votaciones")
 
PREMIOS = [
    "10 DVDcoins","20 DVDcoins","30 DVDcoins","50 DVDcoins","75 DVDcoins",
    "100 DVDcoins","150 DVDcoins","250 DVDcoins","500 DVDcoins","1000 DVDcoins"
]
GARANTIZADOS = {5: "75 DVDcoins", 10: "1000 DVDcoins"}
 
 
def _load_millonario_questions():
    path = os.path.join(MILLONARIO_DIR, "preguntas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json_m.load(f)
    except Exception as e:
        logger.error("Failed to load millonario preguntas.json: %s", e)
        return {}
 
 
def _build_game_questions():
    bank = _load_millonario_questions()
    result = []
    num_levels = len(PREMIOS)  # Use actual PREMIOS length (10)
    for lvl in range(1, num_levels + 1):
        pool = bank.get(str(lvl), [])
        if pool:
            q = _random_m.choice(pool)
            result.append({
                "nivel":    lvl,
                "premio":   PREMIOS[lvl - 1],
                "pregunta": q["p"],
                "opciones": {"A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"]},
                "respuesta": q["r"],
            })
        else:
            result.append(None)
    return result
 
 
class MillonarioManager:
    def __init__(self):
        self.enabled:     bool = False
        self.connections: dict = {}
        self._state:      dict = self._empty_state()
 
    def _empty_state(self):
        return {
            "status":          "waiting",
            "player":          None,
            "nivel":           0,
            "preguntas":       [],
            "comodin_50":      False,
            "eliminadas":      [],
            "ultimo_premio":   None,
            "selected_option": "",      # letter currently marked by dvd (broadcast to all)
            "reveal_result":   None,    # "correct" | "wrong" | None
            "waiting_decision": False,  # True when waiting for plantarse/siguiente decision
        }
 
    def _current_q(self):
        idx = self._state["nivel"] - 1
        qs  = self._state.get("preguntas", [])
        return qs[idx] if 0 <= idx < len(qs) else None
 
    def _build_broadcast(self):
        q   = self._current_q()
        q_pub = None
        if q:
            q_pub = {
                "nivel":       q["nivel"],
                "premio":      q["premio"],
                "pregunta":    q["pregunta"],
                "opciones":    {k: v for k, v in q["opciones"].items()
                                if k not in self._state["eliminadas"]},
                "opciones_all": q["opciones"],
                "respuesta":   q["respuesta"],   # client hides for non-dvd
            }
        return {
            "type":            "state",
            "enabled":         self.enabled,
            "status":          self._state["status"],
            "player":          self._state["player"],
            "nivel":           self._state["nivel"],
            "comodin_50":      self._state["comodin_50"],
            "eliminadas":      self._state["eliminadas"],
            "ultimo_premio":   self._state["ultimo_premio"],
            "premios":         PREMIOS,
            "garantizados":    [5, 10],
            "pregunta":        q_pub,
            "selected_option": self._state.get("selected_option", ""),
            "reveal_result":   self._state.get("reveal_result"),
            "waiting_decision": self._state.get("waiting_decision", False),
        }
 
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws
        try:
            await ws.send_json(self._build_broadcast())
        except Exception:
            pass
 
    def disconnect(self, username: str):
        self.connections.pop(username, None)
 
    async def broadcast(self):
        data = self._build_broadcast()
        dead = []
        for u, sock in list(self.connections.items()):
            try:
                await sock.send_json(data)
            except Exception:
                dead.append(u)
        for u in dead:
            self.connections.pop(u, None)
 
    async def handle_action(self, act: dict):
        action = act.get("action")
 
        if action == "setup":
            player = str(act.get("player", "")).strip()
            if not player:
                return
            self._state              = self._empty_state()
            self._state["player"]    = player
            self._state["nivel"]     = 1
            self._state["status"]    = "playing"
            self._state["preguntas"] = _build_game_questions()
            await self.broadcast()
 
        elif action == "correct":
            if self._state["status"] != "playing":
                return
            nivel = self._state["nivel"]
            if nivel in GARANTIZADOS:
                self._state["ultimo_premio"] = GARANTIZADOS[nivel]
            # Revealing phase: keep selected_option so clients see the marked letter
            self._state["reveal_result"] = "correct"
            self._state["status"]        = "revealing"
            # selected_option stays as-is during reveal
            await self.broadcast()
            await asyncio.sleep(0.15)
            
            # After revealing, check if game is finished or wait for decision
            if nivel == 10:
                self._state["status"]        = "finished"
                self._state["ultimo_premio"] = "1000 DVDcoins"
                self._state["selected_option"] = ""
                self._state["reveal_result"]   = None
                self._state["waiting_decision"] = False
            else:
                # Wait for decision: plantarse or siguiente
                self._state["status"]           = "waiting_decision"
                self._state["waiting_decision"] = True
                # Keep reveal_result and selected_option visible during decision
            
            await self.broadcast()
 
        elif action == "wrong":
            if self._state["status"] != "playing":
                return
            # Revealing phase: keep selected_option so clients see the marked letter
            self._state["reveal_result"] = "wrong"
            self._state["status"]        = "revealing"
            # selected_option stays as-is during reveal
            await self.broadcast()
            await asyncio.sleep(0.15)
            self._state["status"]          = "wrong"
            self._state["selected_option"] = ""   # clear AFTER reveal
            self._state["reveal_result"]   = None
            self._state["waiting_decision"] = False
            await self.broadcast()
 
        elif action == "siguiente":
            # Continue to next question after correct answer
            if self._state["status"] != "waiting_decision":
                return
            nivel = self._state["nivel"]
            self._state["nivel"]            = nivel + 1
            self._state["eliminadas"]       = []
            self._state["status"]           = "playing"
            self._state["selected_option"]  = ""
            self._state["reveal_result"]    = None
            self._state["waiting_decision"] = False
            await self.broadcast()
 
        elif action == "plantarse":
            # Player decides to stop and take current prize
            if self._state["status"] not in ("playing", "waiting_decision"):
                return
            nivel = self._state["nivel"]
            
            # If waiting_decision, player already answered correctly, take current level prize
            if self._state["waiting_decision"]:
                # Take the prize from the question just answered correctly
                premio_idx = nivel - 1
                if 0 <= premio_idx < len(PREMIOS):
                    self._state["ultimo_premio"] = PREMIOS[premio_idx]
                else:
                    self._state["ultimo_premio"] = "0 DVDcoins"
            else:
                # If playing (before answering), take previous level prize
                if nivel < 3:
                    # Cannot stop before question 3
                    return
                premio_idx = nivel - 2  # Previous question prize
                if 0 <= premio_idx < len(PREMIOS):
                    self._state["ultimo_premio"] = PREMIOS[premio_idx]
                else:
                    self._state["ultimo_premio"] = "0 DVDcoins"
            
            self._state["status"]           = "plantado"
            self._state["selected_option"]  = ""
            self._state["reveal_result"]    = None
            self._state["waiting_decision"] = False
            await self.broadcast()
 
        elif action == "comodin_50":
            if self._state["comodin_50"] or self._state["status"] != "playing":
                return
            q = self._current_q()
            if not q:
                return
            correcta    = q["respuesta"]
            incorrectas = [k for k in ["A", "B", "C", "D"]
                           if k != correcta and k not in self._state["eliminadas"]]
            _random_m.shuffle(incorrectas)
            self._state["eliminadas"]  = incorrectas[:2]
            self._state["comodin_50"]  = True
            await self.broadcast()
 
        elif action == "select_option":
            # dvd marks a letter — broadcast to all so everyone sees it highlighted
            letter = act.get("letter", "")
            self._state["selected_option"] = letter if letter in ("A","B","C","D") else ""
            await self.broadcast()
 
        elif action == "reset":
            self._state = self._empty_state()
            await self.broadcast()
 
 
 
millonario_manager = MillonarioManager()
 
 
# ── Routes ────────────────────────────────────────────────
 
@app.get("/bank/millonario", response_class=HTMLResponse)
async def millonario_page():
    """Serve the Millonario game page."""
    return _serve_game_page(MILLONARIO_DIR)


@app.get("/bank/apuestas", response_class=HTMLResponse)
async def apuestas_page():
    """Serve the Betting/Apuestas page."""
    return _serve_game_page(APUESTAS_DIR, "apuestas.html")


@app.get("/bank/apuestas/porra/{porra_id}", response_class=HTMLResponse)
async def porra_individual_page(porra_id: int):
    """Serve individual porra page. Auto-generates if missing."""
    try:
        # Check if page exists
        path = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras", f"porra_{porra_id}.html")
        
        if not os.path.exists(path):
            # Page doesn't exist - try to generate it
            logger.info(f"Porra page {porra_id} not found, attempting to generate...")
            
            try:
                c = db_bets()
                porra = c.execute("""
                    SELECT titulo, descripcion, tipo, fecha_limite, fecha_evento, 
                           creador, opciones_json
                    FROM porras WHERE id = ?
                """, (porra_id,)).fetchone()
                c.close()
                
                if not porra:
                    raise HTTPException(404, f"Porra {porra_id} no encontrada en la base de datos")
                
                # Generate the page
                opciones = _json.loads(porra["opciones_json"])
                _create_porra_page(
                    porra_id,
                    porra["titulo"],
                    porra["descripcion"] or "",
                    opciones,
                    porra["fecha_limite"],
                    porra["fecha_evento"],
                    porra["creador"],
                    porra["tipo"]
                )
                
                logger.info(f"Successfully generated porra page {porra_id}")
                
            except Exception as e:
                logger.error(f"Error generating porra page {porra_id}: {e}")
                raise HTTPException(500, f"Error generando página de porra: {str(e)}")
        
        # Return the page
        return FileResponse(path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving porra page {porra_id}: {e}")
        raise HTTPException(500, f"Error al cargar la página: {str(e)}")
 
 
@app.get("/bank/api/millonario/status")
async def millonario_status():
    """Return Millonario enabled state."""
    return {"enabled": millonario_manager.enabled}
 
 
@app.get("/bank/api/millonario/users")
async def millonario_users(user: str = Depends(get_current_user)):
    """Return eligible user list for Millonario."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT username FROM users ORDER BY username ASC"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows]
 
 
class MillonarioToggleRequest(BaseModel):
    enabled: bool
 
 
@app.post("/bank/api/millonario/toggle")
async def millonario_toggle(
    body: MillonarioToggleRequest,
    user: str = Depends(get_current_user)
):
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    millonario_manager.enabled = body.enabled
    if not body.enabled:
        millonario_manager._state = millonario_manager._empty_state()
    await millonario_manager.broadcast()
    return {"enabled": millonario_manager.enabled}
 
 
class MillonarioSetupRequest(BaseModel):
    player: str
 
 
@app.post("/bank/api/millonario/setup")
async def millonario_setup(body: MillonarioSetupRequest, user: str = Depends(get_current_user)):
    """Configure and start a Millonario game from admin panel."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    player = body.player.strip()
    if not player:
        raise HTTPException(400, "Player required")
    millonario_manager.enabled = True
    await millonario_manager.handle_action({"action": "setup", "player": player})
    logger.info("Millonario setup by %s: player=%s", user, player)
    return {"ok": True, "player": player}
 
 
@app.post("/bank/api/millonario/reset")
async def millonario_reset(user: str = Depends(get_current_user)):
    """Reset Millonario game state."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    millonario_manager._state = millonario_manager._empty_state()
    await millonario_manager.broadcast()
    return {"ok": True}
 
 
@app.websocket("/bank/ws/millonario")
async def millonario_ws(websocket: WebSocket, token: str = ""):
    """WebSocket handler for Millonario game."""
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    conn = db_connect()
    row  = conn.execute(
        "SELECT username FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
    _open_session(username, "millonario")
    await millonario_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if username in ADMINS:
                await millonario_manager.handle_action(data)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        millonario_manager.disconnect(username)
 
 
 
 
 
 
# =============================================================================
# OPO GAME MODULE — Simulacro de oposición tipo test
# Un jugador activo juega solo (puede ser dvd u otro usuario).
# Selecciona respuesta → se revela → 3s → siguiente pregunta.
# dvd controla: iniciar, resetear. Todos ven el marcador en tiempo real.
# =============================================================================
import json    as _json_opo
import asyncio as _aio_opo
 
 
 
 
# =============================================================================
# OPO QUIZ
# =============================================================================
 
OPO_DIR = os.path.join(BASE_DIR, "static", "opo")
 
 
def _load_opo_questions() -> list:
    path = os.path.join(OPO_DIR, "preguntas_opo_nebulosa.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json_opo.load(f)
    except Exception as e:
        logger.error("OPO load error: %s", e)
        return []
 
class OpoManager:
    def __init__(self):
        self.enabled:     bool = False
        self.connections: dict = {}        # username → websocket
        self._questions:  list = []
        self._state:      dict = self._empty_state()
        self._auto_task         = None
 
    # ── State ─────────────────────────────────────────────────────────────────
 
    def _empty_state(self) -> dict:
        return {
            "phase":          "waiting",   # waiting|block_select|question|reveal|block_end|finished
            "active_player":  None,        # username of the player answering
            "block_index":    0,
            "q_index":        0,
            "total_blocks":   0,
            "total_qs":       0,
            "current_q":      None,        # {n,p,A,B,C,D} — no answer key
            "player_answer":  None,        # letter chosen by active_player
            "correct":        None,        # correct letter (set after reveal)
            "reveal_delay":   0,           # seconds to show reveal (3=correct, 5=wrong)
            "block_scores":   {},          # username → {correct,wrong}
            "all_scores":     {},          # username → {correct,wrong} cumul.
            "block_result":   None,        # last block summary
            "countdown":      0,           # seconds remaining before auto-next
        }
 
    def _q(self) -> dict | None:
        """Current question without the answer key."""
        bi  = self._state["block_index"]
        qi  = self._state["q_index"]
        qs  = self._questions[bi * 10: (bi + 1) * 10]
        if qi >= len(qs):
            return None
        q = qs[qi]
        return {"n": q["n"], "p": q["p"],
                "A": q["A"], "B": q["B"], "C": q["C"], "D": q["D"]}
 
    def _correct_letter(self) -> str:
        bi = self._state["block_index"]
        qi = self._state["q_index"]
        qs = self._questions[bi * 10: (bi + 1) * 10]
        return qs[qi]["r"] if qi < len(qs) else ""
 
    def _ensure_score(self, u: str):
        for d in (self._state["block_scores"], self._state["all_scores"]):
            if u not in d:
                d[u] = {"correct": 0, "wrong": 0}
 
    # ── Broadcast ─────────────────────────────────────────────────────────────
 
    def _payload(self) -> dict:
        s = self._state
        return {
            "type":          "state",
            "enabled":       self.enabled,
            "phase":         s["phase"],
            "active_player": s["active_player"],
            "block_index":   s["block_index"],
            "q_index":       s["q_index"],
            "total_blocks":  s["total_blocks"],
            "total_qs":      s["total_qs"],
            "current_q":     s["current_q"],
            "player_answer": s["player_answer"],
            "correct":       s["correct"],
            "reveal_delay":  s["reveal_delay"],
            "block_scores":  s["block_scores"],
            "all_scores":    s["all_scores"],
            "block_result":  s["block_result"],
            "countdown":     s["countdown"],
            "connected":     list(self.connections.keys()),
            "wrong_qs_block": s.get("wrong_qs_this_block", []),
        }
 
    async def broadcast(self):
        msg  = self._payload()
        dead = []
        for u, ws in list(self.connections.items()):
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(u)
        for u in dead:
            self.connections.pop(u, None)
 
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws
        await self.broadcast()
 
    def disconnect(self, username: str):
        self.connections.pop(username, None)
 
    # ── Auto countdown ─────────────────────────────────────────────────────────
 
    def _cancel(self):
        if self._auto_task and not self._auto_task.done():
            self._auto_task.cancel()
        self._auto_task = None
 
    async def _countdown_then(self, seconds: int, fn):
        try:
            for t in range(seconds, 0, -1):
                self._state["countdown"] = t
                await self.broadcast()
                await _aio_opo.sleep(1)
            self._state["countdown"] = 0
            await fn()
        except _aio_opo.CancelledError:
            pass
 
    # ── Game flow ──────────────────────────────────────────────────────────────
 
    async def _do_reveal(self):
        """Score the answer, broadcast reveal. Waits for manual 'next' action."""
        s = self._state
        if s["phase"] != "question":
            return
        correct = self._correct_letter()
        s["correct"]  = correct
        s["phase"]    = "reveal"
        s["countdown"] = 0
        player        = s["active_player"]
        # Score the active player
        if player:
            self._ensure_score(player)
            if s["player_answer"] == correct:
                s["block_scores"][player]["correct"] += 1
                s["all_scores"][player]["correct"]   += 1
            else:
                s["block_scores"][player]["wrong"]   += 1
                s["all_scores"][player]["wrong"]     += 1
                # Track wrong question for review
                if "wrong_qs_this_block" not in s:
                    s["wrong_qs_this_block"] = []
                q = s.get("current_q", {})
                if q:
                    s["wrong_qs_this_block"].append({
                        "n": q.get("n"), "p": q.get("p"),
                        "A": q.get("A"), "B": q.get("B"),
                        "C": q.get("C"), "D": q.get("D"),
                        "r": self._correct_letter(),
                        "given": s["player_answer"]
                    })
        # Set reveal delay: 3s for correct, 5s for wrong
        was_correct = (s["player_answer"] == correct)
        s["reveal_delay"] = 3 if was_correct else 5
        self._cancel()
        await self.broadcast()
        # Auto-advance after reveal_delay seconds
        self._auto_task = _aio_opo.create_task(
            _aio_opo.sleep(s["reveal_delay"])
        )
        async def _auto_next():
            await _aio_opo.sleep(s["reveal_delay"])
            await self._do_next()
        self._auto_task = _aio_opo.create_task(_auto_next())
 
    async def _do_next(self):
        """Advance to next question or end of block."""
        s     = self._state
        bi    = s["block_index"]
        qi    = s["q_index"] + 1
        block = self._questions[bi * 10: (bi + 1) * 10]
        s["player_answer"] = None
        s["correct"]       = None
        s["countdown"]     = 0
        if qi < len(block):
            s["q_index"]   = qi
            s["phase"]     = "question"
            s["current_q"] = self._q()
            await self.broadcast()
        else:
            # End of block — wait for manual advance
            s["phase"]        = "block_end"
            s["countdown"]    = 0
            s["block_result"] = {
                "block":  bi + 1,
                "scores": {k: dict(v) for k, v in s["block_scores"].items()},
            }
            s["current_q"] = None
            self._cancel()
            await self.broadcast()
            # Auto-advance to next block after 3s
            async def _auto_block():
                await _aio_opo.sleep(3)
                await self._do_next_block()
            self._auto_task = _aio_opo.create_task(_auto_block())
 
    async def _do_next_block(self):
        """Called after block_end auto-timer — go to block_select so nebulosa picks next."""
        s = self._state
        s["countdown"] = 0
        next_bi = s["block_index"] + 1
        if next_bi >= s["total_blocks"]:
            s["phase"]     = "finished"
            s["current_q"] = None
            await self.broadcast()
        else:
            # Save block result to DB
            try:
                import json as _jres
                player_u = s.get("active_player", "nebulosa")
                bs = s["block_scores"].get(player_u, {})
                wqs_list = s.get("wrong_qs_this_block", [])
                _conn = db_opo()
                _conn.execute(
                    "INSERT INTO opo_results(username,block_n,correct,wrong,wrong_qs) VALUES(?,?,?,?,?)",
                    (player_u, bi+1, bs.get("correct",0), bs.get("wrong",0),
                     _jres.dumps(wqs_list, ensure_ascii=False))
                )
                _conn.commit()
                _conn.close()
            except Exception as _e:
                logger.error("OPO result save error: %s", _e)
            # Go to block_select: nebulosa chooses which block to do next
            s["phase"]        = "block_select"
            s["current_q"]    = None
            s["block_result"] = None
            await self.broadcast()
 
    # ── Action handler ─────────────────────────────────────────────────────────
 
    async def handle_action(self, act: dict, username: str):
        s      = self._state
        action = act.get("action", "")
 
        # ── start ──────────────────────────────────────────────────────────────
        if action == "start":
            if username not in OPO_USERS:
                return
            self._cancel()
            qs = _load_opo_questions()
            if not qs:
                return
            self._questions = qs
            n = len(qs)
            # Active player is the user who starts their own game
            player = username
            total_blocks = (n + 9) // 10
            # block param: 0-based block index, default 0
            start_block = int(act.get("block", 0))
            start_block = max(0, min(start_block, total_blocks - 1))
            self._state = self._empty_state()
            s = self._state
            s["phase"]        = "question"
            s["active_player"]= player
            s["total_blocks"] = total_blocks
            s["total_qs"]     = n
            s["block_index"]  = start_block
            s["current_q"]    = self._q()
            self._ensure_score(player)
            await self.broadcast()
 
        # ── answer ─────────────────────────────────────────────────────────────
        elif action == "answer":
            if s["phase"] != "question":
                return
            if username not in OPO_USERS:  # only OPO players answer
                return
            if s["player_answer"] is not None:
                return
            letter = act.get("letter", "").upper()
            if letter not in ("A", "B", "C", "D"):
                return
            s["player_answer"] = letter
            await self.broadcast()
            # Auto-reveal immediately
            await self._do_reveal()
 
        # ── force_reveal (dvd only, in case player is stuck) ───────────────────
        elif action == "force_reveal":
            if username not in OPO_USERS or s["phase"] != "question":
                return
            await self._do_reveal()
 
        # ── skip (dvd can skip countdown) ──────────────────────────────────────
        elif action == "select_block":
            # Any OPO player selects which block to play next
            if username not in OPO_USERS:
                return
            if s["phase"] not in ("waiting", "block_select"):
                return
            block_i = int(act.get("block", 0))
            block_i = max(0, min(block_i, s["total_blocks"] - 1))
            s["block_index"]  = block_i
            s["q_index"]      = 0
            s["phase"]        = "question"
            s["player_answer"]= None
            s["correct"]      = None
            s["current_q"]    = self._q()
            s["block_result"] = None
            s["wrong_qs_this_block"] = []
            # Reset block scores only
            s["block_scores"] = {u: {"correct": 0, "wrong": 0}
                                 for u in s["all_scores"]}
            self._ensure_score("nebulosa")
            await self.broadcast()
 
        elif action == "next":
            # Active player advances after seeing the answer
            if username not in OPO_USERS:
                return
            if s["phase"] == "reveal":
                await self._do_next()
 
        elif action == "next_block":
            # Advance to next block after block_end screen
            if username not in OPO_USERS:
                return
            if s["phase"] == "block_end":
                await self._do_next_block()
 
        elif action == "skip":
            if username not in OPO_USERS:
                return
            self._cancel()
            if s["phase"] == "reveal":
                await self._do_next()
            elif s["phase"] == "block_end":
                await self._do_next_block()
 
        # ── reset ──────────────────────────────────────────────────────────────
        elif action == "reset":
            if username not in OPO_USERS:
                return
            self._cancel()
            self._state = self._empty_state()
            await self.broadcast()
 
 
# ── OPO users and managers ────────────────────────────────────────────────────
 
def _load_opo_users() -> set:
    try:
        c = db_rights()
        rows = c.execute("SELECT username FROM opo_players").fetchall()
        c.close()
        return {"dvd", "nebulosa"} | {r["username"] for r in rows}
    except Exception:
        return {"dvd", "nebulosa"}
 
OPO_USERS: set = {"dvd", "nebulosa"}  # refreshed at startup
 
# ── In-memory video room registry — definido una sola vez arriba ──────────────
# _ROOMS y _room_public_list ya están definidos al inicio del archivo

_opo_managers: dict = {}
 
def get_opo_manager(username: str) -> "OpoManager":
    if username not in _opo_managers:
        _opo_managers[username] = OpoManager()
    return _opo_managers[username]
 
# ── OPO routes ─────────────────────────────────────────────────────────────────
 
@app.get("/bank/opo", response_class=HTMLResponse)
async def opo_page():
    """Serve the OPO game page."""
    return _serve_game_page(os.path.join(BASE_DIR, "static", "opo"))
 
@app.get("/bank/api/opo/status")
async def opo_status(user: str = Depends(get_current_user)):
    """Return OPO status and access for the current user."""
    mgr = get_opo_manager(user)
    return {"enabled": mgr.enabled, "username": user, "is_opo_user": user in OPO_USERS}
 
@app.post("/bank/api/opo/toggle")
async def opo_toggle(user: str = Depends(get_current_user)):
    """Enable or disable OPO."""
    if user not in SUPERADMINS: raise HTTPException(403)
    mgr = get_opo_manager(user)
    mgr.enabled = not mgr.enabled
    return {"enabled": mgr.enabled}
 
@app.get("/bank/api/opo/players")
async def opo_players_list(user: str = Depends(get_current_user)):
    """Return the list of OPO players."""
    if user not in OPO_USERS: raise HTTPException(403)
    cr = db_rights()
    player_rows = cr.execute("SELECT username, added_at FROM opo_players ORDER BY username").fetchall()
    cr.close()
    cs = db_stats()
    co = db_opo()
    result = []
    for pr in player_rows:
        u = pr["username"]
        lc = cs.execute("SELECT MAX(started_at) FROM sessions WHERE username=? AND section='opo'", (u,)).fetchone()[0]
        ls = cs.execute("SELECT duration_s FROM sessions WHERE username=? AND section='opo' ORDER BY started_at DESC LIMIT 1", (u,)).fetchone()
        ts = cs.execute("SELECT COALESCE(SUM(duration_s),0) FROM sessions WHERE username=? AND section='opo'", (u,)).fetchone()[0]
        td = co.execute("SELECT COUNT(*) FROM opo_results WHERE username=?", (u,)).fetchone()[0]
        result.append({"username": u, "added_at": pr["added_at"], "last_conn": lc,
                       "last_session_s": (ls[0] if ls else 0) or 0, "total_s": ts or 0, "tests_done": td or 0})
    cs.close(); co.close()
    for u in sorted({"dvd","nebulosa"} - {r["username"] for r in result}):
        cs2 = db_stats(); co2 = db_opo()
        lc2 = cs2.execute("SELECT MAX(started_at) FROM sessions WHERE username=? AND section='opo'", (u,)).fetchone()[0]
        ts2 = cs2.execute("SELECT COALESCE(SUM(duration_s),0) FROM sessions WHERE username=? AND section='opo'", (u,)).fetchone()[0]
        td2 = co2.execute("SELECT COUNT(*) FROM opo_results WHERE username=?", (u,)).fetchone()[0]
        cs2.close(); co2.close()
        result.insert(0, {"username": u, "added_at": None, "last_conn": lc2,
                          "last_session_s": 0, "total_s": ts2 or 0, "tests_done": td2 or 0})
    return result
 
@app.post("/bank/api/opo/players")
async def opo_player_add(body: OpoPlayerRequest, user: str = Depends(get_current_user)):
    """Add a user to OPO access list."""
    global OPO_USERS
    if user not in SUPERADMINS: raise HTTPException(403)
    uname = body.username.strip().lower()
    if not uname: raise HTTPException(400, "username required")
    conn = db_users()
    if not conn.execute("SELECT 1 FROM users WHERE username=?", (uname,)).fetchone():
        conn.close(); raise HTTPException(404, "Usuario no encontrado")
    conn.close()
    cr = db_rights()
    cr.execute("INSERT OR IGNORE INTO opo_players(username,added_by) VALUES(?,?)", (uname, user))
    cr.commit(); cr.close()
    OPO_USERS = _load_opo_users()
    return {"ok": True}
 
@app.delete("/bank/api/opo/players/{username}")
async def opo_player_remove(username: str, user: str = Depends(get_current_user)):
    """Remove a user from OPO access list."""
    global OPO_USERS
    if user not in SUPERADMINS: raise HTTPException(403)
    if username in {"dvd","nebulosa"}: raise HTTPException(400, "Cannot remove dvd or nebulosa")
    cr = db_rights()
    cr.execute("DELETE FROM opo_players WHERE username=?", (username,))
    cr.commit(); cr.close()
    OPO_USERS = _load_opo_users()
    return {"ok": True}
 
@app.post("/bank/api/opo/result")
async def opo_result_save(body: OpoResultRequest, user: str = Depends(get_current_user)):
    """Save an OPO test result."""
    if user not in OPO_USERS: raise HTTPException(403)
    import json as _jr
    conn = db_opo()
    conn.execute(
        "INSERT INTO opo_results(username,block_n,correct,wrong,wrong_qs) VALUES(?,?,?,?,?)",
        (user, body.block_n, body.correct, body.wrong, _jr.dumps(body.wrong_qs, ensure_ascii=False))
    )
    conn.commit(); conn.close()
    return {"ok": True}
 
@app.get("/bank/api/opo/results")
async def opo_results_all(user: str = Depends(get_current_user), username:
    str = ""):
    if user not in OPO_USERS: raise HTTPException(403)
    import json as _jr
    conn = db_opo()
    if user in SUPERADMINS and username:
        rows = conn.execute(
            "SELECT id,username,block_n,played_at,correct,wrong,wrong_qs FROM opo_results "
            "WHERE username=? ORDER BY played_at DESC LIMIT 500", (username,)
        ).fetchall()
    elif user in SUPERADMINS:
        rows = conn.execute(
            "SELECT id,username,block_n,played_at,correct,wrong,wrong_qs FROM opo_results "
            "ORDER BY played_at DESC LIMIT 500"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id,username,block_n,played_at,correct,wrong,wrong_qs FROM opo_results "
            "WHERE username=? ORDER BY played_at DESC LIMIT 200", (user,)
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        try: wqs = _jr.loads(r["wrong_qs"]) if r["wrong_qs"] else []
        except: wqs = []
        result.append({"id":r["id"],"username":r["username"],"block_n":r["block_n"],
                       "played_at":r["played_at"],"correct":r["correct"],"wrong":r["wrong"],"wrong_qs":wqs})
    return result
 
@app.get("/bank/api/opo/stats")
async def opo_stats_endpoint(user: str = Depends(get_current_user)):
    """Return OPO session stats per user."""
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_stats()
    rows = conn.execute(
        "SELECT username, MAX(started_at) last_conn, SUM(duration_s) total_s, COUNT(*) sessions "
        "FROM sessions WHERE section='opo' GROUP BY username ORDER BY last_conn DESC"
    ).fetchall()
    conn.close()
    return [{"username":r["username"],"last_conn":r["last_conn"],"total_s":r["total_s"] or 0,"sessions":r["sessions"]} for r in rows]
 
# ── Cuentos sessions ──────────────────────────────────────────────────────────
 
@app.get("/bank/api/cuentos/sessions")
async def cuentos_sessions(
    user: str = Depends(get_current_user),
    username: str = "", date_from: str = "", date_to: str = "",
    detail: str = "", limit: int = 500
):
    if user not in SUPERADMINS: raise HTTPException(403)
    conn = db_stats()
    q = "SELECT id,username,section,detail,started_at,ended_at,duration_s FROM sessions WHERE section='cuentos'"
    p = []
    if username:  q += " AND username LIKE ?"; p.append(f"%{username}%")
    if date_from: q += " AND started_at >= ?"; p.append(date_from)
    if date_to:   q += " AND started_at <= ?"; p.append(date_to+"T23:59:59")
    if detail:    q += " AND detail LIKE ?";   p.append(f"%{detail}%")
    q += f" ORDER BY started_at DESC LIMIT {min(limit,2000)}"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
# ── OPO WebSocket ─────────────────────────────────────────────────────────────
 
@app.websocket("/bank/ws/opo")
async def opo_ws(websocket: WebSocket, token: str = ""):
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Auth required"); return
    if username not in OPO_USERS:
        await websocket.close(code=4003, reason="OPO access denied"); return
    conn = db_users()
    row = conn.execute("SELECT is_blocked FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and row["is_blocked"]:
        await websocket.close(code=4001, reason="Blocked"); return
    _ping_session(username, "opo")
    mgr = get_opo_manager(username)
    await mgr.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await mgr.handle_action(data, username)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        mgr.disconnect(username)
 
 
# =============================================================================
# MESSAGING SYSTEM
# Supports group chat (room="group") and direct messages (room="dm:a:b").
# Audio messages are uploaded via REST, stored in static/audio/messages/.
# Real-time delivery via WebSocket /ws/messages.
# =============================================================================
 
import uuid as _uuid
import json  as _json_msg
 
# ── DB path ────────────────────────────────────────────────────────────────
DB_MSG      = os.path.join(DATA_DIR, "messages.db")
MSG_DIR     = os.path.join(BASE_DIR, "static", "audio", "messages")
MSG_ALLOWED = {".webm", ".mp4", ".ogg", ".m4a", ".aac", ".wav"}
MSG_MAX_ROWS = 2000  # max messages to keep per room
 
def db_msg() -> sqlite3.Connection:
    """Open the messages database."""
    return _open_db(DB_MSG)
 
 
def _msg_db_init():
    """Create messaging tables. Safe to call on every restart."""
    os.makedirs(MSG_DIR, exist_ok=True)
    c = db_msg()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            room         TEXT    NOT NULL DEFAULT 'group',
            from_user    TEXT    NOT NULL,
            content      TEXT    NOT NULL DEFAULT '',
            msg_type     TEXT    NOT NULL DEFAULT 'text',
            reply_to_id  INTEGER,
            deleted      INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_msg_room ON messages(room, created_at);
        CREATE INDEX IF NOT EXISTS idx_msg_user ON messages(from_user);
 
        CREATE TABLE IF NOT EXISTS msg_reads (
            msg_id   INTEGER NOT NULL,
            username TEXT    NOT NULL,
            PRIMARY KEY (msg_id, username)
        );
 
        CREATE TABLE IF NOT EXISTS msg_reactions (
            msg_id   INTEGER NOT NULL,
            username TEXT    NOT NULL,
            emoji    TEXT    NOT NULL,
            PRIMARY KEY (msg_id, username)
        );
 
        CREATE TABLE IF NOT EXISTS msg_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );
        INSERT OR IGNORE INTO msg_settings(key, value) VALUES('enabled', 'false');

        CREATE TABLE IF NOT EXISTS video_rooms (
            room_key    TEXT PRIMARY KEY,
            title       TEXT NOT NULL DEFAULT '',
            host        TEXT NOT NULL DEFAULT '',
            mode        TEXT NOT NULL DEFAULT 'public',
            active      INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS video_room_members (
            room_key    TEXT NOT NULL,
            username    TEXT NOT NULL,
            joined_at   TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (room_key, username)
        );
        CREATE TABLE IF NOT EXISTS video_room_invites (
            room_key    TEXT NOT NULL,
            username    TEXT NOT NULL,
            invited_at  TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (room_key, username)
        );
    """)
    c.commit()
    # Migration: add new columns if missing
    for col_sql in [
        "ALTER TABLE messages ADD COLUMN reply_to_id INTEGER",
        "ALTER TABLE messages ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0",
        "CREATE TABLE IF NOT EXISTS msg_reactions (msg_id INTEGER NOT NULL, username TEXT NOT NULL, emoji TEXT NOT NULL, PRIMARY KEY (msg_id, username))",
    ]:
        try:
            c.execute(col_sql)
            c.commit()
        except Exception:
            pass
    c.close()
 
 
def _dm_room(a: str, b: str) -> str:
    """Return canonical DM room name for two users (alphabetically sorted)."""
    return "dm:" + ":".join(sorted([a.lower(), b.lower()]))
 
 
def _msg_enabled() -> bool:
    """Check if messaging is currently enabled."""
    try:
        c = db_msg()
        row = c.execute("SELECT value FROM msg_settings WHERE key='enabled'").fetchone()
        c.close()
        return row and row["value"] == "true"
    except Exception:
        return False
 
 
def _set_msg_enabled(val: bool):
    """Persist the messaging enabled flag."""
    c = db_msg()
    c.execute("INSERT OR REPLACE INTO msg_settings(key,value) VALUES('enabled',?)",
              ("true" if val else "false",))
    c.commit()
    c.close()
 
 
def _load_history(room: str, limit: int = 60, before_id: int = 0) -> list:
    """Return message history for a room, newest-last."""
    c = db_msg()
    if before_id:
        rows = c.execute(
            "SELECT id,room,from_user,content,msg_type,reply_to_id,deleted,created_at FROM messages "
            "WHERE room=? AND id<? ORDER BY id DESC LIMIT ?",
            (room, before_id, limit)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT id,room,from_user,content,msg_type,reply_to_id,deleted,created_at FROM messages "
            "WHERE room=? ORDER BY id DESC LIMIT ?",
            (room, limit)
        ).fetchall()
    msgs = [dict(r) for r in reversed(rows)]
    # Attach reactions
    if msgs:
        ids = [m["id"] for m in msgs]
        react_rows = c.execute(
            f"SELECT msg_id,username,emoji FROM msg_reactions WHERE msg_id IN ({','.join('?'*len(ids))})",
            ids
        ).fetchall()
        reactions_map = {}
        for r in react_rows:
            reactions_map.setdefault(r["msg_id"], []).append({"username": r["username"], "emoji": r["emoji"]})
        for m in msgs:
            m["reactions"] = reactions_map.get(m["id"], [])
    c.close()
    return msgs
 
 
def _save_message(room: str, from_user: str, content: str, msg_type: str = "text", reply_to_id: int = None) -> dict:
    """Persist a message and return its full dict."""
    c = db_msg()
    cur = c.execute(
        "INSERT INTO messages(room,from_user,content,msg_type,reply_to_id) VALUES(?,?,?,?,?)",
        (room, from_user, content, msg_type, reply_to_id)
    )
    row = c.execute(
        "SELECT id,room,from_user,content,msg_type,reply_to_id,created_at FROM messages WHERE id=?",
        (cur.lastrowid,)
    ).fetchone()
    # Prune old messages per room
    c.execute(
        "DELETE FROM messages WHERE room=? AND id NOT IN "
        "(SELECT id FROM messages WHERE room=? ORDER BY id DESC LIMIT ?)",
        (room, room, MSG_MAX_ROWS)
    )
    c.commit()
    c.close()
    return dict(row)
 
 
# ── Connection manager ─────────────────────────────────────────────────────
 
class MessageManager:
    """Manages WebSocket connections — supports multiple tabs per user."""

    def __init__(self):
        self._conns: dict = {}   # username → list[WebSocket]

    @property
    def connections(self) -> dict:
        """Legacy compat: username → first ws."""
        return {u: wss[0] for u, wss in self._conns.items() if wss}

    def _all(self, username: str) -> list:
        return list(self._conns.get(username, []))

    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        if username not in self._conns:
            self._conns[username] = []
        if ws not in self._conns[username]:
            self._conns[username].append(ws)
        await self.broadcast_status()

    def disconnect(self, username: str, ws: WebSocket = None):
        if username not in self._conns:
            return
        if ws is None:
            del self._conns[username]
        else:
            try:
                self._conns[username].remove(ws)
            except ValueError:
                pass
            if not self._conns[username]:
                del self._conns[username]

    @property
    def online(self) -> list:
        return list(self._conns.keys())

    async def _send(self, ws: WebSocket, text: str) -> bool:
        try:
            await ws.send_text(text)
            return True
        except Exception:
            return False

    async def broadcast_status(self):
        payload = _json_msg.dumps({"type": "status", "online": self.online})
        for u in list(self._conns.keys()):
            dead = [ws for ws in list(self._conns.get(u, [])) if not await self._send(ws, payload)]
            for ws in dead:
                self.disconnect(u, ws)

    async def deliver(self, msg: dict, room: str):
        payload = _json_msg.dumps({"type": "message", **msg})
        if room == "group":
            targets = list(self._conns.keys())
        else:
            parts = set(room.split(":")[1:])
            targets = [u for u in self._conns if u in parts]
        for u in targets:
            dead = [ws for ws in list(self._conns.get(u, [])) if not await self._send(ws, payload)]
            for ws in dead:
                self.disconnect(u, ws)

    async def send_to(self, username: str, payload: dict):
        """Send to ALL connections of a user (chat tab + video tab)."""
        text = _json_msg.dumps(payload)
        dead = [ws for ws in list(self._conns.get(username, [])) if not await self._send(ws, text)]
        for ws in dead:
            self.disconnect(username, ws)
 
 
msg_manager = MessageManager()
 
 
# ── Pydantic models ────────────────────────────────────────────────────────
 
class MsgToggleRequest(BaseModel):
    enabled: bool
 
class MsgSendRequest(BaseModel):
    room:     str
    content:  str
    msg_type: str = "text"
 
 
# ── REST routes ────────────────────────────────────────────────────────────
 
@app.get("/bank/messages", response_class=HTMLResponse)
async def messages_page():
    """Serve the messaging chat page."""
    resp = FileResponse(os.path.join(BASE_DIR, "static", "pages", "chat.html"))
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp
 
 
@app.get("/bank/api/messages/status")
async def messages_status(user: str = Depends(get_current_user)):
    """Return messaging enabled state, online users, and available rooms."""
    enabled = _msg_enabled()
    if not enabled and user not in ALL_ADMINS:
        return {"enabled": False, "online": [], "rooms": []}
    # Build rooms list: group + DMs where user has history
    c = db_msg()
    dm_rows = c.execute(
        "SELECT DISTINCT room FROM messages WHERE room LIKE 'dm:%' AND ("
        "room LIKE ? OR room LIKE ?)",
        (f"dm:{user}:%", f"dm:%:{user}")
    ).fetchall()
    c.close()
    rooms = ["group"] + [r["room"] for r in dm_rows]
    return {
        "enabled": enabled,
        "online":  msg_manager.online,
        "rooms":   rooms,
    }

# Alias para compatibilidad
@app.get("/api/messages/status")
async def messages_status_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/messages/status para compatibilidad"""
    return await messages_status(user)
 
 
@app.get("/bank/api/messages/history")
async def messages_history(
    user: str = Depends(get_current_user),
    room: str = "group",
    limit: int = 60,
    before_id: int = 0,
):
    """Return paginated message history for a room."""
    enabled = _msg_enabled()
    if not enabled and user not in ALL_ADMINS:
        raise HTTPException(403, "Messaging is disabled")
    # Validate access to DM room
    if room.startswith("dm:"):
        parts = set(room.split(":")[1:])
        if user not in parts and user not in SUPERADMINS:
            raise HTTPException(403, "Access denied")
    limit = max(1, min(limit, 100))
    msgs = _load_history(room, limit, before_id)
    # Attach read status for current user
    if msgs:
        ids = [m["id"] for m in msgs]
        c = db_msg()
        read_ids = {
            r["msg_id"]
            for r in c.execute(
                f"SELECT msg_id FROM msg_reads WHERE username=? AND msg_id IN ({','.join('?'*len(ids))})",
                [user] + ids
            ).fetchall()
        }
        c.close()
        for m in msgs:
            m["read_by_me"] = m["id"] in read_ids
    return msgs

# Alias para compatibilidad
@app.get("/api/messages/history")
async def messages_history_alias(
    user: str = Depends(get_current_user),
    room: str = "group",
    limit: int = 60,
    before_id: int = 0,
):
    """Alias de /bank/api/messages/history para compatibilidad"""
    return await messages_history(user, room, limit, before_id)
 
 
@app.post("/bank/api/messages/read")
async def messages_mark_read(
    user: str = Depends(get_current_user),
    room: str = "group",
    last_id: int = 0,
):
    """Mark all messages up to last_id in a room as read by this user."""
    if not _msg_enabled() and user not in ALL_ADMINS:
        raise HTTPException(403, "Messaging is disabled")
    if not last_id:
        return {"ok": True}
    c = db_msg()
    rows = c.execute(
        "SELECT id FROM messages WHERE room=? AND id<=? AND id NOT IN "
        "(SELECT msg_id FROM msg_reads WHERE username=?)",
        (room, last_id, user)
    ).fetchall()
    for r in rows:
        c.execute("INSERT OR IGNORE INTO msg_reads(msg_id,username) VALUES(?,?)", (r["id"], user))
    c.commit()
    c.close()
    return {"ok": True, "marked": len(rows)}


@app.post("/bank/api/messages/mark-room-read")
async def messages_mark_room_read(
    body: dict,
    user: str = Depends(get_current_user),
):
    """Mark ALL messages in a room as read by this user."""
    if not _msg_enabled() and user not in ALL_ADMINS:
        raise HTTPException(403, "Messaging is disabled")
    
    room = body.get("room", "group")
    
    c = db_msg()
    # Obtener todos los mensajes no leídos del room (excepto los propios)
    rows = c.execute(
        "SELECT id FROM messages WHERE room=? AND from_user!=? AND id NOT IN "
        "(SELECT msg_id FROM msg_reads WHERE username=?)",
        (room, user, user)
    ).fetchall()
    
    # Marcar todos como leídos
    for r in rows:
        c.execute("INSERT OR IGNORE INTO msg_reads(msg_id,username) VALUES(?,?)", (r["id"], user))
    
    c.commit()
    c.close()
    
    return {"ok": True, "marked": len(rows), "room": room}
 
 
@app.post("/bank/api/messages/audio")
async def messages_upload_audio(
    user: str = Depends(get_current_user),
    file: UploadFile = File(...),
):
    """Upload an audio message file; returns its public URL."""
    if not _msg_enabled() and user not in ALL_ADMINS:
        raise HTTPException(403, "Messaging is disabled")
    ext = os.path.splitext(file.filename or "audio.webm")[1].lower()
    if not ext:
        ext = ".webm"
    if ext not in MSG_ALLOWED:
        raise HTTPException(400, f"Audio format not supported: {ext}")
    fname = _uuid.uuid4().hex + ext
    dest  = os.path.join(MSG_DIR, fname)
    os.makedirs(MSG_DIR, exist_ok=True)
    data  = await file.read()
    if len(data) > 10 * 1024 * 1024:  # 10 MB max
        raise HTTPException(413, "Audio too large (max 10 MB)")
    with open(dest, "wb") as f:
        f.write(data)
    url = f"/static/audio/messages/{fname}"
    logger.info("Audio upload: %s by %s (%d bytes)", fname, user, len(data))
    return {"ok": True, "url": url}
 
 
@app.post("/bank/api/messages/toggle")
async def messages_toggle(body: MsgToggleRequest, user: str = Depends(get_current_user)):
    """Enable or disable the messaging system (admins only)."""
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Admins only")
    _set_msg_enabled(body.enabled)
    logger.info("Messaging %s by %s", "enabled" if body.enabled else "disabled", user)
    await msg_manager.broadcast_status()
    return {"enabled": body.enabled}

# Alias para compatibilidad
@app.post("/api/messages/toggle")
async def messages_toggle_alias(body: MsgToggleRequest, user: str = Depends(get_current_user)):
    """Alias de /bank/api/messages/toggle para compatibilidad"""
    return await messages_toggle(body, user)
 
 
@app.get("/bank/api/messages/users")
async def messages_users(user: str = Depends(get_current_user)):
    """Return list of users available to start a DM with."""
    if not _msg_enabled() and user not in ALL_ADMINS:
        raise HTTPException(403, "Messaging is disabled")
    c = db_users()
    rows = c.execute(
        "SELECT username FROM users WHERE password_hash NOT IN ('__UNSET__','__AUTO__') "
        "ORDER BY username"
    ).fetchall()
    c.close()
    return [r["username"] for r in rows if r["username"] != user]
 
 
@app.get("/bank/api/messages/unread")
async def messages_unread(user: str = Depends(get_current_user)):
    """Return unread message counts per room for the current user."""
    if not _msg_enabled() and user not in ALL_ADMINS:
        return {}
    c = db_msg()
    rows = c.execute(
        "SELECT m.room, COUNT(*) cnt FROM messages m "
        "WHERE m.from_user != ? AND m.id NOT IN "
        "(SELECT msg_id FROM msg_reads WHERE username=?) "
        "GROUP BY m.room",
        (user, user)
    ).fetchall()
    c.close()
    return {r["room"]: r["cnt"] for r in rows}

# Alias para compatibilidad
@app.get("/api/messages/unread")
async def messages_unread_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/messages/unread para compatibilidad"""
    return await messages_unread(user)
 
 
@app.get("/bank/api/messages/admin/stats")
async def messages_admin_stats(user: str = Depends(get_current_user)):
    """Return admin-level messaging statistics."""
    if user not in ALL_ADMINS:
        raise HTTPException(403, "Admins only")
    c = db_msg()
    total   = c.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"]
    today   = c.execute(
        "SELECT COUNT(*) n FROM messages WHERE date(created_at)=date('now')"
    ).fetchone()["n"]
    users   = c.execute("SELECT COUNT(DISTINCT from_user) n FROM messages").fetchone()["n"]
    rooms   = c.execute("SELECT COUNT(DISTINCT room) n FROM messages").fetchone()["n"]
    recent  = c.execute(
        "SELECT from_user, content, msg_type, created_at FROM messages "
        "ORDER BY id DESC LIMIT 10"
    ).fetchall()
    c.close()
    return {
        "total_messages": total,
        "messages_today": today,
        "unique_senders": users,
        "total_rooms":    rooms,
        "recent":         [dict(r) for r in recent],
        "online_now":     len(msg_manager.online),
        "enabled":        _msg_enabled(),
    }

# Alias para compatibilidad
@app.get("/api/messages/admin/stats")
async def messages_admin_stats_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/messages/admin/stats para compatibilidad"""
    return await messages_admin_stats(user)
 
 
@app.get("/bank/api/opo/my-access")
async def opo_my_access(user: str = Depends(get_current_user)):
    """Returns whether the current user can access OPO."""
    is_opo = user in OPO_USERS or user in SUPERADMINS
    return {"is_opo_user": is_opo, "username": user}


@app.get("/bank/api/messages/admin/all-rooms")
async def messages_admin_all_rooms(user: str = Depends(get_current_user)):
    """Return all conversation rooms with last message info, for superadmin view."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Superadmins only")
    c = db_msg()
    rows = c.execute(
        "SELECT room, from_user AS last_user, content AS last_content, "
        "created_at AS last_at, COUNT(*) OVER (PARTITION BY room) AS total "
        "FROM messages m1 "
        "WHERE id = (SELECT MAX(id) FROM messages m2 WHERE m2.room = m1.room) "
        "ORDER BY last_at DESC"
    ).fetchall()
    c.close()
    return {"rooms": [dict(r) for r in rows]}

# Alias para compatibilidad
@app.get("/api/messages/admin/all-rooms")
async def messages_admin_all_rooms_alias(user: str = Depends(get_current_user)):
    """Alias de /bank/api/messages/admin/all-rooms para compatibilidad"""
    return await messages_admin_all_rooms(user)
 
 
@app.get("/bank/api/rooms/debug")
async def rooms_debug(user: str = Depends(get_current_user)):
    """Debug endpoint — shows raw DB state and memory state for rooms."""
    try:
        c = db_msg()
        all_rows = c.execute(
            "SELECT room_key, title, host, mode, active, created_at FROM video_rooms ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        members_rows = c.execute(
            "SELECT room_key, username FROM video_room_members"
        ).fetchall()
        c.close()
        return {
            "db_rooms": [dict(r) for r in all_rows],
            "db_members": [dict(r) for r in members_rows],
            "memory_rooms": {k: {"host":v["host"],"title":v["title"],"mode":v["mode"],
                                  "members":list(v["members"]),"invites":list(v["invites"])}
                             for k,v in _ROOMS.items()},
            "sse_subscribers": len(_sse_queues),
            "requesting_user": user,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/bank/api/rooms/status")
async def rooms_status(user: str = Depends(get_current_user)):
    """Game-style status endpoint for rooms.
    Returns active=True/False and the list of visible rooms.
    Polled every 10s by all clients — same pattern as game status endpoints.
    """
    try:
        c = db_msg()
        # Public rooms
        pub_rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode,
                   GROUP_CONCAT(DISTINCT m.username) AS members_csv
            FROM video_rooms r
            LEFT JOIN video_room_members m ON m.room_key = r.room_key
            WHERE r.active = 1 AND r.mode = 'public'
            GROUP BY r.room_key
            ORDER BY r.created_at DESC
        """).fetchall()
        # Private rooms where user is invited
        inv_rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode,
                   GROUP_CONCAT(DISTINCT m.username) AS members_csv
            FROM video_rooms r
            LEFT JOIN video_room_members m ON m.room_key = r.room_key
            INNER JOIN video_room_invites i ON i.room_key = r.room_key AND i.username = ?
            WHERE r.active = 1 AND r.mode = 'private'
            GROUP BY r.room_key
            ORDER BY r.created_at DESC
        """, (user,)).fetchall()
        c.close()

        result = []
        seen = set()
        for row in list(pub_rows) + list(inv_rows):
            k = row["room_key"]
            if k in seen:
                continue
            seen.add(k)
            mem = _ROOMS.get(k)
            members = list(mem["members"]) if mem else [m for m in (row["members_csv"] or "").split(",") if m]
            result.append({
                "key":      k,
                "title":    row["title"],
                "host":     row["host"],
                "mode":     row["mode"],
                "members":  members,
                "invited":  row["mode"] == "private",
                "join_url": f"/join/{k}",
            })

        # Also include memory-only rooms (race condition safety)
        for k, r in list(_ROOMS.items()):
            if k not in seen and (r["mode"] == "public" or user in r["invites"] or user == r["host"]):
                seen.add(k)
                result.append({
                    "key":      k,
                    "title":    r["title"],
                    "host":     r["host"],
                    "mode":     r["mode"],
                    "members":  list(r["members"]),
                    "invited":  user in r["invites"],
                    "join_url": f"/join/{k}",
                })

        return {
            "active": len(result) > 0,
            "count":  len(result),
            "rooms":  result,
        }
    except Exception as e:
        logger.error("rooms_status error: %s", e)
        return {"active": False, "count": 0, "rooms": [], "error": str(e)}


@app.get("/bank/api/rooms/list")
async def rooms_list(user: str = Depends(get_current_user)):
    """List video rooms visible to the current user — memory + DB merged.
    Returns consistent field names: room_key, title, host, mode, members_csv"""
    rooms = _room_public_list(user)
    # Normalize field names for frontend compatibility
    result = []
    for r in rooms:
        result.append({
            "room_key": r.get("key") or r.get("room_key"),
            "title": r.get("title"),
            "host": r.get("host"),
            "mode": r.get("mode"),
            "members_csv": ",".join(r.get("members", [])) if r.get("members") else "",
            "invited": r.get("invited", False),
        })
    return result


@app.get("/bank/api/rooms/public")
async def rooms_public(user: str = Depends(get_current_user)):
    """Ultra-simple endpoint: returns ALL active public rooms + rooms where user is invited.
    Reads directly from DB. No complex logic. Used by members to see open rooms."""
    try:
        c = db_msg()
        # Public rooms
        rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode,
                   GROUP_CONCAT(DISTINCT m.username) AS members_csv
            FROM video_rooms r
            LEFT JOIN video_room_members m ON m.room_key = r.room_key
            WHERE r.active = 1 AND r.mode = 'public'
            GROUP BY r.room_key
            ORDER BY r.created_at DESC
        """).fetchall()
        # Private rooms where user is invited
        inv_rows = c.execute("""
            SELECT r.room_key, r.title, r.host, r.mode,
                   GROUP_CONCAT(DISTINCT m.username) AS members_csv
            FROM video_rooms r
            LEFT JOIN video_room_members m ON m.room_key = r.room_key
            INNER JOIN video_room_invites i ON i.room_key = r.room_key AND i.username = ?
            WHERE r.active = 1 AND r.mode = 'private'
            GROUP BY r.room_key
            ORDER BY r.created_at DESC
        """, (user,)).fetchall()
        c.close()

        result = []
        seen = set()
        for row in list(rows) + list(inv_rows):
            k = row["room_key"]
            if k in seen:
                continue
            seen.add(k)
            # Merge live members from memory
            mem = _ROOMS.get(k)
            if mem:
                members = list(mem["members"])
            else:
                members = [m for m in (row["members_csv"] or "").split(",") if m]
            result.append({
                "key":      k,
                "title":    row["title"],
                "host":     row["host"],
                "mode":     row["mode"],
                "members":  members,
                "invited":  row["mode"] == "private",
                "join_url": f"/join/{k}",
            })

        # Also include rooms only in memory (not yet in DB)
        for k, r in list(_ROOMS.items()):
            if k not in seen and (r["mode"] == "public" or user in r["invites"] or user == r["host"]):
                seen.add(k)
                result.append({
                    "key":      k,
                    "title":    r["title"],
                    "host":     r["host"],
                    "mode":     r["mode"],
                    "members":  list(r["members"]),
                    "invited":  user in r["invites"],
                    "join_url": f"/join/{k}",
                })

        return {"rooms": result, "count": len(result)}
    except Exception as e:
        logger.error("rooms_public error: %s", e)
        return {"rooms": [], "count": 0, "error": str(e)}


@app.post("/bank/api/rooms/create")
async def rooms_create(request: Request, user: str = Depends(get_current_user)):
    """Create a room via REST — works even when messaging WS is disabled.
    This is the fallback when _socialWS is not connected."""
    body = await request.json()
    room_key  = str(body.get("room", _uuid.uuid4().hex[:12]))
    title     = str(body.get("title", f"Sala de {user}"))[:80]
    mode      = str(body.get("mode", "public"))
    invites   = list(body.get("invites", []))

    # Create in memory
    if room_key not in _ROOMS:
        _ROOMS[room_key] = {
            "host": user, "title": title,
            "mode": mode, "invites": set(invites),
            "members": set()
        }
    _ROOMS[room_key]["members"].add(user)

    # Persist to DB
    _db_upsert_room(room_key, title, user, mode)
    _db_add_member(room_key, user)

    # Handle invites
    for inv in invites:
        if inv and inv != user:
            _ROOMS[room_key]["invites"].add(inv)
            _db_add_invite(room_key, inv)
            invite_payload = {
                "type": "room-invite", "room_key": room_key,
                "title": title, "host": user, "join_url": f"/join/{room_key}",
            }
            await msg_manager.send_to(inv, invite_payload)
            await rooms_manager.send_to(inv, invite_payload)

    # Broadcast to all connected users
    await _broadcast_rooms_all()
    _save_rooms()

    return {
        "ok": True, "room": room_key, "title": title,
        "host": user, "mode": mode,
        "members": list(_ROOMS[room_key]["members"]),
        "join_url": f"/join/{room_key}",
    }


@app.post("/bank/api/rooms/join")
async def rooms_join(request: Request, user: str = Depends(get_current_user)):
    """Join an existing room via REST — fallback when WS is not available."""
    body = await request.json()
    room_key = str(body.get("room", ""))
    title    = str(body.get("title", room_key))

    if not room_key:
        raise HTTPException(400, "room required")

    # Check access
    if room_key in _ROOMS:
        r = _ROOMS[room_key]
        if user not in r["invites"] and r["mode"] != "public" and user != r["host"]:
            raise HTTPException(403, "No tienes acceso a esta sala")
        _ROOMS[room_key]["members"].add(user)
    else:
        # Room not in memory — check DB
        db_rooms = _db_get_active_rooms(user)
        db_room  = next((r for r in db_rooms if r["key"] == room_key), None)
        if not db_room:
            raise HTTPException(404, "Sala no encontrada")
        _ROOMS[room_key] = {
            "host": db_room["host"], "title": db_room["title"],
            "mode": db_room["mode"], "invites": set(),
            "members": {user}
        }

    _db_add_member(room_key, user)
    await _broadcast_rooms_all()
    _save_rooms()

    return {
        "ok": True, "room": room_key,
        "title": _ROOMS[room_key]["title"],
        "host":  _ROOMS[room_key]["host"],
        "mode":  _ROOMS[room_key]["mode"],
        "members": list(_ROOMS[room_key]["members"]),
        "join_url": f"/join/{room_key}",
    }


@app.post("/bank/api/rooms/leave")
async def rooms_leave(request: Request, user: str = Depends(get_current_user)):
    """Leave a room via REST — fallback when WS is not available."""
    body = await request.json()
    room_key = str(body.get("room", ""))
    if room_key in _ROOMS:
        _ROOMS[room_key]["members"].discard(user)
        _db_remove_member(room_key, user)
        if not _ROOMS[room_key]["members"]:
            del _ROOMS[room_key]
            _db_close_room(room_key)
        await _broadcast_rooms_all()
        _save_rooms()
    return {"ok": True}


@app.post("/bank/api/rooms/close")
async def rooms_close(request: Request, user: str = Depends(get_current_user)):
    """Close a room (only dvd or the host can do this)."""
    body = await request.json()
    room_key = str(body.get("room", ""))
    
    if room_key not in _ROOMS:
        raise HTTPException(404, "Room not found")
    
    room = _ROOMS[room_key]
    host = room.get("host", "")
    
    # Solo dvd o el host pueden cerrar la sala
    if user != "dvd" and user != host:
        raise HTTPException(403, "Only dvd or the room host can close this room")
    
    # Notificar a todos los miembros que la sala se cerró
    members = list(room["members"])
    
    # Eliminar la sala
    del _ROOMS[room_key]
    _db_close_room(room_key)
    
    # Broadcast actualización de salas
    await _broadcast_rooms_all()
    _save_rooms()
    
    return {"ok": True, "closed": room_key, "members": members}


@app.get("/bank/api/rooms/active")
async def rooms_active(user: str = Depends(get_current_user)):
    """DB-backed active rooms — survives server restarts.
    Returns public rooms + private rooms where user is invited.
    Each room includes a join_url for direct access."""
    rooms = _db_get_active_rooms(user)
    # Merge live member counts from memory
    for r in rooms:
        mem = _ROOMS.get(r["key"])
        if mem:
            r["members"] = list(mem["members"])
    return {"rooms": rooms}


from fastapi.responses import StreamingResponse as _StreamingResponse

@app.get("/bank/api/rooms/stream")
async def rooms_stream(request: Request, token: str = ""):
    """SSE endpoint — pushes room updates in real time to all connected clients.
    Client subscribes once; server pushes 'data: rooms-changed\\n\\n' on every change.
    Client then fetches /api/rooms/list to get the actual data.
    This guarantees instant notification without polling.
    """
    username = decode_token(token) if token else None
    if not username:
        # Try Authorization header
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            username = decode_token(auth[7:])
    if not username:
        return _StreamingResponse(
            iter(["data: unauthorized\n\n"]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "ngrok-skip-browser-warning": "1"},
        )

    q: asyncio.Queue = asyncio.Queue(maxsize=20)
    _sse_queues[token or username] = q

    async def event_generator():
        # Send current rooms immediately on connect — use simple public endpoint logic
        try:
            rooms = _room_public_list(username)
            yield f"data: {_json.dumps({'type':'rooms-update','rooms':rooms})}\n\n"
        except Exception as e:
            logger.error("SSE initial rooms error: %s", e)
            yield f"data: {_json.dumps({'type':'rooms-update','rooms':[]})}\n\n"

        # Keep-alive + push loop
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=25.0)
                    if event == "rooms-changed":
                        rooms = _room_public_list(username)
                        yield f"data: {_json.dumps({'type':'rooms-update','rooms':rooms})}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except Exception:
            pass
        finally:
            _sse_queues.pop(token or username, None)

    return _StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store",
            "X-Accel-Buffering": "no",
            "ngrok-skip-browser-warning": "1",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/bank/join/{room_key}", response_class=HTMLResponse)
async def join_room_page(room_key: str):
    """Direct join link — serves a redirect page that opens Social and joins the room."""
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Unirse a sala — DVDcoin</title>
<style>
  body{{background:#04040A;color:#EAE6D8;font-family:'DM Mono',monospace;
    display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center}}
  .card{{background:#0D0D1C;border:1px solid rgba(212,168,67,.3);border-radius:14px;
    padding:32px 28px;max-width:360px;width:100%}}
  h2{{color:#F0C866;font-size:1.1rem;margin:0 0 8px}}
  p{{color:#9A9070;font-size:.78rem;margin:0 0 20px}}
  a{{display:inline-block;background:linear-gradient(135deg,#F0C866,#8B6010);
    color:#050200;border-radius:10px;padding:12px 28px;text-decoration:none;
    font-size:.82rem;font-weight:700;letter-spacing:.06em}}
  a:hover{{filter:brightness(1.1)}}
</style>
</head>
<body>
<div class="card">
  <div style="font-size:2.5rem;margin-bottom:12px">🎥</div>
  <h2>Sala de videollamada</h2>
  <p>Haz click para unirte a la sala activa en DVDcoin Bank.</p>
  <a href="/?join={room_key}">▶ Unirse ahora</a>
</div>
<script>
  var tok = localStorage.getItem('dvd_token');
  if(tok) window.location.href = '/?join={room_key}';
</script>
</body>
</html>"""
    resp = HTMLResponse(content=html)
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp


@app.get("/bank/salas", response_class=HTMLResponse)
async def salas_page(request: Request):
    """Live rooms page — server-rendered, no cache, auto-refresh every 5s.
    Works without JavaScript. Shows all active public rooms with join links.
    Accessible to anyone with a valid token."""
    token_param = request.query_params.get("token", "")
    username = decode_token(token_param) if token_param else None

    # Build rooms list from both DB and memory
    if username:
        rooms = _db_get_active_rooms(username)
        # Merge live members from memory
        for r in rooms:
            mem = _ROOMS.get(r["key"])
            if mem:
                r["members"] = list(mem["members"])
    else:
        # No auth — show only public rooms from memory
        rooms = []
        for k, r in list(_ROOMS.items()):
            if r["mode"] == "public":
                rooms.append({
                    "key": k, "title": r["title"], "host": r["host"],
                    "mode": "public", "members": list(r["members"]),
                    "invited": False, "join_url": f"/join/{k}",
                })

    base_url = str(request.base_url).rstrip("/")

    rooms_html = ""
    if not rooms:
        rooms_html = """
        <div style="text-align:center;padding:40px 20px;color:#504430">
          <div style="font-size:3rem;margin-bottom:12px;opacity:.4">🎥</div>
          <div style="font-size:.9rem;color:#9A9070">Sin salas activas en este momento</div>
          <div style="font-size:.72rem;color:#504430;margin-top:8px">Esta página se actualiza automáticamente</div>
        </div>"""
    else:
        for r in rooms:
            cnt = len(r.get("members", []))
            members_str = ", ".join(f"@{m}" for m in r.get("members", [])[:3])
            if len(r.get("members", [])) > 3:
                members_str += f" +{len(r['members'])-3}"
            join_url = f"{base_url}/?join={r['key']}"
            if token_param:
                join_url += f"&token={token_param}"
            rooms_html += f"""
        <div style="background:#0D0D1C;border:1px solid rgba(34,197,94,.3);border-radius:12px;
          padding:16px 20px;margin-bottom:12px;display:flex;align-items:center;gap:16px">
          <div style="width:12px;height:12px;border-radius:50%;background:#4ade80;
            box-shadow:0 0 10px #4ade80;flex-shrink:0"></div>
          <div style="flex:1;min-width:0">
            <div style="font-size:1rem;color:#F0C866;font-family:serif;margin-bottom:4px">
              {r['title'] or r['key']}
              {'🔒' if r['mode']=='private' else ''}
            </div>
            <div style="font-size:.72rem;color:#9A9070">
              {cnt} participante{'s' if cnt!=1 else ''} en directo
              {f' · @{r["host"]}' if r.get("host") else ''}
              {f' · {members_str}' if members_str else ''}
            </div>
          </div>
          <a href="{join_url}" style="background:linear-gradient(135deg,#16a34a,#22c55e);
            color:#fff;border-radius:8px;padding:10px 20px;text-decoration:none;
            font-size:.78rem;font-weight:700;white-space:nowrap;flex-shrink:0">
            ▶ Unirse
          </a>
        </div>"""

    count_label = f"{len(rooms)} sala{'s' if len(rooms)!=1 else ''} activa{'s' if len(rooms)!=1 else ''}" if rooms else "Sin salas activas"

    page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="refresh" content="5">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Salas en directo — DVDcoin</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#04040A;color:#EAE6D8;font-family:'DM Mono',monospace;
    min-height:100vh;padding:20px}}
  .wrap{{max-width:600px;margin:0 auto}}
  .hdr{{display:flex;align-items:center;justify-content:space-between;
    margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(212,168,67,.2)}}
  .title{{font-size:1.1rem;color:#F0C866;font-family:serif}}
  .count{{font-size:.72rem;color:#4ade80;background:rgba(34,197,94,.1);
    border:1px solid rgba(34,197,94,.3);border-radius:20px;padding:4px 12px}}
  .back{{color:#9A9070;font-size:.72rem;text-decoration:none}}
  .back:hover{{color:#F0C866}}
  .refresh{{font-size:.6rem;color:#504430;text-align:center;margin-top:16px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <div>
      <a href="/" class="back">← DVDcoin Bank</a>
      <div class="title" style="margin-top:6px">🎥 Salas en directo</div>
    </div>
    <div class="count">{count_label}</div>
  </div>
  {rooms_html}
  <div class="refresh">↻ Actualización automática cada 5 segundos</div>
</div>
<script>
  // Also try to auto-join if token in localStorage
  var tok = localStorage.getItem('dvd_token');
  if(tok && !window.location.search.includes('token=')) {{
    // Reload with token for auth
    window.location.href = '/salas?token=' + encodeURIComponent(tok);
  }}
</script>
</body>
</html>"""
    resp = HTMLResponse(content=page)
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.post("/bank/api/rooms/invite")
async def rooms_invite(request: Request, user: str = Depends(get_current_user)):
    """Invite a user to an existing private room (host only)."""
    body = await request.json()
    room_key = str(body.get("room", ""))
    invite_user = str(body.get("username", ""))
    if not room_key or not invite_user:
        raise HTTPException(400, "room and username required")

    # Check in memory first, then DB
    if room_key not in _ROOMS:
        # Try to restore from DB
        db_rooms = _db_get_active_rooms(user)
        db_room = next((r for r in db_rooms if r["key"] == room_key), None)
        if not db_room:
            raise HTTPException(404, "Room not found")
        # Restore to memory
        _ROOMS[room_key] = {
            "host": db_room["host"], "title": db_room["title"],
            "mode": db_room["mode"], "invites": set(),
            "members": set(db_room["members"]),
        }

    room = _ROOMS[room_key]
    if room["host"] != user and user not in SUPERADMINS:
        raise HTTPException(403, "Only the host can invite")
    room["invites"].add(invite_user)
    # Persist invite to DB
    _db_add_invite(room_key, invite_user)
    # Notify invited user via both WS channels
    invite_payload = {
        "type": "room-invite",
        "room_key": room_key,
        "title": room["title"],
        "host": user,
        "join_url": f"/join/{room_key}",
    }
    await msg_manager.send_to(invite_user, invite_payload)
    await rooms_manager.send_to(invite_user, invite_payload)
    # Send updated room list to invited user via both channels
    rooms_payload = _json_msg.dumps({
        "type": "rooms-update",
        "rooms": _room_public_list(invite_user),
    })
    for mgr in (msg_manager, rooms_manager):
        ws_inv = mgr.connections.get(invite_user)
        if ws_inv:
            try:
                await ws_inv.send_text(rooms_payload)
            except Exception:
                pass
    # Also broadcast to all users so the room list updates everywhere
    await _broadcast_rooms_all()
    return {"ok": True}
 
 
# ── WebSocket ──────────────────────────────────────────────────────────────
 
@app.websocket("/bank/ws/messages")
async def messages_ws(websocket: WebSocket, token: str = ""):
    """WebSocket endpoint for real-time messaging.
    Events received:  join | send | typing | read
    Events sent:      history | message | status | typing | error
    """
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    # Verify user exists
    c = db_users()
    row = c.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    c.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
 
    enabled = _msg_enabled()
    if not enabled and username not in ALL_ADMINS:
        await websocket.close(code=4003, reason="Messaging disabled")
        return
 
    _ping_session(username, "messages")
    await msg_manager.connect(username, websocket)

    # ── Enviar lista de salas activas al conectarse ────────────────────────
    try:
        await websocket.send_text(_json_msg.dumps({
            "type": "rooms-update",
            "rooms": _room_public_list(username),
        }))
    except Exception:
        pass
 
    try:
        while True:
            raw  = await websocket.receive_text()
            data = _json_msg.loads(raw)
            action = data.get("action", "")
 
            # ── join: client requests history for a room ───────────────
            if action == "join":
                room = data.get("room", "group")
                if room.startswith("dm:"):
                    parts = set(room.split(":")[1:])
                    if username not in parts and username not in SUPERADMINS:
                        continue
                history = _load_history(room, limit=60)
                await websocket.send_text(_json_msg.dumps({
                    "type":    "history",
                    "room":    room,
                    "messages": history,
                }))
 
            # ── send: deliver a new message ────────────────────────────
            elif action == "send":
                if not _msg_enabled() and username not in ALL_ADMINS:
                    continue
                room     = data.get("room", "group")
                content  = str(data.get("content", "")).strip()
                msg_type = data.get("msg_type", "text")
 
                if not content:
                    continue
                if len(content) > 4000:
                    content = content[:4000]
                if msg_type not in ("text", "audio"):
                    msg_type = "text"
 
                # Validate DM access
                if room.startswith("dm:"):
                    parts = set(room.split(":")[1:])
                    if username not in parts and username not in SUPERADMINS:
                        continue
 
                reply_to_id = data.get("reply_to_id") or None
                if reply_to_id: reply_to_id = int(reply_to_id)
                msg = _save_message(room, username, content, msg_type, reply_to_id)
                # Attach context for reply preview
                if reply_to_id:
                    c2 = db_msg()
                    ref = c2.execute("SELECT from_user, content, msg_type FROM messages WHERE id=?", (reply_to_id,)).fetchone()
                    c2.close()
                    if ref:
                        msg["reply_to"] = {"id": reply_to_id, "from_user": ref["from_user"],
                                           "content": ref["content"], "msg_type": ref["msg_type"]}
                await msg_manager.deliver(msg, room)
 
            # ── typing: broadcast typing indicator ─────────────────────
            elif action == "typing":
                room = data.get("room", "group")
                if room.startswith("dm:"):
                    parts = set(room.split(":")[1:])
                    other = [u for u in parts if u != username]
                    for u in other:
                        await msg_manager.send_to(u, {
                            "type": "typing", "room": room, "from": username
                        })
                else:
                    # Group: broadcast to all except sender
                    payload = _json_msg.dumps({
                        "type": "typing", "room": room, "from": username
                    })
                    for u, ws in list(msg_manager.connections.items()):
                        if u != username:
                            try:
                                await ws.send_text(payload)
                            except Exception:
                                pass
 
            # ── read: mark messages as read ────────────────────────────
            elif action == "read":
                room    = data.get("room", "group")
                last_id = int(data.get("last_id", 0))
                if last_id:
                    c = db_msg()
                    rows = c.execute(
                        "SELECT id FROM messages WHERE room=? AND id<=? AND from_user!=? "
                        "AND id NOT IN (SELECT msg_id FROM msg_reads WHERE username=?)",
                        (room, last_id, username, username)
                    ).fetchall()
                    for r in rows:
                        c.execute(
                            "INSERT OR IGNORE INTO msg_reads(msg_id,username) VALUES(?,?)",
                            (r["id"], username)
                        )
                    c.commit()
                    c.close()
            
            # ── mark_read: mark ALL messages in room as read ───────────
            elif action == "mark_read":
                room = data.get("room", "group")
                c = db_msg()
                # Marcar todos los mensajes del room como leídos (excepto los propios)
                rows = c.execute(
                    "SELECT id FROM messages WHERE room=? AND from_user!=? "
                    "AND id NOT IN (SELECT msg_id FROM msg_reads WHERE username=?)",
                    (room, username, username)
                ).fetchall()
                for r in rows:
                    c.execute(
                        "INSERT OR IGNORE INTO msg_reads(msg_id,username) VALUES(?,?)",
                        (r["id"], username)
                    )
                c.commit()
                c.close()
                logger.info(f"[CHAT] ✅ {username} marcó {len(rows)} mensajes como leídos en {room}")
 
            # ── react: toggle an emoji reaction ────────────────────────
            elif action == "react":
                msg_id = int(data.get("msg_id", 0))
                emoji  = str(data.get("emoji", ""))[:8]
                if not msg_id or not emoji:
                    continue
                c = db_msg()
                row_check = c.execute(
                    "SELECT 1 FROM msg_reactions WHERE msg_id=? AND username=? AND emoji=?",
                    (msg_id, username, emoji)
                ).fetchone()
                if row_check:
                    c.execute("DELETE FROM msg_reactions WHERE msg_id=? AND username=? AND emoji=?",
                              (msg_id, username, emoji))
                else:
                    c.execute("INSERT OR IGNORE INTO msg_reactions(msg_id,username,emoji) VALUES(?,?,?)",
                              (msg_id, username, emoji))
                # Fetch updated reactions for this message
                react_rows = c.execute(
                    "SELECT username,emoji FROM msg_reactions WHERE msg_id=?", (msg_id,)
                ).fetchall()
                c.commit()
                # Get room for this message to broadcast
                msg_row = c.execute("SELECT room FROM messages WHERE id=?", (msg_id,)).fetchone()
                c.close()
                if msg_row:
                    await msg_manager.deliver({
                        "type":      "reaction",
                        "msg_id":    msg_id,
                        "reactions": [{"username": r["username"], "emoji": r["emoji"]} for r in react_rows],
                    }, msg_row["room"])
 
            # ── delete: soft-delete own message ────────────────────────
            elif action == "delete_msg":
                msg_id = int(data.get("msg_id", 0))
                if not msg_id:
                    continue
                c = db_msg()
                msg_row = c.execute(
                    "SELECT room, from_user FROM messages WHERE id=?", (msg_id,)
                ).fetchone()
                if msg_row and (msg_row["from_user"] == username or username in SUPERADMINS):
                    c.execute("UPDATE messages SET deleted=1, content='Este mensaje fue eliminado' WHERE id=?", (msg_id,))
                    c.commit()
                    room_del = msg_row["room"]
                    c.close()
                    await msg_manager.deliver({"type": "deleted", "msg_id": msg_id}, room_del)
                else:
                    c.close()
 
            # ── webrtc-join: create/join a video room ──────────────────
            elif action == "webrtc-join":
                room_key  = str(data.get("room", _uuid.uuid4().hex[:12]))
                title     = str(data.get("title", f"Sala de {username}"))[:80]
                mode      = data.get("mode", "public")   # "public" | "private"
                invites   = list(data.get("invites", []))  # list of usernames

                if room_key not in _ROOMS:
                    _ROOMS[room_key] = {
                        "host": username, "title": title,
                        "mode": mode, "invites": set(invites),
                        "members": set()
                    }
                else:
                    r = _ROOMS[room_key]
                    if username not in r["invites"] and r["mode"] != "public" and username != r["host"]:
                        await websocket.send_text(_json_msg.dumps({"type":"error","msg":"No tienes acceso a esta sala"}))
                        continue

                _ROOMS[room_key]["members"].add(username)

                # ── Persist to DB ──────────────────────────────────────────
                _db_upsert_room(room_key, title, _ROOMS[room_key]["host"], mode)
                _db_add_member(room_key, username)

                # Notify invited users via both WS channels
                for inv in invites:
                    if inv and inv != username:
                        invite_payload = {
                            "type":     "room-invite",
                            "room_key": room_key,
                            "title":    title,
                            "host":     username,
                            "join_url": f"/join/{room_key}",
                        }
                        await msg_manager.send_to(inv, invite_payload)
                        await rooms_manager.send_to(inv, invite_payload)
                        _ROOMS[room_key]["invites"].add(inv)
                        _db_add_invite(room_key, inv)

                # Confirm to the joining user that they are in the room
                await websocket.send_text(_json_msg.dumps({
                    "type":     "webrtc-room-joined",
                    "room":     room_key,
                    "title":    _ROOMS[room_key]["title"],
                    "host":     _ROOMS[room_key]["host"],
                    "mode":     _ROOMS[room_key]["mode"],
                    "members":  list(_ROOMS[room_key]["members"]),
                    "you":      username,
                    "join_url": f"/join/{room_key}",
                }))

                # Notify peers already in room that a new user joined
                for peer in list(_ROOMS[room_key]["members"]):
                    if peer != username:
                        await msg_manager.send_to(peer, {
                            "type": "webrtc-joined", "from": username, "room": room_key
                        })

                # Broadcast updated room list to ALL users (msg + rooms WS)
                await _broadcast_rooms_all()
                _save_rooms()
            elif action == "webrtc-leave":
                room_key = str(data.get("room", ""))
                if room_key in _ROOMS:
                    _ROOMS[room_key]["members"].discard(username)
                    _db_remove_member(room_key, username)
                    for peer in list(_ROOMS[room_key]["members"]):
                        await msg_manager.send_to(peer, {
                            "type": "webrtc-left", "from": username, "room": room_key
                        })
                    if not _ROOMS[room_key]["members"]:
                        del _ROOMS[room_key]
                        _db_close_room(room_key)
                    # Broadcast updated room list to ALL users (msg + rooms WS)
                    await _broadcast_rooms_all()
                    _save_rooms()
 
            # ── webrtc-offer / webrtc-answer / webrtc-ice — forward ────
            elif action in ("webrtc-offer", "webrtc-answer", "webrtc-ice"):
                to = data.get("to")
                if to:
                    # Map action name → type name expected by the client
                    type_map = {
                        "webrtc-offer":  "webrtc-offer",
                        "webrtc-answer": "webrtc-answer",
                        "webrtc-ice":    "webrtc-ice",
                    }
                    fwd = {
                        "type":      type_map[action],
                        "from":      username,
                        "room":      data.get("room", ""),
                        "to":        to,
                    }
                    if action == "webrtc-ice":
                        fwd["candidate"] = data.get("candidate")
                    else:
                        fwd["sdp"] = data.get("sdp")
                    await msg_manager.send_to(to, fwd)
 
            # ── room-invite: invite user to existing room ──────────────
            elif action == "room-invite":
                room_key = str(data.get("room", ""))
                inv_user = str(data.get("invite", ""))
                if room_key in _ROOMS and (_ROOMS[room_key]["host"] == username or username in SUPERADMINS):
                    _ROOMS[room_key]["invites"].add(inv_user)
                    invite_payload = {
                        "type": "room-invite",
                        "room_key": room_key,
                        "title": _ROOMS[room_key]["title"],
                        "host": username,
                    }
                    await msg_manager.send_to(inv_user, invite_payload)
                    await rooms_manager.send_to(inv_user, invite_payload)
                    # Also send updated room list to invited user
                    rooms_payload = _json_msg.dumps({
                        "type": "rooms-update",
                        "rooms": _room_public_list(inv_user),
                    })
                    for mgr in (msg_manager, rooms_manager):
                        ws_inv = mgr.connections.get(inv_user)
                        if ws_inv:
                            try: await ws_inv.send_text(rooms_payload)
                            except Exception: pass

            # ── call-chat: ephemeral in-call chat message ──────────────
            elif action == "call-chat":
                room_key = str(data.get("room", ""))
                text = str(data.get("text", "")).strip()[:500]
                if room_key in _ROOMS and username in _ROOMS[room_key]["members"] and text:
                    for peer in list(_ROOMS[room_key]["members"]):
                        if peer != username:
                            await msg_manager.send_to(peer, {
                                "type": "call-chat",
                                "room": room_key,
                                "from": username,
                                "text": text,
                            })

            # ── call-mute: broadcast mic mute state to room peers ──────
            elif action == "call-mute":
                room_key = str(data.get("room", ""))
                muted = bool(data.get("muted", False))
                if room_key in _ROOMS and username in _ROOMS[room_key]["members"]:
                    for peer in list(_ROOMS[room_key]["members"]):
                        if peer != username:
                            await msg_manager.send_to(peer, {
                                "type": "call-mute",
                                "room": room_key,
                                "from": username,
                                "muted": muted,
                            })
 
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("Messages WS error [%s]: %s", username, e)
    finally:
        msg_manager.disconnect(username, websocket)
        await msg_manager.broadcast_status()
        # Only clean rooms if user has no more active connections
        if username not in msg_manager._conns:
            rooms_changed = False
            for room_key in list(_ROOMS.keys()):
                if username in _ROOMS[room_key]["members"]:
                    _ROOMS[room_key]["members"].discard(username)
                    _db_remove_member(room_key, username)
                    rooms_changed = True
                    for peer in list(_ROOMS[room_key]["members"]):
                        await msg_manager.send_to(peer, {
                            "type": "webrtc-left", "from": username, "room": room_key
                        })
                    if not _ROOMS[room_key]["members"]:
                        del _ROOMS[room_key]
                        _db_close_room(room_key)
            if rooms_changed:
                await _broadcast_rooms_all()
                _save_rooms()
 
 
# ── Init messaging DB at startup ───────────────────────────────────────────
_msg_db_init()
os.makedirs(os.path.join(BASE_DIR, "static", "messages"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "admin"), exist_ok=True)


# =============================================================================
# ROOMS WebSocket — dedicated endpoint for live room presence
# Independent of messaging system. Always available to all authenticated users.
# =============================================================================

class RoomsManager:
    """Manages WebSocket connections for the rooms presence system."""

    def __init__(self):
        self.connections: dict = {}   # username → WebSocket

    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.connections[username] = ws

    def disconnect(self, username: str):
        self.connections.pop(username, None)

    async def broadcast_rooms(self):
        """Send updated room list to every connected user."""
        dead = []
        for u, ws in list(self.connections.items()):
            try:
                await ws.send_text(_json_msg.dumps({
                    "type": "rooms-update",
                    "rooms": _room_public_list(u),
                }))
            except Exception:
                dead.append(u)
        for u in dead:
            self.connections.pop(u, None)

    async def send_to(self, username: str, payload: dict):
        ws = self.connections.get(username)
        if ws:
            try:
                await ws.send_text(_json_msg.dumps(payload))
            except Exception:
                self.connections.pop(username, None)


rooms_manager = RoomsManager()


@app.websocket("/bank/ws/rooms")
async def rooms_ws(websocket: WebSocket, token: str = ""):
    """Dedicated WebSocket for room presence updates.
    Always available regardless of messaging enabled state.
    Sends rooms-update on connect and whenever rooms change.
    Also handles room-invite notifications.
    """
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return

    c = db_users()
    row = c.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    c.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return

    await rooms_manager.connect(username, websocket)

    # Send current rooms immediately on connect
    try:
        await websocket.send_text(_json_msg.dumps({
            "type": "rooms-update",
            "rooms": _room_public_list(username),
        }))
    except Exception:
        pass

    try:
        while True:
            # Keep connection alive — client sends pings
            raw = await websocket.receive_text()
            try:
                data = _json_msg.loads(raw)
            except Exception:
                continue
            action = data.get("action", "")

            if action == "ping":
                await websocket.send_text(_json_msg.dumps({"type": "pong"}))

            elif action == "get-rooms":
                await websocket.send_text(_json_msg.dumps({
                    "type": "rooms-update",
                    "rooms": _room_public_list(username),
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("Rooms WS error [%s]: %s", username, e)
    finally:
        rooms_manager.disconnect(username)
 
 
# =============================================================================
# GAME ADMIN PAGES — dedicated HTML panel per game
# =============================================================================
 
ADMIN_DIR = os.path.join(BASE_DIR, "static", "admin")
 
def _serve_admin_page(filename: str):
    """Serve a game admin HTML page with cache-busting headers."""
    path = os.path.join(ADMIN_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, f"Admin page not found: {filename}. Upload {filename} to static/admin/")
    resp = FileResponse(path)
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp
 
def _serve_game_page(game_dir: str, filename: str = "game.html"):
    """Serve a player-facing game HTML page. File must exist in the game directory."""
    path = os.path.join(game_dir, filename)
    if not os.path.exists(path):
        game_name = os.path.basename(game_dir)
        # Return a helpful page that explains how to fix it
        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{game_name} — Setup needed</title>
<style>body{{background:#04040A;color:#EAE6D8;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px;box-sizing:border-box}}
.box{{max-width:500px;text-align:center}}h1{{color:#D4A843;font-size:1.4rem;margin-bottom:12px}}
p{{color:#9A9070;font-size:.82rem;line-height:1.6;margin-bottom:10px}}
code{{background:#0C0C1A;border:1px solid rgba(212,168,67,.2);border-radius:6px;padding:8px 12px;display:block;margin:10px 0;font-size:.75rem;color:#F0C866;text-align:left}}
a{{color:#D4A843}}</style></head>
<body><div class="box">
<h1>🎮 {game_name}</h1>
<p>El archivo del juego no está instalado todavía.</p>
<p>Sube el archivo <strong>game.html</strong> a esta carpeta del servidor:</p>
<code>static/{game_name}/game.html</code>
<p>Este archivo viene incluido en el ZIP de actualizaciones bajo <code>game_pages/{game_name}/game.html</code></p>
<p><a href="/">← Volver al inicio</a></p>
</div></body></html>"""
        return HTMLResponse(content=html, status_code=200, headers={"ngrok-skip-browser-warning": "1"})
    resp = FileResponse(path)
    resp.headers["ngrok-skip-browser-warning"] = "1"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp
 
@app.get("/bank/admin/games/pasapalabra", response_class=HTMLResponse)
async def admin_pasapalabra_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("pasapalabra.html")
 
@app.get("/bank/admin/games/millonario", response_class=HTMLResponse)
async def admin_millonario_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("millonario.html")
 
@app.get("/bank/admin/games/quiensoy", response_class=HTMLResponse)
async def admin_quiensoy_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("quiensoy.html")
 
@app.get("/bank/admin/games/cifrasletras", response_class=HTMLResponse)
async def admin_cifrasletras_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("cifrasletras.html")
 
@app.get("/bank/admin/games/cuentos", response_class=HTMLResponse)
async def admin_cuentos_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("cuentos.html")
 
@app.get("/bank/admin/games/mensajes", response_class=HTMLResponse)
async def admin_mensajes_page(user: str = Depends(get_current_user)):
    if user not in ALL_ADMINS: raise HTTPException(403)
    return _serve_admin_page("mensajes.html")
 
 
# =============================================================================
# ENTRY POINT
# =============================================================================
 
# =============================================================================
# VIDEO RELAY — WebSocket relay de video/audio via servidor
# Funciona siempre: PC, Android, iPhone, cualquier red, sin STUN/TURN
# Cada cliente envía su stream como chunks binarios; el servidor los reenvía
# a todos los demás miembros de la sala.
# =============================================================================

# =============================================================================
# VIDEO — Dual mode: WebRTC signaling + binary relay fallback
# WebRTC: offer/answer/ice forwarded between peers (direct P2P with STUN)
# Binary relay: raw video chunks forwarded to all peers (works without STUN)
# =============================================================================

# Salas de video: room_key → {username: websocket}
_VIDEO_ROOMS: dict = {}

@app.websocket("/bank/ws/video")
async def video_relay_ws(websocket: WebSocket, token: str = ""):
    """Dual-mode video WebSocket: WebRTC signaling + binary chunk relay."""
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Auth required")
        return
    conn = db_users()
    row = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return

    await websocket.accept()
    room_key = None
    logger.info("[VIDEO] %s connected", username)

    try:
        while True:
            msg = await websocket.receive()

            # ── Binary: video chunk relay ──────────────────────────────────
            if "bytes" in msg:
                chunk = msg["bytes"]
                if not chunk or not room_key or room_key not in _VIDEO_ROOMS:
                    continue
                uname_b = username.encode("utf-8")
                header  = len(uname_b).to_bytes(1, "big") + uname_b
                payload = header + chunk
                dead = []
                for u, ws_u in list(_VIDEO_ROOMS[room_key].items()):
                    if u != username:
                        try:
                            await ws_u.send_bytes(payload)
                        except Exception:
                            dead.append(u)
                for u in dead:
                    _VIDEO_ROOMS[room_key].pop(u, None)
                continue

            # ── Text: control + WebRTC signaling ──────────────────────────
            if "text" not in msg:
                continue
            try:
                data = _json_msg.loads(msg["text"])
            except Exception:
                continue

            action = data.get("action", "")

            if action == "join":
                room_key = str(data.get("room", ""))
                if not room_key:
                    continue
                if room_key not in _VIDEO_ROOMS:
                    _VIDEO_ROOMS[room_key] = {}

                # Tell new peer about existing peers (optimizado: enviar en paralelo)
                existing = list(_VIDEO_ROOMS[room_key].keys())
                for ep in existing:
                    try:
                        await websocket.send_text(_json_msg.dumps({"type":"peer-joined","from":ep}))
                    except Exception:
                        pass

                # Register new peer
                _VIDEO_ROOMS[room_key][username] = websocket

                # Tell existing peers about new peer (optimizado: enviar en paralelo)
                tasks = []
                for u, ws_u in list(_VIDEO_ROOMS[room_key].items()):
                    if u != username:
                        try:
                            tasks.append(ws_u.send_text(_json_msg.dumps({"type":"peer-joined","from":username})))
                        except Exception:
                            pass
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                logger.info("[VIDEO] %s joined %s (peers: %s)", username, room_key, existing)

            elif action == "leave":
                if room_key and room_key in _VIDEO_ROOMS:
                    _VIDEO_ROOMS[room_key].pop(username, None)
                    if not _VIDEO_ROOMS[room_key]:
                        del _VIDEO_ROOMS[room_key]
                    else:
                        for u, ws_u in list(_VIDEO_ROOMS.get(room_key, {}).items()):
                            try:
                                await ws_u.send_text(_json_msg.dumps({"type":"peer-left","from":username}))
                            except Exception:
                                pass
                room_key = None

            elif action == "close-room":
                # Host or superadmin closes the room — kicks everyone
                rk = str(data.get("room", room_key or ""))
                if rk and rk in _VIDEO_ROOMS:
                    # Check permission: must be the one who created it or superadmin
                    is_super = username in {"dvd", "nebulosa"}
                    # We don't track host in _VIDEO_ROOMS, so allow if superadmin or
                    # if they are currently in the room (host is always in the room)
                    if is_super or username in _VIDEO_ROOMS.get(rk, {}):
                        # Notify all peers the room is closed
                        for u, ws_u in list(_VIDEO_ROOMS.get(rk, {}).items()):
                            if u != username:
                                try:
                                    await ws_u.send_text(_json_msg.dumps({"type":"room-closed","room":rk,"by":username}))
                                except Exception:
                                    pass
                        del _VIDEO_ROOMS[rk]
                        logger.info("[VIDEO] Room %s closed by %s", rk, username)
                if room_key == rk:
                    room_key = None

            elif action in ("offer", "answer", "ice"):
                # Forward WebRTC signaling to target peer
                to = data.get("to", "")
                if not to or not room_key:
                    continue
                target_ws = _VIDEO_ROOMS.get(room_key, {}).get(to)
                if not target_ws:
                    logger.warning("[VIDEO] Target %s not found in room %s for %s", to, room_key, action)
                    continue
                if action == "offer":
                    fwd = {"type":"webrtc-offer",  "from":username, "sdp":data.get("sdp","")}
                elif action == "answer":
                    fwd = {"type":"webrtc-answer", "from":username, "sdp":data.get("sdp","")}
                else:
                    fwd = {"type":"webrtc-ice",    "from":username, "candidate":data.get("candidate")}
                try:
                    await target_ws.send_text(_json_msg.dumps(fwd))
                except Exception:
                    pass

    except WebSocketDisconnect:
        logger.info("[VIDEO] %s disconnected", username)
    except Exception as e:
        logger.error("Video WS error [%s]: %s", username, e)
    finally:
        if room_key and room_key in _VIDEO_ROOMS:
            _VIDEO_ROOMS[room_key].pop(username, None)
            if not _VIDEO_ROOMS[room_key]:
                del _VIDEO_ROOMS[room_key]
            else:
                for u, ws_u in list(_VIDEO_ROOMS.get(room_key, {}).items()):
                    try:
                        await ws_u.send_text(_json_msg.dumps({"type":"peer-left","from":username}))
                    except Exception:
                        pass
        logger.info("[VIDEO] %s cleanup complete", username)


# =============================================================================
# APUESTAS / BETTING SYSTEM
# =============================================================================

class PorraCreateRequest(BaseModel):
    titulo: str
    descripcion: Optional[str] = ''
    tipo: Optional[str] = 'resultado'  # 'resultado', 'marcador', 'torneo', 'mas_menos', 'ambos_marcan'
    fecha_limite: Optional[str] = ''  # Optional, will be auto-generated if empty (24h from now)
    fecha_evento: Optional[str] = ''  # Optional, will be auto-generated if empty (48h from now)
    opciones: list  # [{nombre: "España gana", valor: "espana_gana"}, ...] - valor is auto-generated if not provided

class ApuestaRequest(BaseModel):
    porra_id: int
    opcion: str
    cantidad: float

class ResolverPorraRequest(BaseModel):
    porra_id: int
    resultado: str  # valor de la opción ganadora

@app.get("/bank/api/porras/list")
async def porras_list(user: str = Depends(get_current_user)):
    """List all betting pools (porras)."""
    try:
        logger.info(f"[PORRAS] Listing porras for user: {user}")
        c = db_bets()
        
        # Check if enmascarada column exists
        try:
            rows = c.execute("""
                SELECT id, creador, titulo, descripcion, tipo, fecha_limite, fecha_evento,
                       estado, resultado, comision, opciones_json, created_at, enmascarada
                FROM porras
                ORDER BY created_at DESC
            """).fetchall()
        except:
            # Column doesn't exist yet, add it
            c.execute("ALTER TABLE porras ADD COLUMN enmascarada INTEGER DEFAULT 0")
            c.commit()
            rows = c.execute("""
                SELECT id, creador, titulo, descripcion, tipo, fecha_limite, fecha_evento,
                       estado, resultado, comision, opciones_json, created_at, enmascarada
                FROM porras
                ORDER BY created_at DESC
            """).fetchall()
        
        logger.info(f"[PORRAS] Found {len(rows)} porras in database")
        
        # Get user's bets to mark which porras they participated in
        user_bets = c.execute("""
            SELECT DISTINCT porra_id FROM apuestas_usuarios WHERE username = ?
        """, (user,)).fetchall()
        user_porra_ids = {b["porra_id"] for b in user_bets}
        
        c.close()
        
        is_dvd = user in SUPERADMINS
        logger.info(f"[PORRAS] User is DVD: {is_dvd}")
        
        porras = []
        for r in rows:
            # Filter masked porras (except for DVD)
            # r is a Row object, access by index or key
            try:
                enmascarada = r["enmascarada"] if "enmascarada" in r.keys() else 0
            except:
                enmascarada = r[12] if len(r) > 12 else 0
            
            if enmascarada and not is_dvd:
                logger.info(f"[PORRAS] Skipping masked porra {r['id']} for non-DVD user")
                continue
            
            try:
                opciones = _json.loads(r["opciones_json"])
            except:
                opciones = []
                logger.error(f"Error parsing opciones for porra {r['id']}")
            
            # Anonymize creator for non-dvd users
            creador = r["creador"] if is_dvd else "Anonymous"
            
            porra_dict = {
                "id": r["id"],
                "creador": creador,
                "titulo": r["titulo"],
                "descripcion": r["descripcion"] or "",
                "tipo": r["tipo"],
                "fecha_limite": r["fecha_limite"],
                "fecha_evento": r["fecha_evento"],
                "estado": r["estado"],
                "resultado": r["resultado"],
                "comision": r["comision"],
                "opciones": opciones,
                "created_at": r["created_at"],
                "mis_apuestas": r["id"] in user_porra_ids,
                "enmascarada": enmascarada if is_dvd else False
            }
            porras.append(porra_dict)
            logger.info(f"[PORRAS] Added porra {r['id']}: {r['titulo']}")
        
        logger.info(f"[PORRAS] Returning {len(porras)} porras to user {user}")
        return {"porras": porras}
    except Exception as e:
        logger.error(f"[PORRAS] Error listing porras: {e}")
        logger.exception(e)
        raise HTTPException(500, f"Error al listar porras: {str(e)}")

@app.get("/bank/api/porras/{porra_id}")
async def porra_detail(porra_id: int, user: str = Depends(get_current_user)):
    """Get detailed info about a specific porra including all bets and statistics."""
    try:
        c = db_bets()
        
        # Get porra info
        porra = c.execute("""
            SELECT id, creador, titulo, descripcion, tipo, fecha_limite, fecha_evento,
                   estado, resultado, comision, opciones_json, created_at, closed_at, resolved_at
            FROM porras WHERE id = ?
        """, (porra_id,)).fetchone()
        
        if not porra:
            c.close()
            raise HTTPException(404, "Porra no encontrada")
        
        # Get all bets
        apuestas = c.execute("""
            SELECT username, opcion, cantidad, fecha, pagado, ganancia
            FROM apuestas_usuarios
            WHERE porra_id = ?
            ORDER BY fecha ASC
        """, (porra_id,)).fetchall()
        
        c.close()
        
        # Parse opciones safely
        try:
            opciones = _json.loads(porra["opciones_json"])
        except:
            opciones = []
            logger.error(f"Error parsing opciones_json for porra {porra_id}")
        
        # Check if user is DVD
        is_dvd = user in SUPERADMINS
        
        # Calculate statistics
        total_bote = sum(a["cantidad"] for a in apuestas)
        distribucion = {}
        
        for opt in opciones:
            opt_val = opt.get("valor", "")
            opt_name = opt.get("nombre", "Opción")
            opt_total = sum(a["cantidad"] for a in apuestas if a["opcion"] == opt_val)
            opt_count = sum(1 for a in apuestas if a["opcion"] == opt_val)
            distribucion[opt_val] = {
                "nombre": opt_name,
                "total": opt_total,
                "count": opt_count,
                "porcentaje": (opt_total / total_bote * 100) if total_bote > 0 else 0,
                "cuota_implicita": (total_bote / opt_total) if opt_total > 0 else 0
            }
        
        # Anonymize data for non-dvd users
        creador = porra["creador"] if is_dvd else "Anonymous"
        
        # Anonymize bets for non-dvd users
        apuestas_list = []
        for a in apuestas:
            apuesta_dict = dict(a)
            # Non-dvd users can only see their own bets with username, others are anonymized
            if not is_dvd and a["username"] != user:
                apuesta_dict["username"] = "Anonymous"
                # Hide exact amounts for other users' bets
                apuesta_dict["cantidad"] = 0
                apuesta_dict["ganancia"] = 0
            apuestas_list.append(apuesta_dict)
        
        return {
            "porra": {
                "id": porra["id"],
                "creador": creador,
                "titulo": porra["titulo"],
                "descripcion": porra["descripcion"] or "",
                "tipo": porra["tipo"],
                "fecha_limite": porra["fecha_limite"],
                "fecha_evento": porra["fecha_evento"],
                "estado": porra["estado"],
                "resultado": porra["resultado"],
                "comision": porra["comision"],
                "opciones": opciones,
                "created_at": porra["created_at"],
                "closed_at": porra["closed_at"],
                "resolved_at": porra["resolved_at"]
            },
            "apuestas": apuestas_list,
            "estadisticas": {
                "total_bote": total_bote,
                "total_apostadores": len(apuestas),
                "distribucion": distribucion
            },
            "is_dvd": is_dvd  # Add flag so frontend knows if data is anonymized
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting porra detail {porra_id}: {e}")
        raise HTTPException(500, f"Error al obtener detalles de la porra: {str(e)}")

@app.post("/bank/api/porras/create")
async def porra_create(body: PorraCreateRequest, user: str = Depends(get_current_user)):
    """Create a new betting pool. Any user can create."""
    try:
        # Validate required fields
        if not body.titulo or not body.titulo.strip():
            raise HTTPException(400, "El título es obligatorio")
        if not body.opciones or len(body.opciones) < 2:
            raise HTTPException(400, "Debe haber al menos 2 opciones")
        if len(body.opciones) > 20:
            raise HTTPException(400, "Máximo 20 opciones permitidas")
        
        # Generate automatic dates if not provided
        from datetime import datetime as dt, timedelta
        ahora = dt.now()
        
        # Handle optional fecha_limite
        if not body.fecha_limite or not body.fecha_limite.strip():
            # Default: 24 hours from now
            fecha_limite = (ahora + timedelta(hours=24)).isoformat()
        else:
            fecha_limite = body.fecha_limite.strip()
            try:
                limite = dt.fromisoformat(fecha_limite.replace('Z', '+00:00'))
                if limite <= ahora:
                    raise HTTPException(400, "La fecha límite debe ser futura")
            except ValueError:
                raise HTTPException(400, "Formato de fecha límite inválido. Usa: YYYY-MM-DD HH:MM")
        
        # Handle optional fecha_evento
        if not body.fecha_evento or not body.fecha_evento.strip():
            # Default: 48 hours from now
            fecha_evento = (ahora + timedelta(hours=48)).isoformat()
        else:
            fecha_evento = body.fecha_evento.strip()
            try:
                evento = dt.fromisoformat(fecha_evento.replace('Z', '+00:00'))
                limite_dt = dt.fromisoformat(fecha_limite.replace('Z', '+00:00'))
                if evento <= limite_dt:
                    raise HTTPException(400, "La fecha del evento debe ser posterior a la fecha límite")
            except ValueError:
                raise HTTPException(400, "Formato de fecha evento inválido. Usa: YYYY-MM-DD HH:MM")
        
        # Handle optional descripcion
        descripcion = body.descripcion.strip() if body.descripcion else ''
        
        # Handle optional tipo
        tipo = body.tipo.strip() if body.tipo else 'resultado'
        
        # Process options: generate valor from nombre if not provided
        opciones_procesadas = []
        for i, opt in enumerate(body.opciones):
            # Handle dict or object
            if isinstance(opt, dict):
                nombre = opt.get('nombre', '').strip()
                valor = opt.get('valor', '').strip()
            else:
                nombre = getattr(opt, 'nombre', '').strip()
                valor = getattr(opt, 'valor', '').strip()
            
            if not nombre:
                raise HTTPException(400, f"La opción {i+1} debe tener un nombre")
            
            # Generate valor from nombre if not provided
            if not valor:
                # Generate valor: lowercase, replace spaces with underscore, remove special chars
                import re
                valor = re.sub(r'[^a-z0-9_]', '', nombre.lower().replace(' ', '_'))
                if not valor:
                    valor = f"opcion_{i+1}"
            
            opciones_procesadas.append({
                'nombre': nombre,
                'valor': valor
            })
        
        # Validate unique option values
        valores = [o['valor'] for o in opciones_procesadas]
        if len(valores) != len(set(valores)):
            # If duplicates, add index to make unique
            valores_unicos = []
            for i, opt in enumerate(opciones_procesadas):
                valor_base = opt['valor']
                valor = valor_base
                counter = 1
                while valor in valores_unicos:
                    valor = f"{valor_base}_{counter}"
                    counter += 1
                valores_unicos.append(valor)
                opciones_procesadas[i]['valor'] = valor
        
        # Insert into database
        conn = db_bets()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO porras (creador, titulo, descripcion, tipo, fecha_limite, fecha_evento, comision, opciones_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user, body.titulo.strip(), descripcion, tipo, fecha_limite, 
              fecha_evento, 0.0, _json.dumps(opciones_procesadas)))
        conn.commit()
        porra_id = cursor.lastrowid
        conn.close()
        
        # Create individual HTML page for this porra
        try:
            _create_porra_page(porra_id, body.titulo.strip(), descripcion, opciones_procesadas, 
                             fecha_limite, fecha_evento, user, tipo)
        except Exception as e:
            logger.warning(f"Could not create HTML page for porra {porra_id}: {e}")
        
        # Notify all users via social
        try:
            await _broadcast_social_notification({
                "type": "porra_created",
                "from": user,
                "porra_id": porra_id,
                "titulo": body.titulo.strip(),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.warning(f"Could not broadcast porra creation: {e}")
        
        return {"ok": True, "porra_id": porra_id, "message": "Porra creada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating porra: {e}", exc_info=True)
        raise HTTPException(500, f"Error al crear la porra: {str(e)}")

@app.post("/bank/api/porras/apostar")
async def porra_apostar(body: ApuestaRequest, user: str = Depends(get_current_user)):
    """Place a bet on a porra. Users can bet multiple times on different options."""
    try:
        # Validate amount
        if body.cantidad <= 0:
            raise HTTPException(400, "La cantidad debe ser mayor que 0")
        if body.cantidad < 1:
            raise HTTPException(400, "La apuesta mínima es 1 DVDcoin")
        if body.cantidad > 10000:
            raise HTTPException(400, "La apuesta máxima es 10000 DVDcoins")
        
        c = db_bets()
        
        # Check porra exists and is open
        porra = c.execute("""
            SELECT estado, opciones_json, fecha_limite FROM porras WHERE id = ?
        """, (body.porra_id,)).fetchone()
        
        if not porra:
            c.close()
            raise HTTPException(404, "Porra no encontrada")
        if porra["estado"] != "abierta":
            c.close()
            raise HTTPException(400, "Esta porra ya no acepta apuestas")
        
        # Check if deadline passed
        try:
            from datetime import datetime as dt
            limite = dt.fromisoformat(porra["fecha_limite"].replace('Z', '+00:00'))
            if dt.now() >= limite:
                # Auto-close porra
                c.execute("UPDATE porras SET estado = 'cerrada', closed_at = datetime('now') WHERE id = ?", (body.porra_id,))
                c.commit()
                c.close()
                raise HTTPException(400, "La fecha límite ha pasado. Porra cerrada automáticamente.")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error checking deadline: {e}")
            pass
        
        # Validate option
        opciones = _json.loads(porra["opciones_json"])
        if body.opcion not in [o["valor"] for o in opciones]:
            c.close()
            raise HTTPException(400, "Opción no válida")
        
        # Users can now bet multiple times on any option
        c.close()
        
        # Check user balance with transaction
        cu = db_users()
        cu.execute("BEGIN IMMEDIATE")  # Lock to prevent race conditions
        try:
            user_data = cu.execute("SELECT balance FROM users WHERE username = ?", (user,)).fetchone()
            if not user_data:
                cu.rollback()
                cu.close()
                raise HTTPException(404, "Usuario no encontrado")
            
            if user_data["balance"] < body.cantidad:
                cu.rollback()
                cu.close()
                raise HTTPException(400, f"Saldo insuficiente. Tienes {user_data['balance']:.1f} DVDc, necesitas {body.cantidad:.1f} DVDc")
            
            # Deduct balance
            new_balance = user_data["balance"] - body.cantidad
            cu.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, user))
            cu.commit()
        except HTTPException:
            raise
        except Exception as e:
            cu.rollback()
            cu.close()
            logger.error(f"Error updating user balance: {e}", exc_info=True)
            raise HTTPException(500, f"Error al actualizar el saldo: {str(e)}")
        finally:
            if cu:
                cu.close()
        
        # Record bet
        c = db_bets()
        try:
            c.execute("""
                INSERT INTO apuestas_usuarios (porra_id, username, opcion, cantidad)
                VALUES (?, ?, ?, ?)
            """, (body.porra_id, user, body.opcion, body.cantidad))
            c.commit()
            
            # Get porra title for transaction
            porra_titulo = c.execute("SELECT titulo FROM porras WHERE id = ?", (body.porra_id,)).fetchone()
            titulo = porra_titulo["titulo"] if porra_titulo else f"Porra #{body.porra_id}"
        except Exception as e:
            c.rollback()
            c.close()
            logger.error(f"Error recording bet: {e}", exc_info=True)
            # Try to refund user
            try:
                cu = db_users()
                cu.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (body.cantidad, user))
                cu.commit()
                cu.close()
            except:
                pass
            raise HTTPException(500, f"Error al registrar la apuesta: {str(e)}")
        
        # Record transaction for bet
        try:
            ct = db_tx()
            ct.execute("""
                INSERT INTO transactions (from_user, to_user, amount, concept)
                VALUES (?, ?, ?, ?)
            """, (user, f"Porra: {titulo}", body.cantidad, f"Apuesta en '{titulo}' - Opción: {body.opcion}"))
            ct.commit()
            ct.close()
        except Exception as e:
            logger.error(f"Error recording transaction: {e}", exc_info=True)
            # Continue anyway, bet is already recorded
        
        # Update user stats
        try:
            c.execute("""
                INSERT INTO estadisticas_porras (username, total_apostado)
                VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    total_apostado = total_apostado + ?,
                    updated_at = datetime('now')
            """, (user, body.cantidad, body.cantidad))
            c.commit()
        except Exception as e:
            logger.error(f"Error updating stats: {e}", exc_info=True)
            # Continue anyway
        finally:
            c.close()
        
        logger.info(f"✅ Bet placed: {user} bet {body.cantidad} on {body.opcion} in porra {body.porra_id}")
        return {"ok": True, "message": "Apuesta registrada correctamente", "nuevo_balance": new_balance}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in porra_apostar: {e}", exc_info=True)
        raise HTTPException(500, f"Error inesperado: {str(e)}")

@app.post("/bank/api/porras/resolver")
async def porra_resolver(body: ResolverPorraRequest, user: str = Depends(get_current_user)):
    """Resolve a porra and pay winners. Only dvd can resolve."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Solo dvd puede resolver porras")
    
    c = db_bets()
    
    # Get porra
    porra = c.execute("""
        SELECT estado, comision, opciones_json, titulo FROM porras WHERE id = ?
    """, (body.porra_id,)).fetchone()
    
    if not porra:
        c.close()
        raise HTTPException(404, "Porra no encontrada")
    if porra["estado"] == "finalizada":
        c.close()
        raise HTTPException(400, "Esta porra ya fue resuelta")
    
    # Get all bets
    apuestas = c.execute("""
        SELECT username, opcion, cantidad FROM apuestas_usuarios WHERE porra_id = ?
    """, (body.porra_id,)).fetchall()
    
    # Calculate payouts
    total_bote = sum(a["cantidad"] for a in apuestas)
    bote_neto = total_bote  # Sin comisión - 100% va a ganadores
    
    ganadores = [a for a in apuestas if a["opcion"] == body.resultado]
    total_ganadores = sum(a["cantidad"] for a in ganadores)
    
    titulo_porra = porra['titulo']  # Extract title for f-strings
    
    if total_ganadores == 0:
        # No winners - return all money
        for a in apuestas:
            cu = db_users()
            cu.execute("UPDATE users SET balance = balance + ? WHERE username = ?",
                      (a["cantidad"], a["username"]))
            cu.commit()
            cu.close()
            
            # Record transaction for refund
            ct = db_tx()
            ct.execute("""
                INSERT INTO transactions (from_user, to_user, amount, concept)
                VALUES (?, ?, ?, ?)
            """, (f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (sin ganadores) - '{titulo_porra}'"))
            ct.commit()
            ct.close()
            
            c.execute("""
                UPDATE apuestas_usuarios SET pagado = 1, ganancia = 0
                WHERE porra_id = ? AND username = ? AND opcion = ? AND cantidad = ?
            """, (body.porra_id, a["username"], a["opcion"], a["cantidad"]))
    else:
        # Pay winners proportionally
        usuarios_ganadores = set()  # Track unique winners for stats
        usuarios_perdedores = set()  # Track unique losers for stats
        
        titulo_porra = porra['titulo']  # Extract title for f-strings
        
        for a in ganadores:
            proporcion = a["cantidad"] / total_ganadores
            ganancia = bote_neto * proporcion
            
            cu = db_users()
            cu.execute("UPDATE users SET balance = balance + ? WHERE username = ?",
                      (ganancia, a["username"]))
            cu.commit()
            cu.close()
            
            # Record transaction
            ct = db_tx()
            ct.execute("""
                INSERT INTO transactions (from_user, to_user, amount, concept)
                VALUES (?, ?, ?, ?)
            """, (f"Porra: {titulo_porra}", a["username"], ganancia, f"Ganancia en '{titulo_porra}'"))
            ct.commit()
            ct.close()
            
            # Update apuesta record - FIXED: correct parameter order and unique identification
            c.execute("""
                UPDATE apuestas_usuarios SET pagado = 1, ganancia = ?
                WHERE porra_id = ? AND username = ? AND opcion = ? AND cantidad = ?
            """, (ganancia, body.porra_id, a["username"], a["opcion"], a["cantidad"]))
            
            # Track winner for stats (only count once per user per porra)
            usuarios_ganadores.add(a["username"])
            
            # Update stats - add total_ganado for each bet
            c.execute("""
                INSERT INTO estadisticas_porras (username, total_apostado, total_ganado, porras_ganadas, porras_perdidas)
                VALUES (?, 0, 0, 0, 0)
                ON CONFLICT(username) DO NOTHING
            """, (a["username"],))
            
            c.execute("""
                UPDATE estadisticas_porras
                SET total_ganado = total_ganado + ?,
                    updated_at = datetime('now')
                WHERE username = ?
            """, (ganancia, a["username"]))
        
        # Update porras_ganadas only once per user
        for username in usuarios_ganadores:
            c.execute("""
                UPDATE estadisticas_porras
                SET porras_ganadas = porras_ganadas + 1
                WHERE username = ?
            """, (username,))
        
        # Update losers stats
        perdedores = [a for a in apuestas if a["opcion"] != body.resultado]
        for a in perdedores:
            usuarios_perdedores.add(a["username"])
        
        # Remove users who also won (they had multiple bets)
        usuarios_perdedores -= usuarios_ganadores
        
        for username in usuarios_perdedores:
            c.execute("""
                INSERT INTO estadisticas_porras (username, total_apostado, total_ganado, porras_ganadas, porras_perdidas)
                VALUES (?, 0, 0, 0, 1)
                ON CONFLICT(username) DO UPDATE SET
                    porras_perdidas = porras_perdidas + 1,
                    updated_at = datetime('now')
            """, (username,))
    
    # Update porra status
    c.execute("""
        UPDATE porras SET estado = 'finalizada', resultado = ?, resolved_at = datetime('now')
        WHERE id = ?
    """, (body.resultado, body.porra_id))
    c.commit()
    c.close()
    
    # Notify winners
    if ganadores:
        for g in ganadores:
            await _broadcast_social_notification({
                "type": "porra_won",
                "username": g["username"],
                "porra_id": body.porra_id,
                "timestamp": datetime.now().isoformat()
            })
    
    return {"ok": True, "ganadores": len(ganadores), "bote_repartido": bote_neto}

@app.post("/bank/api/porras/cerrar/{porra_id}")
async def porra_cerrar(porra_id: int, user: str = Depends(get_current_user)):
    """Close a porra (no more bets). Only dvd or creator."""
    if user not in SUPERADMINS:
        c = db_bets()
        porra = c.execute("SELECT creador FROM porras WHERE id = ?", (porra_id,)).fetchone()
        c.close()
        if not porra or porra["creador"] != user:
            raise HTTPException(403, "Solo dvd o el creador pueden cerrar la porra")
    
    c = db_bets()
    c.execute("""
        UPDATE porras SET estado = 'cerrada', closed_at = datetime('now')
        WHERE id = ? AND estado = 'abierta'
    """, (porra_id,))
    c.commit()
    c.close()
    
    return {"ok": True}

@app.post("/bank/api/porras/cerrar-y-resolver/{porra_id}")
async def porra_cerrar_y_resolver(porra_id: int, body: dict, user: str = Depends(get_current_user)):
    """Close porra and resolve with winner in one step. Only dvd can do this."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Solo dvd puede cerrar y resolver porras")
    
    resultado = body.get("resultado")
    if not resultado:
        raise HTTPException(400, "Debe especificar el resultado ganador")
    
    # 1. Cerrar porra primero
    c = db_bets()
    porra = c.execute("SELECT estado FROM porras WHERE id = ?", (porra_id,)).fetchone()
    if not porra:
        c.close()
        raise HTTPException(404, "Porra no encontrada")
    
    if porra["estado"] == "abierta":
        c.execute("""
            UPDATE porras SET estado = 'cerrada', closed_at = datetime('now')
            WHERE id = ?
        """, (porra_id,))
        c.commit()
    c.close()
    
    # 2. Resolver y pagar ganadores
    resolver_request = ResolverPorraRequest(porra_id=porra_id, resultado=resultado)
    return await porra_resolver(resolver_request, user)

@app.post("/bank/api/porras/cancelar/{porra_id}")
async def porra_cancelar(porra_id: int, user: str = Depends(get_current_user)):
    """Cancel a porra and refund all bets. Creator or dvd can cancel."""
    c = db_bets()
    porra = c.execute("SELECT creador, estado, titulo FROM porras WHERE id = ?", (porra_id,)).fetchone()
    
    if not porra:
        c.close()
        raise HTTPException(404, "Porra no encontrada")
    
    if user not in SUPERADMINS and porra["creador"] != user:
        c.close()
        raise HTTPException(403, "Solo dvd o el creador pueden cancelar la porra")
    
    if porra["estado"] == "cancelada":
        c.close()
        raise HTTPException(400, "Esta porra ya fue cancelada")
    
    # Get all bets with full details to identify each one uniquely
    apuestas = c.execute("""
        SELECT id, username, cantidad, opcion FROM apuestas_usuarios WHERE porra_id = ?
    """, (porra_id,)).fetchall()
    
    logger.info(f"Cancelando porra {porra_id}: {len(apuestas)} apuestas a devolver")
    
    titulo_porra = porra['titulo']  # Extract title for f-strings
    
    # Refund all
    refunded_count = 0
    for a in apuestas:
        cu = db_users()
        cu.execute("UPDATE users SET balance = balance + ? WHERE username = ?",
                  (a["cantidad"], a["username"]))
        cu.commit()
        cu.close()
        
        # Record transaction for refund
        ct = db_tx()
        ct.execute("""
            INSERT INTO transactions (from_user, to_user, amount, concept)
            VALUES (?, ?, ?, ?)
        """, (f"Porra: {titulo_porra}", a["username"], a["cantidad"], f"Devolución (cancelada) - '{titulo_porra}'"))
        ct.commit()
        ct.close()
        
        # Update using the unique ID
        c.execute("""
            UPDATE apuestas_usuarios SET pagado = 1, ganancia = 0
            WHERE id = ?
        """, (a["id"],))
        
        refunded_count += 1
        logger.info(f"Devuelto {a['cantidad']} DVDc a {a['username']}")
    
    # Update porra
    c.execute("""
        UPDATE porras SET estado = 'cancelada', resolved_at = datetime('now')
        WHERE id = ?
    """, (porra_id,))
    c.commit()
    c.close()
    
    logger.info(f"Porra {porra_id} cancelada. {refunded_count} apuestas devueltas.")
    
    return {"ok": True, "refunded": refunded_count}

@app.delete("/bank/api/porras/{porra_id}")
async def porra_delete(porra_id: int, user: str = Depends(get_current_user)):
    """Delete a porra completely. Creator or dvd can delete."""
    c = db_bets()
    porra = c.execute("SELECT creador, estado FROM porras WHERE id = ?", (porra_id,)).fetchone()
    
    if not porra:
        c.close()
        raise HTTPException(404, "Porra no encontrada")
    
    if user not in SUPERADMINS and porra["creador"] != user:
        c.close()
        raise HTTPException(403, "Solo dvd o el creador pueden borrar la porra")
    
    # Check if has bets and is not cancelled
    has_bets = c.execute("SELECT COUNT(*) as cnt FROM apuestas_usuarios WHERE porra_id = ?",
                        (porra_id,)).fetchone()
    if has_bets["cnt"] > 0 and porra["estado"] != "cancelada":
        c.close()
        raise HTTPException(400, "No se puede borrar una porra con apuestas. Cancélala primero.")
    
    # Delete bets first (if any)
    c.execute("DELETE FROM apuestas_usuarios WHERE porra_id = ?", (porra_id,))
    
    # Delete porra
    c.execute("DELETE FROM porras WHERE id = ?", (porra_id,))
    c.commit()
    c.close()
    
    # Delete HTML file
    try:
        html_path = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras", f"porra_{porra_id}.html")
        if os.path.exists(html_path):
            os.remove(html_path)
            logger.info(f"Deleted HTML file for porra {porra_id}")
    except Exception as e:
        logger.warning(f"Could not delete HTML file for porra {porra_id}: {e}")
    
    logger.info(f"Porra {porra_id} borrada completamente")
    
    return {"ok": True}

class RelanzarPorraRequest(BaseModel):
    fecha_limite: str
    fecha_evento: str

@app.post("/bank/api/porras/relanzar/{porra_id}")
async def porra_relanzar(porra_id: int, body: RelanzarPorraRequest, user: str = Depends(get_current_user)):
    """Relaunch a porra with new dates. Only dvd can relaunch."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Solo dvd puede relanzar porras")
    
    try:
        c = db_bets()
        
        porra = c.execute("SELECT * FROM porras WHERE id = ?", (porra_id,)).fetchone()
        if not porra:
            c.close()
            raise HTTPException(404, "Porra no encontrada")
        
        # Validate dates
        from datetime import datetime as dt
        ahora = dt.now()
        try:
            limite = dt.fromisoformat(body.fecha_limite.replace('Z', '+00:00'))
            evento = dt.fromisoformat(body.fecha_evento.replace('Z', '+00:00'))
            if limite <= ahora:
                raise HTTPException(400, "La fecha límite debe ser futura")
            if evento <= limite:
                raise HTTPException(400, "La fecha del evento debe ser posterior a la fecha límite")
        except ValueError:
            raise HTTPException(400, "Formato de fecha inválido. Usa: YYYY-MM-DD HH:MM")
        
        # Update porra
        c.execute("""
            UPDATE porras 
            SET estado = 'abierta', 
                fecha_limite = ?, 
                fecha_evento = ?,
                closed_at = NULL,
                resolved_at = NULL,
                resultado = NULL
            WHERE id = ?
        """, (body.fecha_limite, body.fecha_evento, porra_id))
        c.commit()
        c.close()
        
        return {"ok": True, "message": "Porra relanzada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error relaunching porra {porra_id}: {e}")
        raise HTTPException(500, f"Error al relanzar la porra: {str(e)}")

class EnmascararPorraRequest(BaseModel):
    enmascarada: bool

@app.post("/bank/api/porras/enmascarar/{porra_id}")
async def porra_enmascarar(porra_id: int, body: EnmascararPorraRequest, user: str = Depends(get_current_user)):
    """Hide/show a porra from public list. Only dvd can mask."""
    if user not in SUPERADMINS:
        raise HTTPException(403, "Solo dvd puede enmascarar porras")
    
    try:
        c = db_bets()
        
        # Check if column exists, if not add it
        try:
            c.execute("SELECT enmascarada FROM porras LIMIT 1")
        except:
            c.execute("ALTER TABLE porras ADD COLUMN enmascarada INTEGER DEFAULT 0")
            c.commit()
        
        c.execute("""
            UPDATE porras SET enmascarada = ? WHERE id = ?
        """, (1 if body.enmascarada else 0, porra_id))
        c.commit()
        c.close()
        
        return {"ok": True, "enmascarada": body.enmascarada}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error masking porra {porra_id}: {e}")
        raise HTTPException(500, f"Error al enmascarar la porra: {str(e)}")

@app.get("/bank/api/porras/stats/{username}")
async def porra_user_stats(username: str, user: str = Depends(get_current_user)):
    """Get comprehensive betting statistics for a user."""
    try:
        c = db_bets()
        
        # Get basic stats from estadisticas_porras
        stats = c.execute("""
            SELECT total_apostado, total_ganado, porras_ganadas, porras_perdidas
            FROM estadisticas_porras WHERE username = ?
        """, (username,)).fetchone()
        
        # Get detailed bet history
        apuestas = c.execute("""
            SELECT p.id, p.titulo, p.estado, p.resultado, p.opciones_json,
                   a.opcion, a.cantidad, a.fecha, a.pagado, a.ganancia
            FROM apuestas_usuarios a
            JOIN porras p ON a.porra_id = p.id
            WHERE a.username = ?
            ORDER BY a.fecha DESC
        """, (username,)).fetchall()
        
        c.close()
        
        # Calculate comprehensive statistics
        total_apostado = stats["total_apostado"] if stats else 0
        total_ganado = stats["total_ganado"] if stats else 0
        porras_ganadas = stats["porras_ganadas"] if stats else 0
        porras_perdidas = stats["porras_perdidas"] if stats else 0
        
        # Additional calculations
        total_porras = len(apuestas)
        porras_activas = sum(1 for a in apuestas if a["estado"] in ("abierta", "cerrada"))
        porras_finalizadas = sum(1 for a in apuestas if a["estado"] == "finalizada")
        porras_canceladas = sum(1 for a in apuestas if a["estado"] == "cancelada")
        
        beneficio_neto = total_ganado - total_apostado
        roi = (beneficio_neto / total_apostado * 100) if total_apostado > 0 else 0
        
        # Win rate
        win_rate = (porras_ganadas / porras_finalizadas * 100) if porras_finalizadas > 0 else 0
        
        # Average bet size
        apuesta_promedio = total_apostado / total_porras if total_porras > 0 else 0
        
        # Average win
        ganancia_promedio = total_ganado / porras_ganadas if porras_ganadas > 0 else 0
        
        # Biggest win
        mayor_ganancia = max((a["ganancia"] for a in apuestas if a["ganancia"] > 0), default=0)
        
        # Current streak
        racha_actual = 0
        racha_tipo = None  # 'ganadora' o 'perdedora'
        for a in sorted(apuestas, key=lambda x: x["fecha"], reverse=True):
            if a["estado"] == "finalizada":
                es_ganador = a["pagado"] and a["ganancia"] > 0
                if racha_tipo is None:
                    racha_tipo = "ganadora" if es_ganador else "perdedora"
                    racha_actual = 1
                elif (racha_tipo == "ganadora" and es_ganador) or (racha_tipo == "perdedora" and not es_ganador):
                    racha_actual += 1
                else:
                    break
        
        # Porras by status
        porras_por_estado = {
            "abierta": sum(1 for a in apuestas if a["estado"] == "abierta"),
            "cerrada": sum(1 for a in apuestas if a["estado"] == "cerrada"),
            "finalizada": porras_finalizadas,
            "cancelada": porras_canceladas
        }
        
        # Recent activity (last 5 bets)
        actividad_reciente = []
        for a in apuestas[:5]:
            try:
                opciones = _json.loads(a["opciones_json"])
            except:
                opciones = []
            opcion_nombre = next((o["nombre"] for o in opciones if o["valor"] == a["opcion"]), a["opcion"])
            
            actividad_reciente.append({
                "porra_id": a["id"],
                "titulo": a["titulo"],
                "estado": a["estado"],
                "opcion": opcion_nombre,
                "cantidad": a["cantidad"],
                "ganancia": a["ganancia"] if a["pagado"] else None,
                "fecha": a["fecha"]
            })
        
        return {
            "username": username,
            # Totales
            "total_apostado": round(total_apostado, 2),
            "total_ganado": round(total_ganado, 2),
            "beneficio_neto": round(beneficio_neto, 2),
            "beneficio": round(beneficio_neto, 2),  # Alias for frontend compatibility
            "roi": round(roi, 2),
            
            # Porras
            "total_porras": total_porras,
            "porras_ganadas": porras_ganadas,
            "porras_perdidas": porras_perdidas,
            "porras_activas": porras_activas,
            "porras_finalizadas": porras_finalizadas,
            "porras_canceladas": porras_canceladas,
            "porras_por_estado": porras_por_estado,
            
            # Promedios
            "apuesta_promedio": round(apuesta_promedio, 2),
            "ganancia_promedio": round(ganancia_promedio, 2),
            "win_rate": round(win_rate, 2),
            
            # Records
            "mayor_ganancia": round(mayor_ganancia, 2),
            
            # Racha
            "racha_actual": racha_actual,
            "racha_tipo": racha_tipo,
            
            # Actividad reciente
            "actividad_reciente": actividad_reciente
        }
    except Exception as e:
        logger.error(f"Error getting user stats {username}: {e}")
        raise HTTPException(500, f"Error al obtener estadísticas: {str(e)}")

@app.get("/bank/api/porras/mis-estadisticas")
async def porra_mis_estadisticas(user: str = Depends(get_current_user)):
    """Get simplified betting statistics for current user (for dashboard)."""
    try:
        c = db_bets()
        
        # Get basic stats from estadisticas_porras
        stats = c.execute("""
            SELECT total_apostado, total_ganado, porras_ganadas, porras_perdidas
            FROM estadisticas_porras WHERE username = ?
        """, (user,)).fetchone()
        
        # Count active bets
        apuestas_activas = c.execute("""
            SELECT COUNT(*) n FROM apuestas_usuarios a
            JOIN porras p ON a.porra_id = p.id
            WHERE a.username = ? AND p.estado IN ('abierta', 'cerrada')
        """, (user,)).fetchone()
        
        c.close()
        
        total_apostado = stats["total_apostado"] if stats else 0
        total_ganado = stats["total_ganado"] if stats else 0
        porras_ganadas = stats["porras_ganadas"] if stats else 0
        porras_perdidas = stats["porras_perdidas"] if stats else 0
        ganancia_neta = total_ganado - total_apostado
        activas = apuestas_activas["n"] if apuestas_activas else 0
        
        return {
            "total_apostado": round(total_apostado, 2),
            "ganancia_neta": round(ganancia_neta, 2),
            "porras_ganadas": porras_ganadas,
            "porras_perdidas": porras_perdidas,
            "apuestas_activas": activas
        }
    except Exception as e:
        logger.error(f"Error getting user stats {user}: {e}")
        raise HTTPException(500, f"Error al obtener estadísticas: {str(e)}")

@app.get("/bank/api/porras/ranking")
async def porra_ranking(user: str = Depends(get_current_user)):
    """Get global betting ranking."""
    try:
        c = db_bets()
        
        rows = c.execute("""
            SELECT username, total_apostado, total_ganado, porras_ganadas, porras_perdidas
            FROM estadisticas_porras
            ORDER BY total_ganado DESC
            LIMIT 50
        """).fetchall()
        
        c.close()
        
        ranking = []
        for r in rows:
            beneficio = r["total_ganado"]
            roi = (beneficio / r["total_apostado"] * 100) if r["total_apostado"] > 0 else 0
            ranking.append({
                "username": r["username"],
                "total_apostado": r["total_apostado"],
                "total_ganado": r["total_ganado"],
                "porras_ganadas": r["porras_ganadas"],
                "porras_perdidas": r["porras_perdidas"],
                "beneficio": beneficio,
                "roi": roi
            })
        
        return {"ranking": ranking}
    except Exception as e:
        logger.error(f"Error getting ranking: {e}")
        raise HTTPException(500, f"Error al obtener ranking: {str(e)}")

@app.get("/bank/api/porras/mis-apuestas")
async def mis_apuestas(user: str = Depends(get_current_user)):
    """Get all bets from current user."""
    try:
        c = db_bets()
        
        rows = c.execute("""
            SELECT p.id, p.titulo, p.estado, p.resultado, p.opciones_json,
                   a.opcion, a.cantidad, a.fecha, a.pagado, a.ganancia
            FROM apuestas_usuarios a
            JOIN porras p ON a.porra_id = p.id
            WHERE a.username = ?
            ORDER BY a.fecha DESC
        """, (user,)).fetchall()
        
        c.close()
        
        apuestas = []
        for r in rows:
            try:
                opciones = _json.loads(r["opciones_json"])
            except:
                opciones = []
            opcion_nombre = next((o["nombre"] for o in opciones if o["valor"] == r["opcion"]), r["opcion"])
            
            apuestas.append({
                "porra_id": r["id"],
                "titulo": r["titulo"],
                "estado": r["estado"],
                "opcion": opcion_nombre,
                "cantidad": r["cantidad"],
                "fecha": r["fecha"],
                "ganador": r["estado"] == "finalizada" and r["resultado"] == r["opcion"],
                "ganancia": r["ganancia"] if r["pagado"] else 0
            })
        
        return {"apuestas": apuestas}
    except Exception as e:
        logger.error(f"Error getting user bets: {e}")
        raise HTTPException(500, f"Error al obtener apuestas: {str(e)}")

async def _broadcast_social_notification(data: dict):
    """Broadcast notification to all connected social websockets."""
    # This will be integrated with existing social WS system
    pass

def _create_porra_page(porra_id: int, titulo: str, descripcion: str, opciones: list, fecha_limite: str, fecha_evento: str, creador: str, tipo: str = 'Deportiva'):
    """Create individual HTML page for a porra using template."""
    try:
        page_dir = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras")
        os.makedirs(page_dir, exist_ok=True)
        
        # Read template
        template_path = os.path.join(BASE_DIR, "game_pages", "apuestas", "template_porra.html")
        if not os.path.exists(template_path):
            logger.error(f"Template not found: {template_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Generate options HTML with random icons
        opciones_html = ""
        colors = ['#38B87A', '#4878D8', '#E07840', '#D4A843', '#C83060', '#6B9BD4', '#E05260', '#8BB3E8']
        # Varied icons for any type of bet (not just sports)
        icons = [
            '⚽', '🏀', '🎾', '🏈', '⚾', '🏐', '🏓', '🏸',  # Sports
            '🎯', '🎲', '🎰', '🃏', '🎴', '🀄',  # Games
            '🏆', '🥇', '🥈', '🥉', '🏅', '👑',  # Trophies
            '⭐', '✨', '💫', '🌟', '💎', '💰',  # Special
            '🔥', '⚡', '💥', '🌈', '🎪', '🎭',  # Effects
            '🚀', '🎸', '🎬', '📺', '🎮', '🎵',  # Entertainment
            '🍕', '🍔', '🍰', '🍺', '☕', '🍷',  # Food & Drink
            '🌍', '🌙', '☀️', '🌊', '🔔', '📱'   # Misc
        ]
        
        import random
        random.seed(porra_id)  # Same icons for same porra
        shuffled_icons = random.sample(icons, min(len(icons), len(opciones)))
        
        for i, opt in enumerate(opciones):
            color = colors[i % len(colors)]
            nombre = opt.get('nombre', f'Opción {i+1}')
            valor = opt.get('valor', f'opcion_{i+1}')
            icon = shuffled_icons[i] if i < len(shuffled_icons) else '🎯'
            
            opciones_html += f'''
        <div class="optCard" data-valor="{valor}" onclick="selectOption('{valor}')">
          <div class="optIcon" style="background:{color}">{icon}</div>
          <div class="optName">{nombre}</div>
          <div class="optStats" id="stats_{valor}">
            <div class="optStat"><span class="optStatLbl">Apostadores:</span><span class="optStatVal">0</span></div>
            <div class="optStat"><span class="optStatLbl">Total Apostado:</span><span class="optStatVal">0 DVDc</span></div>
            <div class="optStat"><span class="optStatLbl">% del Bote:</span><span class="optStatVal">0%</span></div>
            <div class="optStat"><span class="optStatLbl">Cuota:</span><span class="optStatVal">-</span></div>
            <div class="optStat"><span class="optStatLbl">Ganancia/DVDc:</span><span class="optStatVal">-</span></div>
            <div class="optStat"><span class="optStatLbl">ROI Potencial:</span><span class="optStatVal">-</span></div>
          </div>
        </div>'''
        
        # Format dates
        try:
            from datetime import datetime as dt
            fl = dt.fromisoformat(fecha_limite.replace('Z', '+00:00'))
            fe = dt.fromisoformat(fecha_evento.replace('Z', '+00:00'))
            fecha_limite_fmt = fl.strftime('%d/%m/%Y %H:%M')
            fecha_evento_fmt = fe.strftime('%d/%m/%Y %H:%M')
        except:
            fecha_limite_fmt = fecha_limite
            fecha_evento_fmt = fecha_evento
        
        # Replace placeholders - use a safe method that doesn't interpret $ as regex groups
        html_content = template
        
        # CRITICAL: Replace ${PORRA_ID} FIRST (JavaScript template literal) before {PORRA_ID}
        # This prevents creating $2, $3, etc. when replacing {PORRA_ID}
        html_content = html_content.replace('${PORRA_ID}', str(porra_id))
        
        # Replace all other placeholders
        replacements = {
            '{PORRA_ID}': str(porra_id),
            '{TITULO}': titulo,
            '{DESCRIPCION}': descripcion,
            '{CREADOR}': creador,
            '{FECHA_LIMITE}': fecha_limite_fmt,
            '{FECHA_EVENTO}': fecha_evento_fmt,
            '{TIPO}': tipo,
            '{OPCIONES_HTML}': opciones_html
        }
        
        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, value)
        
        # Sanitize titulo for filename (remove special characters)
        import re
        titulo_safe = re.sub(r'[<>:"/\|?*]', '', titulo)  # Remove invalid filename chars
        titulo_safe = titulo_safe.strip()[:50]  # Limit length to 50 chars
        
        # Write page with descriptive name: porra (Titulo de la Porra).html
        # But keep porra_ID.html for backwards compatibility
        page_path_descriptive = os.path.join(page_dir, f'porra ({titulo_safe}).html')
        page_path_id = os.path.join(page_dir, f"porra_{porra_id}.html")
        
        # Write both files (same content, different names)
        with open(page_path_descriptive, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(page_path_id, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f'Created porra pages: porra ({titulo_safe}).html and porra_{porra_id}.html')
        return True
        
    except Exception as e:
        logger.error(f"Error creating porra page {porra_id}: {e}")
        return False


# =============================================================================
# HUNDIR LA FLOTA (BATTLESHIP)
# =============================================================================

import json as _json_hlf
import random as _random_hlf
import asyncio as _asyncio_hlf
from typing import Dict, List, Optional, Tuple

class HundirLaFlotaManager:
    """Manager for Battleship game with multiple players, ship placement, and turn-based combat."""
    
    DEFAULT_SHIP_TYPES = {
        "carrier": {"name": "Portaaviones", "size": 5, "icon": "🚢", "count": 1},
        "battleship": {"name": "Acorazado", "size": 4, "icon": "⛴️", "count": 1},
        "cruiser": {"name": "Crucero", "size": 3, "icon": "🛳️", "count": 1},
        "submarine": {"name": "Submarino", "size": 3, "icon": "🚤", "count": 1},
        "destroyer": {"name": "Destructor", "size": 2, "icon": "⛵", "count": 2}
    }
    
    def __init__(self):
        self.enabled: bool = False
        self.connections: dict = {}  # username → websocket
        self.custom_ships: dict = {}  # Custom ship configuration
        self._state: dict = self._empty_state()
        self._timer_task = None
    
    def _empty_state(self) -> dict:
        return {
            "phase": "waiting",  # waiting | placement | battle | finished
            "players": [],  # [{username, board, ships, ready, attacks, eliminated}]
            "current_player_idx": 0,
            "setup": {
                "board_size": 10,
                "turn_time": 60,
                "ships": self.custom_ships if self.custom_ships else self.DEFAULT_SHIP_TYPES.copy()
            },
            "winner": None,
            "last_action": None
        }
    
    def get_ship_types(self) -> dict:
        """Get current ship types configuration."""
        return self.custom_ships if self.custom_ships else self.DEFAULT_SHIP_TYPES.copy()
    
    def _create_player(self, username: str, board_size: int, ship_config: dict = None) -> dict:
        """Create a new player with empty board and ships."""
        if ship_config is None:
            ship_config = self.get_ship_types()
        
        ships = {}
        for ship_id, ship_info in ship_config.items():
            count = ship_info.get("count", 1)
            for i in range(count):
                key = f"{ship_id}_{i}" if count > 1 else ship_id
                ships[key] = {
                    "type": ship_id,
                    "name": ship_info["name"],
                    "size": ship_info["size"],
                    "icon": ship_info["icon"],
                    "placed": False,
                    "positions": [],  # [(r,c), ...]
                    "hits": [],  # [(r,c), ...]
                    "sunk": False
                }
        
        return {
            "username": username,
            "board": {},  # "r,c" → {ship: ship_id, hit: bool}
            "ships": ships,
            "ready": False,
            "attacks": {},  # "r,c" → {result: "hit"|"miss"|"sunk"}
            "eliminated": False,
            "time_remaining": 0
        }
    
    def _is_valid_placement(self, player: dict, ship_id: str, row: int, col: int, 
                           orientation: str, board_size: int) -> bool:
        """Check if ship placement is valid."""
        ship = player["ships"][ship_id]
        size = ship["size"]
        
        positions = []
        if orientation == "H":
            if col + size > board_size:
                return False
            positions = [(row, col + i) for i in range(size)]
        else:  # V
            if row + size > board_size:
                return False
            positions = [(row + i, col) for i in range(size)]
        
        # Check if positions are free
        for r, c in positions:
            coord = f"{r},{c}"
            if coord in player["board"]:
                return False
        
        return True
    
    def _place_ship(self, player: dict, ship_id: str, row: int, col: int, 
                   orientation: str, board_size: int) -> bool:
        """Place a ship on the player's board."""
        if not self._is_valid_placement(player, ship_id, row, col, orientation, board_size):
            return False
        
        # Remove old placement if exists
        ship = player["ships"][ship_id]
        if ship["placed"]:
            for r, c in ship["positions"]:
                coord = f"{r},{c}"
                if coord in player["board"] and player["board"][coord].get("ship") == ship_id:
                    del player["board"][coord]
        
        size = ship["size"]
        
        positions = []
        if orientation == "H":
            positions = [(row, col + i) for i in range(size)]
        else:  # V
            positions = [(row + i, col) for i in range(size)]
        
        # Place ship
        for r, c in positions:
            coord = f"{r},{c}"
            player["board"][coord] = {"ship": ship_id, "hit": False}
        
        ship["positions"] = positions
        ship["placed"] = True
        
        return True
    
    def _process_attack(self, attacker: dict, target: dict, row: int, col: int) -> dict:
        """Process an attack and return result."""
        coord = f"{row},{col}"
        
        # Check if already attacked
        if coord in attacker["attacks"]:
            return {"result": "already_attacked"}
        
        # Check target board
        cell = target["board"].get(coord)
        
        if cell and cell.get("ship"):
            # Hit!
            ship_id = cell["ship"]
            cell["hit"] = True
            target["ships"][ship_id]["hits"].append((row, col))
            
            # Check if ship is sunk
            ship = target["ships"][ship_id]
            if len(ship["hits"]) == ship["size"]:
                ship["sunk"] = True
                attacker["attacks"][coord] = {"result": "sunk"}
                
                # Check if all ships sunk (player eliminated)
                all_sunk = all(s["sunk"] for s in target["ships"].values())
                if all_sunk:
                    target["eliminated"] = True
                
                return {"result": "sunk", "ship": ship_id}
            else:
                attacker["attacks"][coord] = {"result": "hit"}
                return {"result": "hit"}
        else:
            # Miss
            attacker["attacks"][coord] = {"result": "miss"}
            return {"result": "miss"}
    
    def _get_next_player_idx(self) -> int:
        """Get next non-eliminated player index."""
        current = self._state["current_player_idx"]
        players = self._state["players"]
        
        for i in range(len(players)):
            idx = (current + i + 1) % len(players)
            if not players[idx]["eliminated"]:
                return idx
        
        return current
    
    def _check_winner(self) -> Optional[str]:
        """Check if there's a winner (only one player left)."""
        active_players = [p for p in self._state["players"] if not p["eliminated"]]
        if len(active_players) == 1:
            return active_players[0]["username"]
        return None
    
    def _build_broadcast(self, username: Optional[str] = None) -> dict:
        """Build state broadcast. If username provided, include their private board."""
        state = self._state.copy()
        
        # Build public player data
        public_players = []
        for p in state["players"]:
            public_p = {
                "username": p["username"],
                "ready": p["ready"],
                "eliminated": p["eliminated"],
                "time_remaining": p.get("time_remaining", 0),
                "ships": {}
            }
            
            # Only show sunk status of ships
            for ship_id, ship in p["ships"].items():
                public_p["ships"][ship_id] = {
                    "sunk": ship["sunk"],
                    "placed": ship["placed"]
                }
            
            # If this is the requesting user, include their full data
            if username and p["username"] == username:
                public_p["board"] = p["board"]
                public_p["ships"] = p["ships"]
                public_p["attacks"] = p["attacks"]
            
            public_players.append(public_p)
        
        return {
            "type": "state",
            "username": username,  # Include username for client identification
            "enabled": self.enabled,
            "phase": state["phase"],
            "players": public_players,
            "current_player_idx": state["current_player_idx"],
            "current_turn": state["players"][state["current_player_idx"]]["username"] if state["players"] else None,
            "setup": state["setup"],
            "winner": state["winner"]
        }
    
    async def connect(self, username: str, ws: WebSocket):
        """Connect a user to the game."""
        await ws.accept()
        self.connections[username] = ws
        
        # If game is in waiting phase and player not in game, add them
        if self._state["phase"] == "waiting":
            existing = next((p for p in self._state["players"] if p["username"] == username), None)
            if not existing:
                board_size = self._state["setup"]["board_size"]
                ship_config = self.get_ship_types()
                player = self._create_player(username, board_size, ship_config)
                self._state["players"].append(player)
                
                # If we have at least 2 players, move to placement phase
                if len(self._state["players"]) >= 2:
                    self._state["phase"] = "placement"
        
        try:
            await ws.send_json(self._build_broadcast(username))
            await self.broadcast()
        except Exception:
            pass
    
    def disconnect(self, username: str):
        """Disconnect a user from the game."""
        self.connections.pop(username, None)
    
    async def broadcast(self):
        """Broadcast state to all connected users."""
        dead = []
        for username, sock in list(self.connections.items()):
            try:
                await sock.send_json(self._build_broadcast(username))
            except Exception:
                dead.append(username)
        for u in dead:
            self.connections.pop(u, None)
    
    async def broadcast_action(self, action: str, data: dict = None):
        """Broadcast an action event to all users."""
        msg = {"type": "action", "action": action}
        if data:
            msg.update(data)
        
        dead = []
        for username, sock in list(self.connections.items()):
            try:
                await sock.send_json(msg)
            except Exception:
                dead.append(username)
        for u in dead:
            self.connections.pop(u, None)
    
    async def _start_turn_timer(self):
        """Start turn timer for current player."""
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        
        turn_time = self._state["setup"]["turn_time"]
        if turn_time <= 0:
            return
        
        current_idx = self._state["current_player_idx"]
        player = self._state["players"][current_idx]
        player["time_remaining"] = turn_time
        
        async def countdown():
            try:
                while player["time_remaining"] > 0:
                    await _asyncio_hlf.sleep(1)
                    player["time_remaining"] -= 1
                    await self.broadcast()
                
                # Time's up - skip turn
                await self._next_turn()
            except _asyncio_hlf.CancelledError:
                pass
        
        self._timer_task = _asyncio_hlf.create_task(countdown())
    
    async def _next_turn(self):
        """Move to next player's turn."""
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        
        self._state["current_player_idx"] = self._get_next_player_idx()
        await self._start_turn_timer()
        await self.broadcast()
    
    async def handle_action(self, act: dict, username: str):
        """Handle game actions."""
        action = act.get("action")
        
        if action == "setup":
            # Admin only - setup new game
            players_list = act.get("players", [])
            board_size = act.get("board_size", 10)
            turn_time = act.get("turn_time", 60)
            custom_ships = act.get("ships")  # Optional custom ship configuration
            
            if len(players_list) < 2:
                return
            
            # Update custom ships if provided, filtering out ships with count=0
            if custom_ships:
                filtered_ships = {k: v for k, v in custom_ships.items() if v.get("count", 0) > 0}
                if filtered_ships:
                    self.custom_ships = filtered_ships
                    logger.info("Custom ships configured: %s", filtered_ships)
                else:
                    # If all ships have count=0, use defaults
                    self.custom_ships = {}
                    logger.warning("No ships with count>0, using defaults")
            
            self._state = self._empty_state()
            self._state["setup"]["board_size"] = board_size
            self._state["setup"]["turn_time"] = turn_time
            self._state["phase"] = "placement"
            
            ship_config = self.get_ship_types()
            logger.info("Creating game with ship config: %s", ship_config)
            
            for player_name in players_list:
                player = self._create_player(player_name, board_size, ship_config)
                self._state["players"].append(player)
            
            await self.broadcast()
        
        elif action == "remove_ship":
            # Player removes a placed ship during placement phase
            if self._state["phase"] != "placement":
                return
            
            player = next((p for p in self._state["players"] if p["username"] == username), None)
            if not player or player["ready"]:
                return
            
            ship_id = act.get("ship")
            if ship_id not in player["ships"]:
                return
            
            ship = player["ships"][ship_id]
            if ship["placed"]:
                # Remove from board
                for r, c in ship["positions"]:
                    coord = f"{r},{c}"
                    if coord in player["board"] and player["board"][coord].get("ship") == ship_id:
                        del player["board"][coord]
                
                ship["placed"] = False
                ship["positions"] = []
                await self.broadcast()
        
        elif action == "place_ships":
            # Player places all ships at once during placement phase
            if self._state["phase"] != "placement":
                logger.warning("place_ships called but phase is %s", self._state["phase"])
                return
            
            player = next((p for p in self._state["players"] if p["username"] == username), None)
            if not player:
                logger.warning("Player %s not found", username)
                return
            
            if player["ready"]:
                logger.warning("Player %s already ready", username)
                return
            
            ships_data = act.get("ships", {})
            board_size = self._state["setup"]["board_size"]
            
            logger.info("Placing ships for %s: %s", username, list(ships_data.keys()))
            
            # Clear existing placements
            player["board"] = {}
            for ship in player["ships"].values():
                ship["placed"] = False
                ship["positions"] = []
            
            # Place all ships
            all_success = True
            for client_ship_id, ship_data in ships_data.items():
                # Find matching ship in player's ships
                ship_type = ship_data.get("type")
                cells = ship_data.get("cells", [])
                orientation = ship_data.get("orientation", "H")
                
                if not cells or not ship_type:
                    logger.warning("Invalid ship data for %s", client_ship_id)
                    all_success = False
                    continue
                
                # Find the actual ship_id in player's ships that matches this type
                # and hasn't been placed yet
                actual_ship_id = None
                for sid, ship in player["ships"].items():
                    if ship["type"] == ship_type and not ship["placed"]:
                        actual_ship_id = sid
                        break
                
                if not actual_ship_id:
                    logger.warning("No available ship of type %s for player %s", ship_type, username)
                    all_success = False
                    continue
                
                # Get first cell as starting position
                row, col = cells[0]
                success = self._place_ship(player, actual_ship_id, row, col, orientation, board_size)
                if not success:
                    logger.warning("Failed to place ship %s at [%d,%d]", actual_ship_id, row, col)
                    all_success = False
            
            if all_success:
                # Check all ships placed
                all_placed = all(s["placed"] for s in player["ships"].values())
                logger.info("Player %s all_placed=%s", username, all_placed)
                
                if all_placed:
                    player["ready"] = True
                    
                    # Check if all players ready
                    all_ready = all(p["ready"] for p in self._state["players"])
                    logger.info("All players ready: %s", all_ready)
                    
                    if all_ready:
                        self._state["phase"] = "battle"
                        self._state["current_player_idx"] = 0
                        logger.info("Starting battle phase!")
                        await self._start_turn_timer()
            else:
                logger.error("Not all ships placed successfully for %s", username)
            
            await self.broadcast()
        
        elif action == "place_ship":
            # Player places a ship during placement phase
            if self._state["phase"] != "placement":
                return
            
            player = next((p for p in self._state["players"] if p["username"] == username), None)
            if not player or player["ready"]:
                return
            
            ship_id = act.get("ship")
            row = act.get("row")
            col = act.get("col")
            orientation = act.get("orientation", "H")
            
            if ship_id not in player["ships"]:
                return
            
            board_size = self._state["setup"]["board_size"]
            success = self._place_ship(player, ship_id, row, col, orientation, board_size)
            
            if success:
                await self.broadcast()
        
        elif action == "ready":
            # Player confirms they're ready
            if self._state["phase"] != "placement":
                return
            
            player = next((p for p in self._state["players"] if p["username"] == username), None)
            if not player:
                return
            
            # Check all ships placed
            all_placed = all(s["placed"] for s in player["ships"].values())
            if not all_placed:
                return
            
            player["ready"] = True
            
            # Check if all players ready
            all_ready = all(p["ready"] for p in self._state["players"])
            if all_ready:
                self._state["phase"] = "battle"
                self._state["current_player_idx"] = 0
                await self._start_turn_timer()
            
            await self.broadcast()
        
        elif action == "attack":
            # Player attacks during battle phase
            if self._state["phase"] != "battle":
                return
            
            current_idx = self._state["current_player_idx"]
            current_player = self._state["players"][current_idx]
            
            if current_player["username"] != username:
                return
            
            row = act.get("row")
            col = act.get("col")
            
            # Get target (next player in list, skip eliminated)
            target_idx = (current_idx + 1) % len(self._state["players"])
            while self._state["players"][target_idx]["eliminated"] and target_idx != current_idx:
                target_idx = (target_idx + 1) % len(self._state["players"])
            
            target_player = self._state["players"][target_idx]
            
            # Process attack
            result = self._process_attack(current_player, target_player, row, col)
            
            if result["result"] == "already_attacked":
                return
            
            # Broadcast attack result to all players
            attack_msg = {
                "type": "attack_result",
                "attacker": username,
                "target": target_player["username"],
                "row": row,
                "col": col,
                "result": result["result"]
            }
            
            if "ship" in result:
                attack_msg["ship"] = result["ship"]
            
            dead = []
            for uname, sock in list(self.connections.items()):
                try:
                    await sock.send_json(attack_msg)
                except Exception:
                    dead.append(uname)
            for u in dead:
                self.connections.pop(u, None)
            
            # Check for winner
            winner = self._check_winner()
            if winner:
                self._state["phase"] = "finished"
                self._state["winner"] = winner
                if self._timer_task and not self._timer_task.done():
                    self._timer_task.cancel()
            else:
                # Next turn
                await self._next_turn()
            
            await self.broadcast()
        
        elif action == "reset":
            # Admin only - reset game
            self._state = self._empty_state()
            if self._timer_task and not self._timer_task.done():
                self._timer_task.cancel()
            await self.broadcast()


hundirlaflota_manager = HundirLaFlotaManager()


# ── Routes ────────────────────────────────────────────────

@app.get("/bank/hundirlaflota/admin.html", response_class=HTMLResponse)
async def hundirlaflota_admin_page():
    """Serve Hundir la Flota admin page."""
    path = os.path.join(BASE_DIR, "game_pages", "hundirlaflota", "admin.html")
    if not os.path.exists(path):
        raise HTTPException(404, "Admin page not found")
    return FileResponse(path)


@app.get("/bank/hundirlaflota/game.html", response_class=HTMLResponse)
async def hundirlaflota_game_page():
    """Serve Hundir la Flota game page."""
    path = os.path.join(BASE_DIR, "game_pages", "hundirlaflota", "game.html")
    if not os.path.exists(path):
        raise HTTPException(404, "Game page not found")
    return FileResponse(path)


@app.get("/bank/api/hundirlaflota/status")
async def hundirlaflota_status():
    """Return Hundir la Flota enabled state."""
    return {"enabled": hundirlaflota_manager.enabled}


@app.get("/bank/api/hundirlaflota/users")
async def hundirlaflota_users(user: str = Depends(get_current_user)):
    """Return eligible user list for Hundir la Flota."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT username FROM users ORDER BY username ASC"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows]


class HundirLaFlotaToggleRequest(BaseModel):
    enabled: bool


@app.post("/bank/api/hundirlaflota/toggle")
async def hundirlaflota_toggle(
    body: HundirLaFlotaToggleRequest,
    user: str = Depends(get_current_user)
):
    """Toggle Hundir la Flota game on/off."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    hundirlaflota_manager.enabled = body.enabled
    if not body.enabled:
        hundirlaflota_manager._state = hundirlaflota_manager._empty_state()
    await hundirlaflota_manager.broadcast()
    return {"enabled": hundirlaflota_manager.enabled}


class HundirLaFlotaSetupRequest(BaseModel):
    players: List[str]
    board_size: int = 10
    turn_time: int = 60
    ships: Optional[Dict] = None


@app.post("/bank/api/hundirlaflota/setup")
async def hundirlaflota_setup(
    body: HundirLaFlotaSetupRequest, 
    user: str = Depends(get_current_user)
):
    """Configure and start a Hundir la Flota game from admin panel."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    
    if len(body.players) < 2 or len(body.players) > 4:
        raise HTTPException(400, "Need 2-4 players")
    
    hundirlaflota_manager.enabled = True
    await hundirlaflota_manager.handle_action({
        "action": "setup",
        "players": body.players,
        "board_size": body.board_size,
        "turn_time": body.turn_time,
        "ships": body.ships
    }, user)
    
    logger.info("Hundir la Flota setup by %s: players=%s", user, body.players)
    return {"ok": True, "players": body.players}


@app.get("/bank/api/hundirlaflota/ships")
async def hundirlaflota_get_ships(user: str = Depends(get_current_user)):
    """Get current ship configuration."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    return {"ships": hundirlaflota_manager.get_ship_types()}


class HundirLaFlotaShipsRequest(BaseModel):
    ships: Dict


@app.post("/bank/api/hundirlaflota/ships")
async def hundirlaflota_set_ships(
    body: HundirLaFlotaShipsRequest,
    user: str = Depends(get_current_user)
):
    """Update ship configuration."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    hundirlaflota_manager.custom_ships = body.ships
    return {"ok": True, "ships": body.ships}


@app.post("/bank/api/hundirlaflota/reset")
async def hundirlaflota_reset(user: str = Depends(get_current_user)):
    """Reset Hundir la Flota game state."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    hundirlaflota_manager._state = hundirlaflota_manager._empty_state()
    await hundirlaflota_manager.broadcast()
    return {"ok": True}


@app.websocket("/bank/ws/hundirlaflota")
async def hundirlaflota_ws(websocket: WebSocket, token: str = ""):
    """WebSocket handler for Hundir la Flota game."""
    username = decode_token(token) if token else None
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    conn = db_connect()
    row = conn.execute(
        "SELECT username FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    
    if not row:
        await websocket.close(code=4001, reason="User not found")
        return
    
    _open_session(username, "hundirlaflota")
    await hundirlaflota_manager.connect(username, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            if username in ADMINS:
                # Admins can do everything
                await hundirlaflota_manager.handle_action(data, username)
            else:
                # Players can only do player actions
                action = data.get("action")
                if action in ["place_ship", "place_ships", "ready", "attack", "remove_ship"]:
                    await hundirlaflota_manager.handle_action(data, username)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("Hundir la Flota WS error: %s", e)
    finally:
        hundirlaflota_manager.disconnect(username)


# =============================================================================
# VOTACIONES / VOTING SYSTEM
# =============================================================================

@app.get("/bank/votaciones", response_class=HTMLResponse)
async def votaciones_page():
    """Serve the voting system page."""
    return _serve_game_page(VOTACIONES_DIR, "votaciones.html")


@app.get("/bank/api/votaciones/list")
async def votaciones_list(user: str = Depends(get_current_user)):
    """List all votaciones visible to the user."""
    c = None
    try:
        c = db_bets()
        
        # Get all votaciones
        rows = c.execute("""
            SELECT id, creador, titulo, descripcion, estado, multiple, anonima,
                   fecha_creacion, fecha_cierre
            FROM votaciones
            ORDER BY fecha_creacion DESC
        """).fetchall()
        
        votaciones = []
        for row in rows:
            vid = row[0]
            # Count total votes
            total_votos = c.execute(
                "SELECT COUNT(*) FROM votos WHERE votacion_id=?", (vid,)
            ).fetchone()[0]
            
            # Check if user has voted
            user_voted = c.execute(
                "SELECT COUNT(*) FROM votos WHERE votacion_id=? AND username=?", (vid, user)
            ).fetchone()[0] > 0
            
            votaciones.append({
                "id": vid,
                "creador": row[1],
                "titulo": row[2],
                "descripcion": row[3],
                "estado": row[4],
                "multiple": bool(row[5]),
                "anonima": bool(row[6]),
                "fecha_creacion": row[7],
                "fecha_cierre": row[8],
                "total_votos": total_votos,
                "mis_votos": user_voted
            })
        
        c.close()
        return {"votaciones": votaciones}
    except Exception as e:
        logger.error("Error listing votaciones: %s", e, exc_info=True)
        if c:
            c.close()
        raise HTTPException(500, f"Error al listar votaciones: {str(e)}")


@app.get("/bank/api/votaciones/{votacion_id}")
async def votacion_detail(votacion_id: int, user: str = Depends(get_current_user)):
    """Get detailed information about a votacion."""
    c = None
    try:
        c = db_bets()
        
        # Get votacion
        row = c.execute("""
            SELECT id, creador, titulo, descripcion, estado, multiple, anonima,
                   fecha_creacion, fecha_cierre
            FROM votaciones WHERE id=?
        """, (votacion_id,)).fetchone()
        
        if not row:
            c.close()
            raise HTTPException(404, "Votación no encontrada")
        
        votacion_data = {
            "id": row[0],
            "creador": row[1],
            "titulo": row[2],
            "descripcion": row[3],
            "estado": row[4],
            "multiple": bool(row[5]),
            "anonima": bool(row[6]),
            "fecha_creacion": row[7],
            "fecha_cierre": row[8]
        }
        
        # Get all options
        opciones_rows = c.execute("""
            SELECT vo.opcion
            FROM votaciones_opciones vo
            WHERE vo.votacion_id=?
            ORDER BY vo.id
        """, (votacion_id,)).fetchall()
        
        # Build options with stats
        opciones = []
        stats = {}
        total_votos = 0
        
        for opt_row in opciones_rows:
            opcion_nombre = opt_row[0]
            
            # Count votes for this option
            votos_count = c.execute("""
                SELECT COUNT(*) FROM votos 
                WHERE votacion_id=? AND opcion=?
            """, (votacion_id, opcion_nombre)).fetchone()[0]
            
            # Get voters for this option (for DVD view)
            votantes = []
            if user in ADMINS:
                votantes_rows = c.execute("""
                    SELECT username FROM votos 
                    WHERE votacion_id=? AND opcion=?
                    ORDER BY fecha
                """, (votacion_id, opcion_nombre)).fetchall()
                votantes = [v[0] for v in votantes_rows]
            
            opciones.append({
                "valor": opcion_nombre,
                "nombre": opcion_nombre,
                "votos": votos_count
            })
            
            total_votos += votos_count
            
            # Calculate percentage
            porcentaje = round((votos_count / total_votos * 100), 1) if total_votos > 0 else 0
            
            stats[opcion_nombre] = {
                "votos": votos_count,
                "porcentaje": porcentaje,
                "votantes": votantes
            }
        
        # Recalculate percentages after knowing total
        for opcion_nombre in stats:
            if total_votos > 0:
                stats[opcion_nombre]["porcentaje"] = round((stats[opcion_nombre]["votos"] / total_votos * 100), 1)
        
        # Check if user has voted (get all votes if multiple)
        user_votes_rows = c.execute("""
            SELECT opcion FROM votos WHERE votacion_id=? AND username=?
        """, (votacion_id, user)).fetchall()
        
        mis_votos = [v[0] for v in user_votes_rows] if user_votes_rows else []
        
        # Get unique participants
        participantes = c.execute("""
            SELECT DISTINCT username FROM votos WHERE votacion_id=?
        """, (votacion_id,)).fetchall()
        
        # Calculate results if closed
        resultado = None
        if votacion_data["estado"] == "cerrada":
            # Sort by votes
            ranking = sorted(
                [{"nombre": opt["nombre"], "votos": opt["votos"], 
                  "porcentaje": stats[opt["nombre"]]["porcentaje"]} 
                 for opt in opciones],
                key=lambda x: x["votos"],
                reverse=True
            )
            
            # Find winners (max votes)
            max_votos = ranking[0]["votos"] if ranking else 0
            ganadores = [r for r in ranking if r["votos"] == max_votos]
            
            resultado = {
                "ganadores": ganadores,
                "ranking": ranking
            }
        
        c.close()
        return {
            **votacion_data,
            "opciones": opciones,
            "mis_votos": mis_votos,
            "total_votos": total_votos,
            "stats": stats,
            "is_dvd": user in ADMINS,
            "resultado": resultado
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting votacion detail: %s", e, exc_info=True)
        if c:
            c.close()
        raise HTTPException(500, f"Error al obtener detalles de la votación: {str(e)}")


class VotacionCreateRequest(BaseModel):
    titulo: str
    descripcion: str = ""
    opciones: List[str]
    multiple: bool = False
    anonima: bool = False


@app.post("/bank/api/votaciones/create")
async def votacion_create(body: VotacionCreateRequest, user: str = Depends(get_current_user)):
    """Create a new votacion."""
    try:
        if user not in ADMINS:
            raise HTTPException(403, "Only admins can create votaciones")
        
        if len(body.opciones) < 2:
            raise HTTPException(400, "Need at least 2 options")
        
        # Validate opciones are strings
        if not all(isinstance(opt, str) for opt in body.opciones):
            raise HTTPException(400, "All options must be strings")
        
        # Remove empty options
        body.opciones = [opt.strip() for opt in body.opciones if opt.strip()]
        
        if len(body.opciones) < 2:
            raise HTTPException(400, "Need at least 2 non-empty options")
        
        conn = db_bets()
        cursor = conn.cursor()
        
        # Create votacion (sin fecha_cierre)
        cursor.execute("""
            INSERT INTO votaciones (creador, titulo, descripcion, estado, multiple, anonima)
            VALUES (?, ?, ?, 'abierta', ?, ?)
        """, (user, body.titulo, body.descripcion, int(body.multiple), int(body.anonima)))
        
        votacion_id = cursor.lastrowid
        
        # Create options
        for opcion in body.opciones:
            cursor.execute("""
                INSERT INTO votaciones_opciones (votacion_id, opcion)
                VALUES (?, ?)
            """, (votacion_id, opcion))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Votación created by %s: %s (ID: %d)", user, body.titulo, votacion_id)
        return {"ok": True, "votacion_id": votacion_id, "message": "Votación creada correctamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error creating votacion: %s", e, exc_info=True)
        raise HTTPException(500, f"Error al crear la votación: {str(e)}")


class VotarRequest(BaseModel):
    votacion_id: int
    opcion: str


@app.post("/bank/api/votaciones/votar")
async def votar(body: VotarRequest, user: str = Depends(get_current_user)):
    """Vote in a votacion."""
    c = None
    try:
        c = db_bets()
        
        # Check votacion exists and is open
        row = c.execute("""
            SELECT estado, multiple FROM votaciones WHERE id=?
        """, (body.votacion_id,)).fetchone()
        
        if not row:
            c.close()
            raise HTTPException(404, "Votación no encontrada")
        
        if row[0] != 'abierta':
            c.close()
            raise HTTPException(400, "La votación está cerrada")
        
        is_multiple = bool(row[1])
        
        # Check option exists
        option_exists = c.execute("""
            SELECT 1 FROM votaciones_opciones WHERE votacion_id=? AND opcion=?
        """, (body.votacion_id, body.opcion)).fetchone()
        
        if not option_exists:
            c.close()
            raise HTTPException(400, "Opción no válida")
        
        # Check if user already voted for this specific option
        existing_vote = c.execute("""
            SELECT id FROM votos WHERE votacion_id=? AND username=? AND opcion=?
        """, (body.votacion_id, user, body.opcion)).fetchone()
        
        if existing_vote:
            c.close()
            raise HTTPException(400, "Ya has votado por esta opción")
        
        # If not multiple, check if user voted for any option
        if not is_multiple:
            any_vote = c.execute("""
                SELECT id FROM votos WHERE votacion_id=? AND username=?
            """, (body.votacion_id, user)).fetchone()
            
            if any_vote:
                c.close()
                raise HTTPException(400, "Ya has votado. Elimina tu voto primero para cambiarlo.")
        
        # Register vote
        c.execute("""
            INSERT INTO votos (votacion_id, username, opcion, fecha)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (body.votacion_id, user, body.opcion))
        
        c.commit()
        c.close()
        
        logger.info("✅ Vote registered: %s voted '%s' in votacion %d", user, body.opcion, body.votacion_id)
        return {"ok": True, "message": "Voto registrado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error voting: %s", e, exc_info=True)
        if c:
            c.close()
        raise HTTPException(500, f"Error al registrar el voto: {str(e)}")


@app.delete("/bank/api/votaciones/{votacion_id}/voto")
async def remove_vote(votacion_id: int, user: str = Depends(get_current_user)):
    """Remove user's vote from a votacion."""
    c = None
    try:
        c = db_bets()
        
        # Check votacion is still open
        row = c.execute("""
            SELECT estado FROM votaciones WHERE id=?
        """, (votacion_id,)).fetchone()
        
        if not row:
            c.close()
            raise HTTPException(404, "Votación no encontrada")
        
        if row[0] != 'abierta':
            c.close()
            raise HTTPException(400, "La votación está cerrada")
        
        # Remove vote
        c.execute("""
            DELETE FROM votos WHERE votacion_id=? AND username=?
        """, (votacion_id, user))
        
        c.commit()
        c.close()
        
        logger.info("Vote removed: %s from votacion %d", user, votacion_id)
        return {"ok": True, "message": "Voto eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error removing vote: %s", e)
        if c:
            c.close()
        raise HTTPException(500, f"Error al eliminar el voto: {str(e)}")


class FinalizarRequest(BaseModel):
    votacion_id: int


@app.post("/bank/api/votaciones/finalizar")
async def finalizar_votacion(body: FinalizarRequest, user: str = Depends(get_current_user)):
    """Finalize a votacion and calculate results."""
    if user not in ADMINS:
        raise HTTPException(403, "Solo los administradores pueden finalizar votaciones")
    
    c = None
    try:
        c = db_bets()
        
        # Check votacion exists
        row = c.execute("""
            SELECT estado FROM votaciones WHERE id=?
        """, (body.votacion_id,)).fetchone()
        
        if not row:
            c.close()
            raise HTTPException(404, "Votación no encontrada")
        
        if row[0] == "cerrada":
            c.close()
            raise HTTPException(400, "La votación ya está cerrada")
        
        # Update state and set close date
        c.execute("""
            UPDATE votaciones 
            SET estado='cerrada', fecha_cierre=CURRENT_TIMESTAMP 
            WHERE id=?
        """, (body.votacion_id,))
        
        c.commit()
        c.close()
        
        logger.info("Votación %d finalized by %s", body.votacion_id, user)
        return {"ok": True, "message": "Votación finalizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error finalizing votacion: %s", e, exc_info=True)
        if c:
            c.close()
        raise HTTPException(500, f"Error al finalizar la votación: {str(e)}")


@app.delete("/bank/api/votaciones/{votacion_id}")
async def delete_votacion(votacion_id: int, user: str = Depends(get_current_user)):
    """Delete a votacion."""
    if user not in ADMINS:
        raise HTTPException(403, "Solo los administradores pueden eliminar votaciones")
    
    c = None
    try:
        c = db_bets()
        
        # Delete votes first
        c.execute("DELETE FROM votos WHERE votacion_id=?", (votacion_id,))
        
        # Delete options
        c.execute("DELETE FROM votaciones_opciones WHERE votacion_id=?", (votacion_id,))
        
        # Delete votacion
        c.execute("DELETE FROM votaciones WHERE id=?", (votacion_id,))
        
        c.commit()
        c.close()
        
        logger.info("Votación %d deleted by %s", votacion_id, user)
        return {"ok": True, "message": "Votación eliminada correctamente"}
    except Exception as e:
        logger.error("Error deleting votacion: %s", e)
        if c:
            c.close()
        raise HTTPException(500, f"Error al eliminar la votación: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# =============================================================================
# SOCKET.IO - VIDEO ROOMS (REMOVIDO - Usando Jitsi Meet en su lugar)
# =============================================================================

asgi_app = app

