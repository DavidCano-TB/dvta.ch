@echo off
chcp 65001 >nul
echo ========================================
echo   BACKUP MANUAL DE BASES DE DATOS
echo ========================================
echo.

cd /d "%~dp0"

echo Ejecutando backup...
python scripts\backup_databases.py

echo.
echo ========================================
echo   Backup completado
echo ========================================
echo.
pause
