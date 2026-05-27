# 🎯 Sistema de Servicios Windows - DVDcoin Platform

## ✅ Estado del Sistema

### Servicios Implementados

| Servicio | Puerto | Descripción | Estado |
|----------|--------|-------------|--------|
| **DVDcoin-Bank** | 8000 | Sistema bancario principal | ✅ Listo |
| **DVDcoin-Exams** | 8001 | Plataforma de exámenes | ✅ Listo |
| **DVDcoin-Tunnel** | - | Túnel Cloudflare (dvta.ch) | ✅ Listo |

### URLs de Acceso

| Servicio | URL Local | URL Externa |
|----------|-----------|-------------|
| Bank | http://localhost:8000 | https://bank.dvta.ch |
| Exams | http://localhost:8001 | https://dvta.ch |

---

## 🚀 Inicio Rápido

### 1. Instalar Servicios (Primera vez)

```cmd
# Ejecutar como Administrador
INSTALAR_SERVICIOS.bat
```

**Esto hará**:
- ✅ Instalar dependencias (pywin32)
- ✅ Crear wrappers de servicios
- ✅ Instalar 3 servicios Windows
- ✅ Configurar auto-inicio
- ✅ Iniciar todos los servicios

### 2. Verificar Estado

```cmd
VER_ESTADO_SERVICIOS.bat
```

### 3. Gestionar Servicios

```cmd
GESTIONAR_SERVICIOS.bat
```

---

## 📋 Arquitectura del Sistema

### Estructura de Archivos

```
C:\dvdcoin\
│
├── main.py                          # Servidor Bank (Puerto 8000)
├── modules\
│   └── exams\
│       └── start_exams.py           # Servidor Exams (Puerto 8001)
│
├── cloudflare-dvta-config.yml       # Configuración Cloudflare Tunnel
│
├── services\                        # Scripts de servicios
│   ├── install_services.ps1         # Instalador PowerShell
│   ├── manage_services.ps1          # Gestor PowerShell
│   ├── uninstall_services.ps1       # Desinstalador PowerShell
│   ├── DVDcoin-Bank-wrapper.py      # Wrapper servicio Bank
│   ├── DVDcoin-Exams-wrapper.py     # Wrapper servicio Exams
│   └── DVDcoin-Tunnel-wrapper.py    # Wrapper servicio Tunnel
│
├── INSTALAR_SERVICIOS.bat           # 🔧 Instalador fácil
├── VER_ESTADO_SERVICIOS.bat         # 📊 Ver estado
├── GESTIONAR_SERVICIOS.bat          # 🎮 Gestor interactivo
├── DESINSTALAR_SERVICIOS.bat        # 🗑️ Desinstalador
│
└── GUIA_SERVICIOS_WINDOWS.md        # 📖 Guía completa
```

### Flujo de Funcionamiento

```
Windows Boot
    ↓
Servicios Windows se inician automáticamente
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  DVDcoin-Bank   │ DVDcoin-Exams   │ DVDcoin-Tunnel  │
│   (Puerto 8000) │  (Puerto 8001)  │  (Cloudflare)   │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                   ↓                   ↓
localhost:8000    localhost:8001      Cloudflare
    ↓                   ↓                   ↓
bank.dvta.ch         dvta.ch          (Túnel seguro)
```

---

## 🔧 Características de los Servicios

### Auto-Inicio
- ✅ Se inician automáticamente con Windows
- ✅ No requieren inicio de sesión
- ✅ Funcionan en segundo plano

### Auto-Reinicio
- ✅ Se reinician automáticamente si fallan
- ✅ Reintentos cada 5 segundos
- ✅ Logs de errores en el sistema

### Gestión Centralizada
- ✅ Panel de Servicios de Windows (`services.msc`)
- ✅ Scripts batch fáciles de usar
- ✅ Comandos PowerShell avanzados

### Logs del Sistema
- ✅ Eventos registrados en Windows Event Log
- ✅ Fácil depuración de problemas
- ✅ Historial de errores y reinicios

