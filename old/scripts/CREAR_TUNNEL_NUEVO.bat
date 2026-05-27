@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 CORREGIR AUTENTICACIÓN Y CREAR TÚNEL NUEVO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Voy a corregir los problemas de autenticación.
echo.
pause

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Eliminar credenciales antiguas
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo Eliminando cert.pem antiguo...
    del "%USERPROFILE%\.cloudflared\cert.pem"
    echo ✅ Eliminado
) else (
    echo ℹ️  No hay cert.pem antiguo
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Iniciar sesión de nuevo
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Se abrirá tu navegador. Haz clic en "Authorize".
echo.
pause

cloudflared tunnel login

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error al iniciar sesión
    pause
    exit /b 1
)

echo.
echo ✅ Sesión iniciada correctamente
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Eliminar túnel antiguo (si existe)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel delete dvta-tunnel

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4: Crear túnel nuevo
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel create dvta-tunnel

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error al crear túnel
    pause
    exit /b 1
)

echo.
echo ✅ Túnel creado correctamente
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 5: Configurar DNS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel route dns dvta-tunnel dvta.ch
cloudflared tunnel route dns dvta-tunnel www.dvta.ch

echo.
echo ✅ DNS configurado
echo.

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 6: Crear archivo de configuración
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python crear_config_tunnel.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ TÚNEL CORREGIDO Y LISTO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Ahora puedes iniciar el túnel con:
echo    INICIAR_TUNNEL_DVTA.bat
echo.
pause
