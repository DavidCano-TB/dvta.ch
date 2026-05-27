@echo off
REM ═══════════════════════════════════════════════════════════════
REM  SCRIPT DE PRUEBA - Actualización Automática de URL de Ngrok
REM ═══════════════════════════════════════════════════════════════

chcp 65001 >nul
title Prueba de Actualización URL Ngrok

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo   PRUEBA DE ACTUALIZACIÓN AUTOMÁTICA DE URL DE NGROK
echo ═══════════════════════════════════════════════════════════════
echo.

REM ── Paso 1: Verificar que ngrok está corriendo ──
echo [1/5] Verificando que ngrok está corriendo...
echo.

tasklist | findstr /I "ngrok.exe" >nul 2>&1
if errorlevel 1 (
    echo   ❌ Ngrok NO está corriendo
    echo.
    echo   Por favor, inicia ngrok primero con:
    echo   - ARRANCAR.bat
    echo   - O manualmente: ngrok http 8000 --domain=tu-dominio.ngrok-free.dev
    echo.
    pause
    exit /b 1
) else (
    echo   ✅ Ngrok está corriendo
)

REM ── Paso 2: Verificar panel de ngrok ──
echo.
echo [2/5] Verificando panel de ngrok...
echo.

curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    echo   ❌ No se puede acceder al panel de ngrok
    echo   Verifica: http://localhost:4040
    echo.
    pause
    exit /b 1
) else (
    echo   ✅ Panel de ngrok accesible
)

REM ── Paso 3: Mostrar URL actual de ngrok ──
echo.
echo [3/5] Obteniendo URL actual de ngrok...
echo.

for /f "delims=" %%i in ('powershell -Command "try { (Invoke-WebRequest http://localhost:4040/api/tunnels -UseBasicParsing | ConvertFrom-Json).tunnels[0].public_url } catch { '' }"') do set CURRENT_URL=%%i

if "%CURRENT_URL%"=="" (
    echo   ❌ No se pudo obtener la URL de ngrok
    echo.
    pause
    exit /b 1
) else (
    echo   ✅ URL actual: %CURRENT_URL%
)

REM ── Paso 4: Mostrar contenido actual del archivo ──
echo.
echo [4/5] Contenido actual de config\ngrok_config.txt:
echo.
echo   ┌────────────────────────────────────────────────────────────┐

if exist "config\ngrok_config.txt" (
    for /f "delims=" %%i in (config\ngrok_config.txt) do (
        echo   │ %%i
    )
) else (
    echo   │ ❌ Archivo no encontrado
)

echo   └────────────────────────────────────────────────────────────┘

REM ── Paso 5: Ejecutar actualización ──
echo.
echo [5/5] Ejecutando actualización...
echo.

python actualizar_url_ngrok.py --verbose

REM ── Resultado Final ──
echo.
echo ═══════════════════════════════════════════════════════════════
echo   CONTENIDO ACTUALIZADO
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "config\ngrok_config.txt" (
    type config\ngrok_config.txt
) else (
    echo ❌ Archivo no encontrado
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ PRUEBA COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo   La próxima vez que reinicies el servidor, la URL se
echo   actualizará automáticamente sin necesidad de este script.
echo.
echo   Archivos de documentación:
echo   - LEEME_ACTUALIZACION_URL.md
echo   - CAMBIOS_ACTUALIZACION_URL.md
echo.

pause
