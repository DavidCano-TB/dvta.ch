"""
Unit tests for the /bank/api/status/batch endpoint and frontend cache system.

Tests cover:
- Batch endpoint returns all game statuses in one response
- Response structure matches expected format
- Frontend cache system is present in index.html
- Performance: batch replaces multiple individual calls

Run:
    python -m pytest tests/test_status_batch.py -v --no-cov
"""
import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent


class TestStatusBatchEndpoint:
    """Test the batch status endpoint in main.py."""

    @pytest.mark.unit
    def test_batch_endpoint_exists_in_main(self):
        """The /bank/api/status/batch route must be defined."""
        content = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert '/bank/api/status/batch' in content

    @pytest.mark.unit
    def test_batch_returns_all_game_keys(self):
        """Batch response must include all expected game/feature keys."""
        content = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Find the batch endpoint function body
        match = re.search(r'async def status_batch\(\).*?return \{(.*?)\}', content, re.DOTALL)
        assert match, "status_batch function not found"
        body = match.group(1)
        expected_keys = ["pasapalabra", "millonario", "quiensoy", "cifrasletras", "hundirlaflota", "cuentos"]
        for key in expected_keys:
            assert f'"{key}"' in body, f"Key '{key}' missing from batch response"

    @pytest.mark.unit
    def test_batch_endpoint_no_auth_required(self):
        """Batch endpoint should not require authentication (public status)."""
        content = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Find the function signature — should NOT have Depends(get_current_user)
        match = re.search(r'async def status_batch\((.*?)\)', content)
        assert match, "status_batch function not found"
        params = match.group(1)
        assert 'get_current_user' not in params, "Batch endpoint should not require auth"


class TestFrontendCacheSystem:
    """Test the frontend API cache system in index.html."""

    @pytest.fixture
    def index_content(self):
        return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_cache_system_defined(self, index_content):
        """The _apiCache object and cachedGet function must exist."""
        assert '_apiCache' in index_content
        assert 'async function cachedGet' in index_content

    @pytest.mark.unit
    def test_cache_uses_session_storage(self, index_content):
        """Cache should persist to sessionStorage for instant boot."""
        assert 'sessionStorage.setItem' in index_content
        assert 'sessionStorage.getItem' in index_content

    @pytest.mark.unit
    def test_cache_has_ttl(self, index_content):
        """Cache entries must have a TTL (time-to-live)."""
        assert '_CACHE_TTL' in index_content
        assert '_cacheIsFresh' in index_content

    @pytest.mark.unit
    def test_req_auto_caches_get(self, index_content):
        """The req() function should auto-cache successful GET responses."""
        assert "_cacheSet(path, d)" in index_content

    @pytest.mark.unit
    def test_batch_call_replaces_individual(self, index_content):
        """loadApp should use _loadStatusBatch instead of 6 individual calls."""
        assert '_loadStatusBatch()' in index_content
        # The old individual calls should NOT be in the Promise.all boot block
        # (they still exist as functions for fallback/toggle, but not in the main boot)
        boot_section = index_content[index_content.find('// Fire status checks'):]
        boot_section = boot_section[:boot_section.find('// Show admin-only panels')]
        assert 'checkGameStatus()' not in boot_section
        assert 'checkMillonarioStatus()' not in boot_section

    @pytest.mark.unit
    def test_batch_function_has_fallback(self, index_content):
        """_loadStatusBatch should fallback to individual calls on error."""
        batch_fn = index_content[index_content.find('async function _loadStatusBatch'):]
        batch_fn = batch_fn[:batch_fn.find('\n/* ──')]
        assert 'checkGameStatus' in batch_fn, "Fallback should call individual status checks"

    @pytest.mark.unit
    def test_stale_while_revalidate_pattern(self, index_content):
        """cachedGet should implement stale-while-revalidate pattern."""
        # Should return stale data immediately while refreshing in background
        assert 'Stale' in index_content or 'stale' in index_content.lower()


class TestPerformanceOptimizations:
    """Test that performance optimizations are in place."""

    @pytest.mark.unit
    def test_gzip_middleware_enabled(self):
        """GZip compression middleware must be active."""
        content = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert 'GZipMiddleware' in content

    @pytest.mark.unit
    def test_service_worker_registered(self):
        """Service worker must be registered in index.html."""
        content = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
        assert "serviceWorker" in content
        assert "sw.js" in content

    @pytest.mark.unit
    def test_font_preconnect(self):
        """Google Fonts should use preconnect for faster loading."""
        content = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
        assert 'rel="preconnect"' in content
        assert 'fonts.googleapis.com' in content
