@echo off
chcp 65001 >nul
title DVDBank - Detener Sistema
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🛑 DETENIENDO SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo [1/2] Deteniendo servidor Python...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Python detenido
) else (
    echo      ℹ️  Servidor Python no estaba ejecutándose
)
echo.

echo [2/2] Deteniendo Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel detenido
) else (
    echo      ℹ️  Cloudflare Tunnel no estaba ejecutándose
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SISTEMA DETENIDO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Todos los procesos han sido detenidos.
echo.
echo Para reiniciar el sistema:
echo   • Ejecuta: ARRANCAR.bat (solo servidor)
echo   • O ejecuta: INICIAR_SISTEMA_DVTA.bat (servidor + túnel)
echo.
pause
