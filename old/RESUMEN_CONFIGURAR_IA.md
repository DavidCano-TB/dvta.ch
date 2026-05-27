# 🚀 RESUMEN RÁPIDO: CONFIGURAR IA (GEMINI) EN 5 MINUTOS

## ✅ OPCIÓN 1: SCRIPT AUTOMÁTICO (MÁS FÁCIL)

### Paso 1: Obtener API Key
1. Ve a: **https://aistudio.google.com/apikey**
2. Inicia sesión con tu cuenta de Google
3. Click en **"Create API Key"**
4. Selecciona un proyecto o crea uno nuevo
5. Copia la clave (empieza con `AIza...`)

### Paso 2: ¡No necesitas pagar!
1. Gemini tiene un **tier gratuito generoso**
2. **15 peticiones/minuto** gratis
3. **1,500 peticiones/día** gratis
4. Perfecto para uso personal y pruebas

### Paso 3: Configurar
1. Ejecuta: **`CONFIGURAR_GEMINI_API.bat`**
2. Pega tu API key cuando te lo pida
3. ¡Listo! ✅

### Paso 4: Verificar
1. Ejecuta: **`python test_gemini_simple.py`**
2. Debería decir: "✅ TODOS LOS TESTS PASARON!"

---

## ✅ OPCIÓN 2: MANUAL (SI EL SCRIPT FALLA)

### Paso 1: Crear archivo con la API key
```bash
# En Windows (PowerShell):
echo "AIzaSyC_TU_CLAVE_AQUI" > config/.gemini_key

# O simplemente:
# 1. Crea el archivo: config/.gemini_key
# 2. Pega tu API key dentro
# 3. Guarda el archivo
```

### Paso 2: Verificar
```bash
# Ver que el archivo existe:
cat config/.gemini_key

# Debería mostrar tu API key
```

### Paso 3: Probar
```bash
python test_gemini_simple.py
```

---

## 📊 PRECIOS DE GEMINI (Mayo 2026)

| Modelo | Peticiones/Min | Tokens/Min | Peticiones/Día | Precio |
|--------|----------------|------------|----------------|--------|
| **gemini-1.5-flash** ⭐ | 15 | 1,000,000 | 1,500 | **GRATIS** |
| gemini-1.5-pro | 2 | 32,000 | 50 | **GRATIS** |

### Estimación de uso:
- **1 partida de "¿Quién Soy?"** (10 preguntas): GRATIS
- **100 partidas/día**: GRATIS (dentro del límite)
- **1500 partidas/día**: GRATIS (límite máximo)
- **Uso personal**: Probablemente nunca necesites pagar

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "API key not found"
**Solución:**
```bash
# Verifica que el archivo existe:
ls config/.gemini_key

# Si no existe, créalo:
echo "tu-api-key-aqui" > config/.gemini_key
```

### ❌ Error: "Invalid API key"
**Solución:**
1. Ve a: https://aistudio.google.com/apikey
2. Crea una **nueva** API key
3. Cópiala de nuevo (asegúrate de copiar TODA la clave)
4. Ejecuta de nuevo: `CONFIGURAR_GEMINI_API.bat`

### ❌ Error: "Rate limit exceeded"
**Solución:**
1. Espera 1 minuto (límite: 15 peticiones/minuto)
2. Para uso intensivo, considera el plan de pago
3. Monitorea tu uso en: https://aistudio.google.com/apikey

### ❌ La IA responde mal o "Ni sí ni no" siempre
**Solución:**
1. Verifica que la API key es correcta:
   ```bash
   cat config/.gemini_key
   ```
2. Verifica tu cuota:
   https://aistudio.google.com/apikey
3. Mira los logs del servidor para ver el error exacto

---

## 🎯 VERIFICACIÓN FINAL

### Test 1: Archivo existe
```bash
cat config/.gemini_key
# Debería mostrar: AIza...
```

### Test 2: API funciona
```bash
python test_gemini_simple.py
# Debería mostrar: ✅ TODOS LOS TESTS PASARON!
```

### Test 3: Juego funciona
1. Ejecuta: `ARRANCAR.bat`
2. Ve a: http://localhost:8000/quiensoy.html
3. Inicia sesión como admin
4. Crea un juego con personaje: "Mickey Mouse"
5. Pregunta: "¿Es un ratón?"
6. Debería responder: **"Sí"** ✅

---

## 🔄 ALTERNATIVAS (SI GEMINI NO FUNCIONA)

### Opción A: Fallback Local (AUTOMÁTICO)
Si Gemini falla, el sistema usa automáticamente una base de datos local.
El juego sigue funcionando, pero con respuestas menos inteligentes.

### Opción B: Groq (GRATIS y MÁS RÁPIDO)
1. Ve a: https://console.groq.com/
2. Crea cuenta
3. Obtén API key (GRATIS)
4. Guárdala en: `config/.groq_key`
5. Modifica `ai_helper.py` para usar Groq

### Opción C: OpenAI (ChatGPT)
1. Ve a: https://platform.openai.com/
2. Crea cuenta
3. Obtén API key
4. Guárdala en: `config/.openai_key`
5. Modifica `ai_helper.py` para usar OpenAI

---

## 📚 DOCUMENTACIÓN COMPLETA

- **Guía detallada**: `GUIA_CONFIGURAR_GEMINI_API.md`
- **Código de IA**: `ai_helper.py`
- **Test**: `test_gemini_simple.py`
- **Ejemplos de uso**: `EJEMPLOS_USO_IA.py`
- **Docs oficiales**: https://ai.google.dev/docs

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta de Google creada
- [ ] API Key obtenida de Google AI Studio
- [ ] API Key guardada en `config/.gemini_key`
- [ ] Test ejecutado: `python test_gemini_simple.py` ✅
- [ ] Servidor reiniciado: `ARRANCAR.bat`
- [ ] Juego probado: http://localhost:8000/quiensoy.html ✅

**¡Listo! Ahora tienes Gemini funcionando correctamente.** 🎉

---

## 💡 PRÓXIMOS PASOS

Ahora que tienes la IA funcionando, puedes:

1. **Usar el juego "¿Quién soy?"** con respuestas inteligentes
2. **Generar preguntas de examen** automáticamente (para el negocio de oposiciones)
3. **Crear explicaciones** personalizadas para estudiantes
4. **Expandir a otros juegos** con IA

Ver ejemplos completos en: **`EJEMPLOS_USO_IA.py`**

¿Necesitas ayuda con algo más? 🚀
