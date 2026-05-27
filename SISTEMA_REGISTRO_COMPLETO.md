# Sistema de Registro Completo - DVDcoin Platform

## 📋 Resumen

Sistema completo de registro de usuarios con:
- ✅ Validación de campos obligatorios
- ✅ Verificación de email
- ✅ Procesamiento de pagos
- ✅ Acceso a Oposiciones (OPO)
- ✅ Recopilación completa de datos de usuario

---

## 🎯 Funcionalidades Implementadas

### 1. Formulario de Registro Mejorado

**Campos del formulario:**
- **Usuario*** (obligatorio): 2-30 caracteres
- **Email*** (obligatorio): Formato válido de email
- **Contraseña*** (obligatorio): Mínimo 4 caracteres
- **Confirmar Contraseña*** (obligatorio): Debe coincidir con la contraseña
- **Nombre Completo** (opcional): Nombre completo del usuario
- **Teléfono** (opcional): Número de teléfono
- **Interés en Oposiciones** (checkbox): Indica si el usuario está interesado en OPO
- **Términos y Condiciones*** (obligatorio): Debe aceptar para registrarse

**Validaciones frontend:**
- Campos obligatorios no vacíos
- Formato de email válido (regex)
- Contraseñas coinciden
- Longitud mínima de contraseña
- Aceptación de términos

### 2. Backend de Registro

**Endpoint:** `POST /bank/api/register`

**Validaciones backend:**
- Username único (2-30 caracteres)
- Email único y formato válido
- Contraseña mínimo 4 caracteres
- Usuarios reservados (GHOST)

**Proceso:**
1. Validar datos de entrada
2. Verificar que username y email no existan
3. Generar token de verificación (32 bytes, expira en 24h)
4. Hash de contraseña con bcrypt
5. Guardar usuario en base de datos con todos los campos
6. Enviar email de verificación
7. Crear sesión y token JWT
8. Retornar respuesta con indicación de verificación requerida

**Campos guardados en DB:**
```sql
username, password_hash, email, full_name, phone, 
opo_interest, verification_token, verification_expires, 
email_verified (0 por defecto)
```

### 3. Verificación de Email

**Endpoint:** `GET /bank/verify-email?token=<token>`

**Proceso:**
1. Validar que el token existe
2. Verificar que no esté ya verificado
3. Verificar que no haya expirado (24 horas)
4. Marcar email como verificado
5. Limpiar token de verificación
6. Mostrar página de confirmación

**Páginas de respuesta:**
- ✅ **Email Verificado**: Confirmación exitosa
- ❌ **Token Inválido**: Token no existe o ya usado
- ⏰ **Token Expirado**: Más de 24 horas
- ℹ️ **Ya Verificado**: Email ya verificado anteriormente

### 4. Sistema de Pagos

**Endpoint:** `POST /bank/api/payment`

**Parámetros:**
```json
{
  "username": "usuario",
  "amount": 10.0,
  "payment_method": "card",
  "opo_access": true
}
```

**Validaciones:**
- Usuario autenticado coincide con el pago
- Email verificado antes de pagar
- Monto válido (> 0)

**Proceso:**
1. Verificar autenticación y email verificado
2. Procesar pago (integración con procesador real pendiente)
3. Actualizar estado de pago en DB
4. Activar acceso OPO si corresponde
5. Retornar confirmación

**Campos actualizados:**
```sql
payment_status = 'completed'
payment_date = <timestamp>
payment_amount = <monto>
opo_access = 1 (si se solicitó)
```

### 5. Pestaña de Oposiciones (OPO)

**Visibilidad:**
- Usuarios con `opo_interest = 1` (marcaron interés en registro)
- Usuarios con `opo_access = 1` (pagaron por acceso)
- Admins (siempre visible)

**Navegación:**
- Botón en barra de navegación: "📚 Oposiciones"
- Función: `openOpo()` → Redirige a `/opo`

**Integración:**
- Se muestra automáticamente al cargar la app si el usuario tiene acceso
- Redirige al servidor de exámenes (puerto 8001)

### 6. Endpoint de Perfil Actualizado

**Endpoint:** `GET /bank/api/me`

