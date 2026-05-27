# Cambios en Permisos de Audio y Cámara

## Resumen
Se han modificado los permisos de audio y cámara para que solo se soliciten cuando el usuario entra en la sección "Social", en lugar de solicitarlos al hacer login.

## Cambios Realizados

### 1. Eliminación de Solicitud de Permisos en Login
Se eliminó el código que solicitaba permisos de cámara y micrófono inmediatamente después del login en todos los archivos HTML principales.

**Archivos modificados:**
- `static/index.html`
- `static/pages/index.html`
- `dvdcoin_pi/static/index.html`
- `dvdcoin_pi/static/pages/index.html`
- `dvdcoin_pi/static/static/index.html`
- `dvdcoin_pi/static/static/pages/index.html`

**Código eliminado:**
```javascript
// 3. Request camera + microphone permission early
// This shows the browser dialog while user is actively using the app (login gesture)
// After granting, subsequent getUserMedia calls in video calls work silently
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
  // ... código de solicitud de permisos ...
}
```

**Reemplazado por:**
```javascript
// Permissions for camera + microphone are now requested only when entering Social section
// This improves user experience by not asking for permissions on login
```

### 2. Nueva Función para Solicitar Permisos
Se creó una nueva función `_requestMediaPermissions()` que se invoca únicamente cuando el usuario navega a la sección "Social".

**Función agregada en todos los archivos:**
```javascript
/* ── Request media permissions for Social section ─────── */
function _requestMediaPermissions() {
  // Only request once
  if (window._permissionsRequested) return;
  window._permissionsRequested = true;

  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    const getMedia = window._videoOptimizations?.getMediaStream || 
                     navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    
    getMedia({
      video: { facingMode:'user', width:{ideal:320}, height:{ideal:240} },
      audio: { echoCancellation:true, noiseSuppression:true }
    }).then(stream => {
      _permStream = stream;
      stream.getTracks().forEach(t => { t.enabled = false; });
      console.log('[SOCIAL] Permission stream obtained successfully');
    }).catch(() => {
      console.warn('[SOCIAL] Video permission failed, trying audio only');
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        _permStream = stream;
        stream.getTracks().forEach(t => { t.enabled = false; });
        console.log('[SOCIAL] Audio-only permission stream obtained');
      }).catch(() => {
        console.warn('[SOCIAL] All permission requests failed');
      });
    });
  }
}
```

### 3. Modificación de la Función de Navegación
Se modificó la función `nav()` para invocar `_requestMediaPermissions()` cuando el usuario navega a la sección "Social".

**Cambio en la función nav():**
```javascript
function nav(name, el) {
  // ... código existente ...
  
  if (name === 'social')  _requestMediaPermissions();  // ← NUEVO
}
```

## Beneficios

1. **Mejor experiencia de usuario**: Los usuarios no verán solicitudes de permisos al iniciar sesión, solo cuando realmente necesiten usar funciones de video/audio.

2. **Privacidad mejorada**: Los permisos solo se solicitan cuando el usuario accede a funcionalidades que los requieren.

3. **Solicitud única**: La función verifica `window._permissionsRequested` para asegurar que los permisos solo se soliciten una vez por sesión.

4. **Fallback inteligente**: Si el video falla, intenta solo con audio. Si ambos fallan, registra el error sin bloquear la aplicación.

## Comportamiento

- **Al hacer login**: No se solicitan permisos de cámara ni micrófono.
- **Al entrar a Social**: Se solicitan permisos de cámara y micrófono la primera vez.
- **Navegaciones posteriores a Social**: No se vuelven a solicitar permisos (ya están concedidos).
- **Stream de permisos**: Se mantiene un stream silencioso (`_permStream`) con tracks deshabilitados para mantener los permisos activos.

## Logs de Consola

Los mensajes de log ahora indican claramente que los permisos se solicitan desde la sección Social:
- `[SOCIAL] Permission stream obtained successfully`
- `[SOCIAL] Video permission failed, trying audio only`
- `[SOCIAL] Audio-only permission stream obtained`
- `[SOCIAL] All permission requests failed`

## Fecha de Implementación
9 de mayo de 2026
