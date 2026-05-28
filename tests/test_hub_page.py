"""
Unit tests for the dvta.ch Hub page (Task: navigation hub)

Covers:
- hub.html file exists and contains all expected sections/links
- GET / serves hub.html (not a redirect)
- GET /hub serves hub.html (alias)
- GET /exams still works
- GET /health still works
- GET /games proxies to port 8002 (or falls back gracefully)
- GET /social proxies to port 8003 (or falls back gracefully)
- All main module links present in hub.html
- Health-check JS block present in hub.html

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
    static_dir = BASE_DIR / "modules" / "exams" / "static"   # real static dir
    opo_dir    = BASE_DIR / "modules" / "exams" / "opo"       # real opo dir
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
# hub.html static file
# =============================================================================

class TestHubHtmlFile:
    """Verify hub.html exists and contains all required content"""

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

    def test_has_exams_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/exams"' in content

    def test_has_games_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/games"' in content

    def test_has_social_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/social"' in content

    def test_has_opo_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/opo"' in content

    def test_has_health_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'href="/health"' in content

    def test_has_pasapalabra_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/pasapalabra" in content

    def test_has_millonario_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/millonario" in content

    def test_has_quiensoy_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/quiensoy" in content

    def test_has_cifrasletras_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/cifrasletras" in content

    def test_has_hundirlaflota_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/hundirlaflota" in content

    def test_has_apuestas_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/apuestas" in content

    def test_has_votaciones_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/votaciones" in content

    def test_has_messages_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/messages" in content

    def test_has_stats_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/stats" in content

    def test_has_cuentos_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/cuentos" in content

    def test_has_salas_link(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "/bank/salas" in content

    def test_has_health_check_script(self):
        """JS health-check block must be present"""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "checkHealth" in content

    def test_has_health_status_indicators(self):
        """Health dot elements for each service"""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        for svc in ("bank", "exams", "games", "social"):
            assert f"dot-{svc}" in content, f"Missing health dot for {svc}"

    def test_has_responsive_meta(self):
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert 'name="viewport"' in content

    def test_no_broken_template_placeholders(self):
        """No {{ }} or {% %} Jinja-style placeholders left unrendered"""
        content = HUB_HTML_PATH.read_text(encoding="utf-8")
        assert "{{" not in content
        assert "{%" not in content


# =============================================================================
# Routes in app_exams.py
# =============================================================================

class TestHubRoutes:
    """Verify the new routes are registered in the Exams app"""

    def test_root_route_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/" in routes

    def test_hub_route_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/hub" in routes

    def test_games_proxy_route_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/games{path:path}" in routes

    def test_social_proxy_route_registered(self, exams_mod):
        routes = {r.path for r in exams_mod.app.routes}
        assert "/social{path:path}" in routes

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
    """HTTP-level tests for the hub routes"""

    async def test_root_serves_hub_html(self, aclient):
        r = await aclient.get("/")
        assert r.status_code == 200
        assert "DVDcoin Platform" in r.text
        assert "text/html" in r.headers.get("content-type", "")

    async def test_root_is_not_redirect(self, aclient):
        """Root must serve content directly, not redirect to /exams"""
        r = await aclient.get("/", follow_redirects=False)
        assert r.status_code == 200

    async def test_hub_alias_serves_hub_html(self, aclient):
        r = await aclient.get("/hub")
        assert r.status_code == 200
        assert "DVDcoin Platform" in r.text

    async def test_exams_still_works(self, aclient):
        r = await aclient.get("/exams")
        assert r.status_code == 200

    async def test_health_still_works(self, aclient):
        r = await aclient.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "DVDcoin Exams"

    async def test_games_proxy_fallback_when_down(self, aclient):
        """When port 8002 is down, /games should not crash (redirect, 503, or 404 all OK)"""
        r = await aclient.get("/games", follow_redirects=False)
        # Either a redirect to games.dvta.ch, a 503, or a 404 — all are acceptable
        assert r.status_code in (302, 307, 404, 503)

    async def test_social_proxy_fallback_when_down(self, aclient):
        """When port 8003 is down, /social should redirect or return 503 — not crash"""
        r = await aclient.get("/social", follow_redirects=False)
        assert r.status_code in (302, 307, 503)

    async def test_games_proxy_success(self, aclient):
        """When port 8002 responds, /games proxies the response"""
        mock_response = MagicMock()
        mock_response.content = b"<html>Games</html>"
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            r = await aclient.get("/games")
        assert r.status_code == 200
        assert b"Games" in r.content

    async def test_social_proxy_success(self, aclient):
        """When port 8003 responds, /social proxies the response"""
        mock_response = MagicMock()
        mock_response.content = b"<html>Social</html>"
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            r = await aclient.get("/social")
        assert r.status_code == 200
        assert b"Social" in r.content

    async def test_hub_contains_all_main_modules(self, aclient):
        """Hub page must mention all 4 main modules"""
        r = await aclient.get("/")
        assert r.status_code == 200
        for module in ("Bank", "Exams", "Games", "Social"):
            assert module in r.text, f"Module '{module}' not found in hub"

    async def test_hub_contains_game_links(self, aclient):
        """Hub page must contain links to all games"""
        r = await aclient.get("/")
        assert r.status_code == 200
        for path in ("/bank/pasapalabra", "/bank/millonario", "/bank/quiensoy",
                     "/bank/cifrasletras", "/bank/hundirlaflota", "/bank/apuestas"):
            assert path in r.text, f"Game link '{path}' not found in hub"


# =============================================================================
# Markers
# =============================================================================

pytestmark = [pytest.mark.unit]
