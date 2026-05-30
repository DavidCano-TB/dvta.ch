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

# Root del proyecto (c:\dvdcoin)
PROJECT_ROOT = os.path.normpath(os.path.join(BASE_DIR, "..", ".."))
PORRAS_DIR = os.path.join(PROJECT_ROOT, "game_pages", "apuestas", "porras")

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
    subscription_status TEXT NOT NULL DEFAULT 'none',
    subscription_expires TEXT,
    subscription_plan TEXT,
    lang TEXT NOT NULL DEFAULT 'es',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    verified_at TEXT,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan TEXT NOT NULL DEFAULT 'monthly',
    status TEXT NOT NULL DEFAULT 'active',
    amount REAL NOT NULL DEFAULT 9.99,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    cancelled_at TEXT,
    payment_method TEXT,
    payment_ref TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_verification ON users(verification_token);
CREATE INDEX IF NOT EXISTS idx_users_reset ON users(reset_token);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
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

# Migraciones seguras — añadir columnas si no existen
_migration_cols = [
    ("users", "subscription_status", "TEXT NOT NULL DEFAULT 'none'"),
    ("users", "subscription_expires", "TEXT"),
    ("users", "subscription_plan", "TEXT"),
    ("users", "lang", "TEXT NOT NULL DEFAULT 'es'"),
]
for table, col, typedef in _migration_cols:
    try:
        db_users.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
    except Exception:
        pass  # column already exists

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
    
    # Insertar usuario (auto-verificado para acceso inmediato)
    user_id = db_users.insert("users", {
        "email": data.email,
        "username": data.username,
        "password_hash": password_hash,
        "role": "admin" if data.username in ADMINS else "free",
        "verified": 1,
        "verified_at": datetime.now().isoformat(),
        "verification_token": verification_token,
        "verification_expires": verification_expires
    })
    
    # Enviar email de verificación
    email_sent = False
    try:
        verification_link = f"https://dvta.ch/verify?token={verification_token}"
        email_sent = email_service.send_verification_email(data.email, data.username, verification_link)
        if not email_sent:
            logger.warning(f"Verification email NOT sent to {data.email} (returned False)")
    except Exception as e:
        logger.error(f"Failed to send verification email to {data.email}: {e}")
    
    logger.info(f"User registered: {data.username}, email_sent={email_sent}")
    
    return {
        "success": True,
        "email_sent": email_sent,
        "message": "Registration successful. Please check your email to verify your account."
    }

@app.post("/api/auth/login")
async def login(data: LoginRequest, response: Response):
    """Login de usuario (acepta username o email)"""
    # Buscar por username O por email
    user = db_users.fetchone("SELECT * FROM users WHERE username=? OR email=?", (data.username, data.username))
    
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


