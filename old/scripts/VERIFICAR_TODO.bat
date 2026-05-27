@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICAR QUE TODO FUNCIONA CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo Verificando configuración...
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. Verificar cloudflared instalado
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ cloudflared está instalado
) else (
    echo ❌ cloudflared NO está instalado
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 2. Verificar archivo de configuración
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "cloudflare-tunnel-dvta.yml" (
    echo ✅ Archivo de configuración existe
) else (
    echo ❌ Archivo de configuración NO existe
    echo    Ejecuta: CONFIGURAR_TODO_DVTA.bat
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 3. Verificar túneles creados
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared tunnel list

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 4. Verificar servidor Python
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

curl -s http://localhost:8000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Servidor Python está corriendo en puerto 8000
) else (
    echo ❌ Servidor Python NO está corriendo
    echo    Ejecuta: ARRANCAR.bat o INICIAR_SISTEMA_COMPLETO.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Si todo está ✅, puedes iniciar el túnel con:
echo    INICIAR_TUNNEL_DVTA.bat
echo.
echo Luego abre tu navegador y ve a:
echo    https://dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
