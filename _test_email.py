"""Test email sending directly."""
import sys, os, logging
logging.basicConfig(level=logging.DEBUG)

sys.path.insert(0, r'c:\dvdcoin\modules\shared')
sys.path.insert(0, r'c:\dvdcoin\modules\exams')

from email_service import create_email_service

config_path = r'c:\dvdcoin\modules\exams\config\email.json'
print(f"Config exists: {os.path.exists(config_path)}")

svc = create_email_service(config_path)
print(f"Provider: {svc.provider}")
print(f"Enabled: {svc.enabled}")
print(f"SMTP host: {svc.config.get('smtp_host')}")
print(f"SMTP user: {svc.config.get('smtp_user')}")
print()

# Try sending a test email
result = svc.send_verification_email(
    "davidcano.ch@gmail.com",
    "test_user",
    "https://dvta.ch/verify?token=TEST123"
)
print(f"\nSend result: {result}")
