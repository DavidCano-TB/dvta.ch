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
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
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

app = FastAPI(title="DVDcoin Exams", version="1.0.0")

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
    """Página principal - redirige a /exams"""
    return RedirectResponse(url="/exams")

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
    """Lista de oposiciones"""
    return FileResponse(os.path.join(OPO_DIR, "list.html"))

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

@app.get("/bank")
async def bank_redirect():
    """Redirige al sistema Bank"""
    return RedirectResponse(url="https://bank.dvta.ch")

@app.get("/bank/")
async def bank_redirect_slash():
    """Redirige al sistema Bank (con slash)"""
    return RedirectResponse(url="https://bank.dvta.ch")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DVDcoin Exams",
        "version": "1.0.0",
        "port": 8001
    }

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
