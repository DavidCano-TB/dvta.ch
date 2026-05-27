@echo off
chcp 65001 >nul
REM ============================================================
REM ARREGLO RÁPIDO DE NGROK - SOLUCIÓN INMEDIATA
REM ============================================================
title Arreglando ngrok...
color 0A

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║         ARREGLO RÁPIDO DE NGROK                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── PASO 1: Matar TODOS los procesos ngrok ──
echo [1/4] Deteniendo TODOS los procesos ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 3 /nobreak >nul

REM Verificar que se detuvieron
tasklist | findstr "ngrok.exe" >nul 2>&1
if not errorlevel 1 (
    echo   ⚠ Aún hay procesos ngrok. Intentando de nuevo...
    taskkill /F /IM ngrok.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo   ✓ Procesos ngrok detenidos
echo.

REM ── PASO 2: Leer configuración ──
echo [2/4] Leyendo configuración...

if not exist "config\ngrok_config.txt" (
    echo   ✗ ERROR: config\ngrok_config.txt no existe
    pause
    exit /b 1
)

for /f "tokens=1,2 delims==" %%a in (config\ngrok_config.txt) do (
    if "%%a"=="NGROK_TOKEN" set NGROK_TOKEN=%%b
    if "%%a"=="NGROK_DOMAIN" set NGROK_DOMAIN=%%b
)

if "%NGROK_TOKEN%"=="" (
    echo   ✗ ERROR: NGROK_TOKEN no configurado
    pause
    exit /b 1
)

if "%NGROK_DOMAIN%"=="" (
    echo   ✗ ERROR: NGROK_DOMAIN no configurado
    pause
    exit /b 1
)

echo   ✓ Token: %NGROK_TOKEN:~0,20%...
echo   ✓ Dominio: %NGROK_DOMAIN%
echo.

REM ── PASO 3: Verificar servidor ──
echo [3/4] Verificando servidor...

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Servidor no está corriendo. Iniciando...
    start "DVDcoin Server" /MIN python main.py
    timeout /t 5 /nobreak >nul
    
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        echo   ✗ No se pudo iniciar el servidor
        pause
        exit /b 1
    )
)

echo   ✓ Servidor activo en puerto 8000
echo.

REM ── PASO 4: Iniciar ngrok (UNA SOLA INSTANCIA) ──
echo [4/4] Iniciando ngrok...
echo   Dominio: %NGROK_DOMAIN%
echo.

REM Buscar ngrok
where ngrok >nul 2>&1
if errorlevel 1 (
    if exist "ngrok.exe" (
        set NGROK_CMD=ngrok.exe
    ) else (
        echo   ✗ ngrok no encontrado
        pause
        exit /b 1
    )
) else (
    set NGROK_CMD=ngrok
)

REM Configurar authtoken
%NGROK_CMD% config add-authtoken %NGROK_TOKEN% >nul 2>&1

REM Iniciar ngrok
start "ngrok - %NGROK_DOMAIN%" %NGROK_CMD% http 8000 --domain=%NGROK_DOMAIN% --log=stdout --log-level=info

REM Esperar conexión
echo   Esperando conexión...
timeout /t 8 /nobreak >nul

REM Obtener URL
curl -s http://localhost:4040/api/tunnels > ngrok_temp.json 2>nul
if exist ngrok_temp.json (
    for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_temp.json -Raw | ConvertFrom-Json; if ($json.tunnels.Count -gt 0) { $json.tunnels[0].public_url } else { '' }"') do set PUBLIC_URL=%%i
    del ngrok_temp.json
)

echo.
if "%PUBLIC_URL%"=="" (
    echo   ⚠ No se pudo obtener la URL
    echo   Verifica: http://localhost:4040
    start "" "http://localhost:4040"
) else (
    echo   ✓ URL pública: %PUBLIC_URL%
    echo %PUBLIC_URL% > ngrok_url.txt
    
    REM Verificar accesibilidad
    curl -s -o nul -w "%%{http_code}" "%PUBLIC_URL%" > http_code_temp.txt 2>&1
    set /p HTTP_CODE=<http_code_temp.txt
    del http_code_temp.txt
    
    echo.
    if "%HTTP_CODE%"=="200" (
        echo   ✓ ¡FUNCIONANDO CORRECTAMENTE!
        echo.
        start "" "%PUBLIC_URL%"
    ) else if "%HTTP_CODE%"=="000" (
        echo   ⚠ ADVERTENCIA: Endpoint offline
        echo.
        echo   El dominio "%NGROK_DOMAIN%" puede estar:
        echo   - Expirado
        echo   - Revocado
        echo   - Asignado a otra cuenta
        echo.
        echo   Verifica tu cuenta: https://dashboard.ngrok.com
        echo   Panel ngrok: http://localhost:4040
        echo.
        start "" "http://localhost:4040"
    ) else (
        echo   ⚠ Código HTTP: %HTTP_CODE%
        start "" "%PUBLIC_URL%"
    )
)

echo.
echo ════════════════════════════════════════════════════
pause
