@echo off
chcp 65001 >nul

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ========================================
    echo   SE REQUIEREN PERMISOS DE ADMINISTRADOR
    echo ========================================
    echo.
    echo Este script necesita ejecutarse como Administrador
    echo para crear la tarea programada.
    echo.
    echo Haz clic derecho en el archivo y selecciona
    echo "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   CONFIGURAR BACKUP CADA 30 MINUTOS
echo ========================================
echo.

cd /d "%~dp0"

python scripts\configurar_backup_30min.py

echo.
pause
