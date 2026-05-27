@echo off
chcp 65001 >nul
title DVDBank - Detener Sistema
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🛑 DETENIENDO SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/3] Deteniendo servidor Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo      ✅ Servidor Python detenido
) else (
    echo      ℹ️  Servidor Python no estaba corriendo
)
echo.

echo [2/3] Deteniendo Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe 2>nul
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel detenido
) else (
    echo      ℹ️  Cloudflare Tunnel no estaba corriendo
)
echo.

echo [3/3] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
echo      ✅ Puerto 8000 liberado
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA DETENIDO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
