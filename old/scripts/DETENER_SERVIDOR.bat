@echo off
REM ============================================================
REM DVDCOIN BANK - DETENER SERVIDOR Y TUNNELS
REM Detiene todos los procesos relacionados con DVDcoin
REM ============================================================

chcp 65001 >nul
title DVDCoin Bank - Detener Servidor

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              DVDCOIN BANK - DETENER SERVIDOR                 ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Deteniendo procesos...
echo.

REM Detener Python
taskkill /F /IM python.exe >nul 2>&1
if errorlevel 1 (
    echo   ○ Python no estaba corriendo
) else (
    echo   ✓ Python detenido
)

taskkill /F /IM pythonw.exe >nul 2>&1
if not errorlevel 1 (
    echo   ✓ Pythonw detenido
)

REM Detener Cloudflare Tunnel
taskkill /F /IM cloudflared.exe >nul 2>&1
if errorlevel 1 (
    echo   ○ Cloudflare Tunnel no estaba corriendo
) else (
    echo   ✓ Cloudflare Tunnel detenido
)

REM Detener ngrok (por si acaso)
taskkill /F /IM ngrok.exe >nul 2>&1
if not errorlevel 1 (
    echo   ✓ ngrok detenido
)

REM Liberar puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   ✓ Puerto 8000 liberado
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ✓ Todos los procesos han sido detenidos
echo.
echo Para reiniciar el servidor:
echo   - Con Cloudflare Tunnel: INICIAR_CON_CLOUDFLARE.bat
echo   - Con ngrok:             ARRANCAR.bat
echo.
pause
