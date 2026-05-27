# 🔒 SEGURIDAD: Tokens NO en URL

## ❌ PROBLEMA DETECTADO

El sistema estaba pasando tokens JWT en las URLs:
```
https://example.com/apuestas?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**RIESGOS:**
- ❌ Tokens visibles en historial del navegador
- ❌ Tokens en logs del servidor
- ❌ Tokens compartidos accidentalmente al copiar URLs
- ❌ Tokens expuestos en referrers HTTP
- ❌ Vulnerabilidad de seguridad crítica

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Cookies HTTP-Only (Backend)

**Archivo**: `src/main.py`

**Cambios**:
- Función `get_current_user()` ahora acepta tokens desde:
  1. **Cookie `dvd_token`** (preferido, seguro)
  2. Header `Authorization: Bearer` (fallback para APIs)
  3. ❌ **NUNCA desde query parameters**

- Endpoints `/api/login` y `/api/register` ahora establecen cookies HTTP-only:
  ```python
  response.set_cookie(
      key="dvd_token",
      value=token,
      httponly=True,  # No accesible desde JavaScript
      secure=False,   # True en producción con HTTPS
      samesite="lax",
      max_age=JWT_EXPIRE_H * 3600
  )
  ```

### 2. Frontend Corregido

**Archivos modificados**:
- `game_pages/apuestas/apuestas.html`
- `game_pages/votaciones/votaciones.html`

**Cambios**:
```javascript
// ANTES (INSEGURO):
const tok = new URLSearchParams(location.search).get('token') || localStorage.getItem('dvd_token');
window.location.href = `/page?token=${encodeURIComponent(token)}`;

// AHORA (SEGURO):
const tok = localStorage.getItem('dvd_token') || '';  // Solo localStorage
window.location.href = `/page`;  // Sin token en URL
```

### 3. Fetch con Credentials

Todas las llamadas fetch ahora incluyen:
```javascript
fetch(url, {
    credentials: 'include',  // Incluir cookies automáticamente
    headers: {
        'Authorization': `Bearer ${token}`  // Fallback
    }
})
```

## 📋 ARCHIVOS QUE NECESITAN CORRECCIÓN

Los siguientes archivos AÚN pasan tokens en URLs y deben ser corregidos:

### Páginas de juegos:
- `static/quiensoy.html`
- `static/quiensoy/quiensoy.html`
- `static/quiensoy/game.html`
- `static/pasapalabra.html`
- `static/pasapalabra/pasapalabra.html`
- `static/pasapalabra/game.html`
- `static/pasapalabra/index.html`
- `static/pages/index.html`
- `static/pages/mensajes.html`
- `static/webrtc-video.html`
- `static/pages/webrtc-video.html`

### WebSockets:
Los WebSockets también pasan tokens en la URL de conexión:
```javascript
// INSEGURO:
ws = new WebSocket(`ws://host/ws/game?token=${token}`);

// DEBE SER:
ws = new WebSocket(`ws://host/ws/game`);
// Y el servidor debe leer el token de las cookies
```

## 🔧 CÓMO CORREGIR MANUALMENTE

### Para páginas HTML:

1. **Eliminar token de URLs**:
```javascript
// ANTES:
window.location.href = `/page?token=${encodeURIComponent(token)}`;

// DESPUÉS:
window.location.href = `/page`;
```

2. **No leer token de URL**:
```javascript
// ANTES:
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token') || localStorage.getItem('dvd_token');

// DESPUÉS:
const token = localStorage.getItem('dvd_token');
```

3. **Agregar credentials a fetch**:
```javascript
fetch(url, {
    credentials: 'include',
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
```

### Para WebSockets:

El servidor debe modificarse para leer tokens de cookies en WebSockets:
```python
@app.websocket("/ws/game")
async def websocket_game(websocket: WebSocket):
    # Leer token de cookie
    token = websocket.cookies.get("dvd_token")
    if not token:
        await websocket.close(code=1008)
        return
    
    user = decode_token(token)
    if not user:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()
    # ...
```

## ✅ BENEFICIOS

1. **Seguridad mejorada**: Tokens no expuestos en URLs
2. **Privacidad**: No quedan tokens en historial del navegador
3. **Compliance**: Cumple con mejores prácticas de seguridad
4. **HTTP-Only**: Cookies no accesibles desde JavaScript (protección XSS)
5. **SameSite**: Protección contra CSRF

## 🚀 PRÓXIMOS PASOS

1. ✅ Backend corregido (`src/main.py`)
2. ✅ Apuestas corregido (`game_pages/apuestas/apuestas.html`)
3. ✅ Votaciones corregido (`game_pages/votaciones/votaciones.html`)
4. ⏳ Corregir páginas de juegos restantes
5. ⏳ Corregir WebSockets para usar cookies
6. ⏳ Habilitar `secure=True` en producción (requiere HTTPS)

## 📝 NOTAS

- El sistema mantiene compatibilidad con `Authorization: Bearer` para APIs
- localStorage sigue usándose como cache del token para el header
- Las cookies se establecen automáticamente en login/register
- El token en localStorage se sincroniza con la cookie

## ⚠️ IMPORTANTE

**NUNCA** volver a pasar tokens en URLs. Siempre usar:
1. Cookies HTTP-only (preferido)
2. Headers Authorization (APIs)
3. ❌ NUNCA query parameters

---

**Fecha**: 14 de mayo de 2026
**Estado**: ✅ Parcialmente implementado
**Prioridad**: 🔴 ALTA - Seguridad crítica
