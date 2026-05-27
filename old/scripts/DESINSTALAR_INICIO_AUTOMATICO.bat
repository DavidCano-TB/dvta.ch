@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🗑️  DESINSTALANDO INICIO AUTOMÁTICO
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Este script requiere permisos de administrador.
    echo.
    echo Por favor:
    echo   1. Haz clic derecho en este archivo
    echo   2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo Eliminando tareas programadas...
schtasks /Delete /TN "DVDBank_AutoStart" /F 2>nul
schtasks /Delete /TN "DVDBank_dvta" /F 2>nul
schtasks /Delete /TN "DVDcoin-Autostart" /F 2>nul
schtasks /Delete /TN "DVDcoin" /F 2>nul
schtasks /Delete /TN "DVDcoin-Cloudflare" /F 2>nul
echo    ✅ Tareas programadas eliminadas
echo.

echo Eliminando entradas del registro...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank_dvta" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f 2>nul
echo    ✅ Entradas de registro eliminadas
echo.

echo Eliminando accesos directos...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del "%STARTUP_FOLDER%\DVDBank.lnk" 2>nul
del "%STARTUP_FOLDER%\DVDBank_dvta.lnk" 2>nul
del "%STARTUP_FOLDER%\DVDcoin.lnk" 2>nul
echo    ✅ Accesos directos eliminados
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ DESINSTALACIÓN COMPLETA
echo ═══════════════════════════════════════════════════════════
echo.
echo El sistema ya NO se iniciará automáticamente con Windows.
echo.
echo Para volver a instalar el inicio automático:
echo   INSTALAR_INICIO_AUTOMATICO.bat
echo.
pause
