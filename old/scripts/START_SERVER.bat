@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Limpiando procesos anteriores...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo Iniciando servidor en puerto 8000...
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000

timeout /t 8 /nobreak >nul

echo.
echo Iniciando ngrok...
start /B ngrok http 8000 --domain=premium-size-unreached.ngrok-free.dev

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo SERVIDOR INICIADO
echo ========================================
echo.
echo Local:   http://localhost:8000
echo Publico: https://premium-size-unreached.ngrok-free.dev
echo.
echo Presiona cualquier tecla para salir...
pause >nul
