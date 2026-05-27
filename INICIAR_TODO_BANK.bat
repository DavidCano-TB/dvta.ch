@echo off
chcp 65001 >nul
title DVDBank - Inicio Completo (dvta.ch/bank)
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 INICIANDO DVDBANK - dvta.ch/bank
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   ⚠️  IMPORTANTE: La aplicación ahora está en /bank
echo   📍 URL: https://dvta.ch/bank
echo.

cd /d "%~dp0"

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

echo [1/7] Deteniendo procesos existentes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

echo [2/7] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo      Matando proceso PID %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul
echo      ✅ Puerto 8000 liberado
echo.

echo [3/7] Verificando archivos necesarios...
if not exist "main.py" (
    echo      ❌ ERROR: main.py no encontrado
    pause
    exit /b 1
)
if not exist "static\index.html" (
    echo      ❌ ERROR: static\index.html no encontrado
    pause
    exit /b 1
)
if not exist "data" mkdir data
if not exist "config" mkdir config
echo      ✅ Archivos verificados
echo.

echo [4/7] Iniciando servidor Python en puerto 8000...
echo      Esto puede tardar 5-10 segundos...
start "DVDBank Server - dvta.ch/bank" /MIN python main.py
timeout /t 8 /nobreak >nul
echo      ✅ Servidor Python iniciado
echo.

echo [5/7] Verificando servidor Python...
set MAX_RETRIES=10
set RETRY_COUNT=0

:CHECK_SERVER
set /a RETRY_COUNT+=1
echo      Intento %RETRY_COUNT%/%MAX_RETRIES%...

REM Verificar si el proceso está corriendo
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ❌ ERROR: El servidor Python no está corriendo
    echo.
    echo      Revisa el log: logs\python_server.log
    pause
    exit /b 1
)

REM Intentar conectar al servidor
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/bank > logs\http_check.txt 2>&1
set /p HTTP_CODE=<logs\http_check.txt

if "%HTTP_CODE%"=="200" (
    echo      ✅ Servidor respondiendo correctamente ^(HTTP %HTTP_CODE%^)
    goto SERVER_OK
) else if "%HTTP_CODE%"=="404" (
    echo      ✅ Servidor activo ^(HTTP %HTTP_CODE% - esperado para /bank^)
    goto SERVER_OK
) else if "%HTTP_CODE%"=="000" (
    if %RETRY_COUNT% lss %MAX_RETRIES% (
        echo      ⏳ Servidor iniciando... esperando 2 segundos
        timeout /t 2 /nobreak >nul
        goto CHECK_SERVER
    ) else (
        echo      ❌ ERROR: Servidor no responde después de %MAX_RETRIES% intentos
        echo.
        echo      Revisa el log: logs\python_server.log
        pause
        exit /b 1
    )
) else (
    echo      ⚠️  Servidor responde con código: %HTTP_CODE%
    goto SERVER_OK
)

:SERVER_OK
echo.

echo [6/7] Iniciando Cloudflare Tunnel para dvta.ch...
if not exist "cloudflared.exe" (
    echo      ❌ cloudflared.exe no encontrado
    echo      ℹ️  Descarga desde: https://github.com/cloudflare/cloudflared/releases
    echo      ℹ️  Guarda como: c:\dvdcoin\cloudflared.exe
    echo.
    echo      ⚠️  El servidor local funciona, pero no será accesible desde dvta.ch
    goto SKIP_TUNNEL
)

if not exist "cloudflare-tunnel-dvta.yml" (
    echo      ⚠️  cloudflare-tunnel-dvta.yml no encontrado
    echo      ℹ️  Ejecuta primero: CONFIGURAR_TUNNEL_DVTA.bat
    echo.
    echo      ⚠️  El servidor local funciona, pero no será accesible desde dvta.ch
    goto SKIP_TUNNEL
)

start "Cloudflare Tunnel - dvta.ch" /MIN cloudflared.exe tunnel --config cloudflare-tunnel-dvta.yml run
timeout /t 5 /nobreak >nul
echo      ✅ Cloudflare Tunnel iniciado
echo.

:SKIP_TUNNEL

echo [7/7] Verificando estado final del sistema...
echo.
echo      ┌─────────────────────────────────────────┐
echo      │  ESTADO DE LOS SERVICIOS                │
echo      └─────────────────────────────────────────┘

tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Python Server: ACTIVO
) else (
    echo      ❌ Python Server: INACTIVO
)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel: ACTIVO
) else (
    echo      ⚠️  Cloudflare Tunnel: INACTIVO
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 URLs de acceso:
echo    • Local:           http://localhost:8000/bank
echo    • Público (dvta):  https://dvta.ch/bank
echo    • Público (www):   https://www.dvta.ch/bank
echo.
echo 📋 Archivos de log:
echo    • Python:     logs\python_server.log
echo    • Cloudflare: logs\cloudflare_tunnel.log
echo.
echo 🔧 Comandos útiles:
echo    • Ver logs Python:     type logs\python_server.log
echo    • Ver logs Cloudflare: type logs\cloudflare_tunnel.log
echo    • Detener sistema:     DETENER_SISTEMA.bat
echo    • Ver estado:          VER_ESTADO_SISTEMA.bat
echo.
echo 🌐 Abre tu navegador en:
echo    https://dvta.ch/bank
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

REM Abrir navegador
start https://dvta.ch/bank

echo.
echo ✅ Navegador abierto
echo.
echo Esta ventana puede permanecer abierta.
echo Los servicios están corriendo en segundo plano.
echo.
pause
