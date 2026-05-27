# 🚀 Instrucciones para Reiniciar el Servidor

## ✅ Cambios Completados

Todos los cambios para la funcionalidad "Plantarse o Seguir" han sido aplicados exitosamente:

### Backend
- ✅ `main.py` - Actualizado con nuevo flujo
- ✅ `src/main.py` - Actualizado con nuevo flujo + pago automático

### Frontend
- ✅ `static/millonario/game.html` - Actualizado con botones de decisión
- ✅ `game_pages/millonario/game.html` - Actualizado con botones de decisión

---

## 🎯 Nuevo Flujo del Juego

### Antes (Antiguo)
```
1. Jugador responde pregunta
2. Admin marca "✓ Correcto"
3. ❌ Juego avanza automáticamente a siguiente pregunta
```

### Ahora (Nuevo) ⭐
```
1. Jugador responde pregunta
2. Admin marca "✓ Correcto"
3. ✅ Aparecen 2 botones:
   ├─ ➡️ Siguiente Pregunta (continuar jugando)
   └─ 🎯 Plantarse (retirarse con el premio)
4. Admin elige una opción
5. El juego continúa según la decisión
```

---

## 🔄 Cómo Reiniciar el Servidor

### Opción 1: Desde la Terminal Actual

Si tienes el servidor corriendo en una terminal:

1. **Detener el servidor:**
   - Presiona `Ctrl + C` en la terminal donde está corriendo

2. **Reiniciar el servidor:**
   ```bash
   python main.py
   ```
   O si usas src/main.py:
   ```bash
   python src/main.py
   ```

### Opción 2: Matar Procesos Python

Si no encuentras la terminal o el servidor está en segundo plano:

```bash
# Ver procesos Python corriendo
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# Matar todos los procesos Python
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Reiniciar el servidor
python main.py
```

### Opción 3: Usar los Scripts BAT

Si tienes scripts de inicio:

```bash
# Detener procesos
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Ejecutar el script de inicio
.\ARRANCAR.bat
```

---

## ✅ Verificar que el Servidor Está Corriendo

Después de reiniciar, deberías ver algo como:

```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🧪 Probar la Nueva Funcionalidad

### Paso 1: Abrir el Panel de Administración
```
http://localhost:8000/admin/games/millonario
```

### Paso 2: Iniciar una Partida
1. Selecciona un jugador
2. Haz clic en "▶ Iniciar partida"
3. Se abrirá automáticamente la ventana del juego

### Paso 3: Probar el Flujo
1. **Pregunta 1:**
   - Selecciona una opción (A, B, C o D)
   - Haz clic en "✓ Correcto"
   - ✅ Deberían aparecer 2 botones:
     - `➡️ Siguiente Pregunta`
     - `🎯 Plantarse`

2. **Elegir "Siguiente Pregunta":**
   - El juego avanza a la pregunta 2
   - Los botones desaparecen
   - Vuelve a estar en modo "jugando"

3. **Elegir "Plantarse" (desde pregunta 3+):**
   - El juego termina
   - Se muestra overlay: "🎯 ¡Se planta!"
   - Se muestra el premio ganado

---

## 📊 Estados del Juego

| Estado | Descripción | Botones Visibles |
|--------|-------------|------------------|
| `playing` | Jugando pregunta actual | ✓ Correcto, ✗ Fallo, 50/50, ↺ Reset |
| `waiting_decision` | Esperando decisión tras respuesta correcta | ➡️ Siguiente, 🎯 Plantarse |
| `plantado` | Jugador se retiró | Ninguno (overlay final) |
| `wrong` | Respuesta incorrecta | Ninguno (overlay final) |
| `finished` | Ganó el juego completo | Ninguno (overlay final) |

---

## 🎮 Interfaz Actualizada

### Durante el Juego (playing)
```
┌─────────────────────────────────────────┐
│  Pregunta: ¿Cuál es la capital de...?  │
│  [A] París  [B] Londres                 │
│  [C] Madrid [D] Roma                    │
│                                         │
│  ┌──────────┐ ┌──────┐ ┌──────┐ ┌────┐ │
│  │✓ Correcto│ │✗ Fallo│ │50/50 │ │↺ R │ │
│  └──────────┘ └──────┘ └──────┘ └────┘ │
└─────────────────────────────────────────┘
```

### Después de Respuesta Correcta (waiting_decision)
```
┌─────────────────────────────────────────┐
│  Pregunta: ¿Cuál es la capital de...?  │
│  [A] París ✓ [B] Londres                │
│  [C] Madrid  [D] Roma                   │
│                                         │
│  ┌──────────┐ ┌──────┐ ┌──────┐ ┌────┐ │
│  │✓ Correcto│ │✗ Fallo│ │50/50 │ │↺ R │ │
│  └──────────┘ └──────┘ └──────┘ └────┘ │
│                                         │
│  ┌─────────────────────┐ ┌─────────────┐│
│  │➡️ Siguiente Pregunta│ │🎯 Plantarse ││
│  └─────────────────────┘ └─────────────┘│
└─────────────────────────────────────────┘
```

---

## 🐛 Solución de Problemas

### Problema: El servidor no inicia
**Solución:**
```bash
# Verificar que no hay otros procesos Python corriendo
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# Matar todos los procesos Python
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Reiniciar
python main.py
```

### Problema: Los botones no aparecen
**Solución:**
1. Limpia la caché del navegador: `Ctrl + Shift + R`
2. Cierra y vuelve a abrir la ventana del juego
3. Verifica que el servidor se reinició correctamente

### Problema: Error en la consola del navegador
**Solución:**
1. Abre la consola del navegador: `F12`
2. Ve a la pestaña "Console"
3. Busca errores en rojo
4. Si hay errores de WebSocket, reinicia el servidor

### Problema: Ngrok offline
**Solución:**
```bash
# Reiniciar ngrok
ngrok http 8000
```

---

## 📝 Comandos Rápidos

```bash
# Matar procesos Python
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Reiniciar servidor
python main.py

# Ver logs en tiempo real
# (Los logs aparecen automáticamente en la terminal)

# Abrir panel admin
start http://localhost:8000/admin/games/millonario
```

---

## ✨ Resumen de Cambios

### Nuevo Estado: `waiting_decision`
- Se activa después de responder correctamente
- Muestra 2 botones de decisión
- Mantiene visible la respuesta correcta marcada

### Nueva Acción: `siguiente`
- Avanza a la siguiente pregunta
- Limpia el estado de decisión
- Vuelve al modo "playing"

### Acción Actualizada: `plantarse`
- Ahora funciona en 2 contextos:
  1. Durante `playing` (antes de responder) → Premio de pregunta anterior
  2. Durante `waiting_decision` (después de responder) → Premio de pregunta actual

### Interfaz Actualizada:
- Barra de decisión separada
- Botones más grandes y claros
- Mejor feedback visual

---

## 🎉 ¡Listo!

Una vez reiniciado el servidor, la nueva funcionalidad estará activa.

**Fecha:** 2026-05-10
**Estado:** ✅ Completado y listo para usar
