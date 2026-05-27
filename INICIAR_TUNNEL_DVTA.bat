@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🌐 INICIANDO TÚNEL DE CLOUDFLARE PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Tu sitio estará disponible en: https://dvta.ch
echo.
echo ⚠️  NO CIERRES ESTA VENTANA - El túnel debe estar siempre activo
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Verificar que existe el archivo de configuración
if not exist "cloudflare-tunnel-dvta.yml" (
    echo ❌ Error: No se encontró cloudflare-tunnel-dvta.yml
    echo.
    echo Ejecuta primero: PASO_3_CREAR_TUNNEL.bat
    echo.
    pause
    exit /b 1
)

REM Verificar que cloudflared.exe existe
if not exist "cloudflared.exe" (
    echo ❌ Error: No se encontró cloudflared.exe
    echo.
    echo Descarga desde: https://github.com/cloudflare/cloudflared/releases
    echo Guarda como: c:\dvdcoin\cloudflared.exe
    echo.
    pause
    exit /b 1
)

REM Iniciar el túnel
cloudflared.exe tunnel --config cloudflare-tunnel-dvta.yml run

pause
