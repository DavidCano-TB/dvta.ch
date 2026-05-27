# 🎤📹 Permisos de Audio y Video Optimizados

## 🎯 Objetivo

Los permisos de audio y cámara ahora se solicitan **SOLO cuando son necesarios**, no al abrir la aplicación. Esto mejora significativamente la experiencia del usuario.

## ✅ Cambios Realizados

### 1. **Eliminada Solicitud Automática al Login** ❌→✅

**Antes:**
```javascript
// Al hacer login, se pedían permisos inmediatamente
await loadApp();
_requestAppPermissions(); // ❌ Pedía audio + video
```

**Ahora:**
```javascript
// Al hacer login, solo se piden notificaciones
await loadApp();
_requestNotificationPermission(); // ✅ Solo notificaciones
```

### 2. **Eliminada Solicitud al Abrir Sección Social** ❌→✅

**Antes:**
```javascript
if (name === 'social') _requestMediaPermissions(); // ❌ Pedía permisos al abrir
```

**Ahora:**
```javascript
// NO se piden permisos al abrir Social
// Se pedirán cuando el usuario inicie/se una a una videollamada
```

### 3. **Permisos Solo al Iniciar Videollamada** ✅

Los permisos de cámara y micrófono se solicitan **exclusivamente** cuando:

- El usuario **crea una sala de videollamada**
- El usuario **se une a una sala de videollamada**

```javascript
async function _enterRoom(key, title, isHost){
  // ...
  // ✅ AQUÍ se solicitan los permisos (cuando el usuario se une)
  console.log('[VIDEO] Requesting camera and microphone permissions...');
  _localStream = await navigator.mediaDevices.getUserMedia({
    video:{ facingMode:'user', width:{ideal:1280}, height:{ideal:720} },
    audio:{ echoCancellation:true, noiseSuppression:true, autoGainControl:true }
  });
  // ...
}
```

### 4. **Permisos de Audio Solo al Grabar** ✅

Los permisos de micrófono para grabar mensajes de voz se solicitan cuando:

- El usuario **presiona el botón de grabar audio** en el chat

```javascript
async function toggleRecord() {
  // ✅ AQUÍ se solicitan permisos de micrófono (al grabar)
  const stream = await navigator.mediaDevices.getUserMedia({ 
    audio: true, 
    video: false 
  });
  // ...
}
```

## 📋 Casos de Uso

### ✅ Caso 1: Usuario Abre la Aplicación

```
1. Usuario hace login
2. ✅ Se solicitan permisos de NOTIFICACIONES
3. ❌ NO se solicitan permisos de audio/video
4. Usuario navega libremente por la app
```

### ✅ Caso 2: Usuario Abre Sección Social

```
1. Usuario click en "Social & Chat"
2. ❌ NO se solicitan permisos
3. Usuario puede ver salas, enviar mensajes de texto
4. Usuario puede ver quién está en línea
```

### ✅ Caso 3: Usuario Inicia Videollamada

```
1. Usuario click en "Crear Sala" o "Unirse a Sala"
2. ✅ Se solicitan permisos de CÁMARA + MICRÓFONO
3. Usuario acepta/rechaza permisos
4. Si acepta: videollamada inicia
5. Si rechaza: se muestra mensaje de error
```

### ✅ Caso 4: Usuario Graba Mensaje de Voz

```
1. Usuario abre chat
2. Usuario click en botón de grabar 🎤
3. ✅ Se solicitan permisos de MICRÓFONO
4. Usuario acepta/rechaza permisos
5. Si acepta: grabación inicia
6. Si rechaza: se muestra mensaje de error
```

### ✅ Caso 5: Usuario Juega Hundir la Flota

```
1. Usuario abre el juego
2. ❌ NO se solicitan permisos
3. Los sonidos del juego usan Audio() con datos embebidos
4. No requieren permisos de micrófono
```

## 🔧 Funciones Modificadas

### `_requestNotificationPermission()` - Nueva

```javascript
function _requestNotificationPermission(){
  // 1. Notification permission
  if('Notification' in window && Notification.permission === 'default'){
    Notification.requestPermission().catch(()=>{});
  }

  // 2. Unlock AudioContext (para reproducir sonidos)
  try{
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    // ... inicializar contexto de audio
    window._audioCtx = ctx;
  }catch(e){}
}
```

### `_requestAppPermissions()` - Actualizada

```javascript
function _requestAppPermissions(){
  // Legacy function - now only requests notifications
  // Audio/Video permissions are requested on-demand
  _requestNotificationPermission();
}
```

### `_requestMediaPermissions()` - Eliminada

```javascript
/* ── Request media permissions REMOVED ─────────────────────
   Media permissions (audio/video) are now requested on-demand:
   - When joining/creating a video call (_enterRoom function)
   - When recording audio messages (chat)
   - When playing games that require audio
   This improves UX by not asking for permissions unnecessarily.
─────────────────────────────────────────────────────────── */
```

### `_enterRoom()` - Actualizada

