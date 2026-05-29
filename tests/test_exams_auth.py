"""
Tests for DVDcoin Exams auth, subscription, and stats endpoints.
Uses HTTP requests against the live server on localhost:8001.
"""
import sys
import os
import json
import http.client
import pytest

BASE_HOST = '127.0.0.1'
BASE_PORT = 8001


def api(method, path, body=None, headers=None, follow_redirects=False):
    """Helper to make HTTP requests to the exams server."""
    c = http.client.HTTPConnection(BASE_HOST, BASE_PORT, timeout=10)
    hdrs = {'Content-Type': 'application/json'}
    if headers:
        hdrs.update(headers)
    c.request(method, path, body=json.dumps(body) if body else None, headers=hdrs)
    r = c.getresponse()
    raw = r.read().decode('utf-8', errors='replace')
    c.close()
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        data = raw
    return r.status, data, dict(r.getheaders())


@pytest.fixture(scope="module")
def registered_user():
    """Register a test user and return credentials."""
    data = {
        "email": "pytest_exams@test.com",
        "username": "pytest_exams",
        "password": "testpass123"
    }
    api('POST', '/api/auth/register', data)
    return data


@pytest.fixture(scope="module")
def auth_token(registered_user):
    """Login and return auth token."""
    status, data, _ = api('POST', '/api/auth/login', {
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    return data.get("token", "") if isinstance(data, dict) else ""


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001. Set EXAMS_SERVER_RUNNING=1 to run."
)
class TestExamsRegistration:
    """Test suite for user registration."""

    def test_register_success(self):
        """Happy path: new user registers."""
        status, data, _ = api('POST', '/api/auth/register', {
            "email": "new_reg_pytest@test.com",
            "username": "new_reg_pytest",
            "password": "pass123456"
        })
        assert status == 200
        assert data["success"] is True

    def test_register_duplicate_email(self, registered_user):
        """Duplicate email rejected."""
        status, data, _ = api('POST', '/api/auth/register', {
            "email": registered_user["email"],
            "username": "another_user_pytest",
            "password": "pass123456"
        })
        assert status == 400

    def test_register_duplicate_username(self, registered_user):
        """Duplicate username rejected."""
        status, data, _ = api('POST', '/api/auth/register', {
            "email": "different_pytest@test.com",
            "username": registered_user["username"],
            "password": "pass123456"
        })
        assert status == 400

    def test_register_invalid_email(self):
        """Invalid email format rejected."""
        status, data, _ = api('POST', '/api/auth/register', {
            "email": "not-an-email",
            "username": "badmail_pytest",
            "password": "pass123456"
        })
        assert status == 422  # Pydantic validation


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsLogin:
    """Test suite for user login."""

    def test_login_success(self, registered_user):
        """Happy path: correct credentials."""
        status, data, _ = api('POST', '/api/auth/login', {
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        assert status == 200
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["username"] == registered_user["username"]

    def test_login_wrong_password(self, registered_user):
        """Wrong password rejected."""
        status, data, _ = api('POST', '/api/auth/login', {
            "username": registered_user["username"],
            "password": "wrongpassword"
        })
        assert status == 401

    def test_login_nonexistent_user(self):
        """Nonexistent user rejected."""
        status, data, _ = api('POST', '/api/auth/login', {
            "username": "ghost_user_xyz",
            "password": "anything"
        })
        assert status == 401


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsMe:
    """Test suite for /api/auth/me endpoint."""

    def test_me_authenticated(self, auth_token):
        """Authenticated user gets their info."""
        status, data, _ = api('GET', '/api/auth/me',
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status == 200
        user = data["user"]
        assert user["username"] == "pytest_exams"
        assert user["verified"] is False
        assert "has_premium" in user

    def test_me_no_token(self):
        """No token returns 401."""
        status, data, _ = api('GET', '/api/auth/me')
        assert status == 401

    def test_me_invalid_token(self):
        """Invalid token returns 401."""
        status, data, _ = api('GET', '/api/auth/me',
                              headers={"Authorization": "Bearer invalid_token_xyz"})
        assert status == 401


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsSubscription:
    """Test suite for subscription endpoints."""

    def test_plans_public(self):
        """Plans endpoint is public."""
        status, data, _ = api('GET', '/api/subscription/plans')
        assert status == 200
        plans = data["plans"]
        assert "monthly" in plans
        assert "quarterly" in plans
        assert "yearly" in plans

    def test_subscription_status_authenticated(self, auth_token):
        """Subscription status for authenticated user."""
        status, data, _ = api('GET', '/api/subscription/status',
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status == 200
        assert data["has_premium"] is False

    def test_subscribe_requires_verification(self, auth_token):
        """Unverified user cannot subscribe."""
        status, data, _ = api('POST', '/api/subscription/subscribe',
                              {"plan": "monthly"},
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status == 403

    def test_subscribe_invalid_plan(self, auth_token):
        """Invalid plan name rejected (after verification check)."""
        status, data, _ = api('POST', '/api/subscription/subscribe',
                              {"plan": "nonexistent"},
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status in (400, 403)


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsStats:
    """Test suite for personal stats."""

    def test_stats_authenticated(self, auth_token):
        """Authenticated user gets stats."""
        status, data, _ = api('GET', '/api/stats/personal',
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status == 200
        assert "overview" in data
        assert data["overview"]["total_exams"] == 0

    def test_stats_no_auth(self):
        """Unauthenticated user rejected."""
        status, data, _ = api('GET', '/api/stats/personal')
        assert status == 401


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsAvailable:
    """Test suite for available exams."""

    def test_exams_list(self, auth_token):
        """Authenticated user gets exam categories."""
        status, data, _ = api('GET', '/api/exams/available',
                              headers={"Authorization": f"Bearer {auth_token}"})
        assert status == 200
        assert "categories" in data
        assert len(data["categories"]) >= 1
        # First category (sanitarias) should be available for free
        sanitarias = next((c for c in data["categories"] if c.get("slug") == "sanitarias"), None)
        if sanitarias:
            assert sanitarias["locked"] is False

    def test_exams_no_auth(self):
        """Unauthenticated user rejected."""
        status, data, _ = api('GET', '/api/exams/available')
        assert status == 401


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsHealth:
    """Test suite for health endpoint."""

    def test_health_returns_200(self):
        """Health check returns 200."""
        status, data, _ = api('GET', '/health')
        assert status == 200
        assert data["status"] == "healthy"

    def test_exams_page_returns_200(self):
        """Exams page returns HTML."""
        status, data, _ = api('GET', '/exams')
        assert status == 200
        assert "DVDcoin Exams" in str(data)


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsVerification:
    """Test suite for email verification."""

    def test_verify_invalid_token(self):
        """Invalid verification token redirects."""
        status, data, headers = api('GET', '/verify?token=invalid_token_xyz')
        assert status in (302, 307)

    def test_verify_missing_token(self):
        """Missing token returns 400."""
        status, data, _ = api('GET', '/verify?token=')
        assert status == 400


@pytest.mark.unit
@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
class TestExamsForgotPassword:
    """Test suite for password reset."""

    def test_forgot_password_success(self, registered_user):
        """Forgot password always returns success (no email leak)."""
        status, data, _ = api('POST', '/api/auth/forgot-password',
                              {"email": registered_user["email"]})
        assert status == 200
        assert data["success"] is True

    def test_forgot_password_unknown_email(self):
        """Unknown email still returns success (security)."""
        status, data, _ = api('POST', '/api/auth/forgot-password',
                              {"email": "unknown@nowhere.com"})
        assert status == 200
        assert data["success"] is True
