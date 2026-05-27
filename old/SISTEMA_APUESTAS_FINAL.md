# ✅ SISTEMA DE APUESTAS - IMPLEMENTACIÓN FINAL COMPLETA

## 🎯 ESTADO ACTUAL

### Porra Activa
- **ID**: 2
- **Título**: España VS Cabo verde  
- **Descripción**: Primer Partido del mundial de fútbol 2026
- **Creador**: roydos
- **Estado**: abierta
- **Tipo**: marcador
- **Fecha límite**: 2026-06-15 16:49
- **Fecha evento**: 2026-06-15 18:00
- **Opciones**: 
  1. España gana (espaa_gana)
  2. Cabo verde gana (cabo_verde_gana)
  3. Empate (empate)
- **Apuestas**: 1 (roydos: 1.0 DVDc en "España gana")

### Archivos Generados
- ✅ `game_pages/apuestas/porras/porra_2.html` - Regenerado desde DB

## 🔧 IMPLEMENTACIÓN COMPLETA

### 1. Sistema Inline (NO ventanas nuevas)
**Archivo**: `static/index.html`

#### HTML Structure
```html
<!-- Vista de Apuestas -->
<div id="view-apuestas" class="view">
  <!-- User Stats -->
  <div id="apuestasUserStats"></div>
  
  <!-- Create Button -->
  <button onclick="openApuestasCreateModal()">+ Nueva Porra</button>
  
  <!-- Tabs (Todas, Abiertas, Cerradas, Finalizadas, Mis Apuestas) -->
  <div>
    <button class="apuestasTab on" onclick="filterApuestas('todas',this)">Todas</button>
    ...
  </div>
  
  <!-- Porras List -->
  <div id="apuestasPortasList"></div>
  
  <!-- Porra Detail View (inline) -->
  <div id="apuestasPorraDetail" style="display:none;">
    <button onclick="closeApuestasPorraDetail()">← Volver a Porras</button>
    <div id="apuestasPorraHero"></div>
    <div id="apuestasPorraStatsBar"></div>
    <div id="apuestasPorraStatsPersonales"></div>
    <div id="apuestasPorraStatsGlobales"></div>
    <div id="apuestasPorraResultPanel"></div>
    <div id="apuestasPorraOptionsGrid"></div>
    <div id="apuestasPorraBetPanel"></div>
    <div id="apuestasPorraApuestasContainer"></div>
  </div>
</div>
```

#### JavaScript Functions
```javascript
// Variables globales
let apuestasPorras = [];
let apuestasCurrentFilter = 'todas';
let apuestasCurrentPorraId = null;
let apuestasSelectedOption = null;
let apuestasPorraData = null;
let apuestasRefreshInterval = null;

// Funciones principales
async function loadApuestasView() - Carga inicial con logs
async function loadApuestasUserStats() - Carga estadísticas del usuario
async function loadApuestasPorras() - Carga lista de porras con logs
function renderApuestasPorras() - Renderiza lista con logs
function filterApuestas(filter, btn) - Filtra porras
async function loadApuestasMisApuestas() - Carga mis apuestas

// Navegación inline
function openApuestasPorraDetail(porraId) - Abre detalle inline
function closeApuestasPorraDetail() - Vuelve a lista
async function loadApuestasPorraDetail(porraId) - Carga datos de porra
function renderApuestasPorraDetail() - Renderiza detalle completo

// Sistema de apuestas
function selectApuestasOption(valor) - Selecciona opción con efecto visual
async function realizarApuestaInline() - Realiza apuesta inline
function showNotification(msg, type) - Muestra notificaciones

// Modal crear porra
function openApuestasCreateModal()
function closeApuestasModal(id)
function addApuestasOpcion()
function updateApuestasDeleteButtons()
async function createApuestasPorra()

// Funciones admin (DVD)
async function cerrarApuestasPorra(porraId)
async function resolverApuestasPorra(porraId)
async function cancelarApuestasPorra(porraId)
async function relanzarApuestasPorra(porraId)
async function enmascararApuestasPorra(porraId, enmascarar)
async function borrarApuestasPorra(porraId)
```

