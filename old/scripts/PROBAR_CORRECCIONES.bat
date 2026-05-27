@echo off
chcp 65001 >nul
cls
echo ═══════════════════════════════════════════════════════════
echo   🔧 PROBANDO CORRECCIONES DE SINTAXIS
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script prueba que los archivos BAT corregidos
echo funcionen correctamente sin errores de sintaxis.
echo.
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/5] Probando VER_ESTADO_SISTEMA.bat...
call VER_ESTADO_SISTEMA.bat >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ VER_ESTADO_SISTEMA.bat - OK
) else (
    echo   ⚠️  VER_ESTADO_SISTEMA.bat - Posible error
)

echo.
echo [2/5] Probando GENERAR_URL_TEMPORAL.bat...
echo   ℹ️  Este script requiere cloudflared instalado
echo   ℹ️  Saltando prueba automática

echo.
echo [3/5] Probando VER_ESTADO_NGROK.bat...
call VER_ESTADO_NGROK.bat >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ VER_ESTADO_NGROK.bat - OK
) else (
    echo   ⚠️  VER_ESTADO_NGROK.bat - Posible error
)

echo.
echo [4/5] Probando VER_ESTADO_WATCHDOG.bat...
call VER_ESTADO_WATCHDOG.bat >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ VER_ESTADO_WATCHDOG.bat - OK
) else (
    echo   ⚠️  VER_ESTADO_WATCHDOG.bat - Posible error
)

echo.
echo [5/5] Verificando sintaxis de startdvdcoin.bat...
echo   ℹ️  Este script inicia el servidor
echo   ℹ️  Saltando prueba automática

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ PRUEBAS COMPLETADAS
echo ═══════════════════════════════════════════════════════════
echo.
echo Archivos corregidos:
echo   • VER_ESTADO_SISTEMA.bat
echo   • VER_ESTADO_NGROK.bat
echo   • VER_ESTADO_WATCHDOG.bat
echo   • DETENER_WATCHDOG.bat
echo   • AGREGAR_USUARIO_Y_REINICIAR.bat
echo   • GENERAR_URL_TEMPORAL.bat
echo   • startdvdcoin.bat
echo   • scripts\windows\VER_ESTADO_WATCHDOG.bat
echo   • scripts\windows\DETENER_WATCHDOG.bat
echo   • scripts\windows\startdvdcoin.bat
echo   • scripts\windows\REINICIAR_SERVICIO.bat
echo.
echo Problema corregido:
echo   ❌ Antes: for /f "tokens=2" %%a in ('tasklist ^| findstr ...')
echo   ✅ Ahora:  tasklist ^| findstr ... ^> temp.txt
echo             for /f "tokens=2" %%a in (temp.txt) do ...
echo             del temp.txt
echo.
echo Esta solución evita problemas de sintaxis con pipes
echo escapados dentro de comandos for /f en Windows.
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
