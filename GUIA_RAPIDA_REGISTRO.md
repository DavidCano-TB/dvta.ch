# 🚀 Guía Rápida - Sistema de Registro

## ✅ ¿Qué se ha implementado?

1. **Formulario de registro completo** con todos los campos
2. **Verificación de email** (con token de 24h)
3. **Sistema de pagos** para activar funcionalidades premium
4. **Pestaña OPO** (Oposiciones) visible para usuarios interesados
5. **Backend completo** con validaciones y seguridad

---

## 🎯 Probar el Sistema (3 minutos)

### Paso 1: Iniciar el Servidor

```bash
# Opción A: Servidor Bank solo
python src/main.py

# Opción B: Todos los servidores
INICIAR_TODOS_SERVIDORES.bat
```

### Paso 2: Registrar un Usuario

1. Ir a: http://localhost:8000/bank
2. Hacer clic en "Registrarse"
3. Completar el formulario:
   - Usuario: `testuser`
   - Email: `test@example.com`
   - Contraseña: `test1234`
   - Confirmar contraseña: `test1234`
   - Nombre completo: `Test User` (opcional)
   - Teléfono: `+34600000000` (opcional)
   - ✅ Marcar "Estoy interesado en Oposiciones"
   - ✅ Aceptar términos y condiciones
4. Hacer clic en "Registrarse"

**Resultado esperado:**
```
✅ Cuenta creada! Revisa tu email para verificar tu cuenta.
```

### Paso 3: Verificar Email (Manualmente)

Como el email está deshabilitado por defecto, verificar manualmente:

```bash
# Abrir base de datos
sqlite3 src/data/users.db

# Ver el token de verificación
SELECT username, email, verification_token, email_verified 
FROM users 
WHERE username='testuser';

# Copiar el token y usarlo en el navegador
# http://localhost:8000/bank/verify-email?token=<TOKEN_COPIADO>

# O verificar directamente en DB
UPDATE users 
SET email_verified=1, verification_token=NULL, verification_expires=NULL 
WHERE username='testuser';

# Salir
.quit
```

### Paso 4: Verificar Pestaña OPO

1. Hacer login con el usuario creado
2. Verificar que aparece la pestaña "📚 Oposiciones" en la navegación
3. Hacer clic para acceder al módulo de oposiciones

---

## 📧 Activar Email (Opcional)

### Opción 1: MailHog (Desarrollo Local - Recomendado)

```bash
# 1. Descargar MailHog
# Windows: https://github.com/mailhog/MailHog/releases
# Mac: brew install mailhog

# 2. Ejecutar MailHog
mailhog

# 3. Editar config/email_config.json
{
  "provider": "smtp",
  "smtp_host": "localhost",
  "smtp_port": 1025,
  "use_tls": false,
  "from_email": "noreply@dvta.ch",
  "from_name": "DVDcoin Platform",
  "enabled": true  ← Cambiar a true
}

# 4. Reiniciar servidor
# 5. Ver emails en: http://localhost:8025
```

### Opción 2: Gmail

```json
// config/email_config.json
{
  "provider": "smtp",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "tu-email@gmail.com",
  "smtp_pass": "tu-app-password",  // Generar en: https://myaccount.google.com/apppasswords
  "use_tls": true,
  "from_email": "tu-email@gmail.com",
  "from_name": "DVDcoin Platform",
  "enabled": true
}
```

---

## 🧪 Probar Pagos

### Método 1: Desde el Frontend (Próximamente)

Panel de usuario → Activar OPO → Pagar

### Método 2: API Directa

```bash
# 1. Obtener token JWT (hacer login primero)
# El token se guarda en localStorage como 'dvd_token'

# 2. Hacer petición de pago
curl -X POST http://localhost:8000/bank/api/payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TU_TOKEN_JWT>" \
  -d '{
    "username": "testuser",
    "amount": 10.0,
    "payment_method": "card",
    "opo_access": true
  }'
```

