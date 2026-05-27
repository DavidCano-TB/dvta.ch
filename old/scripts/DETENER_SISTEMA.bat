@echo off
chcp 65001 >nul
title Deteniendo DVDBank
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🛑 DETENIENDO SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/2] Deteniendo servidor Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo      ✅ Python detenido
) else (
    echo      ℹ️  Python no estaba corriendo
)
echo.

echo [2/2] Deteniendo Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe 2>nul
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare detenido
) else (
    echo      ℹ️  Cloudflare no estaba corriendo
)
echo.

timeout /t 2 /nobreak >nul

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA DETENIDO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Para reiniciar el sistema:
echo    INICIAR_SISTEMA_DVTA.bat
echo.
pause
