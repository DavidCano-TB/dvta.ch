@echo off
chcp 65001 >nul
title 🌐 Configurar Subdominio GRATIS
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 CONFIGURAR SUBDOMINIO GRATIS DE david.ch
echo ═══════════════════════════════════════════════════════════
echo.
echo Ya tienes el dominio david.ch, así que puedes crear
echo subdominios GRATIS con certificado SSL incluido.
echo.
echo ═══════════════════════════════════════════════════════════
echo   📝 SUBDOMINIOS SUGERIDOS
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. dvd.david.ch       (Corto y relacionado con DVD)
echo 2. bank.david.ch      (Relacionado con DVDcoin Bank)
echo 3. coin.david.ch      (Relacionado con monedas)
echo 4. app.david.ch       (YA CONFIGURADO ✅)
echo 5. dvdcoin.david.ch   (Nombre completo)
echo.
echo ═══════════════════════════════════════════════════════════
echo.

set /p subdominio="Escribe el subdominio que quieres (sin .david.ch): "

if "%subdominio%"=="" (
    echo.
    echo ❌ No escribiste ningún subdominio
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 CONFIGURANDO %subdominio%.david.ch
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Verificar cloudflared
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    pause
    exit /b 1
)

echo 📡 Configurando DNS en Cloudflare...
echo.

cloudflared.exe tunnel route dns dvdcoin %subdominio%.david.ch

if errorlevel 1 (
    echo.
    echo ⚠️  Puede que ya esté configurado o haya un error
    echo.
) else (
    echo.
    echo ✅ DNS configurado correctamente
    echo.
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   📝 ACTUALIZANDO CONFIGURACIÓN
echo ═══════════════════════════════════════════════════════════
echo.

REM Crear backup
if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.backup" >nul
    echo ✅ Backup creado: cloudflare-config.yml.backup
)

REM Añadir el nuevo hostname al archivo de configuración
echo.
echo Añadiendo %subdominio%.david.ch a la configuración...
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
    echo   # Subdominio %subdominio%.david.ch - NUEVO
    echo   - hostname: %subdominio%.david.ch
    echo     service: http://127.0.0.1:8000
    echo     originRequest:
    echo       noTLSVerify: true
    echo       connectTimeout: 60s
    echo       tlsTimeout: 20s
    echo       tcpKeepAlive: 60s
    echo       keepAliveConnections: 1024
    echo       keepAliveTimeout: 120s
    echo       httpHostHeader: %subdominio%.david.ch
    echo       disableChunkedEncoding: false
    echo       proxyType: http
    echo.
    echo   # Subdominio app.david.ch - URL PRINCIPAL
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
    echo   # Subdominio localhost.david.ch - URL ALTERNATIVA
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
echo   🔄 REINICIANDO SERVICIOS
echo ═══════════════════════════════════════════════════════════
echo.

echo Deteniendo servicios...
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul

echo Iniciando túnel Cloudflare...
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 5 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════
echo.
echo Tu nuevo subdominio está configurado:
echo.
echo    ✅ https://%subdominio%.david.ch
echo.
echo Características:
echo    ✅ Certificado SSL válido (HTTPS)
echo    ✅ Acceso desde cualquier red
echo    ✅ Compatible con todos los dispositivos
echo    ✅ GRATIS (sin costos adicionales)
echo.
echo ⏱️  Nota: Puede tardar 1-5 minutos en activarse
echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 PRUEBA AHORA
echo ═══════════════════════════════════════════════════════════
echo.
echo Abre tu navegador y ve a:
echo    https://%subdominio%.david.ch
echo.
echo ¿Quieres abrir la URL ahora? (S/N)
set /p abrir=
if /i "%abrir%"=="S" (
    start https://%subdominio%.david.ch
    echo.
    echo ✅ Abriendo navegador...
)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo    • https://%subdominio%.david.ch (NUEVO)
echo    • https://app.david.ch
echo    • https://localhost.david.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
