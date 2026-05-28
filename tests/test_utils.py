"""
Unit tests for utils (modules/shared/utils.py)
Tests all utility functions with 100% coverage
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add shared modules to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))

from utils import (
    generate_token,
    generate_verification_code,
    hash_password,
    verify_password,
    format_datetime,
    validate_email,
    sanitize_username,
    generate_slug,
)


class TestGenerateToken:
    """Test token generation"""
    
    def test_default_length(self):
        token = generate_token()
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_custom_length(self):
        token = generate_token(length=16)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_uniqueness(self):
        t1 = generate_token()
        t2 = generate_token()
        assert t1 != t2


class TestGenerateVerificationCode:
    """Test verification code generation"""
    
    def test_default_length(self):
        code = generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()
    
    def test_custom_length(self):
        code = generate_verification_code(length=8)
        assert len(code) == 8
        assert code.isdigit()


class TestPassword:
    """Test password hashing/verification"""
    
    def test_hash_password(self):
        hashed = hash_password("MyPassword123")
        assert hashed != "MyPassword123"
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        hashed = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False
    
    def test_verify_password_invalid_hash(self):
        # Should return False on exception
        assert verify_password("password", "not_a_valid_hash") is False


class TestFormatDatetime:
    """Test datetime formatting"""
    
    def test_format_with_datetime(self):
        dt = datetime(2026, 5, 28, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "2026-05-28 14:30:45"
    
    def test_format_without_datetime(self):
        result = format_datetime()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_custom_format(self):
        dt = datetime(2026, 5, 28)
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2026/05/28"


class TestValidateEmail:
    """Test email validation"""
    
    def test_valid_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@example.co.uk") is True
    
    def test_invalid_email(self):
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False


class TestSanitizeUsername:
    """Test username sanitization"""
    
    def test_clean_username(self):
        assert sanitize_username("user_name-123") == "user_name-123"
    
    def test_remove_special_chars(self):
        assert sanitize_username("user@name!") == "username"
    
    def test_remove_spaces(self):
        assert sanitize_username("user name") == "username"


class TestGenerateSlug:
    """Test slug generation"""
    
    def test_simple_text(self):
        assert generate_slug("Hello World") == "hello-world"
    
    def test_with_special_chars(self):
        assert generate_slug("Hello, World!") == "hello-world"
    
    def test_with_multiple_spaces(self):
        assert generate_slug("Hello   World") == "hello-world"
    
    def test_strip_leading_trailing(self):
        assert generate_slug("  Hello World  ") == "hello-world"
