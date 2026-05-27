@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   OBTENIENDO URL PÚBLICA DE DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar si el servidor está corriendo
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [1/3] Iniciando servidor Python...
    start /B python main.py
    timeout /t 5 /nobreak >nul
    echo       ✓ Servidor iniciado
) else (
    echo [1/3] Servidor Python ya está corriendo
)

echo.
echo [2/3] Iniciando Cloudflare Tunnel temporal...
echo.
echo       Generando URL pública gratuita...
echo       (Esto puede tardar 10-15 segundos)
echo.

REM Crear archivo temporal para capturar la salida
set LOGFILE=%TEMP%\cloudflare_url.log

REM Iniciar cloudflared y capturar la salida
start /B cmd /c "cloudflared tunnel --url http://localhost:8000 > %LOGFILE% 2>&1"

REM Esperar a que se genere la URL
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Extrayendo URL pública...
echo.
echo ═══════════════════════════════════════════════════════════
echo   URL PÚBLICA DE DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

REM Buscar la URL en el log
for /f "tokens=*" %%i in ('findstr /C:"https://" %LOGFILE% 2^>nul') do (
    echo %%i
)

echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo IMPORTANTE:
echo   • Esta URL es TEMPORAL y cambiará al reiniciar
echo   • Para una URL permanente, configura un dominio propio
echo   • El servidor seguirá corriendo en segundo plano
echo.
echo Para detener: DETENER_SERVIDOR.bat
echo.
pause
