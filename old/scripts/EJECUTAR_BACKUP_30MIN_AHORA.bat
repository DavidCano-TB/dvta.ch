@echo off
chcp 65001 >nul
echo ========================================
echo   BACKUP MANUAL (30 MIN)
echo ========================================
echo.

cd /d "%~dp0"

echo Ejecutando backup...
python scripts\backup_cada_30min.py

echo.
echo ========================================
echo   Backup completado
echo ========================================
echo.
pause
