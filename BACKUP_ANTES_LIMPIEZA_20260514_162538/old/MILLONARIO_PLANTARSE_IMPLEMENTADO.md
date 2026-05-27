# ✅ Millonario - Funcionalidad "Plantarse" Implementada

## Resumen
Se ha implementado la funcionalidad de **"Plantarse o Seguir"** en el juego Millonario, permitiendo al jugador retirarse con el premio acumulado a partir de la pregunta 3.

---

## 🎯 Funcionalidad Implementada

### Reglas del Juego
- **A partir de la pregunta 3**: El jugador puede decidir plantarse y llevarse el premio de la última pregunta respondida correctamente
- **Antes de la pregunta 3**: No se puede plantarse (el botón no aparece)
- **Premio al plantarse**: Se otorga el premio de la pregunta anterior (ya respondida correctamente)
- **Estado final**: El juego termina con estado "plantado" y muestra el premio ganado

### Ejemplo de Premios
Si el jugador está en la **pregunta 3** y decide plantarse:
- Se lleva el premio de la **pregunta 2** (ya respondida correctamente)
- No arriesga el premio intentando responder la pregunta 3

---

## 📝 Cambios Realizados

### 1. Backend (main.py y src/main.py)

#### Acción "plantarse" agregada en `MillonarioManager.handle_action()`

```python
elif action == "plantarse":
    # Player decides to stop and take current prize
    if self._state["status"] != "playing":
        return
    nivel = self._state["nivel"]
    if nivel < 3:
        # Cannot stop before question 3
        return
    # Get prize from previous level (already answered correctly)
    # If at level 3, player gets prize from level 2 (index 1)
    premio_idx = nivel - 2  # Previous question prize
    if 0 <= premio_idx < len(PREMIOS):
        self._state["ultimo_premio"] = PREMIOS[premio_idx]
    else:
        self._state["ultimo_premio"] = "0 DVDcoins"
    self._state["status"] = "plantado"
    await self.broadcast()
```

**Características:**
- ✅ Valida que el juego esté en estado "playing"
- ✅ Valida que el nivel sea >= 3
- ✅ Calcula el premio de la pregunta anterior (nivel - 2)
- ✅ Actualiza el estado a "plantado"
- ✅ Transmite el cambio a todos los clientes conectados

**Nota sobre pagos:** En `src/main.py` existe lógica adicional para pagar automáticamente al jugador. En `main.py` esta lógica no está presente, por lo que el pago debe gestionarse manualmente desde el panel de administración.

---

### 2. Frontend (static/millonario/game.html)

#### A. Botón "Plantarse" agregado en el HTML

```html
<button class="btn btnO btnSm" id="btnPlantarse" 
        onclick="ws.send(JSON.stringify({action:'plantarse'}))" 
        style="display:none">
  🎯 Plantarse
</button>
```

**Ubicación:** En la barra de administración (`adminBar`), entre los botones "Fallo" y "50/50"

#### B. Lógica de visualización en la función `render()`

```javascript
// Plantarse button - show from question 3 onwards
const bp=document.getElementById('btnPlantarse');
if(bp){
  if(st.nivel >= 3 && st.status === 'playing'){
    bp.style.display='';
    bp.disabled=false;
  }else{
    bp.style.display='none';
  }
}
```

**Características:**
- ✅ Solo visible cuando `nivel >= 3`
- ✅ Solo visible cuando el estado es "playing"
- ✅ Se oculta automáticamente en otros estados

#### C. Estado "plantado" agregado en la función `render()`

```javascript
if(st.status==='plantado'){
  showOv('🎯 ¡Se planta!',`@${st.player} se retira con: ${st.ultimo_premio||'nada'}`,st.ultimo_premio);
  return;
}
```

**Características:**
- ✅ Muestra overlay con mensaje de plantarse
- ✅ Muestra el jugador y el premio ganado
- ✅ Formato consistente con otros estados finales (wrong, finished)

---

## 🎮 Flujo de Juego

### Escenario: Jugador se planta en la pregunta 5

1. **Pregunta 1** → Responde correctamente → Gana 10 DVDcoins
2. **Pregunta 2** → Responde correctamente → Gana 20 DVDcoins
3. **Pregunta 3** → Responde correctamente → Gana 30 DVDcoins
4. **Pregunta 4** → Responde correctamente → Gana 50 DVDcoins
5. **Pregunta 5** → **Se planta** → Se lleva **50 DVDcoins** (premio de pregunta 4)

### Estados del Juego

| Estado | Descripción | Overlay |
|--------|-------------|---------|
| `waiting` | Esperando inicio de partida | "Esperando a que comience la partida…" |
| `playing` | Jugador respondiendo preguntas | No (muestra interfaz de juego) |
| `revealing` | Mostrando resultado de respuesta | No (transición rápida) |
| `plantado` | Jugador se retiró | "🎯 ¡Se planta! @usuario se retira con: X DVDcoins" |
| `wrong` | Respuesta incorrecta | "😔 Respuesta incorrecta @usuario se lleva: X DVDcoins" |
| `finished` | Ganó el juego completo | "🏆 ¡¡Enhorabuena!! @usuario gana la máxima cifra" |

