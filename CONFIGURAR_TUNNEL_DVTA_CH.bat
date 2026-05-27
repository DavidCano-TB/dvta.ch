@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN CLOUDFLARE TUNNEL PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Verificar que cloudflared existe
if not exist "cloudflared.exe" (
    echo ERROR: cloudflared.exe no encontrado
    echo.
    echo Descarga cloudflared desde:
    echo https://github.com/cloudflare/cloudflared/releases
    echo.
    pause
    exit /b 1
)

echo [1/4] Creando túnel 'dvta-tunnel'...
echo.
cloudflared.exe tunnel create dvta-tunnel

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear el túnel
    echo.
    echo Posibles causas:
    echo - No has autorizado el túnel en el navegador
    echo - Ya existe un túnel con ese nombre
    echo.
    echo Si ya existe, puedes listar los túneles con:
    echo   cloudflared tunnel list
    echo.
    pause
    exit /b 1
)

echo.
echo [2/4] Configurando rutas DNS...
echo.
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo [3/4] Obteniendo información del túnel...
echo.

REM Obtener el ID del túnel
for /f "tokens=*" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do (
    set TUNNEL_LINE=%%i
)

REM Extraer el ID del túnel (primera columna)
for /f "tokens=1" %%a in ("!TUNNEL_LINE!") do (
    set TUNNEL_ID=%%a
)

if not defined TUNNEL_ID (
    echo ERROR: No se pudo obtener el ID del túnel
    echo.
    echo Ejecuta manualmente:
    echo   cloudflared tunnel list
    echo.
    pause
    exit /b 1
)

echo Tunnel ID: !TUNNEL_ID!

REM Ruta del archivo de credenciales
set CREDS_FILE=%USERPROFILE%\.cloudflared\!TUNNEL_ID!.json

if not exist "!CREDS_FILE!" (
    echo ERROR: Archivo de credenciales no encontrado
    echo Esperado en: !CREDS_FILE!
    echo.
    pause
    exit /b 1
)

echo Credenciales: !CREDS_FILE!

echo.
echo [4/4] Actualizando archivo de configuración...

REM Crear archivo de configuración actualizado
(
echo tunnel: !TUNNEL_ID!
echo credentials-file: !CREDS_FILE!
echo.
echo ingress:
echo   - hostname: dvta.ch
echo     service: http://127.0.0.1:8000
echo     originRequest:
echo       noTLSVerify: true
echo       connectTimeout: 60s
echo       httpHostHeader: dvta.ch
echo.
echo   - hostname: www.dvta.ch
echo     service: http://127.0.0.1:8000
echo     originRequest:
echo       noTLSVerify: true
echo       connectTimeout: 60s
echo       httpHostHeader: www.dvta.ch
echo.
echo   - service: http_status:404
echo.
echo metrics: 127.0.0.1:2000
echo loglevel: info
echo protocol: quic
) > cloudflare-dvta-config.yml

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Tunnel ID:    !TUNNEL_ID!
echo Credenciales: !CREDS_FILE!
echo.
echo Rutas DNS configuradas:
echo   • dvta.ch      → http://localhost:8000
echo   • www.dvta.ch  → http://localhost:8000
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  🚀 PRÓXIMO PASO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Ejecuta: INICIAR_DVDBANK_TUNNEL.bat
echo.
echo O configura inicio automático: CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
pause
