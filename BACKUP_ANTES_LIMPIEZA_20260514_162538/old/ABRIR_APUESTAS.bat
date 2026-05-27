@echo off
title ABRIR SISTEMA DE APUESTAS
cd /d "%~dp0"

echo ============================================
echo  ABRIENDO SISTEMA DE APUESTAS
echo ============================================
echo.

REM Obtener el token del usuario dvd
echo [1/2] Obteniendo token de sesion...
for /f "delims=" %%i in ('python -c "import sqlite3; c=sqlite3.connect('data/users.db'); r=c.execute('SELECT token FROM users WHERE username=\"dvd\"').fetchone(); print(r[0] if r else '')"') do set TOKEN=%%i

if "%TOKEN%"=="" (
    echo ERROR: No se pudo obtener el token
    echo Abriendo sin token...
    set URL=http://127.0.0.1:8000/apuestas
) else (
    echo Token obtenido correctamente
    set URL=http://127.0.0.1:8000/apuestas?token=%TOKEN%
)

echo.
echo [2/2] Abriendo navegador...
echo URL: %URL%
echo.

start "" "%URL%"

echo.
echo ============================================
echo  NAVEGADOR ABIERTO
echo ============================================
echo.
echo URLs disponibles:
echo   - Lista de porras: %URL%
echo   - Porra 1: http://127.0.0.1:8000/apuestas/porra/1?token=%TOKEN%
echo   - Porra 2: http://127.0.0.1:8000/apuestas/porra/2?token=%TOKEN%
echo   - Porra 3: http://127.0.0.1:8000/apuestas/porra/3?token=%TOKEN%
echo.
pause
