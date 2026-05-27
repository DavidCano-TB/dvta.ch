@echo off
chcp 65001 >nul

title DVDcoin - Detener Watchdog

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   DVDcoin - Detener Watchdog Monitor
echo ═══════════════════════════════════════════════════════════════════
echo.

echo 🛑 Deteniendo watchdog...

:: Buscar y detener procesos de watchdog
tasklist /fi "IMAGENAME eq python.exe" /fo list 2>nul | findstr /i "PID" > temp_stop_watchdog_scripts.txt
for /f "tokens=2" %%a in (temp_stop_watchdog_scripts.txt) do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "watchdog_monitor.py" >nul
    if !errorLevel! equ 0 (
        echo Deteniendo proceso %%a...
        taskkill /f /pid %%a >nul 2>&1
    )
)
del temp_stop_watchdog_scripts.txt 2>nul

timeout /t 2 >nul

echo.
echo ✅ Watchdog detenido
echo.
echo Nota: El watchdog se volverá a iniciar automáticamente
echo       en el próximo reinicio del sistema.
echo.
echo Para desinstalarlo permanentemente, ejecuta:
echo    DESINSTALAR_WATCHDOG.bat
echo.
pause
