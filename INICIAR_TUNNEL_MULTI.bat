@echo off
chcp 65001 >nul
title Cloudflare Tunnel - Multi-Módulo
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🌐 CLOUDFLARE TUNNEL - MULTI-MÓDULO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Verificar cloudflared
echo [1/3] Verificando Cloudflare Tunnel...
if not exist "cloudflared.exe" (
    echo      ❌ cloudflared.exe no encontrado
    echo.
    echo      Descarga desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    pause
    exit /b 1
)
echo      ✅ Cloudflared instalado
echo.

REM Verificar configuración
echo [2/3] Verificando configuración...
if not exist "config\tunnels\cloudflare-multi.yml" (
    echo      ❌ Configuración no encontrada
    pause
    exit /b 1
)
echo      ✅ Configuración OK
echo.

REM Iniciar tunnel
echo [3/3] Iniciando tunnel...
echo.
echo      Dominios configurados:
echo        • dvdbank.com     → localhost:8000 (Bank)
echo        • dvta.ch         → localhost:8001 (Exams)
echo        • games.dvdbank.com → localhost:8002 (Games)
echo.
echo      Presiona Ctrl+C para detener
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cloudflared.exe tunnel --config config\tunnels\cloudflare-multi.yml run

pause
