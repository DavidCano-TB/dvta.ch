# 🤖 CONFIGURACIÓN DE IA (CLAUDE) - GUÍA COMPLETA

## 📋 ¿QUÉ HEMOS HECHO?

Hemos configurado **Claude (Anthropic)** como la IA principal de tu plataforma DVDBank, reemplazando el sistema anterior que no funcionaba correctamente.

### ✅ Archivos creados/modificados:

1. **`GUIA_CONFIGURAR_CLAUDE_API.md`** - Guía detallada paso a paso
2. **`RESUMEN_CONFIGURAR_IA.md`** - Resumen rápido en 5 minutos
3. **`ai_helper.py`** - Módulo de IA mejorado y reutilizable
4. **`test_ai_simple.py`** - Script para verificar que funciona
5. **`EJEMPLOS_USO_IA.py`** - Ejemplos de uso para tus negocios
6. **`CONFIGURAR_ANTHROPIC_API.bat`** - Script mejorado de configuración
7. **`main.py`** - Modificado para usar el nuevo sistema de IA

---

## 🚀 INICIO RÁPIDO (3 PASOS)

### 1️⃣ Obtener API Key de Claude

```
1. Ve a: https://console.anthropic.com/
2. Crea cuenta (gratis)
3. Ve a "API Keys" → "Create Key"
4. Copia la clave (empieza con sk-ant-api03-...)
5. Añade créditos: https://console.anthropic.com/settings/billing
   Recomendado: $20 USD para empezar
```

### 2️⃣ Configurar

```bash
# Opción A: Script automático (Windows)
CONFIGURAR_ANTHROPIC_API.bat

# Opción B: Manual
echo "sk-ant-api03-TU_CLAVE_AQUI" > config/.groq_key
```

### 3️⃣ Verificar

```bash
# Test de la API
python test_ai_simple.py

# Debería mostrar: ✅ TODO FUNCIONA CORRECTAMENTE
```

---

## 📚 DOCUMENTACIÓN

### Para configurar:
- **Guía completa**: `GUIA_CONFIGURAR_CLAUDE_API.md`
- **Resumen rápido**: `RESUMEN_CONFIGURAR_IA.md`

### Para desarrollar:
- **Módulo de IA**: `ai_helper.py`
- **Ejemplos de uso**: `EJEMPLOS_USO_IA.py`
- **Test**: `test_ai_simple.py`

### Documentación oficial:
- **Docs de Claude**: https://docs.anthropic.com/
- **Console**: https://console.anthropic.com/
- **Pricing**: https://www.anthropic.com/pricing

---

## 💰 COSTES

### Precios de Claude (Mayo 2026):

| Modelo | Input | Output | Uso recomendado |
|--------|-------|--------|------------------|
| **Claude 3.5 Sonnet** ⭐ | $3/M tokens | $15/M tokens | Mejor calidad/precio |
| Claude 3 Haiku | $0.25/M tokens | $1.25/M tokens | Respuestas simples |
| Claude 3 Opus | $15/M tokens | $75/M tokens | Tareas complejas |

### Estimación práctica:

- **1 pregunta "¿Quién soy?"** ≈ 500 tokens ≈ **$0.002** (0.2 céntimos)
- **1 pregunta de examen generada** ≈ 1.000 tokens ≈ **$0.015** (1.5 céntimos)
- **1 explicación detallada** ≈ 800 tokens ≈ **$0.012** (1.2 céntimos)

### Con $20 USD puedes hacer:
- ✅ **10.000 preguntas** del juego "¿Quién soy?"
- ✅ **1.300 preguntas de examen** generadas
- ✅ **1.600 explicaciones** detalladas

**Conclusión**: Es muy barato para uso normal. $20 USD te duran meses.

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
from ai_helper import get_claude

claude = get_claude()
pregunta = claude.generate_exam_question(
    subject="Matemáticas",
    topic="Derivadas",
    difficulty="medium"
)
# Devuelve: dict con pregunta, opciones, respuesta correcta, explicación
```

### 3. Explicar respuestas (PARA ESTUDIANTES)
```python
explicacion = claude.explain_answer(
    question="¿Cuál es la derivada de x²?",
    user_answer="2",
    correct_answer="2x"
)
# Devuelve: explicación detallada de por qué es 2x y no 2
```

### 4. Uso general (CUALQUIER COSA)
```python
from ai_helper import ask_claude