---

## 📖 Guías de Uso

### Instalación Inicial

1. **Preparar el sistema**:
   ```cmd
   # Verificar Python
   python --version
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Verificar Cloudflared
   where cloudflared
   ```

2. **Instalar servicios**:
   ```cmd
   # Ejecutar como Administrador
   INSTALAR_SERVICIOS.bat
   ```

3. **Verificar instalación**:
   ```cmd
   VER_ESTADO_SERVICIOS.bat
   ```

### Uso Diario

#### Ver Estado
```cmd
VER_ESTADO_SERVICIOS.bat
```

#### Gestionar Servicios (Menú Interactivo)
```cmd
GESTIONAR_SERVICIOS.bat
```

**Opciones del menú**:
1. Ver estado de servicios
2. Iniciar todos los servicios
3. Detener todos los servicios
4. Reiniciar todos los servicios
5. Ver logs recientes
6. Gestionar servicio individual
0. Salir

#### Comandos Rápidos

```powershell
# Iniciar todos
Get-Service -Name "DVDcoin-*" | Start-Service

# Detener todos
Get-Service -Name "DVDcoin-*" | Stop-Service -Force

# Reiniciar todos
Get-Service -Name "DVDcoin-*" | Restart-Service

# Ver estado
Get-Service -Name "DVDcoin-*" | Format-Table Name, Status, StartType

# Ver logs
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 10
```

---

## 🆚 Comparación: Servicios vs Auto-Arranque

### Servicios Windows (Actual)

| Característica | Servicios Windows |
|----------------|-------------------|
| Auto-inicio | ✅ Con Windows (sin sesión) |
| Auto-reinicio | ✅ Automático si falla |
| Prioridad | ✅ Alta (sistema) |
| Logs | ✅ Event Log centralizado |
| Gestión | ✅ Panel de servicios |
| Robustez | ✅ Máxima |
| Visibilidad | ❌ Sin consola visible |
| Depuración | ⚠️ Requiere Event Log |

### Auto-Arranque (Task Scheduler)

| Característica | Auto-Arranque |
|----------------|---------------|
| Auto-inicio | ✅ Después de login |
| Auto-reinicio | ❌ No automático |
| Prioridad | ⚠️ Normal (usuario) |
| Logs | ⚠️ Archivos separados |
| Gestión | ⚠️ Task Scheduler |
| Robustez | ⚠️ Media |
| Visibilidad | ✅ Consola visible |
| Depuración | ✅ Fácil (consola) |

### Recomendación

- **Producción**: Usar **Servicios Windows** (más robusto)
- **Desarrollo**: Usar **Auto-Arranque** o manual (más visible)
- **Ambos**: Puedes tener ambos configurados (servicios tienen prioridad)

---

## 🔍 Verificación del Sistema

### Script de Verificación Completa

```cmd
# Ejecutar verificación
TEST_COMPLETO_SISTEMA.bat
```

### Verificación Manual

```powershell
# 1. Servicios instalados
Get-Service -Name "DVDcoin-*"

# 2. Servicios corriendo
Get-Service -Name "DVDcoin-*" | Where-Object {$_.Status -eq 'Running'}

# 3. Puertos escuchando
netstat -ano | findstr ":8000 :8001"

# 4. Probar endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health

# 5. Ver logs recientes
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 10

# 6. Verificar auto-inicio
Get-Service -Name "DVDcoin-*" | Select-Object Name, StartType
```

### Checklist de Verificación

- [ ] Servicios instalados: `Get-Service -Name "DVDcoin-*"`
- [ ] Servicios corriendo: Todos en estado "Running"
- [ ] Puerto 8000 escuchando: Bank
- [ ] Puerto 8001 escuchando: Exams
- [ ] Health check Bank: `curl http://localhost:8000/health`
- [ ] Health check Exams: `curl http://localhost:8001/health`
- [ ] Cloudflare Tunnel activo
- [ ] Auto-inicio configurado: StartType = "Automatic"
- [ ] Sin errores en Event Log

---

