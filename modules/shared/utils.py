"""
Shared Utilities - Funciones reutilizables para todos los módulos
"""
import hashlib
import secrets
import string
from datetime import datetime
from typing import Optional


def generate_token(length: int = 32) -> str:
    """Genera un token aleatorio seguro"""
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """Genera un código numérico de verificación"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash"""
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formatea una fecha/hora"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def validate_email(email: str) -> bool:
    """Valida formato de email básico"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_username(username: str) -> str:
    """Sanitiza un username (solo alfanuméricos y guiones)"""
    import re
    return re.sub(r'[^a-zA-Z0-9_-]', '', username)


def generate_slug(text: str) -> str:
    """Genera un slug URL-friendly desde texto"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')
