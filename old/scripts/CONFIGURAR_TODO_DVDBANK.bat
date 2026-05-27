@echo off
chcp 65001 >nul
title 🚀 Configuración Completa dvdbank.ch
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN AUTOMÁTICA DE dvdbank.ch
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará AUTOMÁTICAMENTE:
echo   ✅ DNS en Cloudflare (dvdbank.ch y www.dvdbank.ch)
echo   ✅ Túnel Cloudflare
echo   ✅ Certificado SSL (HTTPS)
echo   ✅ Servidor Python
echo   ✅ Todo lo necesario
echo.
echo ⚠️  IMPORTANTE: Primero necesitas añadir dvdbank.ch a Cloudflare
echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO MANUAL: Añadir dvdbank.ch a Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Abre: https://dash.cloudflare.com
echo 2. Haz clic en "Add a Site"
echo 3. Escribe: dvdbank.ch
echo 4. Haz clic en "Add site"
echo 5. Selecciona plan FREE
echo 6. Haz clic en "Continue"
echo.
echo Cloudflare te mostrará 2 nameservers. CÓPIALOS.
echo.
echo ¿Ya añadiste dvdbank.ch a Cloudflare y copiaste los nameservers? (S/N)
set /p cloudflare_ok=
if /i not "%cloudflare_ok%"=="S" (
    echo.
    echo ⚠️  Por favor, añade dvdbank.ch a Cloudflare primero.
    echo    Abriendo Cloudflare en tu navegador...
    start https://dash.cloudflare.com
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO MANUAL: Cambiar nameservers en Hoststar
echo ═══════════════════════════════════════════════════════════
echo.
echo Ahora necesitas cambiar los nameservers en Hoststar:
echo.
echo 1. Ve a: https://my.hoststar.ch
echo 2. Inicia sesión
echo 3. Ve a "Mes domaines" → "dvdbank.ch"
echo 4. Busca "Nameservers" o "DNS"
echo 5. Cambia a "Nameservers personnalisés"
echo 6. Pega los 2 nameservers de Cloudflare
echo 7. Guarda los cambios
echo.
echo ¿Ya cambiaste los nameservers en Hoststar? (S/N)
set /p nameservers_ok=
if /i not "%nameservers_ok%"=="S" (
    echo.
    echo ⚠️  Por favor, cambia los nameservers en Hoststar primero.
    echo    Abriendo Hoststar en tu navegador...
    start https://my.hoststar.ch
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   ⏱️  ESPERANDO PROPAGACIÓN DNS
echo ═══════════════════════════════════════════════════════════
echo.
echo La propagación DNS puede tardar 2-48 horas (normalmente 2-4 horas).
echo.
echo ¿Quieres continuar de todas formas y configurar todo ahora? (S/N)
echo (Recomendado: S - Todo estará listo cuando el DNS se propague)
set /p continuar=
if /i not "%continuar%"=="S" (
    echo.
    echo Configuración cancelada.
    echo Ejecuta este script de nuevo cuando el DNS esté propagado.
    pause
    exit /b 0
)

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 CONFIGURANDO DNS EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar cloudflared
if not exist "cloudflared.exe" (
    echo ❌ cloudflared.exe no encontrado
    echo Descargando...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if not exist "cloudflared.exe" (
        echo ❌ No se pudo descargar cloudflared.exe
        pause
        exit /b 1
    )
    echo ✅ cloudflared.exe descargado
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
echo   🔧 ACTUALIZANDO CONFIGURACIÓN DEL TÚNEL
echo ═══════════════════════════════════════════════════════════
echo.

REM Crear backup
if exist "cloudflare-config.yml" (
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%b%%a)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.backup_%mydate%_%mytime%" >nul 2>&1
    echo ✅ Backup creado
)

echo Creando nueva configuración...
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
    echo   # Respaldo: app.david.ch
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
    echo   # Respaldo: localhost.david.ch
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
echo   🔧 REINICIANDO TODOS LOS SERVICIOS
echo ═══════════════════════════════════════════════════════════
echo.

echo Deteniendo servicios anteriores...
taskkill /F /IM cloudflared.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak >nul
echo ✅ Servicios detenidos
echo.

echo Iniciando servidor Python...
start "DVDcoin Server - dvdbank.ch" /MIN python -m uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 8 /nobreak >nul

netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ⚠️  Advertencia: Servidor no detectado en puerto 8000
) else (
    echo ✅ Servidor Python iniciado correctamente
)
echo.

echo Iniciando túnel Cloudflare...
start "Cloudflare Tunnel - dvdbank.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 10 /nobreak >nul

tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ⚠️  Advertencia: Túnel no detectado
) else (
    echo ✅ Túnel Cloudflare iniciado correctamente
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
echo URLs de respaldo:
echo    ✅ https://app.david.ch
echo    ✅ https://localhost.david.ch
echo.
echo Características:
echo    ✅ Certificado SSL válido (HTTPS)
echo    ✅ Acceso desde cualquier red y dispositivo
echo    ✅ Compatible con navegadores in-app
echo    ✅ Protección DDoS de Cloudflare
echo    ✅ CDN global
echo.
echo ⏱️  IMPORTANTE:
echo    • Si acabas de cambiar los nameservers, puede tardar
echo      2-48 horas en propagarse (normalmente 2-4 horas)
echo    • Recibirás un email de Cloudflare cuando esté listo
echo    • Mientras tanto, puedes usar: https://app.david.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICAR ESTADO
echo ═══════════════════════════════════════════════════════════
echo.
echo Para verificar el estado actual:
echo    VERIFICAR_DVDBANK.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
