@echo off
REM ============================================================
REM DVDCOIN BANK - ASISTENTE DE CONFIGURACION CLOUDFLARE TUNNEL
REM Guia paso a paso para configurar Cloudflare Tunnel
REM ============================================================

chcp 65001 >nul
title DVDCoin Bank - Configurar Cloudflare Tunnel
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║      ASISTENTE DE CONFIGURACION - CLOUDFLARE TUNNEL          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM PASO 1: VERIFICAR CLOUDFLARED
REM ============================================================
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PASO 1: Verificar cloudflared                                │
echo └──────────────────────────────────────────────────────────────┘
echo.

cloudflared version >nul 2>&1
if errorlevel 1 (
    echo ✗ cloudflared NO está instalado
    echo.
    echo Opciones de instalación:
    echo.
    echo   1. Descarga manual:
    echo      https://github.com/cloudflare/cloudflared/releases/latest
    echo      Descarga: cloudflared-windows-amd64.exe
    echo      Renombra a: cloudflared.exe
    echo      Mueve a: c:\dvdcoin\cloudflared.exe
    echo.
    echo   2. Con winget (Windows 10/11):
    echo      winget install --id Cloudflare.cloudflared
    echo.
    echo Después de instalar, ejecuta este script nuevamente.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('cloudflared version 2^>^&1') do (
        echo ✓ cloudflared instalado: %%i
    )
)

echo.
pause

REM ============================================================
REM PASO 2: AUTENTICAR CON CLOUDFLARE
REM ============================================================
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PASO 2: Autenticar con Cloudflare                            │
echo └──────────────────────────────────────────────────────────────┘
echo.

REM Verificar si ya está autenticado
if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ✓ Ya estás autenticado con Cloudflare
    echo.
    echo ¿Quieres volver a autenticar? (S/N)
    set /p REAUTH="> "
    if /i not "%REAUTH%"=="S" goto :skip_auth
)

echo Abriendo navegador para autenticar...
echo.
echo INSTRUCCIONES:
echo   1. Se abrirá tu navegador
echo   2. Inicia sesión en Cloudflare (o crea una cuenta gratis)
echo   3. Autoriza el acceso
echo   4. Vuelve a esta ventana
echo.
pause

cloudflared tunnel login

