@echo off
REM ============================================================
REM PREPARAR SISTEMA PARA INSTALACION AL REINICIAR
REM EJECUTAR COMO ADMINISTRADOR
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo  ERROR: Ejecuta este archivo como Administrador.
    echo  Clic derecho ^> "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

chcp 65001 >nul
title DVDCoin - Preparar para Reinicio
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         PREPARAR SISTEMA PARA INSTALACION AL REINICIAR       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/3] Eliminando marca de instalación previa...
if exist ".cloudflare_instalado" (
    del ".cloudflare_instalado" >nul 2>&1
    echo       ✓ Marca eliminada
) else (
    echo       ○ No había marca previa
)

echo.
echo [2/3] Eliminando tareas antiguas...
schtasks /delete /tn "DVDcoin-Instalador" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
schtasks /delete /tn "DVDcoin" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Cloudflare" /f >nul 2>&1
echo       ✓ Tareas antiguas eliminadas

echo.
echo [3/3] Creando tarea de instalación...

REM Usar PowerShell para crear la tarea con más control
powershell -ExecutionPolicy Bypass -Command ^
"$action = New-ScheduledTaskAction -Execute 'c:\dvdcoin\INSTALACION_AUTOMATICA_CLOUDFLARE.bat'; ^
$trigger = New-ScheduledTaskTrigger -AtLogOn; ^
$trigger.Delay = 'PT5S'; ^
$principal = New-ScheduledTaskPrincipal -UserId '%USERDOMAIN%\%USERNAME%' -LogonType Interactive -RunLevel Highest; ^
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; ^
Register-ScheduledTask -TaskName 'DVDcoin-Instalador' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null; ^
Write-Host '      ✓ Tarea creada correctamente' -ForegroundColor Green"

if errorlevel 1 (
    echo       ✗ Error al crear tarea
    echo.
    echo       Intenta manualmente:
    echo       1. Abre "Programador de tareas" (taskschd.msc)
    echo       2. Crea una tarea básica
    echo       3. Nombre: DVDcoin-Instalador
    echo       4. Desencadenador: Al iniciar sesión
    echo       5. Acción: Iniciar programa
    echo       6. Programa: c:\dvdcoin\INSTALACION_AUTOMATICA_CLOUDFLARE.bat
    echo       7. Propiedades: Ejecutar con privilegios más altos
    echo.
    pause
    exit /b 1
)

echo.
echo [Verificación] Comprobando tarea...
schtasks /query /tn "DVDcoin-Instalador" >nul 2>&1
if errorlevel 1 (
    echo       ✗ La tarea no se pudo verificar
    pause
    exit /b 1
) else (
    echo       ✓ Tarea verificada correctamente
)

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ SISTEMA PREPARADO PARA REINICIO               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ QUE PASARA AL REINICIAR                                      │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   1. Windows se iniciará normalmente
echo   2. 5 segundos después del login
echo   3. Se abrirá automáticamente una ventana CMD
echo   4. El instalador te guiará paso a paso:
echo.
echo      PASO 1: Verificar Python
echo      PASO 2: Instalar cloudflared
echo      PASO 3: Autenticar con Cloudflare
echo      PASO 4: Crear túnel
echo      PASO 5: Configurar dominio
echo      PASO 6: Crear archivo de configuración
echo      PASO 7: Instalar autostart
echo.
echo   5. Al finalizar, DVDcoin estará listo para usar
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ IMPORTANTE                                                    │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   • Guarda todo tu trabajo antes de reiniciar
echo   • Cierra todas las aplicaciones
echo   • Ten a mano tu cuenta de Cloudflare (o créala gratis)
echo   • El proceso tomará unos 5-10 minutos
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ¿Quieres reiniciar Windows AHORA? (S/N)
set /p RESTART_NOW="> "

if /i "%RESTART_NOW%"=="S" (
    echo.
    echo Guardando configuración...
    timeout /t 2 /nobreak >nul
    
    echo Reiniciando en 10 segundos...
    echo Presiona Ctrl+C para cancelar
    timeout /t 10
    
    shutdown /r /t 0
) else (
    echo.
    echo ══════════════════════════════════════════════════════════════
    echo.
    echo Sistema preparado. Reinicia Windows cuando estés listo.
    echo.
    echo La instalación se ejecutará automáticamente al iniciar sesión.
    echo.
    echo Para cancelar la instalación automática:
    echo   CANCELAR_INSTALACION_AL_REINICIO.bat
    echo.
    pause
)

exit /b 0
