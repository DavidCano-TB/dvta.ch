import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid

HOST = "mail.infomaniak.com"
PORT = 587
USER = "info@dvta.ch"
PASS = "Nocturna1234567890"
TO = "davidcano.ch@gmail.com"

# Build a proper email with all anti-spam headers
msg = MIMEMultipart("alternative")
msg["Subject"] = "DVDcoin - Verificacion de cuenta"
msg["From"] = formataddr(("DVDcoin Platform", USER))
msg["To"] = TO
msg["Date"] = formatdate(localtime=True)
msg["Message-ID"] = make_msgid(domain="dvta.ch")
msg["Reply-To"] = USER
msg["X-Mailer"] = "DVDcoin Platform 1.0"

text = "Hola! Este es un email de prueba de DVDcoin Platform (dvta.ch). Si lo recibes, el sistema funciona."
html = """<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px">
<div style="max-width:500px;margin:0 auto;background:#fff;border-radius:10px;padding:30px;border:1px solid #ddd">
<h2 style="color:#4A7AB8;margin-bottom:15px">DVDcoin Platform</h2>
<p>Hola,</p>
<p>Este es un email de prueba del sistema de verificacion de <strong>dvta.ch</strong>.</p>
<p>Si recibes este mensaje, el envio de emails funciona correctamente.</p>
<hr style="border:none;border-top:1px solid #eee;margin:20px 0">
<p style="color:#888;font-size:12px">DVDcoin Platform - dvta.ch</p>
</div></body></html>"""

msg.attach(MIMEText(text, "plain"))
msg.attach(MIMEText(html, "html"))

try:
    print(f"Connecting to {HOST}:{PORT}...")
    with smtplib.SMTP(HOST, PORT, timeout=15) as s:
        s.starttls()
        s.login(USER, PASS)
        print("Authenticated OK")
        s.send_message(msg)
        print(f"SENT to {TO}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
