@echo off
chcp 65001 >nul
title DVDcoin - Arranque Completo dvta.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 ARRANQUE COMPLETO - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script:
echo   1. Detiene procesos anteriores
echo   2. Inicia servidor Exams (puerto 8001)
echo   3. Inicia Cloudflare Tunnel
echo   4. Verifica que todo funcione
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ═══════════════════════════════════════════════════════════════════════════
echo [1/5] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [2/5] Verificando archivos...
if not exist "modules\exams\app_exams.py" (
    echo      ❌ app_exams.py NO encontrado
    echo.
    echo      El módulo Exams no está instalado correctamente.
    pause
    exit /b 1
)
if not exist "cloudflared.exe" (
    echo      ❌ cloudflared.exe NO encontrado
    echo.
    echo      Descarga desde: https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
)
echo      ✅ Archivos OK
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [3/5] Iniciando servidor Exams (puerto 8001)...
start "DVDExams Server" cmd /c "cd modules\exams && python start_exams.py"
timeout /t 7 /nobreak >nul

REM Verificar que el servidor inició
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Exams iniciado
) else (
    echo      ❌ Error: Servidor no se inició
    echo.
    echo      Verifica:
    echo        • Python está instalado
    echo        • Dependencias instaladas: pip install -r modules\exams\requirements.txt
    pause
    exit /b 1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [4/5] Esperando que el servidor esté listo...
timeout /t 3 /nobreak >nul

REM Verificar puerto 8001
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 activo
) else (
    echo      ⚠️  Puerto 8001 no responde aún (puede tardar unos segundos)
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [5/5] Iniciando Cloudflare Tunnel...
echo.
echo      Configuración:
echo        • Dominio: dvta.ch
echo        • Puerto: 8001
echo        • Servicio: Exams
echo.
start "Cloudflare Tunnel - dvta.ch" cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
timeout /t 3 /nobreak >nul

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Tunnel iniciado
) else (
    echo      ❌ Error: Tunnel no se inició
    pause
    exit /b 1
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 ACCESO:
echo   • Local:   http://localhost:8001
echo   • Externo: https://dvta.ch
echo.
echo 🔍 VERIFICAR:
echo   • Abre https://dvta.ch en tu navegador
echo   • Deberías ver la página de Exams
echo.
echo 📊 ESTADO:
echo   • Servidor Exams: Corriendo en puerto 8001
echo   • Cloudflare Tunnel: Activo
echo.
echo 🛑 DETENER:
echo   • Cierra las ventanas de servidor y tunnel
echo   • O ejecuta: taskkill /F /IM python.exe ^& taskkill /F /IM cloudflared.exe
echo.
echo ⚠️  IMPORTANTE:
echo   • Mantén las ventanas abiertas para que el servicio funcione
echo   • Si cierras esta ventana, los servicios seguirán corriendo
echo.
pause
