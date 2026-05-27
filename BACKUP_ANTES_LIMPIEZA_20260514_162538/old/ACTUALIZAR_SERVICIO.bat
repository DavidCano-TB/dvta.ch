@echo off
:: Actualiza el servicio DVDcoinBank para usar Python del sistema
:: EJECUTAR COMO ADMINISTRADOR

title DVDcoin - Actualizar Servicio
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    exit /b
)

echo Buscando Python del sistema...
for /f "tokens=*" %%P in ('where python 2^>nul') do (
    if "%%P" neq "" (
        set PYEXE=%%P
        goto :found
    )
)
:found
echo Python: %PYEXE%

echo Deteniendo servicio...
nssm.exe stop DVDcoinBank force >nul 2>&1
timeout /t 3 /nobreak >nul

echo Actualizando configuracion del servicio...
nssm.exe set DVDcoinBank Application "%PYEXE%"
nssm.exe set DVDcoinBank AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info"
nssm.exe set DVDcoinBank AppDirectory "%~dp0"
nssm.exe set DVDcoinBank AppStdout "%~dp0server.log"
nssm.exe set DVDcoinBank AppStderr "%~dp0server.log"
nssm.exe set DVDcoinBank AppRestartDelay 3000

echo Iniciando servicio...
nssm.exe start DVDcoinBank
timeout /t 8 /nobreak >nul

echo Verificando...
%PYEXE% -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5); print('OK:', r.read().decode())"

echo.
echo Servicio actualizado. Arrancara automaticamente con Windows.
pause
