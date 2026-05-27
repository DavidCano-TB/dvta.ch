@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 PASO 3: CREAR TÚNEL DE CLOUDFLARE PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script creará un túnel permanente de Cloudflare para tu dominio.
echo.
echo El túnel reemplazará completamente a ngrok y te dará:
echo   ✅ URL permanente (https://dvta.ch)
echo   ✅ No cambia al reiniciar
echo   ✅ Más rápido y estable
echo   ✅ Gratis sin límites
echo   ✅ Certificado SSL automático
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo PASO 1: Iniciar sesión en Cloudflare
echo.
echo Se abrirá tu navegador para autorizar el acceso.
echo Haz clic en "Authorize" cuando aparezca la página.
echo.
pause
echo.

cloudflared tunnel login

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error al iniciar sesión en Cloudflare
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sesión iniciada correctamente
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo PASO 2: Crear túnel "dvta-tunnel"
echo.
pause
echo.

cloudflared tunnel create dvta-tunnel

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo PASO 3: Configurar rutas DNS
echo.
pause
echo.

cloudflared tunnel route dns dvta-tunnel dvta.ch
cloudflared tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo ✅ Túnel creado y configurado
echo.
echo Ahora necesitas crear el archivo de configuración.
echo Ejecuta: python crear_config_tunnel.py
echo.
pause
