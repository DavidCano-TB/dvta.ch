@echo off
chcp 65001 >nul
title Arrancar Todo en Paralelo - DVDcoin
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 ARRANCAR TODO EN PARALELO - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/4] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

echo [2/4] Iniciando Exams Server (Puerto 8001)...
start "DVDcoin Exams" cmd /c "cd modules\exams && python start_exams.py"
timeout /t 5 /nobreak >nul
echo      ✅ Exams iniciado
echo.

echo [3/4] Iniciando Cloudflare Tunnel...
start "Cloudflare Tunnel" cmd /c "cloudflared tunnel --config cloudflare-dvta-config.yml run"
timeout /t 5 /nobreak >nul
echo      ✅ Tunnel iniciado
echo.

echo [4/4] Verificando servicios...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 activo
) else (
    echo      ❌ Puerto 8001 no responde
)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo
) else (
    echo      ❌ Cloudflare Tunnel no activo
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 URLs disponibles:
echo   • https://dvta.ch/exams
echo   • https://dvta.ch/opo
echo   • https://dvta.ch/health
echo.
echo ⏱️  Espera 10-30 segundos para que se propague
echo.
echo 💡 Ventanas abiertas:
echo   • DVDcoin Exams - Servidor Exams
echo   • Cloudflare Tunnel - Túnel Cloudflare
echo.
echo ⚠️  NO CIERRES estas ventanas mientras uses el sistema
echo.
pause
