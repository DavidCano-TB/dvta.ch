@echo off
:: Reinicia el servicio DVDcoinBank con los cambios actualizados
:: EJECUTAR COMO ADMINISTRADOR

title DVDcoin - Reiniciar Servicio
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/4] Deteniendo servicio DVDcoinBank...
nssm.exe stop DVDcoinBank force >nul 2>&1
sc stop DVDcoinBank >nul 2>&1
taskkill /f /pid 108 >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/4] Verificando puerto libre...
netstat -ano 2>nul | findstr "0.0.0.0:8000 " > temp_port_check.txt
for /f "tokens=5" %%a in (temp_port_check.txt) do (
    taskkill /f /pid %%a >nul 2>&1
)
del temp_port_check.txt 2>nul
timeout /t 2 /nobreak >nul

echo [3/4] Reiniciando servicio...
nssm.exe restart DVDcoinBank >nul 2>&1
if errorlevel 1 (
    sc start DVDcoinBank >nul 2>&1
)
timeout /t 6 /nobreak >nul

echo [4/4] Verificando...
python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5); print('OK:', r.read().decode())" 2>&1

echo.
echo Listo. Servidor reiniciado con los cambios aplicados.
pause
