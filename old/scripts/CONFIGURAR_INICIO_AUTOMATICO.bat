@echo off
REM ============================================================
REM CONFIGURAR INICIO AUTOMATICO - DVDCoin Bank
REM Configura KILL_ALL_AND_START_FAST.bat como unico script
REM ============================================================

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ============================================================
    echo   REQUIERE PERMISOS DE ADMINISTRADOR
    echo ============================================================
    echo.
    echo Este script necesita permisos de administrador para:
    echo   - Eliminar tareas programadas antiguas
    echo   - Crear nueva tarea programada
    echo   - Modificar el registro de Windows
    echo.
    echo Reiniciando como administrador...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cls
chcp 65001 >nul
title Configurar Inicio Automatico - DVDCoin Bank

echo.
echo ============================================================
echo   CONFIGURAR INICIO AUTOMATICO - DVDCoin Bank
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] Eliminando tareas programadas antiguas...
schtasks /query /fo LIST | findstr /I "DVDcoin" > temp_tasks.txt
for /f "tokens=2 delims=:" %%a in ('findstr /I "Nombre de tarea" temp_tasks.txt') do (
    set "taskname=%%a"
    setlocal enabledelayedexpansion
    set "taskname=!taskname:~1!"
    schtasks /delete /tn "!taskname!" /f >nul 2>&1
    echo       Eliminada: !taskname!
    endlocal
)
del temp_tasks.txt >nul 2>&1
echo       OK

echo.
echo [2/5] Limpiando registro de inicio...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoinBank" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoinBank" /f >nul 2>&1
echo       OK

echo.
echo [3/5] Creando nueva tarea programada...
schtasks /create /tn "DVDcoin_StartFast" /tr "\"%~dp0KILL_ALL_AND_START_FAST.bat\"" /sc onlogon /rl highest /f >nul 2>&1
if %errorlevel%==0 (
    echo       OK - Tarea creada: DVDcoin_StartFast
) else (
    echo       ERROR - No se pudo crear la tarea
)

echo.
echo [4/5] Verificando configuracion...
schtasks /query /tn "DVDcoin_StartFast" >nul 2>&1
if %errorlevel%==0 (
    echo       OK - Tarea configurada correctamente
) else (
    echo       ERROR - Tarea no encontrada
)

echo.
echo [5/5] Configuracion completada
echo       OK

echo.
echo ============================================================
echo   CONFIGURACION COMPLETADA
echo ============================================================
echo.
echo La tarea "DVDcoin_StartFast" se ejecutara automaticamente:
echo   - Al iniciar sesion en Windows
echo   - Con permisos elevados
echo   - Ejecutando: KILL_ALL_AND_START_FAST.bat
echo.
echo El script eliminara automaticamente cualquier otra ejecucion
echo de DVDCoin y sera el UNICO que se ejecute.
echo.
echo ============================================================
echo   OPCIONES
echo ============================================================
echo.
echo 1. Probar ahora (ejecutar KILL_ALL_AND_START_FAST.bat)
echo 2. Ver tareas programadas
echo 3. Deshabilitar inicio automatico
echo 4. Salir
echo.
set /p OPCION="Selecciona una opcion (1-4): "

if "%OPCION%"=="1" (
    echo.
    echo Ejecutando KILL_ALL_AND_START_FAST.bat...
    call KILL_ALL_AND_START_FAST.bat
    exit /b
)

if "%OPCION%"=="2" (
    echo.
    echo Abriendo Programador de tareas...
    taskschd.msc
    pause
    exit /b
)

if "%OPCION%"=="3" (
    echo.
    echo Deshabilitando inicio automatico...
    schtasks /delete /tn "DVDcoin_StartFast" /f >nul 2>&1
    echo OK - Inicio automatico deshabilitado
    pause
    exit /b
)

echo.
echo Saliendo...
timeout /t 2 /nobreak >nul
exit /b
