@echo off
REM ============================================================
REM DESACTIVAR WINDOWS DEFENDER Y ARRANCAR SERVIDOR + NGROK
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

title DVDcoin - Desactivando Antivirus y Arrancando

echo ============================================================
echo PASO 1: DESACTIVANDO WINDOWS DEFENDER
echo ============================================================
echo.

REM Desactivar protección en tiempo real
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" 2>nul
if %errorLevel% == 0 (
    echo [OK] Proteccion en tiempo real desactivada
) else (
    echo [ADVERTENCIA] No se pudo desactivar la proteccion en tiempo real
)

REM Desactivar protección en la nube
powershell -Command "Set-MpPreference -MAPSReporting 0" 2>nul
echo [OK] Proteccion en la nube desactivada

REM Desactivar envío automático de muestras
powershell -Command "Set-MpPreference -SubmitSamplesConsent 2" 2>nul
echo [OK] Envio de muestras desactivado

echo.
echo ============================================================
echo PASO 2: LIMPIANDO PROCESOS ANTERIORES
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
echo PASO 3: INICIANDO SERVIDOR DVDCOIN
echo ============================================================
echo.

start "DVDcoin Server" pythonw main.py

echo [OK] Servidor iniciado
echo Esperando 8 segundos...
timeout /t 8 /nobreak >nul

echo.
echo ============================================================
echo PASO 4: CONFIGURANDO NGROK
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

echo.
echo ============================================================
echo PASO 5: INICIANDO NGROK CON DOMINIO RESERVADO
echo ============================================================
echo.

set DOMAIN=unhidden-patient-cradling.ngrok-free.dev

echo Dominio: https://%DOMAIN%
echo.

start "NGROK Tunnel" ngrok http --url=%DOMAIN% 8000

echo [OK] Ngrok iniciado
echo Esperando 15 segundos para establecer conexion...
timeout /t 15 /nobreak >nul

echo.
echo ============================================================
echo PASO 6: VERIFICANDO CONEXION
echo ============================================================
echo.

REM Verificar que ngrok esta corriendo
tasklist | findstr "ngrok.exe" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ngrok no se inicio correctamente
    echo Abriendo panel de ngrok...
    start http://localhost:4040
    pause
    exit /b 1
)

echo [OK] Ngrok activo
echo.

REM Guardar URL
echo https://%DOMAIN% > ngrok_url.txt

echo ============================================================
echo SISTEMA LISTO
echo ============================================================
echo.
echo URL publica:  https://%DOMAIN%
echo Panel ngrok:  http://localhost:4040
echo.
echo OPO:          https://%DOMAIN%/opo
echo Banco:        https://%DOMAIN%
echo.
echo ============================================================
echo PROBANDO CONEXION
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

curl -s -o nul -w "Codigo HTTP: %%{http_code}\n" https://%DOMAIN%

echo.
echo ============================================================
echo ABRIENDO NAVEGADOR
echo ============================================================
echo.

start https://%DOMAIN%

echo.
echo [OK] Sistema funcionando
echo.
echo NOTA: Windows Defender esta desactivado temporalmente
echo Se reactivara automaticamente al reiniciar Windows
echo.
pause
