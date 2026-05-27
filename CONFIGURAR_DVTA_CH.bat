@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

cls
echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN DE TÚNEL CLOUDFLARE PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script configurará un túnel permanente de Cloudflare para dvta.ch
echo.
echo REQUISITOS:
echo   1. Tener una cuenta de Cloudflare
echo   2. El dominio dvta.ch debe estar en tu cuenta de Cloudflare
echo   3. Los nameservers deben apuntar a Cloudflare (ya configurado)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

REM Verificar que cloudflared.exe existe
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    pause
    exit /b 1
)

echo.
echo [1/5] Iniciando sesión en Cloudflare...
echo.
echo Se abrirá tu navegador para autorizar cloudflared.
echo Inicia sesión y autoriza la aplicación.
echo.
pause

cloudflared.exe tunnel login

if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo iniciar sesión en Cloudflare
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sesión iniciada correctamente
echo.

REM Verificar si el túnel ya existe
echo [2/5] Verificando túnel existente...
cloudflared.exe tunnel list | findstr "dvta-tunnel" >nul 2>&1
if errorlevel 1 (
    echo Creando nuevo túnel...
    cloudflared.exe tunnel create dvta-tunnel
    
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: No se pudo crear el túnel
        echo.
        pause
        exit /b 1
    )
    echo ✅ Túnel creado
) else (
    echo ✅ Túnel ya existe
)

echo.
echo [3/5] Obteniendo ID del túnel...

REM Obtener el ID del túnel
for /f "tokens=1" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if not defined TUNNEL_ID (
    echo ❌ ERROR: No se pudo obtener el ID del túnel
    pause
    exit /b 1
)

echo ✅ ID del túnel: %TUNNEL_ID%

echo.
echo [4/5] Configurando rutas DNS...
echo.

REM Configurar rutas DNS
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo [5/5] Creando archivo de configuración...

REM Buscar el archivo de credenciales
set CRED_FILE=
for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i

if not defined CRED_FILE (
    echo ❌ ERROR: No se encontró el archivo de credenciales
    pause
    exit /b 1
)

REM Crear archivo de configuración
(
echo tunnel: %TUNNEL_ID%
echo credentials-file: %CRED_FILE%
echo.
echo ingress:
echo   - hostname: dvta.ch
echo     service: http://127.0.0.1:8000
echo   - hostname: www.dvta.ch
echo     service: http://127.0.0.1:8000
echo   - service: http_status:404
) > cloudflare-dvta-config.yml

echo ✅ Configuración creada: cloudflare-dvta-config.yml

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Túnel ID: %TUNNEL_ID%
echo Dominios configurados:
echo   - dvta.ch
echo   - www.dvta.ch
echo.
echo IMPORTANTE: Los cambios DNS pueden tardar unos minutos en propagarse.
echo.
echo Ahora puedes:
echo   1. Ejecutar INICIAR_DVDBANK_DVTA.bat para iniciar con dvta.ch
echo   2. Configurar inicio automático con CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
pause
