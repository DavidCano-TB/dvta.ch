# 🎯 INSTRUCCIONES: Activar Gemini AI para "Quién Soy"

## ⚠️ PROBLEMA DETECTADO

La API key de Gemini ha **excedido la cuota gratuita** para los modelos más recientes (gemini-2.x).

**Solución**: He configurado el sistema para usar `gemini-flash-latest` que tiene cuota disponible.

---

## ✅ PASOS PARA ACTIVAR LA IA

### Opción 1: Usar API Key Actual (Recomendado)

El sistema ya está configurado correctamente. Solo necesitas:

```bash
# 1. Ejecutar tests para verificar
python test_gemini_ai.py
```

Si los tests pasan, **la IA ya funciona** y puedes usar el juego normalmente.

### Opción 2: Crear Nueva API Key

Si los tests fallan por cuota excedida:

```bash
# 1. Ejecutar el configurador
CONFIGURAR_GEMINI_API.bat

# 2. Cuando te pida la API key, obtén una nueva en:
#    https://makersuite.google.com/app/apikey

# 3. Pega la nueva API key y presiona Enter

# 4. Ejecutar tests
python test_gemini_ai.py
```

---

## 🧪 TESTS DISPONIBLES

### Test Rápido (Conexión Básica)
```bash
python test_gemini_raw2.py
```
**Resultado esperado**: `✅ Texto extraído: 'OK'`

### Test Completo (Verificación + Respuestas)
```bash
python test_gemini_ai.py
```
**Resultado esperado**:
```
✅ PASS - Conexión con Gemini
✅ PASS - Verificación de personajes
✅ PASS - Respuestas a preguntas
🎉 TODOS LOS TESTS PASARON
```

---

## 🎮 PROBAR EN EL JUEGO

### 1. Reiniciar el Servidor
```bash
KILL_ALL_AND_RESTART.bat
```

### 2. Abrir el Juego
```
http://localhost:8000/opo
```

### 3. Login como Admin
- Usuario: `dvd` o `nebulosa`
- Contraseña: (tu contraseña)

### 4. Configurar Nueva Partida

**Test 1: Corrección Ortográfica**
```
1. Click "Configurar Nueva Partida"
2. Ingresar: "dedpol"
3. Click "Verificar"
4. ✅ Debe corregir a "Deadpool"
5. ✅ Debe mostrar: "Superhéroe de Marvel, conocido por..."
```

**Test 2: Personaje Real**
```
1. Ingresar: "Albert Einsten" (con error)
2. Click "Verificar"
3. ✅ Debe corregir a "Albert Einstein"
4. ✅ Debe mostrar: "Científico, conocido por..."
```

**Test 3: Personaje Inexistente**
```
1. Ingresar: "Asdfghjkl"
2. Click "Verificar"
3. ❌ Debe rechazar
4. ✅ Debe mostrar 5 sugerencias famosas
```

### 5. Jugar una Partida

```
1. Configurar personaje: "Deadpool"
2. Click "Iniciar Partida"
3. Hacer pregunta: "¿Es un superhéroe?"
4. ✅ Debe responder: "Sí"
5. Hacer pregunta: "¿Usa traje rojo?"
6. ✅ Debe responder: "Sí"
```

---

## 📊 CAMBIOS REALIZADOS

### ✅ Archivos Modificados

1. **ai_helper.py**
   - Modelo: `gemini-flash-latest` (con cuota disponible)
   - Tokens mínimos: 500 (para "thoughts" internos)
   - Safety filters: Desactivados
   - Manejo de errores mejorado

2. **main.py** y **src/main.py**
   - Eliminado fallback a base de datos local
   - TODO gestionado por IA
   - Error 503 si IA no disponible

3. **Tests Creados**
   - `test_gemini_ai.py` - Tests completos
   - `test_gemini_raw.py` - Test básico
   - `test_gemini_raw2.py` - Test con más tokens
   - `list_gemini_models.py` - Listar modelos disponibles

---

## 🔍 DIAGNÓSTICO

Si algo no funciona, ejecuta estos comandos en orden:

### 1. Verificar API Key
```bash
type config\.gemini_key
```
Debe mostrar una API key que empiece con `AIza...`

### 2. Listar Modelos Disponibles
```bash
python list_gemini_models.py
```
Debe mostrar lista de modelos con `✅ soporta generateContent`

### 3. Test de Conexión
```bash
python test_gemini_raw2.py
```
Debe mostrar `✅ Texto extraído: 'OK'`

### 4. Tests Completos
```bash
python test_gemini_ai.py
```
Debe pasar los 3 tests

---

## ⚠️ ERRORES COMUNES

### Error: "429 Too Many Requests - Quota exceeded"
**Causa**: API key sin cuota disponible

**Solución**:
1. Crear nueva API key: https://makersuite.google.com/app/apikey
2. Ejecutar: `CONFIGURAR_GEMINI_API.bat`
3. Pegar nueva API key

### Error: "503 Service Unavailable - High demand"
**Causa**: Servicio temporalmente sobrecargado

**Solución**:
1. Esperar 1-2 minutos
2. Reintentar (el sistema reintenta automáticamente 3 veces)

### Error: "Empty response from Gemini"
**Causa**: Tokens insuficientes o filtros de seguridad

**Solución**: Ya corregido en el código actual (mínimo 500 tokens, filtros desactivados)

---

## 📈 FUNCIONALIDADES

### ✅ Corrección Ortográfica Universal
```
"dedpol" → "Deadpool"
"Albert Einsten" → "Albert Einstein"
"Mickey Mause" → "Mickey Mouse"
"Hary Poter" → "Harry Potter"
```

### ✅ Personajes Aceptados
- **Reales**: Einstein, Messi, Obama, etc.
- **Ficticios**: Deadpool, Harry Potter, Mickey Mouse, etc.
- **Mitológicos**: Zeus, Thor, Medusa, etc.

### ✅ Sugerencias Inteligentes
- Basadas en categoría del personaje
- Personajes famosos mundialmente
- Generadas por la IA (no hardcodeadas)

### ✅ Respuestas Durante el Juego
- Basadas en características principales
- Ignora detalles irrelevantes
- Consistentes y precisas

---

## 🚀 SIGUIENTE PASO

**Ejecuta este comando para verificar que todo funciona:**

```bash
python test_gemini_ai.py
```

**Si los tests pasan**: ✅ La IA está lista, puedes jugar

**Si los tests fallan**: ⚠️ Sigue las instrucciones de diagnóstico arriba

---

## 📚 Documentación Completa

Ver: `docs/FIX_GEMINI_AI_DEFINITIVO.md`

---

## ✅ RESUMEN

1. ✅ Sistema configurado para usar `gemini-flash-latest`
2. ✅ Tokens suficientes (mínimo 500)
3. ✅ Fallback a base de datos eliminado
4. ✅ Tests creados y documentados
5. ⏳ **PENDIENTE**: Ejecutar `python test_gemini_ai.py` para verificar

**¡El sistema está listo para funcionar 100% con IA!**
