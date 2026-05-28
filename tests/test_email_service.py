"""
Unit tests for EmailService (modules/shared/email_service.py)
Tests all email operations with 100% coverage
"""
import pytest
import json
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add shared modules to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))

from email_service import EmailService, create_email_service


class TestEmailService:
    """Test suite for EmailService class"""
    
    def test_init_smtp(self):
        """Test EmailService initialization with SMTP"""
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=587,
            enabled=True
        )
        
        assert service.provider == "smtp"
        assert service.config["smtp_host"] == "localhost"
        assert service.config["smtp_port"] == 587
        assert service.enabled is True
    
    def test_init_sendgrid(self):
        """Test EmailService initialization with SendGrid"""
        service = EmailService(
            provider="sendgrid",
            api_key="test_key",
            enabled=True
        )
        
        assert service.provider == "sendgrid"
        assert service.config["api_key"] == "test_key"
    
    def test_init_mailgun(self):
        """Test EmailService initialization with Mailgun"""
        service = EmailService(
            provider="mailgun",
            api_key="test_key",
            domain="test.com",
            enabled=True
        )
        
        assert service.provider == "mailgun"
        assert service.config["api_key"] == "test_key"
        assert service.config["domain"] == "test.com"
    
    def test_send_email_disabled(self):
        """Test that sending email when disabled returns False"""
        service = EmailService(provider="smtp", enabled=False)
        
        result = service.send_email(
            "test@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_smtp_success(self, mock_smtp):
        """Test successful SMTP email sending"""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_pass="password",
            from_email="from@example.com",
            from_name="Test Sender",
            use_tls=True,
            enabled=True
        )
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>",
            "Test Text"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_smtp_no_auth(self, mock_smtp):
        """Test SMTP sending without authentication"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=25,
            use_tls=False,
            enabled=True
        )
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        assert result is True
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_not_called()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_smtp_failure(self, mock_smtp):
        """Test SMTP sending failure"""
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
        
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=587,
            enabled=True
        )
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        assert result is False
    
    def test_send_unknown_provider(self):
        """Test sending with unknown provider"""
        service = EmailService(provider="unknown", enabled=True)
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_verification_email(self, mock_smtp):
        """Test sending verification email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=587,
            from_email="noreply@dvta.ch",
            enabled=True
        )
        
        result = service.send_verification_email(
            "user@example.com",
            "testuser",
            "https://dvta.ch/verify?token=abc123"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Verify the message was constructed and sent
        call_args = mock_server.send_message.call_args
        msg = call_args[0][0]
        assert msg["To"] == "user@example.com"
        assert "DVDcoin" in msg["From"]
    
    @patch('smtplib.SMTP')
    def test_send_password_reset_email(self, mock_smtp):
        """Test sending password reset email"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            provider="smtp",
            smtp_host="localhost",
            smtp_port=587,
            from_email="noreply@dvta.ch",
            enabled=True
        )
        
        result = service.send_password_reset_email(
            "user@example.com",
            "testuser",
            "https://dvta.ch/reset?token=xyz789"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Verify the message was constructed and sent
        call_args = mock_server.send_message.call_args
        msg = call_args[0][0]
        assert msg["To"] == "user@example.com"
        assert "DVDcoin" in msg["From"]
    
    def test_send_sendgrid_no_library(self):
        """Test SendGrid via send_email - exceptions are caught"""
        service = EmailService(
            provider="sendgrid",
            api_key="invalid_key",
            from_email="from@example.com",
            enabled=True
        )
        
        # Use send_email which has try/except wrapper
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        # Should return False due to invalid key / network / library issues
        assert result is False
    
    def test_send_via_sendgrid_provider(self):
        """Test send_email routing to sendgrid provider"""
        service = EmailService(
            provider="sendgrid",
            api_key="test_api_key",
            enabled=True
        )
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        # Library not installed, should return False
        assert result is False
    
    def test_send_via_mailgun_provider(self):
        """Test send_email routing to mailgun provider"""
        service = EmailService(
            provider="mailgun",
            enabled=True
        )
        
        result = service.send_email(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>"
        )
        
        # Missing config, returns False
        assert result is False
    
    def test_send_sendgrid_no_api_key(self):
        """Test SendGrid without API key"""
        service = EmailService(provider="sendgrid", enabled=True)
        
        result = service._send_sendgrid(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>",
            None,
            None,
            None
        )
        
        assert result is False
    
    def test_send_sendgrid_with_mock(self):
        """Test SendGrid with mocked library to cover success path"""
        # Create mock module structure
        mock_sg_module = MagicMock()
        mock_helpers_module = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 202
        mock_sg_instance = Mock()
        mock_sg_instance.send.return_value = mock_response
        mock_sg_module.SendGridAPIClient.return_value = mock_sg_instance
        
        with patch.dict('sys.modules', {
            'sendgrid': mock_sg_module,
            'sendgrid.helpers.mail': mock_helpers_module
        }):
            service = EmailService(
                provider="sendgrid",
                api_key="test_key",
                from_email="from@example.com",
                enabled=True
            )
            result = service._send_sendgrid(
                "to@example.com",
                "Test Subject",
                "<p>Test HTML</p>",
                "Test Text",
                "from@example.com",
                "Test Sender"
            )
        
        assert result is True
    
    @patch('requests.post')
    def test_send_mailgun_success(self, mock_post):
        """Test successful Mailgun email sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        service = EmailService(
            provider="mailgun",
            api_key="test_api_key",
            domain="test.com",
            from_email="from@example.com",
            enabled=True
        )
        
        result = service._send_mailgun(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>",
            "Test Text",
            "from@example.com",
            "Test Sender"
        )
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_mailgun_failure(self, mock_post):
        """Test Mailgun sending failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        service = EmailService(
            provider="mailgun",
            api_key="test_api_key",
            domain="test.com",
            from_email="from@example.com",
            enabled=True
        )
        
        result = service._send_mailgun(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>",
            None,
            None,
            None
        )
        
        assert result is False
    
    def test_send_mailgun_no_config(self):
        """Test Mailgun without required configuration"""
        service = EmailService(provider="mailgun", enabled=True)
        
        result = service._send_mailgun(
            "to@example.com",
            "Test Subject",
            "<p>Test HTML</p>",
            None,
            None,
            None
        )
        
        assert result is False


class TestCreateEmailService:
    """Test suite for create_email_service function"""
    
    def test_create_from_config_file(self, temp_dir):
        """Test creating email service from config file"""
        config_file = os.path.join(temp_dir, "email.json")
        config = {
            "provider": "smtp",
            "smtp_host": "mail.example.com",
            "smtp_port": 587,
            "smtp_user": "user@example.com",
            "smtp_pass": "password",
            "enabled": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        service = create_email_service(config_file)
        
        assert isinstance(service, EmailService)
        assert service.provider == "smtp"
        assert service.config["smtp_host"] == "mail.example.com"
        assert service.enabled is True
    
    def test_create_without_config_file(self):
        """Test creating email service without config file"""
        service = create_email_service("/nonexistent/config.json")
        
        assert isinstance(service, EmailService)
        assert service.provider == "smtp"
        assert service.enabled is False  # Default is disabled
    
    def test_create_with_none(self):
        """Test creating email service with None config"""
        service = create_email_service(None)
        
        assert isinstance(service, EmailService)
        assert service.provider == "smtp"
        assert service.enabled is False
