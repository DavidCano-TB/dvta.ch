@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo   🚀 SETUP COMPLETO - Tests DVDcoin Bank
echo ================================================================================
echo.
echo Este script realizará la configuración completa:
echo   1. Preparar archivos de test
echo   2. Instalar dependencias Python
echo   3. Verificar configuración
echo.
pause
echo.

echo ================================================================================
echo   PASO 1/3: Preparando archivos de test...
echo ================================================================================
echo.
python PREPARAR_TESTS.py
echo.

echo ================================================================================
echo   PASO 2/3: Instalando dependencias...
echo ================================================================================
echo.
pip install requests websocket-client pillow
echo.

echo ================================================================================
echo   PASO 3/3: Verificando configuración...
echo ================================================================================
echo.
python VERIFICAR_CONFIGURACION.py
echo.

echo ================================================================================
echo   ✅ SETUP COMPLETADO
echo ================================================================================
echo.
echo IMPORTANTE: Edita config.json con tus credenciales antes de ejecutar los tests
echo.
echo Luego ejecuta: EJECUTAR_TODOS_LOS_TESTS.bat
echo.
pause
