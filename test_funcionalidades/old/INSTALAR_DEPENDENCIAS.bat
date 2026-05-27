@echo off
chcp 65001 >nul
echo ================================================================================
echo 📦 INSTALAR DEPENDENCIAS PARA TESTS
echo ================================================================================
echo.

echo Instalando dependencias de Python...
python -m pip install websocket-client requests Pillow

echo.
echo ================================================================================
echo ✅ INSTALACIÓN COMPLETADA
echo ================================================================================
echo.
echo Ahora puedes ejecutar: EJECUTAR_TODOS_LOS_TESTS.bat
echo.
pause