@app.get("/verify")
async def verify_email_link(token: str = ""):
    """Verificación de email por enlace (GET) — el usuario hace clic en el link del email"""
    if not token:
        raise HTTPException(400, "Missing verification token")
    
    user = db_users.fetchone(
        "SELECT * FROM users WHERE verification_token=?",
        (token,)
    )
    
    if not user:
        # Token inválido — redirigir a exams con error
        return RedirectResponse(url="/exams?verified=invalid")
    
    # Verificar expiración
    if datetime.fromisoformat(user["verification_expires"]) < datetime.now():
        return RedirectResponse(url="/exams?verified=expired")
    
    # Marcar como verificado
    db_users.update("users", {
        "verified": 1,
        "verified_at": datetime.now().isoformat(),
        "verification_token": None,
        "verification_expires": None
    }, "id=?", (user["id"],))
    
    logger.info(f"Email verified via link: {user['username']}")
    
    return RedirectResponse(url="/exams?verified=success")


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Devuelve info del usuario actual"""
    # Comprobar si la suscripción está activa
    sub = db_users.fetchone(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires_at DESC LIMIT 1",
        (user["id"],)
    )
    
    has_active_sub = False
    sub_info = None
    if sub:
        if datetime.fromisoformat(sub["expires_at"]) > datetime.now():
            has_active_sub = True
            sub_info = {
                "plan": sub["plan"],
                "expires_at": sub["expires_at"],
                "status": "active"
            }
        else:
            # Expirada — marcar como expirada
            db_users.update("subscriptions", {"status": "expired"}, "id=?", (sub["id"],))
            db_users.update("users", {"subscription_status": "expired"}, "id=?", (user["id"],))
    
    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "verified": bool(user["verified"]),
            "lang": user.get("lang", "es"),
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "subscription": sub_info,
            "has_premium": has_active_sub or user["role"] == "admin"
        }
    }


@app.post("/api/auth/resend-verification")
async def resend_verification(user: dict = Depends(get_current_user)):
    """Reenvía el email de verificación (usuario logueado)"""
    if user["verified"]:
        return {"success": True, "message": "Already verified"}
    
    # Generar nuevo token
    verification_token = generate_token()
    verification_expires = (datetime.now() + timedelta(hours=24)).isoformat()
    
    db_users.update("users", {
        "verification_token": verification_token,
        "verification_expires": verification_expires
    }, "id=?", (user["id"],))
    
    # Enviar email
    email_sent = False
    try:
        verification_link = f"https://dvta.ch/verify?token={verification_token}"
        email_sent = email_service.send_verification_email(user["email"], user["username"], verification_link)
    except Exception as e:
        logger.error(f"Resend verification failed: {e}")
    
    return {"success": True, "email_sent": email_sent, "message": "Verification email sent"}


class ResendByEmailRequest(BaseModel):
    email: EmailStr


@app.post("/api/auth/resend-verification-public")
async def resend_verification_public(data: ResendByEmailRequest):
    """Reenvía el email de verificación (sin login, por email)"""
    user = db_users.fetchone("SELECT * FROM users WHERE email=?", (data.email,))
    
    if not user:
        # No revelar si el email existe
        return {"success": True, "message": "If the email is registered, a verification link has been sent"}
    
    if user["verified"]:
        return {"success": True, "message": "Already verified"}
    
    # Generar nuevo token
    verification_token = generate_token()
    verification_expires = (datetime.now() + timedelta(hours=24)).isoformat()
    
    db_users.update("users", {
        "verification_token": verification_token,
        "verification_expires": verification_expires
    }, "id=?", (user["id"],))
    
    # Enviar email
    email_sent = False
    try:
        verification_link = f"https://dvta.ch/verify?token={verification_token}"
        email_sent = email_service.send_verification_email(user["email"], user["username"], verification_link)
        logger.info(f"Resend verification to {data.email}: sent={email_sent}")
    except Exception as e:
        logger.error(f"Resend verification public failed for {data.email}: {e}")
    
    return {"success": True, "email_sent": email_sent, "message": "If the email is registered, a verification link has been sent"}


@app.post("/api/auth/forgot-password")
async def forgot_password(data: ResetPasswordRequest):
    """Envía email de reset de contraseña"""
    user = db_users.fetchone("SELECT * FROM users WHERE email=?", (data.email,))
    
    # Siempre devolver éxito para no revelar si el email existe
    if not user:
        return {"success": True, "message": "If the email exists, a reset link has been sent"}
    
    reset_token = generate_token()
    reset_expires = (datetime.now() + timedelta(hours=2)).isoformat()
    
    db_users.update("users", {
        "reset_token": reset_token,
        "reset_expires": reset_expires
    }, "id=?", (user["id"],))
    
    reset_link = f"https://dvta.ch/exams?reset={reset_token}"
    email_service.send_password_reset_email(user["email"], user["username"], reset_link)
    
    return {"success": True, "message": "If the email exists, a reset link has been sent"}


@app.post("/api/auth/reset-password")
async def reset_password(data: NewPasswordRequest):
    """Resetea la contraseña con token"""
    user = db_users.fetchone("SELECT * FROM users WHERE reset_token=?", (data.token,))
    
    if not user:
        raise HTTPException(400, "Invalid reset token")
    
    if datetime.fromisoformat(user["reset_expires"]) < datetime.now():
        raise HTTPException(400, "Reset token expired")
    
    password_hash = hash_password(data.new_password)
    
    db_users.update("users", {
        "password_hash": password_hash,
        "reset_token": None,
        "reset_expires": None
    }, "id=?", (user["id"],))
    
    return {"success": True, "message": "Password updated successfully"}


@app.post("/api/auth/set-lang")
async def set_lang(request: Request, user: dict = Depends(get_current_user)):
    """Actualiza el idioma preferido del usuario"""
    body = await request.json()
    lang = body.get("lang", "es")
    valid_langs = ["es", "en", "fr", "it", "de", "eu", "ca"]
    if lang not in valid_langs:
        lang = "es"
    
    db_users.update("users", {"lang": lang}, "id=?", (user["id"],))
    return {"success": True, "lang": lang}


# =============================================================================
# RUTAS - SUSCRIPCIONES / PAGOS
# =============================================================================

PLANS = {
    "monthly": {"price": 9.99, "days": 30, "name": "Mensual"},
    "quarterly": {"price": 24.99, "days": 90, "name": "Trimestral"},
    "yearly": {"price": 79.99, "days": 365, "name": "Anual"},
}


@app.get("/api/subscription/plans")
async def get_plans():
    """Devuelve los planes disponibles"""
    return {"plans": PLANS}


@app.get("/api/subscription/status")
async def subscription_status(user: dict = Depends(get_current_user)):
    """Estado de la suscripción del usuario"""
    if user["role"] == "admin":
        return {
            "has_premium": True,
            "reason": "admin",
            "subscription": None
        }
    
    sub = db_users.fetchone(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires_at DESC LIMIT 1",
        (user["id"],)
    )
    
    if not sub:
        return {"has_premium": False, "subscription": None}
    
    if datetime.fromisoformat(sub["expires_at"]) < datetime.now():
        db_users.update("subscriptions", {"status": "expired"}, "id=?", (sub["id"],))
        db_users.update("users", {"subscription_status": "expired"}, "id=?", (user["id"],))
        return {"has_premium": False, "subscription": {"status": "expired", "expired_at": sub["expires_at"]}}
    
    return {
        "has_premium": True,
        "subscription": {
            "plan": sub["plan"],
            "status": "active",
            "started_at": sub["started_at"],
            "expires_at": sub["expires_at"],
            "amount": sub["amount"]
        }
    }


@app.post("/api/subscription/subscribe")
async def subscribe(request: Request, user: dict = Depends(require_verified)):
    """Crea una nueva suscripción (simulación de pago)"""
    body = await request.json()
    plan_key = body.get("plan", "monthly")
    
    if plan_key not in PLANS:
        raise HTTPException(400, "Invalid plan")
    
    plan = PLANS[plan_key]
    
    # Verificar si ya tiene suscripción activa
    existing = db_users.fetchone(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active'",
        (user["id"],)
    )
    if existing and datetime.fromisoformat(existing["expires_at"]) > datetime.now():
        raise HTTPException(400, "Already has active subscription")
    
    # Crear suscripción
    expires_at = (datetime.now() + timedelta(days=plan["days"])).isoformat()
    
    sub_id = db_users.insert("subscriptions", {
        "user_id": user["id"],
        "plan": plan_key,
        "status": "active",
        "amount": plan["price"],
        "expires_at": expires_at,
        "payment_method": body.get("payment_method", "card"),
        "payment_ref": generate_token(16)
    })
    
    # Actualizar usuario
    db_users.update("users", {
        "subscription_status": "active",
        "subscription_expires": expires_at,
        "subscription_plan": plan_key
    }, "id=?", (user["id"],))
    
    logger.info(f"Subscription created: user={user['username']}, plan={plan_key}")
    
    return {
        "success": True,
        "subscription": {
            "id": sub_id,
            "plan": plan_key,
            "amount": plan["price"],
            "expires_at": expires_at,
            "status": "active"
        }
    }


@app.post("/api/subscription/cancel")
async def cancel_subscription(user: dict = Depends(get_current_user)):
    """Cancela la suscripción activa"""
    sub = db_users.fetchone(
        "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires_at DESC LIMIT 1",
        (user["id"],)
    )
    
    if not sub:
        raise HTTPException(400, "No active subscription")
    
    db_users.update("subscriptions", {
        "status": "cancelled",
        "cancelled_at": datetime.now().isoformat()
    }, "id=?", (sub["id"],))
    
    db_users.update("users", {"subscription_status": "cancelled"}, "id=?", (user["id"],))
    
    return {"success": True, "message": "Subscription cancelled. Access remains until expiry."}


# =============================================================================
# RUTAS - ESTADÍSTICAS PERSONALES
# =============================================================================

@app.get("/api/stats/personal")
async def personal_stats(user: dict = Depends(get_current_user)):
    """Estadísticas personales del usuario"""
    user_id = user["id"]
    
    # Resultados OPO
    opo_stats = db_opo.fetchone("""
        SELECT 
            COUNT(*) as total_exams,
            COALESCE(AVG(score), 0) as avg_score,
            COALESCE(MAX(score), 0) as best_score,
            COALESCE(SUM(correct), 0) as total_correct,
            COALESCE(SUM(wrong), 0) as total_wrong,
            COALESCE(SUM(duration_seconds), 0) as total_time
        FROM opo_results WHERE user_id=?
    """, (user_id,))
    
    # Resultados por categoría
    by_category = db_opo.fetchall("""
        SELECT 
            c.name as category_name,
            c.slug as category_slug,
            COUNT(*) as exams_done,
            AVG(r.score) as avg_score,
            MAX(r.score) as best_score
        FROM opo_results r
        JOIN opo_categories c ON c.id = r.category_id
        WHERE r.user_id=?
        GROUP BY c.id
        ORDER BY exams_done DESC
    """, (user_id,))
    
    # Últimos resultados
    recent = db_opo.fetchall("""
        SELECT 
            r.score, r.correct, r.wrong, r.duration_seconds, r.completed_at,
            c.name as category_name
        FROM opo_results r
        LEFT JOIN opo_categories c ON c.id = r.category_id
        WHERE r.user_id=?
        ORDER BY r.completed_at DESC
        LIMIT 10
    """, (user_id,))
    
    return {
        "overview": {
            "total_exams": opo_stats["total_exams"] if opo_stats else 0,
            "avg_score": round(opo_stats["avg_score"] if opo_stats else 0),
            "best_score": opo_stats["best_score"] if opo_stats else 0,
            "total_correct": opo_stats["total_correct"] if opo_stats else 0,
            "total_wrong": opo_stats["total_wrong"] if opo_stats else 0,
            "total_time_minutes": round((opo_stats["total_time"] if opo_stats else 0) / 60)
        },
        "by_category": [dict(r) for r in by_category] if by_category else [],
        "recent": [dict(r) for r in recent] if recent else []
    }


# =============================================================================
# RUTAS - EXÁMENES DISPONIBLES
# =============================================================================

@app.get("/api/exams/available")
async def available_exams(user: dict = Depends(get_current_user)):
    """Lista todos los exámenes disponibles"""
    # Verificar si tiene premium
    has_premium = user["role"] == "admin"
    if not has_premium:
        sub = db_users.fetchone(
            "SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expires_at DESC LIMIT 1",
            (user["id"],)
        )
        if sub and datetime.fromisoformat(sub["expires_at"]) > datetime.now():
            has_premium = True
    
    # Categorías de exámenes
    categories = db_opo.fetchall("SELECT * FROM opo_categories ORDER BY name")
    
    # Si no hay categorías en BD, devolver las predefinidas
    if not categories:
        categories = [
            {"id": 1, "name": "Oposiciones Sanitarias", "slug": "sanitarias",
             "description": "Técnico Superior en Imagen para el Diagnóstico"},
            {"id": 2, "name": "Fuerzas de Seguridad", "slug": "seguridad",
             "description": "Policía Nacional, Guardia Civil"},
            {"id": 3, "name": "Educación", "slug": "educacion",
             "description": "Maestros, Profesores de Secundaria"},
            {"id": 4, "name": "Justicia", "slug": "justicia",
             "description": "Auxilio Judicial, Tramitación Procesal"},
            {"id": 5, "name": "Administración General", "slug": "admin-general",
             "description": "Auxiliar Administrativo, Administrativo del Estado"},
        ]
    
    result = []
    for cat in categories:
        cat_dict = dict(cat) if not isinstance(cat, dict) else cat
        cat_dict["available"] = has_premium or cat_dict.get("slug") == "sanitarias"
        cat_dict["locked"] = not cat_dict["available"]
        
        # Contar preguntas
        count = db_opo.fetchone(
            "SELECT COUNT(*) as cnt FROM opo_questions WHERE category_id=?",
            (cat_dict["id"],)
        )
        cat_dict["question_count"] = count["cnt"] if count else 0
        
        result.append(cat_dict)
    
    return {"categories": result, "has_premium": has_premium}

# =============================================================================
# RUTAS - PÁGINAS HTML
# =============================================================================

@app.get("/")
async def root():
    """Hub principal — pantalla principal de dvta.ch"""
    hub_path = os.path.join(STATIC_DIR, "hub.html")
    if os.path.exists(hub_path):
        return FileResponse(hub_path)
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

@app.get("/register")
async def register_page():
    """Página de registro — sirve la SPA que muestra el formulario de registro"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/login")
