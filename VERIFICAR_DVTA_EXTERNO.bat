@echo off
chcp 65001 >nul
title Verificar dvta.ch Externo
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🌐 VERIFICACIÓN EXTERNA - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/4] Verificando servidor local en puerto 8001...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 activo
) else (
    echo      ❌ Puerto 8001 no responde
    echo      Ejecuta: ARRANCAR_DVTA_COMPLETO.bat
    pause
    exit /b 1
)
echo.

echo [2/4] Verificando Cloudflare Tunnel...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo
) else (
    echo      ❌ Cloudflare Tunnel no está corriendo
    pause
    exit /b 1
)
echo.

echo [3/4] Probando rutas locales...
echo      • http://localhost:8001/health
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo        ✅ Health check OK
) else (
    echo        ❌ Health check falló
)

echo      • http://localhost:8001/exams
curl -s http://localhost:8001/exams >nul 2>&1
if %errorlevel% equ 0 (
    echo        ✅ Exams OK
) else (
    echo        ❌ Exams falló
)

echo      • http://localhost:8001/opo
curl -s http://localhost:8001/opo >nul 2>&1
if %errorlevel% equ 0 (
    echo        ✅ OPO OK
) else (
    echo        ❌ OPO falló
)
echo.

echo [4/4] Instrucciones para verificar externamente...
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🌐 PRUEBA ESTAS URLs EN TU NAVEGADOR:
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   1. https://dvta.ch/exams
echo      → Debe mostrar la página principal de Exams
echo.
echo   2. https://dvta.ch/opo
echo      → Debe mostrar la lista de oposiciones
echo.
echo   3. https://dvta.ch/health
echo      → Debe mostrar: {"status":"healthy","service":"DVDcoin Exams",...}
echo.
echo   4. https://dvta.ch/
echo      → Debe redirigir automáticamente a /exams
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ⏱️  NOTA: Espera 10-30 segundos después de reiniciar para que se propague
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo ¿Quieres abrir las URLs en el navegador? (S/N)
set /p respuesta=
if /i "%respuesta%"=="S" (
    start https://dvta.ch/exams
    timeout /t 2 /nobreak >nul
    start https://dvta.ch/opo
    timeout /t 2 /nobreak >nul
    start https://dvta.ch/health
)

echo.
pause
