@echo off
echo ========================================
echo REINICIANDO SERVIDOR DVDCOIN
echo ========================================
echo.

echo [1/3] Deteniendo procesos antiguos...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Liberar puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Matando proceso en puerto 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul
echo OK - Procesos detenidos
echo.

echo [2/3] Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo OK - Puerto 8000 libre
) else (
    echo ADVERTENCIA - Puerto 8000 todavia en uso
    echo Intenta cerrar manualmente el proceso o reiniciar el PC
)
echo.

echo [3/3] Iniciando servidor...
echo Ejecuta ARRANCAR.bat para iniciar el servidor
echo.
pause
