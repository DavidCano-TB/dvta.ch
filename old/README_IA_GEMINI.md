# 🤖 CONFIGURACIÓN DE IA (GEMINI) - GUÍA COMPLETA

## 📋 ¿QUÉ HEMOS HECHO?

Hemos configurado **Google Gemini** como la IA principal de tu plataforma DVDBank, ofreciendo un tier gratuito generoso y excelente rendimiento.

### ✅ Archivos creados/modificados:

1. **`GUIA_CONFIGURAR_GEMINI_API.md`** - Guía detallada paso a paso
2. **`RESUMEN_CONFIGURAR_IA.md`** - Resumen rápido en 5 minutos
3. **`ai_helper.py`** - Módulo de IA usando Gemini API
4. **`test_gemini_simple.py`** - Script para verificar que funciona
5. **`EJEMPLOS_USO_IA.py`** - Ejemplos de uso para tus negocios
6. **`CONFIGURAR_GEMINI_API.bat`** - Script de configuración automática
7. **`main.py`** - Modificado para usar el nuevo sistema de IA

---

## 🚀 INICIO RÁPIDO (3 PASOS)

### 1️⃣ Obtener API Key de Gemini

```
1. Ve a: https://aistudio.google.com/apikey
2. Inicia sesión con tu cuenta de Google
3. Click en "Create API Key"
4. Selecciona un proyecto o crea uno nuevo
5. Copia la clave (empieza con AIza...)
```

**¡No necesitas pagar!** Gemini tiene un tier gratuito muy generoso.

### 2️⃣ Configurar

```bash
# Opción A: Script automático (Windows)
CONFIGURAR_GEMINI_API.bat

# Opción B: Manual
echo "AIzaSyC_TU_CLAVE_AQUI" > config/.gemini_key
```

### 3️⃣ Verificar

```bash
# Test de la API
python test_gemini_simple.py

# Debería mostrar: ✅ TODOS LOS TESTS PASARON!
```

---

## 📚 DOCUMENTACIÓN

### Para configurar:
- **Guía completa**: `GUIA_CONFIGURAR_GEMINI_API.md`
- **Resumen rápido**: `RESUMEN_CONFIGURAR_IA.md`

### Para desarrollar:
- **Módulo de IA**: `ai_helper.py`
- **Ejemplos de uso**: `EJEMPLOS_USO_IA.py`
- **Test**: `test_gemini_simple.py`

### Documentación oficial:
- **Docs de Gemini**: https://ai.google.dev/docs
- **API Keys**: https://aistudio.google.com/apikey
- **Pricing**: https://ai.google.dev/pricing

---

## 💰 COSTES

### Precios de Gemini (Mayo 2026):

| Modelo | Peticiones/Min | Tokens/Min | Peticiones/Día | Precio |
|--------|----------------|------------|----------------|--------|
| **gemini-1.5-flash** ⭐ | 15 | 1,000,000 | 1,500 | **GRATIS** |
| gemini-1.5-pro | 2 | 32,000 | 50 | **GRATIS** |

### Estimación práctica:

- **1 pregunta "¿Quién soy?"**: GRATIS
- **100 partidas/día**: GRATIS (dentro del límite)
- **1500 partidas/día**: GRATIS (límite máximo)

### Con el tier gratuito puedes hacer:
- ✅ **1,500 peticiones/día** (suficiente para uso personal)
- ✅ **15 peticiones/minuto** (muy rápido)
- ✅ **1,000,000 tokens/minuto** (más que suficiente)

**Conclusión**: Para uso personal y pruebas, probablemente nunca necesites pagar.

---

## 🎯 CASOS DE USO

### 1. Juego "¿Quién soy?" (YA IMPLEMENTADO)
```python
from ai_helper import ask_quien_soy

respuesta = ask_quien_soy("Mickey Mouse", "¿Es un ratón?")
# Devuelve: "Sí"
```

### 2. Generar preguntas de examen (PARA NEGOCIO)
```python
from ai_helper import get_gemini

gemini = get_gemini()
pregunta = gemini.generate_exam_question(
    subject="Matemáticas",
    topic="Derivadas",
    difficulty="medium"
)
# Devuelve: dict con pregunta, opciones, respuesta correcta, explicación
```

### 3. Explicar respuestas (PARA ESTUDIANTES)
```python
explicacion = gemini.explain_answer(
    question="¿Cuál es la derivada de x²?",
    user_answer="2",
    correct_answer="2x"
)
# Devuelve: explicación detallada de por qué es 2x y no 2
```

### 4. Uso general (CUALQUIER COSA)
```python
from ai_helper import ask_gemini

respuesta = ask_gemini(
    "Genera 5 preguntas de trivia sobre historia de Suiza",
    max_tokens=500
)
# Devuelve: 5 preguntas generadas
```

---

## 🔧 ARQUITECTURA

### Flujo de la IA:

```
Usuario hace pregunta
    ↓
main.py → QuienSoyManager._ask_ai()
    ↓
ai_helper.py → GeminiAI.ask_quien_soy()
    ↓
API de Gemini (https://generativelanguage.googleapis.com/)
    ↓
Respuesta: "Sí", "No", o "Ni sí ni no"
    ↓
Usuario recibe respuesta
```

### Fallback inteligente:

