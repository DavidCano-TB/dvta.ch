# =============================================================================
# DVDcoin Bank — Backend API v3.3
# =============================================================================
# Changes from v3.2:
#   - /api/gallery  : reads static/gallery/ folder directly (no config file)
#   - Daily cleanup : keeps last 1000 transactions, deletes oldest (runs at
#                     startup then every 24 h via asyncio background task)
#   - History cap   : user history and admin ledger both capped at 1000 rows
#   - Unblock       : clears is_blocked AND failed_attempts AND locked_until
#   - Index added   : idx_tx_date for faster ORDER BY on large history tables
# =============================================================================

import os
import asyncio
import sqlite3
import bcrypt as _bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# =============================================================================
# CONFIGURATION
# =============================================================================

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_H  = 8

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "data", "dvdcoin.db")
CONF_DIR    = os.path.join(BASE_DIR, "conf")
GALLERY_DIR = os.path.join(BASE_DIR, "static", "gallery")

# Image extensions served by /api/gallery
GALLERY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif"}

# Maximum transaction rows to keep in the database
TX_MAX_ROWS = 1000


def load_jwt_secret() -> str:
    """Load JWT secret from file; generate and persist if missing."""
    path = os.path.join(CONF_DIR, ".jwt_secret")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    import secrets
    s = secrets.token_hex(32)
    os.makedirs(CONF_DIR, exist_ok=True)
    with open(path, "w") as f:
        f.write(s)
    return s


JWT_SECRET = load_jwt_secret()

# Add new admins here (lowercase Clubhouse usernames).
# Admins can transfer any amount; their balance is always forced to 0.
ADMINS = {"dvd", "nina", "victor", "yu"}

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES     = 15

# In-memory heartbeat tracker: username → last ping timestamp (epoch seconds)
import time as _time
_ONLINE: dict = {}      # {username: float}
ONLINE_TIMEOUT_S = 90   # seconds without a ping → offline

limiter = Limiter(key_func=get_remote_address)
logger  = logging.getLogger("dvdcoin")

# =============================================================================
# PASSWORD HELPERS  (bcrypt used directly — avoids passlib 72-byte bug)
# =============================================================================

def hash_password(password: str) -> str:
    """Hash with bcrypt. Input is truncated to 72 bytes (bcrypt hard limit)."""
    pwd_bytes = password.encode("utf-8")[:72]
    return _bcrypt.hashpw(pwd_bytes, _bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password. Returns False for placeholder values."""
    if hashed in ("__UNSET__", "__AUTO__"):
        return False
    try:
        return _bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False

# =============================================================================
# DATABASE
# =============================================================================

def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def db_init() -> None:
    """Create tables and indexes on first run. Safe to call on every restart."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = db_connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username        TEXT PRIMARY KEY,
            password_hash   TEXT    NOT NULL DEFAULT '__UNSET__',
            balance         REAL    NOT NULL DEFAULT 0.0,
            is_blocked      INTEGER NOT NULL DEFAULT 0,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until    TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user   TEXT    NOT NULL,
            to_user     TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            concept     TEXT    NOT NULL DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_user)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_to   ON transactions(to_user)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(created_at)")
    conn.commit()
    conn.close()


def seed_admins() -> None:
    """Pre-create admin rows so they appear in listings before self-registering."""
    conn = db_connect()
    for u in ADMINS:
        conn.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (u,))
    for u in ADMINS:
        conn.execute("UPDATE users SET balance=0.0 WHERE username=?", (u,))
    conn.commit()
    conn.close()


def zero_admin_balances(conn: sqlite3.Connection) -> None:
    """Force all admin balances to 0. Called after every transfer."""
    for u in ADMINS:
        conn.execute("UPDATE users SET balance=0.0 WHERE username=?", (u,))

# =============================================================================
# BACKGROUND TASK — daily transaction cleanup
# =============================================================================

