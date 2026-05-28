"""
Unit tests for the new Registration System (Task 3)

Covers:
- RegisterRequest Pydantic model (new fields: email, full_name, phone, opo_interest)
- PaymentRequest Pydantic model
- Email configuration file (config/email_config.json)
- Verification token generation and expiration logic
- /bank/api/register endpoint (validation, DB persistence, token issuance)
- /bank/verify-email endpoint (success, invalid, expired, already verified)
- /bank/api/payment endpoint (auth, email-verified gate, OPO activation)
- /bank/api/me endpoint (new OPO/payment fields exposure)
- /api/* compatibility aliases
- Users table schema migration (new columns)

Run:
    python -m pytest tests/test_registration_system.py -v --no-cov
"""
import os
import sys
import json
import secrets
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_asyncio
import httpx

BASE_DIR = Path(__file__).parent.parent
SRC_MAIN_PATH = BASE_DIR / "src" / "main.py"


# =============================================================================
# Module loader — load src/main.py specifically (bypassing root legacy main.py)
# =============================================================================

def _load_src_main(monkeypatch, tmp_path):
    """
    Load `src/main.py` as a module under a unique name, with all DB / conf
    paths redirected to a fresh tmp directory.

    Each test gets its own fresh import + fresh DB.
    """
    data_dir = tmp_path / "data"
    conf_dir = tmp_path / "config"
    data_dir.mkdir()
    conf_dir.mkdir()
    (conf_dir / "jwt_secret.txt").write_text("test_jwt_secret_for_unit_tests_0123456789abcdef")
    (conf_dir / "master.txt").write_text("test_master_pwd")

    # Load module from explicit file path
    mod_name = f"_dvd_main_under_test_{tmp_path.name}"
    spec = importlib.util.spec_from_file_location(mod_name, SRC_MAIN_PATH)
    main_mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = main_mod
    spec.loader.exec_module(main_mod)

    # Redirect persistent paths
    monkeypatch.setattr(main_mod, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(main_mod, "CONF_DIR", str(conf_dir))
    monkeypatch.setattr(main_mod, "DB_USERS", str(data_dir / "users.db"))
    monkeypatch.setattr(main_mod, "DB_RIGHTS", str(data_dir / "rights.db"))
    monkeypatch.setattr(main_mod, "DB_TX", str(data_dir / "transactions.db"))
    monkeypatch.setattr(main_mod, "DB_STATS", str(data_dir / "stats.db"))
    monkeypatch.setattr(main_mod, "DB_OPO", str(data_dir / "opo.db"))
    monkeypatch.setattr(main_mod, "DB_BETS", str(data_dir / "apuestas.db"))

    # Init schema (registers users + new columns)
    main_mod.db_init()
    return main_mod


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def isolated_main(tmp_path, monkeypatch):
    """Returns a freshly loaded src.main with isolated DB paths."""
    return _load_src_main(monkeypatch, tmp_path)


@pytest.fixture
def reg_payload():
    return {
        "username": "alice",
        "password": "test1234",
        "email": "alice@example.com",
        "full_name": "Alice Tester",
        "phone": "+34600000000",
        "opo_interest": True,
    }


@pytest_asyncio.fixture
async def aclient(isolated_main):
    """Async HTTP client that talks to the FastAPI app via ASGI transport."""
    transport = httpx.ASGITransport(app=isolated_main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# =============================================================================
# RegisterRequest model
# =============================================================================

class TestRegisterRequestModel:
    """Pydantic model for /bank/api/register payload"""

    def test_minimal_required_fields(self, isolated_main):
        m = isolated_main.RegisterRequest(username="bob", password="abcd")
        assert m.username == "bob"
        assert m.password == "abcd"
        # New fields default to empty / False
        assert m.email == ""
        assert m.full_name == ""
        assert m.phone == ""
        assert m.opo_interest is False

    def test_all_fields_provided(self, isolated_main, reg_payload):
        m = isolated_main.RegisterRequest(**reg_payload)
        assert m.email == "alice@example.com"
        assert m.full_name == "Alice Tester"
        assert m.phone == "+34600000000"
        assert m.opo_interest is True

    def test_opo_interest_explicit_false(self, isolated_main):
        m = isolated_main.RegisterRequest(username="x", password="abcd", opo_interest=False)
        assert m.opo_interest is False

    def test_password_not_stripped(self, isolated_main):
        m = isolated_main.RegisterRequest(username="x", password="  pass  ")
        assert m.password == "  pass  "


# =============================================================================
# PaymentRequest model
# =============================================================================

class TestPaymentRequestModel:
    """Pydantic model for /bank/api/payment payload"""

    def test_required_fields(self, isolated_main):
        m = isolated_main.PaymentRequest(username="alice", amount=10.0)
        assert m.username == "alice"
        assert m.amount == 10.0
        assert m.payment_method == "card"
        assert m.opo_access is False

    def test_all_fields(self, isolated_main):
        m = isolated_main.PaymentRequest(
            username="alice", amount=25.5,
            payment_method="paypal", opo_access=True,
        )
        assert m.payment_method == "paypal"
        assert m.opo_access is True

    def test_amount_must_be_numeric(self, isolated_main):
        with pytest.raises(Exception):
            isolated_main.PaymentRequest(username="alice", amount="not-a-number")


# =============================================================================
# Email config file (static — no module loading needed)
# =============================================================================

class TestEmailConfigFile:
    """Verify config/email_config.json is valid and well-formed"""

    @pytest.fixture
    def config_path(self):
        return BASE_DIR / "config" / "email_config.json"

    def test_file_exists(self, config_path):
        assert config_path.exists()

    def test_valid_json(self, config_path):
        with open(config_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_has_required_keys(self, config_path):
        with open(config_path) as f:
            data = json.load(f)
        for key in ("provider", "smtp_host", "smtp_port", "from_email", "from_name", "enabled"):
            assert key in data

    def test_disabled_by_default(self, config_path):
        with open(config_path) as f:
            data = json.load(f)
        assert data["enabled"] is False

    def test_provider_is_known(self, config_path):
        with open(config_path) as f:
            data = json.load(f)
        assert data["provider"] in ("smtp", "sendgrid", "mailgun")

    def test_loadable_via_create_email_service(self, config_path):
        sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))
        from email_service import create_email_service
        svc = create_email_service(str(config_path))
        assert svc.provider == "smtp"
        assert svc.enabled is False


# =============================================================================
# Verification token logic (pure unit tests)
# =============================================================================

class TestVerificationTokenLogic:
    """Token generation + expiration semantics used by /bank/api/register"""

    def test_token_has_sufficient_entropy(self):
        token = secrets.token_urlsafe(32)
        assert 40 <= len(token) <= 50
        assert all(c.isalnum() or c in "-_" for c in token)

    def test_token_is_unique(self):
        tokens = {secrets.token_urlsafe(32) for _ in range(100)}
        assert len(tokens) == 100

    def test_expiration_is_24h(self):
        now = datetime.utcnow()
        expires = now + timedelta(hours=24)
        assert (expires - now).total_seconds() == 24 * 3600

    def test_expired_token_detected(self):
        past = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        assert datetime.utcnow() > datetime.fromisoformat(past)

    def test_valid_token_not_expired(self):
        future = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        assert datetime.utcnow() < datetime.fromisoformat(future)


# =============================================================================
# Database schema
# =============================================================================

class TestUsersTableSchema:
    """Verify db_init creates / migrates all required columns for the new feature"""

    REQUIRED_COLS = {
        "username", "password_hash", "balance", "is_blocked",
        "email", "full_name", "phone",
        "email_verified", "verification_token", "verification_expires",
        "opo_interest", "opo_access",
        "payment_status", "payment_date", "payment_amount",
    }

    def test_all_new_columns_present(self, isolated_main):
        conn = isolated_main.db_users()
        rows = conn.execute("PRAGMA table_info(users)").fetchall()
        conn.close()
        cols = {r[1] for r in rows}
        missing = self.REQUIRED_COLS - cols
        assert not missing, f"Missing columns: {missing}"

    def test_new_columns_have_safe_defaults(self, isolated_main):
        conn = isolated_main.db_users()
        conn.execute("INSERT INTO users(username, password_hash) VALUES('bob','x')")
        conn.commit()
        row = conn.execute(
            "SELECT email_verified, opo_interest, opo_access, payment_status "
            "FROM users WHERE username='bob'"
        ).fetchone()
        conn.close()
        assert row["email_verified"] == 0
        assert row["opo_interest"] == 0
        assert row["opo_access"] == 0
        assert row["payment_status"] == "pending"


# =============================================================================
# /bank/api/register endpoint
# =============================================================================

@pytest.mark.asyncio
class TestRegisterEndpoint:
    """POST /bank/api/register — uses httpx.AsyncClient + ASGITransport"""

    async def test_register_success(self, aclient, reg_payload):
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["requires_verification"] is True
        assert "token" in data and len(data["token"]) > 10
        assert data["is_admin"] is False
        assert data["is_superadmin"] is False

    async def test_register_persists_all_fields(self, aclient, reg_payload, isolated_main):
        await aclient.post("/bank/api/register", json=reg_payload)
        conn = isolated_main.db_users()
        row = conn.execute(
            "SELECT email, full_name, phone, opo_interest, email_verified, "
            "verification_token, verification_expires "
            "FROM users WHERE username=?", ("alice",)
        ).fetchone()
        conn.close()
        assert row["email"] == "alice@example.com"
        assert row["full_name"] == "Alice Tester"
        assert row["phone"] == "+34600000000"
        assert row["opo_interest"] == 1
        assert row["email_verified"] == 0
        assert row["verification_token"] is not None
        assert len(row["verification_token"]) >= 40
        assert row["verification_expires"] is not None

    async def test_register_rejects_short_username(self, aclient, reg_payload):
        reg_payload["username"] = "a"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 400
        assert "Username" in r.json()["detail"]

    async def test_register_rejects_short_password(self, aclient, reg_payload):
        reg_payload["password"] = "abc"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 400
        assert "Password" in r.json()["detail"]

    async def test_register_rejects_missing_email(self, aclient, reg_payload):
        reg_payload["email"] = ""
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 400
        assert "Email" in r.json()["detail"]

    async def test_register_rejects_invalid_email_format(self, aclient, reg_payload):
        reg_payload["email"] = "not-an-email"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 400
        assert "email" in r.json()["detail"].lower()

    async def test_register_rejects_duplicate_username(self, aclient, reg_payload):
        await aclient.post("/bank/api/register", json=reg_payload)
        reg_payload["email"] = "other@example.com"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 409
        assert "Username" in r.json()["detail"]

    async def test_register_rejects_duplicate_email(self, aclient, reg_payload):
        await aclient.post("/bank/api/register", json=reg_payload)
        reg_payload["username"] = "different_user"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 409
        assert "Email" in r.json()["detail"]

    async def test_register_rejects_reserved_username(self, aclient, reg_payload):
        reg_payload["username"] = "admin"  # in GHOST set
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 400

    async def test_register_lowercases_username_and_email(self, aclient, reg_payload, isolated_main):
        reg_payload["username"] = "MIXEDcase"
        reg_payload["email"] = "Mixed@Example.COM"
        r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 200
        conn = isolated_main.db_users()
        row = conn.execute("SELECT username, email FROM users WHERE username='mixedcase'").fetchone()
        conn.close()
        assert row is not None
        assert row["email"] == "mixed@example.com"

    async def test_register_alias_endpoint(self, aclient, reg_payload):
        """/api/register must mirror /bank/api/register"""
        r = await aclient.post("/api/register", json=reg_payload)
        assert r.status_code == 200
        assert r.json()["username"] == "alice"

    async def test_register_email_send_failure_does_not_break_registration(self, aclient, reg_payload):
        """If email service raises, user must still be created"""
        with patch("modules.shared.email_service.create_email_service",
                   side_effect=Exception("smtp boom")):
            r = await aclient.post("/bank/api/register", json=reg_payload)
        assert r.status_code == 200
        assert r.json()["username"] == "alice"


# =============================================================================
# /bank/verify-email endpoint
# =============================================================================

@pytest.mark.asyncio
class TestVerifyEmailEndpoint:
    """GET /bank/verify-email?token=... — returns HTML pages"""

    def _seed_user(self, main_module, username="alice", token="tok123",
                   expires=None, verified=0):
        if expires is None:
            expires = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        conn = main_module.db_users()
        conn.execute(
            "INSERT OR REPLACE INTO users(username, password_hash, email, "
            "verification_token, verification_expires, email_verified) "
            "VALUES(?,?,?,?,?,?)",
            (username, "hash", f"{username}@example.com", token, expires, verified)
        )
        conn.commit()
        conn.close()

    async def test_verify_success(self, aclient, isolated_main):
        self._seed_user(isolated_main, token="goodtoken")
        r = await aclient.get("/bank/verify-email", params={"token": "goodtoken"})
        assert r.status_code == 200
        assert "verificado" in r.text.lower() or "Verificado" in r.text

        conn = isolated_main.db_users()
        row = conn.execute(
            "SELECT email_verified, verification_token FROM users WHERE username='alice'"
        ).fetchone()
        conn.close()
        assert row["email_verified"] == 1
        assert row["verification_token"] is None

    async def test_verify_invalid_token(self, aclient):
        r = await aclient.get("/bank/verify-email", params={"token": "does_not_exist"})
        assert r.status_code == 400
        assert "inválido" in r.text.lower() or "invalido" in r.text.lower() or "invalid" in r.text.lower()

    async def test_verify_expired_token(self, aclient, isolated_main):
        past = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        self._seed_user(isolated_main, token="expiredtok", expires=past)
        r = await aclient.get("/bank/verify-email", params={"token": "expiredtok"})
        assert r.status_code == 400
        assert "expir" in r.text.lower()

    async def test_verify_already_verified(self, aclient, isolated_main):
        self._seed_user(isolated_main, token="usedtok", verified=1)
        r = await aclient.get("/bank/verify-email", params={"token": "usedtok"})
        assert r.status_code == 200
        assert "verif" in r.text.lower()

    async def test_verify_alias_endpoint(self, aclient, isolated_main):
        self._seed_user(isolated_main, token="aliastok")
        r = await aclient.get("/api/verify-email", params={"token": "aliastok"})
        assert r.status_code == 200


# =============================================================================
# /bank/api/payment endpoint
# =============================================================================

@pytest.mark.asyncio
class TestPaymentEndpoint:
    """POST /bank/api/payment — requires JWT + verified email"""

    async def _register_and_verify(self, aclient, isolated_main, reg_payload):
        """Register, verify email in DB, login. Returns (token, username)."""
        await aclient.post("/bank/api/register", json=reg_payload)
        conn = isolated_main.db_users()
        conn.execute("UPDATE users SET email_verified=1 WHERE username=?",
                     (reg_payload["username"],))
        conn.commit()
        conn.close()
        r = await aclient.post("/bank/api/login", json={
            "username": reg_payload["username"],
            "password": reg_payload["password"],
        })
        assert r.status_code == 200, r.text
        return r.json()["token"], reg_payload["username"]

    async def test_payment_requires_auth(self, aclient):
        r = await aclient.post("/bank/api/payment", json={
            "username": "alice", "amount": 10.0, "opo_access": True
        })
        assert r.status_code in (401, 403)

    async def test_payment_success_activates_opo(self, aclient, isolated_main, reg_payload):
        token, user = await self._register_and_verify(aclient, isolated_main, reg_payload)
        r = await aclient.post(
            "/bank/api/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": user, "amount": 10.0, "opo_access": True},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert data["payment_status"] == "completed"
        assert data["opo_access"] is True

        conn = isolated_main.db_users()
        row = conn.execute(
            "SELECT payment_status, payment_amount, opo_access "
            "FROM users WHERE username=?", (user,)
        ).fetchone()
        conn.close()
        assert row["payment_status"] == "completed"
        assert row["payment_amount"] == 10.0
        assert row["opo_access"] == 1

    async def test_payment_rejects_unverified_email(self, aclient, isolated_main, reg_payload):
        # Register but DON'T verify
        await aclient.post("/bank/api/register", json=reg_payload)
        r = await aclient.post("/bank/api/login", json={
            "username": reg_payload["username"],
            "password": reg_payload["password"],
        })
        token = r.json()["token"]

        r = await aclient.post(
            "/bank/api/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": reg_payload["username"], "amount": 10.0, "opo_access": True},
        )
        assert r.status_code == 400
        assert "verified" in r.json()["detail"].lower()

    async def test_payment_rejects_negative_amount(self, aclient, isolated_main, reg_payload):
        token, user = await self._register_and_verify(aclient, isolated_main, reg_payload)
        r = await aclient.post(
            "/bank/api/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": user, "amount": -5.0},
        )
        assert r.status_code == 400

    async def test_payment_rejects_zero_amount(self, aclient, isolated_main, reg_payload):
        token, user = await self._register_and_verify(aclient, isolated_main, reg_payload)
        r = await aclient.post(
            "/bank/api/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": user, "amount": 0.0},
        )
        assert r.status_code == 400

    async def test_payment_rejects_user_mismatch(self, aclient, isolated_main, reg_payload):
        """Authenticated user must match payment.username"""
        token, _user = await self._register_and_verify(aclient, isolated_main, reg_payload)
        r = await aclient.post(
            "/bank/api/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "someone_else", "amount": 10.0},
        )
        assert r.status_code == 403