## 🛠️ Solución de Problemas

### Problema 1: Servicio no se inicia

```powershell
# Ver por qué falló
Get-EventLog -LogName Application -Source "DVDcoin-Bank" -Newest 5

# Verificar puerto libre
netstat -ano | findstr :8000

# Reiniciar servicio
Restart-Service -Name "DVDcoin-Bank"
```

### Problema 2: Puerto ocupado

```cmd
# Ver qué proceso usa el puerto
netstat -ano | findstr :8001

# Matar proceso (reemplaza PID)
taskkill /F /PID 1234

# Reiniciar servicio
net start "DVDcoin-Exams"
```

### Problema 3: Servicio se detiene solo

```powershell
# Ver errores
Get-EventLog -LogName Application -Source "DVDcoin-*" -EntryType Error -Newest 10

# Verificar dependencias
cd C:\dvdcoin
python -c "import fastapi, uvicorn, bcrypt, jose"

# Reinstalar servicio
.\DESINSTALAR_SERVICIOS.bat
.\INSTALAR_SERVICIOS.bat
```

### Problema 4: Cloudflare Tunnel no conecta

```cmd
# Verificar cloudflared
where cloudflared

# Ver configuración
type cloudflare-dvta-config.yml

# Ver logs
powershell -Command "Get-EventLog -LogName Application -Source 'DVDcoin-Tunnel' -Newest 5"

# Reiniciar túnel
net stop "DVDcoin-Tunnel"
net start "DVDcoin-Tunnel"
```

---

## 📊 Monitoreo

### Monitoreo en Tiempo Real

```cmd
# Ejecutar monitor
MONITOR_SISTEMA.bat
```

### Comandos de Monitoreo

```powershell
# Estado de servicios (actualizar cada 5s)
while ($true) {
    Clear-Host
    Get-Service -Name "DVDcoin-*" | Format-Table Name, Status, StartType
    Start-Sleep -Seconds 5
}

# Logs en tiempo real
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 1 -After (Get-Date).AddMinutes(-1)

# Uso de puertos
netstat -ano | findstr ":8000 :8001"
```

---

## 🔄 Mantenimiento

### Actualizar Sistema

```cmd
# 1. Detener servicios
GESTIONAR_SERVICIOS.bat
# Opción 3: Detener todos

# 2. Actualizar código
git pull

# 3. Actualizar dependencias
pip install -r requirements.txt --upgrade

# 4. Reiniciar servicios
GESTIONAR_SERVICIOS.bat
# Opción 2: Iniciar todos
```

### Backup de Configuración

```cmd
# Backup automático
BACKUP_COMPLETO.bat

# Backup manual
xcopy C:\dvdcoin\services\*.py C:\dvdcoin\backup\services\ /Y
xcopy C:\dvdcoin\cloudflare-dvta-config.yml C:\dvdcoin\backup\ /Y
```

### Reinstalar Servicios

```cmd
# 1. Desinstalar
DESINSTALAR_SERVICIOS.bat

# 2. Limpiar wrappers
del C:\dvdcoin\services\*-wrapper.py

# 3. Reinstalar
INSTALAR_SERVICIOS.bat
```

---

## 📝 Logs y Diagnóstico

### Ver Logs de Servicios

```powershell
# Todos los logs
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20

# Solo errores
Get-EventLog -LogName Application -Source "DVDcoin-*" -EntryType Error -Newest 10

# Logs de un servicio específico
Get-EventLog -LogName Application -Source "DVDcoin-Bank" -Newest 10

# Logs en rango de tiempo
Get-EventLog -LogName Application -Source "DVDcoin-*" -After (Get-Date).AddHours(-1)
```

### Diagnóstico Completo

```cmd
# Ejecutar diagnóstico
DIAGNOSTICO_COMPLETO.bat
```

---

## 🎯 Comandos Útiles

### Gestión Básica

```cmd
# Ver estado
VER_ESTADO_SERVICIOS.bat

# Gestionar (menú)
GESTIONAR_SERVICIOS.bat

# Instalar
INSTALAR_SERVICIOS.bat

# Desinstalar
DESINSTALAR_SERVICIOS.bat
```

