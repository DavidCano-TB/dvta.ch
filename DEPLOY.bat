@echo off
chcp 65001 >nul
title DEPLOY dvta.ch - Actualizar y desplegar
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DEPLOY dvta.ch - Actualizar desde GitHub y reiniciar TODO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

:: ─────────────────────────────────────────────────────────────────────────────
:: 1. PULL desde GitHub
:: ─────────────────────────────────────────────────────────────────────────────
echo [1/5] Descargando últimos cambios de GitHub...
git pull --ff-only
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  git pull falló. Intentando con stash...
    git stash
    git pull --ff-only
    if %errorlevel% neq 0 (
        echo ❌ No se pudo actualizar. Revisa manualmente.
        pause
        exit /b 1
    )
    git stash pop 2>nul
)
echo ✅ Código actualizado
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 2. Instalar/actualizar dependencias
:: ─────────────────────────────────────────────────────────────────────────────
echo [2/5] Actualizando dependencias...
pip install -r requirements.txt -q 2>nul
echo ✅ Dependencias OK
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 3. Matar TODOS los procesos anteriores
:: ─────────────────────────────────────────────────────────────────────────────
echo [3/5] Deteniendo todos los servicios...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo ✅ Procesos detenidos
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 4. Arrancar TODOS los servicios (presente y futuro)
::    Cada servicio se define aquí. Para añadir uno nuevo, solo añade una línea.
:: ─────────────────────────────────────────────────────────────────────────────
echo [4/5] Arrancando servicios...
echo.

:: ── SERVICIO: Bank Principal (puerto 8000) ──
echo   → Bank Principal (main.py, puerto 8000)...
start "DVDcoin-Bank-8000" /MIN cmd /c "cd /d "%~dp0" && python main.py"
timeout /t 3 /nobreak >nul

:: ── SERVICIO: Exams + OPO (puerto 8001) ──
echo   → Exams + OPO (modules\exams\app_exams.py, puerto 8001)...
start "DVDcoin-Exams-8001" /MIN cmd /c "cd /d "%~dp0" && python modules\exams\app_exams.py"
timeout /t 3 /nobreak >nul

:: ── SERVICIO: Bank Proxy (puerto 8002) ──
echo   → Bank Proxy (modules\bank\app_bank.py, puerto 8002)...
start "DVDcoin-BankProxy-8002" /MIN cmd /c "cd /d "%~dp0" && python modules\bank\app_bank.py"
timeout /t 3 /nobreak >nul

:: ── SERVICIO: Cloudflare Tunnel ──
if exist "credentials\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json" (
    echo   → Cloudflare Tunnel...
    start "DVDcoin-Tunnel" /MIN cmd /c "cd /d "%~dp0" && cloudflared tunnel --config cloudflare-dvta-config.yml run"
    timeout /t 5 /nobreak >nul
) else (
    echo   ⚠️  Sin credenciales del túnel. dvta.ch no será accesible externamente.
    echo      Ejecuta SETUP.bat para configurar el túnel.
)

echo.
echo ✅ Servicios arrancados
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 5. Verificación
:: ─────────────────────────────────────────────────────────────────────────────
echo [5/5] Verificando...
echo.
timeout /t 3 /nobreak >nul

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Puerto 8000 - Bank Principal) else (echo   ❌ Puerto 8000 - Bank Principal NO RESPONDE)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Puerto 8001 - Exams + OPO) else (echo   ❌ Puerto 8001 - Exams + OPO NO RESPONDE)

netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Puerto 8002 - Bank Proxy) else (echo   ❌ Puerto 8002 - Bank Proxy NO RESPONDE)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Cloudflare Tunnel activo) else (echo   ⚠️  Cloudflare Tunnel no activo)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ DEPLOY COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Servicios desplegados:
echo     • Bank Principal    → puerto 8000 → https://bank.dvta.ch
echo     • Exams + OPO       → puerto 8001 → https://dvta.ch
echo     • Bank Proxy        → puerto 8002 → https://dvta.ch/bank
echo     • Cloudflare Tunnel → dvta.ch ↔ localhost
echo.
echo   URLs:
echo     • https://dvta.ch/         (página principal)
echo     • https://dvta.ch/opo      (tests OPO)
echo     • https://dvta.ch/bank     (Bank completo)
echo     • https://bank.dvta.ch/    (Bank directo)
echo.
echo   Para añadir un nuevo servicio en el futuro:
echo     1. Crea modules\NOMBRE\app_NOMBRE.py con uvicorn en un puerto libre
echo     2. Añade una sección "start" en este archivo DEPLOY.bat
echo     3. Añade la verificación de puerto abajo
echo     4. Commit + push → ejecuta DEPLOY.bat en el servidor
echo.
echo ═══════════════════════════════════════════════════════════════════════════
pause
