# 🔧 Guía de Servicios Windows - DVDcoin Platform

## 📋 Índice
1. [¿Qué son los Servicios Windows?](#qué-son-los-servicios-windows)
2. [Servicios Disponibles](#servicios-disponibles)
3. [Instalación](#instalación)
4. [Gestión de Servicios](#gestión-de-servicios)
5. [Ventajas vs Auto-Arranque](#ventajas-vs-auto-arranque)
6. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 ¿Qué son los Servicios Windows?

Los **Servicios Windows** son aplicaciones que se ejecutan en segundo plano sin necesidad de que un usuario inicie sesión. Son la forma más profesional y robusta de ejecutar aplicaciones en Windows.

### Características principales:
- ✅ **Auto-inicio**: Se inician automáticamente con Windows
- ✅ **Auto-reinicio**: Se reinician automáticamente si fallan
- ✅ **Sin sesión**: Funcionan sin necesidad de iniciar sesión
- ✅ **Gestión centralizada**: Se gestionan desde el Panel de Servicios de Windows
- ✅ **Logs del sistema**: Registran eventos en el Visor de Eventos de Windows
- ✅ **Prioridad alta**: Tienen prioridad sobre aplicaciones normales

---

## 🚀 Servicios Disponibles

### 1. **DVDcoin-Bank** (Puerto 8000)
- **Descripción**: Servidor principal del sistema bancario DVDcoin
- **URL Local**: http://localhost:8000
- **URL Externa**: https://bank.dvta.ch
- **Script**: `main.py`
- **Directorio**: `C:\dvdcoin\`

### 2. **DVDcoin-Exams** (Puerto 8001)
- **Descripción**: Servidor de exámenes y oposiciones
- **URL Local**: http://localhost:8001
- **URL Externa**: https://dvta.ch
- **Script**: `modules/exams/start_exams.py`
- **Directorio**: `C:\dvdcoin\modules\exams\`

### 3. **DVDcoin-Tunnel**
- **Descripción**: Túnel Cloudflare para acceso externo
- **Función**: Conecta los servidores locales con dvta.ch
- **Configuración**: `cloudflare-dvta-config.yml`
- **Directorio**: `C:\dvdcoin\`

---

## 📦 Instalación

### Método 1: Instalación Rápida (Recomendado)

1. **Ejecutar como Administrador**:
   ```
   Haz clic derecho en: INSTALAR_SERVICIOS.bat
   Selecciona: "Ejecutar como administrador"
   ```

2. **Esperar a que termine**:
   - El script instalará las dependencias necesarias (pywin32)
   - Creará los wrappers de servicios
   - Instalará los 3 servicios
   - Los iniciará automáticamente

3. **Verificar instalación**:
   ```
   Ejecuta: VER_ESTADO_SERVICIOS.bat
   ```

### Método 2: Instalación Manual (PowerShell)

```powershell
# Abrir PowerShell como Administrador
cd C:\dvdcoin\services
.\install_services.ps1
```

### Requisitos previos:
- ✅ Python instalado
- ✅ Dependencias de DVDcoin instaladas (`pip install -r requirements.txt`)
- ✅ Cloudflared instalado (para el túnel)
- ✅ Privilegios de administrador

---

## 🎮 Gestión de Servicios

### Opción 1: Menú Interactivo (Más Fácil)

```
Ejecuta: GESTIONAR_SERVICIOS.bat
```

**Opciones disponibles**:
1. Ver estado de servicios
2. Iniciar todos los servicios
3. Detener todos los servicios
4. Reiniciar todos los servicios
5. Ver logs recientes
6. Gestionar servicio individual
0. Salir

### Opción 2: Panel de Servicios de Windows

1. Presiona `Win + R`
2. Escribe: `services.msc`
3. Busca servicios que empiecen con "DVDcoin-"
4. Haz clic derecho para gestionar

### Opción 3: Comandos PowerShell

```powershell
# Ver estado de todos los servicios
Get-Service -Name "DVDcoin-*"

# Iniciar un servicio
Start-Service -Name "DVDcoin-Bank"

# Detener un servicio
Stop-Service -Name "DVDcoin-Exams"

# Reiniciar un servicio
Restart-Service -Name "DVDcoin-Tunnel"

# Ver logs
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 10
```

### Opción 4: Comandos CMD

```cmd
REM Ver estado
sc query "DVDcoin-Bank"

REM Iniciar servicio
net start "DVDcoin-Bank"

REM Detener servicio
net stop "DVDcoin-Bank"
```

---

## ⚖️ Ventajas vs Auto-Arranque

### Servicios Windows (Recomendado para Producción)

| Ventaja | Descripción |
|---------|-------------|
| ✅ **Auto-reinicio** | Se reinician automáticamente si fallan |
| ✅ **Sin sesión** | Funcionan sin iniciar sesión en Windows |
| ✅ **Prioridad alta** | Tienen prioridad sobre aplicaciones normales |
| ✅ **Logs centralizados** | Eventos registrados en el sistema |
| ✅ **Gestión profesional** | Panel de servicios de Windows |
| ✅ **Más robusto** | Mejor manejo de errores y recuperación |

### Auto-Arranque (Task Scheduler)

| Ventaja | Descripción |
|---------|-------------|
| ✅ **Más simple** | Fácil de configurar |
| ✅ **Visible** | Puedes ver las ventanas de consola |
| ✅ **Depuración** | Más fácil de depurar problemas |
| ❌ **Requiere sesión** | Solo funciona después de iniciar sesión |
| ❌ **Sin auto-reinicio** | No se reinician automáticamente |

### ¿Cuál usar?

- **Servicios Windows**: Para servidores de producción que deben estar siempre activos
- **Auto-Arranque**: Para desarrollo o si necesitas ver los logs en consola

**Puedes usar ambos**: Los servicios tienen prioridad, pero si los detienes, el auto-arranque puede tomar el control.

---

## 🔧 Solución de Problemas

### Problema 1: "El servicio no se inicia"

**Solución**:
```powershell
# Ver logs del servicio
Get-EventLog -LogName Application -Source "DVDcoin-Bank" -Newest 5

# Verificar que el puerto no esté ocupado
netstat -ano | findstr :8000

# Reiniciar el servicio
Restart-Service -Name "DVDcoin-Bank"
```

### Problema 2: "Error al instalar: pywin32 no encontrado"

**Solución**:
```cmd
python -m pip install pywin32
python -m pywin32_postinstall -install
```

### Problema 3: "Acceso denegado"

**Solución**:
- Asegúrate de ejecutar el script como **Administrador**
- Haz clic derecho → "Ejecutar como administrador"

### Problema 4: "El servicio se detiene solo"

**Solución**:
```powershell
# Ver por qué se detuvo
Get-EventLog -LogName Application -Source "DVDcoin-*" -EntryType Error -Newest 10

# Verificar dependencias
cd C:\dvdcoin
python -c "import fastapi, uvicorn, bcrypt, jose"

# Reinstalar el servicio
.\DESINSTALAR_SERVICIOS.bat
.\INSTALAR_SERVICIOS.bat
```

### Problema 5: "Puerto ya en uso"

**Solución**:
```cmd
REM Ver qué proceso usa el puerto
netstat -ano | findstr :8001

REM Matar el proceso (reemplaza PID con el número que viste)
taskkill /F /PID 1234

REM Reiniciar el servicio
net start "DVDcoin-Exams"
```

### Problema 6: "Cloudflare Tunnel no conecta"

**Solución**:
```cmd
REM Verificar que cloudflared esté instalado
where cloudflared

REM Verificar configuración
type cloudflare-dvta-config.yml

REM Ver logs del servicio
powershell -Command "Get-EventLog -LogName Application -Source 'DVDcoin-Tunnel' -Newest 5"

REM Reiniciar el túnel
net stop "DVDcoin-Tunnel"
net start "DVDcoin-Tunnel"
```

---

## 📊 Verificación del Sistema

### Script de Verificación Completa

```cmd
REM Ejecutar verificación completa
VER_ESTADO_SERVICIOS.bat
```

### Verificación Manual

```powershell
# 1. Ver servicios
Get-Service -Name "DVDcoin-*" | Format-Table Name, Status, StartType

# 2. Verificar puertos
netstat -ano | findstr ":8000 :8001"

# 3. Probar conexiones
curl http://localhost:8000/health
curl http://localhost:8001/health

# 4. Ver logs recientes
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 10
```

---

## 🔄 Desinstalación

### Método 1: Script Automático

```
Ejecuta como Administrador: DESINSTALAR_SERVICIOS.bat
```

### Método 2: Manual

```powershell
# Detener servicios
Stop-Service -Name "DVDcoin-*" -Force

# Desinstalar cada servicio
cd C:\dvdcoin\services
python DVDcoin-Bank-wrapper.py remove
python DVDcoin-Exams-wrapper.py remove
python DVDcoin-Tunnel-wrapper.py remove
```

---

## 📝 Comandos Útiles

### Ver Estado
```cmd
VER_ESTADO_SERVICIOS.bat
```

### Gestionar Servicios
```cmd
GESTIONAR_SERVICIOS.bat
```

### Iniciar Todos
```powershell
Get-Service -Name "DVDcoin-*" | Start-Service
```

### Detener Todos
```powershell
Get-Service -Name "DVDcoin-*" | Stop-Service -Force
```

### Reiniciar Todos
```powershell
Get-Service -Name "DVDcoin-*" | Restart-Service
```

### Ver Logs
```powershell
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20 | Format-Table TimeGenerated, Source, Message -AutoSize
```

---

## 🎯 Resumen

### Para Instalar:
1. Ejecuta como Admin: `INSTALAR_SERVICIOS.bat`
2. Espera a que termine
3. Verifica: `VER_ESTADO_SERVICIOS.bat`

### Para Gestionar:
- Ejecuta: `GESTIONAR_SERVICIOS.bat`
- O usa: `services.msc` (Panel de Windows)

### Para Desinstalar:
- Ejecuta como Admin: `DESINSTALAR_SERVICIOS.bat`

---

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `VER_ESTADO_SERVICIOS.bat`
2. Revisa los logs: `Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 10`
3. Verifica puertos: `netstat -ano | findstr ":8000 :8001"`
4. Consulta esta guía en la sección "Solución de Problemas"

---

**¡Los servicios Windows son la forma más profesional y robusta de ejecutar DVDcoin Platform!** 🚀
