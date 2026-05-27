@echo off
chcp 65001 >nul
title Estado de dvta.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 ESTADO DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ============================================================================
REM VERIFICAR SERVIDOR EXAMS (Puerto 8001)
REM ============================================================================
echo [1/5] Servidor Exams (puerto 8001):
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ ACTIVO - Puerto 8001 en uso
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        echo      PID: %%a
    )
) else (
    echo      ❌ INACTIVO - Puerto 8001 libre
    echo      Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
)
echo.

REM ============================================================================
REM VERIFICAR CLOUDFLARE TUNNEL
REM ============================================================================
echo [2/5] Cloudflare Tunnel:
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ ACTIVO - cloudflared.exe corriendo
    for /f "tokens=2" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
        echo      PID: %%a
    )
) else (
    echo      ❌ INACTIVO - cloudflared.exe no encontrado
    echo      Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
)
echo.

REM ============================================================================
REM VERIFICAR PROCESOS PYTHON
REM ============================================================================
echo [3/5] Procesos Python:
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ ACTIVO - python.exe corriendo
    tasklist | findstr "python.exe"
) else (
    echo      ❌ INACTIVO - python.exe no encontrado
)
echo.

REM ============================================================================
REM VERIFICAR ACCESO LOCAL
REM ============================================================================
echo [4/5] Acceso local (http://localhost:8001):
curl -s -o nul -w "%%{http_code}" http://localhost:8001 >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ RESPONDE - Servidor local accesible
) else (
    echo      ⚠️  NO RESPONDE - curl no disponible o servidor inactivo
)
echo.

REM ============================================================================
REM VERIFICAR ARCHIVOS DE CONFIGURACIÓN
REM ============================================================================
echo [5/5] Archivos de configuración:
if exist "cloudflare-dvta-config.yml" (
    echo      ✅ cloudflare-dvta-config.yml existe
) else (
    echo      ❌ cloudflare-dvta-config.yml NO EXISTE
)

if exist "modules\exams\app_exams.py" (
    echo      ✅ modules\exams\app_exams.py existe
) else (
    echo      ❌ modules\exams\app_exams.py NO EXISTE
)

if exist "modules\exams\start_exams.py" (
    echo      ✅ modules\exams\start_exams.py existe
) else (
    echo      ❌ modules\exams\start_exams.py NO EXISTE
)

if exist "modules\exams\requirements.txt" (
    echo      ✅ modules\exams\requirements.txt existe
) else (
    echo      ❌ modules\exams\requirements.txt NO EXISTE
)
echo.

REM ============================================================================
REM RESUMEN
REM ============================================================================
echo ═══════════════════════════════════════════════════════════════════════════
echo   📋 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.

netstat -ano | findstr ":8001" >nul 2>&1
set SERVER_OK=%errorlevel%

tasklist | findstr "cloudflared.exe" >nul 2>&1
set TUNNEL_OK=%errorlevel%

if %SERVER_OK% equ 0 (
    if %TUNNEL_OK% equ 0 (
        echo ✅ TODO FUNCIONANDO CORRECTAMENTE
        echo.
        echo 🌐 ACCESO:
        echo   • Externo: https://dvta.ch
        echo   • Local:   http://localhost:8001
        echo.
        echo 💡 TIP: Si dvta.ch no carga, espera 30 segundos y recarga
    ) else (
        echo ⚠️  SERVIDOR OK, PERO TUNNEL INACTIVO
        echo.
        echo 🔧 SOLUCIÓN:
        echo   Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
    )
) else (
    echo ❌ SERVICIOS INACTIVOS
    echo.
    echo 🔧 SOLUCIÓN:
    echo   Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
