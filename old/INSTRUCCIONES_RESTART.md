# 🔄 Scripts de Reinicio DVDcoin Bank

## 📋 Descripción

Scripts definitivos para reiniciar el servidor DVDcoin Bank, matando todos los procesos (especialmente puerto 8000) y aplicando cualquier cambio del proyecto.

## 🚀 Uso Rápido

### Opción 1: Script BAT (Windows - Recomendado)
```bash
# Doble click en:
RESTART_SERVER.bat
```
- ✅ Auto-solicita privilegios de administrador
- ✅ Mata todos los procesos (puerto 8000, Python, ngrok)
- ✅ Limpia archivos temporales
- ✅ Reinicia el servidor automáticamente
- ✅ Abre el navegador

### Opción 2: Script Python (Multiplataforma)
```bash
python restart_server.py
```
- ✅ Funciona en Windows, Linux y Mac
- ✅ Salida con colores y progreso visual
- ✅ Más control y feedback detallado

### Opción 3: Script Admin Directo (Windows)
```bash
# Click derecho -> "Ejecutar como administrador"
RESTART_SERVER_ADMIN.bat
```
- ⚠️ Requiere ejecutar manualmente como admin
- ✅ Mismo resultado que Opción 1

## 🔧 Qué Hace el Script

### 1️⃣ Termina Procesos
- ✅ Mata procesos en puerto **8000**
- ✅ Termina todos los procesos **Python** (python.exe, pythonw.exe, py.exe)
- ✅ Termina procesos **ngrok**
- ✅ Termina procesos **watchdog**
- ✅ Verifica que el puerto 8000 queda libre

### 2️⃣ Limpia Archivos Temporales
- ✅ Elimina carpetas `__pycache__`
- ✅ Elimina archivos `.pyc`
- ✅ Limpia logs antiguos de ngrok (mantiene los 5 más recientes)

### 3️⃣ Verifica Dependencias
- ✅ Comprueba que Python está instalado
- ✅ Verifica que fastapi y uvicorn están disponibles
- ✅ Instala dependencias faltantes automáticamente

### 4️⃣ Reinicia el Servidor
- ✅ Usa `start.py` si existe (incluye ngrok)
- ✅ Usa `main.py` como fallback
- ✅ Ejecuta en segundo plano (ventana minimizada)
- ✅ Guarda logs en `server.log`

### 5️⃣ Verifica que Funciona
- ✅ Espera hasta 20 segundos a que el servidor responda
- ✅ Comprueba que el puerto 8000 está activo
- ✅ Intenta obtener la URL pública de ngrok
- ✅ Abre el navegador automáticamente

## 📊 Salida del Script

```
============================================================================
 REINICIO COMPLETO - DVDcoin Bank
============================================================================

[1/5] Matando procesos en puerto 8000...
  > Matando PID 12345 en puerto 8000
[2/5] Matando procesos Python (main.py, start.py, uvicorn)...
[3/5] Matando procesos ngrok...
[4/5] Matando procesos watchdog...
[5/5] Verificando que puerto 8000 está libre...

============================================
 PROCESOS ELIMINADOS CORRECTAMENTE
============================================

[LIMPIEZA] Limpiando archivos temporales...
  > Archivos temporales limpiados

[VERIFICACION] Verificando dependencias...
  > Dependencias OK

============================================
 REINICIANDO SERVIDOR
============================================

[INICIO] Usando start.py (con ngrok)...
  > Servidor iniciado con start.py
  > Ventana minimizada: "DVDcoin Server"

[ESPERA] Esperando a que el servidor arranque...
[VERIFICACION] Comprobando que el servidor responde...

============================================
 SERVIDOR REINICIADO CORRECTAMENTE
============================================

  URL Local:   http://localhost:8000
  Estado:      ACTIVO
  URL Publica: https://unhidden-patient-cradling.ngrok-free.dev

  Logs:        server.log
  Procesos:    Usa "tasklist | findstr python" para ver PIDs

============================================
 CAMBIOS APLICADOS - Sistema listo
============================================
```

## 🛠️ Solución de Problemas

### ❌ "Se requieren privilegios de ADMIN"
**Solución:** Usa `RESTART_SERVER.bat` (auto-eleva) o click derecho → "Ejecutar como administrador"

### ❌ "Puerto 8000 aún ocupado"
**Solución:** 
1. Abre el Administrador de tareas (Ctrl+Shift+Esc)
2. Busca procesos "Python" o "uvicorn"
3. Termínalos manualmente
4. Ejecuta el script de nuevo

### ❌ "Python no encontrado en PATH"
**Solución:** 
1. Instala Python desde https://www.python.org/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia la terminal

### ❌ "No se pudieron instalar las dependencias"
**Solución:**
```bash
# Instalar manualmente
pip install -r requirements.txt
```

### ❌ "Servidor no respondió en 20 segundos"
**Solución:**
1. Revisa `server.log` para ver errores
2. Verifica que no hay errores de sintaxis en `main.py`
3. Comprueba que la base de datos no está corrupta

## 📝 Cuándo Usar Este Script

✅ **Después de cambiar código** → Aplica cambios inmediatamente  
✅ **Cuando el servidor no responde** → Reinicio limpio  
✅ **Después de actualizar dependencias** → Recarga todo  
✅ **Cuando el puerto 8000 está ocupado** → Libera y reinicia  
✅ **Después de cambios en la base de datos** → Reinicia conexiones  
✅ **Cuando ngrok no funciona** → Reinicia túnel  

## 🔍 Archivos Creados

| Archivo | Descripción |
|---------|-------------|
| `RESTART_SERVER.bat` | 🎯 **Launcher principal** - Auto-eleva a admin |
| `RESTART_SERVER_ADMIN.bat` | 🔧 Script completo con todas las funciones |
| `restart_server.py` | 🐍 Versión Python multiplataforma |
| `INSTRUCCIONES_RESTART.md` | 📖 Este archivo de documentación |

## 💡 Consejos

1. **Usa `RESTART_SERVER.bat`** para reinicio rápido (doble click)
2. **Usa `restart_server.py`** si quieres ver más detalles del proceso
3. **Revisa `server.log`** si algo falla
4. **Mantén una terminal abierta** para ver logs en tiempo real:
   ```bash
   tail -f server.log  # Linux/Mac
   Get-Content server.log -Wait  # PowerShell
   ```

## 🎯 Atajos de Teclado

Puedes crear un atajo en el escritorio:
1. Click derecho en `RESTART_SERVER.bat`
2. "Crear acceso directo"
3. Arrastra el acceso directo al escritorio
4. (Opcional) Click derecho → Propiedades → Cambiar icono

## 📞 Soporte

Si el script no funciona:
1. Revisa `server.log` para errores
2. Verifica que Python está instalado: `python --version`
3. Verifica dependencias: `pip list | findstr fastapi`
4. Ejecuta manualmente: `python main.py` para ver errores directos

---

**✨ Script creado para aplicar cambios instantáneamente en DVDcoin Bank**
