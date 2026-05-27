# 🔧 GUÍA RÁPIDA DE SOLUCIÓN DE PROBLEMAS

**Versión**: 1.0  
**Fecha**: 27 Mayo 2026  
**Sistema**: DVDcoin v2.0 - dvta.ch

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### 1. ❌ Error 502 Bad Gateway en dvta.ch

**Síntomas**:
- Al abrir https://dvta.ch aparece "Error 502 Bad Gateway"
- Cloudflare muestra error de conexión

**Causa**:
- El servidor Exams no está corriendo en puerto 8001
- Cloudflare Tunnel está activo pero no hay servidor

**Solución Rápida**:
```batch
ACTIVAR_DVTA_CH_AHORA.bat
```

**Solución Manual**:
```batch
# Terminal 1: Iniciar servidor
cd modules\exams
python start_exams.py

# Terminal 2: Iniciar tunnel
cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
```

**Verificación**:
```batch
netstat -ano | findstr ":8001"
# Debe mostrar: TCP 0.0.0.0:8001 ... LISTENING
```

---

### 2. ❌ Puerto 8001 ya está en uso

**Síntomas**:
- Error al iniciar: "Address already in use"
- El servidor no puede iniciar

**Causa**:
- Otro proceso Python está usando el puerto 8001

**Solución**:
```batch
# Detener todos los procesos Python
taskkill /F /IM python.exe

# Esperar 2 segundos
timeout /t 2

# Reiniciar
ACTIVAR_DVTA_CH_AHORA.bat
```

**Verificación**:
```batch
netstat -ano | findstr ":8001"
# Si muestra algo, identifica el PID y mátalo:
taskkill /F /PID [número_del_pid]
```

---

### 3. ❌ dvta.ch no carga (página en blanco)

**Síntomas**:
- La página carga pero está en blanco
- No aparece contenido

**Causa**:
- El tunnel está conectando
- Archivos estáticos no se cargan

**Solución**:
```batch
# Espera 30-60 segundos
# Luego recarga con Ctrl+F5 (recarga forzada)
```

**Si persiste**:
```batch
# Verifica que los archivos estáticos existen
dir modules\exams\static\index.html
dir modules\exams\static\css\exams-style.css

# Si faltan, restaura desde backup
ACTUALIZAR_DESDE_GIT.bat
```

---

### 4. ❌ Error 1033 en Cloudflare

**Síntomas**:
- Error 1033: "Argo Tunnel error"
- Cloudflare no puede conectar

**Causa**:
- Cloudflare Tunnel no está corriendo
- Configuración incorrecta

**Solución**:
```batch
# Detener tunnel anterior
taskkill /F /IM cloudflared.exe

# Reiniciar
cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
```

**Verificación**:
```batch
tasklist | findstr "cloudflared.exe"
# Debe mostrar al menos un proceso cloudflared.exe
```

---

### 5. ❌ Dependencias faltantes (ImportError)

**Síntomas**:
- Error: "No module named 'fastapi'"
- Error: "No module named 'uvicorn'"

**Causa**:
- Dependencias Python no instaladas

**Solución**:
```batch
cd modules\exams
pip install -r requirements.txt
```

**Verificación**:
```batch
python -c "import fastapi, uvicorn, pydantic, bcrypt, jose"
# Si no hay error, las dependencias están OK
```

---

### 6. ❌ Auto-arranque no funciona

**Síntomas**:
- El sistema no inicia al arrancar Windows
- Hay que iniciar manualmente

**Causa**:
- Auto-arranque no configurado
- Configuración incorrecta

**Solución**:
```batch
# Verificar estado
VERIFICAR_AUTOARRANQUE.bat

# Si no está configurado
CONFIGURAR_AUTOARRANQUE_COMPLETO.bat
# (Ejecutar como administrador)
```

**Verificación**:
```batch
# Después de reiniciar Windows
VERIFICAR_ESTADO_AHORA.bat
```

---

### 7. ❌ Múltiples procesos Python conflictivos

**Síntomas**:
- Muchos procesos python.exe corriendo
- Comportamiento errático

**Causa**:
- Inicios múltiples sin detener anteriores

**Solución**:
```batch
# Detener TODOS los procesos Python
taskkill /F /IM python.exe

# Detener TODOS los Cloudflare
taskkill /F /IM cloudflared.exe

# Esperar
timeout /t 3

# Iniciar limpio
ACTIVAR_DVTA_CH_AHORA.bat
```

---

### 8. ❌ Base de datos corrupta

**Síntomas**:
- Error: "database disk image is malformed"
- Datos no se guardan

**Causa**:
- Base de datos SQLite corrupta

**Solución**:
```batch
# Restaurar desde backup
cd modules\exams\data
copy /Y ..\..\..\backup\[fecha]\*.db .

# O crear nueva
del users_exams.db
del exams.db
# El sistema creará nuevas al iniciar
```

---

### 9. ❌ Git push falla

**Síntomas**:
- Error al hacer push
- "rejected" o "conflict"

