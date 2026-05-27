@echo off
:: Instala DVDcoin Bank como tarea de inicio automatico en Windows
:: EJECUTAR COMO ADMINISTRADOR

title DVDcoin — Instalar Autostart
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Ejecuta este archivo como Administrador.
    echo  Clic derecho ^> "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo [1/3] Eliminando tareas antiguas...
schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
schtasks /delete /tn "DVDcoin" /f >nul 2>&1
echo       OK

echo.
echo [2/3] Creando tarea de inicio automatico...

:: Find Python
set PYTHON=
python --version >nul 2>&1 && set PYTHON=python
if "%PYTHON%"=="" py --version >nul 2>&1 && set PYTHON=py

if "%PYTHON%"=="" (
    echo ERROR: Python no encontrado.
    pause
    exit /b 1
)

:: Get full python path
for /f "tokens=*" %%P in ('%PYTHON% -c "import sys; print(sys.executable)"') do set PYEXE=%%P

:: Create the scheduled task
schtasks /create /tn "DVDcoin-Autostart" /f ^
  /tr "\"%PYEXE%\" \"%~dp0start.py\"" ^
  /sc ONLOGON ^
  /delay 0000:10 ^
  /rl HIGHEST ^
  /it

if %errorlevel% equ 0 (
    echo       Tarea creada correctamente.
) else (
    echo       Error creando tarea. Revisa permisos.
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando...
schtasks /query /tn "DVDcoin-Autostart" /fo LIST 2>&1 | findstr /i "nom\|estado\|prox\|nom de"
echo.
echo ============================================================
echo   OK  DVDcoin arrancara automaticamente al iniciar Windows
echo       Archivo de arranque: start.py
echo       Servidor:            main.py
echo ============================================================
echo.
pause
