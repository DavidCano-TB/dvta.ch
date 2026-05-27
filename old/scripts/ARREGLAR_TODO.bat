@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 ARREGLAR TODOS LOS PROBLEMAS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script corregirá TODOS los problemas y te dará 2 soluciones:
echo.
echo   SOLUCIÓN A: URL temporal que funciona AHORA (mientras DNS propaga)
echo   SOLUCIÓN B: Túnel permanente para dvta.ch (cuando DNS propague)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Qué quieres hacer?
echo.
echo   1. Solución RÁPIDA: Dame una URL que funcione AHORA (recomendado)
echo   2. Solución COMPLETA: Arreglar autenticación y crear túnel nuevo
echo   3. Ambas: URL temporal AHORA + túnel permanente para después
echo   4. Salir
echo.
set /p opcion="Elige (1-4): "

if "%opcion%"=="1" goto rapida
if "%opcion%"=="2" goto completa
if "%opcion%"=="3" goto ambas
if "%opcion%"=="4" goto salir

echo.
echo ❌ Opción inválida
pause
exit /b 1

:rapida
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ⚡ SOLUCIÓN RÁPIDA - URL TEMPORAL
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Verificando que el servidor Python esté corriendo...
echo.

curl -s http://localhost:8000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ El servidor Python NO está corriendo
    echo.
    echo Iniciando servidor Python...
    start "Python Server" cmd /k "cd /d c:\dvdcoin && python main.py"
    echo.
    echo ⏱️  Esperando 5 segundos...
    timeout /t 5 /nobreak >nul
)

echo ✅ Servidor Python corriendo
echo.
echo Generando URL temporal de Cloudflare...
echo.
echo ⚠️  Se abrirá una nueva ventana con tu URL
echo ⚠️  NO CIERRES ESA VENTANA
echo.
pause

start "Cloudflare Quick Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ✅ URL temporal generada
echo.
echo Mira la ventana que se abrió para ver tu URL.
echo Busca una línea como:
echo    https://xxxxx-xxxxx-xxxxx.trycloudflare.com
echo.
echo Esa es tu URL temporal que funciona AHORA.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
goto fin

:completa
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 SOLUCIÓN COMPLETA - TÚNEL PERMANENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
call CREAR_TUNNEL_NUEVO.bat
goto fin

:ambas
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 AMBAS SOLUCIONES
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo PASO 1: Crear URL temporal (funciona AHORA)
echo.
pause

REM Verificar servidor Python
curl -s http://localhost:8000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando servidor Python...
    start "Python Server" cmd /k "cd /d c:\dvdcoin && python main.py"
    timeout /t 5 /nobreak >nul
)

echo Generando URL temporal...
start "Cloudflare Quick Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo.
echo ✅ URL temporal generada (mira la ventana que se abrió)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo PASO 2: Crear túnel permanente para dvta.ch
echo.
pause

call CREAR_TUNNEL_NUEVO.bat

goto fin

:salir
echo.
echo Adiós!
exit /b 0

:fin
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
