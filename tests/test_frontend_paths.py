"""
Regression tests: all API paths, WebSocket paths, and onclick handlers
in static/index.html must be correct.

Bugs fixed:
- 85+ req('/api/...') calls missing /bank prefix → 404 on all game/admin APIs
- 6 template-literal API paths missing /bank prefix
- 6 WebSocket connections using /ws/... instead of /bank/ws/...
- navStats onclick had broken double-quotes inside double-quoted attribute
- i18n fetch used /static/i18n/ instead of /bank/static/i18n/
- mlOpen/ppOpen used /millonario? and /pasapalabra? instead of /bank/...
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent
HTML = BASE_DIR / "static" / "index.html"
MAIN_PY = BASE_DIR / "main.py"


@pytest.fixture(scope="module")
def html():
    return HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def routes():
    """Extract all route paths from main.py."""
    src = MAIN_PY.read_text(encoding="utf-8")
    paths = set()
    for m in re.finditer(r'@app\.(get|post|put|delete|patch|websocket)\("([^"]+)"', src):
        paths.add(m.group(2))
    return paths


# ---------------------------------------------------------------------------
# API path correctness
# ---------------------------------------------------------------------------

class TestApiPaths:
    """All req() calls must use /bank/api/ prefix."""

    @pytest.mark.unit
    def test_no_bare_api_calls(self, html):
        """req('/api/...') without /bank prefix must not exist."""
        # Match req('METHOD', '/api/...) or req("METHOD", "/api/...)
        bad = re.findall(
            r"req\(['\"](?:GET|POST|PUT|DELETE|PATCH)['\"],\s*['\"]\/api\/",
            html
        )
        assert not bad, f"Found {len(bad)} req() calls with bare /api/ prefix: {bad[:5]}"

    @pytest.mark.unit
    def test_no_bare_template_api_calls(self, html):
        """Template literal API calls must also use /bank/api/ prefix."""
        # Find backtick strings starting with /api/
        bad = re.findall(r"`/api/", html)
        assert not bad, f"Found {len(bad)} template literal calls with bare /api/ prefix"

    @pytest.mark.unit
    def test_no_bare_fetch_api_calls(self, html):
        """Direct fetch('/api/...') calls must not exist."""
        bad = re.findall(r"fetch\(['\"`]/api/", html)
        assert not bad, f"Found {len(bad)} direct fetch() calls with bare /api/ prefix"

    @pytest.mark.unit
    def test_i18n_uses_bank_prefix(self, html):
        """i18n JSON files must be fetched from /bank/static/i18n/."""
        assert "/bank/static/i18n/" in html
        assert "fetch(`/static/i18n/" not in html
        assert 'fetch("/static/i18n/' not in html
        assert "fetch('/static/i18n/" not in html

    @pytest.mark.unit
    def test_refresh_token_uses_bank_prefix(self, html):
        """Token refresh must call /bank/api/me/refresh-token."""
        assert "/bank/api/me/refresh-token" in html
        # Old wrong path must not appear
        assert "'/api/me/refresh-token'" not in html
        assert '"/api/me/refresh-token"' not in html


# ---------------------------------------------------------------------------
# WebSocket path correctness
# ---------------------------------------------------------------------------

class TestWebSocketPaths:
    """All WebSocket connections must use /bank/ws/ prefix."""

    @pytest.mark.unit
    def test_no_bare_ws_connections(self, html):
        """new WebSocket(...'/ws/...') without /bank prefix must not exist."""
        bad = re.findall(r"new WebSocket\([^)]*['\"`]/ws/", html)
        assert not bad, f"Found {len(bad)} WebSocket connections with bare /ws/ prefix: {bad}"

    @pytest.mark.unit
    def test_pasapalabra_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/pasapalabra" in html

    @pytest.mark.unit
    def test_millonario_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/millonario" in html

    @pytest.mark.unit
    def test_cifrasletras_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/cifrasletras" in html

    @pytest.mark.unit
    def test_video_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/video" in html

    @pytest.mark.unit
    def test_rooms_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/rooms" in html

    @pytest.mark.unit
    def test_messages_ws_uses_bank_prefix(self, html):
        assert "/bank/ws/messages" in html


# ---------------------------------------------------------------------------
# onclick handler correctness
# ---------------------------------------------------------------------------

class TestOnclickHandlers:
    """Every onclick="foo()" must have a matching function definition."""

    @pytest.fixture(scope="class")
    def onclick_funcs(self, html):
        """Extract all function names called in onclick attributes."""
        funcs = set()
        for m in re.finditer(r'onclick="([a-zA-Z_$][a-zA-Z0-9_$]*)\(', html):
            funcs.add(m.group(1))
        return funcs

    @pytest.fixture(scope="class")
    def defined_funcs(self, html):
        """Extract all function definitions."""
        funcs = set()
        for m in re.finditer(r'(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', html):
            funcs.add(m.group(1))
        # Also catch arrow functions assigned to const/let/var
        for m in re.finditer(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?\(', html):
            funcs.add(m.group(1))
        return funcs

    @pytest.mark.unit
    def test_all_onclick_functions_defined(self, html, onclick_funcs, defined_funcs):
        """Every function called in onclick must be defined in the same file."""
        # Some are browser built-ins
        builtins = {'window', 'location', 'confirm', 'alert', 'open'}
        missing = []
        for fn in onclick_funcs:
            if fn not in defined_funcs and fn not in builtins:
                missing.append(fn)
        assert not missing, f"onclick functions not defined: {missing}"

    @pytest.mark.unit
    def test_navstats_onclick_valid_quotes(self, html):
        """navStats onclick must use valid HTML attribute quoting."""
        # The broken version had onclick="window.location.href="/bank/stats""
        assert 'onclick="window.location.href="/bank/stats""' not in html
        # The fixed version uses single quotes inside
        assert "onclick=\"window.location.href='/bank/stats'\"" in html

    @pytest.mark.unit
    def test_dologin_defined(self, html):
        """doLogin must be defined — this was the root cause of the login bug."""
        assert "async function doLogin()" in html or "function doLogin()" in html

    @pytest.mark.unit
    def test_doreg_defined(self, html):
        assert "async function doReg()" in html or "function doReg()" in html


# ---------------------------------------------------------------------------
# Game window.open paths
# ---------------------------------------------------------------------------

class TestGameOpenPaths:
    """window.open() for games must use /bank/ prefix."""

    @pytest.mark.unit
    def test_millonario_open_uses_bank_prefix(self, html):
        assert "open('/bank/millonario?" in html or 'open("/bank/millonario?' in html
        assert "open('/millonario?" not in html

    @pytest.mark.unit
    def test_pasapalabra_open_uses_bank_prefix(self, html):
        assert "open('/bank/pasapalabra?" in html or 'open("/bank/pasapalabra?' in html
        assert "open('/pasapalabra?" not in html


# ---------------------------------------------------------------------------
# Route existence checks (cross-reference frontend vs backend)
# ---------------------------------------------------------------------------

class TestRouteExistence:
    """Key API routes called by the frontend must exist in main.py."""

    REQUIRED_ROUTES = [
        "/bank/api/login",
        "/bank/api/register",
        "/bank/api/me",
        "/bank/api/me/refresh-token",
        "/bank/api/transfer",
        "/bank/api/history",
        "/bank/api/users",
        "/bank/api/ping",
        "/bank/api/admin/users",
        "/bank/api/admin/activity",
        "/bank/api/admin/ledger",
        "/bank/api/cuentos/status",
        "/bank/api/pasapalabra/status",
        "/bank/api/millonario/status",
        "/bank/api/quiensoy/status",
        "/bank/api/cifrasletras/status",
        "/bank/api/hundirlaflota/status",
        "/bank/api/rooms/status",
        "/bank/api/rooms/active",
        "/bank/ws/pasapalabra",
        "/bank/ws/millonario",
        "/bank/ws/cifrasletras",
        "/bank/ws/video",
        "/bank/ws/rooms",
        "/bank/ws/messages",
    ]

    @pytest.mark.unit
    def test_required_routes_exist(self, routes):
        """All routes called by the frontend must be defined in main.py."""
        missing = [r for r in self.REQUIRED_ROUTES if r not in routes]
        assert not missing, f"Routes missing from main.py: {missing}"
