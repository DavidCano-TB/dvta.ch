@echo off
chcp 65001 >nul
title 🌐 Configurar dvdbank.david.ch GRATIS
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 CONFIGURAR dvdbank.david.ch (GRATIS)
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará automáticamente:
echo   ✅ dvdbank.david.ch (GRATIS)
echo   ✅ Certificado SSL (HTTPS)
echo   ✅ Acceso desde cualquier red y dispositivo
echo.
echo Tiempo estimado: 5 minutos
echo.
pause

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 PASO 1: Configurar DNS en Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar cloudflared
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    pause
    exit /b 1
)

echo Configurando DNS para dvdbank.david.ch...
cloudflared.exe tunnel route dns dvdcoin dvdbank.david.ch

echo.
echo ✅ DNS configurado
echo.

echo ═══════════════════════════════════════════════════════════
echo   🔧 PASO 2: Actualizar configuración del túnel
echo ═══════════════════════════════════════════════════════════
echo.

REM Crear backup
if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.backup" >nul
    echo ✅ Backup creado
)

echo Actualizando configuración...
echo.

REM Crear nueva configuración
(
    echo # Configuracion de Cloudflare Tunnel para DVDcoin
    echo # Dominio: david.ch
    echo # Certificado SSL automatico de Cloudflare
    echo tunnel: 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
    echo credentials-file: C:\Users\PC\.cloudflared\6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.json
    echo.
    echo ingress:
    echo   # Subdominio dvdbank.david.ch - PRINCIPAL
    echo   - hostname: dvdbank.david.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: dvdbank.david.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Subdominio app.david.ch - RESPALDO
    echo   - hostname: app.david.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: app.david.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Subdominio localhost.david.ch - RESPALDO
    echo   - hostname: localhost.david.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: localhost.david.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Catch-all
    echo   - service: http_status:404
    echo.
    echo metrics: 127.0.0.1:2000
    echo loglevel: info
    echo protocol: quic
    echo retries: 5
    echo grace-period: 30s
    echo no-autoupdate: false
) > cloudflare-config.yml

echo ✅ Configuración actualizada
echo.

echo ═══════════════════════════════════════════════════════════
echo   🔧 PASO 3: Reiniciar servicios
echo ═══════════════════════════════════════════════════════════
echo.

echo Deteniendo servicios...
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul

echo Iniciando túnel Cloudflare...
start "Cloudflare Tunnel - dvdbank.david.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 8 /nobreak >nul

echo ✅ Túnel reiniciado
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════
echo.
echo Tu subdominio está configurado:
echo.
echo    ✅ https://dvdbank.david.ch
echo.
echo Características:
echo    ✅ GRATIS (sin costos)
echo    ✅ Certificado SSL válido (HTTPS)
echo    ✅ Acceso desde cualquier red y dispositivo
echo    ✅ Compatible con navegadores in-app
echo.
echo ⏱️  Nota: Puede tardar 1-5 minutos en activarse
echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 PROBAR AHORA
echo ═══════════════════════════════════════════════════════════
echo.
echo Abre tu navegador y ve a:
echo    https://dvdbank.david.ch
echo.
echo ¿Quieres abrir la URL ahora? (S/N)
set /p abrir=
if /i "%abrir%"=="S" (
    start https://dvdbank.david.ch
    echo.
    echo ✅ Abriendo navegador...
    echo.
    echo Si no funciona inmediatamente, espera 2-3 minutos
    echo y refresca la página.
)
echo.
echo ═══════════════════════════════════════════════════════════
echo   📝 URLS DISPONIBLES
echo ═══════════════════════════════════════════════════════════
echo.
echo URL PRINCIPAL (NUEVA):
echo    ✅ https://dvdbank.david.ch
echo.
echo URLs DE RESPALDO:
echo    ✅ https://app.david.ch
echo    ✅ https://localhost.david.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 💡 NOTA: Si más tarde completas el pago de dvdbank.ch en
echo    Hoststar, podrás tener ambos funcionando:
echo    • https://dvdbank.ch (dominio propio)
echo    • https://dvdbank.david.ch (subdominio gratis)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
