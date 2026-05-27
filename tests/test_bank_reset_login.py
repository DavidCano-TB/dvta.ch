"""
Unit tests for the /bank/reset endpoint and the /bank/api/login routing.

These tests exercise the running Bank server on http://localhost:8000.
If the server isn't running, the tests are skipped so CI / dev runs without
a live backend stay green.

The /bank/reset endpoint serves a self-contained HTML page that helps users
recover from a stale Service Worker (which was the root cause of "the login
button doesn't work" reports). The page unregisters all SWs, clears caches
and storage, then redirects to /bank.

Marker: pytest.mark.unit
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

import pytest


BANK_BASE = "http://localhost:8000"


def _server_alive(host: str = "localhost", port: int = 8000, timeout: float = 0.5) -> bool:
    """Return True if a TCP listener is accepting connections on host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


@pytest.fixture(scope="module")
def bank_running() -> bool:
    """Skip this whole module if the Bank server isn't reachable."""
    if not _server_alive():
        pytest.skip("Bank server not running on localhost:8000")
    return True


# -----------------------------------------------------------------------------
# /bank/reset
# -----------------------------------------------------------------------------

class TestBankResetEndpoint:
    """Test suite for the /bank/reset recovery page."""

    @pytest.mark.unit
    def test_reset_returns_200(self, bank_running):
        """Happy path: /bank/reset responds with HTTP 200."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/reset", timeout=5) as r:
            assert r.status == 200

    @pytest.mark.unit
    def test_reset_is_html(self, bank_running):
        """Content-Type is HTML so the browser renders the recovery page."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/reset", timeout=5) as r:
            ctype = r.headers.get("content-type", "")
            assert "text/html" in ctype.lower()

    @pytest.mark.unit
    def test_reset_no_cache_headers(self, bank_running):
        """The reset page must never be cached — otherwise it can't fix caching."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/reset", timeout=5) as r:
            cc = (r.headers.get("cache-control") or "").lower()
            assert "no-cache" in cc or "no-store" in cc

    @pytest.mark.unit
    def test_reset_contains_recovery_logic(self, bank_running):
        """The page must include the SW unregister + cache clear + storage wipe logic."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/reset", timeout=5) as r:
            body = r.read().decode("utf-8", errors="ignore")
        # Each recovery step must be in the page
        assert "serviceWorker" in body
        assert "unregister" in body
        assert "caches" in body
        assert "localStorage" in body
        # After cleanup it must redirect users back to /bank
        assert "/bank" in body


# -----------------------------------------------------------------------------
# /bank/api/login routing (regression test for "login button doesn't work")
# -----------------------------------------------------------------------------

class TestBankLoginEndpoint:
    """Smoke tests confirming the login route is wired correctly.

    These don't try to authenticate a real user — they only check that the
    endpoint exists, accepts JSON, and returns the documented HTTP semantics.
    """

    @pytest.mark.unit
    def test_login_rejects_unknown_user(self, bank_running):
        """POST with bogus credentials returns 401 Unauthorized."""
        body = json.dumps({"username": "__nope_xyz__", "password": "wrong"}).encode()
        req = urllib.request.Request(
            f"{BANK_BASE}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=5)
        assert exc.value.code == 401

    @pytest.mark.unit
    def test_login_returns_json_error_body(self, bank_running):
        """Error responses are JSON with a 'detail' field (frontend reads d.detail)."""
        body = json.dumps({"username": "__nope_xyz__", "password": "wrong"}).encode()
        req = urllib.request.Request(
            f"{BANK_BASE}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=5)
            pytest.fail("Expected 401")
        except urllib.error.HTTPError as e:
            payload = json.loads(e.read().decode())
            assert "detail" in payload
            assert isinstance(payload["detail"], str)

    @pytest.mark.unit
    def test_login_cors_preflight(self, bank_running):
        """OPTIONS preflight from bank.dvta.ch must succeed for CORS."""
        req = urllib.request.Request(
            f"{BANK_BASE}/bank/api/login",
            method="OPTIONS",
            headers={
                "Origin": "https://bank.dvta.ch",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            assert r.status in (200, 204)
            allow_origin = r.headers.get("access-control-allow-origin", "")
            # CORSMiddleware in main.py uses allow_origins=["*"]
            assert allow_origin in ("*", "https://bank.dvta.ch")

    @pytest.mark.unit
    def test_root_redirects_to_bank(self, bank_running):
        """GET / must redirect to /bank — confirms top-level routing."""
        # urlopen follows redirects by default; final URL should end in /bank
        with urllib.request.urlopen(f"{BANK_BASE}/", timeout=5) as r:
            assert r.status == 200
            assert r.url.rstrip("/").endswith("/bank")

    @pytest.mark.unit
    def test_bank_page_references_login_api(self, bank_running):
        """The HTML served at /bank must reference /bank/api/login.

        Regression guard: if a future refactor changes the API path on the
        backend without updating the frontend (or vice versa) the login button
        silently stops working — this test catches that.
        """
        with urllib.request.urlopen(f"{BANK_BASE}/bank", timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        assert "/bank/api/login" in html
        assert "doLogin" in html
        assert 'id="btnL"' in html


# -----------------------------------------------------------------------------
# Service Worker (sw.js)
# -----------------------------------------------------------------------------

class TestBankServiceWorker:
    """Validate the Service Worker doesn't break login.

    The SW used to call `request.headers.get('accept').includes(...)` which
    crashes when 'accept' is null and made all subsequent fetches fail.
    """

    @pytest.mark.unit
    def test_sw_served_with_correct_content_type(self, bank_running):
        """sw.js must be served as application/javascript."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/static/sw.js", timeout=5) as r:
            assert r.status == 200
            ctype = r.headers.get("content-type", "")
            assert "javascript" in ctype.lower()

    @pytest.mark.unit
    def test_sw_does_not_intercept_non_get_requests(self, bank_running):
        """The SW must early-return on POST/PUT/DELETE so login (POST) is untouched."""
        with urllib.request.urlopen(f"{BANK_BASE}/bank/static/sw.js", timeout=5) as r:
            sw = r.read().decode("utf-8", errors="ignore")
        # Either explicit method check or no fetch handler at all
        assert "request.method" in sw and "GET" in sw, (
            "Service Worker must guard non-GET requests so POST /bank/api/login "
            "is never intercepted."
        )

    @pytest.mark.unit
    def test_sw_safely_reads_accept_header(self, bank_running):
        """The SW must not crash when the Accept header is missing.

        Older versions called `.includes('text/html')` directly on the result
        of `headers.get('accept')` which throws when accept is null.
        """
        with urllib.request.urlopen(f"{BANK_BASE}/bank/static/sw.js", timeout=5) as r:
            sw = r.read().decode("utf-8", errors="ignore")
        # The fix uses a fallback: `headers.get('accept') || ''`
        assert "headers.get('accept') || ''" in sw or 'headers.get("accept") || ""' in sw
