@echo off
REM ============================================================
REM EJECUTAR MIGRACION COMPLETA AHORA (SIN REINICIAR)
REM ============================================================

chcp 65001 >nul
title DVDCoin - Migración a Cloudflare Tunnel
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         MIGRACION A CLOUDFLARE TUNNEL - EJECUCION AHORA      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Este script ejecutará la migración completa AHORA.
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul

REM ============================================================
REM PASO 1: VERIFICAR PYTHON
REM ============================================================
cls
echo.
echo [1/7] Verificando Python...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python NO está instalado
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
    echo ✓ %%i instalado
)

timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 2: VERIFICAR CLOUDFLARED
REM ============================================================
cls
echo.
echo [2/7] Verificando cloudflared...
echo.

cloudflared version >nul 2>&1
if errorlevel 1 (
    echo ✗ cloudflared NO está instalado
    echo.
    echo Instalando con winget...
    winget install --id Cloudflare.cloudflared --silent --accept-package-agreements --accept-source-agreements
    
    if errorlevel 1 (
        echo ✗ Error al instalar
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('cloudflared version 2^>^&1') do (
    echo ✓ %%i instalado
)

timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 3: AUTENTICAR CON CLOUDFLARE
REM ============================================================
cls
echo.
echo [3/7] Autenticar con Cloudflare...
echo.

if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ✓ Ya estás autenticado
    timeout /t 2 /nobreak >nul
    goto :skip_auth
)

echo Se abrirá tu navegador para autenticar.
echo.
echo INSTRUCCIONES:
echo   1. Inicia sesión en Cloudflare (o crea cuenta gratis)
echo   2. Autoriza el acceso
echo   3. Vuelve a esta ventana
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

cloudflared tunnel login

if errorlevel 1 (
    echo ✗ Error al autenticar
    pause
    exit /b 1
)

:skip_auth
echo ✓ Autenticación exitosa
timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 4: CREAR TUNEL
REM ============================================================
cls
echo.
echo [4/7] Crear túnel...
echo.

REM Verificar si ya existe
cloudflared tunnel list 2>nul | findstr "dvdcoin" >nul 2>&1
if not errorlevel 1 (
    echo ✓ El túnel 'dvdcoin' ya existe
    for /f "tokens=1" %%i in ('cloudflared tunnel list ^| findstr "dvdcoin" ^| findstr /v "NAME"') do (
        set TUNNEL_ID=%%i
    )
) else (
    echo Creando túnel 'dvdcoin'...
    cloudflared tunnel create dvdcoin
    
    if errorlevel 1 (
        echo ✗ Error al crear túnel
        pause
        exit /b 1
    )
    
    for /f "tokens=1" %%i in ('cloudflared tunnel list ^| findstr "dvdcoin" ^| findstr /v "NAME"') do (
        set TUNNEL_ID=%%i
    )
    echo ✓ Túnel creado
)

echo TUNNEL-ID: %TUNNEL_ID%
timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 5: CONFIGURAR DOMINIO (AUTOMATICO - SIN DOMINIO)
REM ============================================================
cls
echo.
echo [5/7] Configurar dominio...
echo.

echo Usando subdominio gratuito de Cloudflare (.trycloudflare.com)
echo ✓ No requiere configuración adicional

timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 6: CREAR ARCHIVO DE CONFIGURACION
REM ============================================================
cls
echo.
echo [6/7] Crear archivo de configuración...
echo.

if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.bak" >nul 2>&1
    echo ✓ Backup creado
)

(
echo # Configuracion de Cloudflare Tunnel para DVDcoin
echo tunnel: %TUNNEL_ID%
echo credentials-file: %USERPROFILE%\.cloudflared\%TUNNEL_ID%.json
echo.
echo ingress:
echo   - service: http://localhost:8000
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

echo ✓ cloudflare-config.yml creado

timeout /t 2 /nobreak >nul

REM ============================================================
REM PASO 7: INICIAR SERVIDOR
REM ============================================================
cls
echo.
echo [7/7] Iniciar servidor...
echo.

echo Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1

timeout /t 2 /nobreak >nul

echo Iniciando servidor Python...
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000 >server.log 2>&1

timeout /t 5 /nobreak >nul

echo Iniciando Cloudflare Tunnel...
start /B cloudflared tunnel --config cloudflare-config.yml run >cloudflare_tunnel.log 2>&1

timeout /t 5 /nobreak >nul

REM ============================================================
REM RESUMEN FINAL
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ MIGRACION COMPLETADA EXITOSAMENTE             ║
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
echo │ ACCESO PUBLICO                                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   Para ver tu URL pública, revisa:
echo   - cloudflare_tunnel.log (busca "https://")
echo   - Dashboard: https://dash.cloudflare.com
echo   - Comando: cloudflared tunnel info dvdcoin
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ VENTAJAS                                                      │
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
echo El servidor está funcionando en segundo plano.
echo.
echo Para detener: DETENER_SERVIDOR.bat
echo Para ver logs: type cloudflare_tunnel.log
echo.
pause

exit /b 0
