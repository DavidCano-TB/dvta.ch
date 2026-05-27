@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════════════════════
echo  FINALIZANDO CONFIGURACIÓN DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════

REM Verificar certificado
if not exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ❌ Certificado no encontrado
    exit /b 1
)

echo ✅ Certificado encontrado

REM Crear túnel
echo.
echo Creando túnel dvta-tunnel...
cloudflared.exe tunnel create dvta-tunnel 2>nul
echo ✅ Túnel creado o ya existe

REM Configurar DNS
echo.
echo Configurando DNS...
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch 2>nul
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch 2>nul
echo ✅ DNS configurado

REM Obtener ID del túnel
echo.
echo Obteniendo información del túnel...
for /f "tokens=1" %%i in ('cloudflared.exe tunnel list 2^>nul ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if not defined TUNNEL_ID (
    echo ❌ No se pudo obtener el ID del túnel
    exit /b 1
)

echo ✅ ID del túnel: %TUNNEL_ID%

REM Buscar credenciales
for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i

if not defined CRED_FILE (
    echo ❌ No se encontraron credenciales
    exit /b 1
)

echo ✅ Credenciales encontradas

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

echo ✅ Configuración creada: cloudflare-dvta-config.yml

REM Detener procesos actuales
echo.
echo Deteniendo procesos actuales...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Túnel ID: %TUNNEL_ID%
echo Dominios: dvta.ch, www.dvta.ch
echo Config: cloudflare-dvta-config.yml
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO SISTEMA CON dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

call INICIAR_DVDBANK_DVTA.bat
