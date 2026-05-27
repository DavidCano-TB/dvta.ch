@echo off
REM ============================================================
REM ABRIR INSTRUCCIONES Y DOCUMENTACION
REM ============================================================

chcp 65001 >nul
title DVDCoin - Abrir Instrucciones
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN - DOCUMENTACION E INSTRUCCIONES              ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Abriendo documentación...
echo.

REM Abrir el archivo principal de instrucciones
if exist "LEER_ANTES_DE_REINICIAR.txt" (
    start notepad "LEER_ANTES_DE_REINICIAR.txt"
    echo ✓ LEER_ANTES_DE_REINICIAR.txt
    timeout /t 1 /nobreak >nul
)

REM Abrir el tutorial completo
if exist "TUTORIAL_CLOUDFLARE_TUNNEL.md" (
    start notepad "TUTORIAL_CLOUDFLARE_TUNNEL.md"
    echo ✓ TUTORIAL_CLOUDFLARE_TUNNEL.md
    timeout /t 1 /nobreak >nul
)

REM Abrir la guía rápida
if exist "README_CLOUDFLARE.md" (
    start notepad "README_CLOUDFLARE.md"
    echo ✓ README_CLOUDFLARE.md
    timeout /t 1 /nobreak >nul
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo Documentación abierta. Lee las instrucciones antes de continuar.
echo.
echo PRÓXIMO PASO:
echo   1. Lee: LEER_ANTES_DE_REINICIAR.txt
echo   2. Ejecuta como admin: PREPARAR_PARA_REINICIO.bat
echo   3. Reinicia Windows
echo.
timeout /t 10

exit /b 0
