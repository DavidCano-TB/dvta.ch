# 🧪 TEST HUNDIR LA FLOTA - GUÍA PASO A PASO

## 🎯 OBJETIVO
Verificar que todas las mejoras implementadas funcionan correctamente.

---

## ✅ CHECKLIST DE PRUEBAS

### 📋 PREPARACIÓN
- [ ] Servidor iniciado (`ABRIR_APUESTAS.bat`)
- [ ] Login como admin (usuario: dvd)
- [ ] Panel de admin abierto

---

## 🧪 TEST 1: CONFIGURACIÓN PERSONALIZADA DE FLOTA

### Pasos:
1. [ ] Ir a Admin → Hundir la Flota
2. [ ] En "Configuración de flota", modificar valores:
   - Portaaviones: `2`
   - Acorazado: `1`
   - Crucero: `2`
   - Submarino: `0`
   - Destructor: `3`
3. [ ] Añadir 2 jugadores
4. [ ] Click "Iniciar partida"

### Verificar:
- [ ] La partida se inicia correctamente
- [ ] Se abre la ventana del juego

---

## 🧪 TEST 2: PANTALLA DE COLOCACIÓN

### Pasos:
1. [ ] Abrir el juego en 2 ventanas (una por jugador)
2. [ ] Verificar que **solo se ve el tablero propio**
3. [ ] Verificar que **NO se ve el tablero enemigo**

### Verificar:
- [ ] Solo aparece "🛡️ Tu Flota"
- [ ] No aparece "🎯 Tablero Enemigo"
- [ ] Mensaje: "📝 Fase de preparación — Coloca tus barcos"

---

## 🧪 TEST 3: COLOCACIÓN DE BARCOS - HORIZONTAL

### Pasos:
1. [ ] Click en "➡️ Horizontal" (debe estar activo por defecto)
2. [ ] Click en "🚢 Portaaviones (5) [2]"
3. [ ] Click en tablero en posición superior izquierda

### Verificar:
- [ ] Barco se coloca horizontalmente (5 celdas seguidas →)
- [ ] Celdas se pintan de azul
- [ ] Contador cambia a [1]
- [ ] Mensaje: "✓ Barco colocado"

---

## 🧪 TEST 4: COLOCACIÓN DE BARCOS - VERTICAL

### Pasos:
1. [ ] Click en "⬇️ Vertical"
2. [ ] Click en "⛴️ Acorazado (4) [1]"
3. [ ] Click en tablero en otra posición

### Verificar:
- [ ] Barco se coloca verticalmente (4 celdas seguidas ↓)
- [ ] Celdas se pintan de azul
- [ ] Contador cambia a [0]
- [ ] Botón se grisea (disabled)

---

## 🧪 TEST 5: VALIDACIÓN DE COLISIONES

### Pasos:
1. [ ] Intentar colocar un barco sobre otro ya colocado

### Verificar:
- [ ] Mensaje de error: "❌ Ya hay un barco en esa posición"
- [ ] El barco NO se coloca
- [ ] Contador NO cambia

---

## 🧪 TEST 6: VALIDACIÓN DE LÍMITES

### Pasos:
1. [ ] Intentar colocar un barco que se salga del tablero

### Verificar:
- [ ] Mensaje de error: "❌ El barco no cabe en esa posición"
- [ ] El barco NO se coloca
- [ ] Contador NO cambia

---

## 🧪 TEST 7: SELECCIONAR BARCO

### Pasos:
1. [ ] Click en un barco ya colocado

### Verificar:
- [ ] El barco se resalta en **dorado**
- [ ] Aparece botón "↔️ Mover"
- [ ] La orientación se actualiza según el barco

---

## 🧪 TEST 8: MOVER BARCO

### Pasos:
1. [ ] Seleccionar un barco (click en él)
2. [ ] Click en "↔️ Mover"
3. [ ] Click en nueva posición válida

### Verificar:
- [ ] Mensaje: "📍 Haz click en el tablero para colocar el barco..."
- [ ] Al hacer click, el barco se mueve
- [ ] Mensaje: "✓ Barco movido correctamente"
- [ ] El barco mantiene su orientación

---

## 🧪 TEST 9: BORRAR BARCO