**Causa**:
- Cambios remotos no sincronizados

**Solución**:
```batch
# Actualizar desde remoto
git pull --rebase

# Resolver conflictos si hay
# Luego push
git push
```

---

### 10. ❌ Cloudflare Tunnel desconectado

**Síntomas**:
- dvta.ch no accesible
- Tunnel muestra "disconnected"

**Causa**:
- Conexión a internet perdida
- Tunnel cerrado

**Solución**:
```batch
# Reiniciar tunnel
taskkill /F /IM cloudflared.exe
timeout /t 2
cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
```

---

## 🛠️ HERRAMIENTAS DE DIAGNÓSTICO

### Verificar Estado General
```batch
VERIFICAR_ESTADO_AHORA.bat
```

### Dashboard en Tiempo Real
```batch
DASHBOARD_SISTEMA.bat
```

### Diagnóstico Completo
```batch
DIAGNOSTICO_COMPLETO.bat
```

### Monitor Continuo
```batch
MONITOR_SISTEMA.bat
```

### Tests Automatizados
```batch
TEST_COMPLETO_SISTEMA.bat
```

---

## 📊 COMANDOS ÚTILES

### Ver puertos en uso
```batch
netstat -ano | findstr ":8000 :8001"
```

### Ver procesos Python
```batch
tasklist | findstr "python.exe"
```

### Ver procesos Cloudflare
```batch
tasklist | findstr "cloudflared.exe"
```

### Matar proceso por PID
```batch
taskkill /F /PID [número]
```

### Matar todos los Python
```batch
taskkill /F /IM python.exe
```

### Verificar conectividad local
```batch
curl http://localhost:8001/health
# O en PowerShell:
Invoke-WebRequest -Uri "http://localhost:8001/health"
```

---

## 🔍 LOGS Y DEPURACIÓN

### Ver logs del servidor
- Ventana "DVDExams Server" muestra logs en tiempo real
- Mantén esta ventana abierta para ver errores

### Ver logs del tunnel
- Ventana "Cloudflare Tunnel" muestra logs de conexión
- Busca "registered tunnel connection" para confirmar conexión

### Logs de Python
```batch
cd modules\exams
python start_exams.py
# Los errores aparecerán en consola
```

---

## 🚀 SOLUCIÓN UNIVERSAL

**Si nada funciona, usa la solución definitiva**:

```batch
# 1. Limpiar todo
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe
timeout /t 3

# 2. Verificar que todo está limpio
netstat -ano | findstr ":8001"
# No debe mostrar nada

# 3. Iniciar desde cero
ACTIVAR_DVTA_CH_AHORA.bat

# 4. Esperar 30 segundos
timeout /t 30

# 5. Verificar
VERIFICAR_ESTADO_AHORA.bat

# 6. Abrir navegador
start https://dvta.ch
```

---

## 📞 ESCALACIÓN

Si después de intentar todas las soluciones el problema persiste:

1. **Ejecuta diagnóstico completo**:
   ```batch
   DIAGNOSTICO_COMPLETO.bat > diagnostico.txt
   ```

2. **Revisa documentación**:
   - `ERROR_502_RESUELTO.md` - Último problema resuelto
   - `ESTADO_ACTUAL_SISTEMA.md` - Estado actual
   - `ARQUITECTURA_MODULAR_IMPLEMENTADA.md` - Detalles técnicos

3. **Verifica archivos críticos**:
   - `modules/exams/app_exams.py`
   - `modules/exams/start_exams.py`
   - `cloudflare-dvta-config.yml`

4. **Restaura desde Git**:
   ```batch
   ACTUALIZAR_DESDE_GIT.bat
   ```

---

## ✅ PREVENCIÓN

### Para evitar problemas:

1. **Usa auto-arranque**:
   ```batch
   CONFIGURAR_AUTOARRANQUE_COMPLETO.bat
   ```

2. **Haz backups regulares**:
   ```batch
   BACKUP_COMPLETO.bat
   ```

3. **Monitorea el sistema**:
   ```batch
   DASHBOARD_SISTEMA.bat
   ```

4. **Actualiza regularmente**:
   ```batch
   ACTUALIZAR_DESDE_GIT.bat
   ```

5. **Verifica después de cambios**:
   ```batch
   TEST_COMPLETO_SISTEMA.bat
   ```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `ERROR_502_RESUELTO.md` - Resolución detallada del error 502
- `ESTADO_ACTUAL_SISTEMA.md` - Estado actual del sistema
- `GUIA_AUTOARRANQUE.md` - Configuración de auto-arranque
- `LEEME_PRIMERO.txt` - Guía de inicio rápido
- `README_DVTA_CH.md` - Documentación completa de dvta.ch

---

**Última actualización**: 27 Mayo 2026  
**Versión**: 1.0  
**Estado**: ✅ Probado y verificado

---

**💡 Consejo**: Guarda esta guía en tus favoritos para acceso rápido cuando necesites solucionar problemas.
