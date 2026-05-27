@echo off
REM ============================================================================
REM ESTADO DE SERVICIOS WINDOWS - DVDcoin Platform
REM ============================================================================
REM Muestra el estado actual de todos los servicios DVDcoin
REM ============================================================================

echo.
echo ============================================================================
echo   ESTADO DE SERVICIOS WINDOWS - DVDcoin Platform
echo ============================================================================
echo.

REM Verificar si PowerShell esta disponible
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell no esta disponible
    pause
    exit /b 1
)

REM Mostrar estado de servicios
powershell -ExecutionPolicy Bypass -Command "Get-Service -Name 'DVDcoin-*' -ErrorAction SilentlyContinue | Format-Table Name, DisplayName, Status, StartType -AutoSize"

if %errorlevel% neq 0 (
    echo.
    echo No se encontraron servicios DVDcoin instalados
    echo.
    echo Para instalar los servicios, ejecuta: INSTALAR_SERVICIOS.bat
    echo.
)

echo.
pause