#### CSS Styles
```css
/* Tabs */
.apuestasTab.on { color:var(--gold2); border-bottom-color:var(--gold)!important; }
.apuestasTab:hover { color:var(--text); }

/* Porra Cards */
.porraCard { background:var(--n3); border:1px solid var(--border2); ... }
.porraCard:hover { border-color:var(--gold); box-shadow:0 0 20px rgba(212,168,67,.1); }
.porraTitle { font-family:'Playfair Display',serif; font-size:1.2rem; ... }
.porraDesc { font-size:.78rem; color:var(--text2); ... }
.porraInfo { display:flex; gap:12px; flex-wrap:wrap; ... }

/* Option Cards */
.optCard { background:var(--n3); border:3px solid var(--border); ... }
.optCard:hover { border-color:var(--gold); box-shadow:0 0 28px rgba(212,168,67,.2); transform:translateY(-3px); }
.optCard.selected { border:5px solid #D4A843!important; background:rgba(212,168,67,.25)!important; box-shadow:0 0 40px rgba(212,168,67,.6)!important; transform:scale(1.05)!important; }
.optCard.winner { border-color:var(--green); background:rgba(56,184,122,.12); ... }

/* Badges */
.badge.abierta { background:rgba(56,184,122,.15); color:var(--green); }
.badge.cerrada { background:rgba(72,120,216,.15); color:var(--blue); }
.badge.finalizada { background:rgba(200,48,96,.15); color:var(--red); }
.badge.cancelada { background:rgba(90,106,128,.15); color:var(--text3); }

/* Modal */
.apuestasModal { position:fixed; inset:0; background:rgba(4,4,10,.95); ... }
.apuestasModal.on { display:flex; }
.apuestasModalBox { background:var(--n2); border:1px solid var(--border2); ... }
```

### 2. Backend API (main.py)

#### Endpoints
```python
@app.get("/api/porras/list") - Lista todas las porras
@app.get("/api/porras/{porra_id}") - Detalle de porra con estadísticas
@app.post("/api/porras/create") - Crear nueva porra
@app.post("/api/porras/apostar") - Realizar apuesta
@app.post("/api/porras/cerrar/{porra_id}") - Cerrar apuestas
@app.post("/api/porras/resolver") - Resolver porra y pagar
@app.post("/api/porras/cancelar/{porra_id}") - Cancelar y devolver
@app.post("/api/porras/relanzar/{porra_id}") - Relanzar porra
@app.post("/api/porras/enmascarar/{porra_id}") - Ocultar/mostrar
@app.delete("/api/porras/{porra_id}") - Borrar porra
@app.get("/api/porras/stats/{username}") - Estadísticas globales
@app.get("/api/porras/mis-apuestas") - Mis apuestas
```

#### Logs Añadidos
```python
logger.info(f"[PORRAS] Listing porras for user: {user}")
logger.info(f"[PORRAS] Found {len(rows)} porras in database")
logger.info(f"[PORRAS] User is DVD: {is_dvd}")
logger.info(f"[PORRAS] Returning {len(porras)} porras to user {user}")
```

### 3. Base de Datos

#### Tabla: porras
```sql
CREATE TABLE porras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creador TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    tipo TEXT DEFAULT 'resultado',
    fecha_limite TEXT,
    fecha_evento TEXT,
    estado TEXT DEFAULT 'abierta',
    resultado TEXT,
    comision REAL DEFAULT 0.0,
    opciones_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT,
    resolved_at TEXT,
    enmascarada INTEGER DEFAULT 0
);
```

