@echo off
chcp 65001 >nul
cls
echo ================================================================================
echo 🔓 DESBLOQUEAR USUARIOS
echo ================================================================================
echo.
echo Este script limpia los bloqueos de cuenta causados por intentos fallidos.
echo.
pause

python DESBLOQUEAR_USUARIOS.py

pause
