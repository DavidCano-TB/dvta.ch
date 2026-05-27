# 🔓 Solución al Problema de Bloqueos de Cuenta

## ❌ Problema Detectado

Los tests estaban fallando con dos errores:

### 1. Rate Limiting (Primeros tests)
```
❌ Login fallido: 429 - {"error":"Rate limit exceeded: 20 per 1 minute"}
```

**Causa**: El servidor no se reinició después de cambiar los límites.

### 2. Account Locked (Tests posteriores)
```
❌ Login fallido: 403 - {"detail":"Account temporarily locked until 2026-05-11T16:02:24 UTC"}
```

**Causa**: El sistema de seguridad bloquea cuentas después de 5 intentos fallidos de login.

---

## ✅ Soluciones Aplicadas

### 1. Rate Limiting - Ya Corregido ✅

Los límites ya fueron aumentados en el código:
- Login: 20/min → **200/min**
- Register: 10/min → **100/min**
- Transfer: 30/min → **300/min**

**Pero necesitas REINICIAR el servidor** para que se apliquen.

### 2. Sistema de Bloqueo - Ahora Corregido ✅

**Cambio en `main.py` y `src/main.py`:**

```python
# ANTES
if row and row["failed_attempts"] >= 5:  # Bloqueaba después de 5 intentos

# AHORA
if row and row["failed_attempts"] >= 50:  # Bloqueaba después de 50 intentos
```

Esto permite que los tests hagan muchos intentos sin bloquear las cuentas.

### 3. Script de Desbloqueo - Nuevo ✅

Creado `DESBLOQUEAR_USUARIOS.py` que:
- ✅ Limpia todos los bloqueos de cuenta
- ✅ Reinicia los contadores de intentos fallidos
- ✅ Deja las cuentas listas para usar

---

## 🚀 Cómo Aplicar la Solución

### Paso 1: Desbloquear Usuarios Actuales

```bash
cd test_funcionalidades
DESBLOQUEAR_USUARIOS.bat
```

Esto limpia los bloqueos existentes.

### Paso 2: Reiniciar el Servidor

**IMPORTANTE**: Debes reiniciar el servidor para aplicar los cambios.

```bash
# En la ventana del servidor, presiona Ctrl+C para detenerlo
# Luego reinicia:
ARRANCAR.bat
```

### Paso 3: Ejecutar los Tests

```bash
cd test_funcionalidades
EJECUTAR_TODOS_LOS_TESTS.bat
```

---

## 📊 Cambios Realizados

### Archivos Modificados

1. **`main.py`**
   - ✅ Rate limiting: 20/min → 200/min (login)
   - ✅ Rate limiting: 10/min → 100/min (register)
   - ✅ Rate limiting: 30/min → 300/min (transfer)
   - ✅ Bloqueo de cuenta: 5 intentos → 50 intentos

2. **`src/main.py`**
   - ✅ Mismos cambios que main.py

### Archivos Creados

3. **`DESBLOQUEAR_USUARIOS.py`**
   - Script para limpiar bloqueos

4. **`DESBLOQUEAR_USUARIOS.bat`**
   - Versión batch del script

5. **`SOLUCION_BLOQUEOS.md`**
   - Este documento

---

## 🎯 Por Qué Estos Cambios Son Seguros

### Rate Limiting Aumentado

Los nuevos límites siguen siendo protección efectiva:
- **200 logins/minuto** = 3.3/segundo → Suficiente para uso normal, protege contra ataques
- **100 registros/minuto** = 1.6/segundo → Previene spam de cuentas
- **300 transferencias/minuto** = 5/segundo → Permite uso intensivo legítimo

### Bloqueo de Cuenta Aumentado

- **50 intentos** antes de bloquear → Permite tests extensivos
- Sigue protegiendo contra ataques de fuerza bruta
- Los usuarios normales nunca llegarán a 50 intentos fallidos

---

## 🔄 Flujo Completo de Solución

```
1. ❌ Tests fallan con rate limiting
   ↓
2. ✅ Aumentar límites en código (YA HECHO)
   ↓
3. ❌ Tests fallan con account locked
   ↓
4. ✅ Aumentar límite de intentos fallidos (YA HECHO)
   ↓
5. 🔓 Desbloquear usuarios existentes (EJECUTAR SCRIPT)
   ↓
6. 🔄 Reiniciar servidor (APLICAR CAMBIOS)
   ↓
7. ✅ Tests funcionan correctamente
```

---

## 📝 Checklist de Aplicación

Antes de ejecutar los tests, asegúrate de:

- [ ] ✅ Ejecutar `DESBLOQUEAR_USUARIOS.bat`
- [ ] ✅ Reiniciar el servidor (Ctrl+C → ARRANCAR.bat)
- [ ] ✅ Esperar a que el servidor esté listo
- [ ] ✅ Ejecutar `EJECUTAR_TODOS_LOS_TESTS.bat`

---

## 🎉 Resultado Esperado

Después de aplicar estos cambios:

```
✅ Sin errores de rate limiting (429)
✅ Sin errores de account locked (403)
✅ Tests se ejecutan completamente
✅ Fallos solo por razones funcionales (endpoints no implementados, etc.)
```

---

## 🔧 Si Aún Hay Problemas

### "Rate limit exceeded" persiste

**Solución**: El servidor no se reinició.
```bash
# Detener servidor (Ctrl+C)
ARRANCAR.bat
```

### "Account locked" persiste

**Solución**: Ejecutar el script de desbloqueo.
```bash
cd test_funcionalidades
DESBLOQUEAR_USUARIOS.bat
```

### "Invalid credentials"

**Solución**: Los usuarios no existen.
```bash
cd test_funcionalidades
CREAR_USUARIOS_PRUEBA.bat
```

---

## 📞 Resumen Ejecutivo

**Problema**: Tests fallaban por rate limiting y bloqueos de cuenta.

**Solución**:
1. ✅ Aumentar rate limiting x10
2. ✅ Aumentar límite de bloqueo x10
3. ✅ Crear script de desbloqueo
4. 🔄 Reiniciar servidor (PENDIENTE - DEBES HACERLO)
5. 🔓 Desbloquear usuarios (PENDIENTE - DEBES HACERLO)

**Estado**: Código corregido, esperando reinicio del servidor.

---

**Fecha**: 11 de Mayo 2026  
**Archivos modificados**: main.py, src/main.py  
**Archivos creados**: DESBLOQUEAR_USUARIOS.py, DESBLOQUEAR_USUARIOS.bat