async def login_page():
    """Página de login — sirve la SPA que muestra el formulario de login"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/dashboard")
async def dashboard_page():
    """Página de dashboard — sirve la SPA"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/profile")
async def profile_page():
    """Página de perfil — sirve la SPA"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/plans")
async def plans_page():
    """Página de planes — sirve la SPA"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/stats")
async def stats_page_exams():
    """Página de estadísticas — sirve la SPA"""
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


# =============================================================================
# SHARED HTTP CLIENT for Bank proxy (connection pooling - no new conn per request)
# =============================================================================
import httpx as _httpx

_bank_client: _httpx.AsyncClient | None = None

@app.on_event("startup")
async def _start_bank_client():
    global _bank_client
    _bank_client = _httpx.AsyncClient(
        base_url="http://localhost:8000",
        timeout=_httpx.Timeout(15.0, connect=3.0),
        follow_redirects=False,
        limits=_httpx.Limits(max_connections=50, max_keepalive_connections=20),
    )

@app.on_event("shutdown")
async def _stop_bank_client():
    global _bank_client
    if _bank_client:
        await _bank_client.aclose()

_HOP_REQ = frozenset({"host", "content-length", "connection", "keep-alive",
                       "transfer-encoding", "upgrade", "te", "trailers",
                       "accept-encoding"})
