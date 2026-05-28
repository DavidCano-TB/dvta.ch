@echo off
REM ============================================================================
REM DVDcoin Platform - Test Runner
REM Ejecuta todos los tests unitarios con coverage
REM ============================================================================

echo.
echo ========================================================================
echo DVDcoin Platform - Test Suite
echo ========================================================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Instalar dependencias de desarrollo si es necesario
echo [1/4] Verificando dependencias de testing...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias de testing...
    pip install -r requirements-dev.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo [2/4] Instalando dependencias del proyecto...
pip install -r requirements.txt >nul 2>&1
if exist "modules\exams\requirements.txt" (
    pip install -r modules\exams\requirements.txt >nul 2>&1
)

echo [3/4] Ejecutando tests con coverage...
echo.
pytest tests/ -v --cov=modules --cov=main --cov-report=html --cov-report=term-missing --cov-fail-under=100

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo [ERROR] Tests fallidos o coverage insuficiente
    echo ========================================================================
    echo.
    echo Revisa los errores arriba y corrige los tests.
    echo El coverage debe ser 100%% para pasar.
    echo.
    echo Reporte HTML generado en: htmlcov\index.html
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo [SUCCESS] Todos los tests pasaron con 100%% coverage
echo ========================================================================
echo.
echo [4/4] Reporte de coverage generado en: htmlcov\index.html
echo.
echo Para ver el reporte detallado:
echo   start htmlcov\index.html
echo.
pause