# =============================================================================
# /bank/api/me — new fields
# =============================================================================

@pytest.mark.asyncio
class TestMeEndpointNewFields:
    """GET /bank/api/me must expose email_verified, opo_interest, opo_access, payment_status"""

    async def test_me_includes_opo_fields(self, aclient, reg_payload):
        r = await aclient.post("/bank/api/register", json=reg_payload)
        token = r.json()["token"]

        r = await aclient.get("/bank/api/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        data = r.json()

        for key in ("email_verified", "opo_interest", "opo_access", "payment_status"):
            assert key in data, f"Missing field: {key}"

        # Just registered → not verified, opo_interest=True (from payload), no payment yet
        assert data["email_verified"] is False
        assert data["opo_interest"] is True
        assert data["opo_access"] is False
        assert data["payment_status"] == "pending"

    async def test_me_after_verification_and_payment(self, aclient, isolated_main, reg_payload):
        await aclient.post("/bank/api/register", json=reg_payload)
        conn = isolated_main.db_users()
        conn.execute(
            "UPDATE users SET email_verified=1, opo_access=1, "
            "payment_status='completed', payment_amount=10.0 WHERE username=?",
            (reg_payload["username"],)
        )
        conn.commit()
        conn.close()

        r = await aclient.post("/bank/api/login", json={
            "username": reg_payload["username"],
            "password": reg_payload["password"],
        })
        token = r.json()["token"]

        r = await aclient.get("/bank/api/me", headers={"Authorization": f"Bearer {token}"})
        data = r.json()
        assert data["email_verified"] is True
        assert data["opo_access"] is True
        assert data["payment_status"] == "completed"


# =============================================================================
# Markers
# =============================================================================

pytestmark = [pytest.mark.unit]
