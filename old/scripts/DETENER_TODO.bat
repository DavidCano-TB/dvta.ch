@echo off
chcp 65001 >nul
title 🛑 Detener DVDcoin
color 0C

echo.
echo ═══════════════════════════════════════════════════════════
echo   🛑 DETENIENDO DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

REM Detener cloudflared
echo Deteniendo túnel Cloudflare...
taskkill /F /IM cloudflared.exe 2>nul
if errorlevel 1 (
    echo   ℹ️  cloudflared no estaba corriendo
) else (
    echo   ✅ Túnel Cloudflare detenido
)
echo.

REM Detener servidor Python
echo Deteniendo servidor Python...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq DVDcoin*" 2>nul
if errorlevel 1 (
    echo   ℹ️  Servidor Python no estaba corriendo
) else (
    echo   ✅ Servidor Python detenido
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ TODOS LOS SERVICIOS DETENIDOS
echo ═══════════════════════════════════════════════════════════
echo.
echo Para reiniciar, ejecuta: INICIO.bat
echo.
pause
