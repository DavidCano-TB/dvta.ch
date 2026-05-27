@echo off
chcp 65001 >nul
title 📊 Dashboard Sistema dvta.ch
color 0B

:LOOP
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                    📊 DASHBOARD SISTEMA dvta.ch                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ============================================================================
REM FECHA Y HORA
REM ============================================================================
echo ⏰ Fecha y Hora: %date% %time:~0,8%
echo.

REM ============================================================================
REM ESTADO DE SERVICIOS
REM ============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║  🔧 ESTADO DE SERVICIOS                                                   ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar puerto 8001
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Exams Server ^(Puerto 8001^)        [ACTIVO]
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        echo      └─ PID: %%a
    )
) else (
    echo   ❌ Exams Server ^(Puerto 8001^)        [INACTIVO]
)

REM Verificar Cloudflare
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Cloudflare Tunnel                  [ACTIVO]
    for /f "tokens=2" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
        echo      └─ PID: %%a
        goto :CLOUD_FOUND
    )
    :CLOUD_FOUND
) else (
    echo   ❌ Cloudflare Tunnel                  [INACTIVO]
)

echo.

REM ============================================================================
REM PROCESOS PYTHON
REM ============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║  🐍 PROCESOS PYTHON                                                       ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Procesos Python activos:
    echo.
    tasklist | findstr "python.exe"
) else (
    echo   ❌ No hay procesos Python corriendo
)

echo.

REM ============================================================================
REM CONECTIVIDAD
REM ============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║  🌐 CONECTIVIDAD                                                          ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Puerto 8001: LISTENING
    echo   ✅ Acceso Local:   http://localhost:8001
    echo   ✅ Acceso Externo: https://dvta.ch
) else (
    echo   ❌ Puerto 8001: NO DISPONIBLE
    echo   ❌ Servidor no está corriendo
)

echo.

REM ============================================================================
REM PUERTOS EN USO
REM ============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║  🔌 PUERTOS EN USO                                                        ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

echo   Puertos del sistema:
echo.
netstat -ano | findstr ":8000 :8001" | findstr "LISTENING"

echo.

REM ============================================================================
REM RESUMEN
REM ============================================================================
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║  📊 RESUMEN                                                               ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

set SISTEMA_OK=1

netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% neq 0 set SISTEMA_OK=0

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% neq 0 set SISTEMA_OK=0

if %SISTEMA_OK% equ 1 (
    echo   ╔═══════════════════════════════════════════════════════════════════════╗
    echo   ║                    ✅ SISTEMA OPERATIVO                               ║
    echo   ╚═══════════════════════════════════════════════════════════════════════╝
    echo.
    echo   🎉 Todos los servicios están funcionando correctamente
    echo   🌐 dvta.ch está disponible y accesible
) else (
    echo   ╔═══════════════════════════════════════════════════════════════════════╗
    echo   ║                    ❌ SISTEMA NO OPERATIVO                            ║
    echo   ╚═══════════════════════════════════════════════════════════════════════╝
    echo.
    echo   ⚠️  Algunos servicios no están corriendo
    echo   🔧 Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   🔄 Actualizando en 10 segundos... ^(Ctrl+C para salir^)
echo.
echo   📝 Acciones rápidas:
echo      [1] Iniciar sistema     - ACTIVAR_DVTA_CH_AHORA.bat
echo      [2] Verificar estado    - VERIFICAR_ESTADO_AHORA.bat
echo      [3] Diagnóstico         - DIAGNOSTICO_COMPLETO.bat
echo      [4] Arreglar problemas  - ARREGLAR_DVTA_AHORA.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════

timeout /t 10 /nobreak >nul
goto LOOP
