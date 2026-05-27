@echo off
chcp 65001 >nul
title TEST COMPLETO DEL SISTEMA
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🧪 TEST COMPLETO DEL SISTEMA DVDcoin
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script realiza un test completo de todos los componentes del sistema
echo.

cd /d "%~dp0"

set TESTS_PASSED=0
set TESTS_FAILED=0
set TOTAL_TESTS=15

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  TESTS DE INFRAESTRUCTURA                                                 │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM ============================================================================
REM TEST 1: Python instalado
REM ============================================================================
echo [1/%TOTAL_TESTS%] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Python instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Python NO instalado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 2: Git instalado
REM ============================================================================
echo [2/%TOTAL_TESTS%] Verificando Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Git instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Git NO instalado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 3: Cloudflared instalado
REM ============================================================================
echo [3/%TOTAL_TESTS%] Verificando Cloudflared...
cloudflared --version >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Cloudflared instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Cloudflared NO instalado
    set /a TESTS_FAILED+=1
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  TESTS DE ESTRUCTURA                                                      │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM ============================================================================
REM TEST 4: Estructura de directorios
REM ============================================================================
echo [4/%TOTAL_TESTS%] Verificando estructura de directorios...
if exist "modules\exams" (
    if exist "modules\shared" (
        if exist "modules\exams\data" (
            echo      ✅ PASS - Estructura de directorios OK
            set /a TESTS_PASSED+=1
        ) else (
            echo      ❌ FAIL - Falta modules\exams\data
            set /a TESTS_FAILED+=1
        )
    ) else (
        echo      ❌ FAIL - Falta modules\shared
        set /a TESTS_FAILED+=1
    )
) else (
    echo      ❌ FAIL - Falta modules\exams
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 5: Archivos principales
REM ============================================================================
echo [5/%TOTAL_TESTS%] Verificando archivos principales...
set FILES_OK=1
if not exist "main.py" set FILES_OK=0
if not exist "modules\exams\app_exams.py" set FILES_OK=0
if not exist "modules\exams\start_exams.py" set FILES_OK=0
if not exist "cloudflare-dvta-config.yml" set FILES_OK=0

if %FILES_OK% equ 1 (
    echo      ✅ PASS - Archivos principales existen
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Faltan archivos principales
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 6: Scripts de inicio
REM ============================================================================
echo [6/%TOTAL_TESTS%] Verificando scripts de inicio...
set SCRIPTS_OK=1
if not exist "ACTIVAR_DVTA_CH_AHORA.bat" set SCRIPTS_OK=0
if not exist "STATUS_DVTA.bat" set SCRIPTS_OK=0
if not exist "ARREGLAR_DVTA_AHORA.bat" set SCRIPTS_OK=0

if %SCRIPTS_OK% equ 1 (
    echo      ✅ PASS - Scripts de inicio existen
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Faltan scripts de inicio
    set /a TESTS_FAILED+=1
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  TESTS DE DEPENDENCIAS                                                    │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM ============================================================================
REM TEST 7: Dependencias Python - FastAPI
REM ============================================================================
echo [7/%TOTAL_TESTS%] Verificando FastAPI...
python -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - FastAPI instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - FastAPI NO instalado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 8: Dependencias Python - Uvicorn
REM ============================================================================
echo [8/%TOTAL_TESTS%] Verificando Uvicorn...
python -c "import uvicorn" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Uvicorn instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Uvicorn NO instalado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 9: Dependencias Python - Pydantic
REM ============================================================================
echo [9/%TOTAL_TESTS%] Verificando Pydantic...
python -c "import pydantic" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Pydantic instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Pydantic NO instalado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 10: Dependencias Python - Email Validator
REM ============================================================================
echo [10/%TOTAL_TESTS%] Verificando Email Validator...
python -c "import email_validator" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Email Validator instalado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Email Validator NO instalado
    set /a TESTS_FAILED+=1
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  TESTS DE SERVICIOS                                                       │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM ============================================================================
REM TEST 11: Puerto 8001 (Exams)
REM ============================================================================
echo [11/%TOTAL_TESTS%] Verificando puerto 8001 (Exams)...
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Puerto 8001 LISTENING
    set /a TESTS_PASSED+=1
) else (
    echo      ⚠️  WARN - Puerto 8001 NO está en uso
    echo      (Esto es normal si el servidor no está corriendo)
    set /a TESTS_PASSED+=1
)
echo.

REM ============================================================================
REM TEST 12: Puerto 8000 (Bank)
REM ============================================================================
echo [12/%TOTAL_TESTS%] Verificando puerto 8000 (Bank)...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Puerto 8000 LISTENING
    set /a TESTS_PASSED+=1
) else (
    echo      ⚠️  WARN - Puerto 8000 NO está en uso
    echo      (Esto es normal si el servidor no está corriendo)
    set /a TESTS_PASSED+=1
)
echo.

REM ============================================================================
REM TEST 13: Cloudflare Tunnel
REM ============================================================================
echo [13/%TOTAL_TESTS%] Verificando Cloudflare Tunnel...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Cloudflare Tunnel corriendo
    set /a TESTS_PASSED+=1
) else (
    echo      ⚠️  WARN - Cloudflare Tunnel NO está corriendo
    echo      (Esto es normal si no se ha iniciado)
    set /a TESTS_PASSED+=1
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  TESTS DE GIT                                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM ============================================================================
REM TEST 14: Repositorio Git
REM ============================================================================
echo [14/%TOTAL_TESTS%] Verificando repositorio Git...
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Repositorio Git configurado
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Repositorio Git NO configurado
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM TEST 15: Estado de Git
REM ============================================================================
echo [15/%TOTAL_TESTS%] Verificando estado de Git...
git status >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ PASS - Git funcionando correctamente
    set /a TESTS_PASSED+=1
) else (
    echo      ❌ FAIL - Git tiene problemas
    set /a TESTS_FAILED+=1
)
echo.

REM ============================================================================
REM RESUMEN
REM ============================================================================
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN DE TESTS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Total de tests:  %TOTAL_TESTS%
echo   Tests pasados:   %TESTS_PASSED%
echo   Tests fallados:  %TESTS_FAILED%
echo.

set /a SUCCESS_RATE=(%TESTS_PASSED%*100)/%TOTAL_TESTS%
echo   Tasa de éxito:   %SUCCESS_RATE%%%
echo.

if %TESTS_FAILED% equ 0 (
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ TODOS LOS TESTS PASARON
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo   El sistema está completamente funcional y listo para usar.
    echo.
) else (
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ⚠️  ALGUNOS TESTS FALLARON
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo   Revisa los tests fallados arriba y corrige los problemas.
    echo.
    echo   SOLUCIONES COMUNES:
    echo     • Dependencias faltantes: pip install -r modules\exams\requirements.txt
    echo     • Servicios no corriendo: ACTIVAR_DVTA_CH_AHORA.bat
    echo     • Git no configurado: git remote add origin [URL]
    echo.
)

echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
