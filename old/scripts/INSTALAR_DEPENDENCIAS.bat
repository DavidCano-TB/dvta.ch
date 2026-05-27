@echo off
REM ============================================================
REM INSTALAR DEPENDENCIAS DE DVDCOIN BANK
REM ============================================================

echo ============================================================
echo INSTALACION DE DEPENDENCIAS
echo ============================================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    echo Por favor, instala Python desde https://www.python.org/
    pause
    exit /b 1
)

python --version
echo [OK] Python instalado

echo.
echo Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no esta instalado
    pause
    exit /b 1
)

echo [OK] pip instalado

echo.
echo ============================================================
echo INSTALANDO DEPENDENCIAS
echo ============================================================
echo.

if exist requirements.txt (
    echo Instalando desde requirements.txt...
    pip install -r requirements.txt
) else (
    echo Instalando dependencias manualmente...
    pip install fastapi uvicorn[standard] python-jose[cryptography] bcrypt pydantic python-multipart slowapi websockets
)

echo.
echo ============================================================
echo VERIFICANDO INSTALACION
echo ============================================================
echo.

echo Verificando uvicorn...
pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uvicorn no se instalo correctamente
    pause
    exit /b 1
)

echo [OK] uvicorn instalado

echo.
echo Verificando fastapi...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [ERROR] fastapi no se instalo correctamente
    pause
    exit /b 1
)

echo [OK] fastapi instalado

echo.
echo ============================================================
echo INSTALACION COMPLETADA
echo ============================================================
echo.
echo Ahora puedes ejecutar:
echo   ARRANCAR.bat
echo   o
echo   ARRANQUE_AUTOMATICO_COMPLETO.bat
echo.
pause