---

## 🎨 Interfaz de Usuario

### Botón "Plantarse"
- **Color:** Dorado (clase `btnO`)
- **Icono:** 🎯
- **Texto:** "Plantarse"
- **Posición:** Barra de administración, entre "Fallo" y "50/50"
- **Visibilidad:** Solo desde pregunta 3 en adelante

### Overlay de Plantarse
- **Título:** "🎯 ¡Se planta!"
- **Mensaje:** "@[jugador] se retira con: [premio]"
- **Premio destacado:** Tamaño grande, color dorado

---

## 🔧 Archivos Modificados

1. **main.py** (líneas ~4470-4560)
   - Agregada acción "plantarse" en `MillonarioManager.handle_action()`

2. **src/main.py** (líneas ~4620-4680)
   - Agregada acción "plantarse" con lógica de pago automático

3. **static/millonario/game.html**
   - Agregado botón "Plantarse" en HTML
   - Agregada lógica de visualización en función `render()`
   - Agregado manejo de estado "plantado"

---

## ✅ Testing Recomendado

### Casos de Prueba

1. **Pregunta 1-2**: Verificar que el botón "Plantarse" NO aparece
2. **Pregunta 3**: Verificar que el botón "Plantarse" aparece
3. **Plantarse en pregunta 3**: Verificar que se otorga el premio de pregunta 2
4. **Plantarse en pregunta 5**: Verificar que se otorga el premio de pregunta 4 (garantizado)
5. **Plantarse en pregunta 10**: Verificar que se otorga el premio de pregunta 9
6. **Estado final**: Verificar que el overlay muestra correctamente el premio

### Comandos de Testing

```bash
# 1. Reiniciar el servidor
python main.py

# 2. Abrir panel de administración como DVD
# http://localhost:8000/admin/games/millonario

# 3. Iniciar una partida de Millonario

# 4. Abrir el juego desde el botón "↗ Abrir juego"

# 5. Responder correctamente las preguntas 1 y 2

# 6. En la pregunta 3, verificar que aparece el botón "🎯 Plantarse"

# 7. Hacer clic en "Plantarse" y verificar:
#    - El overlay muestra "🎯 ¡Se planta!"
#    - El premio mostrado es el de la pregunta 2 (20 DVDcoins)
```

---

## 📊 Estructura de Premios

### Premios por Nivel (main.py)
```python
PREMIOS = [
    "10 DVDcoins",   # Nivel 1
    "20 DVDcoins",   # Nivel 2
    "30 DVDcoins",   # Nivel 3
    "50 DVDcoins",   # Nivel 4
    "75 DVDcoins",   # Nivel 5 (garantizado)
    "100 DVDcoins",  # Nivel 6
    "150 DVDcoins",  # Nivel 7
    "250 DVDcoins",  # Nivel 8
    "500 DVDcoins",  # Nivel 9
    "1000 DVDcoins"  # Nivel 10 (garantizado)
]

GARANTIZADOS = {5: "75 DVDcoins", 10: "1000 DVDcoins"}
```

### Premios por Nivel (src/main.py)
```python
PREMIOS = [
    "100 DVDcoins",   # Nivel 1
    "250 DVDcoins",   # Nivel 2
    "500 DVDcoins",   # Nivel 3
    "750 DVDcoins",   # Nivel 4
    "1000 DVDcoins",  # Nivel 5 (garantizado)
    "1500 DVDcoins",  # Nivel 6
    "2000 DVDcoins",  # Nivel 7
    "3000 DVDcoins",  # Nivel 8
    "4000 DVDcoins",  # Nivel 9
    "5000 DVDcoins"   # Nivel 10 (garantizado)
]

GARANTIZADOS = {5: "1000 DVDcoins", 10: "5000 DVDcoins"}
```

---

## 🚀 Próximos Pasos

### Mejoras Opcionales

1. **Confirmación antes de plantarse**
   - Agregar un diálogo de confirmación: "¿Estás seguro de que quieres plantarte?"
   
2. **Animación de plantarse**
   - Agregar una animación especial cuando el jugador se planta
   
3. **Historial de decisiones**
   - Registrar en la base de datos cuándo un jugador se planta
   
4. **Estadísticas**
   - Mostrar estadísticas de cuántos jugadores se plantan en cada nivel

---

## 📌 Notas Importantes

- ⚠️ El botón "Plantarse" solo es visible para administradores (DVD)
- ⚠️ El jugador no puede plantarse antes de la pregunta 3
- ⚠️ Al plantarse, el juego termina inmediatamente
- ⚠️ El premio otorgado es siempre el de la pregunta anterior (ya respondida)
- ⚠️ En `src/main.py` el pago es automático, en `main.py` es manual

---

## ✨ Conclusión

La funcionalidad de "Plantarse" ha sido implementada exitosamente en el juego Millonario, proporcionando una experiencia de juego más completa y estratégica. Los jugadores ahora pueden decidir si arriesgar su premio acumulado o retirarse con seguridad a partir de la pregunta 3.

**Estado:** ✅ Implementado y listo para testing
**Fecha:** 2026-05-10
