# 🤖 Guía Completa: Configurar Google Gemini API

Esta guía te ayudará a configurar la API de Google Gemini para usar las funcionalidades de IA en DVDBank.

---

## 📋 Índice

1. [¿Qué es Gemini?](#qué-es-gemini)
2. [Obtener tu API Key](#obtener-tu-api-key)
3. [Configuración Automática](#configuración-automática)
4. [Configuración Manual](#configuración-manual)
5. [Verificar la Configuración](#verificar-la-configuración)
6. [Precios y Límites](#precios-y-límites)
7. [Solución de Problemas](#solución-de-problemas)

---

## 🤖 ¿Qué es Gemini?

**Google Gemini** es el modelo de IA de última generación de Google. En DVDBank lo usamos para:

- **Juego "¿Quién Soy?"**: La IA responde preguntas sobre personajes
- **Cifras y Letras**: Validar palabras en español
- **Generación de Preguntas**: Crear exámenes automáticamente
- **Tutorías**: Explicar conceptos y resolver dudas

### ¿Por qué Gemini?

- ✅ **Tier gratuito generoso**: 15 peticiones/minuto gratis
- ✅ **Rápido**: Modelo `gemini-1.5-flash` optimizado para velocidad
- ✅ **Multilingüe**: Excelente soporte para español
- ✅ **Fácil de usar**: API simple y bien documentada

---

## 🔑 Obtener tu API Key

### Paso 1: Acceder a Google AI Studio

1. Ve a: **https://aistudio.google.com/apikey**
2. Inicia sesión con tu cuenta de Google
3. Si es tu primera vez, acepta los términos de servicio

### Paso 2: Crear una API Key

1. Haz clic en **"Create API Key"**
2. Selecciona un proyecto existente o crea uno nuevo:
   - **Opción A**: "Create API key in new project" (recomendado para empezar)
   - **Opción B**: Selecciona un proyecto de Google Cloud existente

3. La API key se generará automáticamente
4. **¡IMPORTANTE!** Copia la clave inmediatamente (empieza con `AIza...`)

### Paso 3: Guardar tu API Key

⚠️ **NUNCA compartas tu API key públicamente**

- No la subas a GitHub
- No la pegues en foros públicos
- No la compartas por email sin cifrar

---

## ⚡ Configuración Automática

### Método Recomendado: Script BAT

1. Ejecuta el script: **`CONFIGURAR_GEMINI_API.bat`**
2. Pega tu API key cuando te lo pida
3. El script hará todo automáticamente:
   - Guardará la key en `config/.gemini_key`
   - Configurará la variable de entorno
   - Verificará que funcione

```batch
# Ejemplo de ejecución
C:\dvdcoin> CONFIGURAR_GEMINI_API.bat

============================================================
  CONFIGURAR GOOGLE GEMINI API KEY
============================================================

Pega tu API Key aqui: AIzaSyC...

[OK] Guardada en: config\.gemini_key
[OK] Variable de entorno configurada
✅ Gemini configurado correctamente
```

---

## 🔧 Configuración Manual

Si prefieres configurar manualmente:

### Opción 1: Archivo de Configuración

1. Crea la carpeta `config` si no existe:
   ```bash
   mkdir config
   ```

2. Crea el archivo `config/.gemini_key`:
   ```bash
   echo AIzaSyC_TU_API_KEY_AQUI > config\.gemini_key
   ```

### Opción 2: Variable de Entorno

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSyC_TU_API_KEY_AQUI', 'User')
```

**Windows (CMD):**
```batch
setx GEMINI_API_KEY "AIzaSyC_TU_API_KEY_AQUI"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="AIzaSyC_TU_API_KEY_AQUI"
# Añadir a ~/.bashrc o ~/.zshrc para hacerlo permanente
echo 'export GEMINI_API_KEY="AIzaSyC_TU_API_KEY_AQUI"' >> ~/.bashrc
```

---

## ✅ Verificar la Configuración

### Test Rápido con Python

```python
from ai_helper import get_gemini

# Verificar que la API key se cargó
ai = get_gemini()
if ai.api_key:
    print("✅ API key configurada correctamente")
else:
    print("❌ No se encontró la API key")

# Hacer una pregunta de prueba
respuesta = ai.ask("¿Cuál es la capital de Francia?", max_tokens=20)
if respuesta:
    print(f"✅ Gemini funciona: {respuesta}")
else:
    print("❌ Error al conectar con Gemini")
```

### Test en el Juego

1. Ejecuta el servidor: `ARRANCAR.bat`
2. Ve a: http://localhost:8000/quiensoy.html
3. Inicia un juego como DVD
4. Configura un personaje (ej: "Mickey Mouse")
5. Haz una pregunta (ej: "¿Es un ratón?")
6. Si la IA responde "Sí", "No" o "Ni sí ni no" → ✅ **¡Funciona!**

---

## 💰 Precios y Límites

### Tier Gratuito (Free Tier)

Google Gemini ofrece un tier gratuito muy generoso:

| Modelo | Peticiones/Minuto | Tokens/Minuto | Peticiones/Día |
|--------|-------------------|---------------|----------------|
| gemini-1.5-flash | 15 | 1,000,000 | 1,500 |
| gemini-1.5-pro | 2 | 32,000 | 50 |

**DVDBank usa `gemini-1.5-flash`** (el más rápido y con más cuota gratuita)

### ¿Necesito Pagar?

**NO** para uso normal:
- Juegos ocasionales con amigos
- Pruebas y desarrollo
- Uso personal

**SÍ** si planeas:
- Uso comercial intensivo
- Miles de peticiones por día
- Necesitas más velocidad

### Monitorear tu Uso

1. Ve a: https://aistudio.google.com/apikey
2. Haz clic en tu API key
3. Verás estadísticas de uso en tiempo real

---

## 🔧 Solución de Problemas

### ❌ Error: "API key not found"

**Causa**: La API key no se cargó correctamente

**Solución**:
1. Verifica que el archivo existe: `config/.gemini_key`
2. Verifica que contiene tu API key (sin espacios extra)
3. Reinicia el servidor después de configurar

### ❌ Error: "HTTP 400 - Invalid API key"

**Causa**: La API key es incorrecta o está mal formateada

**Solución**:
1. Verifica que copiaste la key completa (empieza con `AIza`)
2. Genera una nueva API key en: https://aistudio.google.com/apikey
3. Vuelve a ejecutar `CONFIGURAR_GEMINI_API.bat`

### ❌ Error: "HTTP 429 - Rate limit exceeded"

**Causa**: Superaste el límite de peticiones por minuto

**Solución**:
- **Tier gratuito**: Espera 1 minuto y vuelve a intentar
- **Uso intensivo**: Considera actualizar a un plan de pago

### ❌ Error: "HTTP 403 - Permission denied"

**Causa**: La API key no tiene permisos o el proyecto está deshabilitado

**Solución**:
1. Ve a: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Asegúrate de que la API está habilitada
3. Verifica que tu proyecto tiene facturación configurada (aunque uses el tier gratuito)

### ❌ La IA responde "Ni sí ni no" a todo

**Causa**: La API no está funcionando y se usa el fallback

**Solución**:
1. Verifica los logs del servidor: busca mensajes de error
2. Ejecuta el test de Python (ver sección "Verificar la Configuración")
3. Revisa tu cuota en Google AI Studio

### ❌ Error: "Network error" o "Timeout"

**Causa**: Problemas de conexión a internet o firewall

**Solución**:
1. Verifica tu conexión a internet
2. Comprueba que puedes acceder a: https://generativelanguage.googleapis.com
3. Revisa configuración de firewall/proxy

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **Google AI Studio**: https://aistudio.google.com/
- **Documentación de Gemini**: https://ai.google.dev/docs
- **Guía de Precios**: https://ai.google.dev/pricing
- **Referencia de API**: https://ai.google.dev/api/rest

### Ejemplos de Uso en DVDBank

Ver archivo: **`EJEMPLOS_USO_IA.py`**

Incluye ejemplos de:
- Juego "¿Quién Soy?"
- Generación de preguntas de examen
- Explicaciones pedagógicas
- Análisis de rendimiento
- Y mucho más...

### Soporte

- **Issues en GitHub**: [Tu repositorio]
- **Documentación DVDBank**: Ver carpeta `docs/`
- **Comunidad de Google AI**: https://discuss.ai.google.dev/

---

## 🎉 ¡Listo!

Ahora tienes Gemini configurado y funcionando en DVDBank.

**Próximos pasos**:
1. Prueba el juego "¿Quién Soy?" con IA
2. Explora los ejemplos en `EJEMPLOS_USO_IA.py`
3. Personaliza las funcionalidades de IA para tus necesidades

**¿Preguntas?** Revisa la sección de [Solución de Problemas](#solución-de-problemas)

---

*Última actualización: Mayo 2026*
*Versión: 1.0*
