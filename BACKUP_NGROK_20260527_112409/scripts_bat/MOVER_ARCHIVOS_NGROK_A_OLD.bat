@echo off
REM ============================================================
REM DVDCOIN - MOVER ARCHIVOS DE NGROK A CARPETA OLD
REM Limpia archivos antiguos de ngrok
REM ============================================================

chcp 65001 >nul
title DVDCoin - Mover archivos ngrok a OLD
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN - LIMPIAR ARCHIVOS DE NGROK                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Crear carpeta OLD_NGROK si no existe
if not exist "OLD_NGROK" (
    mkdir "OLD_NGROK"
    echo ✓ Carpeta OLD_NGROK creada
)

echo.
echo Moviendo archivos relacionados con ngrok...
echo.

REM Mover archivos .bat de ngrok
if exist "INICIAR_COMO_ADMIN_NGROK_OLD.bat" (
    move /Y "INICIAR_COMO_ADMIN_NGROK_OLD.bat" "OLD_NGROK\" >nul 2>&1
    echo   ✓ INICIAR_COMO_ADMIN_NGROK_OLD.bat
)

if exist "ACTUALIZAR_URL_NGROK.bat" (
    move /Y "ACTUALIZAR_URL_NGROK.bat" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ACTUALIZAR_URL_NGROK.bat
)

if exist "ARREGLAR_NGROK_AHORA.bat" (
    move /Y "ARREGLAR_NGROK_AHORA.bat" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ARREGLAR_NGROK_AHORA.bat
)

REM Mover scripts Python de ngrok
if exist "actualizar_url_ngrok.py" (
    move /Y "actualizar_url_ngrok.py" "OLD_NGROK\" >nul 2>&1
    echo   ✓ actualizar_url_ngrok.py
)

if exist "update_ngrok_yml.py" (
    move /Y "update_ngrok_yml.py" "OLD_NGROK\" >nul 2>&1
    echo   ✓ update_ngrok_yml.py
)

if exist "verificar_config_ngrok.py" (
    move /Y "verificar_config_ngrok.py" "OLD_NGROK\" >nul 2>&1
    echo   ✓ verificar_config_ngrok.py
)

REM Mover logs de ngrok
if exist "ngrok.log" (
    move /Y "ngrok.log" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ngrok.log
)

if exist "ngrok_*.log" (
    move /Y ngrok_*.log "OLD_NGROK\" >nul 2>&1
    echo   ✓ ngrok_*.log
)

if exist "ngrok_tunnels.json" (
    move /Y "ngrok_tunnels.json" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ngrok_tunnels.json
)

if exist "ngrok_api.json" (
    move /Y "ngrok_api.json" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ngrok_api.json
)

if exist "ngrok_url.txt" (
    move /Y "ngrok_url.txt" "OLD_NGROK\" >nul 2>&1
    echo   ✓ ngrok_url.txt
)

REM Mover ejecutable de ngrok (opcional)
if exist "ngrok.exe" (
    echo.
    echo ¿Quieres mover también ngrok.exe? (S/N)
    set /p MOVE_EXE="> "
    if /i "%MOVE_EXE%"=="S" (
        move /Y "ngrok.exe" "OLD_NGROK\" >nul 2>&1
        echo   ✓ ngrok.exe movido
    ) else (
        echo   ○ ngrok.exe mantenido (por si acaso)
    )
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ✓ Archivos de ngrok movidos a OLD_NGROK\
echo.
echo Ahora DVDcoin usa Cloudflare Tunnel exclusivamente.
echo.
echo Para iniciar el servidor:
echo   ARRANCAR.bat  (ahora usa Cloudflare)
echo   INICIAR_CON_CLOUDFLARE.bat
echo.
pause
