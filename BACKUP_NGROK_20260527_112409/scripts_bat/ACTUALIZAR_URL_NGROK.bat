@echo off
REM ═══════════════════════════════════════════════════════════════
REM  ACTUALIZADOR AUTOMÁTICO DE URL DE NGROK
REM  Obtiene la URL actual de ngrok y actualiza config\ngrok_config.txt
REM ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Si se llama con /SILENT, no mostrar mensajes ni pausar
set SILENT=0
if /i "%1"=="/SILENT" set SILENT=1
if /i "%1"=="-s" set SILENT=1

if %SILENT%==0 (
    title Actualizador URL Ngrok
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ACTUALIZADOR AUTOMÁTICO DE URL DE NGROK
    echo ═══════════════════════════════════════════════════════════════
    echo.
)

cd /d "%~dp0"

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    if %SILENT%==0 (
        echo ❌ Python no está instalado o no está en el PATH
        echo.
        pause
    )
    exit /b 1
)

REM Ejecutar el script de actualización
if %SILENT%==1 (
    python actualizar_url_ngrok.py >nul 2>&1
) else (
    python actualizar_url_ngrok.py
    echo.
    pause
)

exit /b %errorlevel%