_HOP_RESP = frozenset({"transfer-encoding", "connection", "keep-alive",
                        "upgrade", "te", "trailers",
                        "content-encoding", "content-length"})

# =============================================================================
# ACCESO DIRECTO DESDE dvta.ch (redirigen a /bank/* con login)
# =============================================================================

@app.get("/apuestas")
async def apuestas_redirect(token: str = ""):
    """Redirige a /bank/apuestas con token si lo tiene."""
    if token:
        return RedirectResponse(url=f"/bank/apuestas?token={token}")
    return RedirectResponse(url="/bank/apuestas")


# =============================================================================
# ADMIN PANEL - USERS (dvd & nebulosa only)
# =============================================================================

EXAMS_SUPERADMINS = {"dvd", "nebulosa", "tata"}


@app.get("/exams/admin/users", response_class=HTMLResponse)
async def exams_admin_users_page():
    """Serve the exams admin users panel."""
    path = os.path.join(STATIC_DIR, "admin_users.html")
    if not os.path.exists(path):
        return HTMLResponse("<h1>Admin page not found</h1>", status_code=404)
    return FileResponse(path)


@app.get("/api/admin/users")
async def exams_admin_list_users(user: dict = Depends(get_current_user)):
    """List all exams users with last login info. Superadmins only."""
    if user["username"] not in EXAMS_SUPERADMINS:
        raise HTTPException(403, "Superadmin access required")
    rows = db_users.fetchall(
        "SELECT id, email, username, role, verified, subscription_status, "
        "subscription_plan, lang, created_at, last_login FROM users ORDER BY last_login DESC"
    )
    now = datetime.now()
    result = []
    for r in rows:
        last_login = r.get("last_login") or r.get("created_at") or ""
        # Consider "online" if last_login within last 10 minutes
        is_online = False
        if last_login:
            try:
                ll = datetime.fromisoformat(last_login.replace("Z", "+00:00").replace("+00:00", ""))
                diff = (now - ll).total_seconds()
                is_online = diff < 600  # 10 minutes
            except Exception:
                pass
        result.append({
            "id": r["id"],
            "email": r["email"],
            "username": r["username"],
            "role": r["role"],
            "verified": bool(r["verified"]),
            "subscription": r.get("subscription_status") or "none",
            "plan": r.get("subscription_plan") or "",
            "lang": r.get("lang") or "es",
            "created_at": r.get("created_at") or "",
            "last_login": last_login,
            "online": is_online,
        })
    return {"users": result, "total": len(result)}


