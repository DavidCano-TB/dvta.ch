# 🤖 GUÍA COMPLETA: CONFIGURAR CLAUDE (ANTHROPIC) API

## 📌 PASO 1: OBTENER TU API KEY DE ANTHROPIC

### 1.1 Crear cuenta en Anthropic Console

1. **Ir a**: https://console.anthropic.com/
2. **Hacer clic en**: "Sign Up" (Registrarse)
3. **Completar**:
   - Email
   - Contraseña
   - Verificar email

### 1.2 Obtener la API Key

1. **Iniciar sesión** en: https://console.anthropic.com/
2. **Ir a**: "API Keys" en el menú lateral izquierdo
3. **Hacer clic en**: "Create Key" (Crear clave)
4. **Darle un nombre**: Por ejemplo "DVDBank Production"
5. **Copiar la clave**: Empieza con `sk-ant-api03-...`
   
   ⚠️ **IMPORTANTE**: Guarda esta clave en un lugar seguro. Solo se muestra UNA VEZ.

### 1.3 Añadir créditos (Billing)

1. **Ir a**: "Billing" en el menú
2. **Hacer clic en**: "Add Credits"
3. **Añadir**: Mínimo $5 USD (recomendado: $20-50 USD)
4. **Completar** datos de tarjeta

**Precios de Claude (Mayo 2026):**
- Claude 3.5 Sonnet: $3 por millón de tokens input / $15 por millón output
- Claude 3 Haiku: $0.25 por millón input / $1.25 por millón output

**Estimación de uso:**
- 1 pregunta de "¿Quién soy?" ≈ 500 tokens ≈ $0.002 (0.2 céntimos)
- 1.000 preguntas ≈ $2 USD
- Con $20 USD puedes hacer ~10.000 preguntas

---

## 📌 PASO 2: CONFIGURAR LA API KEY EN TU PROYECTO

### Opción A: Usando el script automático (RECOMENDADO)

1. **Ejecutar**: `CONFIGURAR_ANTHROPIC_API.bat`
2. **Pegar tu API key** cuando te lo pida
3. **Listo** ✅

### Opción B: Manual

#### En Windows:

1. **Abrir**: `config/.groq_key` (o crear el archivo)
2. **Pegar tu API key**: `sk-ant-api03-...`
3. **Guardar** el archivo

#### Verificar que funciona:

```bash
# En tu terminal bash:
cat config/.groq_key
```

Debería mostrar tu API key.

---

## 📌 PASO 3: VERIFICAR QUE FUNCIONA

### 3.1 Test rápido desde terminal

```bash
# Ejecutar test de IA
python test_ai_simple.py
```

### 3.2 Test desde la aplicación

1. **Arrancar el servidor**: `ARRANCAR.bat`
2. **Ir a**: http://localhost:8000/quiensoy.html
3. **Iniciar juego** como admin
4. **Hacer una pregunta**: "¿Es hombre?"
5. **Debería responder**: "Sí" o "No" usando Claude

---

## 📌 PASO 4: MODELOS DISPONIBLES

### Claude 3.5 Sonnet (RECOMENDADO)
- **Modelo**: `claude-3-5-sonnet-20241022`
- **Mejor para**: Respuestas inteligentes, razonamiento complejo
- **Precio**: Medio
- **Velocidad**: Rápida

### Claude 3 Haiku (MÁS BARATO)
- **Modelo**: `claude-3-haiku-20240307`
- **Mejor para**: Respuestas simples, alta velocidad
- **Precio**: Muy bajo (5x más barato)
- **Velocidad**: Muy rápida

### Claude 3 Opus (MÁS POTENTE)
- **Modelo**: `claude-3-opus-20240229`
- **Mejor para**: Tareas muy complejas
- **Precio**: Alto
- **Velocidad**: Más lenta

**Recomendación para tu caso**: Usa **Claude 3.5 Sonnet** para mejor calidad/precio.

---

## 📌 PASO 5: LÍMITES Y CUOTAS

### Rate Limits (Límites de uso)

**Tier 1 (Gratis - primeros $5):**
- 50 requests/minuto
- 40.000 tokens/minuto

**Tier 2 ($5+ gastados):**
- 1.000 requests/minuto
- 80.000 tokens/minuto

**Tier 3 ($40+ gastados):**
- 2.000 requests/minuto
- 160.000 tokens/minuto

### Monitorear uso

1. **Ir a**: https://console.anthropic.com/settings/usage
2. **Ver**: Cuánto has gastado hoy/mes
3. **Configurar alertas**: Para no gastar más de X

---

## 📌 PASO 6: MEJORES PRÁCTICAS

### 6.1 Seguridad

✅ **NUNCA** subas tu API key a Git  
✅ **NUNCA** la compartas públicamente  
✅ Guárdala en `config/.groq_key` (está en .gitignore)  
✅ Usa variables de entorno en producción  

### 6.2 Optimización de costes

✅ Usa **Claude 3 Haiku** para preguntas simples (5x más barato)  
✅ Usa **Claude 3.5 Sonnet** para preguntas complejas  
✅ Cachea respuestas comunes  
✅ Limita el tamaño de contexto (max_tokens)  

### 6.3 Manejo de errores

✅ Implementa reintentos automáticos (3 intentos)  
✅ Maneja errores de rate limit (espera y reintenta)  
✅ Tiene respuestas fallback si la API falla  

---

## 📌 PASO 7: ALTERNATIVAS (SI CLAUDE NO FUNCIONA)

### OpenAI (ChatGPT)
- **Web**: https://platform.openai.com/
- **Modelo**: `gpt-4o` o `gpt-4o-mini`
- **Precio**: Similar a Claude
- **Configurar**: Igual que Claude, pero en `config/.openai_key`

### Groq (MÁS RÁPIDO Y GRATIS)
- **Web**: https://console.groq.com/
- **Modelo**: `llama-3.1-70b-versatile`
- **Precio**: **GRATIS** (con límites)
- **Velocidad**: 10x más rápido que Claude
- **Configurar**: Igual que Claude, pero en `config/.groq_key`

**Recomendación**: Empieza con **Groq** (gratis) para probar, luego pasa a Claude si necesitas mejor calidad.

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "API key not found"
**Solución**: Verifica que el archivo `config/.groq_key` existe y contiene tu clave.

### Error: "Invalid API key"
**Solución**: Copia de nuevo la clave desde https://console.anthropic.com/

### Error: "Rate limit exceeded"
**Solución**: Espera 1 minuto y reintenta. O sube de tier añadiendo más créditos.

### Error: "Insufficient credits"
**Solución**: Añade más créditos en https://console.anthropic.com/settings/billing

### La IA responde mal o no responde
**Solución**: 
1. Verifica que la API key es correcta
2. Verifica que tienes créditos
3. Mira los logs del servidor para ver el error exacto

---

## 📞 SOPORTE

- **Documentación oficial**: https://docs.anthropic.com/
- **Discord de Anthropic**: https://discord.gg/anthropic
- **Email soporte**: support@anthropic.com

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta creada en Anthropic Console
- [ ] API Key obtenida
- [ ] Créditos añadidos ($20+ recomendado)
- [ ] API Key guardada en `config/.groq_key`
- [ ] Test ejecutado correctamente
- [ ] Juego "¿Quién soy?" funciona con IA

**¡Listo! Ahora tienes Claude funcionando correctamente.** 🎉
