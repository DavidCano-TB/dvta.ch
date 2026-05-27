# 🚀 Referencia Rápida - Sistema de Registro

## 📋 Campos del Formulario

| Campo | Tipo | Obligatorio | Validación |
|-------|------|-------------|------------|
| Usuario | text | ✅ | 2-30 caracteres, único |
| Email | email | ✅ | Formato válido, único |
| Contraseña | password | ✅ | Mínimo 4 caracteres |
| Confirmar Contraseña | password | ✅ | Debe coincidir |
| Nombre Completo | text | ❌ | - |
| Teléfono | tel | ❌ | - |
| Interés en OPO | checkbox | ❌ | - |
| Términos | checkbox | ✅ | Debe aceptar |

---

## 🔌 Endpoints API

### Registro
```http
POST /bank/api/register
Content-Type: application/json

{
  "username": "usuario",
  "password": "contraseña",
  "email": "email@example.com",
  "full_name": "Nombre Completo",
  "phone": "+34600000000",
  "opo_interest": true
}

Response 200:
{
  "token": "jwt_token",
  "username": "usuario",
  "email": "email@example.com",
  "requires_verification": true,
  "message": "Cuenta creada. Por favor verifica tu email..."
}
```

### Verificación de Email
```http
GET /bank/verify-email?token=<verification_token>

Response: Página HTML de confirmación
```

### Pago
```http
POST /bank/api/payment
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "username": "usuario",
  "amount": 10.0,
  "payment_method": "card",
  "opo_access": true
}

Response 200:
{
  "success": true,
  "message": "Pago procesado exitosamente",
  "payment_status": "completed",
  "opo_access": true
}
```

### Perfil de Usuario
```http
GET /bank/api/me
Authorization: Bearer <jwt_token>

Response 200:
{
  "username": "usuario",
  "balance": 100.0,
  "is_admin": false,
  "email_verified": true,
  "opo_interest": true,
  "opo_access": true,
  "payment_status": "completed"
}
```

---

## 🗄️ Campos de Base de Datos

### Tabla: users

```sql
-- Campos nuevos añadidos
email           TEXT                    -- Email del usuario
full_name       TEXT                    -- Nombre completo
phone           TEXT                    -- Teléfono
email_verified  INTEGER DEFAULT 0       -- 0=No, 1=Sí
verification_token TEXT                 -- Token de verificación
verification_expires TEXT               -- Fecha de expiración
opo_interest    INTEGER DEFAULT 0       -- Interés en OPO
opo_access      INTEGER DEFAULT 0       -- Acceso pagado
payment_status  TEXT DEFAULT 'pending'  -- Estado del pago
payment_date    TEXT                    -- Fecha del pago
payment_amount  REAL DEFAULT 0.0        -- Monto pagado
```

---

## 💻 Comandos SQL Útiles

### Ver usuario
```sql
SELECT username, email, email_verified, opo_interest, opo_access, payment_status 
FROM users 
WHERE username='usuario';
```

### Verificar email manualmente
```sql
UPDATE users 
SET email_verified=1, verification_token=NULL, verification_expires=NULL 
WHERE username='usuario';
```

### Activar acceso OPO
```sql
UPDATE users 
SET opo_access=1, payment_status='completed', 
    payment_date=datetime('now'), payment_amount=10.0
WHERE username='usuario';
```

### Ver todos los usuarios con OPO
```sql
SELECT username, email, opo_interest, opo_access, payment_status 
FROM users 
WHERE opo_interest=1 OR opo_access=1;
```

### Limpiar usuario de prueba
```sql
DELETE FROM users WHERE username='testuser';
```

---

## 📧 Configuración de Email

### Archivo: `config/email_config.json`

#### MailHog (Desarrollo)
```json
{
  "provider": "smtp",
  "smtp_host": "localhost",
  "smtp_port": 1025,
  "use_tls": false,
  "from_email": "noreply@dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

#### Gmail
```json
{
  "provider": "smtp",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "tu-email@gmail.com",
  "smtp_pass": "app-password-aqui",
  "use_tls": true,
  "from_email": "tu-email@gmail.com",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

#### SendGrid
```json
{
  "provider": "sendgrid",
  "api_key": "SG.xxxxx",
  "from_email": "noreply@dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

---

## 🧪 Testing con cURL

### Registrar usuario
```bash
curl -X POST http://localhost:8000/bank/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test1234",
    "email": "test@example.com",
    "full_name": "Test User",
    "phone": "+34600000000",
    "opo_interest": true
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/bank/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test1234"
  }'
