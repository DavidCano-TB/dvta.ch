@echo off
chcp 65001 >nul
title 🚀 Configurar dvdbank.ch REAL
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN DE dvdbank.ch (DOMINIO REAL)
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará dvdbank.ch como dominio independiente.
echo.
echo ⚠️  REQUISITOS:
echo    1. Ya añadiste dvdbank.ch a Cloudflare
echo    2. Ya cambiaste los nameservers en Hoststar
echo    3. Cloudflare confirmó que dvdbank.ch está activo
echo.
echo ¿Cumples todos los requisitos? (S/N)
set /p requisitos=
if /i not "%requisitos%"=="S" (
    echo.
    echo ⚠️  Por favor, completa los requisitos primero.
    echo.
    echo PASO 1: Añadir dvdbank.ch a Cloudflare
    echo    https://dash.cloudflare.com
    echo.
    echo PASO 2: Cambiar nameservers en Hoststar
    echo    https://my.hoststar.ch
    echo.
    echo PASO 3: Esperar email de Cloudflare (2-48h)
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 CONFIGURANDO DNS EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.

if not exist "cloudflared.exe" (
    echo ❌ cloudflared.exe no encontrado
    pause
    exit /b 1
)

echo Configurando DNS para dvdbank.ch...
cloudflared.exe tunnel route dns dvdcoin dvdbank.ch
echo.

echo Configurando DNS para www.dvdbank.ch...
cloudflared.exe tunnel route dns dvdcoin www.dvdbank.ch
echo.

echo ✅ DNS configurado
echo.

echo ═══════════════════════════════════════════════════════════
echo   🔧 ACTUALIZANDO CONFIGURACIÓN
echo ═══════════════════════════════════════════════════════════
echo.

if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.backup" >nul
    echo ✅ Backup creado
)

(
    echo # Configuracion de Cloudflare Tunnel para DVDcoin
    echo # Dominio principal: dvdbank.ch
    echo tunnel: 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
    echo credentials-file: C:\Users\PC\.cloudflared\6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.json
    echo.
    echo ingress:
    echo   # Dominio principal dvdbank.ch
    echo   - hostname: dvdbank.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: dvdbank.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Subdominio www.dvdbank.ch
    echo   - hostname: www.dvdbank.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: www.dvdbank.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Respaldo: app.david.ch
    echo   - hostname: app.david.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       httpHostHeader: app.david.ch
    echo.
    echo   # Catch-all
    echo   - service: http_status:404
    echo.
    echo metrics: 127.0.0.1:2000
    echo loglevel: info
    echo protocol: quic
    echo retries: 5
    echo grace-period: 30s
) > cloudflare-config.yml

echo ✅ Configuración actualizada
echo.

echo ═══════════════════════════════════════════════════════════
echo   🔧 REINICIANDO SERVICIOS
echo ═══════════════════════════════════════════════════════════
echo.

echo Deteniendo servicios...
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul

echo Iniciando túnel Cloudflare...
start "Cloudflare Tunnel - dvdbank.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 10 /nobreak >nul

echo ✅ Túnel reiniciado
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════
echo.
echo Tu dominio dvdbank.ch está configurado:
echo.
echo    ✅ https://dvdbank.ch
echo    ✅ https://www.dvdbank.ch
echo.
echo ⏱️  Nota: Puede tardar 5-15 minutos en activarse
echo.
echo ¿Quieres abrir dvdbank.ch en tu navegador? (S/N)
set /p abrir=
if /i "%abrir%"=="S" (
    start https://dvdbank.ch
    echo.
    echo ✅ Abriendo navegador...
)
echo.
pause
