@echo off
chcp 65001 >nul
echo ========================================
echo   LIMPIAR BACKUPS ANTIGUOS
echo ========================================
echo.

cd /d "%~dp0"

python scripts\limpiar_backups_antiguos.py

echo.
pause
