@echo off
title ABRIR APUESTAS VIA NGROK
cd /d "%~dp0"

echo ============================================
echo  OBTENIENDO URL DE NGROK
echo ============================================
echo.

REM Esperar a que ngrok inicie
timeout /t 3 /nobreak >nul

REM Obtener URL de ngrok
echo Consultando API de ngrok...
curl -s http://127.0.0.1:4040/api/tunnels > ngrok_temp.json

REM Extraer URL usando PowerShell
for /f "delims=" %%i in ('powershell -Command "(Get-Content ngrok_temp.json | ConvertFrom-Json).tunnels[0].public_url"') do set NGROK_URL=%%i

del ngrok_temp.json

if "%NGROK_URL%"=="" (
    echo ERROR: No se pudo obtener la URL de ngrok
    echo Asegurate de que ngrok este corriendo
    pause
    exit /b 1
)

echo URL de ngrok: %NGROK_URL%
echo.

REM Obtener token
echo Obteniendo token de sesion...
for /f "delims=" %%i in ('python -c "import sqlite3; c=sqlite3.connect('data/users.db'); r=c.execute('SELECT jwt_token FROM users WHERE username=\"dvd\"').fetchone(); print(r[0] if r else '')"') do set TOKEN=%%i

if "%TOKEN%"=="" (
    echo ADVERTENCIA: No se pudo obtener el token
    echo Abriendo sin autenticacion...
    set FULL_URL=%NGROK_URL%/apuestas
) else (
    echo Token obtenido correctamente
    set FULL_URL=%NGROK_URL%/apuestas?token=%TOKEN%
)

echo.
echo ============================================
echo  ABRIENDO NAVEGADOR
echo ============================================
echo.
echo URL completa: %FULL_URL%
echo.

start "" "%FULL_URL%"

echo.
echo URLs disponibles:
echo   - Lista: %NGROK_URL%/apuestas?token=%TOKEN%
echo   - Porra 1: %NGROK_URL%/apuestas/porra/1?token=%TOKEN%
echo   - Porra 2: %NGROK_URL%/apuestas/porra/2?token=%TOKEN%
echo   - Porra 3: %NGROK_URL%/apuestas/porra/3?token=%TOKEN%
echo.
pause