```

### Obtener perfil
```bash
curl -X GET http://localhost:8000/bank/api/me \
  -H "Authorization: Bearer <token>"
```

### Procesar pago
```bash
curl -X POST http://localhost:8000/bank/api/payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "username": "testuser",
    "amount": 10.0,
    "payment_method": "card",
    "opo_access": true
  }'
```

---

## 🔍 Debugging

### Ver logs del servidor
```bash
# El servidor muestra logs en la consola
# Buscar líneas como:
INFO dvdcoin: Register: testuser (email: test@example.com, opo_interest: True)
INFO dvdcoin: Email verified for user: testuser
INFO dvdcoin: Payment processed for user testuser: $10.0 (OPO access: True)
```

### Verificar base de datos
```bash
sqlite3 src/data/users.db
.schema users
SELECT * FROM users WHERE username='testuser';
.quit
```

### Verificar configuración de email
```bash
cat config/email_config.json
# Verificar que "enabled": true
```

---

## ⚡ Atajos de Desarrollo

### Crear usuario de prueba completo
```sql
INSERT INTO users (
  username, password_hash, email, full_name, phone,
  email_verified, opo_interest, opo_access, 
  payment_status, payment_amount
) VALUES (
  'testuser',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF6k5K3u', -- "test1234"
  'test@example.com',
  'Test User',
  '+34600000000',
  1,  -- email verificado
  1,  -- interés en OPO
  1,  -- acceso OPO
  'completed',
  10.0
);
```

### Resetear usuario
```sql
UPDATE users 
SET email_verified=0, 
    opo_access=0, 
    payment_status='pending',
    payment_amount=0.0
WHERE username='testuser';
```

---

## 🎯 Flujo Rápido de Testing

1. **Iniciar servidor:** `python src/main.py`
2. **Abrir:** http://localhost:8000/bank
3. **Registrar:** Completar formulario
4. **Verificar DB:** `sqlite3 src/data/users.db`
5. **Verificar email:** `UPDATE users SET email_verified=1 WHERE username='testuser';`
6. **Login:** Usar credenciales
7. **Verificar OPO:** Debe aparecer pestaña 📚

---

## 📱 Frontend - Funciones JavaScript

### Registro
```javascript
async function doReg() {
  // Validaciones
  // POST /bank/api/register
  // Manejo de respuesta
}
```

### Mostrar pestaña OPO
```javascript
// En loadApp()
if (me.opo_interest || me.opo_access) {
  document.getElementById('navOpo')?.classList.remove('hidden');
}
```

### Abrir OPO
```javascript
function openOpo() {
  const t = localStorage.getItem('dvd_token');
  window.location.href = t ? '/opo?token=' + encodeURIComponent(t) : '/opo';
}
```

---

## 🔐 Seguridad

### Tokens de Verificación
- **Generación:** `secrets.token_urlsafe(32)`
- **Expiración:** 24 horas
- **Uso único:** Se elimina después de verificar

### Contraseñas
- **Hash:** bcrypt
- **Mínimo:** 4 caracteres (aumentar en producción)

### JWT
- **Algoritmo:** HS256
- **Expiración:** 168 horas (1 semana)
- **Cookie:** HTTP-only, SameSite=Lax

### Rate Limiting
- **Registro:** 100/minuto
- **Pagos:** 50/minuto
- **Login:** 200/minuto

---

## 📚 Documentación Completa

- **SISTEMA_REGISTRO_COMPLETO.md** - Documentación técnica
- **GUIA_RAPIDA_REGISTRO.md** - Guía de inicio
- **CAMBIOS_SISTEMA_REGISTRO.md** - Resumen de cambios
- **REGISTRO_COMPLETADO.txt** - Resumen ejecutivo

---

## 🆘 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "Email already registered" | `DELETE FROM users WHERE email='...'` |
| "Token Inválido" | Token expiró o ya se usó, generar nuevo |
| Pestaña OPO no aparece | Verificar `opo_interest=1` o `opo_access=1` |
| Email no se envía | Verificar `config/email_config.json` → `enabled: true` |
| Error al registrar | Ver logs del servidor, verificar validaciones |

---

**Última actualización:** 2026-05-27
**Versión:** 1.0.0