### Pasos:
1. [ ] Seleccionar un barco (click en él)
2. [ ] Click en "🗑️ Borrar"

### Verificar:
- [ ] El barco desaparece del tablero
- [ ] Contador aumenta en 1
- [ ] Botón se deshabilita si estaba grisado
- [ ] Mensaje: "✓ Barco eliminado"

---

## 🧪 TEST 10: LIMPIAR TODO

### Pasos:
1. [ ] Colocar varios barcos
2. [ ] Click en "↺ Limpiar todo"
3. [ ] Confirmar en el diálogo

### Verificar:
- [ ] Todos los barcos desaparecen
- [ ] Todos los contadores vuelven a su valor inicial
- [ ] Todos los botones se habilitan
- [ ] Mensaje: "✓ Todos los barcos eliminados"

---

## 🧪 TEST 11: BOTÓN VALIDAR

### Pasos:
1. [ ] Verificar que el botón "✓ Validar" está deshabilitado
2. [ ] Colocar todos los barcos (hasta que todos los contadores sean [0])

### Verificar:
- [ ] Botón "✓ Validar" se habilita
- [ ] Mensaje: "✅ Todos los barcos colocados — ¡Pulsa 'Validar'!"
- [ ] Click en "Validar"
- [ ] Mensaje: "✓ Listo — Esperando a otros jugadores..."
- [ ] Los controles desaparecen

---

## 🧪 TEST 12: INICIO DE BATALLA

### Pasos:
1. [ ] Ambos jugadores validan su configuración

### Verificar:
- [ ] Aparece el panel "🎯 Tablero de Ataque"
- [ ] El tablero enemigo está vacío (sin barcos visibles)
- [ ] Aparece botón "💣 Atacar" (deshabilitado)
- [ ] Mensaje indica de quién es el turno

---

## 🧪 TEST 13: SELECCIONAR OBJETIVO

### Pasos (jugador en turno):
1. [ ] Click en una celda del tablero enemigo

### Verificar:
- [ ] La celda se resalta en **dorado**
- [ ] Botón "💣 Atacar" se habilita
- [ ] Mensaje: "🎯 Objetivo seleccionado: [x, y] — Pulsa 'Atacar'"

---

## 🧪 TEST 14: ATAQUE - AGUA (FALLO)

### Pasos:
1. [ ] Seleccionar una celda vacía (sin barco enemigo)
2. [ ] Click en "💣 Atacar"

### Verificar:
- [ ] Animación central: **💨** (grande)
- [ ] Mensaje: "💨 AGUA. Has fallado en [x, y]"
- [ ] La celda se marca con **○** (círculo azul)
- [ ] El turno pasa al otro jugador
- [ ] Botón "Atacar" se deshabilita

---

## 🧪 TEST 15: ATAQUE - TOCADO (IMPACTO)

### Pasos:
1. [ ] Seleccionar una celda con barco enemigo
2. [ ] Click en "💣 Atacar"

### Verificar:
- [ ] Animación central: **💥** (grande)
- [ ] Mensaje: "🎯 ¡TOCADO! Has impactado en [x, y]"
- [ ] La celda se marca con **💥** (rojo)
- [ ] El turno pasa al otro jugador

---

## 🧪 TEST 16: ATAQUE - HUNDIDO

### Pasos:
1. [ ] Atacar todas las celdas de un barco enemigo

### Verificar:
- [ ] En el último impacto:
  - Animación central: **🚢💥** (grande)
  - Mensaje: "💥 ¡HUNDIDO! Has hundido un barco enemigo"
- [ ] Las celdas del barco se marcan en **rojo oscuro**
- [ ] El turno pasa al otro jugador

---

## 🧪 TEST 17: RECIBIR ATAQUE - TU TABLERO

### Pasos:
1. [ ] Esperar a que el enemigo te ataque

### Verificar:
- [ ] Si es impacto:
  - Animación: **💥**
  - Mensaje: "💥 ¡Te han impactado en [x, y]!"
  - **Punto rojo** aparece en tu tablero
- [ ] Si es fallo:
  - Animación: **💨**
  - Mensaje: "🌊 Han fallado el ataque en [x, y]"
  - **Círculo azul** aparece en tu tablero
