# Guía de Implementación del Sistema i18n

## 📋 Resumen

Se ha creado un sistema completo de internacionalización (i18n) para DVDcoin Bank que soporta 7 idiomas:
- 🇪🇸 Español (ES) - por defecto
- 🇬🇧 English (EN)
- 🇫🇷 Français (FR)
- 🏴 Català (CA)
- 🏴 Euskara (EU)
- 🇩🇪 Deutsch (DE)
- 🇮🇹 Italiano (IT)

## 🎯 Componentes Creados

### 1. Archivos CSS
- **`static/css/language-bar.css`** - Estilos para la barra de idiomas con auto-hide al hacer scroll

### 2. Archivos JavaScript
- **`static/js/i18n.js`** - Sistema completo de traducciones con:
  - Carga dinámica de traducciones
  - Barra de selección de idiomas
  - Auto-hide al hacer scroll
  - API global `window.i18n`

### 3. Archivos de Traducción (JSON)
Ubicados en `static/i18n/`:
- `es.json` - Español ✅ COMPLETO
- `en.json` - English ✅ COMPLETO
- `fr.json` - Français ✅ COMPLETO
- `ca.json` - Català ✅ COMPLETO
- `eu.json` - Euskara ⚠️ PENDIENTE (añadir claves de juegos)
- `de.json` - Deutsch ⚠️ PENDIENTE (añadir claves de juegos)
- `it.json` - Italiano ⚠️ PENDIENTE (añadir claves de juegos)

## 🚀 Cómo Aplicar i18n a un Archivo HTML

### Paso 1: Añadir los recursos necesarios en el `<head>`

```html
<head>
  <!-- ... otros meta tags y estilos ... -->
  
  <!-- Sistema i18n -->
  <link rel="stylesheet" href="/static/css/language-bar.css">
</head>
```

### Paso 2: Añadir el script i18n antes del cierre de `</body>`

```html
<body>
  <!-- ... contenido de la página ... -->
  
  <!-- Sistema i18n - DEBE IR ANTES de otros scripts -->
  <script src="/static/js/i18n.js"></script>
  
  <!-- Otros scripts de la página -->
  <script>
    // Tu código JavaScript aquí
  </script>
</body>
```

### Paso 3: Marcar elementos para traducción

Hay varias formas de marcar elementos:

#### A) Texto simple con `data-i18n`
```html
<h1 data-i18n="hundirTitle">Hundir la Flota</h1>
<button data-i18n="hundirValidate">Validar posición</button>
<span data-i18n="hundirWaiting">Esperando jugadores...</span>
```

#### B) Placeholders con `data-i18n-placeholder`
```html
<input type="text" data-i18n-placeholder="txPlaceholderSearch" placeholder="Buscar...">
```

#### C) Contenido HTML con `data-i18n-html`
```html
<div data-i18n-html="regNoteExample">
  Ej.: <strong>usuario</strong>
</div>
```

#### D) Títulos (tooltips) con `data-i18n-title`
```html
<button data-i18n-title="close" title="Cerrar">✕</button>
```

#### E) Título de la página con `data-i18n-page-title`
```html
<head>
  <title data-i18n-page-title="hundirTitle">Hundir la Flota</title>
</head>
```

### Paso 4: Traducciones dinámicas en JavaScript

Si necesitas traducir texto dinámicamente en JavaScript:

```javascript
// Esperar a que el sistema i18n esté listo
window.addEventListener('DOMContentLoaded', () => {
  // Usar la API de traducción
  const message = window.i18n.t('hundirYourTurn'); // "¡Tu turno!"
  
  // Con reemplazos de variables
  const greeting = window.i18n.t('dashGreet', { user: 'Juan' }); // "Hola Juan"
  
  // Obtener idioma actual
  const currentLang = window.i18n.getCurrentLanguage(); // "es"
  
  // Cambiar idioma programáticamente
  window.i18n.setLanguage('en');
});

// Escuchar cambios de idioma
window.addEventListener('languageChanged', (e) => {
  console.log('Idioma cambiado a:', e.detail.language);
  // Actualizar contenido dinámico aquí
});
```

## 📝 Ejemplo Completo: Hundir la Flota

Ver el archivo `game_pages/hundirlaflota/game.html` para un ejemplo completo de implementación.

### Estructura básica:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title data-i18n-page-title="hundirTitle">Hundir la Flota</title>
  
  <!-- Estilos del juego -->
  <link rel="stylesheet" href="/static/css/game-styles.css">
  
  <!-- Sistema i18n -->
  <link rel="stylesheet" href="/static/css/language-bar.css">
</head>
<body>
  <!-- La barra de idiomas se añade automáticamente aquí -->
  
  <div class="game-container">
    <h1 data-i18n="hundirTitle">Hundir la Flota</h1>
    
    <div class="status">
      <span data-i18n="hundirWaiting">Esperando jugadores...</span>
    </div>
    
    <button data-i18n="hundirValidate" onclick="validatePosition()">
      Validar posición
    </button>
  </div>
  
  <!-- Sistema i18n -->
  <script src="/static/js/i18n.js"></script>
  
  <!-- Lógica del juego -->
  <script>
    function validatePosition() {
      const message = window.i18n.t('hundirValidate');
      console.log(message);
    }
    
    // Actualizar UI cuando cambie el idioma
    window.addEventListener('languageChanged', () => {
      // Recargar datos dinámicos si es necesario
      updateGameUI();
    });
  </script>
