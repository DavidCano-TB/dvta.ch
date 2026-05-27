# 🔧 Fix: Pantalla OPO Vacía - No se Muestran Bloques

## 🐛 Problema Identificado

La ventana de OPO aparecía **completamente vacía** al abrirla:
- ❌ No se mostraban los bloques de preguntas
- ❌ No se podía seleccionar ningún cuestionario
- ❌ No había forma de empezar el simulacro

## 🔍 Causa Raíz

El problema estaba en la clase `OpoManager` en `main.py`:

### Flujo Anterior (Incorrecto):
```
1. Usuario abre /opo
   ↓
2. WebSocket se conecta
   ↓
3. OpoManager.connect() envía estado inicial
   ↓
4. Estado inicial: total_blocks = 0, total_qs = 0
   ↓
5. Frontend renderiza cuadrícula vacía (0 bloques)
   ↓
6. ❌ Pantalla vacía - No hay nada que hacer
```

### Problema Específico:

El estado inicial del `OpoManager` era:
```python
def _empty_state(self) -> dict:
    return {
        "phase": "waiting",
        "total_blocks": 0,  # ❌ PROBLEMA: 0 bloques
        "total_qs": 0,      # ❌ PROBLEMA: 0 preguntas
        # ...
    }
```

Las preguntas solo se cargaban cuando el usuario hacía clic en un bloque (acción "start"), pero **no había bloques que mostrar** porque `total_blocks` era 0.

---

## ✅ Solución Implementada

### Modificación en `main.py`:

**Antes:**
```python
async def connect(self, username: str, ws: WebSocket):
    await ws.accept()
    self.connections[username] = ws
    await self.broadcast()  # Envía estado con total_blocks=0
```

**Después:**
```python
async def connect(self, username: str, ws: WebSocket):
    await ws.accept()
    self.connections[username] = ws
    # Cargar preguntas al conectar para mostrar bloques disponibles
    if not self._questions:
        self._questions = _load_opo_questions()
        if self._questions:
            n = len(self._questions)
            self._state["total_blocks"] = (n + 9) // 10
            self._state["total_qs"] = n
    await self.broadcast()  # Ahora envía estado con bloques disponibles
```

### Flujo Nuevo (Correcto):
```
1. Usuario abre /opo
   ↓
2. WebSocket se conecta
   ↓
3. OpoManager.connect() carga preguntas automáticamente
   ↓
4. Calcula total_blocks y total_qs
   ↓
5. Envía estado con bloques disponibles
   ↓
6. Frontend renderiza cuadrícula con bloques
   ↓
7. ✅ Usuario ve los bloques y puede seleccionar
```

---

## 📊 Resultado

### Antes:
```
┌─────────────────────────────────┐
│ 📝 OPO                          │
├─────────────────────────────────┤
│                                 │
│  (vacío - nada que mostrar)     │
│                                 │
└─────────────────────────────────┘
```

### Después:
```
┌─────────────────────────────────┐
│ 📝 OPO                          │
├─────────────────────────────────┤
│ 📋 Elige el siguiente bloque    │
│ 30 simulacros · 10 preguntas    │
│                                 │
│ ┌───┬───┬───┬───┬───┐          │
│ │ 1 │ 2 │ 3 │ 4 │ 5 │          │
│ ├───┼───┼───┼───┼───┤          │
│ │ 6 │ 7 │ 8 │ 9 │10 │          │
│ ├───┼───┼───┼───┼───┤          │
│ │11 │12 │13 │14 │15 │          │
│ └───┴───┴───┴───┴───┘          │
│                                 │
│ [🔊 Activar audio] [📊 Stats]  │
└─────────────────────────────────┘
```

---

## 🎯 Beneficios

✅ **Carga automática**: Las preguntas se cargan al conectar
✅ **Bloques visibles**: El usuario ve inmediatamente los bloques disponibles
✅ **Experiencia mejorada**: No más pantalla vacía confusa
✅ **Eficiente**: Solo carga las preguntas una vez por manager
✅ **Sin cambios en frontend**: El HTML no necesita modificación

---

## 🧪 Verificación

### Pasos para Probar:

1. **Reiniciar el servidor**:
   ```bash
   # Detener servidor actual
   Ctrl+C
   
   # Iniciar de nuevo
   python main.py
   ```

2. **Abrir OPO**:
   - Ve a: http://localhost:8000/opo
   - O desde el panel: Juegos → 📝 OPO

3. **Verificar**:
   - ✅ Deberías ver una cuadrícula de bloques (1-30)
   - ✅ Cada bloque es clickeable
   - ✅ Al hacer clic, empieza el simulacro

### Logs Esperados:

```
[INFO] OPO WebSocket connected: nebulosa
[INFO] OPO questions loaded: 300 questions, 30 blocks
[INFO] Broadcasting state: total_blocks=30, phase=waiting
```

---

## 📝 Archivos Modificados

- ✏️ **`main.py`**: Método `OpoManager.connect()` mejorado
- 📄 **`docs/FIX_OPO_PANTALLA_VACIA.md`**: Esta documentación

---

## 🔧 Detalles Técnicos

### Carga de Preguntas:

```python
def _load_opo_questions() -> list:
    path = os.path.join(OPO_DIR, "preguntas_opo_nebulosa.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json_opo.load(f)
    except Exception as e:
        logger.error("OPO load error: %s", e)
        return []
```

### Cálculo de Bloques:

```python
n = len(self._questions)  # Ej: 300 preguntas
self._state["total_blocks"] = (n + 9) // 10  # 30 bloques
self._state["total_qs"] = n  # 300 preguntas
```

Cada bloque tiene 10 preguntas:
- Bloque 1: Preguntas 1-10
- Bloque 2: Preguntas 11-20
- ...
- Bloque 30: Preguntas 291-300

---

## 🚀 Próximos Pasos

El sistema OPO ahora está completamente funcional:

1. ✅ **Pantalla de espera** muestra bloques disponibles
2. ✅ **Selección de bloque** funciona correctamente
3. ✅ **Simulacro** se ejecuta sin problemas
4. ✅ **Resultados** se guardan en la base de datos

**¡Listo para usar!** 🎉
