"""
DVDcoin Exams Module - Sistema de Exámenes y Oposiciones
Puerto: 8001
Dominio: dvta.ch
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Optional
import logging

# Añadir módulos compartidos al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from db_helper import DatabaseHelper, create_database
from jwt_helper import JWTHelper, load_or_create_secret
from email_service import EmailService, create_email_service
try:
    from utils import generate_token, hash_password, verify_password, validate_email
except ImportError:
    # Fallback si no se puede importar
    import secrets
    import re
    import bcrypt as _bcrypt
    
    def generate_token(length=32):
        return secrets.token_urlsafe(length)
    
    def hash_password(password):
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
    
    def verify_password(password, hashed):
        try:
            return _bcrypt.checkpw(password.encode(), hashed.encode())
        except:
            return False
    
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OPO_DIR = os.path.join(BASE_DIR, "opo")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Bases de datos
DB_USERS = os.path.join(DATA_DIR, "users_exams.db")
DB_EXAMS = os.path.join(DATA_DIR, "exams.db")
DB_OPO = os.path.join(DATA_DIR, "opo.db")

# Admins
ADMINS = {"dvd", "tata"}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exams")

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

app = FastAPI(title="DVDcoin Exams", version="1.0.0", redirect_slashes=False)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT
jwt_secret = load_or_create_secret(CONFIG_DIR, "jwt_secret_exams.txt")
jwt_helper = JWTHelper(jwt_secret, expire_hours=168)

# Email
email_service = create_email_service(os.path.join(CONFIG_DIR, "email.json"))

# Security
security = HTTPBearer(auto_error=False)

# =============================================================================
# SCHEMAS DE BASE DE DATOS
# =============================================================================

SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'free',
    verified INTEGER NOT NULL DEFAULT 0,
    verification_token TEXT,
    verification_expires TEXT,
    reset_token TEXT,
    reset_expires TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    verified_at TEXT,
    last_login TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_verification ON users(verification_token);
CREATE INDEX IF NOT EXISTS idx_users_reset ON users(reset_token);
"""

SCHEMA_EXAMS = """
CREATE TABLE IF NOT EXISTS exam_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    requires_premium INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    total_questions INTEGER NOT NULL DEFAULT 50,
    passing_score INTEGER NOT NULL DEFAULT 50,
    requires_premium INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES exam_categories(id)
);

CREATE TABLE IF NOT EXISTS exam_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    completed_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (exam_id) REFERENCES exams(id)
);

CREATE INDEX IF NOT EXISTS idx_results_user ON exam_results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_exam ON exam_results(exam_id);
"""

SCHEMA_OPO = """
CREATE TABLE IF NOT EXISTS opo_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS opo_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty TEXT NOT NULL DEFAULT 'medium',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES opo_categories(id)
);

CREATE TABLE IF NOT EXISTS opo_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    score INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    completed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_opo_questions_category ON opo_questions(category_id);
CREATE INDEX IF NOT EXISTS idx_opo_results_user ON opo_results(user_id);
"""

# =============================================================================
# INICIALIZACIÓN DE BASES DE DATOS
# =============================================================================

db_users = DatabaseHelper(DB_USERS)
db_exams = DatabaseHelper(DB_EXAMS)
db_opo = DatabaseHelper(DB_OPO)

db_users.create_tables(SCHEMA_USERS)
db_exams.create_tables(SCHEMA_EXAMS)
db_opo.create_tables(SCHEMA_OPO)

logger.info("Databases initialized")

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class NewPasswordRequest(BaseModel):
    token: str
    new_password: str

# =============================================================================
# DEPENDENCIAS
# =============================================================================

