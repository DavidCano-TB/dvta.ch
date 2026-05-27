@echo off
chcp 65001 >nul
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   CONFIGURAR DOMINIO DVD.CH CON CLOUDFLARE TUNNEL
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ⚠️  Este script requiere permisos de administrador
    echo.
    echo Ejecutando como administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/7] Verificando cloudflared...
where cloudflared >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       ✗ ERROR: cloudflared no está instalado
    echo.
    echo       Instala cloudflared primero:
    echo       winget install --id Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)
echo       ✓ cloudflared encontrado

echo.
echo [2/7] Verificando túnel existente...
cloudflared tunnel list | findstr "dvdcoin" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       ✗ ERROR: Túnel 'dvdcoin' no encontrado
    echo.
    echo       Crea el túnel primero:
    echo       cloudflared tunnel create dvdcoin
    echo.
    pause
    exit /b 1
)
echo       ✓ Túnel 'dvdcoin' encontrado

echo.
echo ═══════════════════════════════════════════════════════════
echo   IMPORTANTE: CONFIGURACIÓN DE DNS
echo ═══════════════════════════════════════════════════════════
echo.
echo Antes de continuar, asegúrate de:
echo.
echo 1. Haber añadido dvd.ch a tu cuenta de Cloudflare
echo    https://dash.cloudflare.com
echo.
echo 2. Haber cambiado los nameservers en tu registrador
echo    a los nameservers de Cloudflare
echo.
echo 3. Esperar a que el DNS se propague (2-24 horas)
echo.
echo ¿Has completado estos pasos? (S/N)
set /p CONFIRM="> "

if /I not "%CONFIRM%"=="S" (
    echo.
    echo Completa estos pasos primero y vuelve a ejecutar este script.
    echo.
    echo Consulta la guía completa: CONFIGURAR_DVD_CH.md
    echo.
    pause
    exit /b 0
)

echo.
echo [3/7] Configurando ruta DNS para dvd.ch...
cloudflared tunnel route dns dvdcoin dvd.ch
if %ERRORLEVEL% NEQ 0 (
    echo       ⚠️  Error al configurar DNS
    echo       Esto puede ser normal si ya está configurado
) else (
    echo       ✓ DNS configurado correctamente
)

echo.
echo [4/7] Actualizando cloudflare-config.yml...

REM Crear backup del archivo actual
if exist "cloudflare-config.yml" (
    copy "cloudflare-config.yml" "cloudflare-config.yml.backup" >nul 2>&1
    echo       ✓ Backup creado: cloudflare-config.yml.backup
)

REM Crear nuevo archivo de configuración
(
echo # Configuracion de Cloudflare Tunnel para DVDcoin
echo # Dominio: dvd.ch
echo tunnel: 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
echo credentials-file: C:\Users\PC\.cloudflared\6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.json
echo.
echo ingress:
echo   - hostname: dvd.ch
echo     service: http://localhost:8000
echo     originRequest:
echo       noTLSVerify: false
echo       connectTimeout: 30s
echo       tlsTimeout: 10s
echo       tcpKeepAlive: 30s
echo       keepAliveConnections: 100
echo       keepAliveTimeout: 90s
echo       httpHostHeader: localhost:8000
echo   - service: http_status:404
echo.
echo metrics: localhost:2000
echo loglevel: info
echo protocol: auto
echo retries: 5
echo grace-period: 30s
) > cloudflare-config.yml

echo       ✓ Archivo cloudflare-config.yml actualizado

echo.
echo [5/7] Verificando servidor Python...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo       ⚠️  Servidor Python no está corriendo
    echo       Iniciando servidor...
    start /B python main.py
    timeout /t 5 /nobreak >nul
    echo       ✓ Servidor iniciado
) else (
    echo       ✓ Servidor Python ya está corriendo
)

echo.
echo [6/7] Reiniciando Cloudflare Tunnel...

REM Detener túnel actual
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Iniciar túnel con nueva configuración
echo       Iniciando túnel con dvd.ch...
start /B cloudflared tunnel --config cloudflare-config.yml run dvdcoin >cloudflare_tunnel.log 2>&1

timeout /t 8 /nobreak >nul

REM Verificar que cloudflared está corriendo
tasklist | findstr cloudflared >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: cloudflared no se inició correctamente
    echo       Revisa cloudflare_tunnel.log para más detalles
    echo.
    type cloudflare_tunnel.log
    echo.
    pause
    exit /b 1
)

echo       ✓ Túnel iniciado correctamente

echo.
echo [7/7] Verificando configuración...

REM Verificar DNS
echo       Verificando DNS de dvd.ch...
nslookup dvd.ch >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo       ⚠️  DNS aún no propagado completamente
    echo       Esto es normal, puede tardar 2-24 horas
) else (
    echo       ✓ DNS responde correctamente
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════
echo.
echo Tu dominio dvd.ch está configurado con Cloudflare Tunnel
echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │ ACCESO A TU APLICACIÓN                                   │
echo └──────────────────────────────────────────────────────────┘
echo.
echo   URL Principal:  https://dvd.ch
echo   URL Local:      http://localhost:8000
echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │ IMPORTANTE                                               │
echo └──────────────────────────────────────────────────────────┘
echo.
echo   • Si el DNS no se ha propagado aún, espera 2-4 horas
echo   • Puedes verificar la propagación en: https://dnschecker.org
echo   • El túnel está corriendo en segundo plano
echo   • SSL/HTTPS está activado automáticamente por Cloudflare
echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │ VERIFICACIÓN                                             │
echo └──────────────────────────────────────────────────────────┘
echo.
echo   Verificar DNS:
echo     nslookup dvd.ch
echo.
echo   Verificar túnel:
echo     cloudflared tunnel info dvdcoin
echo.
echo   Ver logs:
echo     type cloudflare_tunnel.log
echo.
echo   Test de conectividad (cuando DNS esté propagado):
echo     curl -I https://dvd.ch
echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │ PRÓXIMOS PASOS                                           │
echo └──────────────────────────────────────────────────────────┘
echo.
echo   1. Espera a que el DNS se propague (2-4 horas normalmente)
echo   2. Prueba acceder a https://dvd.ch desde tu navegador
echo   3. Configura SSL/TLS en Cloudflare Dashboard (opcional)
echo   4. Configura reglas de firewall (opcional)
echo.
echo   Guía completa: CONFIGURAR_DVD_CH.md
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
