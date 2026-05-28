"""
Tests verifying the login system works correctly with the synced database.

These tests verify:
1. The users.db has valid bcrypt hashes for all users
2. The login endpoint works with master password for superadmins
3. The login endpoint returns correct fields
4. The DB sync preserved all users from dvdcoin.db
5. No users have UNSET hashes except known ghost users
"""
from __future__ import annotations

import json
import os
import socket
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent
USERS_DB = BASE_DIR / "data" / "users.db"
DVDCOIN_DB = BASE_DIR / "data" / "dvdcoin.db"
MASTER_FILE = BASE_DIR / "conf" / "master.txt"


def _server_alive(port: int = 8000) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=0.5):
            return True
    except (OSError, socket.timeout):
        return False


@pytest.fixture(scope="module")
def bank_up():
    if not _server_alive(8000) and not _server_alive(8001):
        pytest.skip("No Bank server running on 8000 or 8001")
    return True


@pytest.fixture(scope="module")
def bank_port():
    for port in [8000, 8001]:
        if _server_alive(port):
            return port
    pytest.skip("No Bank server running")


@pytest.fixture(scope="module")
def master_password():
    if not MASTER_FILE.exists():
        pytest.skip("conf/master.txt not found")
    return MASTER_FILE.read_text().strip()


# ---------------------------------------------------------------------------
# Database integrity tests
# ---------------------------------------------------------------------------

class TestDatabaseIntegrity:
    """users.db must have valid hashes for all real users."""

    @pytest.fixture(scope="class")
    def users(self):
        if not USERS_DB.exists():
            pytest.skip("data/users.db not found")
        c = sqlite3.connect(str(USERS_DB))
        c.row_factory = sqlite3.Row
        rows = c.execute("SELECT username, password_hash, balance FROM users").fetchall()
        c.close()
        return [dict(r) for r in rows]

    @pytest.mark.unit
    def test_users_db_exists(self):
        assert USERS_DB.exists(), "data/users.db must exist"

    @pytest.mark.unit
    def test_has_users(self, users):
        assert len(users) > 0, "users.db must have at least one user"

    @pytest.mark.unit
    def test_dvd_has_valid_hash(self, users):
        """dvd must have a valid bcrypt hash."""
        dvd = next((u for u in users if u['username'] == 'dvd'), None)
        assert dvd is not None, "dvd user must exist"
        h = dvd['password_hash']
        assert h.startswith('$2b$') or h.startswith('$2a$'), \
            f"dvd must have valid bcrypt hash, got: {h[:30]}"

    @pytest.mark.unit
    def test_no_invalid_hashes(self, users):
        """All non-ghost users must have valid bcrypt hashes."""
        ghost_users = {'admin'}  # admin is a ghost user, UNSET is expected
        invalid = []
        for u in users:
            h = u['password_hash']
            if u['username'] in ghost_users:
                continue
            if h in ('__UNSET__', '__AUTO__', None, ''):
                invalid.append(u['username'])
            elif not (h.startswith('$2b$') or h.startswith('$2a$')):
                invalid.append(f"{u['username']} (bad hash: {h[:20]})")
        assert not invalid, f"Users with invalid/missing passwords: {invalid}"

    @pytest.mark.unit
    def test_all_dvdcoin_users_migrated(self):
        """All users from dvdcoin.db must be in users.db."""
        if not DVDCOIN_DB.exists():
            pytest.skip("data/dvdcoin.db not found")
        c_old = sqlite3.connect(str(DVDCOIN_DB))
        c_old.row_factory = sqlite3.Row
        old_users = {r['username'] for r in c_old.execute("SELECT username FROM users").fetchall()}
        c_old.close()

        c_new = sqlite3.connect(str(USERS_DB))
        c_new.row_factory = sqlite3.Row
        new_users = {r['username'] for r in c_new.execute("SELECT username FROM users").fetchall()}
        c_new.close()

        missing = old_users - new_users
        assert not missing, f"Users from dvdcoin.db missing in users.db: {missing}"

    @pytest.mark.unit
    def test_balances_synced(self):
        """Balances from dvdcoin.db must be in users.db."""
        if not DVDCOIN_DB.exists():
            pytest.skip("data/dvdcoin.db not found")
        c_old = sqlite3.connect(str(DVDCOIN_DB))
        c_old.row_factory = sqlite3.Row
        old = {r['username']: r['balance'] for r in c_old.execute(
            "SELECT username, balance FROM users WHERE balance > 0"
        ).fetchall()}
        c_old.close()

        c_new = sqlite3.connect(str(USERS_DB))
        c_new.row_factory = sqlite3.Row
        new = {r['username']: r['balance'] for r in c_new.execute(
            "SELECT username, balance FROM users"
        ).fetchall()}
        c_new.close()

        mismatched = []
        for username, old_bal in old.items():
            new_bal = new.get(username, 0)
            if abs(old_bal - new_bal) > 0.01:
                mismatched.append(f"{username}: dvdcoin={old_bal}, users={new_bal}")
        assert not mismatched, f"Balance mismatches: {mismatched}"


# ---------------------------------------------------------------------------
# Live login tests
# ---------------------------------------------------------------------------

class TestLoginLive:
    """Login endpoint must work correctly."""

    @pytest.mark.unit
    def test_master_password_works_for_dvd(self, bank_port, master_password):
        """dvd must be able to login with master password."""
        body = json.dumps({"username": "dvd", "password": master_password}).encode()
        req = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            data = json.loads(r.read())
        assert data["username"] == "dvd"
        assert data["is_admin"] is True
        assert data["is_superadmin"] is True
        assert "token" in data
        assert len(data["token"]) > 20

    @pytest.mark.unit
    def test_master_password_works_for_nebulosa(self, bank_port, master_password):
        """nebulosa must be able to login with master password."""
        body = json.dumps({"username": "nebulosa", "password": master_password}).encode()
        req = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            data = json.loads(r.read())
        assert data["username"] == "nebulosa"
        assert data["is_admin"] is True

    @pytest.mark.unit
    def test_wrong_password_returns_401(self, bank_port):
        """Wrong password must return 401."""
        body = json.dumps({"username": "dvd", "password": "definitely_wrong_xyz"}).encode()
        req = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=10)
        assert exc.value.code == 401

    @pytest.mark.unit
    def test_login_returns_all_required_fields(self, bank_port, master_password):
        """Login response must include all fields the frontend expects."""
        body = json.dumps({"username": "dvd", "password": master_password}).encode()
        req = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        required_fields = ["token", "username", "is_admin", "is_superadmin", "lang"]
        missing = [f for f in required_fields if f not in data]
        assert not missing, f"Login response missing fields: {missing}"

    @pytest.mark.unit
    def test_token_works_on_me_endpoint(self, bank_port, master_password):
        """Token from login must work on /bank/api/me."""
        body = json.dumps({"username": "dvd", "password": master_password}).encode()
        req = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            token = json.loads(r.read())["token"]

        req2 = urllib.request.Request(
            f"http://localhost:{bank_port}/bank/api/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req2, timeout=10) as r:
            me = json.loads(r.read())
        assert me["username"] == "dvd"
        assert me["is_admin"] is True

    @pytest.mark.unit
    def test_login_through_port_8001(self, master_password):
        """Login must work through port 8001 (the Exams/proxy server)."""
        if not _server_alive(8001):
            pytest.skip("Port 8001 not running")
        body = json.dumps({"username": "dvd", "password": master_password}).encode()
        req = urllib.request.Request(
            "http://localhost:8001/bank/api/login",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            data = json.loads(r.read())
        assert data["username"] == "dvd"
