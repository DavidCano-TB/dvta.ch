"""
Pytest configuration and shared fixtures for DVDcoin Platform tests
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add modules to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))
sys.path.insert(0, str(BASE_DIR / "modules" / "exams"))


@pytest.fixture
def temp_db():
    """Create a temporary database file"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config_dir(temp_dir):
    """Create a mock config directory"""
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir(exist_ok=True)
    return str(config_dir)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "role": "free"
    }


@pytest.fixture
def sample_admin_data():
    """Sample admin data for testing"""
    return {
        "email": "admin@example.com",
        "username": "dvd",
        "password": "AdminPassword123!",
        "role": "admin"
    }


@pytest.fixture
def mock_jwt_secret():
    """Mock JWT secret for testing"""
    return "test_secret_key_for_jwt_tokens_12345678"


@pytest.fixture
def mock_email_config():
    """Mock email configuration for testing"""
    return {
        "provider": "smtp",
        "smtp_host": "localhost",
        "smtp_port": 1025,
        "smtp_user": "test@example.com",
        "smtp_pass": "testpass",
        "from_email": "noreply@dvta.ch",
        "from_name": "DVDcoin Test",
        "enabled": False  # Disabled for tests
    }
