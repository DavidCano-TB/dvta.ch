@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔧 SOLUCIÓN COMPLETA - SISTEMA DVTA.CH
echo ═══════════════════════════════════════════════════════════════
echo.

echo DIAGNÓSTICO DEL PROBLEMA:
echo ─────────────────────────────────────────────────────────────
echo • El servidor en puerto 8000 devuelve 404 para la ruta raíz /
echo • La ruta correcta es /bank pero no hay redirección desde /
echo • El proceso Python (PID 10764) está bloqueado y requiere admin
echo.
echo SOLUCIÓN IMPLEMENTADA:
echo ─────────────────────────────────────────────────────────────
echo ✅ Agregada redirección de / a /bank en main.py
echo ✅ Importado RedirectResponse en main.py
echo ✅ Creados scripts de reinicio con privilegios admin
echo.

echo [PASO 1] Verificando estado actual...
echo.
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ⚠ Puerto 8000 ocupado por proceso protegido
    echo.
    echo OPCIONES:
    echo ─────────────────────────────────────────────────────────────
    echo.
    echo A) SOLUCIÓN RÁPIDA (sin reiniciar):
    echo    El servidor ya está corriendo. Solo necesitas:
    echo    1. Acceder a https://dvta.ch/bank (con /bank al final^)
    echo    2. O esperar a que el túnel Cloudflare redirija correctamente
    echo.
    echo B) SOLUCIÓN COMPLETA (reiniciar servidor):
    echo    1. Ejecuta: EJECUTAR_COMO_ADMIN.bat
    echo    2. Acepta el UAC (Control de Cuentas de Usuario^)
    echo    3. Luego ejecuta: REINICIAR_SERVIDOR_FORZADO.bat
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo.
    
    echo Probando si el servidor responde en /bank...
    curl -s http://localhost:8000/bank >nul 2>&1
    if not errorlevel 1 (
        echo ✅ El servidor SÍ funciona en http://localhost:8000/bank
        echo.
        echo El problema es solo la redirección de / a /bank
        echo Esto se solucionará cuando reinicies el servidor
        echo.
        echo MIENTRAS TANTO, usa estas URLs:
        echo   • http://localhost:8000/bank
        echo   • https://dvta.ch/bank
        echo.
    ) else (
        echo ❌ El servidor no responde ni en /bank
        echo DEBES reiniciar el servidor con privilegios de administrador
        echo.
    )
) else (
    echo ✅ Puerto 8000 libre
    echo.
    echo [PASO 2] Iniciando servidor...
    start "DVDBank Server" /MIN python main.py
    timeout /t 15 /nobreak >nul
    
    echo [PASO 3] Verificando...
    curl -s http://localhost:8000/ >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Servidor funcionando correctamente
        echo.
        echo URLs disponibles:
        echo   • http://localhost:8000
        echo   • http://localhost:8000/bank
        echo.
    ) else (
        echo ❌ Error al iniciar servidor
        echo.
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo  📋 RESUMEN
echo ═══════════════════════════════════════════════════════════════
echo.
echo CAMBIOS REALIZADOS EN EL CÓDIGO:
echo   ✅ main.py: Agregada ruta @app.get("/") que redirige a /bank
echo   ✅ main.py: Importado RedirectResponse
echo.
echo PARA APLICAR LOS CAMBIOS:
echo   1. Ejecuta: EJECUTAR_COMO_ADMIN.bat (mata proceso bloqueado^)
echo   2. Ejecuta: REINICIAR_SERVIDOR_FORZADO.bat (reinicia servidor^)
echo.
echo VERIFICACIÓN:
echo   • Local: http://localhost:8000 (debe redirigir a /bank^)
echo   • Public: https://dvta.ch (debe mostrar la aplicación^)
echo   • Bank: https://bank.dvta.ch (debe funcionar^)
echo.
pause
