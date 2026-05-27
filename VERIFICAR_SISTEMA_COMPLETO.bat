@echo off
chcp 65001 >nul
title Verificación Sistema Completo
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN SISTEMA COMPLETO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

set ERRORS=0

REM ═══════════════════════════════════════════════════════════════════════════
echo [1/10] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo       ✅ Python %%i instalado
) else (
    echo       ❌ Python NO encontrado
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [2/10] Verificando estructura de carpetas...
set FOLDERS_OK=0
if exist "modules\shared" (
    echo       ✅ modules\shared
    set /a FOLDERS_OK+=1
)
if exist "modules\exams" (
    echo       ✅ modules\exams
    set /a FOLDERS_OK+=1
)
if exist "modules\bank" (
    echo       ✅ modules\bank
    set /a FOLDERS_OK+=1
)
if exist "data" (
    echo       ✅ data
    set /a FOLDERS_OK+=1
)
if exist "config" (
    echo       ✅ config
    set /a FOLDERS_OK+=1
)
if %FOLDERS_OK% lss 5 (
    echo       ⚠️  Algunas carpetas faltan
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [3/10] Verificando archivos críticos...
set FILES_OK=0
if exist "main.py" (
    echo       ✅ main.py (Bank)
    set /a FILES_OK+=1
) else (
    echo       ❌ main.py NO encontrado
    set /a ERRORS+=1
)
if exist "modules\exams\app_exams.py" (
    echo       ✅ app_exams.py (Exams)
    set /a FILES_OK+=1
) else (
    echo       ⚠️  app_exams.py no encontrado (módulo nuevo)
)
if exist "modules\shared\db_helper.py" (
    echo       ✅ db_helper.py (Shared)
    set /a FILES_OK+=1
)
if exist "requirements.txt" (
    echo       ✅ requirements.txt
    set /a FILES_OK+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [4/10] Verificando dependencias Python...
python -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✅ FastAPI instalado
) else (
    echo       ❌ FastAPI NO instalado
    set /a ERRORS+=1
)
python -c "import uvicorn" >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✅ Uvicorn instalado
) else (
    echo       ❌ Uvicorn NO instalado
    set /a ERRORS+=1
)
python -c "import bcrypt" >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✅ bcrypt instalado
) else (
    echo       ⚠️  bcrypt no instalado
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [5/10] Verificando sintaxis Python...
python -m py_compile main.py >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✅ main.py sintaxis OK
) else (
    echo       ❌ main.py tiene errores de sintaxis
    set /a ERRORS+=1
)
if exist "modules\exams\app_exams.py" (
    python -m py_compile modules\exams\app_exams.py >nul 2>&1
    if %errorlevel% equ 0 (
        echo       ✅ app_exams.py sintaxis OK
    ) else (
        echo       ❌ app_exams.py tiene errores
        set /a ERRORS+=1
    )
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [6/10] Verificando bases de datos...
if exist "data\users.db" (
    echo       ✅ users.db existe
) else (
    echo       ⚠️  users.db se creará al iniciar
)
if exist "data\transactions.db" (
    echo       ✅ transactions.db existe
) else (
    echo       ⚠️  transactions.db se creará al iniciar
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [7/10] Verificando configuración Cloudflare...
if exist "cloudflared.exe" (
    echo       ✅ cloudflared.exe instalado
) else (
    echo       ⚠️  cloudflared.exe no encontrado
)
if exist "cloudflare-dvta-config.yml" (
    echo       ✅ cloudflare-dvta-config.yml
) else (
    echo       ⚠️  cloudflare-dvta-config.yml no encontrado
)
if exist "config\tunnels\cloudflare-multi.yml" (
    echo       ✅ cloudflare-multi.yml (nuevo)
) else (
    echo       ⚠️  cloudflare-multi.yml no encontrado
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [8/10] Verificando scripts de arranque...
if exist "ARRANCAR.bat" (
    echo       ✅ ARRANCAR.bat (Bank)
) else (
    echo       ❌ ARRANCAR.bat NO encontrado
    set /a ERRORS+=1
)
if exist "ARRANCAR_TODO.bat" (
    echo       ✅ ARRANCAR_TODO.bat (Todos los módulos)
) else (
    echo       ⚠️  ARRANCAR_TODO.bat no encontrado
)
if exist "INICIAR_TUNNEL_DVTA.bat" (
    echo       ✅ INICIAR_TUNNEL_DVTA.bat
) else (
    echo       ⚠️  INICIAR_TUNNEL_DVTA.bat no encontrado
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [9/10] Verificando GitHub Actions...
if exist ".github\workflows\deploy.yml" (
    echo       ✅ deploy.yml configurado
) else (
    echo       ❌ deploy.yml NO encontrado
    set /a ERRORS+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [10/10] Verificando servidores en ejecución...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('tasklist ^| findstr "python.exe" ^| find /c /v ""') do (
        echo       ✅ %%i proceso(s) Python en ejecución
    )
) else (
    echo       ⚠️  Ningún servidor Python en ejecución
)
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✅ Cloudflare Tunnel en ejecución
) else (
    echo       ⚠️  Cloudflare Tunnel no está en ejecución
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
    echo   🚀 LISTO PARA:
    echo      • Arrancar servidores: ARRANCAR_TODO.bat
    echo      • Iniciar tunnel: INICIAR_TUNNEL_DVTA.bat
    echo      • Push a GitHub: git push
) else (
    echo   ❌ ERRORES ENCONTRADOS: %ERRORS%
    echo.
    echo   🔧 ACCIONES REQUERIDAS:
    if %ERRORS% gtr 0 (
        echo      • Instalar dependencias: pip install -r requirements.txt
        echo      • Verificar archivos críticos
        echo      • Revisar errores arriba
    )
)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