def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """Obtiene el usuario actual desde cookie o header"""
    token = request.cookies.get("exams_token")
    
    if not token and creds:
        token = creds.credentials
    
    if not token:
        raise HTTPException(401, "Authentication required")
    
    payload = jwt_helper.decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired session")
    
    username = payload.get("sub")
    user = db_users.fetchone("SELECT * FROM users WHERE username=?", (username,))
    
    if not user:
        raise HTTPException(401, "User not found")
    
    return user

def require_verified(user: dict = Depends(get_current_user)) -> dict:
    """Requiere que el usuario esté verificado"""
    if not user["verified"]:
        raise HTTPException(403, "Email verification required")
    return user

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Requiere que el usuario sea admin"""
    if user["username"] not in ADMINS:
        raise HTTPException(403, "Admin access required")
    return user

# =============================================================================
# RUTAS - AUTENTICACIÓN
# =============================================================================

@app.post("/api/auth/register")
async def register(data: RegisterRequest):
    """Registro de nuevo usuario"""
    # Validar email
    if not validate_email(data.email):
        raise HTTPException(400, "Invalid email format")
    
    # Verificar si ya existe
    existing = db_users.fetchone(
        "SELECT id FROM users WHERE email=? OR username=?",
        (data.email, data.username)
    )
    if existing:
        raise HTTPException(400, "Email or username already registered")
    
    # Hash password
    password_hash = hash_password(data.password)
    
    # Generar token de verificación
    verification_token = generate_token()
    verification_expires = (datetime.now() + timedelta(hours=24)).isoformat()
    
    # Insertar usuario
    user_id = db_users.insert("users", {
        "email": data.email,
        "username": data.username,
        "password_hash": password_hash,
        "role": "admin" if data.username in ADMINS else "free",
        "verification_token": verification_token,
        "verification_expires": verification_expires
    })
    
    # Enviar email de verificación
    verification_link = f"https://dvta.ch/verify?token={verification_token}"
    email_service.send_verification_email(data.email, data.username, verification_link)
    
    logger.info(f"User registered: {data.username}")
    
    return {
        "success": True,
        "message": "Registration successful. Please check your email to verify your account."
    }

@app.post("/api/auth/login")
async def login(data: LoginRequest, response: Response):
    """Login de usuario"""
    user = db_users.fetchone("SELECT * FROM users WHERE username=?", (data.username,))
    
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    
    # Actualizar último login
    db_users.update("users", {"last_login": datetime.now().isoformat()}, "id=?", (user["id"],))
    
    # Crear token
    token = jwt_helper.create_token(user["username"], {
        "role": user["role"],
        "verified": user["verified"]
    })
    
    # Setear cookie
    response.set_cookie(
        key="exams_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60  # 7 días
    )
    
    logger.info(f"User logged in: {data.username}")
    
    return {
        "success": True,
        "token": token,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "verified": bool(user["verified"])
        }
    }

@app.post("/api/auth/logout")
async def logout(response: Response):
    """Logout de usuario"""
    response.delete_cookie("exams_token")
    return {"success": True}

@app.post("/api/auth/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Verifica el email de un usuario"""
    user = db_users.fetchone(
        "SELECT * FROM users WHERE verification_token=?",
        (data.token,)
    )
    
    if not user:
        raise HTTPException(400, "Invalid verification token")
    
    # Verificar expiración
    if datetime.fromisoformat(user["verification_expires"]) < datetime.now():
        raise HTTPException(400, "Verification token expired")
    
    # Marcar como verificado
    db_users.update("users", {
        "verified": 1,
        "verified_at": datetime.now().isoformat(),
        "verification_token": None,
        "verification_expires": None
    }, "id=?", (user["id"],))
    
    logger.info(f"Email verified: {user['username']}")
    
    return {"success": True, "message": "Email verified successfully"}

# =============================================================================
# RUTAS - PÁGINAS HTML
# =============================================================================

@app.get("/")
async def root():
    """Hub principal — lista todos los módulos de la plataforma"""
    hub_path = os.path.join(STATIC_DIR, "hub.html")
    if os.path.exists(hub_path):
        return FileResponse(hub_path)
    # Fallback si el archivo no existe
    return RedirectResponse(url="/exams")