</body>
</html>
```

## 🔑 Claves de Traducción Disponibles

### Comunes
- `loading`, `error`, `success`, `close`, `save`, `cancel`, `confirm`, `yes`, `no`, `ok`

### Hundir la Flota
- `hundirTitle`, `hundirPlaceShips`, `hundirValidate`, `hundirWaiting`
- `hundirYourTurn`, `hundirOpponentTurn`, `hundirHit`, `hundirMiss`
- `hundirSunk`, `hundirVictory`, `hundirDefeat`
- `shipCarrier`, `shipBattleship`, `shipSubmarine`, `shipDestroyer`, `shipPatrol`

### Quien Soy
- `quienSoyTitle`, `quienSoyAsk`, `quienSoyGuess`, `quienSoyYes`, `quienSoyNo`
- `quienSoyCorrect`, `quienSoyWrong`

### Millonario
- `millonarioTitle`, `millonarioAnswer`, `millonarioFiftyFifty`
- `millonarioAudience`, `millonarioCall`

### Pasapalabra
- `pasapalabraTitle`, `pasapalabraPass`, `pasapalabraAnswer`, `pasapalabraTime`

### Cifras y Letras
- `cifrasLetrasTitle`, `cifrasNumbers`, `cifrasLetters`, `cifrasTarget`, `cifrasSolution`

### Admin
- `adminTitle`, `adminStatus`, `adminActive`, `adminInactive`
- `adminActivate`, `adminDeactivate`, `adminReset`, `adminStart`
- `adminPlayers`, `adminAddPlayer`, `adminOpenGame`

### Votaciones
- `votacionesTitle`, `votacionesCreate`, `votacionesVote`, `votacionesResults`
- `votacionesOpen`, `votacionesClosed`

## ✅ Archivos Pendientes de Traducir

### Prioridad Alta (Juegos)
1. `game_pages/hundirlaflota/game.html` ⚠️ EJEMPLO A CREAR
2. `game_pages/hundirlaflota/admin.html`
3. `game_pages/quiensoy/game.html`
4. `game_pages/millonario/game.html`
5. `game_pages/pasapalabra/game.html`
6. `game_pages/cifrasletras/game.html`
7. `game_pages/apuestas/apuestas.html`
8. `game_pages/votaciones/votaciones.html`

### Prioridad Media (Admin)
9. `static/admin/quiensoy.html`
10. `static/admin/millonario.html`
11. `static/admin/pasapalabra.html`
12. `static/admin/cifrasletras.html`

### Prioridad Baja (Otros)
13. `static/index.html` (página principal)
14. `static/chat.html`
15. `static/mensajes.html`
16. `static/stats.html`
17. `static/cuentos.html`
18. `static/cuentos_admin.html`
19. `static/cuentos_member.html`

## 🛠️ Añadir Nuevas Traducciones

### 1. Añadir la clave en todos los archivos JSON

Edita cada archivo en `static/i18n/`:

**es.json:**
```json
{
  ...
  "miNuevaClave": "Mi texto en español"
}
```

**en.json:**
```json
{
  ...
  "miNuevaClave": "My text in English"
}
```

Y así para FR, CA, EU, DE, IT.

### 2. Usar la clave en el HTML

```html
<span data-i18n="miNuevaClave">Mi texto en español</span>
```

### 3. O usar en JavaScript

```javascript
const texto = window.i18n.t('miNuevaClave');
```

## 🎨 Personalización de la Barra de Idiomas

La barra de idiomas se puede personalizar editando `static/css/language-bar.css`:

- **Posición**: Cambiar `top`, `left`, `right`
- **Colores**: Modificar `background`, `border-color`, `color`
- **Animación**: Ajustar `transition`, `transform`
- **Scroll behavior**: Modificar el threshold en `i18n.js` (línea con `currentScrollY > 50`)

## 📱 Responsive

La barra de idiomas es responsive:
- En móviles: Solo muestra las banderas y códigos de idioma
- En desktop: Muestra también el label "🌐 Language:"

## 🐛 Troubleshooting

### La barra no aparece
- Verificar que `language-bar.css` esté cargado
- Verificar que `i18n.js` esté cargado
- Abrir consola y buscar errores

### Las traducciones no funcionan
- Verificar que los archivos JSON estén en `static/i18n/`
- Verificar que las claves existan en el JSON
- Verificar que `data-i18n` esté correctamente escrito

### La barra no se oculta al hacer scroll
- Verificar que no haya errores de JavaScript
- Verificar que el scroll esté en el elemento correcto

## 📚 Recursos

- **Archivos de ejemplo**: Ver `game_pages/hundirlaflota/game.html`
- **API completa**: Ver comentarios en `static/js/i18n.js`
- **Estilos**: Ver `static/css/language-bar.css`

## 🎯 Próximos Pasos

1. ✅ Completar traducciones de EU, DE, IT (añadir claves de juegos)
2. ⚠️ Aplicar sistema a Hundir la Flota (ejemplo completo)
3. 📝 Aplicar a los demás juegos siguiendo el ejemplo
4. 🧪 Probar en todos los navegadores
5. 📱 Verificar responsive en móviles

---

**Creado**: 2026-05-17
**Autor**: Kiro AI Assistant
**Versión**: 1.0
