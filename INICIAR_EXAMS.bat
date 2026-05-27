@echo off
echo ========================================
echo   DVDcoin Exams - Iniciar Servidor
echo ========================================
echo.

cd modules\exams

echo Verificando dependencias...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Dependencias no instaladas
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

echo.
echo Iniciando servidor en puerto 8001...
echo.
echo Accede a: http://localhost:8001
echo.
echo Presiona Ctrl+C para detener
echo.

python app_exams.py

pause
