@echo off
REM ============================================================================
REM DESINSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
REM ============================================================================
REM Este script elimina todos los servicios Windows de DVDcoin
REM ============================================================================

echo.
echo ============================================================================
echo   DESINSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
echo ============================================================================
echo.
echo Este script eliminara todos los servicios Windows de DVDcoin
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

REM Ejecutar script de desinstalacion
echo.
echo Ejecutando desinstalador...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0services\uninstall_services.ps1"

echo.
pause