```python
# Si Gemini falla (sin API key, sin conexión, error de red):
# → Usa base de datos local (hardcodeada)
# → El juego sigue funcionando (con menos inteligencia)
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### ❌ "API key not found"
```bash
# Verifica que existe:
cat config/.gemini_key

# Si no existe, créalo:
echo "tu-api-key" > config/.gemini_key
```

### ❌ "Invalid API key"
```
1. Ve a: https://aistudio.google.com/apikey
2. Crea una NUEVA key
3. Cópiala completa (empieza con AIza)
4. Ejecuta: CONFIGURAR_GEMINI_API.bat
```

### ❌ "Rate limit exceeded"
```
1. Espera 1 minuto (límite: 15 peticiones/minuto)
2. Para uso intensivo, considera el plan de pago
3. Monitorea tu uso en: https://aistudio.google.com/apikey
```

### ❌ "HTTP 403 - Permission denied"
```
1. Ve a: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Asegúrate de que la API está habilitada
3. Verifica que tu proyecto tiene facturación configurada (aunque uses el tier gratuito)
```

### ❌ La IA responde siempre "Ni sí ni no"
```bash
# 1. Verifica la API key:
cat config/.gemini_key

# 2. Verifica tu cuota:
# https://aistudio.google.com/apikey

# 3. Ejecuta el test:
python test_gemini_simple.py

# 4. Mira los logs del servidor:
# Busca líneas con "Gemini" o "AI" para ver el error
```

---

## 🔄 ALTERNATIVAS

### Si Gemini no funciona:

#### Opción A: Fallback Local (AUTOMÁTICO)
El sistema usa automáticamente una base de datos local si Gemini falla.
El juego sigue funcionando, pero con respuestas menos inteligentes.

#### Opción B: Groq (GRATIS y MÁS RÁPIDO)
```
1. Ve a: https://console.groq.com/
2. Crea cuenta (gratis)
3. Obtén API key (gratis, sin tarjeta)
4. Guárdala en: config/.groq_key
5. Modifica ai_helper.py para usar Groq
```

**Ventajas**: Gratis, muy rápido  
**Desventajas**: Límites más bajos

#### Opción C: OpenAI (ChatGPT)
```
1. Ve a: https://platform.openai.com/
2. Crea cuenta
3. Obtén API key
4. Guárdala en: config/.openai_key
5. Modifica ai_helper.py para usar OpenAI
```

**Ventajas**: Muy conocido, buena calidad  
**Desventajas**: Requiere pago

---

## 📊 MONITOREO DE USO

### Ver cuánto has usado:
```
https://aistudio.google.com/apikey
```

### Configurar alertas:
```
1. Ve a: https://console.cloud.google.com/
2. Configura alertas de cuota
3. Recibe notificaciones cuando te acerques al límite
```

### Ver logs en tu aplicación:
```bash
# Los logs muestran cada llamada a la API:
# "Gemini response: ... (tokens: 50/20)"
```

---

## 🚀 PRÓXIMOS PASOS

Ahora que tienes la IA funcionando, puedes:

### 1. Probar el juego "¿Quién soy?"
```bash
ARRANCAR.bat
# Ve a: http://localhost:8000/quiensoy.html
```

### 2. Ver ejemplos de uso
```bash
python EJEMPLOS_USO_IA.py
```

### 3. Implementar tu negocio
- **Oposiciones**: Usa `generate_exam_question()` y `explain_answer()`
- **Trivias**: Usa `ask_gemini()` para generar preguntas
- **Tutorías**: Usa `ask_gemini()` con system prompts personalizados

### 4. Personalizar la IA
Edita `ai_helper.py` para:
- Cambiar el modelo (línea 24)
- Ajustar temperatura (creatividad)
- Añadir nuevos métodos específicos

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta de Google creada
- [ ] API Key obtenida de Google AI Studio
- [ ] API Key guardada en `config/.gemini_key`
- [ ] Test ejecutado: `python test_gemini_simple.py` ✅
- [ ] Servidor reiniciado: `ARRANCAR.bat`
- [ ] Juego probado: http://localhost:8000/quiensoy.html ✅
- [ ] Ejemplos revisados: `python EJEMPLOS_USO_IA.py`

---

## 📞 SOPORTE

### Documentación:
- **Esta guía**: `README_IA_GEMINI.md`
- **Guía detallada**: `GUIA_CONFIGURAR_GEMINI_API.md`
- **Resumen rápido**: `RESUMEN_CONFIGURAR_IA.md`

### Recursos oficiales:
- **Docs**: https://ai.google.dev/docs
- **API Keys**: https://aistudio.google.com/apikey
- **Comunidad**: https://discuss.ai.google.dev/

---

## 🎉 ¡LISTO!

Ahora tienes Google Gemini funcionando correctamente en tu plataforma.

**¿Qué puedes hacer ahora?**
1. ✅ Jugar "¿Quién soy?" con IA inteligente
2. ✅ Generar preguntas de examen automáticamente
3. ✅ Crear explicaciones personalizadas
4. ✅ Desarrollar tus negocios con IA
5. ✅ Todo GRATIS con el tier gratuito

**¿Necesitas ayuda?** Revisa los archivos de documentación o la comunidad de Google AI.

---

**Migrado de**: Anthropic Claude → Google Gemini  
**Fecha**: Mayo 2026  
**Versión**: 2.0

