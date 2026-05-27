@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   INICIANDO DVDCOIN CON CLOUDFLARE TUNNEL TEMPORAL
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script inicia el servidor con una URL temporal gratuita
echo La URL cambiará cada vez que reinicies el túnel
echo.
echo Para una URL permanente, configura un dominio propio
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar si el servidor Python está corriendo
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [1/2] Iniciando servidor Python...
    start /B python main.py
    timeout /t 3 /nobreak >nul
    echo       ✓ Servidor iniciado
) else (
    echo [1/2] Servidor Python ya está corriendo
)

echo.
echo [2/2] Iniciando Cloudflare Tunnel...
echo.
echo ═══════════════════════════════════════════════════════════
echo   OBTENIENDO URL PÚBLICA...
echo ═══════════════════════════════════════════════════════════
echo.

REM Iniciar cloudflared con URL temporal
cloudflared tunnel --url http://localhost:8000

pause
