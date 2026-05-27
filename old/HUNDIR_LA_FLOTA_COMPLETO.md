# 🚢 HUNDIR LA FLOTA - Documentación Completa

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Características](#características)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Flujo del Juego](#flujo-del-juego)
5. [Gestión por DVD (Admin)](#gestión-por-dvd-admin)
6. [Interfaz de Jugador](#interfaz-de-jugador)
7. [Sistema de Turnos](#sistema-de-turnos)
8. [Videos y Efectos](#videos-y-efectos)
9. [API y WebSockets](#api-y-websockets)
10. [Instalación y Configuración](#instalación-y-configuración)

---

## 🎮 Descripción General

**Hundir la Flota** es una implementación completa del clásico juego de estrategia naval (Battleship) integrada en el sistema DVDcoin. Permite partidas multijugador (2-4 jugadores) con gestión completa por administrador, sistema de turnos, efectos visuales y videos.

### Características Principales:
- ✅ **2-4 jugadores simultáneos**
- ✅ **Gestión completa por DVD en panel admin**
- ✅ **Colocación estratégica de barcos**
- ✅ **Sistema de turnos con temporizador**
- ✅ **Videos de impactos, fallos y hundimientos**
- ✅ **Tableros personalizables (8x8, 10x10, 12x12)**
- ✅ **Tiempo por turno configurable**
- ✅ **Efectos visuales y animaciones**
- ✅ **WebSocket en tiempo real**
- ✅ **Responsive design**

---

## 🏗️ Arquitectura del Sistema

### Componentes del Sistema:

```
hundir-la-flota/
├── Backend (main.py)
│   ├── HundirLaFlotaManager (Clase principal)
│   ├── API REST Endpoints
│   └── WebSocket Handler
├── Frontend
│   ├── game_pages/hundirlaflota/
│   │   ├── admin.html (Panel de administración)
│   │   └── game.html (Interfaz del juego)
│   └── static/hundirlaflota/
│       └── videos/ (Videos de efectos)
└── Documentación
    └── HUNDIR_LA_FLOTA_COMPLETO.md
```

### Tecnologías Utilizadas:
- **Backend**: Python, FastAPI, WebSockets, asyncio
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Comunicación**: WebSocket bidireccional
- **Efectos**: Videos MP4, CSS animations

---

## 🎯 Flujo del Juego

### 1. **Fase de Espera (waiting)**
- El juego está desactivado o esperando configuración
- Los jugadores ven un mensaje de espera

### 2. **Fase de Colocación (placement)**
- Cada jugador coloca sus 5 barcos en su tablero:
  - 🚢 **Portaaviones** (5 casillas)
  - ⛴️ **Acorazado** (4 casillas)
  - 🛳️ **Crucero** (3 casillas)
  - 🚤 **Submarino** (3 casillas)
  - ⛵ **Destructor** (2 casillas)
- Los jugadores pueden rotar los barcos (Horizontal/Vertical)
- Cuando todos los barcos están colocados, el jugador marca "Listo"
- La batalla comienza cuando todos los jugadores están listos

### 3. **Fase de Batalla (battle)**
- Los jugadores atacan por turnos
- Cada jugador ataca al siguiente jugador en la lista
- Resultados posibles:
  - 💥 **Impacto**: Acertaste una casilla con barco
  - 💦 **Agua**: Fallaste, no hay barco
  - 🔥 **Hundido**: Destruiste un barco completo
- El turno pasa al siguiente jugador automáticamente
- Jugadores eliminados (todos sus barcos hundidos) son saltados

### 4. **Fase Final (finished)**
- Gana el último jugador con barcos a flote
- Se muestra el ganador y estadísticas
- DVD puede reiniciar la partida

---

## 👨‍💼 Gestión por DVD (Admin)

### Panel de Administración (`/hundirlaflota/admin.html`)

#### Funcionalidades:

1. **Estado del Juego**
   - Indicador visual (activo/desactivado)
   - Botones de control:
     - ▶ Activar
     - ■ Desactivar
     - ↺ Reiniciar
     - ↗ Abrir juego

2. **Configuración de Partida**
   - **Tamaño del tablero**:
     - 8x8 (Rápido)
     - 10x10 (Clásico) ⭐
     - 12x12 (Épico)
   
   - **Tiempo por turno**:
     - 30 segundos
     - 60 segundos ⭐
     - 90 segundos
     - 120 segundos
     - Sin límite
   
   - **Selección de jugadores**:
     - Mínimo: 2 jugadores
     - Máximo: 4 jugadores
     - Búsqueda con autocompletado
     - Añadir/eliminar jugadores

3. **Monitoreo en Vivo**
   - Ver jugadores en partida
   - Estado de cada jugador (listo/colocando)
   - Barcos restantes de cada jugador
   - Jugador actual en turno

### Acciones del Administrador:

```javascript
// Activar/Desactivar juego
POST /api/hundirlaflota/toggle
{
  "enabled": true/false
}

// Configurar nueva partida
POST /api/hundirlaflota/setup
{
  "players": ["user1", "user2", "user3"],
  "board_size": 10,
  "turn_time": 60
}

// Reiniciar partida
POST /api/hundirlaflota/reset
```

---

## 🎮 Interfaz de Jugador

### Pantalla Principal (`/hundirlaflota/game.html`)

#### Elementos de la Interfaz:

1. **Header**
   - Logo del juego ⚓
   - Estado de la fase actual
   - Indicador de conexión

2. **Panel de Jugadores**
   - Tarjetas de todos los jugadores
   - Indicador de turno actual (▶)
   - Barcos restantes (🚢)
   - Barra de tiempo restante
   - Estado (listo/eliminado)

3. **Tablero Propio (Mi Flota)**
   - Visualización de tus barcos
   - Indicadores de impactos recibidos
   - Controles de colocación (fase placement)
   - Botón "Rotar" para cambiar orientación
   - Botón "Listo" cuando todos los barcos están colocados
   - Leyenda de colores

4. **Tablero Enemigo**
   - Tablero del siguiente jugador
   - Tus ataques previos
   - Casillas clickeables en tu turno
   - Indicadores de impactos/fallos
   - Lista de barcos enemigos (con estado hundido)

### Interacciones del Jugador:

#### Fase de Colocación:
1. Click en casilla del tablero propio
2. Se coloca el primer barco sin colocar
3. Usar botón "Rotar" para cambiar orientación
4. Repetir hasta colocar todos los barcos
5. Click en "Listo" para confirmar

#### Fase de Batalla:
1. Esperar tu turno
2. Click en casilla del tablero enemigo
3. Ver resultado (video + animación)
4. Esperar siguiente turno

---

## ⏱️ Sistema de Turnos

### Mecánica de Turnos:

1. **Orden de Turnos**
   - Los jugadores atacan en orden circular
   - Jugador 1 → Jugador 2 → Jugador 3 → Jugador 1...
   - Los jugadores eliminados son saltados automáticamente

2. **Temporizador**
   - Cada jugador tiene un tiempo límite por turno
   - El tiempo se muestra en la barra de progreso
   - Colores del temporizador:
     - 🟦 Azul: >50% tiempo restante
     - 🟨 Amarillo: 20-50% tiempo restante
     - 🟥 Rojo: <20% tiempo restante
   - Si se acaba el tiempo, el turno pasa automáticamente

3. **Cambio de Turno**
   - Automático después de cada ataque
   - Automático si se acaba el tiempo
   - Los jugadores ven claramente de quién es el turno

---

## 🎬 Videos y Efectos

### Sistema de Videos:

El juego reproduce videos automáticamente en eventos clave:

1. **hit.mp4** - Impacto en barco
   - Trigger: Cuando aciertas un disparo
   - Duración: 2-3 segundos
   - Efecto: Explosión, fuego

2. **miss.mp4** - Disparo fallido
   - Trigger: Cuando fallas (agua)
   - Duración: 2-3 segundos
   - Efecto: Salpicadura de agua

3. **sunk.mp4** - Barco hundido
   - Trigger: Cuando hundes un barco completo
   - Duración: 3-5 segundos
   - Efecto: Barco hundiéndose

4. **win.mp4** - Victoria
   - Trigger: Cuando ganas la partida
   - Duración: 3-5 segundos
   - Efecto: Celebración

5. **lose.mp4** - Derrota
   - Trigger: Cuando pierdes
   - Duración: 3-5 segundos
   - Efecto: Derrota

6. **start.mp4** - Inicio
   - Trigger: Al comenzar la partida
   - Duración: 3-5 segundos
   - Efecto: Preparación

### Efectos Visuales:

- **Animaciones CSS**:
  - `hitPulse`: Pulsación en impacto
  - `sinkShake`: Vibración al hundir
  - `explode`: Explosión rotativa
  - `pulse`: Pulsación continua
  - `fadeUp/fadeOut`: Mensajes flash

- **Indicadores Visuales**:
  - 🚢 Barcos propios
  - 💥 Impactos
  - 💦 Agua (fallos)
  - 💀 Barcos hundidos
  - ▶ Turno actual
  - ✓ Listo
  - 🎯 Objetivo

---

## 🔌 API y WebSockets

### Endpoints REST:

```python
# Estado del juego
GET /api/hundirlaflota/status
Response: {"enabled": true/false}

# Lista de usuarios
GET /api/hundirlaflota/users
Response: ["user1", "user2", ...]

# Activar/Desactivar
POST /api/hundirlaflota/toggle
Body: {"enabled": true/false}

# Configurar partida
POST /api/hundirlaflota/setup
Body: {
  "players": ["user1", "user2"],
  "board_size": 10,
  "turn_time": 60
}

# Reiniciar
POST /api/hundirlaflota/reset
```

### WebSocket:

```javascript
// Conexión
ws://host/ws/hundirlaflota?token=JWT_TOKEN

// Mensajes del servidor
{
  "type": "state",
  "enabled": true,
  "phase": "battle",
  "players": [...],
  "current_player_idx": 0,
  "setup": {...},
  "winner": null
}

{
  "type": "action",
  "action": "hit|miss|sunk|win",
  "ship": "carrier"  // si aplica
}

// Mensajes del cliente
{
  "action": "place_ship",
  "ship": "carrier",
  "row": 0,
  "col": 0,
  "orientation": "H"
}

{
  "action": "ready"
}

{
  "action": "attack",
  "row": 5,
  "col": 3
}
```

### Estructura de Estado:

```python
{
  "phase": "waiting|placement|battle|finished",
  "players": [
    {
      "username": "player1",
      "board": {
        "0,0": {"ship": "carrier", "hit": false},
        ...
      },
      "ships": {
        "carrier": {
          "size": 5,
          "placed": true,
          "positions": [(0,0), (0,1), ...],
          "hits": [(0,0)],
          "sunk": false
        },
        ...
      },
      "ready": true,
      "attacks": {
        "5,3": {"result": "hit"},
        ...
      },
      "eliminated": false,
      "time_remaining": 45
    },
    ...
  ],
  "current_player_idx": 0,
  "setup": {
    "board_size": 10,
    "turn_time": 60
  },
  "winner": null
}
```

---

## 🚀 Instalación y Configuración

### Requisitos:
- Python 3.8+
- FastAPI
- WebSockets
- Sistema DVDcoin existente

### Archivos Creados:

1. **Backend**:
   - `main.py` (código añadido al final)
   - Clase `HundirLaFlotaManager`
   - Endpoints y WebSocket handler

2. **Frontend**:
   - `game_pages/hundirlaflota/admin.html`
   - `game_pages/hundirlaflota/game.html`

3. **Assets**:
   - `static/hundirlaflota/videos/` (directorio para videos)
   - `static/hundirlaflota/videos/README.md` (guía de videos)

4. **Documentación**:
   - `HUNDIR_LA_FLOTA_COMPLETO.md` (este archivo)

### Pasos de Instalación:

1. **Verificar archivos**:
   ```bash
   # Verificar que existen los archivos
   ls game_pages/hundirlaflota/
   ls static/hundirlaflota/videos/
   ```

2. **Añadir videos** (opcional):
   - Descargar videos de Pixabay, Pexels, etc.
   - Colocar en `static/hundirlaflota/videos/`
   - Nombrar: hit.mp4, miss.mp4, sunk.mp4, win.mp4, lose.mp4, start.mp4

3. **Reiniciar servidor**:
   ```bash
   # Detener servidor actual
   # Iniciar servidor
   python main.py
   ```

4. **Acceder al juego**:
   - Admin: `http://localhost:8000/hundirlaflota/admin.html`
   - Juego: `http://localhost:8000/hundirlaflota/game.html`

### Integración con el Sistema:

Para añadir el juego al menú principal de DVDcoin, añadir en `static/index.html`:

```html
<a href="/hundirlaflota/admin.html" class="game-link">
  <span class="game-icon">⚓</span>
  <span class="game-name">Hundir la Flota</span>
</a>
```

---

## 🎯 Casos de Uso

### Caso 1: Partida Rápida (2 jugadores)
1. DVD abre panel admin
2. Selecciona tablero 8x8
3. Tiempo 30s por turno
4. Añade 2 jugadores
5. Click "Iniciar partida"
6. Los jugadores colocan barcos
7. Batalla rápida de 5-10 minutos

### Caso 2: Partida Épica (4 jugadores)
1. DVD configura tablero 12x12
2. Tiempo 90s por turno
3. Añade 4 jugadores
4. Partida larga y estratégica
5. Múltiples eliminaciones
6. Ganador final

### Caso 3: Torneo
1. DVD organiza múltiples partidas
2. Ganadores pasan a siguiente ronda
3. Final con mejores jugadores
4. Premio en DVDcoins

---

## 🐛 Solución de Problemas

### Problema: Videos no se reproducen
**Solución**: 
- Verificar que los archivos existen en `static/hundirlaflota/videos/`
- Verificar formato MP4 (H.264)
- El juego funciona sin videos, son opcionales

### Problema: WebSocket no conecta
**Solución**:
- Verificar token JWT válido
- Verificar que el servidor está corriendo
- Revisar logs del servidor

### Problema: No puedo colocar barcos
**Solución**:
- Verificar que hay espacio suficiente
- Probar rotar el barco
- Verificar que no hay barcos superpuestos

### Problema: El turno no cambia
**Solución**:
- Verificar que el ataque fue válido
- Esperar a que termine el video
- Revisar conexión WebSocket

---

## 📊 Estadísticas y Métricas

### Métricas del Juego:
- Partidas jugadas
- Tiempo promedio de partida
- Jugador con más victorias
- Barco más difícil de hundir
- Precisión de disparos

### Futuras Mejoras:
- [ ] Sistema de ranking
- [ ] Estadísticas por jugador
- [ ] Replay de partidas
- [ ] Chat en vivo
- [ ] Modo espectador
- [ ] Powerups especiales
- [ ] Diferentes tipos de barcos
- [ ] Modos de juego alternativos

---

## 📝 Notas Finales

Este juego está completamente integrado con el sistema DVDcoin y sigue las mismas convenciones que los otros juegos (Millonario, Pasapalabra, etc.).

**Características destacadas**:
- ✅ 100% funcional y jugable
- ✅ Gestión completa por DVD
- ✅ Sistema de turnos robusto
- ✅ Efectos visuales y videos
- ✅ Responsive y accesible
- ✅ WebSocket en tiempo real
- ✅ Código limpio y documentado

**Autor**: Kiro AI Assistant
**Fecha**: 2026
**Versión**: 1.0.0

---

## 🎮 ¡A Jugar!

El juego está listo para usar. Solo necesitas:
1. Reiniciar el servidor
2. Acceder al panel admin
3. Configurar una partida
4. ¡Disfrutar!

**¡Que gane el mejor estratega naval!** ⚓🚢💥
