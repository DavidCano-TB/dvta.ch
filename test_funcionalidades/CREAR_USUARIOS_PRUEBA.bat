@echo off
chcp 65001 >nul
cls
echo ================================================================================
echo 👥 CREAR USUARIOS DE PRUEBA
echo ================================================================================
echo.
echo Este script creará automáticamente los usuarios necesarios para los tests:
echo   - test_user / test123
echo   - test_user2 / test123
echo.
echo ⚠️  IMPORTANTE: El servidor debe estar ejecutándose
echo.
pause

python CREAR_USUARIOS_PRUEBA.py

pause
