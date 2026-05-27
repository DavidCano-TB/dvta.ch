@echo off
REM ============================================================================
REM INSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
REM ============================================================================
REM Este script instala servicios Windows para Bank, Exams y Cloudflare Tunnel
REM Los servicios se inician automaticamente con Windows
REM ============================================================================

echo.
echo ============================================================================
echo   INSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
echo ============================================================================
echo.
echo Este script instalara servicios Windows para:
echo   - DVDcoin Bank (Puerto 8000)
echo   - DVDcoin Exams (Puerto 8001)
echo   - Cloudflare Tunnel (dvta.ch)
echo.
echo Los servicios se iniciaran automaticamente con Windows y se reiniciaran
echo automaticamente si fallan.
echo.
echo IMPORTANTE: Este script requiere privilegios de administrador
echo.
pause

REM Verificar si PowerShell esta disponible
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell no esta disponible
    pause
    exit /b 1
)

REM Ejecutar script de instalacion de servicios
echo.
echo Ejecutando instalador de servicios...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0services\install_services.ps1"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================================
    echo   INSTALACION COMPLETADA
    echo ============================================================================
    echo.
    echo Los servicios han sido instalados y se iniciaran automaticamente con Windows
    echo.
    echo Para gestionar los servicios, ejecuta: GESTIONAR_SERVICIOS.bat
    echo.
) else (
    echo.
    echo ============================================================================
    echo   ERROR EN LA INSTALACION
    echo ============================================================================
    echo.
    echo Verifica que ejecutaste este script como administrador
    echo Haz clic derecho y selecciona "Ejecutar como administrador"
    echo.
)

pause