@app.get("/apuestas/porra/{porra_id}")
async def apuestas_porra_redirect(porra_id: int, token: str = ""):
    """Serve porra page directly or redirect to bank."""
    page_path = os.path.join(PORRAS_DIR, f"porra_{porra_id}.html")
    if os.path.exists(page_path):
        return FileResponse(page_path)
    # Fallback: redirect to bank which can generate the page
    if token:
        return RedirectResponse(url=f"/bank/apuestas/porra/{porra_id}?token={token}")
    return RedirectResponse(url=f"/bank/apuestas/porra/{porra_id}")

@app.get("/votaciones")
async def votaciones_redirect(token: str = ""):
    """Redirige a /bank/votaciones con token si lo tiene."""
    if token:
        return RedirectResponse(url=f"/bank/votaciones?token={token}")
    return RedirectResponse(url="/bank/votaciones")

@app.get("/mensajes")
async def mensajes_redirect(token: str = ""):
    """Redirige a /bank (sección social/mensajes)."""
    if token:
        return RedirectResponse(url=f"/bank?token={token}#social")
    return RedirectResponse(url="/bank")

@app.get("/social")
async def social_redirect(token: str = ""):
    """Redirige a /bank (sección social)."""
    if token:
        return RedirectResponse(url=f"/bank?token={token}#social")
    return RedirectResponse(url="/bank")

