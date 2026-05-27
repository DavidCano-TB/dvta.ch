@echo off
chcp 65001 >nul
title MONITOR DEL SISTEMA DVDcoin
color 0A

:LOOP
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 MONITOR DEL SISTEMA DVDcoin - %date% %time%
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  SERVICIOS                                                                │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Servidor Exams (puerto 8001)
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Servidor Exams (8001):  ACTIVO
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        echo      PID: %%a
    )
) else (
    echo   ❌ Servidor Exams (8001):  INACTIVO
)
echo.

REM Servidor Bank (puerto 8000)
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Servidor Bank (8000):   ACTIVO
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        echo      PID: %%a
    )
) else (
    echo   ❌ Servidor Bank (8000):   INACTIVO
)
echo.

REM Cloudflare Tunnel
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Cloudflare Tunnel:      ACTIVO
    for /f "tokens=2" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
        echo      PID: %%a
    )
) else (
    echo   ❌ Cloudflare Tunnel:      INACTIVO
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PROCESOS PYTHON                                                          │
echo └───────────────────────────────────────────────────────────────────────────┘
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

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PUERTOS EN USO                                                           │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo   Puertos 8000-8010:
netstat -ano | findstr ":800" | findstr "LISTENING"
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MEMORIA Y CPU                                                            │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Memoria de procesos Python
for /f "tokens=2,5" %%a in ('tasklist ^| findstr "python.exe"') do (
    echo   Python PID %%a: %%b
)

REM Memoria de procesos Cloudflared
for /f "tokens=2,5" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
    echo   Cloudflared PID %%a: %%b
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  ACCESO                                                                   │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   🌐 Exams Local:    http://localhost:8001
    echo   🌐 Exams Externo:  https://dvta.ch
) else (
    echo   ⚠️  Exams no disponible (servidor no corriendo)
)
echo.

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   🌐 Bank Local:     http://localhost:8000
    echo   🌐 Bank Externo:   https://dvdcoin.ch
) else (
    echo   ⚠️  Bank no disponible (servidor no corriendo)
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  ESTADO GENERAL                                                           │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

set SERVICES_OK=0

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 set /a SERVICES_OK+=1

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 set /a SERVICES_OK+=1

if %SERVICES_OK% equ 2 (
    echo   ✅ SISTEMA OPERATIVO - Todos los servicios funcionando
) else if %SERVICES_OK% equ 1 (
    echo   ⚠️  SISTEMA PARCIAL - Algunos servicios no están corriendo
) else (
    echo   ❌ SISTEMA INACTIVO - Servicios no están corriendo
    echo.
    echo   💡 Para iniciar: ACTIVAR_DVTA_CH_AHORA.bat
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Actualizando en 5 segundos... (Presiona Ctrl+C para salir)
echo.

timeout /t 5 /nobreak >nul
goto LOOP
