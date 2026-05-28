@echo off
chcp 65001 >nul
title Instalar Servicios Windows - DVDcoin
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 INSTALAR SERVICIOS WINDOWS - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Esto registra cada servicio como un Servicio Windows independiente.
echo   Se inician automáticamente con Windows y se reinician si caen.
echo.
echo   ⚠️  REQUIERE EJECUTAR COMO ADMINISTRADOR
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

:: Verificar admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Este script requiere privilegios de Administrador.
    echo    Haz clic derecho → Ejecutar como administrador.
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [1/3] Instalando servicios...
echo.

:: ── Bank Principal (puerto 8000) ──
echo   → DVDcoin-Bank (puerto 8000)...
python services\svc_bank.py --startup auto install >nul 2>&1
if %errorlevel% equ 0 (echo     ✅ Instalado) else (
    python services\svc_bank.py stop >nul 2>&1
    python services\svc_bank.py remove >nul 2>&1
    timeout /t 2 /nobreak >nul
    python services\svc_bank.py --startup auto install >nul 2>&1
    if %errorlevel% equ 0 (echo     ✅ Reinstalado) else (echo     ❌ Error)
)

:: ── Exams + OPO (puerto 8001) ──
echo   → DVDcoin-Exams (puerto 8001)...
python services\svc_exams.py --startup auto install >nul 2>&1
if %errorlevel% equ 0 (echo     ✅ Instalado) else (
    python services\svc_exams.py stop >nul 2>&1
    python services\svc_exams.py remove >nul 2>&1
    timeout /t 2 /nobreak >nul
    python services\svc_exams.py --startup auto install >nul 2>&1
    if %errorlevel% equ 0 (echo     ✅ Reinstalado) else (echo     ❌ Error)
)

:: ── Bank Proxy (puerto 8002) ──
echo   → DVDcoin-BankProxy (puerto 8002)...
python services\svc_bankproxy.py --startup auto install >nul 2>&1
if %errorlevel% equ 0 (echo     ✅ Instalado) else (
    python services\svc_bankproxy.py stop >nul 2>&1
    python services\svc_bankproxy.py remove >nul 2>&1
    timeout /t 2 /nobreak >nul
    python services\svc_bankproxy.py --startup auto install >nul 2>&1
    if %errorlevel% equ 0 (echo     ✅ Reinstalado) else (echo     ❌ Error)
)

:: ── Cloudflare Tunnel ──
echo   → DVDcoin-Tunnel (Cloudflare)...
python services\svc_tunnel.py --startup auto install >nul 2>&1
if %errorlevel% equ 0 (echo     ✅ Instalado) else (
    python services\svc_tunnel.py stop >nul 2>&1
    python services\svc_tunnel.py remove >nul 2>&1
    timeout /t 2 /nobreak >nul
    python services\svc_tunnel.py --startup auto install >nul 2>&1
    if %errorlevel% equ 0 (echo     ✅ Reinstalado) else (echo     ❌ Error)
)

echo.
echo [2/3] Iniciando servicios...
echo.

net start DVDcoin-Bank >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Bank iniciado) else (echo   ⚠️  DVDcoin-Bank ya corriendo o error)

net start DVDcoin-Exams >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Exams iniciado) else (echo   ⚠️  DVDcoin-Exams ya corriendo o error)

net start DVDcoin-BankProxy >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-BankProxy iniciado) else (echo   ⚠️  DVDcoin-BankProxy ya corriendo o error)

net start DVDcoin-Tunnel >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Tunnel iniciado) else (echo   ⚠️  DVDcoin-Tunnel ya corriendo o error)

echo.
echo [3/3] Verificando...
echo.
timeout /t 5 /nobreak >nul

sc query DVDcoin-Bank | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Bank = RUNNING) else (echo   ❌ DVDcoin-Bank NO está corriendo)

sc query DVDcoin-Exams | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Exams = RUNNING) else (echo   ❌ DVDcoin-Exams NO está corriendo)

sc query DVDcoin-BankProxy | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-BankProxy = RUNNING) else (echo   ❌ DVDcoin-BankProxy NO está corriendo)

sc query DVDcoin-Tunnel | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ DVDcoin-Tunnel = RUNNING) else (echo   ❌ DVDcoin-Tunnel NO está corriendo)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SERVICIOS WINDOWS INSTALADOS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Los servicios se inician automáticamente con Windows.
echo   Si un servicio cae, se reinicia solo en 5 segundos.
echo.
echo   Comandos útiles:
echo     net stop DVDcoin-Bank          (detener Bank)
echo     net start DVDcoin-Bank         (iniciar Bank)
echo     sc query DVDcoin-Bank          (ver estado)
echo     services.msc                   (panel de servicios)
echo.
echo   Para desinstalar: DESINSTALAR_SERVICIOS_WINDOWS.bat
echo.
pause