@app.get("/video")
async def video_redirect(token: str = ""):
    """Redirige a /bank/video (videollamadas)."""
    if token:
        return RedirectResponse(url=f"/bank/video?token={token}")
    return RedirectResponse(url="/bank/video")

@app.get("/salas")
async def salas_redirect(token: str = ""):
    """Redirige a /bank/salas (salas de video)."""
    if token:
        return RedirectResponse(url=f"/bank/salas?token={token}")
    return RedirectResponse(url="/bank/salas")


# ── Direct porra page serving (avoids proxy issues) ──
@app.get("/bank/apuestas/porra/{porra_id}", response_class=HTMLResponse)
async def bank_porra_direct(porra_id: int, request: Request):
    """Serve porra page directly without going through bank proxy."""
    page_path = os.path.join(PORRAS_DIR, f"porra_{porra_id}.html")
    if os.path.exists(page_path):
        return FileResponse(page_path)
    # File doesn't exist - proxy to bank so it can generate the page
    target = f"/bank/apuestas/porra/{porra_id}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"
    fwd_headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP_REQ}
    fwd_headers["accept-encoding"] = "identity"
    try:
        r = await _bank_client.request(method="GET", url=target, headers=fwd_headers)
        resp_headers = {k: v for k, v in r.headers.items() if k.lower() not in _HOP_RESP}
        return Response(content=r.content, status_code=r.status_code, headers=resp_headers,
                        media_type=r.headers.get("content-type"))
    except Exception:
        raise HTTPException(404, f"Porra {porra_id} not found")