```javascript
async function _enterRoom(key, title, isHost){
  // ...
  // ✅ Solicitar permisos AQUÍ (cuando el usuario se une)
  console.log('[VIDEO] Requesting camera and microphone permissions...');
  try{
    _localStream = await navigator.mediaDevices.getUserMedia({
      video:{ facingMode:'user', width:{ideal:1280}, height:{ideal:720} },
      audio:{ echoCancellation:true, noiseSuppression:true, autoGainControl:true }
    });
    console.log('[VIDEO] ✅ Local stream obtained');
  }catch(e1){
    // Intentar solo audio si video falla
    try{ 
      _localStream = await navigator.mediaDevices.getUserMedia({audio:true}); 
      console.log('[VIDEO] ✅ Audio-only stream obtained');
    }
    catch(e2){ 
      console.error('[VIDEO] ❌ All media failed');
      alert('⚠️ No se pudo acceder a la cámara o micrófono. Verifica los permisos del navegador.');
      _localStream = new MediaStream(); 
    }
  }
  // ...
}
```

## 🎮 Juegos y Audio

### Juegos que NO Requieren Permisos

Los siguientes juegos usan `Audio()` con datos embebidos (base64) y **NO requieren permisos**:

- ✅ **Hundir la Flota** - Sonidos de explosiones, agua, victoria
- ✅ **Millonario** - Sonidos de respuestas correctas/incorrectas
- ✅ **Pasapalabra** - Sonidos de tiempo, aciertos
- ✅ **Cifras y Letras** - Sonidos de cuenta atrás
- ✅ **¿Quién Soy?** - Sonidos de juego

Estos juegos reproducen audio pregrabado, no graban ni transmiten audio.

### Funciones que SÍ Requieren Permisos

- 🎤 **Grabar mensajes de voz** en el chat
- 📹 **Videollamadas** (cámara + micrófono)
- 🎙️ **Cualquier función que use `getUserMedia()`**

## 📊 Comparación Antes vs Ahora

| Acción | Antes | Ahora |
|--------|-------|-------|
| **Login** | ❌ Pide audio + video | ✅ Solo notificaciones |
| **Abrir Social** | ❌ Pide audio + video | ✅ No pide nada |
| **Crear/Unirse a Videollamada** | ✅ Usa permisos ya otorgados | ✅ Pide permisos aquí |
| **Grabar Audio** | ✅ Pide permisos | ✅ Pide permisos aquí |
| **Jugar Hundir la Flota** | ✅ No pide permisos | ✅ No pide permisos |
| **Reproducir Sonidos** | ✅ No pide permisos | ✅ No pide permisos |

## 🚀 Beneficios

### 1. **Mejor Experiencia de Usuario** 🎯
- No se molesta al usuario con permisos innecesarios
- Los permisos se solicitan en el contexto correcto
- El usuario entiende por qué se piden los permisos

### 2. **Mayor Tasa de Aceptación** 📈
- Los usuarios son más propensos a aceptar permisos cuando entienden por qué se necesitan
- Solicitar permisos "justo a tiempo" aumenta la confianza

### 3. **Cumplimiento de Mejores Prácticas** ✅
- Sigue las recomendaciones de UX de Google, Apple y Mozilla
- Cumple con las directrices de privacidad modernas
- Reduce la "fatiga de permisos"

### 4. **Menor Consumo de Recursos** 💪
- No se mantienen streams de audio/video innecesarios
- Mejor rendimiento de la aplicación
- Menor consumo de batería en móviles

## 🔍 Verificación

Para verificar que los cambios funcionan correctamente:

### Test 1: Login
```
1. Abre la aplicación en modo incógnito
2. Haz login
3. ✅ Verifica que NO se pidan permisos de cámara/micrófono
4. ✅ Verifica que solo se pidan permisos de notificaciones (opcional)
```

### Test 2: Sección Social
```
1. Navega a "Social & Chat"
2. ✅ Verifica que NO se pidan permisos
3. Envía mensajes de texto
4. ✅ Verifica que funciona sin permisos
```

### Test 3: Videollamada
```
1. Click en "Crear Sala"
2. ✅ Verifica que SE PIDEN permisos de cámara + micrófono
3. Acepta los permisos
4. ✅ Verifica que la videollamada funciona
```

### Test 4: Grabar Audio
```
1. Abre un chat
2. Click en botón de grabar 🎤
3. ✅ Verifica que SE PIDEN permisos de micrófono
4. Acepta los permisos
5. ✅ Verifica que la grabación funciona
```

### Test 5: Juegos
```
1. Abre "Hundir la Flota"
2. ✅ Verifica que NO se piden permisos
3. Juega y escucha los sonidos
4. ✅ Verifica que los sonidos funcionan sin permisos
```

## 📝 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `static/index.html` | ✅ Eliminada solicitud automática de permisos |
| | ✅ Creada función `_requestNotificationPermission()` |
| | ✅ Actualizada función `_requestAppPermissions()` |
| | ✅ Eliminada función `_requestMediaPermissions()` |
| | ✅ Actualizada función `_enterRoom()` |
| `game_pages/messages/chat.html` | ✅ Ya solicita permisos al grabar (sin cambios) |
| `game_pages/hundirlaflota/game.html` | ✅ Usa Audio() embebido (sin cambios) |

## 🎯 Resumen

**Antes:** Los permisos se pedían al login y al abrir Social, molestando al usuario innecesariamente.

**Ahora:** Los permisos se piden **solo cuando son necesarios**:
- 📹 Al iniciar/unirse a videollamada
- 🎤 Al grabar mensaje de voz
- 🔔 Notificaciones al login (opcional)

**Resultado:** Mejor UX, mayor tasa de aceptación, cumplimiento de mejores prácticas.

---

## 🚀 Para Aplicar los Cambios

```bash
RESTART_SERVER.bat
```

¡Los permisos ahora se solicitan de forma inteligente y contextual! 🎉
