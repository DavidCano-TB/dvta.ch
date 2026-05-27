"""
Unit tests for the DVDcoin Bank Proxy module (modules/bank/app_bank.py)

The Bank service is a reverse proxy to the main Bank (localhost:8000),
giving /bank its own dedicated lifecycle, health probe, and fallback panel.

Tests cover:
- Endpoints: /, /health, /api/info, /bank/panel-fallback
- Reverse proxy behaviour (mocked upstream)
- Fallback when upstream is unreachable
- Header filtering (hop-by-hop)
- DB initialisation

Note: uses httpx.AsyncClient with ASGITransport because the installed
starlette + httpx pair has a TestClient compatibility issue.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))
sys.path.insert(0, str(BASE_DIR / "modules" / "bank"))


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bank_app(tmp_path_factory):
    """Import the bank module fresh so it picks up patched config."""
    tmp_data = tmp_path_factory.mktemp("bank_data")

    bank_module_path = str(BASE_DIR / "modules" / "bank")
    if bank_module_path not in sys.path:
        sys.path.insert(0, bank_module_path)

    if "app_bank" in sys.modules:
        del sys.modules["app_bank"]
    import app_bank  # type: ignore

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
# Unit tests
# -----------------------------------------------------------------------------

@pytest.mark.unit
class TestConfiguration:
    """Module-level constants and configuration."""

    def test_port_is_8002(self, bank_app):
        assert bank_app.PORT == 8002

    def test_origin_points_to_bank_dvta_ch(self, bank_app):
        assert bank_app.BANK_ORIGIN_URL == "https://bank.dvta.ch"

    def test_upstream_default_is_localhost_8000(self, bank_app):
        assert bank_app.BANK_UPSTREAM in ("http://localhost:8000",
                                          os.environ.get("BANK_UPSTREAM", ""))

    def test_required_dirs_are_strings(self, bank_app):
        for attr in ("BASE_DIR", "DATA_DIR", "STATIC_DIR", "CONFIG_DIR"):
            assert isinstance(getattr(bank_app, attr), str)

    def test_hop_by_hop_headers_listed(self, bank_app):
        # Must include critical hop-by-hop entries
        for h in ("connection", "transfer-encoding", "host"):
            assert h in bank_app.HOP_BY_HOP


@pytest.mark.unit
class TestDatabaseInitialization:
    """The schema must create visits + preferences tables on import."""

    def test_visits_table_exists(self, bank_app):
        import sqlite3
        conn = sqlite3.connect(bank_app.DB_PANEL)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='visits'"
            )
            assert cur.fetchone() is not None
        finally:
            conn.close()

    def test_preferences_table_exists(self, bank_app):
        import sqlite3
        conn = sqlite3.connect(bank_app.DB_PANEL)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'"
            )
            assert cur.fetchone() is not None
        finally:
            conn.close()


@pytest.mark.unit
@pytest.mark.asyncio
class TestRootRedirect:
    async def test_root_redirects_to_bank(self, aclient):
        r = await aclient.get("/", follow_redirects=False)
        assert r.status_code in (302, 307)
        assert r.headers["location"] == "/bank"


@pytest.mark.unit
@pytest.mark.asyncio
class TestApiInfo:
    async def test_info_returns_200(self, aclient):
        r = await aclient.get("/api/info")
        assert r.status_code == 200

    async def test_info_payload(self, aclient):
        data = (await aclient.get("/api/info")).json()
        assert data["service"] == "Bank Proxy"
        assert data["port"] == 8002
        assert "available_routes" in data
        assert isinstance(data["available_routes"], list)
        assert len(data["available_routes"]) >= 4


@pytest.mark.unit
@pytest.mark.asyncio
class TestPanelFallbackEndpoint:
    """/bank/panel-fallback always serves the static panel without proxying."""

    async def test_panel_fallback_returns_200(self, aclient):
        r = await aclient.get("/bank/panel-fallback")
        assert r.status_code == 200

    async def test_panel_fallback_has_html(self, aclient):
        r = await aclient.get("/bank/panel-fallback")
        body = r.text
        assert "<html" in body.lower()
        assert "DVDcoin" in body


@pytest.mark.unit
class TestHeaderFiltering:
    """Hop-by-hop headers must not be forwarded."""

    def test_filter_response_headers_strips_hop_by_hop(self, bank_app):
        # Build fake httpx-like headers
        h = httpx.Headers([
            ("content-type", "text/html"),
            ("connection", "keep-alive"),
            ("transfer-encoding", "chunked"),
            ("set-cookie", "x=1"),
        ])
        out = dict(bank_app._filter_response_headers(h))
        assert "content-type" in out
        assert "set-cookie" in out
        assert "connection" not in out
        assert "transfer-encoding" not in out

    def test_filter_request_headers_strips_host(self, bank_app):
        # Build a fake request stub
        class StubURL:
            scheme = "http"
            netloc = "example.com"

        class StubReq:
            headers = {
                "host": "evil.example.com",
                "content-type": "application/json",
                "authorization": "Bearer xyz",
                "connection": "keep-alive",
            }
            client = type("C", (), {"host": "1.2.3.4"})()
            url = StubURL()

        out = bank_app._filter_request_headers(StubReq())
        assert "host" not in {k.lower() for k in out}
        assert "connection" not in {k.lower() for k in out}
        assert "content-type" in out
        assert "authorization" in out
        # X-Forwarded-* must be set
        assert out.get("X-Forwarded-For") == "1.2.3.4"
        assert out.get("X-Forwarded-Proto") == "http"


@pytest.mark.unit
@pytest.mark.asyncio
class TestReverseProxyWithMockedUpstream:
    """Mocks the upstream client to verify proxy semantics without 8000 running."""

    async def test_proxy_forwards_status_and_body(self, aclient, bank_app, monkeypatch):
        # Arrange: replace _client with a mock whose send() returns a fake response
        fake_upstream_response = MagicMock()
        fake_upstream_response.status_code = 200
        fake_upstream_response.headers = {"content-type": "text/plain"}

        async def fake_aiter_raw():
            yield b"hello from upstream"

        fake_upstream_response.aiter_raw = fake_aiter_raw
        fake_upstream_response.aclose = AsyncMock(return_value=None)

        fake_client = MagicMock()
        fake_client.build_request = MagicMock(return_value=MagicMock())
        fake_client.send = AsyncMock(return_value=fake_upstream_response)
        monkeypatch.setattr(bank_app, "_client", fake_client)

        # Act
        r = await aclient.get("/bank/something")

        # Assert
        assert r.status_code == 200
        assert b"hello from upstream" in r.content

    async def test_proxy_handles_connect_error_with_fallback(
        self, aclient, bank_app, monkeypatch
    ):
        """Edge case: when upstream is unreachable, GET /bank serves the fallback panel."""
        fake_client = MagicMock()
        fake_client.build_request = MagicMock(return_value=MagicMock())
        fake_client.send = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )
        monkeypatch.setattr(bank_app, "_client", fake_client)

        r = await aclient.get("/bank")
        # Falls back to the static panel (200 + HTML)
        assert r.status_code == 200
        assert "DVDcoin" in r.text

    async def test_proxy_handles_connect_error_returns_503_for_post(
        self, aclient, bank_app, monkeypatch
    ):
        """Edge case: non-GET request when upstream is down returns 503 JSON."""
        fake_client = MagicMock()
        fake_client.build_request = MagicMock(return_value=MagicMock())
        fake_client.send = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )
        monkeypatch.setattr(bank_app, "_client", fake_client)

        r = await aclient.post("/bank/api/login", json={"u": "x", "p": "y"})
        assert r.status_code == 503
        body = r.json()
        assert body.get("error") == "upstream_unavailable"

    async def test_proxy_handles_timeout_returns_504(
        self, aclient, bank_app, monkeypatch
    ):
        """Edge case: timeout from upstream returns 504."""
        fake_client = MagicMock()
        fake_client.build_request = MagicMock(return_value=MagicMock())
        fake_client.send = AsyncMock(
            side_effect=httpx.TimeoutException("timed out")
        )
        monkeypatch.setattr(bank_app, "_client", fake_client)

        r = await aclient.get("/bank/api/me")
        assert r.status_code == 504
        body = r.json()
        assert body.get("error") == "upstream_timeout"


@pytest.mark.unit
@pytest.mark.asyncio
class TestHealthEndpoint:
    """Health probe must succeed even if upstream is down (just reports it)."""

    async def test_health_returns_200_even_when_upstream_down(
        self, aclient, bank_app, monkeypatch
    ):
        fake_client = MagicMock()
        fake_client.get = AsyncMock(side_effect=httpx.ConnectError("nope"))
        monkeypatch.setattr(bank_app, "_client", fake_client)

        r = await aclient.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["upstream_ok"] is False

    async def test_health_reports_upstream_ok_when_reachable(
        self, aclient, bank_app, monkeypatch
    ):
        fake_resp = MagicMock()
        fake_resp.status_code = 200

        fake_client = MagicMock()
        fake_client.get = AsyncMock(return_value=fake_resp)
        monkeypatch.setattr(bank_app, "_client", fake_client)

        r = await aclient.get("/health")
        data = r.json()
        assert data["upstream_ok"] is True
        assert data["upstream_status"] == 200


@pytest.mark.unit
@pytest.mark.asyncio
class TestPanelFallbackMissing:
    """When STATIC_DIR has no panel.html, the fallback returns 404."""

    async def test_panel_fallback_404_when_missing(
        self, aclient, bank_app, tmp_path, monkeypatch
    ):
        empty = tmp_path / "empty"
        empty.mkdir()
        monkeypatch.setattr(bank_app, "STATIC_DIR", str(empty))
        r = await aclient.get("/bank/panel-fallback")
        assert r.status_code == 404
