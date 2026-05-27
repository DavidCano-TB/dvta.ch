# 🔧 GUÍA DE SERVICIOS WINDOWS - DVDcoin Platform

## 📋 Índice
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Gestión de Servicios](#gestión-de-servicios)
4. [Añadir Nuevos Servicios](#añadir-nuevos-servicios)
5. [Solución de Problemas](#solución-de-problemas)
6. [Arquitectura](#arquitectura)

---

## 🎯 Introducción

Los servicios Windows permiten que las aplicaciones DVDcoin se ejecuten automáticamente al iniciar el sistema, sin necesidad de intervención manual. Cada funcionalidad tiene su propio servicio dedicado.

### Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **DVDcoin-Bank** | 8000 | Sistema bancario principal |
| **DVDcoin-Exams** | 8001 | Sistema de exámenes y oposiciones |
| **DVDcoin-Tunnel** | - | Túnel Cloudflare para acceso externo |

### Ventajas

✅ **Inicio automático** - Se inician con Windows  
✅ **Reinicio automático** - Se recuperan de fallos  
✅ **Gestión centralizada** - Fácil administración  
✅ **Logs del sistema** - Registro en Event Viewer  
✅ **Aislamiento** - Cada servicio es independiente  

---

## 📦 Instalación

### Requisitos Previos

- Windows 10/11 o Windows Server
- Python 3.8 o superior instalado
- Privilegios de administrador
- Puertos 8000 y 8001 disponibles

### Instalación Rápida

1. **Ejecutar como Administrador**:
   ```
   INSTALAR_SERVICIOS.bat
   ```

2. **Esperar a que termine** (puede tomar 1-2 minutos)

3. **Verificar instalación**:
   ```
   GESTIONAR_SERVICIOS.bat
   ```

### Instalación Manual

Si prefieres instalar manualmente:

```powershell
# Abrir PowerShell como Administrador
cd C:\dvdcoin\services

# Instalar pywin32
python -m pip install pywin32

# Ejecutar instalador
.\install_services.ps1
```

### Verificación

Después de la instalación, verifica que los servicios estén corriendo:

```powershell
Get-Service -Name "DVDcoin-*"
```

Deberías ver:

```
Status   Name               DisplayName
------   ----               -----------
Running  DVDcoin-Bank       DVDcoin Bank Server
Running  DVDcoin-Exams      DVDcoin Exams Server
Running  DVDcoin-Tunnel     DVDcoin Cloudflare Tunnel
```

---

## 🎮 Gestión de Servicios

### Gestor Interactivo

La forma más fácil de gestionar los servicios:

```
GESTIONAR_SERVICIOS.bat
```

Opciones disponibles:
1. Ver estado de servicios
2. Iniciar todos los servicios
3. Detener todos los servicios
4. Reiniciar todos los servicios
5. Ver logs recientes
6. Gestionar servicio individual

### Comandos PowerShell

#### Ver Estado
```powershell
Get-Service -Name "DVDcoin-*"
```

#### Iniciar Servicios
```powershell
# Todos
Start-Service -Name "DVDcoin-*"

# Individual
Start-Service -Name "DVDcoin-Bank"
```

#### Detener Servicios
```powershell
# Todos
Stop-Service -Name "DVDcoin-*" -Force

# Individual
Stop-Service -Name "DVDcoin-Exams" -Force
```

#### Reiniciar Servicios
```powershell
# Todos
Restart-Service -Name "DVDcoin-*"

# Individual
Restart-Service -Name "DVDcoin-Tunnel"
```

#### Ver Logs
```powershell
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20
```

### Administrador de Servicios de Windows

También puedes usar la herramienta nativa de Windows:

1. Presiona `Win + R`
2. Escribe `services.msc`
3. Busca servicios que empiecen con "DVDcoin"

---

## ➕ Añadir Nuevos Servicios

Cuando crees una nueva funcionalidad, puedes añadirla como servicio Windows.

### Método 1: Script Automático

```powershell
# Abrir PowerShell como Administrador
cd C:\dvdcoin\services

.\add_new_service.ps1 `
    -ServiceName "DVDcoin-Games" `
    -DisplayName "DVDcoin Games Server" `
    -Description "Servidor de juegos DVDcoin (Puerto 8002)" `
    -WorkingDir "C:\dvdcoin\modules\games" `
    -Script "start_games.py" `
    -Port 8002
```

### Método 2: Manual

1. **Crear el módulo**:
   ```
   C:\dvdcoin\modules\tu_modulo\
   ├── start_tu_modulo.py
   ├── app_tu_modulo.py
   └── ...
   ```

2. **Crear wrapper del servicio**:
   
   Copia `services\DVDcoin-Exams-wrapper.py` y modifica:
   - `_svc_name_`
   - `_svc_display_name_`
   - `_svc_description_`
   - Rutas de `WorkingDir` y `Script`

3. **Instalar servicio**:
   ```powershell
   python tu_servicio-wrapper.py install
   Set-Service -Name "DVDcoin-TuModulo" -StartupType Automatic
   Start-Service -Name "DVDcoin-TuModulo"
   ```

### Ejemplo Completo: Módulo de Juegos

```python
# modules/games/start_games.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="DVDcoin Games")

@app.get("/")
async def root():
    return {"message": "Games Server Running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Games", "port": 8002}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

Luego añadir como servicio:

```powershell
.\add_new_service.ps1 `
    -ServiceName "DVDcoin-Games" `
    -DisplayName "DVDcoin Games Server" `
    -Description "Servidor de juegos DVDcoin (Puerto 8002)" `
    -WorkingDir "C:\dvdcoin\modules\games" `
    -Script "start_games.py" `
    -Port 8002
```

### Actualizar Cloudflare Tunnel

Si el nuevo servicio necesita acceso externo, actualiza `cloudflare-dvta-config.yml`:

```yaml
ingress:
  # Nuevo servicio
  - hostname: games.dvta.ch
    service: http://localhost:8002
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
  
  # Servicios existentes...
  - hostname: dvta.ch
    service: http://localhost:8001
  
  # ...resto de configuración
```

Luego reinicia el tunnel:

```powershell
Restart-Service -Name "DVDcoin-Tunnel"
```

---

## 🔧 Solución de Problemas

### Servicio No Inicia

**Síntomas**: El servicio aparece como "Stopped" o "Starting"

**Soluciones**:

1. **Verificar logs**:
   ```powershell
   Get-EventLog -LogName Application -Source "DVDcoin-Bank" -Newest 10
   ```

2. **Verificar puerto**:
   ```powershell
   netstat -ano | findstr ":8000"
   ```
   Si el puerto está ocupado, detén el proceso:
   ```powershell
   Stop-Process -Id <PID> -Force
   ```

3. **Verificar script**:
   ```powershell
   cd C:\dvdcoin
   python main.py
   ```
   Si hay errores, corrígelos antes de reiniciar el servicio.

4. **Reinstalar servicio**:
   ```powershell
   python services\DVDcoin-Bank-wrapper.py remove
   python services\DVDcoin-Bank-wrapper.py install
   Start-Service -Name "DVDcoin-Bank"
   ```

### Error "Access Denied"

**Causa**: No tienes privilegios de administrador

**Solución**: Ejecuta PowerShell o el script como Administrador

### Servicio Se Detiene Solo

**Causa**: El script Python tiene un error

**Solución**:

1. Ver logs del servicio
2. Ejecutar el script manualmente para ver el error
3. Corregir el error
4. Reiniciar el servicio

### Puerto Ya en Uso

**Síntomas**: Error "Address already in use"

**Solución**:

```powershell
# Encontrar proceso usando el puerto
netstat -ano | findstr ":8000"

# Detener proceso
Stop-Process -Id <PID> -Force

# Reiniciar servicio
Start-Service -Name "DVDcoin-Bank"
```

### Desinstalar y Reinstalar

Si nada funciona:

```
1. DESINSTALAR_SERVICIOS.bat
2. Reiniciar Windows
3. INSTALAR_SERVICIOS.bat
```

---

## 🏗️ Arquitectura

### Estructura de Archivos

```
C:\dvdcoin\
├── services/
│   ├── install_services.ps1          # Instalador principal
│   ├── uninstall_services.ps1        # Desinstalador
│   ├── manage_services.ps1           # Gestor interactivo
│   ├── add_new_service.ps1           # Añadir nuevo servicio
│   ├── DVDcoin-Bank-wrapper.py       # Wrapper servicio Bank
│   ├── DVDcoin-Exams-wrapper.py      # Wrapper servicio Exams
│   └── DVDcoin-Tunnel-wrapper.py     # Wrapper servicio Tunnel
├── modules/
│   ├── exams/
│   │   ├── start_exams.py            # Punto de entrada Exams
│   │   └── app_exams.py              # Aplicación FastAPI
│   └── [nuevo_modulo]/
│       ├── start_[modulo].py         # Punto de entrada
│       └── app_[modulo].py           # Aplicación FastAPI
├── main.py                            # Punto de entrada Bank
├── INSTALAR_SERVICIOS.bat            # Script instalación
├── DESINSTALAR_SERVICIOS.bat         # Script desinstalación
└── GESTIONAR_SERVICIOS.bat           # Script gestión
```

### Flujo de Ejecución

```
Windows Startup
    ↓
Service Control Manager
    ↓
DVDcoin Service Wrapper (Python)
    ↓
subprocess.Popen()
    ↓
Aplicación FastAPI (uvicorn)
    ↓
Servidor HTTP escuchando en puerto
```

### Características del Wrapper

- **Auto-reinicio**: Si el proceso muere, se reinicia automáticamente
- **Gestión de eventos**: Maneja señales de Windows (stop, pause, etc.)
- **Logging**: Registra eventos en Windows Event Log
- **Aislamiento**: Cada servicio corre en su propio proceso

### Dependencias

```
pywin32
    ├── win32serviceutil  # Utilidades de servicios
    ├── win32service      # API de servicios Windows
    ├── win32event        # Eventos de Windows
    └── servicemanager    # Gestor de servicios
```

---

## 📚 Referencias

### Comandos Útiles

```powershell
# Ver todos los servicios DVDcoin
Get-Service -Name "DVDcoin-*" | Format-Table -AutoSize

# Ver estado detallado
Get-Service -Name "DVDcoin-Bank" | Select-Object *

# Ver logs de errores
Get-EventLog -LogName Application -EntryType Error -Source "DVDcoin-*" -Newest 10

# Cambiar tipo de inicio
Set-Service -Name "DVDcoin-Bank" -StartupType Automatic

# Deshabilitar servicio
Set-Service -Name "DVDcoin-Bank" -StartupType Disabled
```

### Tipos de Inicio

- **Automatic**: Inicia con Windows
- **Automatic (Delayed Start)**: Inicia después de otros servicios
- **Manual**: Requiere inicio manual
- **Disabled**: No se puede iniciar

### Estados de Servicio

- **Running**: Servicio corriendo
- **Stopped**: Servicio detenido
- **Starting**: Iniciando
- **Stopping**: Deteniéndose
- **Paused**: Pausado

---

## 🎯 Mejores Prácticas

1. **Siempre ejecutar como Administrador** al instalar/desinstalar servicios

2. **Verificar logs regularmente**:
   ```powershell
   Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20
   ```

3. **Hacer backup antes de cambios importantes**:
   ```
   BACKUP_COMPLETO.bat
   ```

4. **Probar scripts manualmente** antes de convertirlos en servicios

5. **Usar puertos únicos** para cada servicio

6. **Documentar cambios** en servicios y configuraciones

7. **Monitorear recursos** (CPU, memoria) de los servicios

8. **Actualizar Cloudflare Tunnel** cuando añadas nuevos servicios con acceso externo

---

## ✅ Checklist de Nuevo Servicio

Cuando crees un nuevo módulo/servicio:

- [ ] Crear directorio en `modules/[nombre]`
- [ ] Crear script de inicio `start_[nombre].py`
- [ ] Probar script manualmente
- [ ] Elegir puerto único
- [ ] Ejecutar `add_new_service.ps1`
- [ ] Verificar que el servicio inicia
- [ ] Probar endpoint `/health`
- [ ] Actualizar `cloudflare-dvta-config.yml` si necesario
- [ ] Reiniciar Cloudflare Tunnel
- [ ] Documentar en README
- [ ] Commit y push a GitHub

---

**¡Los servicios Windows hacen que DVDcoin Platform sea robusto y confiable!** 🚀