if errorlevel 1 (
    echo.
    echo ✗ Error al autenticar
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Autenticación exitosa
echo.

:skip_auth
pause

REM ============================================================
REM PASO 3: CREAR TUNEL
REM ============================================================
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PASO 3: Crear túnel                                          │
echo └──────────────────────────────────────────────────────────────┘
echo.

REM Verificar si ya existe el túnel
cloudflared tunnel list 2>nul | findstr "dvdcoin" >nul 2>&1
if not errorlevel 1 (
    echo ✓ El túnel 'dvdcoin' ya existe
    echo.
    echo Información del túnel:
    cloudflared tunnel list | findstr "dvdcoin"
    echo.
    echo ¿Quieres crear un nuevo túnel? (S/N)
    set /p NEWTUNNEL="> "
    if /i not "%NEWTUNNEL%"=="S" goto :skip_create
)

echo Creando túnel 'dvdcoin'...
echo.

cloudflared tunnel create dvdcoin

if errorlevel 1 (
    echo.
    echo ✗ Error al crear el túnel
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Túnel creado exitosamente
echo.

:skip_create

REM Obtener el TUNNEL-ID
for /f "tokens=1" %%i in ('cloudflared tunnel list ^| findstr "dvdcoin" ^| findstr /v "NAME"') do (
    set TUNNEL_ID=%%i
)

if "%TUNNEL_ID%"=="" (
    echo ✗ No se pudo obtener el TUNNEL-ID
    echo.
    echo Ejecuta manualmente:
    echo   cloudflared tunnel list
    echo.
    pause
    exit /b 1
)

echo TUNNEL-ID: %TUNNEL_ID%
echo.
echo ⚠ IMPORTANTE: Guarda este ID en un lugar seguro
echo.

pause

REM ============================================================
REM PASO 4: CONFIGURAR ARCHIVO YML
REM ============================================================
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PASO 4: Configurar archivo cloudflare-config.yml             │
echo └──────────────────────────────────────────────────────────────┘
echo.

echo ¿Tienes un dominio propio? (S/N)
set /p HAS_DOMAIN="> "

if /i "%HAS_DOMAIN%"=="S" (
    echo.
    echo Ingresa tu dominio (ej: midominio.com):
    set /p DOMAIN="> "
    set HOSTNAME=dvdcoin.%DOMAIN%
) else (
    echo.
    echo Se usará un subdominio de Cloudflare (.trycloudflare.com)
    set HOSTNAME=
)

echo.
echo Actualizando cloudflare-config.yml...

REM Crear backup del archivo original
if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.bak" >nul 2>&1
)

REM Crear nuevo archivo de configuración
(
echo # Configuracion de Cloudflare Tunnel para DVDcoin
echo tunnel: %TUNNEL_ID%
echo credentials-file: %USERPROFILE%\.cloudflared\%TUNNEL_ID%.json
echo.
echo ingress:
if not "%HOSTNAME%"=="" (
    echo   - hostname: %HOSTNAME%
)
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

echo ✓ Archivo cloudflare-config.yml actualizado
echo.

pause

REM ============================================================
REM PASO 5: CONFIGURAR DNS (SI TIENE DOMINIO)
REM ============================================================
if /i "%HAS_DOMAIN%"=="S" (
    echo.
    echo ┌──────────────────────────────────────────────────────────────┐
    echo │ PASO 5: Configurar DNS                                        │
    echo └──────────────────────────────────────────────────────────────┘
    echo.
    
    echo ¿Tu dominio ya está en Cloudflare? (S/N)
    set /p DOMAIN_IN_CF="> "
    
    if /i "%DOMAIN_IN_CF%"=="N" (
        echo.
        echo INSTRUCCIONES:
        echo   1. Ve a: https://dash.cloudflare.com
        echo   2. Click en "Add a Site"
        echo   3. Ingresa tu dominio: %DOMAIN%
        echo   4. Sigue las instrucciones para cambiar los nameservers
        echo   5. Espera a que se active (puede tardar hasta 24 horas)
        echo.
        echo Cuando tu dominio esté activo en Cloudflare, ejecuta:
        echo   cloudflared tunnel route dns dvdcoin %HOSTNAME%
        echo.
    ) else (
        echo.
        echo Configurando DNS...
        cloudflared tunnel route dns dvdcoin %HOSTNAME%
        
        if errorlevel 1 (
            echo.
            echo ✗ Error al configurar DNS
            echo.
            echo Configura manualmente:
            echo   cloudflared tunnel route dns dvdcoin %HOSTNAME%
            echo.
        ) else (
            echo.
            echo ✓ DNS configurado exitosamente
            echo.
        )
    )
    
    pause
)

REM ============================================================
REM RESUMEN FINAL
REM ============================================================
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ CONFIGURACION COMPLETADA                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ RESUMEN                                                       │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   Túnel ID:     %TUNNEL_ID%
if not "%HOSTNAME%"=="" (
    echo   URL pública:  https://%HOSTNAME%
) else (
    echo   URL pública:  Se asignará automáticamente
)
echo   Config:       cloudflare-config.yml
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PROXIMOS PASOS                                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   1. Inicia el servidor:
echo      INICIAR_CON_CLOUDFLARE.bat
echo.
echo   2. Verifica que funciona:
if not "%HOSTNAME%"=="" (
    echo      https://%HOSTNAME%
) else (
    echo      Revisa cloudflare_tunnel.log para ver la URL
)
echo.
echo   3. Para detener:
echo      DETENER_SERVIDOR.bat
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ¿Quieres iniciar el servidor ahora? (S/N)
set /p START_NOW="> "

if /i "%START_NOW%"=="S" (
    echo.
    echo Iniciando servidor...
    call INICIAR_CON_CLOUDFLARE.bat
) else (
    echo.
    echo Para iniciar el servidor más tarde, ejecuta:
    echo   INICIAR_CON_CLOUDFLARE.bat
    echo.
    pause
)
