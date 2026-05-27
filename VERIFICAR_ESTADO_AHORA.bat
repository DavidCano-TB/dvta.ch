@echo off
chcp 65001 >nul
title Verificación Estado dvta.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 VERIFICACIÓN ESTADO COMPLETO - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ============================================================================
REM VERIFICAR PUERTO 8001
REM ============================================================================
echo [1/5] Verificando puerto 8001 (Exams Server)...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 ACTIVO
    netstat -ano | findstr ":8001"
) else (
    echo      ❌ Puerto 8001 NO está en uso
    echo      ⚠️  El servidor Exams NO está corriendo
)
echo.

REM ============================================================================
REM VERIFICAR PROCESOS PYTHON
REM ============================================================================
echo [2/5] Verificando procesos Python...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Procesos Python encontrados:
    tasklist | findstr "python.exe"
) else (
    echo      ❌ NO hay procesos Python corriendo
)
echo.

REM ============================================================================
REM VERIFICAR CLOUDFLARE TUNNEL
REM ============================================================================
echo [3/5] Verificando Cloudflare Tunnel...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo:
    tasklist | findstr "cloudflared.exe"
) else (
    echo      ❌ Cloudflare Tunnel NO está corriendo
)
echo.

REM ============================================================================
REM VERIFICAR ARCHIVOS CRÍTICOS
REM ============================================================================
echo [4/5] Verificando archivos críticos...

set ARCHIVOS_OK=1

if exist "modules\exams\app_exams.py" (
    echo      ✅ app_exams.py
) else (
    echo      ❌ app_exams.py NO encontrado
    set ARCHIVOS_OK=0
)

if exist "modules\exams\start_exams.py" (
    echo      ✅ start_exams.py
) else (
    echo      ❌ start_exams.py NO encontrado
    set ARCHIVOS_OK=0
)

if exist "cloudflare-dvta-config.yml" (
    echo      ✅ cloudflare-dvta-config.yml
) else (
    echo      ❌ cloudflare-dvta-config.yml NO encontrado
    set ARCHIVOS_OK=0
)

if exist "modules\exams\requirements.txt" (
    echo      ✅ requirements.txt
) else (
    echo      ❌ requirements.txt NO encontrado
    set ARCHIVOS_OK=0
)

if %ARCHIVOS_OK% equ 1 (
    echo      ✅ Todos los archivos críticos presentes
) else (
    echo      ⚠️  Algunos archivos críticos faltan
)
echo.

REM ============================================================================
REM RESUMEN FINAL
REM ============================================================================
echo [5/5] Resumen del sistema...
echo.

set SISTEMA_OK=1

REM Verificar puerto
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% neq 0 set SISTEMA_OK=0

REM Verificar Python
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% neq 0 set SISTEMA_OK=0

REM Verificar Cloudflare
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% neq 0 set SISTEMA_OK=0

echo ═══════════════════════════════════════════════════════════════════════════

if %SISTEMA_OK% equ 1 (
    echo   ✅ SISTEMA OPERATIVO
    echo.
    echo   🌐 Acceso disponible en:
    echo      • https://dvta.ch
    echo      • http://localhost:8001
    echo.
    echo   📊 Servicios activos:
    echo      • Exams Server ^(puerto 8001^)
    echo      • Cloudflare Tunnel
    echo.
    echo   ✅ Todo funcionando correctamente
) else (
    echo   ❌ SISTEMA NO OPERATIVO
    echo.
    echo   ⚠️  Algunos servicios no están corriendo
    echo.
    echo   🔧 Para iniciar el sistema:
    echo      ACTIVAR_DVTA_CH_AHORA.bat
    echo.
    echo   📝 Para diagnóstico completo:
    echo      DIAGNOSTICO_COMPLETO.bat
)

echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