@app.api_route(
    "/bank{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def bank_reverse_proxy(path: str, request: Request):
    """
    Reverse proxy a /bank{path} → localhost:8000/bank{path}.
    Usa client compartido con connection pooling.
    """
    target = f"/bank{path}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"

    fwd_headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP_REQ}
    fwd_headers["accept-encoding"] = "identity"

    body = await request.body() if request.method not in ("GET", "HEAD") else None

    try:
        r = await _bank_client.request(
            method=request.method,
            url=target,
            headers=fwd_headers,
            content=body,
        )
        resp_headers = {k: v for k, v in r.headers.items() if k.lower() not in _HOP_RESP}
        return Response(
            content=r.content,
            status_code=r.status_code,
            headers=resp_headers,
            media_type=r.headers.get("content-type"),
        )
    except (_httpx.ConnectError, _httpx.TimeoutException) as e:
        logger.warning(f"Bank proxy: {e}")
        return JSONResponse({"error": "bank_unavailable", "detail": "Bank (8000) no responde."}, status_code=503)
    except Exception as e:
        logger.exception(f"Bank proxy error: {e}")
        return JSONResponse({"error": "proxy_error", "detail": str(e)}, status_code=502)


# =============================================================================
# WEBSOCKET PROXY - Para juegos del Bank (pasapalabra, millonario, etc.)
# =============================================================================

import asyncio
import websockets as _ws_lib
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/bank/ws/{path:path}")
async def bank_ws_proxy(websocket: WebSocket, path: str):
    """
    Proxy WebSocket: dvta.ch/bank/ws/{game} → localhost:8000/bank/ws/{game}
    Esto permite que los juegos funcionen a través del proxy.
    """
    await websocket.accept()

    # Build upstream URL preserving query params (token)
    qs = websocket.query_params
    qs_str = ("?" + "&".join(f"{k}={v}" for k, v in qs.items())) if qs else ""
    target = f"ws://localhost:8000/bank/ws/{path}{qs_str}"

    try:
        async with _ws_lib.connect(target, max_size=None, ping_interval=20) as upstream:
            async def client_to_upstream():
                try:
                    while True:
                        msg = await websocket.receive_text()
                        await upstream.send(msg)
                except WebSocketDisconnect:
                    pass
                except Exception:
                    pass

            async def upstream_to_client():
                try:
                    async for msg in upstream:
                        if isinstance(msg, bytes):
                            await websocket.send_bytes(msg)
                        else:
                            await websocket.send_text(msg)
                except Exception:
                    pass

            done, pending = await asyncio.gather(
                client_to_upstream(), upstream_to_client(),
                return_exceptions=True
            )
    except Exception as e:
        logger.warning(f"WS proxy /bank/ws/{path} error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/games", response_class=HTMLResponse)
