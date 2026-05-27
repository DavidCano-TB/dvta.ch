@echo off
REM ============================================================
REM DESACTIVAR INICIO AUTOMATICO EN WINDOWS
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:admin

echo ============================================================
echo DESACTIVANDO INICIO AUTOMATICO
echo ============================================================
echo.

REM Eliminar del registro
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoinBank" /f >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] Eliminado del registro de Windows
) else (
    echo [INFO] No estaba en el registro
)

REM Eliminar tarea programada
schtasks /delete /tn "DVDcoin Bank Startup" /f >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] Tarea programada eliminada
) else (
    echo [INFO] No habia tarea programada
)

echo.
echo ============================================================
echo REACTIVANDO WINDOWS DEFENDER
echo ============================================================
echo.

REM Reactivar protección en tiempo real
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false" 2>nul
echo [OK] Proteccion en tiempo real reactivada

REM Reactivar protección en la nube
powershell -Command "Set-MpPreference -MAPSReporting 2" 2>nul
echo [OK] Proteccion en la nube reactivada

REM Reactivar envío automático de muestras
powershell -Command "Set-MpPreference -SubmitSamplesConsent 1" 2>nul
echo [OK] Envio de muestras reactivado

echo.
echo ============================================================
echo COMPLETADO
echo ============================================================
echo.
echo El inicio automatico ha sido desactivado.
echo Windows Defender ha sido reactivado.
echo.
pause
