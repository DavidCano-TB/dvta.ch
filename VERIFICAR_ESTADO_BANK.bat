@echo off
chcp 65001 >nul
title DVDBank - Verificar Estado
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICANDO ESTADO DEL SISTEMA - dvta.ch/bank
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/5] Verificando procesos...
echo.
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Python Server: ACTIVO
    for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
        echo         PID: %%a
    )
) else (
    echo      ❌ Python Server: INACTIVO
)
echo.

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel: ACTIVO
    for /f "tokens=2" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
        echo         PID: %%a
    )
) else (
    echo      ❌ Cloudflare Tunnel: INACTIVO
)
echo.

echo [2/5] Verificando puerto 8000...
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8000: EN USO
    netstat -ano | findstr :8000 | findstr LISTENING
) else (
    echo      ❌ Puerto 8000: LIBRE (servidor no está escuchando)
)
echo.

echo [3/5] Probando conexión local...
curl -s -o nul -w "HTTP %%{http_code}" http://127.0.0.1:8000/bank > temp_status.txt 2>&1
set /p LOCAL_STATUS=<temp_status.txt
del temp_status.txt 2>nul
echo      Local (http://127.0.0.1:8000/bank): %LOCAL_STATUS%
echo.

echo [4/5] Probando conexión pública...
curl -s -o nul -w "HTTP %%{http_code}" https://dvta.ch/bank > temp_status.txt 2>&1
set /p PUBLIC_STATUS=<temp_status.txt
del temp_status.txt 2>nul
echo      Público (https://dvta.ch/bank): %PUBLIC_STATUS%
echo.

echo [5/5] Verificando archivos de configuración...
if exist "main.py" (
    echo      ✅ main.py: EXISTE
) else (
    echo      ❌ main.py: NO ENCONTRADO
)

if exist "cloudflare-tunnel-dvta.yml" (
    echo      ✅ cloudflare-tunnel-dvta.yml: EXISTE
) else (
    echo      ⚠️  cloudflare-tunnel-dvta.yml: NO ENCONTRADO
)

if exist "cloudflared.exe" (
    echo      ✅ cloudflared.exe: EXISTE
) else (
    echo      ⚠️  cloudflared.exe: NO ENCONTRADO
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Determinar estado general
set ALL_OK=1

tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% neq 0 set ALL_OK=0

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% neq 0 set ALL_OK=0

if %ALL_OK% equ 1 (
    echo   ✅ SISTEMA FUNCIONANDO CORRECTAMENTE
    echo.
    echo   📍 Accede a: https://dvta.ch/bank
) else (
    echo   ⚠️  SISTEMA CON PROBLEMAS
    echo.
    echo   🔧 Para iniciar el sistema:
    echo      INICIAR_TODO_BANK.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
