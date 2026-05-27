@echo off
REM ============================================================
REM DVDCOIN BANK - INICIO CON CLOUDFLARE TUNNEL
REM Sistema sin limites de conexiones con URL fija
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    REM Auto-elevar sin preguntar
    powershell -Command "Start-Process '%~f0' -Verb RunAs" >nul 2>&1
    exit /b
)

:admin
chcp 65001 >nul
title DVDCoin Bank - Cloudflare Tunnel [ADMIN]
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN BANK - CLOUDFLARE TUNNEL (SIN LIMITES)       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM [1/6] LIMPIEZA DE PROCESOS ANTERIORES
REM ============================================================
echo [1/6] Limpiando procesos anteriores...

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1

REM Liberar puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo       ✓ Procesos anteriores terminados
timeout /t 2 /nobreak >nul

REM ============================================================
REM [2/6] LIMPIEZA DE LOGS ANTIGUOS
REM ============================================================
echo.
echo [2/6] Limpiando logs antiguos...

if exist server.log del /Q server.log >nul 2>&1
if exist cloudflare_tunnel.log del /Q cloudflare_tunnel.log >nul 2>&1

echo       ✓ Logs limpiados

REM ============================================================
REM [3/6] VERIFICACION DE CLOUDFLARED
REM ============================================================
echo.
echo [3/6] Verificando cloudflared...

set CLOUDFLARED_CMD=cloudflared
if exist "cloudflared.exe" set CLOUDFLARED_CMD=cloudflared.exe
if exist "tools\cloudflared.exe" set CLOUDFLARED_CMD=tools\cloudflared.exe

REM Verificar que cloudflared existe
%CLOUDFLARED_CMD% version >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: cloudflared no encontrado
    echo.
    echo       Descarga cloudflared desde:
    echo       https://github.com/cloudflare/cloudflared/releases/latest
    echo.
    echo       O instala con winget:
    echo       winget install --id Cloudflare.cloudflared
    echo.
    echo       Luego ejecuta:
    echo       cloudflared tunnel login
    echo       cloudflared tunnel create dvdcoin
    echo.
    echo       Consulta TUTORIAL_CLOUDFLARE_TUNNEL.md para mas detalles
    echo.
    pause
    exit /b 1
)

echo       ✓ cloudflared encontrado

REM Verificar que existe el archivo de configuración
if not exist "cloudflare-config.yml" (
    echo       ✗ ERROR: cloudflare-config.yml no encontrado
    echo.
    echo       Crea el archivo cloudflare-config.yml siguiendo el tutorial
    echo       Consulta TUTORIAL_CLOUDFLARE_TUNNEL.md
    echo.
    pause
    exit /b 1
)

echo       ✓ Configuración encontrada

REM ============================================================
REM [4/6] INICIO DEL SERVIDOR PYTHON
REM ============================================================
echo.
echo [4/6] Iniciando servidor DVDcoin...

REM Verificar que main.py existe
if not exist "main.py" (
    if not exist "src\main.py" (
        echo       ✗ ERROR: No se encontro main.py
        echo.
        pause
        exit /b 1
    )
)

REM Iniciar servidor en segundo plano
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000 >server.log 2>&1

echo       ✓ Servidor iniciado
echo       Esperando que el servidor este listo...

REM Esperar y verificar cada 3 segundos (maximo 5 intentos)
set SERVER_READY=0
for /L %%i in (1,1,5) do (
    timeout /t 3 /nobreak >nul
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo       ✓ Servidor respondiendo en puerto 8000
        set SERVER_READY=1
        goto :server_ready
    )
    echo       Esperando... (%%i/5^)
)

:server_ready

if "%SERVER_READY%"=="0" (
    echo       ✗ ERROR: El servidor no responde en el puerto 8000
    echo       Revisa server.log para mas detalles
    echo.
    pause
    exit /b 1
)

REM ============================================================
REM [5/6] VERIFICACION DEL SERVIDOR LOCAL
REM ============================================================
echo.
echo [5/6] Verificando servidor local...

timeout /t 2 /nobreak >nul

REM Intentar acceder al servidor
curl -s -o nul -w "%%{http_code}" http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo       ⚠ No se pudo verificar con curl (puede no estar instalado^)
) else (
    echo       ✓ Servidor verificado y funcionando
)

REM ============================================================
REM [6/6] INICIO DE CLOUDFLARE TUNNEL
REM ============================================================
echo.
echo [6/6] Iniciando Cloudflare Tunnel...

REM Iniciar cloudflared con el archivo de configuración
start /B %CLOUDFLARED_CMD% tunnel --config cloudflare-config.yml run >cloudflare_tunnel.log 2>&1

echo       ✓ Túnel iniciado
echo       Esperando establecer conexión...

timeout /t 8 /nobreak >nul

REM Verificar que cloudflared está corriendo
tasklist | findstr cloudflared >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: cloudflared no está corriendo
    echo       Revisa cloudflare_tunnel.log para mas detalles
    echo.
    type cloudflare_tunnel.log
    echo.
    pause
    exit /b 1
)

echo       ✓ Túnel establecido

REM Intentar obtener la URL del túnel desde los logs
timeout /t 2 /nobreak >nul

REM Buscar la URL en los logs
for /f "tokens=*" %%i in ('findstr /C:"https://" cloudflare_tunnel.log 2^>nul') do (
    set TUNNEL_LINE=%%i
    goto :found_url
)

:found_url

REM ============================================================
REM RESUMEN FINAL
REM ============================================================
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ SISTEMA INICIADO CORRECTAMENTE               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ ACCESO LOCAL                                                 │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   URL:        http://localhost:8000
echo   Panel OPO:  http://localhost:8000/opo
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ ACCESO PUBLICO (CLOUDFLARE TUNNEL)                           │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   Tu URL pública está configurada en cloudflare-config.yml
echo   
echo   Para ver la URL exacta, revisa:
echo   - Dashboard de Cloudflare: https://dash.cloudflare.com
echo   - O ejecuta: cloudflared tunnel info dvdcoin
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ VENTAJAS DE CLOUDFLARE TUNNEL                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   ✓ Sin límites de conexiones
echo   ✓ URL fija (no cambia)
echo   ✓ SSL/HTTPS automático
echo   ✓ Protección DDoS
echo   ✓ Gratis para siempre
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo El sistema esta funcionando en segundo plano.
echo.
echo Para detener el servidor:
echo   - Ejecuta: DETENER_SERVIDOR.bat, o
echo   - Cierra esta ventana y ejecuta:
echo     taskkill /F /IM python.exe
echo     taskkill /F /IM cloudflared.exe
echo.
echo Para ver los logs:
echo   - Servidor: type server.log
echo   - Túnel:    type cloudflare_tunnel.log
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
echo (El servidor seguira corriendo en segundo plano)
echo.
pause >nul

REM El servidor continua ejecutandose en segundo plano
exit /b 0
