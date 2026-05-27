@echo off
chcp 65001 >nul
title Solucionar Tunnel dvta.ch
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 SOLUCIÓN RÁPIDA - Tunnel dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [DIAGNÓSTICO]
echo.

REM Verificar cloudflared
echo 1. Verificando cloudflared.exe...
if not exist "cloudflared.exe" (
    echo    ❌ cloudflared.exe NO encontrado
    echo.
    echo    Descarga desde: https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
) else (
    echo    ✅ cloudflared.exe encontrado
)
echo.

REM Verificar configuración
echo 2. Verificando configuración...
if not exist "cloudflare-dvta-config.yml" (
    echo    ❌ cloudflare-dvta-config.yml NO encontrado
    pause
    exit /b 1
) else (
    echo    ✅ Configuración encontrada
    type cloudflare-dvta-config.yml
)
echo.

REM Verificar servidor Python
echo 3. Verificando servidor Python...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Servidor Python corriendo
) else (
    echo    ❌ Servidor Python NO está corriendo
    echo.
    echo    SOLUCIÓN: Ejecuta primero ARRANCAR_TODO.bat
    pause
    exit /b 1
)
echo.

REM Verificar puerto 8001
echo 4. Verificando puerto 8001...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Puerto 8001 en uso (servidor corriendo)
) else (
    echo    ❌ Puerto 8001 NO está en uso
    echo.
    echo    SOLUCIÓN: El servidor Exams no está corriendo
    echo    Ejecuta: INICIAR_EXAMS.bat
    pause
    exit /b 1
)
echo.

REM Detener tunnel anterior
echo 5. Deteniendo tunnel anterior...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo    ✅ Tunnel anterior detenido
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 INICIANDO TUNNEL
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Configuración:
echo   • Dominio: dvta.ch
echo   • Puerto local: 8001
echo   • Servicio: Exams
echo.
echo Presiona Ctrl+C para detener
echo.

cloudflared.exe tunnel --config cloudflare-dvta-config.yml run

pause