async def cleanup_old_transactions() -> None:
    """
    Runs immediately at startup, then every 24 hours.
    Deletes the oldest rows so only the last TX_MAX_ROWS remain.
    """
    while True:
        try:
            conn = db_connect()
            deleted = conn.execute("""
                DELETE FROM transactions
                WHERE id NOT IN (
                    SELECT id FROM transactions
                    ORDER BY created_at DESC
                    LIMIT ?
                )
            """, (TX_MAX_ROWS,)).rowcount
            conn.commit()
            conn.close()
            if deleted > 0:
                logger.info("Transaction cleanup: removed %d old rows", deleted)
            else:
                logger.info("Transaction cleanup: nothing to remove")
        except Exception as e:
            logger.error("Transaction cleanup error: %s", e)
        await asyncio.sleep(86400)  # 24 hours

# =============================================================================
# APP LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DVDcoin Bank v3.3 starting...")
    db_init()
    seed_admins()
    asyncio.create_task(cleanup_old_transactions())
    logger.info("Ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(title="DVDcoin Bank", version="3.3", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def skip_ngrok_warning(request: Request, call_next):
    """Add header so ngrok skips the browser warning page.
    Guard against WebSocket upgrades and streaming responses that have no mutable headers."""
    response = await call_next(request)
    try:
        response.headers["ngrok-skip-browser-warning"] = "1"
    except Exception:
        pass  # WebSocket upgrades and some streaming responses don't support header mutation
    return response
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBearer()

# =============================================================================
# JWT HELPERS
# =============================================================================

def create_token(username: str) -> str:
    exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_H)
    return jwt.encode({"sub": username, "exp": exp}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]).get("sub")
    except JWTError:
        return None


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """FastAPI dependency: validate JWT and return username."""
    u = decode_token(creds.credentials)
    if not u:
        raise HTTPException(401, "Invalid or expired session")
    conn = db_connect()
    row  = conn.execute("SELECT is_blocked FROM users WHERE username=?", (u,)).fetchone()
    conn.close()
    if not row:           raise HTTPException(401, "User not found")
    if row["is_blocked"]: raise HTTPException(403, "Account blocked")
    return u

# =============================================================================
# BRUTE-FORCE PROTECTION
# =============================================================================

