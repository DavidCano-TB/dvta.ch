# 🎯 Pasapalabra - Implementación Pendiente

**Fecha:** 9 de Mayo de 2026  
**Estado:** ⚠️ En progreso

---

## ✅ LO QUE YA ESTÁ HECHO

1. ✅ Estructura del JSON de preguntas creada
2. ✅ Prompt completo para generar preguntas documentado
3. ✅ Ejemplos de preguntas para letras A y B (50 cada una)

---

## ⚠️ LO QUE FALTA POR HACER

### 1. **Completar el JSON de preguntas** (PRIORITARIO)

**Archivo:** `static/pasapalabra/preguntas.json`

**Necesitas:**
- 50 preguntas por cada letra del abecedario (A-Z + Ñ)
- Total: 27 letras × 50 preguntas = **1.350 preguntas**

**Ya tienes:**
- ✅ Letra A: 50 preguntas
- ✅ Letra B: 50 preguntas
- ⚠️ Letras C-Z + Ñ: PENDIENTES (1.250 preguntas)

**Formato de cada pregunta:**
```json
{
  "tipo": "empieza",  // o "contiene" para letras difíciles
  "definicion": "Empieza por X: [PREGUNTA DIVERTIDA Y EDUCATIVA]",
  "respuesta": "RESPUESTA EN MAYÚSCULAS"
}
```

**Características:**
- Nivel: 3º ESO (14-15 años)
- Tono: Divertido pero educativo
- Categorías: Geografía, Historia, Literatura, Ciencia, Cultura pop, Deportes
- Para letras difíciles (K, W, X, Y, Z): Usar tipo "contiene"

---

### 2. **Modificar el código del juego** (PRIORITARIO)

**Archivo a modificar:** `main.py` (buscar sección de Pasapalabra)

#### Funcionalidades a implementar:

##### A) **Sistema de preguntas no repetidas**
```python
# Cuando se selecciona una pregunta para una letra:
# 1. Filtrar preguntas ya usadas
# 2. Seleccionar aleatoriamente de las disponibles
# 3. Marcar como usada (guardar en DB o archivo)
# 4. NUNCA volver a mostrar esa pregunta
```

##### B) **Vista especial para DVD**

**Requisitos:**
1. **Ver pregunta precedente:**
   - Mostrar la pregunta anterior (del mismo jugador u otro)
   - Excepción: Primera pregunta de todos los miembros (no hay precedente)
   - Visible ANTES de iniciar el tiempo

2. **Ver respuesta correcta:**
   - DVD debe ver SIEMPRE la respuesta correcta de cada palabra
   - Para poder validar si la respuesta del jugador es correcta

3. **Contador de preguntas restantes:**
   - Mostrar cuántas preguntas quedan disponibles para cada letra
   - Ejemplo: "A: 48/50 | B: 50/50 | C: 49/50"
   - Solo visible para DVD

##### C) **Prohibir repeticiones**
```python
# Sistema de tracking:
# - Guardar en DB: letra + hash de la pregunta
# - Al cargar preguntas: excluir las ya usadas
# - Resetear solo manualmente por admin
```

---

### 3. **Estructura de datos sugerida**

#### Tabla en DB para tracking de preguntas usadas:
```sql
CREATE TABLE IF NOT EXISTS pasapalabra_preguntas_usadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letra TEXT NOT NULL,
    pregunta_hash TEXT NOT NULL,
    usado_en_partida INTEGER,
    usado_por_jugador TEXT,
    fecha_uso TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(letra, pregunta_hash)
);
```

#### Modificación del JSON (opcional):
```json
{
  "A": [
    {
      "id": "a001",  // ID único para tracking
      "tipo": "empieza",
      "definicion": "Empieza por A: ...",
      "respuesta": "ATENAS"
    }
  ]
}
```

---

### 4. **Interfaz para DVD**

**Archivo a modificar:** `static/pasapalabra/game.html` o crear `static/pasapalabra/admin_view.html`

#### Elementos a añadir:

```html
<!-- Panel de administración (solo visible para DVD) -->
<div id="dvd-admin-panel" style="display: none;">
  
  <!-- Pregunta precedente -->
  <div class="precedente-box">
    <h4>📋 Pregunta Precedente</h4>
    <p id="pregunta-precedente">
      [Letra anterior]: [Pregunta anterior]
    </p>
    <p><strong>Respuesta:</strong> <span id="respuesta-precedente">XXXXX</span></p>
  </div>

  <!-- Pregunta actual -->
  <div class="actual-box">
    <h4>🎯 Pregunta Actual</h4>
    <p id="pregunta-actual">[Letra]: [Pregunta]</p>
    <p><strong>Respuesta correcta:</strong> <span id="respuesta-actual">XXXXX</span></p>
  </div>

  <!-- Contador de preguntas -->
  <div class="contador-box">
    <h4>📊 Preguntas Restantes</h4>
    <div id="contador-preguntas">
      <!-- A: 48/50 | B: 50/50 | C: 49/50 ... -->
    </div>
  </div>

</div>
```

---

### 5. **API Endpoints a crear/modificar**

