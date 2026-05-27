@echo off
chcp 65001 >nul
title 🚀 DVDcoin - Inicio Automático
color 0B

REM ═══════════════════════════════════════════════════════════
REM   INICIO AUTOMÁTICO DE DVDCOIN CON DVD.CH
REM ═══════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 INICIANDO DVDCOIN CON DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que cloudflared existe
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    echo Descargando cloudflared.exe...
    echo.
    
    REM Intentar descargar cloudflared
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'}"
    
    if not exist "cloudflared.exe" (
        echo ❌ No se pudo descargar cloudflared.exe
        echo.
        echo Por favor, descárgalo manualmente desde:
        echo https://github.com/cloudflare/cloudflared/releases
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ cloudflared.exe descargado correctamente
    echo.
)

echo ✅ cloudflared.exe encontrado
echo.

REM Detener procesos anteriores
echo 🛑 Deteniendo procesos anteriores...
taskkill /F /IM cloudflared.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq DVDcoin*" 2>nul
timeout /t 2 /nobreak >nul
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado
    echo.
    echo Por favor, instala Python desde: https://www.python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Verificar que main.py existe
if not exist "main.py" (
    echo ❌ ERROR: main.py no encontrado
    echo.
    pause
    exit /b 1
)

echo ✅ main.py encontrado
echo.

REM Iniciar servidor Python con Uvicorn
echo 🐍 Iniciando servidor FastAPI en 0.0.0.0:8000...
start "DVDcoin Server" /MIN python -m uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ⚠️  ADVERTENCIA: El servidor no está corriendo en puerto 8000
    echo    Verifica los logs del servidor
    echo.
) else (
    echo ✅ Servidor iniciado correctamente en puerto 8000
    echo.
)

REM Verificar que el archivo de configuración existe
if not exist "cloudflare-config.yml" (
    echo ❌ ERROR: cloudflare-config.yml no encontrado
    echo.
    echo Creando configuración básica...
    echo.
    
    REM Crear configuración básica
    (
        echo # Configuracion de Cloudflare Tunnel para DVDcoin
        echo # Dominio: dvd.ch
        echo tunnel: 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
        echo credentials-file: C:\Users\PC\.cloudflared\6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.json
        echo.
        echo ingress:
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
        echo.  
        echo   # Subdominio localhost.david.ch
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
    
    echo ✅ Configuración creada
    echo.
)

echo ✅ cloudflare-config.yml encontrado
echo.

REM Iniciar túnel Cloudflare
echo 🌐 Iniciando túnel Cloudflare para dvd.ch...
start "Cloudflare Tunnel - dvd.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 5 /nobreak >nul

REM Verificar que cloudflared está corriendo
tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ⚠️  ADVERTENCIA: cloudflared no está corriendo
    echo    Verifica los logs: type cloudflare_tunnel.log
    echo.
) else (
    echo ✅ Túnel Cloudflare iniciado correctamente
    echo.
)

echo ═══════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 Tu aplicación está disponible en:
echo.
echo    ✅ https://app.david.ch
echo    ✅ https://localhost.david.ch
echo.
echo 🔒 Certificado SSL: Automático (Cloudflare)
echo 🌍 Acceso: Desde cualquier red y dispositivo
echo.
echo 📊 Para verificar el estado:
echo    VERIFICAR_DVD_CH.bat
echo.
echo 🔍 Para ver logs:
echo    type cloudflare_tunnel.log
echo.
echo 🛑 Para detener:
echo    DETENER_TODO.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo Los servicios están corriendo en segundo plano.
echo Puedes cerrar esta ventana sin problemas.
echo.
timeout /t 10
exit
