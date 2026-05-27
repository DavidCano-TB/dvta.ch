@echo off
chcp 65001 >nul
title Verificar Sistema - DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN DEL SISTEMA - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/5] Verificando puerto 8001...
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 ACTIVO
) else (
    echo      ❌ Puerto 8001 NO ACTIVO
    echo      Ejecuta: ARRANCAR_TODO_PARALELO.bat
)
echo.

echo [2/5] Verificando Cloudflare Tunnel...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel ACTIVO
) else (
    echo      ❌ Cloudflare Tunnel NO ACTIVO
    echo      Ejecuta: ARRANCAR_TODO_PARALELO.bat
)
echo.

echo [3/5] Probando endpoint /health...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor respondiendo
) else (
    echo      ❌ Servidor no responde
)
echo.

echo [4/5] Probando endpoint /opo...
curl -s http://localhost:8001/opo >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Ruta /opo funcionando
) else (
    echo      ❌ Ruta /opo no funciona
)
echo.

echo [5/5] Probando endpoint /exams...
curl -s http://localhost:8001/exams >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Ruta /exams funcionando
) else (
    echo      ❌ Ruta /exams no funciona
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Procesos Python:
tasklist | findstr "python.exe"
echo.
echo Procesos Cloudflare:
tasklist | findstr "cloudflared.exe"
echo.
echo Puertos escuchando:
netstat -ano | findstr ":800" | findstr "LISTENING"
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 Prueba en tu navegador:
echo   • https://dvta.ch/exams
echo   • https://dvta.ch/opo
echo.
pause
