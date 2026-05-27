@echo off
:: Aplica todos los cambios y reinicia DVDcoin correctamente
:: Ejecutar como Administrador

title DVDcoin - Aplicar Cambios
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    goto :check_result
)

echo ============================================
echo  DVDcoin - Aplicando cambios
echo ============================================
echo.

:: Find Python
set PYTHON=
for /f "tokens=*" %%P in ('where python 2^>nul') do (
    if "!PYTHON!"=="" set PYTHON=%%P
)
if "%PYTHON%"=="" set PYTHON=python

echo [1/5] Python: %PYTHON%

:: Stop service
echo [2/5] Deteniendo servicio DVDcoinBank...
nssm.exe stop DVDcoinBank force >nul 2>&1
sc stop DVDcoinBank >nul 2>&1
timeout /t 3 /nobreak >nul

:: Kill any remaining process on port 8000
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "0.0.0.0:8000 "') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: Update NSSM service to use system Python
echo [3/5] Actualizando servicio para usar Python del sistema...
nssm.exe set DVDcoinBank Application "%PYTHON%" >nul 2>&1
nssm.exe set DVDcoinBank AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info" >nul 2>&1
nssm.exe set DVDcoinBank AppDirectory "%~dp0" >nul 2>&1

:: Install missing deps if needed
echo [4/5] Verificando dependencias...
%PYTHON% -c "import fastapi,uvicorn,bcrypt,jose,pydantic,slowapi,multipart" >nul 2>&1
if errorlevel 1 (
    echo     Instalando dependencias...
    %PYTHON% -m pip install -r "%~dp0requirements.txt" --quiet
)

:: Start service
echo [5/5] Iniciando servicio...
nssm.exe start DVDcoinBank >nul 2>&1
if errorlevel 1 (
    sc start DVDcoinBank >nul 2>&1
)
timeout /t 8 /nobreak >nul

:: Verify
%PYTHON% -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5); print('SERVIDOR OK:', r.read().decode())" 2>&1
%PYTHON% -c "import urllib.request,urllib.error
try:
    urllib.request.urlopen('http://127.0.0.1:8000/api/ice-servers',timeout=3)
except urllib.error.HTTPError as e:
    print('ICE endpoint:', 'OK (HTTP %d)' % e.code if e.code != 404 else 'ERROR 404')
except Exception as e:
    print('ICE endpoint error:', e)" 2>&1

echo.
echo ============================================
echo  Listo. Cambios aplicados.
echo ============================================
pause
exit /b 0

:check_result
echo.
echo Si ves errores arriba, ejecuta este bat como Administrador.
pause
