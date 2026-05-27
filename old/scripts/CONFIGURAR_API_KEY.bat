@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   Configurar ANTHROPIC_API_KEY para Quien Soy   ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo Este script te ayudará a configurar la API key de Anthropic
echo para habilitar la IA en el juego "¿Quién soy?"
echo.
echo Pasos:
echo 1. Visita: https://console.anthropic.com/
echo 2. Crea una cuenta o inicia sesión
echo 3. Ve a "API Keys" y crea una nueva key
echo 4. Copia la key (empieza con sk-ant-...)
echo.
echo ──────────────────────────────────────────────────
echo.

set /p API_KEY="Pega tu API key aquí: "

if "%API_KEY%"=="" (
    echo.
    echo ❌ No se ingresó ninguna API key
    pause
    exit /b 1
)

echo.
echo Configurando...
echo.

REM Opción 1: Variable de entorno permanente
setx ANTHROPIC_API_KEY "%API_KEY%" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✓ API key configurada correctamente
    echo.
    echo ⚠️  IMPORTANTE: Debes REINICIAR el terminal para que tome efecto
    echo.
    echo Después de reiniciar, ejecuta:
    echo   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    echo.
) else (
    echo ❌ Error al configurar la variable de entorno
    echo.
    echo Alternativa: Configura manualmente con:
    echo   set ANTHROPIC_API_KEY=%API_KEY%
    echo.
)

echo ──────────────────────────────────────────────────
echo.
echo 📖 Para más información, lee: docs\QUIEN_SOY_AI_INTEGRATION.md
echo.
pause
