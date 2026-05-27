@echo off
chcp 65001 >nul
title DVDcoin Exams - Servidor
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DVDcoin Exams - Iniciar Servidor
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0\modules\exams"

echo [1/2] Verificando dependencias...
python -c "import fastapi, uvicorn, pydantic" 2>nul
if errorlevel 1 (
    echo      ⚠️  Instalando dependencias...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo      ❌ Error instalando dependencias
        pause
        exit /b 1
    )
    echo      ✅ Dependencias instaladas
) else (
    echo      ✅ Dependencias OK
)
echo.

echo [2/2] Iniciando servidor...
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   Servidor iniciando en:
echo     • Local:    http://localhost:8001
echo     • External: https://dvta.ch
echo.
echo   Presiona Ctrl+C para detener
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python start_exams.py

if errorlevel 1 (
    echo.
    echo ❌ Error al iniciar el servidor
    pause
)

cd ..\..
