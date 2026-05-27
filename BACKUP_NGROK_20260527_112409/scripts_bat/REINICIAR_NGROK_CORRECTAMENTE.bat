@echo off
REM ============================================================
REM REINICIAR NGROK CON CONFIGURACIÓN CORRECTA
REM ============================================================
title Reiniciando ngrok...
color 0B

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║     REINICIO DE NGROK CON CONFIG CORRECTA        ║
echo ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── 1. Detener todos los procesos ngrok ──
echo [1/5] Deteniendo procesos ngrok existentes...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✓ Procesos detenidos

REM ── 2. Verificar configuración principal ──
echo.
echo [2/5] Verificando configuración...
if not exist "config\ngrok_config.txt" (
    echo       ✗ ERROR: config\ngrok_config.txt no existe
    echo.
    echo       Crea el archivo con:
    echo       NGROK_TOKEN=tu_token
    echo       NGROK_DOMAIN=tu_dominio.ngrok-free.dev
    pause
    exit /b 1
)

REM Leer configuración
for /f "tokens=1,2 delims==" %%a in (config\ngrok_config.txt) do (
    if "%%a"=="NGROK_TOKEN" set NGROK_TOKEN=%%b
    if "%%a"=="NGROK_DOMAIN" set NGROK_DOMAIN=%%b
)

if "%NGROK_TOKEN%"=="" (
    echo       ✗ ERROR: NGROK_TOKEN no configurado
    pause
    exit /b 1
)

if "%NGROK_DOMAIN%"=="" (
    echo       ✗ ERROR: NGROK_DOMAIN no configurado
    pause
    exit /b 1
)

echo       ✓ Token: %NGROK_TOKEN:~0,20%...
echo       ✓ Dominio: %NGROK_DOMAIN%

REM ── 3. Sincronizar conf/.ngrok_token ──
echo.
echo [3/5] Sincronizando archivos de configuración...
if not exist "conf" mkdir conf
(
    echo NGROK_TOKEN=%NGROK_TOKEN%
    echo NGROK_DOMAIN=%NGROK_DOMAIN%
) > conf\.ngrok_token
echo       ✓ conf\.ngrok_token actualizado

REM ── 4. Configurar authtoken en ngrok ──
echo.
echo [4/5] Configurando authtoken en ngrok...
ngrok config add-authtoken %NGROK_TOKEN% >nul 2>&1
if errorlevel 1 (
    echo       ⚠ No se pudo configurar authtoken automáticamente
    echo       Continuando de todas formas...
) else (
    echo       ✓ Authtoken configurado
)

REM ── 5. Verificar que el servidor esté corriendo ──
echo.
echo [5/5] Verificando servidor local...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo       ⚠ Servidor no está corriendo en puerto 8000
    echo.
    echo       Iniciando servidor...
    start "DVDcoin Server" /MIN python main.py
    timeout /t 5 /nobreak >nul
    
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        echo       ✗ No se pudo iniciar el servidor
        echo       Ejecuta manualmente: python main.py
        pause
        exit /b 1
    )
)
echo       ✓ Servidor activo en puerto 8000

REM ── 6. Iniciar ngrok con dominio reservado ──
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║           INICIANDO NGROK                        ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo   Dominio: %NGROK_DOMAIN%
echo   Puerto:  8000
echo.

start "ngrok" ngrok http 8000 --domain=%NGROK_DOMAIN% --log=stdout

REM ── 7. Esperar y obtener URL ──
echo   Esperando que ngrok se conecte...
timeout /t 5 /nobreak >nul

REM Intentar obtener URL de la API de ngrok
curl -s http://localhost:4040/api/tunnels > ngrok_temp.json 2>nul
if exist ngrok_temp.json (
    for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_temp.json | ConvertFrom-Json; if ($json.tunnels.Count -gt 0) { $json.tunnels[0].public_url } else { '' }"') do set PUBLIC_URL=%%i
    del ngrok_temp.json
    
    if not "%PUBLIC_URL%"=="" (
        echo   ✓ URL pública: %PUBLIC_URL%
        echo %PUBLIC_URL% > ngrok_url.txt
        echo.
        echo ╔══════════════════════════════════════════════════╗
        echo ║              ✓ NGROK ACTIVO                      ║
        echo ╚══════════════════════════════════════════════════╝
        echo.
        echo   Accede a: %PUBLIC_URL%
        echo   Panel ngrok: http://localhost:4040
        echo.
        
        REM Abrir en navegador
        start "" "%PUBLIC_URL%"
    ) else (
        echo   ⚠ No se pudo obtener la URL pública
        echo   Verifica el panel de ngrok: http://localhost:4040
        start "" "http://localhost:4040"
    )
) else (
    echo   ⚠ No se pudo conectar a la API de ngrok
    echo   Verifica el panel de ngrok: http://localhost:4040
    start "" "http://localhost:4040"
)

echo.
echo   Presiona cualquier tecla para cerrar esta ventana...
pause >nul
