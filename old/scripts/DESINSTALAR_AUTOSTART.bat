@echo off
:: Desinstala el inicio automatico de DVDcoin Bank
:: EJECUTAR COMO ADMINISTRADOR

title DVDcoin — Desinstalar Autostart
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Ejecuta este archivo como Administrador.
    echo  Clic derecho ^> "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN - DESINSTALAR INICIO AUTOMATICO              ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Eliminando tareas de inicio automatico...
echo.

schtasks /delete /tn "DVDcoin-Cloudflare" /f >nul 2>&1
if errorlevel 1 (
    echo   ○ DVDcoin-Cloudflare no estaba instalado
) else (
    echo   ✓ DVDcoin-Cloudflare eliminado
)

schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
if not errorlevel 1 (
    echo   ✓ DVDcoin-Autostart eliminado
)

schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
if not errorlevel 1 (
    echo   ✓ DVDcoin-ngrok eliminado
)

schtasks /delete /tn "DVDcoin" /f >nul 2>&1
if not errorlevel 1 (
    echo   ✓ DVDcoin eliminado
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ✓ Autostart desinstalado correctamente
echo.
echo DVDcoin ya NO se iniciará automáticamente al encender Windows.
echo.
echo Para volver a instalarlo:
echo   INSTALAR_AUTOSTART.bat
echo.
pause
