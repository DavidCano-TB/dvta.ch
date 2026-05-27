@echo off
:: Configura el servicio DVDcoinBank con service_launcher.py
:: EJECUTAR COMO ADMINISTRADOR
title DVDcoin - Configurar Servicio
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    exit /b
)

:: Find Python
set PYEXE=
for /f "tokens=*" %%P in ('where python 2^>nul') do (
    if "!PYEXE!"=="" set PYEXE=%%P
)
if "%PYEXE%"=="" (
    echo ERROR: Python no encontrado
    pause & exit /b 1
)
echo Python: %PYEXE%

:: Stop service
echo Deteniendo servicio...
nssm.exe stop DVDcoinBank force >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "0.0.0.0:8000 "') do taskkill /f /pid %%a >nul 2>&1
timeout /t 3 /nobreak >nul

:: Configure service to use service_launcher.py
echo Configurando servicio...
nssm.exe set DVDcoinBank Application "%PYEXE%"
nssm.exe set DVDcoinBank AppParameters "service_launcher.py"
nssm.exe set DVDcoinBank AppDirectory "%~dp0"
nssm.exe set DVDcoinBank AppStdout "%~dp0server.log"
nssm.exe set DVDcoinBank AppStderr "%~dp0server.log"
nssm.exe set DVDcoinBank AppRestartDelay 5000
nssm.exe set DVDcoinBank Start SERVICE_AUTO_START
nssm.exe set DVDcoinBank DisplayName "DVDcoin Bank"
nssm.exe set DVDcoinBank Description "DVDcoin Bank server + ngrok"

:: Start service
echo Iniciando servicio...
nssm.exe start DVDcoinBank
timeout /t 12 /nobreak >nul

:: Verify
echo Verificando...
%PYEXE% -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=8); print('SERVIDOR OK:', r.read().decode())" 2>&1

echo.
echo ============================================================
echo  Servicio configurado. Al reiniciar Windows arrancara solo.
echo  Solo UN proceso Python. Solo UN ngrok.
echo ============================================================
pause
