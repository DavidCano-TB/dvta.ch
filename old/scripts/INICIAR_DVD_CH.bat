@echo off
chcp 65001 >nul
title 🚀 Iniciar DVDcoin con dvd.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 INICIANDO DVDCOIN CON DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar que cloudflared existe
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    pause
    exit /b 1
)

echo ✅ cloudflared.exe encontrado
echo.

REM Detener procesos anteriores
echo 🛑 Deteniendo procesos anteriores...
taskkill /F /IM cloudflared.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.

REM Iniciar servidor Python
echo 🐍 Iniciando servidor Python en puerto 8000...
start "DVDcoin Server" /MIN python main.py
timeout /t 3 /nobreak >nul
echo ✅ Servidor iniciado
echo.

REM Iniciar túnel Cloudflare
echo 🌐 Iniciando túnel Cloudflare para dvd.ch...
start "Cloudflare Tunnel - dvd.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 5 /nobreak >nul
echo ✅ Túnel iniciado
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 Tu aplicación estará disponible en:
echo.
echo    https://dvd.ch
echo    https://www.dvd.ch
echo.
echo ⏱️  Nota: Si es la primera vez, el DNS puede tardar 2-4 horas
echo     en propagarse. Después de eso, funcionará instantáneamente.
echo.
echo 📊 Para verificar el estado:
echo    VERIFICAR_DVD_CH.bat
echo.
echo 🔍 Para ver logs:
echo    type cloudflare_tunnel.log
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo Presiona cualquier tecla para salir (los servicios seguirán corriendo)...
pause >nul
