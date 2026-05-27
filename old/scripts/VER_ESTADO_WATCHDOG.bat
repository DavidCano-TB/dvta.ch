@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title DVDcoin - Estado del Watchdog

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   DVDcoin - Estado del Watchdog Monitor
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Verificar si la tarea programada existe
echo 📋 Verificando tarea programada...
schtasks /query /tn "DVDcoin_Watchdog" >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Tarea programada: INSTALADA
    echo.
    schtasks /query /tn "DVDcoin_Watchdog" /fo list /v | findstr /i "Estado: Nombre: Ejecutar Última"
) else (
    echo ❌ Tarea programada: NO INSTALADA
    echo.
    echo Para instalar, ejecuta: INSTALAR_WATCHDOG.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Verificar si el proceso está corriendo
echo 🔍 Verificando proceso...
set "WATCHDOG_RUNNING=0"

tasklist /fi "IMAGENAME eq python.exe" /fo list 2>nul | findstr /i "PID" > temp_watchdog_pids.txt
for /f "tokens=2" %%a in (temp_watchdog_pids.txt) do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "watchdog_monitor.py" >nul
    if !errorLevel! equ 0 (
        set "WATCHDOG_RUNNING=1"
        echo ✅ Proceso watchdog: CORRIENDO (PID: %%a)
    )
)
del temp_watchdog_pids.txt 2>nul

if !WATCHDOG_RUNNING! equ 0 (
    echo ❌ Proceso watchdog: NO ESTÁ CORRIENDO
    echo.
    echo Para iniciarlo, ejecuta: INICIAR_WATCHDOG.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Mostrar últimas líneas del log
if exist "logs\watchdog.log" (
    echo 📝 Últimas 15 líneas del log:
    echo.
    powershell -Command "Get-Content 'logs\watchdog.log' -Tail 15 -Encoding UTF8"
) else (
    echo ℹ️  No se encontró el archivo de log
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Para ver el log completo: notepad logs\watchdog.log
echo.
pause
