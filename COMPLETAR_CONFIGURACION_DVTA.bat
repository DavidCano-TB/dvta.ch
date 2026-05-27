@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  COMPLETANDO CONFIGURACIÓN DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Esperando autorización de Cloudflare...
echo.
echo Si no se abrió el navegador, ve a:
echo https://dash.cloudflare.com/argotunnel
echo.
echo Completa la autorización y presiona cualquier tecla aquí...
pause >nul

echo.
echo Verificando autorización...
timeout /t 5 /nobreak >nul

REM Verificar si el certificado existe
if not exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ❌ Autorización no completada
    echo.
    echo Por favor completa la autorización en el navegador y ejecuta este script de nuevo.
    pause
    exit /b 1
)

echo ✅ Autorización completada
echo.

REM Crear túnel
echo Creando túnel dvta-tunnel...
cloudflared.exe tunnel create dvta-tunnel

if errorlevel 1 (
    echo ⚠ El túnel puede ya existir, continuando...
)

echo.
echo Configurando DNS...
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo Obteniendo información del túnel...
for /f "tokens=1" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if not defined TUNNEL_ID (
    echo ❌ No se pudo obtener el ID del túnel
    pause
    exit /b 1
)

echo ✅ ID del túnel: %TUNNEL_ID%

REM Buscar credenciales
for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i

if not defined CRED_FILE (
    echo ❌ No se encontraron credenciales
    pause
    exit /b 1
)

echo ✅ Credenciales: %CRED_FILE%

REM Crear configuración
echo.
echo Creando archivo de configuración...
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

echo ✅ Configuración creada

REM Detener procesos actuales
echo.
echo Deteniendo procesos actuales...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 3 /nobreak >nul

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Túnel ID: %TUNNEL_ID%
echo Dominios: dvta.ch, www.dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO SISTEMA CON dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

call INICIAR_DVDBANK_DVTA.bat
