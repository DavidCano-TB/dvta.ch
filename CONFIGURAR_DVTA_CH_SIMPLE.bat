@echo off
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURAR dvta.ch - MÉTODO SIMPLE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este método usa el dashboard web de Cloudflare (más fácil y visual).
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

REM Eliminar certificado antiguo si existe
del "%USERPROFILE%\.cloudflared\cert.pem" >nul 2>&1

echo.
echo [1/3] Abriendo login de Cloudflare...
echo.
echo Se abrirá tu navegador. Autoriza cloudflared y cierra la pestaña.
echo.
pause

cloudflared.exe tunnel login

if errorlevel 1 (
    echo.
    echo ⚠ Si hubo un error, usa el método del dashboard:
    echo   ABRIR_CLOUDFLARE_DASHBOARD.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Login exitoso
echo.

echo [2/3] Creando túnel...
echo.

cloudflared.exe tunnel create dvta-tunnel

if errorlevel 1 (
    echo.
    echo ⚠ El túnel puede ya existir. Continuando...
    echo.
)

echo [3/3] Configurando DNS...
echo.

cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo Creando archivo de configuración...

REM Obtener ID del túnel
for /f "tokens=1" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if defined TUNNEL_ID (
    REM Buscar credenciales
    for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i
    
    if defined CRED_FILE (
        REM Crear config
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
        
        echo.
        echo ✅ Configuración completada
        echo.
        echo Túnel ID: %TUNNEL_ID%
        echo Config: cloudflare-dvta-config.yml
        echo.
        echo Ahora ejecuta: INICIAR_DVDBANK_DVTA.bat
        echo.
    )
)

pause
