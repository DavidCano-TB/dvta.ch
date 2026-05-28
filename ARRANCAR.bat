@echo off
chcp 65001 >nul
title DVDcoin Platform - Arranque Unificado
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DVDCOIN PLATFORM - ARRANQUE UNIFICADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 1: Verificar Python
REM ═══════════════════════════════════════════════════════════════════════════
echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo      ❌ Python no encontrado en PATH
    echo      Instala Python 3.11+ desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo      ✅ Python %%v
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 2: Instalar/verificar dependencias
REM ═══════════════════════════════════════════════════════════════════════════
echo [2/7] Verificando dependencias...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ⚠️  Instalando dependencias principales...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo      ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)
python -c "import pytest" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ⚠️  Instalando dependencias de desarrollo...
    pip install -r requirements-dev.txt --quiet
)
if exist "modules\exams\requirements.txt" (
    pip install -r modules\exams\requirements.txt --quiet 2>nul
)
echo      ✅ Dependencias OK
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 3: Crear directorios necesarios
REM ═══════════════════════════════════════════════════════════════════════════
echo [3/7] Verificando estructura de directorios...
if not exist "data" mkdir data
if not exist "config" mkdir config
if not exist "modules\exams\data" mkdir modules\exams\data
if not exist "modules\exams\config" mkdir modules\exams\config
if not exist "modules\bank\data" mkdir modules\bank\data
if not exist "modules\bank\config" mkdir modules\bank\config
echo      ✅ Directorios OK
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 4: Matar procesos anteriores en los puertos del proyecto
REM ═══════════════════════════════════════════════════════════════════════════
echo [4/7] Liberando puertos (8000, 8001, 8002)...

REM Kill processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
REM Kill processes on port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
REM Kill processes on port 8002
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
REM Kill cloudflared
taskkill /F /IM cloudflared.exe >nul 2>&1

timeout /t 2 /nobreak >nul
echo      ✅ Puertos liberados
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 5: Iniciar servicios
REM ═══════════════════════════════════════════════════════════════════════════
echo [5/7] Iniciando servicios...
echo.

echo      → Bank principal (puerto 8000)...
start "DVDcoin Bank [8000]" cmd /c "python main.py"
timeout /t 4 /nobreak >nul

echo      → Exams / Hub (puerto 8001)...
if exist "modules\exams\app_exams.py" (
    start "DVDcoin Exams [8001]" cmd /c "cd modules\exams && python app_exams.py"
    timeout /t 4 /nobreak >nul
) else (
    echo      ⚠️  modules\exams\app_exams.py no encontrado - saltando
)

echo      → Bank Panel (puerto 8002)...
if exist "modules\bank\app_bank.py" (
    start "DVDcoin Bank Panel [8002]" cmd /c "cd modules\bank && python app_bank.py"
    timeout /t 3 /nobreak >nul
) else (
    echo      ⚠️  modules\bank\app_bank.py no encontrado - saltando
)

echo      → Cloudflare Tunnel...
where cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    if exist "cloudflare-dvta-config.yml" (
        start "Cloudflare Tunnel" cmd /c "cloudflared tunnel --config cloudflare-dvta-config.yml run"
        timeout /t 3 /nobreak >nul
        echo      ✅ Tunnel iniciado
    ) else (
        echo      ⚠️  cloudflare-dvta-config.yml no encontrado - sin tunnel
    )
) else (
    echo      ⚠️  cloudflared no instalado - sin tunnel externo
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 6: Verificar que los servicios responden
REM ═══════════════════════════════════════════════════════════════════════════
echo [6/7] Verificando servicios...
timeout /t 3 /nobreak >nul

set SERVICES_OK=0
set SERVICES_TOTAL=0

REM Check port 8000
set /a SERVICES_TOTAL+=1
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8000 - Bank principal
    set /a SERVICES_OK+=1
) else (
    echo      ❌ Puerto 8000 - Bank NO responde
)

REM Check port 8001
set /a SERVICES_TOTAL+=1
netstat -ano | findstr ":8001 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 - Exams / Hub
    set /a SERVICES_OK+=1
) else (
    echo      ❌ Puerto 8001 - Exams NO responde
)

REM Check port 8002
set /a SERVICES_TOTAL+=1
netstat -ano | findstr ":8002 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8002 - Bank Panel
    set /a SERVICES_OK+=1
) else (
    echo      ❌ Puerto 8002 - Bank Panel NO responde
)

REM Check cloudflared
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo
) else (
    echo      ⚠️  Cloudflare Tunnel no activo (solo acceso local)
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM   PASO 7: Resumen
REM ═══════════════════════════════════════════════════════════════════════════
echo [7/7] Resumen...
echo.
echo ═══════════════════════════════════════════════════════════════════════════
if %SERVICES_OK% equ %SERVICES_TOTAL% (
    echo   ✅ PLATAFORMA INICIADA CORRECTAMENTE (%SERVICES_OK%/%SERVICES_TOTAL% servicios)
) else (
    echo   ⚠️  PLATAFORMA PARCIALMENTE INICIADA (%SERVICES_OK%/%SERVICES_TOTAL% servicios)
)
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 ACCESO LOCAL:
echo   • Bank:       http://localhost:8000
echo   • Exams/Hub:  http://localhost:8001
echo   • Bank Panel: http://localhost:8002
echo.
echo 🌐 ACCESO EXTERNO (requiere Cloudflare Tunnel):
echo   • dvta.ch          → Exams/Hub
echo   • bank.dvta.ch     → Bank
echo   • dvta.ch/bank     → Bank (via proxy)
echo.
echo 🛑 PARA DETENER:
echo   • Cierra las ventanas de servidor
echo   • O ejecuta: taskkill /F /IM python.exe ^& taskkill /F /IM cloudflared.exe
echo.
echo ⚠️  NO CIERRES las ventanas mientras uses el sistema
echo.
pause
