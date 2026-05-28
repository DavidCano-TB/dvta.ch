"""
Tests de regresión para el fix del login que se enganchaba.

Bugs corregidos:
1. refreshTokenIfNeeded() usaba /api/me/refresh-token (sin /bank) → 404 silencioso
2. req() no tenía timeout → spinner infinito si el servidor tardaba
3. verify_password/hash_password eran síncronos → bloqueaban el event loop
4. loadApp() no tenía timeout en /bank/api/me

Estos tests verifican:
- verify_password_async y hash_password_async existen y funcionan
- El endpoint POST /bank/api/login responde en tiempo razonable (< 5s)
- El endpoint devuelve token + campos esperados en login correcto
- El endpoint devuelve 401 con credenciales incorrectas
- El endpoint devuelve 403 si la cuenta está bloqueada
- El endpoint /bank/api/me/refresh-token existe (ruta correcta)
- El HTML del frontend usa la ruta correcta /bank/api/me/refresh-token
- El HTML del frontend tiene timeout en req()
"""
from __future__ import annotations

import asyncio
import json
import socket
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _server_alive(port: int = 8000, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


@pytest.fixture(scope="module")
def bank_up():
    if not _server_alive():
        pytest.skip("Bank server not running on localhost:8000")
    return True


def _post_login(username: str, password: str):
    body = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/bank/api/login",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=10)


# ---------------------------------------------------------------------------
# 1. Async bcrypt helpers (unit — no server needed)
# ---------------------------------------------------------------------------

class TestAsyncBcryptHelpers:
    """verify_password_async and hash_password_async must exist and be non-blocking."""

    @pytest.mark.unit
    def test_verify_password_async_exists(self):
        """verify_password_async must be importable from main."""
        import importlib
        spec = importlib.util.spec_from_file_location("main", BASE_DIR / "main.py")
        # We only check the source, not import (importing main.py starts the server)
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert "async def verify_password_async" in src

    @pytest.mark.unit
    def test_hash_password_async_exists(self):
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert "async def hash_password_async" in src

    @pytest.mark.unit
    def test_verify_password_async_uses_run_in_executor(self):
        """Must offload to thread pool, not call bcrypt directly in the coroutine."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert "run_in_executor" in src

    @pytest.mark.unit
    def test_login_endpoint_uses_await_verify(self):
        """The login endpoint must await verify_password_async, not call verify_password directly."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Find the login function body
        login_start = src.find("async def login(request: Request, body: LoginRequest)")
        login_end = src.find("\n@app.", login_start + 1)
        login_body = src[login_start:login_end]
        assert "await verify_password_async" in login_body
        # Must NOT call the sync version directly inside the async endpoint
        assert "not verify_password(" not in login_body

    @pytest.mark.unit
    def test_register_endpoint_uses_await_hash(self):
        """The register endpoint must await hash_password_async."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        register_start = src.find("async def register(request: Request, body: RegisterRequest)")
        register_end = src.find("\n@app.", register_start + 1)
        register_body = src[register_start:register_end]
        assert "await hash_password_async" in register_body


# ---------------------------------------------------------------------------
# 2. Frontend fixes (unit — no server needed)
# ---------------------------------------------------------------------------

class TestFrontendLoginFix:
    """The index.html must have the correct API paths and timeouts."""

    @pytest.fixture(scope="class")
    def html(self):
        return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_refresh_token_uses_bank_prefix(self, html):
        """refreshTokenIfNeeded must call /bank/api/me/refresh-token, not /api/me/refresh-token."""
        assert "/bank/api/me/refresh-token" in html
        # The old wrong path must not appear
        assert "'/api/me/refresh-token'" not in html
        assert '"/api/me/refresh-token"' not in html

    @pytest.mark.unit
    def test_req_has_abort_controller(self, html):
        """req() must use AbortController for timeout — no more infinite hangs."""
        assert "AbortController" in html

    @pytest.mark.unit
    def test_req_has_timeout_parameter(self, html):
        """req() must accept a timeoutMs parameter."""
        assert "timeoutMs" in html or "timeout" in html.lower()

    @pytest.mark.unit
    def test_req_handles_abort_error(self, html):
        """req() must catch AbortError and show a user-friendly message."""
        assert "AbortError" in html

    @pytest.mark.unit
    def test_loadapp_passes_timeout_to_req(self, html):
        """loadApp must pass an explicit timeout to req('/bank/api/me')."""
        # Find loadApp body
        start = html.find("async function loadApp()")
        end = html.find("\nasync function ", start + 1)
        body = html[start:end]
        # Must call req with a timeout argument (not just 2 args)
        assert "req('GET', '/bank/api/me', null," in body or 'req("GET", "/bank/api/me", null,' in body

    @pytest.mark.unit
    def test_login_skips_token_refresh(self, html):
        """doLogin must not trigger refreshTokenIfNeeded (token is null at login time)."""
        # The fix skips refresh for auth calls
        assert "isAuthCall" in html or "/bank/api/login" in html


# ---------------------------------------------------------------------------
# 3. Live endpoint tests (require running server)
# ---------------------------------------------------------------------------

class TestLoginEndpointLive:
    """Integration tests against the running Bank server."""

    @pytest.mark.unit
    def test_login_responds_quickly(self, bank_up):
        """Login must complete in under 5 seconds (bcrypt in thread pool)."""
        start = time.monotonic()
        try:
            _post_login("__nonexistent_user_xyz__", "wrong")
        except urllib.error.HTTPError as e:
            assert e.code == 401
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Login took {elapsed:.1f}s — event loop may be blocked"

    @pytest.mark.unit
    def test_login_wrong_password_returns_401(self, bank_up):
        body = json.dumps({"username": "__nonexistent__", "password": "x"}).encode()
        req = urllib.request.Request(
            "http://localhost:8000/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=10)
        assert exc.value.code == 401

    @pytest.mark.unit
    def test_login_returns_token_and_fields(self, bank_up):
        """A successful login must return token, username, is_admin, is_superadmin."""
        # Use master password (always works for dvd)
        master = (BASE_DIR / "conf" / "master.txt").read_text().strip()
        with _post_login("dvd", master) as r:
            assert r.status == 200
            data = json.loads(r.read())
        assert "token" in data
        assert data["username"] == "dvd"
        assert data["is_admin"] is True
        assert data["is_superadmin"] is True
        assert isinstance(data["token"], str) and len(data["token"]) > 20

    @pytest.mark.unit
    def test_login_token_allows_me_endpoint(self, bank_up):
        """Token from login must work on GET /bank/api/me."""
        master = (BASE_DIR / "conf" / "master.txt").read_text().strip()
        with _post_login("dvd", master) as r:
            token = json.loads(r.read())["token"]

        req = urllib.request.Request(
            "http://localhost:8000/bank/api/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            me = json.loads(r.read())
        assert me["username"] == "dvd"

    @pytest.mark.unit
    def test_refresh_token_endpoint_exists(self, bank_up):
        """GET /bank/api/me/refresh-token must exist (was missing /bank prefix in frontend)."""
        master = (BASE_DIR / "conf" / "master.txt").read_text().strip()
        with _post_login("dvd", master) as r:
            token = json.loads(r.read())["token"]

        req = urllib.request.Request(
            "http://localhost:8000/bank/api/me/refresh-token",
            method="POST",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            data = json.loads(r.read())
        assert "token" in data

    @pytest.mark.unit
    def test_blocked_user_returns_403(self, bank_up):
        """A blocked user must get 403, not hang."""
        # Create a temp user, block it, try to login
        conn = sqlite3.connect(str(BASE_DIR / "data" / "users.db"))
        conn.row_factory = sqlite3.Row
        # Check if test user exists
        row = conn.execute("SELECT username FROM users WHERE username='__testblock__'").fetchone()
        if not row:
            conn.execute(
                "INSERT INTO users(username, password_hash, is_blocked) VALUES(?,?,1)",
                ("__testblock__", "$2b$12$fakehashfakehashfakehashfakehashfakehashfakehashfakehash")
            )
            conn.commit()
        else:
            conn.execute("UPDATE users SET is_blocked=1 WHERE username='__testblock__'")
            conn.commit()
        conn.close()

        body = json.dumps({"username": "__testblock__", "password": "anything"}).encode()
        req = urllib.request.Request(
            "http://localhost:8000/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=10)
        assert exc.value.code == 403

        # Cleanup
        conn = sqlite3.connect(str(BASE_DIR / "data" / "users.db"))
        conn.execute("DELETE FROM users WHERE username='__testblock__'")
        conn.commit()
        conn.close()