### PowerShell Avanzado

```powershell
# Iniciar todos
Get-Service -Name "DVDcoin-*" | Start-Service

# Detener todos
Get-Service -Name "DVDcoin-*" | Stop-Service -Force

# Reiniciar todos
Get-Service -Name "DVDcoin-*" | Restart-Service

# Ver estado detallado
Get-Service -Name "DVDcoin-*" | Select-Object Name, DisplayName, Status, StartType | Format-Table

# Cambiar tipo de inicio
Set-Service -Name "DVDcoin-Bank" -StartupType Automatic

# Ver dependencias
Get-Service -Name "DVDcoin-Bank" -DependentServices
```

### CMD Rápido

```cmd
REM Iniciar servicio
net start "DVDcoin-Bank"

REM Detener servicio
net stop "DVDcoin-Bank"

REM Ver estado
sc query "DVDcoin-Bank"

REM Ver configuración
sc qc "DVDcoin-Bank"
```

---

## 🚀 Próximos Pasos

### Servicios Futuros (Preparados)

Cuando implementes más módulos, puedes crear servicios adicionales:

1. **DVDcoin-Games** (Puerto 8002)
   - Módulo de juegos
   - `modules/games/start_games.py`

2. **DVDcoin-Social** (Puerto 8003)
   - Módulo social
   - `modules/social/start_social.py`

3. **DVDcoin-API** (Puerto 8004)
   - API unificada
   - `modules/api/start_api.py`

### Agregar Nuevo Servicio

```powershell
# Editar install_services.ps1
# Agregar nuevo servicio al array $services

$services = @(
    # ... servicios existentes ...
    @{
        Name = "DVDcoin-Games"
        DisplayName = "DVDcoin Games Server"
        Description = "Servidor de juegos DVDcoin (Puerto 8002)"
        WorkingDir = "$baseDir\modules\games"
        Script = "start_games.py"
        Port = 8002
    }
)

# Reinstalar servicios
.\INSTALAR_SERVICIOS.bat
```

---

## 📞 Soporte

### Recursos

- 📖 **Guía Completa**: `GUIA_SERVICIOS_WINDOWS.md`
- 🔧 **Scripts**: Carpeta `services/`
- 📊 **Verificación**: `TEST_COMPLETO_SISTEMA.bat`
- 🔍 **Diagnóstico**: `DIAGNOSTICO_COMPLETO.bat`

### Comandos de Ayuda

```cmd
# Ver estado
VER_ESTADO_SERVICIOS.bat

# Ver logs
powershell -Command "Get-EventLog -LogName Application -Source 'DVDcoin-*' -Newest 10"

# Verificar puertos
netstat -ano | findstr ":8000 :8001"

# Probar conexiones
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## ✅ Resumen

### Sistema Completo Implementado

- ✅ **3 Servicios Windows** creados (Bank, Exams, Tunnel)
- ✅ **Auto-inicio** configurado
- ✅ **Auto-reinicio** en caso de fallo
- ✅ **Scripts de gestión** fáciles de usar
- ✅ **Logs centralizados** en Event Log
- ✅ **Documentación completa**

### Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `INSTALAR_SERVICIOS.bat` | Instalar todos los servicios |
| `VER_ESTADO_SERVICIOS.bat` | Ver estado actual |
| `GESTIONAR_SERVICIOS.bat` | Menú de gestión |
| `DESINSTALAR_SERVICIOS.bat` | Eliminar servicios |
| `GUIA_SERVICIOS_WINDOWS.md` | Guía completa |

### Para Empezar

```cmd
# 1. Instalar (como Administrador)
INSTALAR_SERVICIOS.bat

# 2. Verificar
VER_ESTADO_SERVICIOS.bat

# 3. Gestionar
GESTIONAR_SERVICIOS.bat
```

---

**¡Sistema de Servicios Windows completamente implementado y listo para usar!** 🎉
