@echo off
chcp 65001 >nul
cd /d "%~dp0"
title DVDCoin - Reinicio Completo

echo ========================================
echo REINICIO COMPLETO DEL SISTEMA
echo ========================================
echo.

echo [1/5] Matando procesos anteriores...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
echo       OK - Procesos terminados
timeout /t 3 /nobreak >nul

echo.
echo [2/5] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo       OK - Puerto liberado
timeout /t 2 /nobreak >nul

echo.
echo [3/5] Iniciando servidor Python...
start /B pythonw -m uvicorn src.main:app --host 0.0.0.0 --port 8000 >server.log 2>&1
echo       Esperando que el servidor arranque...
timeout /t 10 /nobreak >nul

REM Verificar que el servidor responde
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo       ERROR: El servidor no arranco en el puerto 8000
    echo       Revisa server.log para mas detalles
    pause
    exit /b 1
) else (
    echo       OK - Servidor corriendo en puerto 8000
)

echo.
echo [4/5] Iniciando ngrok...
start /B ngrok http 8000 --domain=premium-size-unreached.ngrok-free.dev --log=stdout >ngrok.log 2>&1
echo       Esperando que ngrok se conecte...
timeout /t 8 /nobreak >nul
echo       OK - Ngrok iniciado

echo.
echo [5/5] Verificando conexion...
curl -s -o nul -w "%%{http_code}" http://localhost:8000 >temp_status.txt 2>&1
set /p STATUS=<temp_status.txt
del temp_status.txt >nul 2>&1

if "%STATUS%"=="200" (
    echo       OK - Servidor responde correctamente
) else (
    echo       ADVERTENCIA: Servidor responde con codigo %STATUS%
)

echo.
echo ========================================
echo SISTEMA INICIADO
echo ========================================
echo.
echo Local:   http://localhost:8000
echo Publico: https://premium-size-unreached.ngrok-free.dev
echo Panel:   http://localhost:4040
echo.
echo Abriendo navegador...
start https://premium-size-unreached.ngrok-free.dev
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
