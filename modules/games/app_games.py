"""
DVDcoin Games Module - Sistema de Juegos y Entretenimiento
Puerto: 8002
Dominio: games.dvta.ch
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
DB_GAMES = os.path.join(DATA_DIR, "games.db")
DB_SCORES = os.path.join(DATA_DIR, "scores.db")

# Admins
ADMINS = {"dvd", "nebulosa", "nina", "victor", "yu", "roy", "admin", "aitor"}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("games")

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

app = FastAPI(title="DVDcoin Games", version="1.0.0")

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
    
    # DB Games
    db_games = DatabaseHelper(DB_GAMES)
    db_games.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # DB Scores
    db_scores = DatabaseHelper(DB_SCORES)
    db_scores.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db_scores.execute("""
        CREATE INDEX IF NOT EXISTS idx_scores_game ON scores(game_name)
    """)
    db_scores.execute("""
        CREATE INDEX IF NOT EXISTS idx_scores_user ON scores(username)
    """)
    
    logger.info("Databases initialized")

init_databases()

# =============================================================================
# RUTAS PRINCIPALES
# =============================================================================

@app.get("/")
async def root():
    """Redirige a la página principal de juegos"""
    return RedirectResponse(url="/games")

@app.get("/games", response_class=HTMLResponse)
async def games_page():
    """Página principal de juegos"""
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DVDcoin Games</title>
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
            .games-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .game-card {
                background: rgba(255, 255, 255, 0.2);
                padding: 30px;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
                color: white;
                display: block;
            }
            .game-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.3);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            .game-icon {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            .game-name {
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🎮</div>
            <h1>DVDcoin Games</h1>
            <p>Centro de Juegos y Entretenimiento</p>
            
            <div class="status">
                ✅ Servidor Games activo en puerto 8002
            </div>
            
            <div class="games-grid">
                <a href="https://dvta.ch/bank/pasapalabra" class="game-card">
                    <div class="game-icon">🔤</div>
                    <div class="game-name">Pasapalabra</div>
                </a>
                
                <a href="https://dvta.ch/bank/millonario" class="game-card">
                    <div class="game-icon">💰</div>
                    <div class="game-name">Millonario</div>
                </a>
                
                <a href="https://dvta.ch/bank/quiensoy" class="game-card">
                    <div class="game-icon">🎭</div>
                    <div class="game-name">¿Quién Soy?</div>
                </a>
                
                <a href="https://dvta.ch/bank/cifrasletras" class="game-card">
                    <div class="game-icon">🔢</div>
                    <div class="game-name">Cifras y Letras</div>
                </a>
                
                <a href="https://dvta.ch/bank/hundirlaflota" class="game-card">
                    <div class="game-icon">⚓</div>
                    <div class="game-name">Hundir la Flota</div>
                </a>
                
                <a href="https://dvta.ch/bank/apuestas" class="game-card">
                    <div class="game-icon">🎲</div>
                    <div class="game-name">Apuestas</div>
                </a>
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
        "service": "games",
        "port": 8002,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/games")
async def list_games(user: str = Depends(get_current_user)):
    """Lista todos los juegos disponibles"""
    db = DatabaseHelper(DB_GAMES)
    games = db.fetchall("SELECT * FROM games WHERE active=1 ORDER BY name")
    return {"games": games}

@app.get("/api/scores/{game_name}")
async def get_scores(game_name: str, limit: int = 10):
    """Obtiene los mejores puntajes de un juego"""
    db = DatabaseHelper(DB_SCORES)
    scores = db.fetchall(
        "SELECT username, score, created_at FROM scores WHERE game_name=? ORDER BY score DESC LIMIT ?",
        (game_name, limit)
    )
    return {"game": game_name, "scores": scores}

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
    
    logger.info("Starting DVDcoin Games server on port 8002")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
