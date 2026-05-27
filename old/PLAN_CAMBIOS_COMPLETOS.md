# Plan de Cambios Completos - DVDcoin Bank

## Estado: EN PROGRESO

## Tareas Completadas ✅
1. **Optimización de velocidad de juegos** - DONE
   - Reducidos timeouts de WebSocket de 3s a 1s
   - Reducidas transiciones CSS de 0.2-0.35s a 0.1-0.12s
   - Reducidos delays de focus de 60ms a 20ms
   - Añadido `will-change: transform` para mejor rendimiento

2. **Traducción de textos frontend básicos** - DONE
   - "Sign out" → "Cerrar sesión"
   - Filtros de stats traducidos
   - Nombres de juegos traducidos

## Tareas Pendientes 🔄

### TAREA 3: Sistema i18n completo en todos los HTML
**Objetivo**: Reemplazar todos los textos hardcodeados con atributos data-i18n

**Archivos a modificar**:
- ✅ Sistema i18n ya existe en `/static/js/i18n.js`
- ✅ Traducciones completas en `/static/i18n/*.json`
- ❌ Falta aplicar data-i18n en TODOS los HTML

**Archivos críticos**:
1. `c:\dvdcoin\static\index.html` - Referencia correcta
2. `c:\dvdcoin\game_pages\apuestas\apuestas.html` - Necesita i18n
3. `c:\dvdcoin\game_pages\votaciones\votaciones.html` - Necesita i18n
4. `c:\dvdcoin\static\cuentos_admin.html` - Necesita i18n
5. Todos los archivos de juegos en `/static/`

**Cambios necesarios**:
- Añadir `<script src="/static/js/i18n.js"></script>` en todos los HTML
- Reemplazar textos hardcodeados con `data-i18n="key"`
- Ejemplo: `<button>Cerrar sesión</button>` → `<button data-i18n="signOut">Cerrar sesión</button>`

### TAREA 4: Navegación unificada en TODOS los HTML
**Objetivo**: Asegurar que TODOS los HTML tengan la misma navegación

**Sistema existente**:
- ✅ CSS: `/static/css/unified-nav.css`
- ✅ JS: `/static/js/unified-nav.js`
- ✅ Container: `<div id="unifiedNavContainer"></div>`

**Archivos que necesitan navegación unificada**:
1. ❌ `c:\dvdcoin\game_pages\apuestas\apuestas.html` - Tiene nav custom, reemplazar
2. ❌ `c:\dvdcoin\game_pages\votaciones\votaciones.html` - Tiene nav custom, reemplazar
3. ✅ `c:\dvdcoin\static\index.html` - Ya tiene unified nav
4. ✅ `c:\dvdcoin\static\cuentos_admin.html` - Ya tiene unified nav

**Cambios necesarios**:
- Añadir `<link rel="stylesheet" href="/static/css/unified-nav.css">`
- Añadir `<script src="/static/js/unified-nav.js"></script>`
- Añadir `<div id="unifiedNavContainer"></div>` al inicio del body
- Eliminar navegación custom existente

### TAREA 5: Eliminar iconos duplicados en navegación
**Objetivo**: Cada pestaña debe tener SOLO UN icono

**Archivo a modificar**:
- `c:\dvdcoin\static\js\unified-nav.js`

**Problema identificado**:
```javascript
{ id: 'cuentos', icon: '📖', label: 'Cuentos', ... }
```
Si el label también tiene icono, hay duplicación.

**Solución**:
- Revisar NAV_CONFIG en unified-nav.js
- Asegurar que cada tab tenga icono SOLO en el campo `icon`, no en `label`

### TAREA 6: Permisos admin para todos los juegos
**Objetivo**: Todos los admins (no solo 'dvd') pueden acceder a controles de juegos

**Archivos a modificar**:
- Buscar `username === 'dvd'` y reemplazar con `is_admin`
- Archivos encontrados en grep:
  - `c:\dvdcoin\static\index.html`
  - `c:\dvdcoin\static\pages\index.html`
  - `c:\dvdcoin\static\pasapalabra\index.html`
  - Admin pages de juegos

**Cambio necesario**:
```javascript
// ANTES:
if (me.username === 'dvd') { ... }

// DESPUÉS:
if (me.is_admin) { ... }
```

### TAREA 7: Todos los admins pueden subir cuentos
**Objetivo**: Permitir que todos los admins suban cuentos desde la pestaña Cuentos

**Archivo a modificar**:
- `c:\dvdcoin\static\cuentos_admin.html`

**Verificar**:
- Ya tiene check `if (!me.is_admin)` en línea ~24
- ✅ Parece que ya está correcto
- Verificar que no haya restricciones adicionales

**Botón duplicado**:
- Buscar y eliminar botón "Cuentos" duplicado (ubicación por determinar)

## Orden de Ejecución

1. ✅ TAREA 5: Arreglar iconos duplicados en unified-nav.js
2. ✅ TAREA 4: Añadir navegación unificada a apuestas.html y votaciones.html
3. ✅ TAREA 3: Añadir sistema i18n a todos los HTML
4. ✅ TAREA 6: Cambiar permisos de 'dvd' a 'is_admin'
5. ✅ TAREA 7: Verificar permisos de cuentos

## Notas Importantes

- **NO aplicar cambios hasta completar TODO** (instrucción del usuario)
- Todos los textos deben ser traducibles
- Todas las páginas deben tener la misma navegación
- Todos los admins deben tener los mismos permisos (excepto OPO que es exclusivo de dvd)
