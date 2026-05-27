"""
Shared Email Service - Reutilizable para todos los módulos
Maneja envío de emails con diferentes proveedores
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio de email configurable para múltiples proveedores"""
    
    def __init__(self, provider: str = "smtp", **config):
        """
        Inicializa el servicio de email
        
        Args:
            provider: Tipo de proveedor (smtp, sendgrid, mailgun)
            **config: Configuración específica del proveedor
        """
        self.provider = provider.lower()
        self.config = config
        self.enabled = config.get('enabled', True)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Envía un email
        
        Args:
            to_email: Email destinatario
            subject: Asunto
            html_content: Contenido HTML
            text_content: Contenido texto plano (opcional)
            from_email: Email remitente (opcional, usa config por defecto)
            from_name: Nombre remitente (opcional)
        
        Returns:
            True si se envió correctamente, False si no
        """
        if not self.enabled:
            logger.warning("Email service is disabled")
            return False
        
        try:
            if self.provider == "smtp":
                return self._send_smtp(to_email, subject, html_content, text_content, from_email, from_name)
            elif self.provider == "sendgrid":
                return self._send_sendgrid(to_email, subject, html_content, text_content, from_email, from_name)
            elif self.provider == "mailgun":
                return self._send_mailgun(to_email, subject, html_content, text_content, from_email, from_name)
            else:
                logger.error(f"Unknown email provider: {self.provider}")
                return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _send_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: Optional[str],
        from_name: Optional[str]
    ) -> bool:
        """Envía email usando SMTP"""
        smtp_host = self.config.get('smtp_host', 'localhost')
        smtp_port = self.config.get('smtp_port', 587)
        smtp_user = self.config.get('smtp_user')
        smtp_pass = self.config.get('smtp_pass')
        use_tls = self.config.get('use_tls', True)
        
        from_email = from_email or self.config.get('from_email', smtp_user)
        from_name = from_name or self.config.get('from_name', 'DVDcoin Platform')
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Añadir contenido
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Email sent to {to_email} via SMTP")
        return True
    
    def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: Optional[str],
        from_name: Optional[str]
    ) -> bool:
        """Envía email usando SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except ImportError:
            logger.error("SendGrid library not installed. Run: pip install sendgrid")
            return False
        
        api_key = self.config.get('api_key')
        if not api_key:
            logger.error("SendGrid API key not configured")
            return False
        
        from_email = from_email or self.config.get('from_email')
        from_name = from_name or self.config.get('from_name', 'DVDcoin Platform')
        
        message = Mail(
            from_email=(from_email, from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"Email sent to {to_email} via SendGrid (status: {response.status_code})")
        return response.status_code in [200, 201, 202]
    
    def _send_mailgun(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: Optional[str],
        from_name: Optional[str]
    ) -> bool:
        """Envía email usando Mailgun API"""
        try:
            import requests
        except ImportError:
            logger.error("Requests library not installed")
            return False
        
        api_key = self.config.get('api_key')
        domain = self.config.get('domain')
        
        if not api_key or not domain:
            logger.error("Mailgun API key or domain not configured")
            return False
        
        from_email = from_email or self.config.get('from_email')
        from_name = from_name or self.config.get('from_name', 'DVDcoin Platform')
        
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"{from_name} <{from_email}>",
                "to": to_email,
                "subject": subject,
                "text": text_content or "",
                "html": html_content
            }
        )
        
        logger.info(f"Email sent to {to_email} via Mailgun (status: {response.status_code})")
        return response.status_code == 200
    
    def send_verification_email(self, to_email: str, username: str, verification_link: str) -> bool:
        """
        Envía email de verificación de cuenta
        
        Args:
            to_email: Email del usuario
            username: Nombre de usuario
            verification_link: Link de verificación
        
        Returns:
            True si se envió correctamente
        """
        subject = "Verifica tu cuenta - DVDcoin Platform"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4A7AB8, #6B9BD4); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #4A7AB8; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Bienvenido a DVDcoin Platform!</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{username}</strong>,</p>
                    <p>Gracias por registrarte en nuestra plataforma. Para activar tu cuenta, por favor verifica tu email haciendo clic en el siguiente botón:</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verificar mi cuenta</a>
                    </p>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; color: #4A7AB8;">{verification_link}</p>
                    <p><strong>Este enlace expira en 24 horas.</strong></p>
                    <p>Si no has creado esta cuenta, puedes ignorar este email.</p>
                </div>
                <div class="footer">
                    <p>© 2026 DVDcoin Platform. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        ¡Bienvenido a DVDcoin Platform!
        
        Hola {username},
        
        Gracias por registrarte. Para activar tu cuenta, verifica tu email visitando:
        {verification_link}
        
        Este enlace expira en 24 horas.
        
        Si no has creado esta cuenta, ignora este email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_link: str) -> bool:
        """
        Envía email de recuperación de contraseña
        
        Args:
            to_email: Email del usuario
            username: Nombre de usuario
            reset_link: Link de reset
        
        Returns:
            True si se envió correctamente
        """
        subject = "Recuperación de contraseña - DVDcoin Platform"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4A7AB8, #6B9BD4); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #4A7AB8; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recuperación de contraseña</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{username}</strong>,</p>
                    <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente botón para crear una nueva:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Restablecer contraseña</a>
                    </p>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; color: #4A7AB8;">{reset_link}</p>
                    <div class="warning">
                        <strong>⚠️ Importante:</strong> Este enlace expira en 1 hora por seguridad.
                    </div>
                    <p>Si no has solicitado este cambio, ignora este email y tu contraseña permanecerá sin cambios.</p>
                </div>
                <div class="footer">
                    <p>© 2026 DVDcoin Platform. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Recuperación de contraseña
        
        Hola {username},
        
        Para restablecer tu contraseña, visita:
        {reset_link}
        
        Este enlace expira en 1 hora.
        
        Si no has solicitado este cambio, ignora este email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


def create_email_service(config_file: str = None) -> EmailService:
    """
    Crea un servicio de email desde configuración
    
    Args:
        config_file: Ruta al archivo de configuración JSON (opcional)
    
    Returns:
        EmailService configurado
    """
    if config_file and os.path.exists(config_file):
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        return EmailService(**config)
    
    # Configuración por defecto (SMTP local para desarrollo)
    return EmailService(
        provider="smtp",
        smtp_host="localhost",
        smtp_port=1025,  # MailHog para desarrollo
        enabled=False  # Deshabilitado por defecto hasta configurar
    )