**Campos adicionales retornados:**
```json
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

## 📧 Configuración de Email

### Archivo de Configuración

**Ubicación:** `config/email_config.json`

### Opciones de Configuración

#### 1. SMTP (Gmail, Outlook, servidor propio)

```json
{
  "provider": "smtp",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "tu-email@gmail.com",
  "smtp_pass": "tu-app-password",
  "use_tls": true,
  "from_email": "noreply@dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

**Para Gmail:**
1. Activar verificación en 2 pasos
2. Generar contraseña de aplicación: https://myaccount.google.com/apppasswords
3. Usar la contraseña generada en `smtp_pass`

#### 2. SendGrid (API)

```json
{
  "provider": "sendgrid",
  "api_key": "SG.xxxxxxxxxxxxx",
  "from_email": "noreply@dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

**Instalación:**
```bash
pip install sendgrid
```

#### 3. Mailgun (API)

```json
{
  "provider": "mailgun",
  "api_key": "key-xxxxxxxxxxxxx",
  "domain": "mg.dvta.ch",
  "from_email": "noreply@mg.dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

**Instalación:**
```bash
pip install requests
```

#### 4. MailHog (Desarrollo Local)

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

**Instalación MailHog:**
- Windows: Descargar desde https://github.com/mailhog/MailHog/releases
- Mac: `brew install mailhog`
- Linux: `go get github.com/mailhog/MailHog`

**Uso:**
1. Ejecutar MailHog: `mailhog`
2. Ver emails en: http://localhost:8025
3. SMTP escucha en: localhost:1025

---

## 🗄️ Estructura de Base de Datos

### Tabla `users` - Campos Nuevos

```sql
email           TEXT,                    -- Email del usuario
full_name       TEXT,                    -- Nombre completo
phone           TEXT,                    -- Teléfono
email_verified  INTEGER DEFAULT 0,       -- 0=no verificado, 1=verificado
verification_token TEXT,                 -- Token de verificación
verification_expires TEXT,               -- Fecha de expiración del token
opo_interest    INTEGER DEFAULT 0,       -- Interés en oposiciones
opo_access      INTEGER DEFAULT 0,       -- Acceso pagado a oposiciones
payment_status  TEXT DEFAULT 'pending',  -- Estado del pago
payment_date    TEXT,                    -- Fecha del pago
payment_amount  REAL DEFAULT 0.0         -- Monto pagado
```

**Migración automática:** Los campos se añaden automáticamente al iniciar el servidor si no existen.

---

## 🔄 Flujo Completo de Registro

```
1. Usuario completa formulario de registro
   ↓
2. Frontend valida campos
   ↓
3. POST /bank/api/register
   ↓
4. Backend valida y guarda usuario
   ↓
5. Se genera token de verificación
   ↓
6. Se envía email de verificación
   ↓
7. Usuario recibe email y hace clic en link
   ↓
8. GET /bank/verify-email?token=xxx
   ↓
9. Email marcado como verificado
   ↓
10. Usuario puede acceder a funcionalidades completas
    ↓
11. (Opcional) Usuario realiza pago para OPO
    ↓
12. POST /bank/api/payment
    ↓
13. Acceso OPO activado
    ↓
14. Pestaña OPO visible en navegación
```

---

## 🧪 Testing

### 1. Probar Registro

```bash
# Con curl
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

### 2. Verificar Email (Desarrollo)

Si el email está deshabilitado, puedes verificar manualmente:

```sql
-- Conectar a la base de datos
sqlite3 src/data/users.db

-- Ver token de verificación
SELECT username, verification_token, verification_expires 
FROM users 
WHERE username='testuser';

-- Verificar manualmente
UPDATE users 
SET email_verified=1, verification_token=NULL, verification_expires=NULL 
WHERE username='testuser';
```

### 3. Probar Pago

```bash
curl -X POST http://localhost:8000/bank/api/payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu-token-jwt>" \
  -d '{
    "username": "testuser",
    "amount": 10.0,
    "payment_method": "card",
    "opo_access": true
  }'
```

---

## 🔐 Seguridad

### Implementado

✅ **Contraseñas hasheadas** con bcrypt
✅ **Tokens JWT** para autenticación
✅ **Tokens de verificación** aleatorios (32 bytes)
✅ **Expiración de tokens** (24 horas)
✅ **Validación de email** formato y unicidad
✅ **Rate limiting** en endpoints
✅ **Cookies HTTP-only** para tokens
✅ **Verificación de email** antes de pagos

### Recomendaciones para Producción

⚠️ **HTTPS obligatorio** - Cambiar `secure=False` a `secure=True` en cookies
⚠️ **Integración de pago real** - Stripe, PayPal, etc.
⚠️ **Validación de teléfono** - Formato internacional
⚠️ **Límites de intentos** - Bloqueo temporal tras fallos
⚠️ **Logs de auditoría** - Registrar acciones sensibles
⚠️ **Backup automático** - Base de datos regular

---

## 📝 Endpoints API

### Registro
- `POST /bank/api/register` - Crear cuenta
- `POST /api/register` - Alias para compatibilidad

### Verificación
- `GET /bank/verify-email?token=xxx` - Verificar email
- `GET /api/verify-email?token=xxx` - Alias

### Pago
- `POST /bank/api/payment` - Procesar pago
- `POST /api/payment` - Alias

### Perfil
- `GET /bank/api/me` - Obtener perfil
- `GET /api/me` - Alias

---

## 🚀 Próximos Pasos

### Funcionalidades Pendientes

1. **Integración de Pago Real**
   - Stripe: https://stripe.com/docs/api
   - PayPal: https://developer.paypal.com/
   - Redsys (España): https://pagosonline.redsys.es/

2. **Reenvío de Email de Verificación**
   - Endpoint para solicitar nuevo email
   - Límite de reenvíos (ej: 3 por hora)

3. **Recuperación de Contraseña**
   - Endpoint para solicitar reset
   - Email con link temporal
   - Formulario de nueva contraseña

4. **Panel de Usuario**
   - Ver estado de verificación
   - Historial de pagos
   - Gestionar suscripción OPO

5. **Dashboard de Admin**
   - Ver usuarios registrados
   - Estado de verificaciones
   - Gestionar accesos OPO manualmente

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs del servidor: `src/main.py` (logging.INFO)
2. Verificar configuración de email: `config/email_config.json`
3. Comprobar base de datos: `src/data/users.db`

---

**Última actualización:** 2026-05-27
**Versión:** 1.0.0
**Estado:** ✅ Completamente funcional (email deshabilitado por defecto)
