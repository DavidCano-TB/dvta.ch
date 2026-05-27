@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Matando procesos...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1

timeout /t 3 /nobreak >nul

echo Iniciando servidor...
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000

timeout /t 8 /nobreak >nul

echo Iniciando ngrok...
start /B ngrok http 8000 --domain=premium-size-unreached.ngrok-free.dev

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo SERVIDOR REINICIADO
echo ========================================
echo.
echo URL: https://premium-size-unreached.ngrok-free.dev
echo Login: dvd / 3666
echo.
