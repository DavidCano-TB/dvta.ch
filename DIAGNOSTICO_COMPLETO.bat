@echo off
chcp 65001 >nul
title Diagnóstico Completo - dvta.ch
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 DIAGNÓSTICO COMPLETO - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

set ERRORS=0

REM ═══════════════════════════════════════════════════════════════════════════
echo [1/8] Verificando archivos necesarios...
if exist "cloudflared.exe" (
    echo      ✅ cloudflared.exe
) else (
    echo      ❌ cloudflared.exe NO encontrado
    set /a ERRORS+=1
)
if exist "cloudflare-dvta-config.yml" (
    echo      ✅ cloudflare-dvta-config.yml
) else (
    echo      ❌ cloudflare-dvta-config.yml NO encontrado
    set /a ERRORS+=1
)
if exist "modules\exams\app_exams.py" (
    echo      ✅ modules\exams\app_exams.py
) else (
    echo      ❌ app_exams.py NO encontrado
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [2/8] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo      ✅ Python %%i
) else (
    echo      ❌ Python NO encontrado
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [3/8] Verificando dependencias...
python -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ FastAPI instalado
) else (
    echo      ❌ FastAPI NO instalado
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [4/8] Verificando procesos en ejecución...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('tasklist ^| findstr "python.exe" ^| find /c /v ""') do (
        echo      ✅ %%i proceso(s) Python corriendo
    )
) else (
    echo      ⚠️  Ningún servidor Python corriendo
)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel corriendo
) else (
    echo      ⚠️  Cloudflare Tunnel NO está corriendo
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [5/8] Verificando puertos...
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8000 (Bank) en uso
) else (
    echo      ⚠️  Puerto 8000 libre
)

netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 (Exams) en uso
) else (
    echo      ⚠️  Puerto 8001 libre
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [6/8] Verificando conectividad local...
echo      Probando localhost:8001...
curl -s -o nul -w "%%{http_code}" http://localhost:8001 >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor responde en localhost:8001
) else (
    echo      ❌ Servidor NO responde en localhost:8001
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [7/8] Mostrando configuración del tunnel...
echo.
type cloudflare-dvta-config.yml
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [8/8] Verificando credenciales de Cloudflare...
if exist "C:\Users\PC\.cloudflared\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json" (
    echo      ✅ Credenciales encontradas
) else (
    echo      ❌ Credenciales NO encontradas
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if %ERRORS% equ 0 (
    echo   ✅ SISTEMA OK - Sin errores críticos
    echo.
    echo   🚀 PARA INICIAR:
    echo      ARRANCAR_DVTA_COMPLETO.bat
) else (
    echo   ❌ ERRORES ENCONTRADOS: %ERRORS%
    echo.
    echo   🔧 SOLUCIONES:
    echo.
    if %ERRORS% gtr 0 (
        echo      1. Instalar dependencias:
        echo         pip install -r requirements.txt
        echo         cd modules\exams
        echo         pip install -r requirements.txt
        echo.
        echo      2. Iniciar servidor Exams:
        echo         INICIAR_EXAMS.bat
        echo.
        echo      3. Iniciar tunnel:
        echo         SOLUCIONAR_TUNNEL_DVTA.bat
    )
)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
