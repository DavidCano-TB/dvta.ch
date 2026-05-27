@echo off
chcp 65001 >nul
cls
echo ================================================================================
echo 🚀 INICIO RÁPIDO - Suite de Tests DVDcoin Bank
echo ================================================================================
echo.
echo Este script te guiará para configurar y ejecutar los tests.
echo.
pause

echo.
echo ================================================================================
echo 📦 PASO 1: Instalar Dependencias
echo ================================================================================
echo.
python -m pip install websocket-client requests Pillow
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo ================================================================================
echo 🔧 PASO 2: Preparar Tests
echo ================================================================================
echo.
python PREPARAR_TESTS.py
if errorlevel 1 (
    echo ❌ Error preparando tests
    pause
    exit /b 1
)
echo ✅ Tests preparados

echo.
echo ================================================================================
echo 🔍 PASO 3: Verificar Servidor
echo ================================================================================
echo.
echo ⚠️  IMPORTANTE: Asegúrate de que el servidor DVDcoin Bank esté ejecutándose
echo.
echo    Para iniciar el servidor, ejecuta en otra ventana:
echo    ARRANCAR.bat
echo.
echo ¿Está el servidor ejecutándose? (S/N)
set /p respuesta="> "
if /i not "%respuesta%"=="S" (
    echo.
    echo ⚠️  Por favor, inicia el servidor primero y vuelve a ejecutar este script
    pause
    exit /b 0
)

echo.
echo ================================================================================
echo 👥 PASO 4: Crear Usuarios de Prueba
echo ================================================================================
echo.
python CREAR_USUARIOS_PRUEBA.py
if errorlevel 1 (
    echo.
    echo ⚠️  Hubo problemas creando usuarios
    echo    Puedes crearlos manualmente o continuar si ya existen
    echo.
    pause
)

echo.
echo ================================================================================
echo 🔓 PASO 5: Desbloquear Usuarios
echo ================================================================================
echo.
echo Limpiando bloqueos de cuenta...
python DESBLOQUEAR_USUARIOS.py

echo.
echo ================================================================================
echo 🧪 PASO 6: Ejecutar Tests
echo ================================================================================
echo.
echo Ejecutando suite completa de tests...
echo.
python RUN_ALL_TESTS.py

echo.
echo ================================================================================
echo 📊 TESTS COMPLETADOS
echo ================================================================================
echo.
echo Revisa los logs en cada carpeta de test para más detalles.
echo El resumen general está en: logs\test_summary_*.json
echo.
pause
