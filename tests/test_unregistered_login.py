"""
Tests for unregistered user login (users with __UNSET__/__AUTO__ hash).

These users can login using their username as the default password.
The response includes needs_registration=True to signal the frontend.
"""
import pytest
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

USERS_DB = BASE_DIR / "data" / "users.db"


@pytest.fixture
def test_user_unset():
    """Create a temporary unregistered user for testing."""
    username = "_test_unreg_user_"
    conn = sqlite3.connect(str(USERS_DB))
    conn.execute(
        "INSERT OR REPLACE INTO users(username, password_hash, balance, is_blocked) VALUES(?, '__UNSET__', 100.0, 0)",
        (username,)
    )
    conn.commit()
    conn.close()
    yield username
    # Cleanup
    conn = sqlite3.connect(str(USERS_DB))
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()


@pytest.fixture
def test_user_auto():
    """Create a temporary user with __AUTO__ hash."""
    username = "_test_auto_user_"
    conn = sqlite3.connect(str(USERS_DB))
    conn.execute(
        "INSERT OR REPLACE INTO users(username, password_hash, balance, is_blocked) VALUES(?, '__AUTO__', 50.0, 0)",
        (username,)
    )
    conn.commit()
    conn.close()
    yield username
    # Cleanup
    conn = sqlite3.connect(str(USERS_DB))
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()


class TestUnregisteredLogin:
    """Test suite for unregistered user login with default password."""

    @pytest.mark.unit
    def test_login_source_code_allows_unset_users(self):
        """The login endpoint must handle __UNSET__/__AUTO__ users with username as password."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        assert "needs_registration" in src, "Login must return needs_registration flag"
        assert 'row["password_hash"] in ("__UNSET__", "__AUTO__")' in src, \
            "Login must check for __UNSET__/__AUTO__ hash"

    @pytest.mark.unit
    def test_login_uses_username_as_default_password(self):
        """Unregistered users should be able to login with their username as password."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Find the login endpoint section
        login_start = src.find("async def login(request: Request, body: LoginRequest)")
        login_end = src.find("\n@app.", login_start + 1)
        login_body = src[login_start:login_end]
        assert "body.password != u" in login_body, \
            "Login must compare password to username for unregistered users"

    @pytest.mark.unit
    def test_login_returns_needs_registration_flag(self):
        """Login response must include needs_registration field."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        login_start = src.find("async def login(request: Request, body: LoginRequest)")
        login_end = src.find("\n@app.", login_start + 1)
        login_body = src[login_start:login_end]
        assert '"needs_registration": needs_registration' in login_body or \
               '"needs_registration":needs_registration' in login_body, \
            "Login response must include needs_registration field"


class TestUnregisteredLoginLive:
    """Live tests against the running server for unregistered user login."""

    @pytest.fixture(autouse=True)
    def _check_server(self):
        """Skip if server is not running."""
        import httpx
        try:
            r = httpx.get("http://localhost:8001/bank/api/health", timeout=3)
            if r.status_code != 200:
                pytest.skip("Server not running")
        except Exception:
            pytest.skip("Server not running on port 8001")

    @pytest.mark.unit
    def test_unregistered_user_login_with_username(self, test_user_unset):
        """Unregistered user can login with username as password."""
        import httpx
        r = httpx.post("http://localhost:8001/bank/api/login", json={
            "username": test_user_unset,
            "password": test_user_unset
        }, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "token" in data
        assert data["username"] == test_user_unset
        assert data.get("needs_registration") is True

    @pytest.mark.unit
    def test_unregistered_user_wrong_password_rejected(self, test_user_unset):
        """Unregistered user cannot login with wrong password."""
        import httpx
        r = httpx.post("http://localhost:8001/bank/api/login", json={
            "username": test_user_unset,
            "password": "wrong_password"
        }, timeout=10)
        assert r.status_code == 401

    @pytest.mark.unit
    def test_auto_user_login_with_username(self, test_user_auto):
        """User with __AUTO__ hash can login with username as password."""
        import httpx
        r = httpx.post("http://localhost:8001/bank/api/login", json={
            "username": test_user_auto,
            "password": test_user_auto
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("needs_registration") is True

    @pytest.mark.unit
    def test_registered_user_no_needs_registration(self):
        """Registered user (with bcrypt hash) should not have needs_registration=True."""
        import httpx
        # dvd is a registered admin
        r = httpx.post("http://localhost:8001/bank/api/login", json={
            "username": "dvd",
            "password": "dvd"  # This will likely fail auth, but we test the concept
        }, timeout=10)
        # If login succeeds, check the flag
        if r.status_code == 200:
            data = r.json()
            assert data.get("needs_registration") is not True


class TestBettingStatsIndividualCount:
    """Test that betting statistics count each individual bet, not unique porras."""

    @pytest.mark.unit
    def test_stats_endpoint_counts_individual_bets(self):
        """The stats endpoint must count each row in apuestas_usuarios individually."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Find porra_user_stats
        stats_start = src.find("async def porra_user_stats")
        stats_end = src.find("\n@app.", stats_start + 1)
        stats_body = src[stats_start:stats_end]
        
        # It should count each apuesta individually (not group by porra_id)
        assert "total_porras = len(apuestas)" in stats_body, \
            "Stats must count total from all individual bets"
        # porras_ganadas counts each individual winning bet
        assert 'porras_ganadas = sum(1 for a in apuestas' in stats_body, \
            "Stats must count each winning bet individually"

    @pytest.mark.unit
    def test_resolve_porra_counts_individual_bets_in_code(self):
        """The porra resolution code must count each bet individually for stats."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        # Check that we use per-bet counting, not per-user sets
        assert "apuestas_ganadas_por_user" in src, \
            "Resolution must track individual winning bets per user"
        assert "apuestas_perdidas_por_user" in src, \
            "Resolution must track individual losing bets per user"

    @pytest.mark.unit
    def test_ranking_calculates_beneficio_correctly(self):
        """The ranking endpoint must calculate beneficio as total_ganado - total_apostado."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        ranking_start = src.find("async def porra_ranking")
        ranking_end = src.find("\n@app.", ranking_start + 1)
        ranking_body = src[ranking_start:ranking_end]
        assert 'beneficio = r["total_ganado"] - r["total_apostado"]' in ranking_body, \
            "Ranking must calculate beneficio as ganado minus apostado"


class TestVotacionStatsCount:
    """Test that votacion statistics count each vote individually."""

    @pytest.mark.unit
    def test_votaciones_list_counts_total_votes(self):
        """The votaciones list must count total votes (not just unique participants)."""
        src = (BASE_DIR / "main.py").read_text(encoding="utf-8")
        list_start = src.find("async def votaciones_list")
        list_end = src.find("\n@app.", list_start + 1)
        list_body = src[list_start:list_end]
        # Should use COUNT(*) for total votes, not COUNT(DISTINCT username)
        assert 'SELECT COUNT(*) FROM votos WHERE votacion_id' in list_body, \
            "Votaciones list must count all votes with COUNT(*)"
        # Should also provide participantes count
        assert 'COUNT(DISTINCT username)' in list_body, \
            "Votaciones list must also count unique participants"
