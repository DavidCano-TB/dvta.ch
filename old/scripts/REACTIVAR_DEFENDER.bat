@echo off
REM ============================================================
REM REACTIVAR WINDOWS DEFENDER
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
echo REACTIVANDO WINDOWS DEFENDER
echo ============================================================
echo.

REM Eliminar claves de registro
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v "DisableAntiSpyware" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v "DisableAntiVirus" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Reporting" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\SpyNet" /f >nul 2>&1

echo [OK] Registro limpiado

REM Habilitar servicios
sc config WinDefend start=auto >nul 2>&1
sc config WdNisSvc start=auto >nul 2>&1
sc config SecurityHealthService start=auto >nul 2>&1

echo [OK] Servicios habilitados

REM Iniciar servicios
sc start WinDefend >nul 2>&1
sc start WdNisSvc >nul 2>&1
sc start SecurityHealthService >nul 2>&1

echo [OK] Servicios iniciados

REM Reactivar protecciones
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false" 2>nul
powershell -Command "Set-MpPreference -MAPSReporting 2" 2>nul
powershell -Command "Set-MpPreference -SubmitSamplesConsent 1" 2>nul

echo [OK] Protecciones reactivadas

echo.
echo ============================================================
echo WINDOWS DEFENDER REACTIVADO
echo ============================================================
echo.
echo Se recomienda reiniciar Windows para aplicar todos los cambios
echo.
pause
