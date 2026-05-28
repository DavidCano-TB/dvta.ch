# 📧 Configurar Email para Exams (info@dvta.ch)

## Estado Actual

El sistema de registro con verificación por email está **completamente implementado**:

1. ✅ Usuario se registra con email + username + password
2. ✅ Se genera un token de verificación (expira en 24h)
3. ✅ Se envía email desde `info@dvta.ch` con link de verificación
4. ✅ El usuario hace clic en `https://dvta.ch/verify?token=...`
5. ✅ La cuenta se activa (`verified=1`)

**Lo que falta:** Configurar las credenciales del proveedor de email.

---

## Configuración

Edita el archivo `modules/exams/config/email.json`:

### Opción 1: Mailgun (Recomendado para dvta.ch)

```json
{
  "provider": "mailgun",
  "enabled": true,
  "api_key": "TU_API_KEY_DE_MAILGUN",
  "domain": "dvta.ch",
  "from_email": "info@dvta.ch",
  "from_name": "DVDcoin Exams"
}
```

**Pasos para configurar Mailgun:**
1. Crear cuenta en https://www.mailgun.com
2. Añadir dominio `dvta.ch`
3. Configurar DNS en Cloudflare (MX, TXT para SPF/DKIM)
4. Obtener API key
5. Pegar en `email.json`
6. Cambiar `"enabled": true`

### Opción 2: SendGrid

```json
{
  "provider": "sendgrid",
  "enabled": true,
  "api_key": "SG.TU_API_KEY_DE_SENDGRID",
  "from_email": "info@dvta.ch",
  "from_name": "DVDcoin Exams"
}
```

### Opción 3: SMTP (Gmail, Outlook, etc.)

```json
{
  "provider": "smtp",
  "enabled": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "tu_email@gmail.com",
  "smtp_pass": "tu_app_password",
  "use_tls": true,
  "from_email": "info@dvta.ch",
  "from_name": "DVDcoin Exams"
}
```

---

## Flujo de Registro

```
Usuario → POST /api/auth/register (email, username, password)
  ↓
Servidor → Crea usuario con verified=0
  ↓
Servidor → Envía email desde info@dvta.ch con link:
           https://dvta.ch/verify?token=XXXXX
  ↓
Usuario → Hace clic en el link del email
  ↓
Servidor → GET /verify?token=XXXXX
  ↓
Servidor → Marca verified=1, redirige a /exams?verified=success
```

---

## Verificar que Funciona

1. Configura `email.json` con credenciales reales
2. Reinicia el servidor Exams
3. Registra un usuario de prueba en https://dvta.ch/exams
4. Verifica que llega el email a la bandeja de entrada
5. Haz clic en el link de verificación
6. Confirma que la cuenta se activa

---

## DNS Necesarios en Cloudflare (para Mailgun)

Añadir en Cloudflare Dashboard → dvta.ch → DNS:

| Tipo | Nombre | Valor |
|------|--------|-------|
| TXT | @ | `v=spf1 include:mailgun.org ~all` |
| TXT | mailo._domainkey | (proporcionado por Mailgun) |
| MX | @ | `mxa.mailgun.org` (prioridad 10) |
| MX | @ | `mxb.mailgun.org` (prioridad 10) |
| CNAME | email.dvta.ch | `mailgun.org` |

---

## Archivo de Configuración

Ubicación: `modules/exams/config/email.json`

**IMPORTANTE:** Este archivo contiene credenciales. Está en `.gitignore` para no subirlo a GitHub.