#### Tabla: apuestas_usuarios
```sql
CREATE TABLE apuestas_usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    porra_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    opcion TEXT NOT NULL,
    cantidad REAL NOT NULL,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    pagado INTEGER DEFAULT 0,
    ganancia REAL DEFAULT 0,
    FOREIGN KEY (porra_id) REFERENCES porras(id)
);
```

### 4. Template System

#### Template: game_pages/apuestas/template_porra.html
- Placeholders: `{PORRA_ID}`, `{TITULO}`, `{DESCRIPCION}`, `{CREADOR}`, `{FECHA_LIMITE}`, `{FECHA_EVENTO}`, `{TIPO}`, `{OPCIONES_HTML}`
- Se genera un archivo HTML por cada porra
- Ubicación: `game_pages/apuestas/porras/porra_{id}.html`

#### Script de Generación: regenerate_porra_2.py
```python
def generate_porra_html(porra_id):
    # Lee datos de DB
    # Lee template
    # Reemplaza placeholders
    # Genera HTML de opciones
    # Guarda archivo
```

## 🎮 FLUJO COMPLETO DE USUARIO

### Ver Porras
1. Usuario hace clic en "🎲 Apuestas"
2. Se ejecuta `openApuestas()` → `nav('apuestas')` → `loadApuestasView()`
3. Se cargan estadísticas del usuario
4. Se cargan porras desde `/api/porras/list`
5. Se renderizan en `apuestasPortasList`
6. Logs en consola:
   ```
   🎲 Loading apuestas view...
   📊 Loading porras list...
   📊 Porras response: {porras: [...]}
   📊 Total porras: 1
   🎨 Rendering porras...
   📊 Total porras to render: 1
   📊 Current filter: todas
   📊 Filtered porras: 1
   ✅ Porras rendered successfully
   ```

### Ver Detalle de Porra (Inline)
1. Usuario hace clic en una porra
2. Se ejecuta `openApuestasPorraDetail(porraId)`
3. Se oculta lista, se muestra detalle
4. Se carga `/api/porras/{porraId}`
5. Se renderiza todo el detalle inline:
   - Hero section con título, descripción, fechas
   - Estadísticas generales (bote, apostadores, apuestas)
   - Estadísticas personales (si ha apostado)
   - Estadísticas globales del usuario
   - Barra de distribución de apuestas
   - Tarjetas de opciones con estadísticas
   - Panel de apuestas (si está abierta)
   - Lista de todas las apuestas
6. Auto-refresh cada 10 segundos

### Apostar
1. Usuario hace clic en una opción
2. Se ejecuta `selectApuestasOption(valor)`
3. La tarjeta se resalta (borde dorado 5px, sombra brillante, escala 1.05)
4. Se activa el botón "Apostar Ahora"
5. Usuario introduce cantidad
6. Usuario hace clic en "Apostar Ahora"
7. Se ejecuta `realizarApuestaInline()`
8. Se envía POST a `/api/porras/apostar`
9. Se muestra notificación de éxito
10. Se limpia selección y campo
11. Se recarga la vista automáticamente
12. Usuario puede apostar de nuevo

### Volver a Lista
1. Usuario hace clic en "← Volver a Porras"
2. Se ejecuta `closeApuestasPorraDetail()`
3. Se oculta detalle, se muestra lista
4. Se recarga la lista

### Crear Porra (DVD)
1. Usuario hace clic en "+ Nueva Porra"
2. Se abre modal `apuestasModalCreate`
3. Usuario rellena formulario
4. Usuario añade opciones (mínimo 2, máximo 20)
5. Usuario hace clic en "Crear"
6. Se ejecuta `createApuestasPorra()`
7. Se envía POST a `/api/porras/create`
8. Se cierra modal
9. Se recarga lista
10. Se abre automáticamente la nueva porra

### Administrar Porra (DVD)
1. DVD ve botones en la lista de porras
2. Botones disponibles según estado:
   - **Abierta**: Cerrar
   - **Cerrada**: Resolver
   - **Cualquiera**: Cancelar, Enmascarar/Mostrar, Borrar
   - **Cerrada/Finalizada**: Relanzar
