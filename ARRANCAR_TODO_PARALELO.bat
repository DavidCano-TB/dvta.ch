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

echo [1/5] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

echo [2/5] Iniciando Bank Server principal (Puerto 8000)...
start "DVDcoin Bank Main" cmd /c "python main.py"
timeout /t 3 /nobreak >nul
echo      ✅ Bank principal iniciado
echo.

echo [3/5] Iniciando Bank Panel Server (Puerto 8002)...
start "DVDcoin Bank Panel" cmd /c "python modules\bank\app_bank.py"
timeout /t 3 /nobreak >nul
echo      ✅ Bank Panel iniciado
echo.

echo [4/5] Iniciando Exams Server (Puerto 8001)...
start "DVDcoin Exams" cmd /c "python modules\exams\app_exams.py"
timeout /t 5 /nobreak >nul
echo      ✅ Exams iniciado
echo.

echo [5/5] Iniciando Cloudflare Tunnel...
start "Cloudflare Tunnel" cmd /c "cloudflared tunnel --config cloudflare-dvta-config.yml run"
timeout /t 5 /nobreak >nul
echo      ✅ Tunnel iniciado
echo.

echo ─── Verificando servicios ───
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8000 activo - Bank principal) else (echo      ❌ Puerto 8000 no responde)

netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8001 activo - Exams) else (echo      ❌ Puerto 8001 no responde)

netstat -ano | findstr ":8002" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8002 activo - Bank Panel) else (echo      ❌ Puerto 8002 no responde)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Cloudflare Tunnel activo) else (echo      ❌ Cloudflare Tunnel no activo)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 URLs disponibles:
echo   • https://dvta.ch/        → Exams (home)
echo   • https://dvta.ch/exams   → Exams
echo   • https://dvta.ch/opo     → Panel OPO
echo   • https://dvta.ch/bank    → Panel Bank ^(NUEVO, puerto 8002^)
echo   • https://dvta.ch/health  → Health
echo   • https://bank.dvta.ch/   → Bank principal completo ^(puerto 8000^)
echo.
echo ⏱️  Espera 10-30 segundos para que se propague
echo.
echo 💡 Ventanas abiertas:
echo   • DVDcoin Bank Main  - Servidor principal del Bank ^(8000^)
echo   • DVDcoin Bank Panel - Panel modular Bank ^(8002^)
echo   • DVDcoin Exams      - Servidor Exams ^(8001^)
echo   • Cloudflare Tunnel  - Túnel Cloudflare
echo.
echo ⚠️  NO CIERRES estas ventanas mientras uses el sistema
echo.
pause
