"""
DVDcoin Social Module - Sistema de Chat y Mensajería
Puerto: 8003
Dominio: social.dvta.ch
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Optional
import logging

# Añadir módulos compartidos al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from fastapi import FastAPI, HTTPException, Depends, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from db_helper import DatabaseHelper, create_database
from jwt_helper import JWTHelper, load_or_create_secret

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Bases de datos
DB_MESSAGES = os.path.join(DATA_DIR, "messages.db")
DB_ROOMS = os.path.join(DATA_DIR, "rooms.db")

# Admins
ADMINS = {"dvd", "nebulosa", "nina", "victor", "yu", "roy", "admin", "aitor"}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("social")

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

app = FastAPI(title="DVDcoin Social", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT - Compartido con el servidor principal
jwt_secret = load_or_create_secret(os.path.join(BASE_DIR, "..", "..", "src", "config"), "jwt_secret.txt")
jwt_helper = JWTHelper(jwt_secret, expire_hours=168)

# Security
security = HTTPBearer(auto_error=False)

# WebSocket connections
active_connections: dict = {}

# =============================================================================
# AUTENTICACIÓN
# =============================================================================

def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Obtiene el usuario actual desde cookie o header Authorization"""
    token = None
    
    # Opción 1: Cookie (preferido)
    token = request.cookies.get("dvd_token")
    
    # Opción 2: Header Authorization (fallback)
    if not token and creds:
        token = creds.credentials
    
    if not token:
        raise HTTPException(401, "Authentication required")
    
    username = jwt_helper.get_username(token)
    if not username:
        raise HTTPException(401, "Invalid or expired session")
    
    return username

# =============================================================================
# INICIALIZACIÓN DE BASE DE DATOS
# =============================================================================

def init_databases():
    """Inicializa las bases de datos necesarias"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # DB Messages
    db_messages = DatabaseHelper(DB_MESSAGES)
    db_messages.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            from_user TEXT NOT NULL,
            content TEXT NOT NULL,
            msg_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db_messages.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room)
    """)
    
    # DB Rooms
    db_rooms = DatabaseHelper(DB_ROOMS)
    db_rooms.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            host TEXT NOT NULL,
            mode TEXT DEFAULT 'public',
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    logger.info("Databases initialized")

init_databases()

# =============================================================================
# RUTAS PRINCIPALES
# =============================================================================

@app.get("/")
async def root():
    """Redirige a la página principal de social"""
    return RedirectResponse(url="/social")

@app.get("/social", response_class=HTMLResponse)
async def social_page():
    """Página principal de social"""
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DVDcoin Social</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                max-width: 800px;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .emoji {
                font-size: 5rem;
                margin-bottom: 20px;
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.2);
                padding: 30px;
                border-radius: 15px;
                transition: all 0.3s;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.3);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            .feature-name {
                font-size: 1.2rem;
                font-weight: bold;
            }
            .status {
                margin-top: 30px;
                padding: 15px;
                background: rgba(0, 255, 0, 0.2);
                border-radius: 10px;
                border: 2px solid rgba(0, 255, 0, 0.5);
            }
            .back-btn {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 25px;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
            }
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.05);
            }
            .link-btn {
                display: inline-block;
                margin: 10px;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                text-decoration: none;
                color: white;
                font-weight: bold;
                transition: all 0.3s;
            }
            .link-btn:hover {
                background: rgba(255, 255, 255, 0.4);
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">💬</div>
            <h1>DVDcoin Social</h1>
            <p>Centro de Comunicación y Mensajería</p>
            
            <div class="status">
                ✅ Servidor Social activo en puerto 8003
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <div class="feature-name">Chat en Tiempo Real</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📹</div>
                    <div class="feature-name">Videollamadas</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔔</div>
                    <div class="feature-name">Notificaciones</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <div class="feature-name">Salas Privadas</div>
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://dvta.ch/bank/messages" class="link-btn">💬 Ir al Chat</a>
                <a href="https://dvta.ch/bank/salas" class="link-btn">📹 Salas de Video</a>
            </div>
            
            <a href="https://dvta.ch/bank" class="back-btn">← Volver al Bank</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "social",
        "port": 8003,
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(active_connections)
    }

@app.get("/api/messages/status")
async def messages_status(user: str = Depends(get_current_user)):
    """Estado del sistema de mensajería"""
    return {
        "enabled": True,
        "online": list(active_connections.keys()),
        "rooms": ["group"]
    }

@app.websocket("/ws/messages")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    """WebSocket para mensajería en tiempo real"""
    username = jwt_helper.get_username(token) if token else None
    
    if not username:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    await websocket.accept()
    active_connections[username] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast a todos los usuarios conectados
            for user, conn in active_connections.items():
                if user != username:
                    try:
                        await conn.send_text(data)
                    except:
                        pass
    except WebSocketDisconnect:
        active_connections.pop(username, None)

# =============================================================================
# MONTAR ARCHIVOS ESTÁTICOS
# =============================================================================

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting DVDcoin Social server on port 8003")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