respuesta = ask_claude(
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
ai_helper.py → ClaudeAI.ask_quien_soy()
    ↓
API de Claude (https://api.anthropic.com/)
    ↓
Respuesta: "Sí", "No", o "Ni sí ni no"
    ↓
Usuario recibe respuesta
```

### Fallback inteligente:

```python
# Si Claude falla (sin API key, sin créditos, error de red):
# → Usa base de datos local (hardcodeada)
# → El juego sigue funcionando (con menos inteligencia)
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### ❌ "API key not found"
```bash
# Verifica que existe:
cat config/.groq_key

# Si no existe, créalo:
echo "tu-api-key" > config/.groq_key
```

### ❌ "Invalid API key"
```
1. Ve a: https://console.anthropic.com/settings/keys
2. Crea una NUEVA key
3. Cópiala completa (empieza con sk-ant-api03-)
4. Ejecuta: CONFIGURAR_ANTHROPIC_API.bat
```

### ❌ "Insufficient credits"
```
1. Ve a: https://console.anthropic.com/settings/billing
2. Añade $20+ USD
3. Espera 1-2 minutos
4. Prueba de nuevo
```

### ❌ "Rate limit exceeded"
```
- Espera 1 minuto
- O añade más créditos para subir de tier
```

### ❌ La IA responde siempre "Ni sí ni no"
```bash
# 1. Verifica la API key:
cat config/.groq_key

# 2. Verifica que tienes créditos:
# https://console.anthropic.com/settings/usage

# 3. Ejecuta el test:
python test_ai_simple.py

# 4. Mira los logs del servidor:
# Busca líneas con "Claude" o "AI" para ver el error
```

---

## 🔄 ALTERNATIVAS

### Si Claude no funciona o es muy caro:

#### Opción A: Groq (GRATIS y 10x más rápido)
```
1. Ve a: https://console.groq.com/
2. Crea cuenta (gratis)
3. Obtén API key (gratis, sin tarjeta)
4. Guárdala en: config/.groq_key
5. Modifica ai_helper.py línea 24:
   self.model = "llama-3.1-70b-versatile"
   self.api_url = "https://api.groq.com/openai/v1/chat/completions"
```

**Ventajas**: Gratis, muy rápido  
**Desventajas**: Límites más bajos, calidad ligeramente inferior

#### Opción B: OpenAI (ChatGPT)
```
1. Ve a: https://platform.openai.com/
2. Crea cuenta
3. Obtén API key
4. Guárdala en: config/.openai_key
5. Modifica ai_helper.py para usar OpenAI
```

**Ventajas**: Muy conocido, buena calidad  
**Desventajas**: Más caro que Claude

---

## 📊 MONITOREO DE USO

### Ver cuánto has gastado:
```
https://console.anthropic.com/settings/usage
```

### Configurar alertas:
```
1. Ve a: https://console.anthropic.com/settings/billing
2. Click en "Set up billing alerts"
3. Configura: "Alertarme cuando gaste $X"
```

### Ver logs en tu aplicación:
```bash
# Los logs muestran cada llamada a la API:
# "Claude response: ... (tokens: 50/20)"
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
- **Trivias**: Usa `ask_claude()` para generar preguntas
- **Tutorías**: Usa `ask_claude()` con system prompts personalizados

### 4. Personalizar la IA
Edita `ai_helper.py` para:
- Cambiar el modelo (línea 24)
- Ajustar temperatura (creatividad)
- Añadir nuevos métodos específicos

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta creada en Anthropic Console
- [ ] API Key obtenida
- [ ] Créditos añadidos ($20+ recomendado)
- [ ] API Key guardada en `config/.groq_key`
- [ ] Test ejecutado: `python test_ai_simple.py` ✅
- [ ] Servidor reiniciado: `ARRANCAR.bat`
- [ ] Juego probado: http://localhost:8000/quiensoy.html ✅
- [ ] Ejemplos revisados: `python EJEMPLOS_USO_IA.py`

---

## 📞 SOPORTE

### Documentación:
- **Esta guía**: `README_IA_CLAUDE.md`
- **Guía detallada**: `GUIA_CONFIGURAR_CLAUDE_API.md`
- **Resumen rápido**: `RESUMEN_CONFIGURAR_IA.md`

### Recursos oficiales:
- **Docs**: https://docs.anthropic.com/
- **Console**: https://console.anthropic.com/
- **Discord**: https://discord.gg/anthropic
- **Email**: support@anthropic.com

### Comunidad:
- **Reddit**: r/ClaudeAI
- **Twitter**: @AnthropicAI

---

## 🎉 ¡LISTO!

Ahora tienes Claude (Anthropic) funcionando correctamente en tu plataforma.

**¿Qué puedes hacer ahora?**
1. ✅ Jugar "¿Quién soy?" con IA inteligente
2. ✅ Generar preguntas de examen automáticamente
3. ✅ Crear explicaciones personalizadas
4. ✅ Desarrollar tus negocios con IA

**¿Necesitas ayuda?** Revisa los archivos de documentación o contacta con soporte.

---

**Creado por**: Kiro AI Assistant  
**Fecha**: Mayo 2026  
**Versión**: 1.0