def check_lockout(username: str) -> None:
    conn = db_connect()
    row  = conn.execute("SELECT locked_until FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and row["locked_until"]:
        locked_until = datetime.fromisoformat(row["locked_until"])
        if datetime.utcnow() < locked_until:
            mins = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
            raise HTTPException(429, f"Too many attempts. Try again in ~{mins} minute(s).")


def record_failed_login(username: str) -> None:
    conn = db_connect()
    row  = conn.execute("SELECT failed_attempts FROM users WHERE username=?", (username,)).fetchone()
    if not row:
        conn.close()
        return
    n    = (row["failed_attempts"] or 0) + 1
    lock = (datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat() \
           if n >= MAX_FAILED_ATTEMPTS else None
    conn.execute(
        "UPDATE users SET failed_attempts=?, locked_until=? WHERE username=?",
        (n, lock, username)
    )
    conn.commit()
    conn.close()


def clear_failed_logins(username: str) -> None:
    conn = db_connect()
    conn.execute(
        "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()


def get_or_create_user(username: str, conn: sqlite3.Connection) -> bool:
    """Auto-create account if not exists. Returns True if just created."""
    if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        return False
    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, '__AUTO__')",
        (username,)
    )
    return True

# =============================================================================
# REQUEST MODELS
# =============================================================================

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TransferRequest(BaseModel):
    to_user: str
    amount:  float
    concept: str = ""

# =============================================================================
# ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    resp = FileResponse("static/index.html")
    resp.headers["ngrok-skip-browser-warning"] = "1"
    return resp


@app.get("/api/health")
async def health():
    """Health check — used by the watchdog script."""
    conn  = db_connect()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    txs   = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    return {
        "status":       "ok",
        "version":      "3.3",
        "users":        users,
        "transactions": txs,
        "timestamp":    datetime.utcnow().isoformat()
    }


@app.post("/api/ping")
async def ping(user: str = Depends(get_current_user)):
    """Heartbeat: client calls every 30 s to register as online."""
    _ONLINE[user] = _time.time()
    return {"ok": True}


@app.get("/api/admin/connected")
async def admin_connected(user: str = Depends(get_current_user)):
    """List usernames that pinged within ONLINE_TIMEOUT_S seconds."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    now = _time.time()
    online = [u for u, ts in list(_ONLINE.items()) if now - ts < ONLINE_TIMEOUT_S]
    return {"online": online}


@app.get("/api/gallery")
async def gallery_images():
    """
    Return a sorted list of image files found in static/gallery/.
    No config file or index.json needed — reads the directory directly.
    Response: [{file: "1.jpg", url: "/static/gallery/1.jpg"}, ...]
    """
    if not os.path.exists(GALLERY_DIR):
        return []
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


# ── REGISTER ──────────────────────────────────────────────────────────────────

@app.post("/api/register")
@limiter.limit("10/minute")
async def register(request: Request, body: RegisterRequest):
    """Register a new account, or activate a pre-created / auto-created one."""
    u = body.username.strip().lower()
    if not (2 <= len(u) <= 30):
        raise HTTPException(400, "Username must be 2–30 characters")
    if len(body.password) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")

    conn = db_connect()
    row  = conn.execute("SELECT password_hash FROM users WHERE username=?", (u,)).fetchone()

    if row:
        if row["password_hash"] not in ("__UNSET__", "__AUTO__"):
            conn.close()
            raise HTTPException(409, "Username already registered")
        conn.execute(
            "UPDATE users SET password_hash=? WHERE username=?",
            (hash_password(body.password), u)
        )
    else:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (u, hash_password(body.password))
        )

    zero_admin_balances(conn)
    conn.commit()
    conn.close()
    logger.info("Registered: %s", u)
    return {"token": create_token(u), "username": u}


# ── LOGIN ──────────────────────────────────────────────────────────────────────

@app.post("/api/login")
@limiter.limit("20/minute")
async def login(request: Request, body: LoginRequest):
    """Authenticate and return a JWT token."""
    u = body.username.strip().lower()
    check_lockout(u)

    conn = db_connect()
    row  = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(401, "Invalid username or password")
    if row["is_blocked"]:
        raise HTTPException(403, "Account blocked. Contact an admin.")
    if not verify_password(body.password, row["password_hash"]):
        record_failed_login(u)
        raise HTTPException(401, "Invalid username or password")

    clear_failed_logins(u)
    logger.info("Login: %s", u)
    return {
        "token":    create_token(u),
        "username": u,
        "balance":  0.0 if u in ADMINS else row["balance"],
        "is_admin": u in ADMINS
    }


# ── ME ────────────────────────────────────────────────────────────────────────

@app.get("/api/me")
async def me(user: str = Depends(get_current_user)):
    conn = db_connect()
    row  = conn.execute(
        "SELECT username, balance, created_at FROM users WHERE username=?", (user,)
    ).fetchone()
    conn.close()
    return {
        "username":   row["username"],
        "balance":    0.0 if user in ADMINS else row["balance"],
        "created_at": row["created_at"],
        "is_admin":   user in ADMINS
    }


# ── USER LIST ─────────────────────────────────────────────────────────────────

@app.get("/api/users")
async def list_users(user: str = Depends(get_current_user)):
    """Alphabetical list of active users for the transfer dropdown."""
    conn = db_connect()
    rows = conn.execute(
        "SELECT username FROM users "
        "WHERE password_hash NOT IN ('__UNSET__','__AUTO__') "
        "ORDER BY username ASC"
    ).fetchall()
    conn.close()
    return [r["username"] for r in rows if r["username"] != user]


# ── TRANSFER ──────────────────────────────────────────────────────────────────

@app.post("/api/transfer")
@limiter.limit("30/minute")
async def transfer(
    request: Request,
    body: TransferRequest,
    user: str = Depends(get_current_user)
):
    """
    Transfer DVDcoins between users.
    - Regular users : balance is debited (must have sufficient funds)
    - Admins        : no balance check; their balance stays 0
    - Auto-creates recipient account if they don't exist yet
    """
    to_user = body.to_user.strip().lower()
    amount  = round(body.amount, 6)

    if to_user == user:         raise HTTPException(400, "Cannot transfer to yourself")
    if amount <= 0:             raise HTTPException(400, "Amount must be positive")
    if len(body.concept) > 200: raise HTTPException(400, "Reference max 200 characters")

    conn = db_connect()

    if user not in ADMINS:
        sender = conn.execute(
            "SELECT balance FROM users WHERE username=?", (user,)
        ).fetchone()
        if not sender:
            conn.close()
            raise HTTPException(404, "Sender not found")
        if sender["balance"] < amount:
            conn.close()
            raise HTTPException(
                400, f"Insufficient funds. Balance: {sender['balance']:.4f} DVDcoins"
            )

    was_created = get_or_create_user(to_user, conn)

    if user not in ADMINS:
        conn.execute(
            "UPDATE users SET balance = balance - ? WHERE username=?", (amount, user)
        )
    if to_user not in ADMINS:
        conn.execute(
            "UPDATE users SET balance = balance + ? WHERE username=?", (amount, to_user)
        )

    conn.execute(
        "INSERT INTO transactions (from_user, to_user, amount, concept) VALUES (?,?,?,?)",
        (user, to_user, amount, body.concept)
    )

    zero_admin_balances(conn)
    conn.commit()

    new_balance = 0.0 if user in ADMINS else \
        conn.execute(
            "SELECT balance FROM users WHERE username=?", (user,)
        ).fetchone()["balance"]
    conn.close()

    logger.info("Transfer %s -> %s: %.4f", user, to_user, amount)
    return {
        "success":      True,
        "message":      f"Sent {amount} DVDcoins to @{to_user}" +
                        (" (account auto-created)" if was_created else ""),
        "new_balance":  new_balance,
        "auto_created": was_created
    }


# ── HISTORY ───────────────────────────────────────────────────────────────────

@app.get("/api/history")
async def history(user: str = Depends(get_current_user), limit: int = 100):
    """
    Transaction history for the current user only (sent + received).
    Maximum returned: TX_MAX_ROWS (1000).
    """
    conn = db_connect()
    rows = conn.execute(
        "SELECT id, from_user, to_user, amount, concept, created_at "
        "FROM transactions "
        "WHERE from_user=? OR to_user=? "
        "ORDER BY created_at DESC LIMIT ?",
        (user, user, min(limit, TX_MAX_ROWS))
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── ADMIN: LIST USERS ─────────────────────────────────────────────────────────

@app.get("/api/admin/users")
async def admin_users(user: str = Depends(get_current_user)):
    """
    Return ALL user rows (including unregistered/auto-created accounts).
    Extra fields added per row:
      is_admin      — bool
      registered    — bool: False when password_hash is __UNSET__ or __AUTO__
      online        — bool: pinged within ONLINE_TIMEOUT_S seconds
    Sort: admins first, then by balance desc, then alphabetically.
    """
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT username, password_hash, balance, is_blocked, "
        "failed_attempts, locked_until, created_at "
        "FROM users ORDER BY username ASC"
    ).fetchall()
    conn.close()
    now = _time.time()
    result = []
    for r in rows:
        d = dict(r)
        d.pop("password_hash", None)          # never expose the hash
        is_adm = d["username"] in ADMINS
        d["is_admin"]   = is_adm
        d["registered"] = r["password_hash"] not in ("__UNSET__", "__AUTO__")
        last_ping = _ONLINE.get(d["username"], 0)
        d["online"]      = now - last_ping < ONLINE_TIMEOUT_S
        d["last_ping_at"] = last_ping if last_ping > 0 else None  # epoch seconds or None
        if is_adm:
            d["balance"] = 0.0
        result.append(d)
    # Sort: alphabetically, always
    result.sort(key=lambda x: x["username"].lower())
    return result


@app.get("/api/admin/ledger")
async def admin_ledger(user: str = Depends(get_current_user), limit: int = 1000):
    """All transactions, newest first. Maximum TX_MAX_ROWS (1000)."""
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    conn = db_connect()
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?",
        (min(limit, TX_MAX_ROWS),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/admin/block/{target}")
async def block(target: str, user: str = Depends(get_current_user)):
    if user != "dvd":
        raise HTTPException(403, "Only dvd can block users")
    conn = db_connect()
    conn.execute("UPDATE users SET is_blocked=1 WHERE username=?", (target,))
    conn.commit()
    conn.close()
    logger.info("Blocked %s by %s", target, user)
    return {"ok": True, "message": f"{target} blocked"}


@app.post("/api/admin/unblock/{target}")
async def unblock(target: str, user: str = Depends(get_current_user)):
    """
    Unblock a user.
    Clears: is_blocked flag, failed_attempts counter, locked_until timer.
    Works for both manually blocked users AND attempt-locked users.
    Only dvd can unblock.
    """
    if user != "dvd":
        raise HTTPException(403, "Only dvd can unblock users")
    conn = db_connect()
    conn.execute(
        "UPDATE users SET is_blocked=0, failed_attempts=0, locked_until=NULL WHERE username=?",
        (target,)
    )
    conn.commit()
    conn.close()
    logger.info("Unblocked %s by %s", target, user)
    return {"ok": True, "message": f"{target} unblocked and lockout cleared"}


@app.post("/api/admin/reset-pwd/{target}")
async def reset_pwd(target: str, user: str = Depends(get_current_user)):
    """Reset password to __UNSET__ so user can re-register. Balance preserved. Only dvd."""
    if user != "dvd":
        raise HTTPException(403, "Only dvd can reset passwords")
    conn = db_connect()
    conn.execute(
        "UPDATE users SET password_hash='__UNSET__' WHERE username=?", (target,)
    )
    conn.commit()
    conn.close()
    logger.info("Password reset for %s by %s", target, user)
    return {"ok": True, "message": f"Password reset for @{target}. They can now re-register."}


class DeleteUserRequest(BaseModel):
    dvd_password: str


@app.post("/api/admin/delete/{target}")
async def delete_user(target: str, body: DeleteUserRequest, user: str = Depends(get_current_user)):
    """Delete a user account. Only dvd can delete. Requires dvd's password as confirmation."""
    if user != "dvd":
        raise HTTPException(403, "Only dvd can delete accounts")
    if target in ADMINS:
        raise HTTPException(400, "Cannot delete admin accounts")
    # Verify dvd's password as confirmation
    conn = db_connect()
    dvd_row = conn.execute("SELECT password_hash FROM users WHERE username='dvd'").fetchone()
    if not dvd_row or not verify_password(body.dvd_password, dvd_row["password_hash"]):
        conn.close()
        raise HTTPException(403, "Incorrect dvd password")
    # Delete user and their transactions
    conn.execute("DELETE FROM users WHERE username=?", (target,))
    conn.execute("DELETE FROM transactions WHERE from_user=? OR to_user=?", (target, target))
    conn.commit()
    conn.close()
    logger.info("User %s deleted by %s", target, user)
    return {"ok": True, "message": f"@{target} deleted permanently"}



# =============================================================================
# PASAPALABRA GAME MODULE v5
# =============================================================================
import json as _json
import random

LETTERS_26       = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
PASAPALABRA_DIR  = os.path.join(BASE_DIR, "static", "pasapalabra")
DEFAULT_ROSCO_T  = 500


def load_question_pool() -> dict:
    path = os.path.join(PASAPALABRA_DIR, "preguntas.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        if isinstance(data, list):
            pool: dict = {}
            for q in data:
                l = q.get("letra", "").upper()
                if l:
                    pool.setdefault(l, []).append(q)
            return pool
        return {k.upper(): v for k, v in data.items()}
    except Exception as e:
        logger.error("Failed to load preguntas.json: %s", e)
        return {}


def assign_questions_for_players(pool: dict, n: int) -> list:
    per = [{} for _ in range(n)]
    for letter in LETTERS_26:
        opts = list(pool.get(letter, []))
        if not opts:
            for p in per:
                p[letter] = None
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
            # celebration: None | {type: "mid"|"final", winners: [username,...]}
            "celebration": None,
            # last_action: sent once per action so all clients react identically
            "last_action": None,
            "_action_seq": 0,
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


game_manager = PasapalabraManager()


# =============================================================================
# PASAPALABRA ROUTES
# =============================================================================

@app.get("/pasapalabra", response_class=HTMLResponse)
async def pasapalabra_page():
    return FileResponse(os.path.join(PASAPALABRA_DIR, "game.html"))

@app.get("/api/pasapalabra/status")
async def pasapalabra_status():
    return {"enabled": game_manager.enabled}

@app.get("/api/pasapalabra/users")
async def pasapalabra_users(user: str = Depends(get_current_user)):
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

@app.post("/api/pasapalabra/toggle")
async def pasapalabra_toggle(body: GameToggleRequest, user: str = Depends(get_current_user)):
    if user not in ADMINS:
        raise HTTPException(403, "Admins only")
    game_manager.enabled = body.enabled
    if not body.enabled:
        game_manager._stop_timer()
        game_manager._state = game_manager._empty_state()
    await game_manager.broadcast()
    logger.info("Pasapalabra %s by %s", "enabled" if body.enabled else "disabled", user)
    return {"enabled": game_manager.enabled}

@app.websocket("/ws/pasapalabra")
async def pasapalabra_ws(websocket: WebSocket, token: str = ""):
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
    await game_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if username in ADMINS:
                await game_manager.handle_action(data, username)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        game_manager.disconnect(username)


# =============================================================================
# MILLONARIO GAME MODULE
# =============================================================================
import json as _json_m
import random as _random_m

MILLONARIO_DIR = os.path.join(BASE_DIR, "static", "millonario")

PREMIOS = [
    "100 €","200 €","300 €","500 €","1.000 €",
    "2.000 €","4.000 €","8.000 €","16.000 €","32.000 €",
    "64.000 €","125.000 €","250.000 €","500.000 €","1.000.000 €"
]
GARANTIZADOS = {5: "1.000 €", 10: "32.000 €"}


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
    for lvl in range(1, 16):
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
            if nivel == 15:
                self._state["status"]        = "finished"
                self._state["ultimo_premio"] = "1.000.000 €"
            else:
                self._state["nivel"]      = nivel + 1
                self._state["eliminadas"] = []
                self._state["status"]     = "playing"
            self._state["selected_option"] = ""   # clear AFTER reveal
            self._state["reveal_result"]   = None
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

@app.get("/millonario", response_class=HTMLResponse)
async def millonario_page():
    return FileResponse(os.path.join(MILLONARIO_DIR, "game.html"))


@app.get("/api/millonario/status")
async def millonario_status():
    return {"enabled": millonario_manager.enabled}


@app.get("/api/millonario/users")
async def millonario_users(user: str = Depends(get_current_user)):
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


@app.post("/api/millonario/toggle")
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


@app.websocket("/ws/millonario")
async def millonario_ws(websocket: WebSocket, token: str = ""):
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
