# 🔐 Corrección del Sistema de Login - DVDcoin Bank

## 📋 Problema Identificado

El login en https://dvta.ch/bank no funcionaba debido a un **desajuste entre las rutas del frontend y backend**:

- **Frontend** llamaba a: `POST /api/login`, `GET /api/me`, etc.
- **Backend** esperaba: `POST /bank/api/login`, `GET /bank/api/me`, etc.

## ✅ Solución Implementada

### 1. **Corrección del Frontend Principal**
Se actualizó `static/index.html` para usar las rutas correctas:
- ✅ `POST /api/login` → `POST /bank/api/login`
- ✅ `POST /api/register` → `POST /bank/api/register`
- ✅ `GET /api/me` → `GET /bank/api/me`

### 2. **Aliases de Compatibilidad en Backend**
Se agregaron **aliases** en `src/main.py` para soportar ambas rutas y garantizar compatibilidad con todos los archivos HTML existentes:

#### Endpoints de Autenticación:
- ✅ `/api/login` → alias de `/bank/api/login`
- ✅ `/api/register` → alias de `/bank/api/register`
- ✅ `/api/me` → alias de `/bank/api/me`
- ✅ `/api/me/refresh-token` → alias de `/bank/api/me/refresh-token`
- ✅ `/api/me/change-password` → alias de `/bank/api/me/change-password`
- ✅ `/api/me/lang` → alias de `/bank/api/me/lang` (GET y POST)

#### Endpoints de Operaciones:
- ✅ `/api/users` → alias de `/bank/api/users`
- ✅ `/api/transfer` → alias de `/bank/api/transfer`
- ✅ `/api/history` → alias de `/bank/api/history`

#### Endpoints de Mensajería:
- ✅ `/api/messages/status` → alias de `/bank/api/messages/status`
- ✅ `/api/messages/history` → alias de `/bank/api/messages/history`
- ✅ `/api/messages/unread` → alias de `/bank/api/messages/unread`
- ✅ `/api/messages/toggle` → alias de `/bank/api/messages/toggle`
- ✅ `/api/messages/admin/stats` → alias de `/bank/api/messages/admin/stats`
- ✅ `/api/messages/admin/all-rooms` → alias de `/bank/api/messages/admin/all-rooms`

## 🎯 Beneficios de esta Solución

### ✅ Compatibilidad Total
- **Archivos nuevos** pueden usar `/bank/api/*` (ruta canónica)
- **Archivos antiguos** siguen funcionando con `/api/*` (alias)
- **Sin breaking changes** para ningún módulo existente

### ✅ Escalabilidad
- Fácil agregar nuevos aliases cuando sea necesario
- Patrón consistente para futuros endpoints
- Documentación clara de rutas canónicas vs aliases

### ✅ Mantenibilidad
- Código DRY: los aliases llaman a las funciones principales
- Un solo punto de lógica para cada endpoint
- Fácil deprecar aliases en el futuro si es necesario

## 🔧 Archivos Modificados

1. **`static/index.html`** - Frontend principal corregido
2. **`src/main.py`** - Backend con aliases agregados

## 🚀 Próximos Pasos

### Para Otros Archivos HTML
Si encuentras otros archivos HTML que usan `/api/*`, tienes dos opciones:

**Opción 1 (Recomendada):** Actualizar a rutas canónicas
```javascript
// Cambiar de:
await req('POST', '/api/login', { username, password })

// A:
await req('POST', '/bank/api/login', { username, password })
```

**Opción 2:** Dejar como está
- Los aliases garantizan que sigan funcionando
- Útil para archivos que no quieres tocar

### Para Nuevos Servidores/Módulos
Cuando agregues nuevos servidores (exams, games, social), sigue este patrón:

1. **Rutas canónicas:** `/<modulo>/api/<endpoint>`
   - Ejemplo: `/exams/api/login`, `/games/api/scores`

2. **Aliases opcionales:** `/api/<modulo>/<endpoint>`
   - Solo si necesitas compatibilidad con código legacy

3. **JWT compartido:** Usa `modules/shared/jwt_helper.py`
   - Permite autenticación unificada entre módulos

## 📊 Sistema de Autenticación Unificado

### Flujo Actual
```
Usuario → Frontend (static/index.html)
           ↓
       POST /bank/api/login (o /api/login)
           ↓
       Backend (src/main.py)
           ↓
       Valida credenciales (users.db)
           ↓
       Genera JWT token (168h expiración)
           ↓
       Retorna token + cookie HTTP-only
           ↓
       Frontend almacena en localStorage
           ↓
       Todas las requests usan token
```

### Características de Seguridad
- ✅ JWT con expiración de 1 semana
- ✅ Refresh automático cuando queda < 1 hora
- ✅ Cookies HTTP-only (protección XSS)
- ✅ Rate limiting (200 login/min, 100 register/min)
- ✅ Sistema de bloqueo por intentos fallidos
- ✅ Master password para superadmins (emergencia)
- ✅ Bcrypt para hash de contraseñas
- ✅ Validación de bloqueo en cada request

## 🎉 Resultado

El login ahora funciona correctamente en https://dvta.ch/bank y todos los módulos existentes mantienen compatibilidad.

---

**Fecha de corrección:** 27 de mayo de 2026  
**Versión:** DVDcoin Bank v4.0