```python
# En main.py

@app.get("/api/pasapalabra/pregunta/{letra}")
async def get_pregunta_letra(letra: str, current_user: str = Depends(get_current_user)):
    """
    Obtiene una pregunta aleatoria para una letra que NO haya sido usada.
    """
    # 1. Cargar todas las preguntas de esa letra
    # 2. Filtrar las ya usadas
    # 3. Si no quedan, retornar error o reciclar
    # 4. Seleccionar aleatoria
    # 5. Marcar como usada
    # 6. Retornar pregunta
    pass

@app.get("/api/pasapalabra/stats/preguntas")
async def get_stats_preguntas(current_user: str = Depends(get_current_user)):
    """
    Retorna estadísticas de preguntas usadas/disponibles por letra.
    Solo para admins (DVD).
    """
    if current_user not in SUPERADMINS:
        raise HTTPException(403, "No autorizado")
    
    # Retornar: {"A": {"usadas": 2, "total": 50}, "B": {...}, ...}
    pass

@app.post("/api/pasapalabra/reset-preguntas")
async def reset_preguntas(current_user: str = Depends(get_current_user)):
    """
    Resetea el tracking de preguntas usadas.
    Solo para superadmins.
    """
    if current_user not in SUPERADMINS:
        raise HTTPException(403, "No autorizado")
    
    # Limpiar tabla de preguntas usadas
    pass
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Contenido (URGENTE)
- [ ] Completar preguntas letra C (50 preguntas)
- [ ] Completar preguntas letra D (50 preguntas)
- [ ] Completar preguntas letra E (50 preguntas)
- [ ] Completar preguntas letra F (50 preguntas)
- [ ] Completar preguntas letra G (50 preguntas)
- [ ] Completar preguntas letra H (50 preguntas)
- [ ] Completar preguntas letra I (50 preguntas)
- [ ] Completar preguntas letra J (50 preguntas)
- [ ] Completar preguntas letra K (50 preguntas - usar "contiene")
- [ ] Completar preguntas letra L (50 preguntas)
- [ ] Completar preguntas letra M (50 preguntas)
- [ ] Completar preguntas letra N (50 preguntas)
- [ ] Completar preguntas letra Ñ (50 preguntas - usar "contiene")
- [ ] Completar preguntas letra O (50 preguntas)
- [ ] Completar preguntas letra P (50 preguntas)
- [ ] Completar preguntas letra Q (50 preguntas)
- [ ] Completar preguntas letra R (50 preguntas)
- [ ] Completar preguntas letra S (50 preguntas)
- [ ] Completar preguntas letra T (50 preguntas)
- [ ] Completar preguntas letra U (50 preguntas)
- [ ] Completar preguntas letra V (50 preguntas)
- [ ] Completar preguntas letra W (50 preguntas - usar "contiene")
- [ ] Completar preguntas letra X (50 preguntas - usar "contiene")
- [ ] Completar preguntas letra Y (50 preguntas)
- [ ] Completar preguntas letra Z (50 preguntas)

### Fase 2: Backend
- [ ] Crear tabla `pasapalabra_preguntas_usadas` en DB
- [ ] Implementar función `get_pregunta_no_usada(letra)`
- [ ] Implementar función `marcar_pregunta_usada(letra, pregunta_id)`
- [ ] Implementar endpoint `/api/pasapalabra/pregunta/{letra}`
- [ ] Implementar endpoint `/api/pasapalabra/stats/preguntas`
- [ ] Implementar endpoint `/api/pasapalabra/reset-preguntas`
- [ ] Modificar lógica del juego para usar nuevas funciones

### Fase 3: Frontend
- [ ] Crear panel de administración para DVD
- [ ] Mostrar pregunta precedente
- [ ] Mostrar respuesta correcta actual
- [ ] Mostrar contador de preguntas restantes
- [ ] Ocultar panel para usuarios no-DVD
- [ ] Conectar con WebSocket para actualizaciones en tiempo real

### Fase 4: Testing
- [ ] Probar que no se repiten preguntas
- [ ] Probar vista de DVD
- [ ] Probar contador de preguntas
- [ ] Probar con múltiples jugadores
- [ ] Probar reset de preguntas

---

## 🎯 PRIORIDAD INMEDIATA

**LO MÁS URGENTE:**
1. Completar el JSON con las 1.250 preguntas restantes
2. Implementar sistema de no repetición en el backend
3. Crear vista especial para DVD

**TIEMPO ESTIMADO:**
- Generar preguntas: 4-6 horas (con IA o manualmente)
- Implementar backend: 2-3 horas
- Implementar frontend: 1-2 horas
- Testing: 1 hora

**TOTAL:** ~8-12 horas de trabajo

---

## 💡 SUGERENCIAS

### Para generar preguntas más rápido:
1. Usar ChatGPT/Claude con el prompt que te di
2. Generar 10 preguntas a la vez
3. Revisar y ajustar el tono
4. Copiar al JSON

### Para las letras difíciles (K, W, X, Y, Z):
- Usar más preguntas tipo "contiene"
- Ejemplos:
  - K: "Contiene la K: Deporte de artes marciales japonés" → "KARATE"
  - W: "Contiene la W: Red social de videos cortos" → "TIKTOK"  
  - X: "Contiene la X: Instrumento musical de percusión" → "XILÓFONO"
  - Y: "Contiene la Y: País sudamericano" → "URUGUAY"
  - Z: "Contiene la Z: Fruta cítrica amarilla" → "LIMÓN" (no, mejor "MANZANA")

---

## 📞 CONTACTO

Si necesitas ayuda para:
- Generar las preguntas restantes
- Implementar el código
- Resolver dudas técnicas

**¡Avísame y continuamos!** 🚀

---

**Última actualización:** 9 de Mayo de 2026  
**Estado:** ⚠️ Documentación completa - Pendiente implementación

