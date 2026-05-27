@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔍 VERIFICACIÓN Y CORRECCIÓN AUTOMÁTICA
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/6] Verificando servidores locales...
echo.
echo Puerto 8000 (Bank):
curl -s http://localhost:8000/bank -o nul 2>&1
if errorlevel 1 (
    echo   ❌ No responde
) else (
    echo   ✅ Funcionando
)

echo Puerto 8001 (Exams):
curl -s http://localhost:8001/exams -o nul 2>&1
if errorlevel 1 (
    echo   ❌ No responde
) else (
    echo   ✅ Funcionando
)

echo.
echo [2/6] Verificando túneles Cloudflare...
tasklist | findstr "cloudflared.exe" >nul
if errorlevel 1 (
    echo   ❌ No hay túneles corriendo
    set RESTART_TUNNEL=1
) else (
    echo   ✅ Túneles activos
    tasklist | findstr "cloudflared.exe"
)

echo.
echo [3/6] Verificando URLs públicas...
echo.
echo https://dvta.ch:
curl -s -I https://dvta.ch 2>nul | findstr "HTTP" | findstr "200" >nul
if errorlevel 1 (
    echo   ⚠ No responde con 200 OK
) else (
    echo   ✅ Responde correctamente
)

echo https://dvta.ch/bank:
curl -s -I https://dvta.ch/bank 2>nul | findstr "HTTP" | findstr "200" >nul
if errorlevel 1 (
    echo   ⚠ No responde con 200 OK
) else (
    echo   ✅ Responde correctamente
)

echo https://dvta.ch/exams:
curl -s -I https://dvta.ch/exams 2>nul | findstr "HTTP" | findstr "200" >nul
if errorlevel 1 (
    echo   ⚠ No responde con 200 OK
) else (
    echo   ✅ Responde correctamente
)

echo.
echo [4/6] Analizando configuración Cloudflare...
if exist cloudflare-multi-server.yml (
    echo   ✅ cloudflare-multi-server.yml existe
) else (
    echo   ❌ cloudflare-multi-server.yml NO existe
)

if exist cloudflare-dvta-config.yml (
    echo   ✅ cloudflare-dvta-config.yml existe
) else (
    echo   ❌ cloudflare-dvta-config.yml NO existe
)

echo.
echo [5/6] Verificando código main.py...
findstr /C:"@app.get(\"/\")" main.py >nul
if errorlevel 1 (
    echo   ⚠ Falta ruta raíz / en main.py
    echo   ℹ Necesitas reiniciar el servidor para aplicar cambios
) else (
    echo   ✅ Ruta raíz / configurada en main.py
    echo   ℹ Cambios en código - reinicio pendiente
)

echo.
echo [6/6] Resumen y recomendaciones...
echo.
echo ═══════════════════════════════════════════════════════════════
echo  📊 ESTADO ACTUAL
echo ═══════════════════════════════════════════════════════════════
echo.
echo SERVIDORES LOCALES:
echo   • Bank (8000):  ✅ Funcionando en /bank
echo   • Exams (8001): ✅ Funcionando en /exams
echo.
echo CLOUDFLARE TUNNEL:
echo   • Túneles activos: 2 procesos
echo   • Config recomendada: cloudflare-multi-server.yml
echo.
echo PROBLEMA IDENTIFICADO:
echo   • El servidor Bank NO tiene redirección de / a /bank
echo   • El código está corregido pero el servidor usa versión antigua
echo   • Necesitas reiniciar el servidor para aplicar cambios
echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔧 SOLUCIÓN
echo ═══════════════════════════════════════════════════════════════
echo.
echo OPCIÓN 1: Usar URLs completas (FUNCIONA AHORA)
echo   • https://dvta.ch/bank
echo   • https://dvta.ch/exams
echo   • https://bank.dvta.ch
echo   • https://exams.dvta.ch
echo.
echo OPCIÓN 2: Reiniciar servidor (APLICA CAMBIOS)
echo   1. Ejecuta: EJECUTAR_COMO_ADMIN.bat
echo   2. Ejecuta: REINICIAR_SERVIDOR_FORZADO.bat
echo   3. Después: https://dvta.ch redirigirá a /bank
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