@app.get("/hub")
async def hub():
    """Alias explícito del hub principal"""
    hub_path = os.path.join(STATIC_DIR, "hub.html")
    if os.path.exists(hub_path):
        return FileResponse(hub_path)
    return RedirectResponse(url="/")

@app.get("/exams")
async def exams_index():
    """Página principal de exámenes"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/exams/")
async def exams_index_slash():
    """Página principal de exámenes (con slash)"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/opo")
async def opo_index():
    """Panel de gestión de tests OPO (sin login)"""
    return FileResponse(os.path.join(OPO_DIR, "panel.html"))

@app.get("/opo/list")
async def opo_list_old():
    """Lista de oposiciones (versión antigua)"""
    return FileResponse(os.path.join(OPO_DIR, "list.html"))

@app.get("/opo/panel")
async def opo_panel():
    """Panel OPO directo"""
    return FileResponse(os.path.join(OPO_DIR, "panel.html"))

@app.get("/opo/admin")
async def opo_admin(user: dict = Depends(require_admin)):
    """Panel de administración OPO"""
    return FileResponse(os.path.join(OPO_DIR, "admin.html"))

@app.get("/opo/exam-types")
async def opo_exam_types(user: dict = Depends(require_verified)):
    """Tipos de examen OPO"""
    return FileResponse(os.path.join(OPO_DIR, "exam-types.html"))

@app.get("/opo/exam")
async def opo_exam(user: dict = Depends(require_verified)):
    """Ejecución del examen OPO"""
    return FileResponse(os.path.join(OPO_DIR, "exam.html"))

