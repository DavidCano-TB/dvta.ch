"""
Shared JWT Helper - Reutilizable para todos los módulos
Maneja creación y validación de tokens JWT
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 1 semana por defecto


class JWTHelper:
    """Helper para manejar JWT tokens de forma consistente en todos los módulos"""
    
    def __init__(self, secret_key: str, expire_hours: int = JWT_EXPIRE_HOURS):
        self.secret_key = secret_key
        self.expire_hours = expire_hours
        self.algorithm = JWT_ALGORITHM
    
    def create_token(self, username: str, extra_claims: dict = None) -> str:
        """
        Crea un token JWT para un usuario
        
        Args:
            username: Nombre de usuario
            extra_claims: Claims adicionales (role, email, etc.)
        
        Returns:
            Token JWT como string
        """
        exp = datetime.utcnow() + timedelta(hours=self.expire_hours)
        payload = {
            "sub": username,
            "exp": exp,
            "iat": datetime.utcnow()
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decodifica y valida un token JWT
        
        Args:
            token: Token JWT
        
        Returns:
            Payload del token o None si es inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def get_username(self, token: str) -> Optional[str]:
        """
        Extrae el username de un token
        
        Args:
            token: Token JWT
        
        Returns:
            Username o None si el token es inválido
        """
        payload = self.decode_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    def verify_token(self, token: str) -> bool:
        """
        Verifica si un token es válido
        
        Args:
            token: Token JWT
        
        Returns:
            True si es válido, False si no
        """
        return self.decode_token(token) is not None


def load_or_create_secret(config_dir: str, filename: str = "jwt_secret.txt") -> str:
    """
    Carga o crea un secret key para JWT
    
    Args:
        config_dir: Directorio de configuración
        filename: Nombre del archivo de secret
    
    Returns:
        Secret key
    """
    os.makedirs(config_dir, exist_ok=True)
    secret_path = os.path.join(config_dir, filename)
    
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            secret = f.read().strip()
            if secret:
                return secret
    
    # Generar nuevo secret
    import secrets
    secret = secrets.token_hex(32)
    
    with open(secret_path, 'w') as f:
        f.write(secret)
    
    return secret
