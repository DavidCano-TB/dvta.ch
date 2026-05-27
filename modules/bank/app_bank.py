"""
DVDcoin Bank Module - Servicio dedicado del Bank
Puerto: 8002

Este servicio actúa como REVERSE PROXY al Bank principal (localhost:8000).
Sirve como punto de entrada modular para `dvta.ch/bank/*` con su propio
ciclo de vida, health-check, y panel de fallback cuando el Bank principal
no responde.

Rutas:
- /bank, /bank/*           → reverse proxy a http://localhost:8000/bank/*
- /static/*                → reverse proxy (Bank principal sirve assets ahí)
- /ws/*                    → websocket reverse proxy
- /bank/panel-fallback     → panel estático de respaldo (modules/bank/static/panel.html)
- /health                  → health del proxy + estado del Bank principal
- /api/info                → metadata del servicio
"""
import os
import sys
import logging
from typing import AsyncIterator
from urllib.parse import urlencode

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

from db_helper import DatabaseHelper

# =============================================================================
# CONFIG
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
for d in (DATA_DIR, STATIC_DIR, CONFIG_DIR):
    os.makedirs(d, exist_ok=True)

DB_PANEL = os.path.join(DATA_DIR, "bank_panel.db")

# Upstream Bank principal (main.py corriendo en 8000)
BANK_UPSTREAM = os.environ.get("BANK_UPSTREAM", "http://localhost:8000")
BANK_ORIGIN_URL = "https://bank.dvta.ch"  # solo informativo
PORT = 8002

# Headers de salto-a-salto que NO deben reenviarse
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "host",
    "content-length",  # httpx will set this; let it
}

# Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bank-proxy")

# =============================================================================
# APP
# =============================================================================

