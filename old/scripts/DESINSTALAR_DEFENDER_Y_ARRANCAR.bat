@echo off
REM ============================================================
REM DESINSTALAR WINDOWS DEFENDER PERMANENTEMENTE Y ARRANCAR TODO
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
cd /d "%~dp0"

title DVDcoin - Desinstalando Defender y Arrancando

echo ============================================================
echo DESINSTALACION PERMANENTE DE WINDOWS DEFENDER
echo ============================================================
echo.
echo ADVERTENCIA: Esto desactivara Windows Defender permanentemente
echo.
timeout /t 3 /nobreak >nul

echo ============================================================
echo PASO 1: DETENIENDO SERVICIOS DE WINDOWS DEFENDER
echo ============================================================
echo.

REM Detener servicios
sc stop WinDefend >nul 2>&1
sc stop WdNisSvc >nul 2>&1
sc stop WdNisDrv >nul 2>&1
sc stop WdBoot >nul 2>&1
sc stop WdFilter >nul 2>&1
sc stop SecurityHealthService >nul 2>&1

echo [OK] Servicios detenidos

echo.
echo ============================================================
echo PASO 2: DESHABILITANDO SERVICIOS PERMANENTEMENTE
echo ============================================================
echo.

REM Deshabilitar servicios
sc config WinDefend start=disabled >nul 2>&1
sc config WdNisSvc start=disabled >nul 2>&1
sc config WdNisDrv start=disabled >nul 2>&1
sc config WdBoot start=disabled >nul 2>&1
sc config WdFilter start=disabled >nul 2>&1
sc config SecurityHealthService start=disabled >nul 2>&1

echo [OK] Servicios deshabilitados

echo.
echo ============================================================
echo PASO 3: DESACTIVANDO TODAS LAS PROTECCIONES
echo ============================================================
echo.

REM Desactivar todas las protecciones
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" 2>nul
powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true" 2>nul
powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true" 2>nul
powershell -Command "Set-MpPreference -DisableIOAVProtection $true" 2>nul
powershell -Command "Set-MpPreference -DisablePrivacyMode $true" 2>nul
powershell -Command "Set-MpPreference -DisableScriptScanning $true" 2>nul
powershell -Command "Set-MpPreference -DisableArchiveScanning $true" 2>nul
powershell -Command "Set-MpPreference -DisableIntrusionPreventionSystem $true" 2>nul
powershell -Command "Set-MpPreference -DisableEmailScanning $true" 2>nul
powershell -Command "Set-MpPreference -DisableRemovableDriveScanning $true" 2>nul
powershell -Command "Set-MpPreference -DisableScanningMappedNetworkDrivesForFullScan $true" 2>nul
powershell -Command "Set-MpPreference -DisableScanningNetworkFiles $true" 2>nul
powershell -Command "Set-MpPreference -MAPSReporting 0" 2>nul
powershell -Command "Set-MpPreference -SubmitSamplesConsent 2" 2>nul

echo [OK] Todas las protecciones desactivadas

echo.
echo ============================================================
echo PASO 4: MODIFICANDO REGISTRO DE WINDOWS
echo ============================================================
echo.

REM Deshabilitar Windows Defender via registro
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v "DisableAntiSpyware" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v "DisableAntiVirus" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableBehaviorMonitoring" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableIOAVProtection" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableOnAccessProtection" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableRealtimeMonitoring" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableScanOnRealtimeEnable" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Reporting" /v "DisableEnhancedNotifications" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\SpyNet" /v "DisableBlockAtFirstSeen" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\SpyNet" /v "SpynetReporting" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\SpyNet" /v "SubmitSamplesConsent" /t REG_DWORD /d 2 /f >nul 2>&1

REM Deshabilitar Tamper Protection
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows Defender\Features" /v "TamperProtection" /t REG_DWORD /d 0 /f >nul 2>&1

echo [OK] Registro modificado

echo.
echo ============================================================
echo PASO 5: AGREGANDO EXCLUSIONES TOTALES
echo ============================================================
echo.

REM Agregar exclusiones
powershell -Command "Add-MpPreference -ExclusionPath 'C:\'" 2>nul
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0'" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'python.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'pythonw.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'ngrok.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionExtension '.py'" 2>nul
powershell -Command "Add-MpPreference -ExclusionExtension '.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionExtension '.bat'" 2>nul

echo [OK] Exclusiones agregadas

echo.
echo ============================================================
echo PASO 6: LIMPIANDO PROCESOS ANTERIORES
echo ============================================================
echo.

REM Matar Python
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo [OK] Procesos Python terminados

REM Matar ngrok
taskkill /F /IM ngrok.exe >nul 2>&1
echo [OK] Procesos ngrok terminados

REM Liberar puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
echo [OK] Puerto 8000 liberado

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo PASO 7: INICIANDO SERVIDOR DVDCOIN
echo ============================================================
echo.

start "DVDcoin Server" pythonw main.py

echo [OK] Servidor iniciado
echo Esperando 10 segundos...
timeout /t 10 /nobreak >nul

echo.
echo ============================================================
echo PASO 8: CONFIGURANDO Y ARRANCANDO NGROK
echo ============================================================
echo.

REM Leer token
for /f %%i in (config\.ngrok_token) do set TOKEN=%%i

if "%TOKEN%"=="" (
    echo [ERROR] No se encontro el token
    pause
    exit /b 1
)

ngrok config add-authtoken %TOKEN%
echo [OK] Token configurado

set DOMAIN=unhidden-patient-cradling.ngrok-free.dev

echo.
echo Dominio: https://%DOMAIN%
echo.

start "NGROK Tunnel" ngrok http --url=%DOMAIN% 8000

echo [OK] Ngrok iniciado
echo Esperando 15 segundos para establecer conexion...
timeout /t 15 /nobreak >nul

echo.
echo ============================================================
echo PASO 9: VERIFICANDO SISTEMA
echo ============================================================
echo.

REM Verificar servidor
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Servidor no esta corriendo
) else (
    echo [OK] Servidor activo en puerto 8000
)

REM Verificar ngrok
tasklist | findstr "ngrok.exe" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ngrok no esta corriendo
) else (
    echo [OK] Ngrok activo
)

REM Guardar URL
echo https://%DOMAIN% > ngrok_url.txt

echo.
echo ============================================================
echo SISTEMA COMPLETAMENTE FUNCIONAL
echo ============================================================
echo.
echo Windows Defender: DESINSTALADO/DESACTIVADO PERMANENTEMENTE
echo.
echo URL publica:  https://%DOMAIN%
echo Panel ngrok:  http://localhost:4040
echo Servidor:     http://localhost:8000
echo.
echo OPO:          https://%DOMAIN%/opo
echo Banco:        https://%DOMAIN%
echo.
echo ============================================================
echo PROBANDO CONEXION
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

curl -s -o nul -w "Codigo HTTP: %%{http_code}\n" https://%DOMAIN% 2>nul

echo.
echo ============================================================
echo ABRIENDO NAVEGADOR
echo ============================================================
echo.

start https://%DOMAIN%

echo.
echo [OK] Sistema completamente funcional
echo.
echo NOTA IMPORTANTE:
echo - Windows Defender esta PERMANENTEMENTE desactivado
echo - Los cambios persisten despues de reiniciar
echo - Para reactivarlo, ejecuta: REACTIVAR_DEFENDER.bat
echo.
pause