@app.get("/games/", response_class=HTMLResponse)
async def games_page():
    """Página principal de juegos - servida directamente sin proxy"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DVDcoin Games</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0e14;min-height:100vh;color:#e8edf5}
.container{max-width:900px;margin:0 auto;padding:40px 20px}
h1{font-size:2.2rem;color:#8bb3e8;margin-bottom:8px;text-align:center}
.sub{text-align:center;color:#5a6a80;margin-bottom:40px;font-size:.9rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.card{background:#141a24;border:1px solid rgba(107,155,212,.18);border-radius:14px;
padding:24px;cursor:pointer;transition:all .25s;text-decoration:none;color:#e8edf5;display:block}
.card:hover{border-color:#4a7ab8;transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.4)}
.icon{font-size:2.5rem;margin-bottom:12px}
.name{font-size:1.1rem;font-weight:600;margin-bottom:4px}
.desc{font-size:.78rem;color:#5a6a80}
.back{display:block;text-align:center;margin-top:30px;color:#4a7ab8;text-decoration:none;font-size:.85rem}
.back:hover{color:#8bb3e8}
</style>
</head>
<body>
<div class="container">
<h1>🎮 DVDcoin Games</h1>
<p class="sub">Centro de Juegos y Entretenimiento</p>
<div class="grid">
<a href="/bank/pasapalabra" class="card"><div class="icon">🎯</div><div class="name">Pasapalabra</div><div class="desc">El rosco de preguntas</div></a>
<a href="/bank/millonario" class="card"><div class="icon">💰</div><div class="name">Millonario</div><div class="desc">¿Quién quiere ser millonario?</div></a>
<a href="/bank/quiensoy" class="card"><div class="icon">🎭</div><div class="name">¿Quién Soy?</div><div class="desc">Adivina el personaje</div></a>
<a href="/bank/cifrasletras" class="card"><div class="icon">🔢</div><div class="name">Cifras y Letras</div><div class="desc">Números y palabras</div></a>
<a href="/bank/hundirlaflota" class="card"><div class="icon">⚓</div><div class="name">Hundir la Flota</div><div class="desc">Estrategia naval</div></a>
<a href="/bank/apuestas" class="card"><div class="icon">🎲</div><div class="name">Apuestas</div><div class="desc">Porras y predicciones</div></a>
<a href="/bank/votaciones" class="card"><div class="icon">🗳️</div><div class="name">Votaciones</div><div class="desc">Encuestas de la comunidad</div></a>
</div>
<a href="/" class="back">← Volver al Hub</a>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.api_route(
    "/games/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def games_subpath_proxy(path: str, request: Request):
    """Proxy para sub-rutas de games que necesiten el backend."""
    import httpx
    target = f"/games/{path}"
    qs = request.url.query
    if qs:
        target = f"{target}?{qs}"
    try:
        body = await request.body()
        async with httpx.AsyncClient(base_url="http://localhost:8004", timeout=8.0,
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
        return JSONResponse(
            {"error": "games_unavailable", "detail": "Servicio Games no disponible."},
            status_code=503,
        )
    except Exception as e:
        logger.exception(f"Games proxy error: {e}")
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
        async with httpx.AsyncClient(base_url="http://localhost:8003", timeout=2.0,
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
            return HTMLResponse(content="""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Social - DVDcoin</title>
<style>body{font-family:sans-serif;background:#0a0e14;color:#e8edf5;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.box{text-align:center;padding:40px;border:1px solid rgba(107,155,212,.2);border-radius:16px;max-width:400px}
h2{color:#8bb3e8;margin-bottom:12px}p{color:#5a6a80;margin-bottom:20px}
a{color:#4a7ab8;text-decoration:none}a:hover{color:#8bb3e8}</style></head>
<body><div class="box"><h2>💬 Social</h2><p>El módulo Social está integrado en el Bank.<br>Accede desde la pestaña Social dentro del Bank.</p>
<a href="/bank">→ Ir al Bank (pestaña Social)</a></div></body></html>""", status_code=200)
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
