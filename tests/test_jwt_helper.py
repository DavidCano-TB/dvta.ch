"""
Unit tests for JWTHelper (modules/shared/jwt_helper.py)
Tests all JWT operations with 100% coverage
"""
import pytest
import time
from pathlib import Path
import sys
import os
import tempfile

# Add shared modules to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))

from jwt_helper import JWTHelper, load_or_create_secret


class TestJWTHelper:
    """Test suite for JWTHelper class"""
    
    def test_init(self, mock_jwt_secret):
        """Test JWTHelper initialization"""
        helper = JWTHelper(mock_jwt_secret, expire_hours=24)
        assert helper.secret_key == mock_jwt_secret
        assert helper.expire_hours == 24
        assert helper.algorithm == "HS256"
    
    def test_create_token_basic(self, mock_jwt_secret):
        """Test creating a basic token"""
        helper = JWTHelper(mock_jwt_secret)
        token = helper.create_token("testuser")
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_with_extra_claims(self, mock_jwt_secret):
        """Test creating token with extra claims"""
        helper = JWTHelper(mock_jwt_secret)
        extra_claims = {
            "role": "admin",
            "email": "test@example.com",
            "verified": True
        }
        token = helper.create_token("testuser", extra_claims)
        
        payload = helper.decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"
        assert payload["verified"] is True
    
    def test_decode_token_valid(self, mock_jwt_secret):
        """Test decoding a valid token"""
        helper = JWTHelper(mock_jwt_secret)
        token = helper.create_token("testuser", {"role": "free"})
        
        payload = helper.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "free"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_decode_token_invalid(self, mock_jwt_secret):
        """Test decoding an invalid token"""
        helper = JWTHelper(mock_jwt_secret)
        
        # Invalid token format
        payload = helper.decode_token("invalid.token.here")
        assert payload is None
        
        # Empty token
        payload = helper.decode_token("")
        assert payload is None
    
    def test_decode_token_wrong_secret(self, mock_jwt_secret):
        """Test decoding token with wrong secret"""
        helper1 = JWTHelper(mock_jwt_secret)
        token = helper1.create_token("testuser")
        
        helper2 = JWTHelper("different_secret_key")
        payload = helper2.decode_token(token)
        assert payload is None
    
    def test_decode_token_expired(self, mock_jwt_secret):
        """Test decoding an expired token"""
        from datetime import datetime, timedelta
        from jose import jwt as jose_jwt
        
        helper = JWTHelper(mock_jwt_secret, expire_hours=1)
        # Create a token manually with expiration in the past
        past_time = datetime.utcnow() - timedelta(hours=1)
        payload_in = {
            "sub": "testuser",
            "exp": past_time,
            "iat": past_time - timedelta(hours=1)
        }
        token = jose_jwt.encode(payload_in, mock_jwt_secret, algorithm="HS256")
        
        payload = helper.decode_token(token)
        assert payload is None
    
    def test_get_username_valid(self, mock_jwt_secret):
        """Test extracting username from valid token"""
        helper = JWTHelper(mock_jwt_secret)
        token = helper.create_token("testuser")
        
        username = helper.get_username(token)
        assert username == "testuser"
    
    def test_get_username_invalid(self, mock_jwt_secret):
        """Test extracting username from invalid token"""
        helper = JWTHelper(mock_jwt_secret)
        
        username = helper.get_username("invalid.token")
        assert username is None
    
    def test_verify_token_valid(self, mock_jwt_secret):
        """Test verifying a valid token"""
        helper = JWTHelper(mock_jwt_secret)
        token = helper.create_token("testuser")
        
        assert helper.verify_token(token) is True
    
    def test_verify_token_invalid(self, mock_jwt_secret):
        """Test verifying an invalid token"""
        helper = JWTHelper(mock_jwt_secret)
        
        assert helper.verify_token("invalid.token") is False
        assert helper.verify_token("") is False
    
    def test_token_expiration_time(self, mock_jwt_secret):
        """Test that token expiration is set correctly"""
        expire_hours = 48
        helper = JWTHelper(mock_jwt_secret, expire_hours=expire_hours)
        token = helper.create_token("testuser")
        
        payload = helper.decode_token(token)
        exp_time = payload["exp"]
        iat_time = payload["iat"]
        
        # Check that expiration is approximately expire_hours from issued time
        time_diff = exp_time - iat_time
        expected_diff = expire_hours * 3600  # Convert to seconds
        
        # Allow 1 second tolerance
        assert abs(time_diff - expected_diff) < 1


class TestLoadOrCreateSecret:
    """Test suite for load_or_create_secret function"""
    
    def test_create_new_secret(self, temp_dir):
        """Test creating a new secret when file doesn't exist"""
        secret = load_or_create_secret(temp_dir, "jwt_secret.txt")
        
        assert isinstance(secret, str)
        assert len(secret) > 0
        
        # Verify file was created
        secret_path = os.path.join(temp_dir, "jwt_secret.txt")
        assert os.path.exists(secret_path)
        
        # Verify file contains the secret
        with open(secret_path, 'r') as f:
            file_content = f.read().strip()
            assert file_content == secret
    
    def test_load_existing_secret(self, temp_dir):
        """Test loading an existing secret"""
        secret_path = os.path.join(temp_dir, "jwt_secret.txt")
        expected_secret = "existing_secret_key_12345"
        
        # Create secret file
        with open(secret_path, 'w') as f:
            f.write(expected_secret)
        
        # Load secret
        secret = load_or_create_secret(temp_dir, "jwt_secret.txt")
        assert secret == expected_secret
    
    def test_recreate_empty_secret(self, temp_dir):
        """Test recreating secret when file exists but is empty"""
        secret_path = os.path.join(temp_dir, "jwt_secret.txt")
        
        # Create empty file
        with open(secret_path, 'w') as f:
            f.write("")
        
        # Should create new secret
        secret = load_or_create_secret(temp_dir, "jwt_secret.txt")
        assert isinstance(secret, str)
        assert len(secret) > 0
        
        # Verify file was updated
        with open(secret_path, 'r') as f:
            file_content = f.read().strip()
            assert file_content == secret
    
    def test_creates_directory(self, temp_dir):
        """Test that function creates directory if it doesn't exist"""
        config_dir = os.path.join(temp_dir, "config", "subdir")
        secret = load_or_create_secret(config_dir, "jwt_secret.txt")
        
        assert os.path.exists(config_dir)
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_secret_uniqueness(self, temp_dir):
        """Test that generated secrets are unique"""
        secret1 = load_or_create_secret(temp_dir, "secret1.txt")
        secret2 = load_or_create_secret(temp_dir, "secret2.txt")
        
        assert secret1 != secret2
    
    def test_secret_persistence(self, temp_dir):
        """Test that secret persists across multiple loads"""
        secret1 = load_or_create_secret(temp_dir, "jwt_secret.txt")
        secret2 = load_or_create_secret(temp_dir, "jwt_secret.txt")
        secret3 = load_or_create_secret(temp_dir, "jwt_secret.txt")
        
        assert secret1 == secret2 == secret3
