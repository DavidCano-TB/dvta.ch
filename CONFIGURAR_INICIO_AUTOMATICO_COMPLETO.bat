@echo off
chcp 65001 >nul

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cls
echo ═══════════════════════════════════════════════════════════
echo   CONFIGURAR INICIO AUTOMÁTICO CON WINDOWS
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará DVDBank para:
echo   1. Iniciarse automáticamente con Windows
echo   2. Abrir el navegador en https://dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Verificar que el script de inicio existe
if not exist "%~dp0INICIAR_DVDBANK_DVTA.bat" (
    echo ERROR: INICIAR_DVDBANK_DVTA.bat no encontrado
    echo.
    pause
    exit /b 1
)

REM Eliminar tarea anterior si existe
schtasks /query /tn "DVDBank_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo Eliminando tarea anterior...
    schtasks /delete /tn "DVDBank_AutoStart" /f >nul 2>&1
)

REM Crear tarea programada con delay de 30 segundos para dar tiempo al sistema
echo Creando tarea programada...
schtasks /create /tn "DVDBank_AutoStart" /tr "\"%~dp0INICIAR_DVDBANK_DVTA.bat\"" /sc onlogon /delay 0000:30 /rl highest /f >nul 2>&1

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   ✅ CONFIGURACIÓN COMPLETADA
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo DVDBank se iniciará automáticamente 30 segundos después
    echo de iniciar Windows y abrirá el navegador en https://dvta.ch
    echo.
    echo Para desactivar, ejecuta: DESACTIVAR_INICIO_AUTOMATICO.bat
    echo.
    echo Para probar ahora, ejecuta: INICIAR_DVDBANK_DVTA.bat
    echo.
) else (
    echo.
    echo ❌ Error al crear la tarea programada
    echo.
    echo Intenta ejecutar este script como Administrador
    echo.
)

pause