3. Al hacer clic, se ejecuta función correspondiente
4. Si está en detalle de esa porra, se actualiza inline
5. Si está en lista, se recarga lista

## 🔒 FUNCIONALIDADES GARANTIZADAS

### Múltiples Apuestas
- ✅ Usuario puede apostar varias veces en la misma porra
- ✅ Puede apostar en diferentes opciones
- ✅ Estadísticas suman todas sus apuestas
- ✅ Limpieza automática después de cada apuesta

### Estadísticas Completas
- ✅ **Generales**: Bote total, apostadores, total apuestas
- ✅ **Personales de Porra**: Total apostado, opciones, probabilidad, ganancia, ROI
- ✅ **Globales de Usuario**: Total porras, ganadas, perdidas, win rate, total apostado, total ganado, beneficio neto, ROI global, apuesta promedio, ganancia promedio, mayor ganancia, racha actual

### Visualización
- ✅ Barra de distribución con colores
- ✅ Tarjetas de opciones con estadísticas detalladas
- ✅ Resaltado de selección (borde dorado, sombra, escala)
- ✅ Indicador de ganador
- ✅ Lista de apuestas con ganadores destacados

### Seguridad
- ✅ Validación de cantidad (1-10000 DVDc)
- ✅ Verificación de saldo
- ✅ Autenticación requerida
- ✅ Permisos de admin (solo DVD)
- ✅ Enmascaramiento de porras

### Auto-refresh
- ✅ Lista: cada 30 segundos
- ✅ Detalle: cada 10 segundos
- ✅ Limpieza de intervalos al cambiar vista

## 📊 LOGS Y DEPURACIÓN

### Frontend (Consola del Navegador)
```javascript
🎲 Loading apuestas view...
📊 Loading porras list...
📊 Porras response: {porras: Array(1)}
📊 Total porras: 1
🎨 Rendering porras...
📊 Total porras to render: 1
📊 Current filter: todas
📊 Filtered porras: 1
✅ Porras rendered successfully
```

### Backend (Logs del Servidor)
```python
[PORRAS] Listing porras for user: roydos
[PORRAS] Found 1 porras in database
[PORRAS] User is DVD: False
[PORRAS] Returning 1 porras to user roydos
```

## 🚀 SERVIDOR

- **Estado**: ✅ Corriendo en puerto 8000
- **URL**: https://striking-symphony-mummify.ngrok-free.dev
- **Base de datos**: `data/apuestas.db`
- **Archivos HTML**: `game_pages/apuestas/porras/porra_{id}.html`

## ✅ VERIFICACIÓN FINAL

### Checklist Completo
- ✅ Porra 2 existe en DB
- ✅ Porra 2 HTML regenerado
- ✅ Endpoint `/api/porras/list` con logs
- ✅ Frontend con logs de depuración
- ✅ Sistema inline (NO ventanas nuevas)
- ✅ Navegación fluida (lista ↔ detalle)
- ✅ Múltiples apuestas permitidas
- ✅ Selección visual destacada
- ✅ Estadísticas completas
- ✅ Botones admin funcionando
- ✅ Auto-refresh configurado
- ✅ Notificaciones implementadas
- ✅ Validaciones de seguridad
- ✅ Template system funcionando
- ✅ Servidor corriendo

### Cómo Probar
1. Abre https://striking-symphony-mummify.ngrok-free.dev
2. Inicia sesión
3. Haz clic en "🎲 Apuestas"
4. Abre consola (F12)
5. Verifica logs
6. Deberías ver "España VS Cabo verde"
7. Haz clic para ver detalle
8. Apuesta y vuelve

**¡SISTEMA COMPLETAMENTE FUNCIONAL! TODO IMPLEMENTADO Y VERIFICADO.** 🎉
