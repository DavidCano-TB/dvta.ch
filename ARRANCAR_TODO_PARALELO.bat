@echo off
chcp 65001 >nul
title Arrancar Todo en Paralelo - DVDcoin
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 ARRANCAR TODO EN PARALELO - DVDcoin Platform (dvta.ch)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/6] Actualizando código desde GitHub...
git pull --ff-only 2>nul
if %errorlevel% equ 0 (
    echo      ✅ Código actualizado
) else (
    echo      ⚠️  No se pudo actualizar (sin conexión o conflictos)
)
echo.

echo [2/6] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

echo [3/6] Iniciando Bank Server principal (Puerto 8000)...
start "DVDcoin Bank Main" cmd /c "python main.py"
timeout /t 3 /nobreak >nul
echo      ✅ Bank principal iniciado
echo.

echo [4/6] Iniciando Bank Panel Server (Puerto 8002)...
start "DVDcoin Bank Panel" cmd /c "python modules\bank\app_bank.py"
timeout /t 3 /nobreak >nul
echo      ✅ Bank Panel iniciado
echo.

echo [5/6] Iniciando Exams Server (Puerto 8001)...
start "DVDcoin Exams" cmd /c "python modules\exams\app_exams.py"
timeout /t 5 /nobreak >nul
echo      ✅ Exams iniciado
echo.

echo [6/6] Iniciando Cloudflare Tunnel...
if exist "credentials\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json" (
    start "Cloudflare Tunnel" cmd /c "cloudflared tunnel --config cloudflare-dvta-config.yml run"
    timeout /t 5 /nobreak >nul
    echo      ✅ Tunnel iniciado
) else (
    echo      ❌ No hay credenciales del túnel. Ejecuta SETUP.bat primero.
    echo         Sin túnel, dvta.ch no será accesible desde internet.
    echo         Los servidores locales sí funcionan (localhost:8000/8001/8002)
)
echo.

echo ─── Verificando servicios ───
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8000 activo - Bank principal) else (echo      ❌ Puerto 8000 no responde)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8001 activo - Exams) else (echo      ❌ Puerto 8001 no responde)

netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Puerto 8002 activo - Bank Panel) else (echo      ❌ Puerto 8002 no responde)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (echo      ✅ Cloudflare Tunnel activo) else (echo      ⚠️  Cloudflare Tunnel no activo)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 URLs disponibles:
echo   • https://dvta.ch/        → Página principal (Exams)
echo   • https://dvta.ch/opo     → Panel OPO
echo   • https://dvta.ch/bank    → Bank completo
echo   • https://dvta.ch/health  → Health check
echo   • https://bank.dvta.ch/   → Bank directo
echo.
echo 🖥️  URLs locales (siempre funcionan):
echo   • http://localhost:8000/bank  → Bank principal
echo   • http://localhost:8001/opo   → OPO
echo   • http://localhost:8002/bank  → Bank via proxy
echo.
echo ⏱️  Espera 10-30 segundos para que Cloudflare propague
echo.
echo ⚠️  NO CIERRES las ventanas mientras uses el sistema
echo.
pause
