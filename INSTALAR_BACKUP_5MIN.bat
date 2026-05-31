@echo off
chcp 65001 >nul
title Instalar Backup cada 5 minutos

echo.
echo ═══════════════════════════════════════════════════════════════
echo   INSTALAR BACKUP CADA 5 MINUTOS (retención 72h)
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Este script requiere permisos de Administrador.
    echo         Haz clic derecho → Ejecutar como administrador
    echo.
    pause
    exit /b 1
)

:: Configurar rutas
set PYTHON_PATH=C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe
set SCRIPT_PATH=C:\dvdcoin\scripts\backup_cada_5min.py

:: Verificar que existen
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python no encontrado en: %PYTHON_PATH%
    pause
    exit /b 1
)
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] Script no encontrado en: %SCRIPT_PATH%
    pause
    exit /b 1
)

echo Creando tarea programada: DVDCoin_Backup_5min
echo   Frecuencia: Cada 5 minutos
echo   Retención: 72 horas
echo   Destino: bdd_copy\
echo.

schtasks /Create /TN "DVDCoin_Backup_5min" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /SC MINUTE /MO 5 /F /RL HIGHEST

if %errorlevel% equ 0 (
    echo.
    echo [OK] Tarea programada creada exitosamente
    echo.
    echo Para verificar:  schtasks /Query /TN "DVDCoin_Backup_5min" /V /FO LIST
    echo Para ejecutar:   schtasks /Run /TN "DVDCoin_Backup_5min"
    echo Para eliminar:   schtasks /Delete /TN "DVDCoin_Backup_5min" /F
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea programada
)

echo.
pause