@app.api_route(
    "/bank{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def bank_reverse_proxy(path: str, request: Request):
    Esto permite que dvta.ch/bank/* funcione exactamente igual que el Bank
    en bank.dvta.ch: mismo HTML (static/index.html), mismo login, mismas APIs.

    Intenta primero el servicio dedicado (puerto 8002) y, si no responde,
    cae al Bank principal en localhost:8000. Si ninguno responde, redirige
    a https://bank.dvta.ch para que el usuario nunca quede sin servicio.
    """
    import httpx
    target = f"/bank{path}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"

    # Forward headers (drop hop-by-hop).
    # Also drop Accept-Encoding so the upstream responds uncompressed —
    # httpx decompresses transparently but strips Content-Encoding from the
    # response headers, which causes the browser to receive gzip bytes without
    # knowing they are compressed (Content-Length mismatch → truncated HTML).
    HOP = {"host", "content-length", "connection", "keep-alive",
           "transfer-encoding", "upgrade", "te", "trailers",
           "accept-encoding"}  # ← force uncompressed upstream response
    fwd_headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP}

    body = await request.body() if request.method not in ("GET", "HEAD") else None

    last_error = None
    for upstream in ("http://localhost:8002", "http://localhost:8000"):
        try:
            async with httpx.AsyncClient(base_url=upstream, timeout=30.0,
                                         follow_redirects=False) as client:
                r = await client.request(
                    method=request.method,
                    url=target,
                    headers=fwd_headers,
                    content=body,
                )
            # Filter hop-by-hop headers from the response.
            # Also drop content-encoding/content-length: httpx already decoded
            # the body, so these headers would be wrong for the decoded content.
            RESP_HOP = {"transfer-encoding", "connection", "keep-alive",
                        "upgrade", "te", "trailers",
                        "content-encoding", "content-length"}
            resp_headers = {k: v for k, v in r.headers.items()
                            if k.lower() not in RESP_HOP}
            return Response(
                content=r.content,
                status_code=r.status_code,
                headers=resp_headers,
                media_type=r.headers.get("content-type"),
            )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            last_error = e
            logger.info(f"Bank proxy {upstream} not available: {e}, trying next")
            continue
        except Exception as e:
            logger.exception(f"Bank reverse proxy error on {upstream}: {e}")
            return JSONResponse(
                {"error": "proxy_error", "detail": str(e)},
                status_code=502,
            )

    # Both upstreams failed — fallback
    logger.warning(f"Bank proxy: both 8002 and 8000 down ({last_error}). "
                   f"Fallback to bank.dvta.ch")
    if request.method == "GET":
        return RedirectResponse(url=f"https://bank.dvta.ch{target}",
                                status_code=302)
    return JSONResponse(
        {"error": "bank_proxy_unavailable",
         "detail": "Servicio Bank no responde. Intenta en unos segundos."},
        status_code=503,
    )

# ── Games proxy (/games → localhost:8002) ─────────────────────────────────────

@app.api_route(
    "/games{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def games_reverse_proxy(path: str, request: Request):
    """Reverse proxy a /games{path} hacia el servicio Games (puerto 8002)."""
    import httpx
    target = f"/games{path}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"
    try:
        body = await request.body()
        async with httpx.AsyncClient(base_url="http://localhost:8002", timeout=15.0,
                                     follow_redirects=False) as client:
            r = await client.request(
                method=request.method,
                url=target,
                headers={k: v for k, v in request.headers.items()
                         if k.lower() not in ("host", "content-length")},
                content=body,
            )
            return Response(
                content=r.content,
                status_code=r.status_code,
                headers=dict(r.headers),
                media_type=r.headers.get("content-type"),
            )
    except (httpx.ConnectError, httpx.TimeoutException):
        if request.method == "GET":
            return RedirectResponse(url=f"https://games.dvta.ch{target}", status_code=302)
        return JSONResponse(
            {"error": "games_proxy_unavailable", "detail": "Servicio Games no responde."},
            status_code=503,
        )
    except Exception as e:
        logger.exception(f"Games reverse proxy error: {e}")
        return JSONResponse({"error": "proxy_error", "detail": str(e)}, status_code=502)


# ── Social proxy (/social → localhost:8003) ───────────────────────────────────

@app.api_route(
    "/social{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def social_reverse_proxy(path: str, request: Request):
    """Reverse proxy a /social{path} hacia el servicio Social (puerto 8003)."""
    import httpx
    target = f"/social{path}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"
    try:
        body = await request.body()
        async with httpx.AsyncClient(base_url="http://localhost:8003", timeout=15.0,
                                     follow_redirects=False) as client:
            r = await client.request(
                method=request.method,
                url=target,
                headers={k: v for k, v in request.headers.items()
                         if k.lower() not in ("host", "content-length")},
                content=body,
            )
            return Response(
                content=r.content,
                status_code=r.status_code,
                headers=dict(r.headers),
                media_type=r.headers.get("content-type"),
            )
    except (httpx.ConnectError, httpx.TimeoutException):
        if request.method == "GET":
            return RedirectResponse(url=f"https://social.dvta.ch{target}", status_code=302)
        return JSONResponse(
            {"error": "social_proxy_unavailable", "detail": "Servicio Social no responde."},
            status_code=503,
        )
    except Exception as e:
        logger.exception(f"Social reverse proxy error: {e}")
        return JSONResponse({"error": "proxy_error", "detail": str(e)}, status_code=502)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DVDcoin Exams",
        "version": "1.0.0",
        "port": 8001
    }

# =============================================================================
# RUTAS - API OPO
# =============================================================================

@app.get("/api/opo/questions/{category}")
async def get_opo_questions(
    category: str,
    count: int = 50,
    user: dict = Depends(require_verified)
):
    """Obtiene preguntas para un examen OPO"""
    import random
    
    # Buscar preguntas de la categoría
    questions = db_opo.fetchall(
        "SELECT * FROM opo_questions WHERE category_id IN (SELECT id FROM opo_categories WHERE slug=?) ORDER BY RANDOM() LIMIT ?",
        (category, count)
    )
    
    # Si no hay preguntas en BD, generar preguntas de ejemplo
    if not questions:
        logger.warning(f"No questions found for category {category}, generating samples")
        questions = []
        for i in range(count):
            questions.append({
                "id": i + 1,
                "question": f"Pregunta de ejemplo {i + 1} sobre {category}. ¿Cuál es la respuesta correcta?",
                "option_a": "Opción A - Primera respuesta posible",
                "option_b": "Opción B - Segunda respuesta posible",
                "option_c": "Opción C - Tercera respuesta posible",
                "option_d": "Opción D - Cuarta respuesta posible",
                "correct_answer": random.choice(['a', 'b', 'c', 'd']),
                "explanation": "Esta es una explicación de ejemplo de por qué esta respuesta es correcta."
            })
    
    # Formatear respuesta
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "id": q.get("id"),
            "question": q.get("question"),
            "options": {
                "a": q.get("option_a"),
                "b": q.get("option_b"),
                "c": q.get("option_c"),
                "d": q.get("option_d")
            },
            "correct": q.get("correct_answer"),
            "explanation": q.get("explanation", "")
        })
    
    return formatted_questions

@app.get("/api/opo/stats/{category}")
async def get_opo_stats(
    category: str,
    user: dict = Depends(require_verified)
):
    """Obtiene estadísticas del usuario para una categoría"""
    user_id = user["id"]
    
    # Obtener ID de categoría
    cat = db_opo.fetchone("SELECT id FROM opo_categories WHERE slug=?", (category,))
    if not cat:
        return {
            "total_exams": 0,
            "avg_score": 0,
            "best_score": 0,
            "total_time": 0
        }
    
    category_id = cat["id"]
    
    # Obtener estadísticas
    stats = db_opo.fetchone("""
        SELECT 
            COUNT(*) as total_exams,
            AVG(score) as avg_score,
            MAX(score) as best_score,
            SUM(duration_seconds) as total_time
        FROM opo_results
        WHERE user_id=? AND category_id=?
    """, (user_id, category_id))
    
    return {
        "total_exams": stats["total_exams"] or 0,
        "avg_score": round(stats["avg_score"] or 0),
        "best_score": stats["best_score"] or 0,
        "total_time": stats["total_time"] or 0
    }

class OpoResultRequest(BaseModel):
    category: str
    exam_type: str
    score: int
    correct: int
    wrong: int
    duration: int

@app.post("/api/opo/results")
async def save_opo_result(
    data: OpoResultRequest,
    user: dict = Depends(require_verified)
):
    """Guarda el resultado de un examen OPO"""
    user_id = user["id"]
    
    # Obtener o crear categoría
    cat = db_opo.fetchone("SELECT id FROM opo_categories WHERE slug=?", (data.category,))
    if not cat:
        # Crear categoría si no existe
        category_id = db_opo.insert("opo_categories", {
            "name": data.category.replace('-', ' ').title(),
            "slug": data.category
        })
    else:
        category_id = cat["id"]
    
    # Guardar resultado
    result_id = db_opo.insert("opo_results", {
        "user_id": user_id,
        "category_id": category_id,
        "exam_type": data.exam_type,
        "score": data.score,
        "correct": data.correct,
        "wrong": data.wrong,
        "duration_seconds": data.duration
    })
    
    logger.info(f"OPO result saved: user={user['username']}, category={data.category}, score={data.score}")
    
    return {"success": True, "result_id": result_id}

# Montar archivos estáticos ANTES de las rutas catch-all
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/opo/static", StaticFiles(directory=OPO_DIR), name="opo_static")

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("DVDcoin Exams starting...")
    logger.info(f"Port: 8001")
    logger.info(f"Access: http://localhost:8001")
    logger.info(f"External: https://dvta.ch")
    logger.info("=" * 80)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import sys
        sys.exit(1)
