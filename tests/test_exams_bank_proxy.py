"""
Unit tests for the /bank reverse-proxy in modules/exams/app_exams.py.

The route `/bank{path:path}` in the Exams service (port 8001) must
proxy to the Bank service so that https://dvta.ch/bank shows the
exact same UI as https://bank.dvta.ch (the dvdcoin index.html).

Strategy:
1. Smoke tests against the live Exams server when reachable.
2. If the server is not reachable, the suite is skipped (CI / dev
   without a live backend stays green).

Marker: pytest.mark.unit
"""
from __future__ import annotations

import socket
import urllib.request
import urllib.error

import pytest


EXAMS_BASE = "http://localhost:8001"


def _server_alive() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 8001), timeout=1.5):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def exams_running() -> bool:
    """Skip suite if Exams server isn't reachable on localhost:8001."""
    if not _server_alive():
        pytest.skip("Exams server not running on localhost:8001")
    return True


# -----------------------------------------------------------------------------
# /bank should serve the dvdcoin index.html via the Bank reverse proxy
# -----------------------------------------------------------------------------
class TestBankReverseProxy:
    """Test suite for the Exams /bank reverse-proxy."""

    @pytest.mark.unit
    def test_bank_returns_200_with_html(self, exams_running):
        """Happy path: /bank responds with HTTP 200 and HTML."""
        with urllib.request.urlopen(f"{EXAMS_BASE}/bank", timeout=20) as r:
            assert r.status == 200
            ctype = r.headers.get("content-type", "").lower()
            assert "text/html" in ctype

    @pytest.mark.unit
    def test_bank_serves_dvdcoin_index_html(self, exams_running):
        """The body served at /bank must be the dvdcoin Bank index.html.

        Regression guard: confirms the proxy is not silently
        falling back to a redirect or to a different page.
        """
        with urllib.request.urlopen(f"{EXAMS_BASE}/bank", timeout=20) as r:
            body = r.read().decode("utf-8", errors="ignore")

        # Hallmarks of static/index.html (DVDcoin Bank UI)
        assert "DVDcoin Bank" in body, "page title from index.html missing"
        assert "/bank/api/login" in body, "login API reference missing"
        # The dvdcoin index.html is large — sanity-check the size
        assert len(body) > 100_000, (
            f"unexpectedly small body ({len(body)} bytes); "
            "proxy probably returned a fallback page"
        )

    @pytest.mark.unit
    def test_bank_login_api_is_proxied(self, exams_running):
        """POST /bank/api/login through the Exams proxy must hit the real
        Bank backend and return its JSON 401 for bogus credentials.
        """
        import json

        body = json.dumps(
            {"username": "__nope_xyz__", "password": "wrong"}
        ).encode()
        req = urllib.request.Request(
            f"{EXAMS_BASE}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            pytest.fail("expected HTTPError 401 for bogus credentials")
        except urllib.error.HTTPError as e:
            assert e.code == 401
            payload = e.read().decode("utf-8", errors="ignore")
            # FastAPI HTTPException returns {"detail": "..."}
            assert "detail" in payload.lower()

    @pytest.mark.unit
    def test_bank_static_assets_are_proxied(self, exams_running):
        """A static asset under /bank/static/* must be reachable via Exams.

        index.html references /bank/static/sw.js; if the proxy doesn't
        forward static assets, the page would render but be unstyled
        and JS-broken.
        """
        try:
            with urllib.request.urlopen(
                f"{EXAMS_BASE}/bank/static/sw.js", timeout=10
            ) as r:
                assert r.status == 200
                ctype = r.headers.get("content-type", "").lower()
                # Service workers must be served as JavaScript
                assert "javascript" in ctype or "ecmascript" in ctype
        except urllib.error.HTTPError as e:  # pragma: no cover
            pytest.fail(f"/bank/static/sw.js should be 200, got {e.code}")
