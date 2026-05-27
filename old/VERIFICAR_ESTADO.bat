@echo off
title Verificar Estado - DVDcoin Bank
cd /d "%~dp0"

echo ============================================
echo  VERIFICANDO ESTADO DE DVDCOIN BANK
echo ============================================
echo.

REM Verificar si el servidor está corriendo en el puerto 8000
echo [1/3] Verificando servidor local (puerto 8000)...
netstat -ano | findstr ":8000" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Servidor activo en http://localhost:8000
) else (
    echo   [ERROR] Servidor NO esta corriendo
    echo   Ejecuta ARRANCAR.bat para iniciar el servidor
)
echo.

REM Verificar si ngrok está corriendo
echo [2/3] Verificando ngrok (puerto 4040)...
netstat -ano | findstr ":4040" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] ngrok activo
    echo.
    echo [3/3] Obteniendo URL publica de ngrok...
    
    REM Obtener URL de ngrok
    curl -s http://127.0.0.1:4040/api/tunnels > ngrok_temp.json 2>nul
    
    REM Extraer URL usando PowerShell
    for /f "delims=" %%i in ('powershell -Command "try { (Get-Content ngrok_temp.json | ConvertFrom-Json).tunnels[0].public_url } catch { '' }"') do set NGROK_URL=%%i
    
    del ngrok_temp.json 2>nul
    
    if not "%NGROK_URL%"=="" (
        echo   [OK] URL publica: %NGROK_URL%
        echo.
        echo ============================================
        echo  SISTEMA FUNCIONANDO CORRECTAMENTE
        echo ============================================
        echo.
        echo URLs disponibles:
        echo   - Local:   http://localhost:8000
        echo   - Publica: %NGROK_URL%
        echo.
    ) else (
        echo   [ADVERTENCIA] No se pudo obtener la URL de ngrok
        echo   Pero el tunel esta activo
        echo.
    )
) else (
    echo   [ERROR] ngrok NO esta corriendo
    echo   Ejecuta ARRANCAR.bat para iniciar ngrok
    echo.
)

REM Verificar arranque automático
echo.
echo [EXTRA] Verificando arranque automatico...
set "SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DVDcoin Bank.lnk"
if exist "%SHORTCUT_PATH%" (
    echo   [OK] Arranque automatico INSTALADO
    echo   La aplicacion se iniciara con Windows
) else (
    echo   [INFO] Arranque automatico NO instalado
    echo   Ejecuta install_autostart.bat para instalarlo
)

echo.
echo ============================================
pause