### Método 3: Activar Manualmente en DB

```sql
sqlite3 src/data/users.db

UPDATE users 
SET payment_status='completed', 
    payment_date=datetime('now'), 
    payment_amount=10.0,
    opo_access=1
WHERE username='testuser';

.quit
```

---

## 🔍 Verificar Estado del Usuario

```sql
sqlite3 src/data/users.db

SELECT 
  username, 
  email, 
  email_verified, 
  opo_interest, 
  opo_access, 
  payment_status,
  payment_amount
FROM users 
WHERE username='testuser';

.quit
```

**Resultado esperado:**
```
testuser|test@example.com|1|1|1|completed|10.0
```

---

## 📊 Campos de la Base de Datos

| Campo | Descripción | Valores |
|-------|-------------|---------|
| `email_verified` | Email verificado | 0=No, 1=Sí |
| `opo_interest` | Interés en OPO | 0=No, 1=Sí |
| `opo_access` | Acceso pagado a OPO | 0=No, 1=Sí |
| `payment_status` | Estado del pago | pending, completed, failed |
| `payment_amount` | Monto pagado | Número decimal |

---

## 🎨 Personalizar Emails

Los templates de email están en: `modules/shared/email_service.py`

**Funciones disponibles:**
- `send_verification_email()` - Email de verificación
- `send_password_reset_email()` - Recuperación de contraseña
- `send_email()` - Email genérico

**Personalizar:**
1. Editar el HTML en las funciones
2. Cambiar colores, logos, textos
3. Reiniciar servidor

---

## ⚠️ Troubleshooting

### Problema: "Email already registered"
**Solución:** El email ya existe en la base de datos
```sql
DELETE FROM users WHERE email='test@example.com';
```

### Problema: "Token Inválido" al verificar
**Solución:** El token expiró (24h) o ya se usó
```sql
-- Generar nuevo token
UPDATE users 
SET verification_token='nuevo_token_aqui',
    verification_expires=datetime('now', '+1 day')
WHERE username='testuser';
```

### Problema: Pestaña OPO no aparece
**Solución:** Verificar que `opo_interest=1` o `opo_access=1`
```sql
UPDATE users SET opo_interest=1 WHERE username='testuser';
```

### Problema: Email no se envía
**Solución:** 
1. Verificar `config/email_config.json` → `"enabled": true`
2. Verificar logs del servidor
3. Probar con MailHog primero

---

## 📝 Checklist de Funcionalidades

- [x] Formulario de registro con validaciones
- [x] Campos: username, email, password, full_name, phone
- [x] Checkbox de interés en OPO
- [x] Términos y condiciones
- [x] Backend con validaciones
- [x] Generación de token de verificación
- [x] Email de verificación (configurable)
- [x] Endpoint de verificación de email
- [x] Sistema de pagos (simulado)
- [x] Pestaña OPO visible según acceso
- [x] Endpoint /bank/api/me con campos OPO
- [x] Migración automática de DB
- [x] Documentación completa

---

## 🚀 Siguiente: Integración de Pago Real

Para producción, integrar con:

1. **Stripe** (Recomendado)
   - Documentación: https://stripe.com/docs/payments
   - Librería: `pip install stripe`

2. **PayPal**
   - Documentación: https://developer.paypal.com/
   - Librería: `pip install paypalrestsdk`

3. **Redsys** (España)
   - Documentación: https://pagosonline.redsys.es/
   - Librería: `pip install python-redsys`

---

## 📞 Ayuda

**Logs del servidor:**
```bash
# Ver logs en tiempo real
tail -f logs/server.log  # Linux/Mac
Get-Content logs/server.log -Wait  # Windows PowerShell
```

**Verificar configuración:**
```bash
# Email
cat config/email_config.json

# Base de datos
sqlite3 src/data/users.db ".schema users"
```

---

**¡Sistema listo para usar!** 🎉

Para más detalles, ver: `SISTEMA_REGISTRO_COMPLETO.md`
