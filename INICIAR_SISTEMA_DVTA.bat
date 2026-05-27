@echo off
chcp 65001 >nul
title DVDBank - Sistema dvta.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 INICIANDO SISTEMA DVDBANK - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

echo [1/6] Deteniendo procesos existentes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

echo [2/6] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 /nobreak >nul
echo      ✅ Puerto 8000 liberado
echo.

echo [3/6] Iniciando servidor Python en puerto 8000...
start /B python main.py > logs\python_server.log 2>&1
timeout /t 5 /nobreak >nul
echo      ✅ Servidor Python iniciado
echo.

echo [4/6] Verificando servidor Python...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000 > logs\http_check.txt 2>&1
set /p HTTP_CODE=<logs\http_check.txt
if "%HTTP_CODE%"=="200" (
    echo      ✅ Servidor respondiendo correctamente ^(HTTP %HTTP_CODE%^)
) else if "%HTTP_CODE%"=="000" (
    echo      ⚠️  Servidor iniciando... ^(puede tardar unos segundos^)
) else (
    echo      ⚠️  Servidor responde con código: %HTTP_CODE%
)
echo.

echo [5/6] Iniciando Cloudflare Tunnel para dvta.ch...
if exist "cloudflared.exe" (
    if exist "cloudflare-tunnel-dvta.yml" (
        start "Cloudflare Tunnel - dvta.ch" cloudflared.exe tunnel --config cloudflare-tunnel-dvta.yml run > logs\cloudflare_tunnel.log 2>&1
        timeout /t 8 /nobreak >nul
        echo      ✅ Cloudflare Tunnel iniciado
    ) else (
        echo      ⚠️  Archivo cloudflare-tunnel-dvta.yml no encontrado
        echo      ℹ️  Ejecuta primero: CONFIGURAR_TUNNEL_DVTA.bat
    )
) else (
    echo      ❌ cloudflared.exe no encontrado
    echo      ℹ️  Descarga desde: https://github.com/cloudflare/cloudflared/releases
    echo      ℹ️  Guarda como: c:\dvdcoin\cloudflared.exe
)
echo.

echo [6/6] Verificando estado del sistema...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Python: Corriendo
) else (
    echo      ❌ Python: No activo
)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare: Corriendo
) else (
    echo      ⚠️  Cloudflare: No activo
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 URLs de acceso:
echo    • Local:    http://localhost:8000
echo    • Público:  https://dvta.ch (cuando DNS esté activo)
echo    • Público:  https://www.dvta.ch (cuando DNS esté activo)
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
echo ═══════════════════════════════════════════════════════════════════════════
echo.
