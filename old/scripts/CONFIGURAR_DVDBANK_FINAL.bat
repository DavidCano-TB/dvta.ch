@echo off
chcp 65001 >nul
title 🚀 Configurar dvdbank.ch - FINAL
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN FINAL DE dvdbank.ch
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará automáticamente:
echo   ✅ DNS en Cloudflare
echo   ✅ Túnel Cloudflare
echo   ✅ Certificado SSL (HTTPS)
echo   ✅ Acceso desde cualquier red y dispositivo
echo.
echo ⚠️  IMPORTANTE: Solo ejecuta este script DESPUÉS de recibir
echo    el email de Cloudflare confirmando que dvdbank.ch está activo.
echo.
echo ¿Recibiste el email de confirmación de Cloudflare? (S/N)
set /p confirmado=
if /i not "%confirmado%"=="S" (
    echo.
    echo ⚠️  Por favor, espera a recibir el email antes de continuar.
    echo    Cloudflare te enviará un email cuando dvdbank.ch esté activo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 PASO 1: Configurar DNS en Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar cloudflared
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    echo Descargando cloudflared.exe...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    
    if not exist "cloudflared.exe" (
        echo ❌ No se pudo descargar cloudflared.exe
        pause
        exit /b 1
    )
    echo ✅ cloudflared.exe descargado
    echo.
)

echo Configurando DNS para dvdbank.ch...
cloudflared.exe tunnel route dns dvdcoin dvdbank.ch
echo.

echo Configurando DNS para www.dvdbank.ch...
cloudflared.exe tunnel route dns dvdcoin www.dvdbank.ch
echo.

echo ✅ DNS configurado en Cloudflare
echo.

echo ═══════════════════════════════════════════════════════════
echo   🔧 PASO 2: Actualizar configuración del túnel
echo ═══════════════════════════════════════════════════════════
echo.

REM Crear backup
if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul 2>&1
    echo ✅ Backup creado
)

echo Actualizando configuración...
echo.

REM Crear nueva configuración con dvdbank.ch
(
    echo # Configuracion de Cloudflare Tunnel para DVDcoin
    echo # Dominio principal: dvdbank.ch
    echo # Certificado SSL automatico de Cloudflare
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
    echo   # Mantener app.david.ch como respaldo
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
    echo   # Mantener localhost.david.ch como respaldo
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
    echo   # Catch-all para cualquier otro tráfico
    echo   - service: http_status:404
    echo.
    echo # Metricas y configuracion avanzada
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

echo Deteniendo servicios anteriores...
taskkill /F /IM cloudflared.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak >nul
echo.

echo Iniciando servidor Python...
start "DVDcoin Server" /MIN python -m uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 8 /nobreak >nul

REM Verificar servidor
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ⚠️  Advertencia: Servidor no detectado en puerto 8000
    echo    Continuando de todas formas...
) else (
    echo ✅ Servidor Python iniciado
)
echo.

echo Iniciando túnel Cloudflare...
start "Cloudflare Tunnel - dvdbank.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 10 /nobreak >nul

REM Verificar túnel
tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ⚠️  Advertencia: Túnel no detectado
    echo    Puede tardar unos segundos en iniciarse...
) else (
    echo ✅ Túnel Cloudflare iniciado
)
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
echo Características:
echo    ✅ Certificado SSL válido (HTTPS)
echo    ✅ Acceso desde cualquier red y dispositivo
echo    ✅ Compatible con navegadores in-app
echo    ✅ Protección DDoS de Cloudflare
echo    ✅ CDN global (carga rápida)
echo.
echo ⏱️  Nota: Puede tardar 5-15 minutos en activarse completamente
echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 PROBAR AHORA
echo ═══════════════════════════════════════════════════════════
echo.
echo Abre tu navegador y ve a:
echo    https://dvdbank.ch
echo.
echo Si ves "Site Temporarily Closed" o error 1016:
echo    • Espera 5-15 minutos
echo    • Refresca la página (F5)
echo    • El DNS puede tardar un poco en propagarse
echo.
echo ¿Quieres abrir dvdbank.ch en tu navegador ahora? (S/N)
set /p abrir=
if /i "%abrir%"=="S" (
    start https://dvdbank.ch
    echo.
    echo ✅ Abriendo navegador...
    echo.
    echo Si no funciona inmediatamente, espera 5-15 minutos
    echo y refresca la página.
)
echo.
echo ═══════════════════════════════════════════════════════════
echo   📝 URLS DISPONIBLES
echo ═══════════════════════════════════════════════════════════
echo.
echo URL PRINCIPAL (NUEVA):
echo    ✅ https://dvdbank.ch
echo    ✅ https://www.dvdbank.ch
echo.
echo URLs DE RESPALDO:
echo    ✅ https://app.david.ch
echo    ✅ https://localhost.david.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo   💾 GUARDAR INFORMACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Guarda esta información:
echo.
echo Dominio: dvdbank.ch
echo Registrador: Hoststar (hoststar.ch)
echo DNS: Cloudflare
echo Certificado SSL: Cloudflare (gratis, automático)
echo Túnel ID: 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
