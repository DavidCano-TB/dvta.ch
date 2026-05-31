"""
Unit tests for the dvta.ch Hub page

The hub page (modules/exams/static/hub.html) is a minimal landing page
that links to the main platform modules: Bank and Bulletin Board.

Run:
    python -m pytest tests/test_hub_page.py -v --no-cov
"""
import os
import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import httpx

BASE_DIR = Path(__file__).parent.parent
EXAMS_APP_PATH = BASE_DIR / "modules" / "exams" / "app_exams.py"
HUB_HTML_PATH  = BASE_DIR / "modules" / "exams" / "static" / "hub.html"


# =============================================================================
# Module loader — load app_exams.py in isolation
# =============================================================================

def _load_exams_app(tmp_path, monkeypatch):
    """Load modules/exams/app_exams.py with DB paths redirected to tmp_path."""
    data_dir   = tmp_path / "data"
    config_dir = tmp_path / "config"
    static_dir = BASE_DIR / "modules" / "exams" / "static"
    opo_dir    = BASE_DIR / "modules" / "exams" / "opo"
    data_dir.mkdir()
    config_dir.mkdir()

    # Pre-create JWT secret
    (config_dir / "jwt_secret.txt").write_text("test_jwt_secret_hub_tests_0000000000000000")

    mod_name = f"_exams_app_{tmp_path.name}"
    spec = importlib.util.spec_from_file_location(mod_name, EXAMS_APP_PATH)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    # Redirect DB paths
    monkeypatch.setattr(mod, "DATA_DIR",   str(data_dir))
    monkeypatch.setattr(mod, "CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(mod, "STATIC_DIR", str(static_dir))
    monkeypatch.setattr(mod, "OPO_DIR",    str(opo_dir))
    monkeypatch.setattr(mod, "DB_USERS",   str(data_dir / "users_exams.db"))
    monkeypatch.setattr(mod, "DB_EXAMS",   str(data_dir / "exams.db"))
    monkeypatch.setattr(mod, "DB_OPO",     str(data_dir / "opo.db"))

    return mod


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def exams_mod(tmp_path, monkeypatch):
    return _load_exams_app(tmp_path, monkeypatch)


@pytest.fixture
async def aclient(exams_mod):
    transport = httpx.ASGITransport(app=exams_mod.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# =============================================================================
# hub.html static file tests — matches current simplified hub
# =============================================================================

class TestHubHtmlFile:
    """Verify hub.html exists and contains expected content."""

    def test_file_exists(self):
        assert HUB_HTML_PATH.exists(), "hub.html must exist"

    def test_is_valid_html(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content

    def test_has_title(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "DVDcoin Platform" in content

    def test_has_bank_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/bank"' in content

    def test_has_bulletin_board_link(self):
        """Hub must link to the bulletin board (Anuncios)."""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "Anuncios" in content

    def test_has_bulletin_board_title(self):
        """Hub must show 'Anuncios' as the bulletin board name."""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "Anuncios" in content

    def test_has_responsive_meta(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'name="viewport"' in content

    def test_no_broken_template_placeholders(self):
        """No {{ }} or {% %} Jinja-style placeholders left unrendered."""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "{{" not in content
        assert "{%" not in content

    def test_no_social_section(self):
        """Social section was removed from hub."""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "Videollamadas" not in content
        assert "Mensajes" not in content

    def test_no_stats_section(self):
        """Stats section was removed from hub."""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "Estadísticas" not in content


# =============================================================================
# Routes in app_exams.py
# =============================================================================

class TestHubRoutes:
    """Verify core routes are registered in the Exams app."""

    def test_root_route_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/" in routes

    def test_exams_route_still_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/exams" in routes

    def test_health_route_still_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/health" in routes


# =============================================================================
# HTTP endpoint tests
# =============================================================================

@pytest.mark.asyncio
class TestHubEndpoints:
    """HTTP-level tests for the hub routes."""

    async def test_root_serves_hub_html(self, aclient):
        r = await aclient.get("/")
        assert r.status_code == 200
        assert "DVDcoin Platform" in r.text
        assert "text/html" in r.headers.get("content-type", "")

    async def test_root_is_not_redirect(self, aclient):
        """Root must serve content directly, not redirect."""
        r = await aclient.get("/", follow_redirects=False)
        assert r.status_code == 200

    async def test_exams_still_works(self, aclient):
        r = await aclient.get("/exams")
        assert r.status_code == 200

    async def test_health_still_works(self, aclient):
        r = await aclient.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "DVDcoin Exams"

    async def test_hub_contains_bank(self, aclient):
        """Hub page must mention Bank module."""
        r = await aclient.get("/")
        assert r.status_code == 200
        assert "Bank" in r.text

    async def test_hub_contains_bulletin_board(self, aclient):
        """Hub page must contain bulletin board section."""
        r = await aclient.get("/")
        assert r.status_code == 200
        assert "Anuncios" in r.text


# =============================================================================
# Markers
# =============================================================================

pytestmark = [pytest.mark.unit]
