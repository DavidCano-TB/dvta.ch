echo off
chcp 65001 >nul
title DVDcoin Bank v4.0 - Backend

echo ========================================================
echo          DVDcoin Bank v4.0 - Iniciando servidor
echo ========================================================
echo.

:: ==================== CONFIGURACIÓN ====================
set PYTHON=python
set PORT=8000
set HOST=0.0.0.0

:: Cambia aquí si usas python3 o una ruta específica
:: set PYTHON=C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe

:: ==================== MATAR PROCESOS ANTIGUOS ====================
echo [1/4] Matando procesos antiguos en puerto %PORT%...
netstat -ano | findstr :%PORT% >nul
if %errorlevel%==0 (
    netstat -ano | findstr :%PORT% > temp_port_pids.txt
    for /f "tokens=5" %%a in (temp_port_pids.txt) do (
        taskkill /F /PID %%a >nul 2>&1
    )
    del temp_port_pids.txt 2>nul
    timeout /t 2 >nul
)

:: ==================== VERIFICAR QUE main.py EXISTE ====================
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py en esta carpeta.
    echo Asegúrate de estar en la carpeta correcta.
    pause
    exit /b 1
)

:: ==================== INICIAR EL SERVIDOR ====================
echo [2/4] Iniciando servidor FastAPI en http://localhost:%PORT% ...
echo.

%PYTHON% -m uvicorn main:app ^
    --host %HOST% ^
    --port %PORT% ^
    --workers 1 ^
    --log-level info ^
    --proxy-headers ^
    --forwarded-allow-ips "*"

:: Si uvicorn falla (por ejemplo, python no está en PATH), intentar método alternativo
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] uvicorn falló. Intentando con python -m directamente...
    %PYTHON% main.py
)

echo.
echo ========================================================
echo Servidor detenido.
pause