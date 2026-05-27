@echo off
chcp 65001 >nul
title DVDCoin Bank - Servidor

echo.
echo ================================================================================
echo   DVDCoin Bank - Iniciando Servidor
echo ================================================================================
echo.

cd /d "%~dp0"

echo Matando procesos anteriores...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Iniciando servidor...
echo.
echo   - Local: http://localhost:8000
echo   - Ngrok: Se mostrara la URL publica en unos segundos
echo.
echo   NO CIERRES ESTA VENTANA
echo   Presiona Ctrl+C para detener
echo.
echo ================================================================================
echo.

python src\start.py

pause