app = FastAPI(title="DVDcoin Bank Proxy", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
logger.info("Bank proxy database initialized")

# Single shared httpx client (connection pool)
_client: httpx.AsyncClient | None = None


@app.on_event("startup")
async def _startup():
    global _client
    _client = httpx.AsyncClient(
        base_url=BANK_UPSTREAM,
        timeout=httpx.Timeout(30.0, connect=5.0),
        follow_redirects=False,
    )
    logger.info(f"Bank Proxy ready · upstream={BANK_UPSTREAM}")


@app.on_event("shutdown")
async def _shutdown():
    global _client
    if _client:
        await _client.aclose()


# =============================================================================
# HELPERS
# =============================================================================

def _filter_request_headers(req: Request) -> dict:
    """Forward all headers except hop-by-hop and Host."""
    out = {}
    for k, v in req.headers.items():
        if k.lower() not in HOP_BY_HOP:
            out[k] = v
    # Preserve original client info for the upstream
    client_host = req.client.host if req.client else ""
    if client_host:
        out["X-Forwarded-For"] = req.headers.get("x-forwarded-for", client_host)
    out["X-Forwarded-Proto"] = req.headers.get("x-forwarded-proto", req.url.scheme)
    out["X-Forwarded-Host"] = req.headers.get("x-forwarded-host", req.url.netloc)
    return out


def _filter_response_headers(headers) -> list:
    """Strip hop-by-hop response headers."""
    return [(k, v) for k, v in headers.items() if k.lower() not in HOP_BY_HOP]


async def _proxy(request: Request, upstream_path: str):
    """Stream-proxy a request to the upstream Bank."""
    assert _client is not None

    # Build upstream URL preserving the query string
    qs = request.url.query
    target = upstream_path + (f"?{qs}" if qs else "")

    headers = _filter_request_headers(request)

    # Stream the body for upload-friendly behavior
    body = await request.body() if request.method not in ("GET", "HEAD") else None

    try:
        upstream_req = _client.build_request(
            method=request.method,
            url=target,
            headers=headers,
            content=body,
        )
        upstream_resp = await _client.send(upstream_req, stream=True)
    except httpx.ConnectError:
        logger.warning(f"Upstream {BANK_UPSTREAM} unreachable for {target}")
        return _fallback_response(request, upstream_path)
    except httpx.TimeoutException:
        logger.warning(f"Upstream timeout for {target}")
        return JSONResponse(
            {"error": "upstream_timeout",
             "detail": "Bank principal no responde a tiempo. Intenta en unos segundos."},
            status_code=504,
        )
    except Exception as e:
        logger.exception(f"Proxy error for {target}: {e}")
        return JSONResponse(
            {"error": "proxy_error", "detail": str(e)},
            status_code=502,
        )

    # Build a streaming response back to the client
    async def stream() -> AsyncIterator[bytes]:
        try:
            async for chunk in upstream_resp.aiter_raw():
                yield chunk
        finally:
            await upstream_resp.aclose()

    return StreamingResponse(
        stream(),
        status_code=upstream_resp.status_code,
        headers=dict(_filter_response_headers(upstream_resp.headers)),
        media_type=upstream_resp.headers.get("content-type"),
        background=BackgroundTask(upstream_resp.aclose),
    )


def _fallback_response(request: Request, upstream_path: str):
    """When the upstream is down, serve the static panel for /bank GETs,
    or return JSON 503 for API calls."""
    if request.method != "GET":
        return JSONResponse(
            {"error": "upstream_unavailable",
             "detail": f"El Bank principal ({BANK_UPSTREAM}) no está disponible."},
            status_code=503,
        )
    panel = os.path.join(STATIC_DIR, "panel.html")
    if upstream_path.startswith("/bank") and os.path.exists(panel):
        return FileResponse(panel, status_code=200)
    return JSONResponse(
        {"error": "upstream_unavailable",
         "detail": f"Bank principal ({BANK_UPSTREAM}) no responde."},
        status_code=503,
    )


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/")
async def root():
    return RedirectResponse(url="/bank")


@app.get("/health")
async def health_check():
    """Salud del proxy + estado del upstream"""
    upstream_ok = False
    upstream_status = None
    try:
        if _client is not None:
            r = await _client.get("/health", timeout=2.0)
            upstream_status = r.status_code
            upstream_ok = r.status_code < 500
    except Exception as e:
        logger.debug(f"Upstream health probe failed: {e}")
    return {
        "status": "healthy",
        "service": "DVDcoin Bank Proxy",
        "version": "2.0.0",
        "port": PORT,
        "upstream": BANK_UPSTREAM,
        "upstream_ok": upstream_ok,
        "upstream_status": upstream_status,
        "origin": BANK_ORIGIN_URL,
    }


@app.get("/api/info")
async def api_info():
    return {
        "service": "Bank Proxy",
        "port": PORT,
        "upstream": BANK_UPSTREAM,
        "origin": BANK_ORIGIN_URL,
        "available_routes": [
            "/bank, /bank/* - Reverse proxy al Bank principal",
            "/static/* - Reverse proxy (assets del Bank)",
            "/ws/* - Reverse proxy WebSocket",
            "/bank/panel-fallback - Panel estático de respaldo",
            "/health - Estado del proxy y del upstream",
            "/api/info - Metadata del servicio",
        ],
    }


@app.get("/bank/panel-fallback")
async def bank_panel_fallback():
    """Panel estático de respaldo (no depende del Bank principal)."""
    panel = os.path.join(STATIC_DIR, "panel.html")
    if os.path.exists(panel):
        return FileResponse(panel)
    raise HTTPException(404, "Panel not found")


# Reverse proxy: catch-all for Bank routes
@app.api_route(
    "/bank{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy_bank(path: str, request: Request):
    return await _proxy(request, f"/bank{path}")


@app.api_route(
    "/static/{path:path}",
    methods=["GET", "HEAD", "OPTIONS"],
)
async def proxy_static(path: str, request: Request):
    return await _proxy(request, f"/static/{path}")


# =============================================================================
# WEBSOCKET PROXY (for /ws/* used by Bank games)
# =============================================================================

import asyncio
import websockets  # type: ignore


@app.websocket("/ws/{path:path}")
async def ws_proxy(websocket: WebSocket, path: str):
    """Reverse proxy de WebSocket hacia el Bank principal."""
    await websocket.accept()

    qs = websocket.query_params
    qs_str = ("?" + urlencode(dict(qs))) if qs else ""
    upstream_url = BANK_UPSTREAM.replace("http://", "ws://").replace("https://", "wss://")
    target = f"{upstream_url}/ws/{path}{qs_str}"

    try:
        async with websockets.connect(target, max_size=None) as upstream:
            async def client_to_upstream():
                try:
                    while True:
                        msg = await websocket.receive_text()
                        await upstream.send(msg)
                except WebSocketDisconnect:
                    await upstream.close()

            async def upstream_to_client():
                try:
                    async for msg in upstream:
                        if isinstance(msg, bytes):
                            await websocket.send_bytes(msg)
                        else:
                            await websocket.send_text(msg)
                except Exception:
                    pass

            await asyncio.gather(client_to_upstream(), upstream_to_client(),
                                 return_exceptions=True)
    except Exception as e:
        logger.warning(f"WS proxy error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 80)
    logger.info("DVDcoin Bank Proxy starting...")
    logger.info(f"Port:     {PORT}")
    logger.info(f"Local:    http://localhost:{PORT}/bank")
    logger.info(f"Upstream: {BANK_UPSTREAM}")
    logger.info(f"External: https://dvta.ch/bank (via tunnel)")
    logger.info("=" * 80)
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