- [ ] Si hunden tu barco:
  - Animación: **🚢💥**
  - Mensaje: "🚢 ¡Te han hundido un barco en [x, y]!"
  - El barco se marca en **rojo oscuro**

---

## 🧪 TEST 18: VALIDACIÓN DE ATAQUE REPETIDO

### Pasos:
1. [ ] Intentar atacar una celda ya atacada

### Verificar:
- [ ] Mensaje: "❌ Ya has atacado esta posición"
- [ ] El ataque NO se ejecuta
- [ ] El turno NO cambia

---

## 🧪 TEST 19: VALIDACIÓN DE TURNO

### Pasos:
1. [ ] Cuando NO es tu turno, intentar atacar

### Verificar:
- [ ] Mensaje: "❌ No es tu turno"
- [ ] El ataque NO se ejecuta

---

## 🧪 TEST 20: VICTORIA

### Pasos:
1. [ ] Hundir todos los barcos del enemigo

### Verificar:
- [ ] Mensaje: "🏆 ¡VICTORIA! Has ganado la partida"
- [ ] El juego termina
- [ ] No se pueden hacer más ataques

---

## 🧪 TEST 21: DERROTA

### Pasos:
1. [ ] Que el enemigo hunda todos tus barcos

### Verificar:
- [ ] Mensaje: "🏁 Partida terminada — Ganador: @enemigo"
- [ ] El juego termina

---

## 🧪 TEST 22: CONFIGURACIÓN EXTREMA

### Pasos:
1. [ ] Configurar partida con:
   - Todos los barcos en 0 excepto uno
   - Ej: Solo 5 destructores
2. [ ] Iniciar partida

### Verificar:
- [ ] Solo aparecen los botones de barcos configurados
- [ ] Los contadores son correctos
- [ ] Se puede jugar normalmente

---

## 🧪 TEST 23: CONFIGURACIÓN MÍNIMA

### Pasos:
1. [ ] Intentar iniciar partida con todos los barcos en 0

### Verificar:
- [ ] Mensaje de error: "Debes configurar al menos un barco"
- [ ] La partida NO se inicia

---

## 🧪 TEST 24: MÚLTIPLES JUGADORES (3-4)

### Pasos:
1. [ ] Configurar partida con 3 o 4 jugadores
2. [ ] Iniciar y jugar

### Verificar:
- [ ] Todos los jugadores pueden colocar barcos
- [ ] Los turnos rotan correctamente
- [ ] Los ataques van al siguiente jugador
- [ ] El ganador es el último con barcos

---

## 📊 RESUMEN DE RESULTADOS

### Funcionalidades Básicas:
- [ ] Configuración personalizada de flota
- [ ] Solo tablero propio en colocación
- [ ] Rotación horizontal/vertical
- [ ] Colocación de barcos

### Funcionalidades de Gestión:
- [ ] Seleccionar barco
- [ ] Mover barco
- [ ] Borrar barco
- [ ] Limpiar todo
- [ ] Validar configuración

### Funcionalidades de Batalla:
- [ ] Seleccionar objetivo
- [ ] Atacar
- [ ] Feedback visual (animaciones)
- [ ] Mensajes descriptivos
- [ ] Puntos rojos en tablero propio
- [ ] Cambio de turnos
- [ ] Victoria/Derrota

### Validaciones:
- [ ] Colisiones
- [ ] Límites del tablero
- [ ] Ataques repetidos
- [ ] Turnos
- [ ] Configuración mínima

---

## 🐛 REPORTE DE BUGS

Si encuentras algún problema, anótalo aquí:

### Bug #1:
- **Descripción**: 
- **Pasos para reproducir**: 
- **Resultado esperado**: 
- **Resultado actual**: 

### Bug #2:
- **Descripción**: 
- **Pasos para reproducir**: 
- **Resultado esperado**: 
- **Resultado actual**: 

---

## ✅ CONCLUSIÓN

**Fecha de prueba**: _______________

**Probado por**: _______________

**Estado general**: 
- [ ] ✅ Todas las pruebas pasadas
- [ ] ⚠️ Algunas pruebas fallidas (ver bugs)
- [ ] ❌ Muchas pruebas fallidas

**Comentarios adicionales**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**¡Gracias por probar! 🚢**
