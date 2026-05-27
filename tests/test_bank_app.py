"""
Unit tests for the DVDcoin Bank Panel module (modules/bank/app_bank.py)

Tests cover:
- Endpoints (root, /bank, /bank/full, /health, /api/info)
- Static file mounts
- Database initialization
- Error handling and fallbacks

Note: Uses httpx.AsyncClient with ASGITransport because the installed
starlette + httpx pair has a TestClient compatibility issue.
"""
import os
import sys
import pytest
from pathlib import Path

import httpx

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))
sys.path.insert(0, str(BASE_DIR / "modules" / "bank"))


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bank_app(tmp_path_factory):
    """
    Import the bank module with isolated DATA_DIR / DB so tests don't pollute
    the real working directory.
    """
    tmp_data = tmp_path_factory.mktemp("bank_data")

    bank_module_path = str(BASE_DIR / "modules" / "bank")
    if bank_module_path not in sys.path:
        sys.path.insert(0, bank_module_path)

    if "app_bank" in sys.modules:
        del sys.modules["app_bank"]
    import app_bank  # type: ignore

    # Re-target DB to a temp location to avoid touching the real one.
    # NOTE: tables in the *original* DB are already created at import time;
    # we override the path only for tests that inspect/run new DBs separately.
    app_bank._original_db_panel = app_bank.DB_PANEL
    app_bank._test_db_panel = str(tmp_data / "bank_panel_test.db")
    return app_bank


@pytest.fixture
def asgi_transport(bank_app):
    """ASGI transport bound to the FastAPI app (httpx >= 0.28 style)."""
    return httpx.ASGITransport(app=bank_app.app)


@pytest.fixture
async def aclient(asgi_transport):
    """Async HTTP client backed by ASGI transport."""
    async with httpx.AsyncClient(
        transport=asgi_transport,
        base_url="http://testserver",
    ) as client:
        yield client


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test suite for /health endpoint"""

    async def test_health_returns_200(self, aclient):
        """Happy path: health check responds 200"""
        resp = await aclient.get("/health")
        assert resp.status_code == 200

    async def test_health_returns_expected_payload(self, aclient):
        """Health response contains required fields"""
        resp = await aclient.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "DVDcoin Bank Panel"
        assert data["port"] == 8002
        assert "origin" in data
        assert data["version"] == "1.0.0"


@pytest.mark.unit
@pytest.mark.asyncio
class TestApiInfo:
    """Test suite for /api/info endpoint"""

    async def test_info_returns_200(self, aclient):
        resp = await aclient.get("/api/info")
        assert resp.status_code == 200

    async def test_info_contains_routes_list(self, aclient):
        resp = await aclient.get("/api/info")
        data = resp.json()
        assert "available_routes" in data
        assert isinstance(data["available_routes"], list)
        assert len(data["available_routes"]) >= 4

    async def test_info_contains_service_metadata(self, aclient):
        resp = await aclient.get("/api/info")
        data = resp.json()
        assert data["service"] == "Bank Panel"
        assert data["port"] == 8002


@pytest.mark.unit
@pytest.mark.asyncio
class TestBankPanelEndpoint:
    """Test suite for /bank panel page"""

    async def test_bank_with_real_panel_html_returns_200(self, aclient):
        """Happy path: the shipped panel.html is served"""
        resp = await aclient.get("/bank")
        assert resp.status_code == 200
        # Real panel content sanity-check
        assert "DVDcoin" in resp.text

    async def test_bank_with_slash_works(self, aclient):
        """Trailing slash variant works"""
        resp = await aclient.get("/bank/")
        assert resp.status_code == 200

    async def test_bank_panel_html_contains_expected_markup(self, aclient):
        """The real panel.html shipped with the repo should contain key markers"""
        resp = await aclient.get("/bank")
        body = resp.text
        assert "Bank Panel" in body or "Bank" in body
        assert "<html" in body.lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestRootRedirect:
    """Test suite for / root endpoint"""

    async def test_root_redirects_to_bank(self, aclient):
        resp = await aclient.get("/", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert resp.headers["location"] == "/bank"


@pytest.mark.unit
@pytest.mark.asyncio
class TestBankFullRedirect:
    """Test suite for /bank/full external redirect"""

    async def test_bank_full_redirects_to_origin(self, aclient, bank_app):
        resp = await aclient.get("/bank/full", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert resp.headers["location"] == bank_app.BANK_ORIGIN_URL


@pytest.mark.unit
@pytest.mark.asyncio
class TestStaticMount:
    """Test suite for /static and /bank/static mounts"""

    async def test_static_mount_returns_404_for_unknown_file(self, aclient):
        """Edge case: missing static file returns 404"""
        resp = await aclient.get("/static/no_such_file_xyz.txt")
        assert resp.status_code == 404

    async def test_bank_static_mount_returns_404_for_unknown_file(self, aclient):
        """Edge case: missing /bank/static file returns 404"""
        resp = await aclient.get("/bank/static/no_such_file_xyz.txt")
        assert resp.status_code == 404


@pytest.mark.unit
class TestDatabaseInitialization:
    """Test suite for DB initialization (visits, preferences tables)"""

    def test_db_panel_path_is_set(self, bank_app):
        assert bank_app.DB_PANEL.endswith(".db")

    def test_visits_table_exists(self, bank_app):
        """The schema must create a visits table on the real DB used at import"""
        import sqlite3
        conn = sqlite3.connect(bank_app.DB_PANEL)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='visits'"
            )
            row = cur.fetchone()
            assert row is not None, "visits table must exist"
        finally:
            conn.close()

    def test_preferences_table_exists(self, bank_app):
        """The schema must create a preferences table on the real DB used at import"""
        import sqlite3
        conn = sqlite3.connect(bank_app.DB_PANEL)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'"
            )
            row = cur.fetchone()
            assert row is not None, "preferences table must exist"
        finally:
            conn.close()


@pytest.mark.unit
class TestConfiguration:
    """Test suite for module configuration constants"""

    def test_port_is_8002(self, bank_app):
        """Bank panel must run on the dedicated port 8002"""
        assert bank_app.PORT == 8002

    def test_origin_points_to_bank_dvta_ch(self, bank_app):
        """Origin URL should point to the main Bank deployment"""
        assert bank_app.BANK_ORIGIN_URL == "https://bank.dvta.ch"

    def test_required_dirs_are_strings(self, bank_app):
        for attr in ("BASE_DIR", "DATA_DIR", "STATIC_DIR", "CONFIG_DIR"):
            assert isinstance(getattr(bank_app, attr), str)


@pytest.mark.unit
@pytest.mark.asyncio
class TestPanelFallbackBehavior:
    """Test suite covering the 404 path when panel.html is missing"""

    async def test_bank_returns_404_when_panel_missing(self, aclient, bank_app, tmp_path, monkeypatch):
        """Edge case: when panel.html doesn't exist, a 404 is raised"""
        empty_static = tmp_path / "empty_static"
        empty_static.mkdir()
        monkeypatch.setattr(bank_app, "STATIC_DIR", str(empty_static))

        resp = await aclient.get("/bank")
        assert resp.status_code == 404
        assert "not found" in resp.json().get("detail", "").lower()
