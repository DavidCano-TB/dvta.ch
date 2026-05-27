@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN COMPLETA DE dvta.ch CON CLOUDFLARE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script configurará TODO automáticamente:
echo   1. Verificar cloudflared instalado
echo   2. Iniciar sesión en Cloudflare
echo   3. Crear túnel "dvta-tunnel"
echo   4. Configurar DNS automáticamente
echo   5. Crear archivo de configuración
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Verificar cloudflared
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared --version

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ cloudflared no está instalado
    echo.
    echo Para instalarlo:
    echo 1. Ve a: https://github.com/cloudflare/cloudflared/releases
    echo 2. Descarga: cloudflared-windows-amd64.exe
    echo 3. Renómbralo a: cloudflared.exe
    echo 4. Muévelo a: C:\Windows\System32\
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ cloudflared está instalado
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Iniciar sesión en Cloudflare
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Se abrirá tu navegador. Haz clic en "Authorize" para continuar.
echo.
pause

cloudflared tunnel login

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error al iniciar sesión
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sesión iniciada correctamente
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Crear túnel "dvta-tunnel"
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel create dvta-tunnel

echo.
echo ✅ Túnel creado
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4: Configurar DNS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel route dns dvta-tunnel dvta.ch
cloudflared tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo ✅ DNS configurado
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 5: Crear archivo de configuración
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python crear_config_tunnel.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Tu túnel está listo para usar.
echo.
echo Para iniciar el túnel, ejecuta:
echo    INICIAR_TUNNEL_DVTA.bat
echo.
echo Tu sitio estará disponible en:
echo    https://dvta.ch
echo    https://www.dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
