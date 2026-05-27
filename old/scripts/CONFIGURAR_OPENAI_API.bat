@echo off
title Configurar OpenAI API Key
cd /d "%~dp0"

echo.
echo ========================================
echo   CONFIGURAR OPENAI API KEY
echo ========================================
echo.
echo Este script configurara la API key de OpenAI
echo para que la IA del juego "Quien Soy" funcione.
echo.
echo Necesitas obtener tu API key desde:
echo https://platform.openai.com/api-keys
echo.
echo ========================================
echo.

set /p API_KEY="Ingresa tu OpenAI API Key: "

if "%API_KEY%"=="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" (
    echo.
    echo ERROR: No ingresaste ninguna API key
    pause
    exit /b 1
)

echo.
echo Guardando API key en config\.openai_key...
echo %API_KEY%> config\.openai_key

echo.
echo Configurando variable de entorno del sistema...
setx OPENAI_API_KEY "%API_KEY%"

echo.
echo ========================================
echo   CONFIGURACION COMPLETADA
echo ========================================
echo.
echo La API key ha sido guardada en:
echo   - config\.openai_key
echo   - Variable de entorno del sistema
echo.
echo IMPORTANTE: Debes REINICIAR el servidor para
echo que los cambios surtan efecto.
echo.
echo Ejecuta: ARRANCAR.bat
echo.
pause
