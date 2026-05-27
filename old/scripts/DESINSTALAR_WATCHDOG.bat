@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ═══════════════════════════════════════════════════════════════════
:: DVDcoin - Desinstalador de Watchdog Monitor
:: ═══════════════════════════════════════════════════════════════════

title DVDcoin - Desinstalar Watchdog Monitor

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   DVDcoin - Desinstalar Watchdog Monitor
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Este script requiere permisos de administrador.
    echo.
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ✅ Permisos de administrador verificados
echo.

:: Detener procesos del watchdog
echo 🛑 Deteniendo procesos del watchdog...
taskkill /f /fi "WINDOWTITLE eq watchdog_monitor.py*" >nul 2>&1
taskkill /f /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq *watchdog*" >nul 2>&1

:: Esperar un momento
timeout /t 2 >nul

:: Eliminar tarea programada
echo 📋 Eliminando tarea programada...
schtasks /query /tn "DVDcoin_Watchdog" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /delete /tn "DVDcoin_Watchdog" /f
    if %errorLevel% equ 0 (
        echo ✅ Tarea programada eliminada
    ) else (
        echo ❌ Error al eliminar la tarea programada
    )
) else (
    echo ℹ️  No se encontró la tarea programada
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   ✅ DESINSTALACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════
echo.
echo El watchdog ha sido desinstalado.
echo.
echo Nota: Los archivos watchdog_monitor.py e INICIAR_WATCHDOG.bat
echo      no se han eliminado. Puedes borrarlos manualmente si lo deseas.
echo.
echo Los logs se mantienen en: logs\watchdog.log
echo.
pause
