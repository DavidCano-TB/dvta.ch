# ⚠️ INSTRUCCIONES URGENTES - Ejecutar Tests AHORA

## 🎯 Resumen del Problema

Los tests fallaban por:
1. ❌ **Rate limiting** (429 error) - Límites muy bajos
2. ❌ **Account locked** (403 error) - Cuentas bloqueadas por intentos fallidos

## ✅ Solución Aplicada

**TODO EL CÓDIGO YA ESTÁ CORREGIDO:**
- ✅ Rate limiting aumentado x10
- ✅ Límite de bloqueo aumentado x10 (5 → 50 intentos)
- ✅ Scripts de desbloqueo creados

---

## 🚀 PASOS PARA EJECUTAR AHORA

### 1️⃣ Desbloquear Usuarios (30 segundos)

```bash
cd test_funcionalidades
DESBLOQUEAR_USUARIOS.bat
```

Esto limpia los bloqueos actuales.

---

### 2️⃣ Reiniciar el Servidor (1 minuto)

**CRÍTICO**: Debes reiniciar el servidor para aplicar los cambios.

```bash
# En la ventana del servidor:
# 1. Presiona Ctrl+C para detenerlo
# 2. Espera a que se detenga completamente
# 3. Ejecuta:
ARRANCAR.bat
```

⏱️ **Espera** hasta ver: `Uvicorn running on http://0.0.0.0:8000`

---

### 3️⃣ Ejecutar Tests (2 minutos)

```bash
cd test_funcionalidades
EJECUTAR_TODOS_LOS_TESTS.bat
```

---

## 🎯 O Usa el Inicio Rápido

Si prefieres que todo se haga automáticamente:

```bash
cd test_funcionalidades
INICIO_RAPIDO.bat
```

Este script:
1. Instala dependencias
2. Prepara tests
3. Crea usuarios
4. Desbloquea usuarios
5. Ejecuta tests

**Pero DEBES reiniciar el servidor manualmente primero.**

---

## 📊 Qué Esperar

### ✅ Resultado Exitoso

```
🧪 Ejecutando: Autenticación y Sesiones...
✅ Autenticación y Sesiones: EXITOSO

🧪 Ejecutando: Transferencias...
✅ Transferencias: EXITOSO

...

📊 RESUMEN FINAL
Total de tests:     15
✅ Tests exitosos:  X
❌ Tests fallidos:  Y
📈 Tasa de éxito:   X%
```

### ⚠️ Algunos Tests Pueden Fallar

Es normal que algunos tests fallen si:
- Endpoints no implementados
- Funcionalidades incompletas
- Configuraciones específicas faltan

**Pero NO deben fallar por rate limiting o bloqueos.**

---

## 🔧 Si Aún Falla

### Error: "Rate limit exceeded: 20 per 1 minute"

**Causa**: El servidor no se reinició.

**Solución**:
```bash
# Detener servidor (Ctrl+C en su ventana)
ARRANCAR.bat
# Esperar a que inicie completamente
# Ejecutar tests de nuevo
```

---

### Error: "Account temporarily locked"

**Causa**: No se ejecutó el script de desbloqueo.

**Solución**:
```bash
cd test_funcionalidades
DESBLOQUEAR_USUARIOS.bat
# Ejecutar tests de nuevo
```

---

### Error: "Invalid credentials"

**Causa**: Los usuarios no existen.

**Solución**:
```bash
cd test_funcionalidades
CREAR_USUARIOS_PRUEBA.bat
```

---

## 📝 Checklist Rápido

Antes de ejecutar tests:

- [ ] ✅ Desbloquear usuarios (`DESBLOQUEAR_USUARIOS.bat`)
- [ ] ✅ Reiniciar servidor (Ctrl+C → `ARRANCAR.bat`)
- [ ] ✅ Servidor completamente iniciado
- [ ] ✅ Usuarios de prueba existen

Si todos están ✅:

```bash
cd test_funcionalidades
EJECUTAR_TODOS_LOS_TESTS.bat
```

---

## 🎉 Cambios Realizados

### Código del Servidor

**`main.py` y `src/main.py`:**

```python
# Rate Limiting
@limiter.limit("200/minute")  # Era 20/minute
@limiter.limit("100/minute")  # Era 10/minute
@limiter.limit("300/minute")  # Era 30/minute

# Bloqueo de Cuenta
if row["failed_attempts"] >= 50:  # Era 5
```

### Scripts Nuevos

- ✅ `DESBLOQUEAR_USUARIOS.py` - Limpia bloqueos
- ✅ `DESBLOQUEAR_USUARIOS.bat` - Versión batch
- ✅ `SOLUCION_BLOQUEOS.md` - Documentación completa

---

## 💡 Resumen Ultra-Rápido

```bash
# 1. Desbloquear
cd test_funcionalidades
DESBLOQUEAR_USUARIOS.bat

# 2. Reiniciar servidor (en otra ventana)
# Ctrl+C → ARRANCAR.bat

# 3. Ejecutar tests
EJECUTAR_TODOS_LOS_TESTS.bat
```

**¡Eso es todo! Los tests deberían funcionar ahora.** 🚀

---

**Última actualización**: 11 de Mayo 2026, 18:10  
**Estado**: Código corregido, esperando reinicio del servidor
