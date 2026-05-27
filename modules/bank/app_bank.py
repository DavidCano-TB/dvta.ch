"""
DVDcoin Bank Module - Servicio dedicado del Bank
Puerto: 8002
Acceso: dvta.ch/bank (proxied) y http://localhost:8002

Este servicio es independiente del main.py original (puerto 8000) que sigue
funcionando como bank.dvta.ch sin cambios.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db_helper import DatabaseHelper

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Crear directorios si no existen
for d in [DATA_DIR, STATIC_DIR, CONFIG_DIR]:
    os.makedirs(d, exist_ok=True)

# Base de datos local del panel Bank (estadísticas/preferencias)
DB_PANEL = os.path.join(DATA_DIR, "bank_panel.db")

# URL del Bank original (donde está toda la lógica completa)
BANK_ORIGIN_URL = "https://bank.dvta.ch"

PORT = 8002

# Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bank-panel")

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

app = FastAPI(title="DVDcoin Bank Panel", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema básico de la BD del panel
SCHEMA_PANEL = """
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visited_at TEXT NOT NULL DEFAULT (datetime('now')),
    user_agent TEXT,
    ip TEXT
);

CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

db_panel = DatabaseHelper(DB_PANEL)
db_panel.create_tables(SCHEMA_PANEL)
logger.info("Bank panel database initialized")

# =============================================================================
# RUTAS
# =============================================================================

@app.get("/")
async def root():
    """Página principal - redirige a /bank"""
    return RedirectResponse(url="/bank")

@app.get("/bank")
async def bank_panel():
    """Panel principal del Bank"""
    panel_path = os.path.join(STATIC_DIR, "panel.html")
    if os.path.exists(panel_path):
        return FileResponse(panel_path)
    raise HTTPException(404, "Panel not found")

@app.get("/bank/")
async def bank_panel_slash():
    return await bank_panel()

@app.get("/bank/full")
async def bank_full_redirect():
    """Redirige al Bank completo (main.py original en bank.dvta.ch)"""
    return RedirectResponse(url=BANK_ORIGIN_URL)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "DVDcoin Bank Panel",
        "version": "1.0.0",
        "port": PORT,
        "origin": BANK_ORIGIN_URL
    }

@app.get("/api/info")
async def api_info():
    """Información del servicio"""
    return {
        "service": "Bank Panel",
        "port": PORT,
        "origin": BANK_ORIGIN_URL,
        "available_routes": [
            "/bank - Panel principal",
            "/bank/full - Redirige al Bank completo",
            "/health - Health check",
            "/api/info - Información"
        ]
    }

# Static files mount
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/bank/static", StaticFiles(directory=STATIC_DIR), name="bank_static")

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 80)
    logger.info("DVDcoin Bank Panel starting...")
    logger.info(f"Port: {PORT}")
    logger.info(f"Local:    http://localhost:{PORT}/bank")
    logger.info(f"External: https://dvta.ch/bank (via proxy)")
    logger.info(f"Origin:   {BANK_ORIGIN_URL}")
    logger.info("=" * 80)

    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
