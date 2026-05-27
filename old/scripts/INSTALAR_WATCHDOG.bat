@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ═══════════════════════════════════════════════════════════════════
:: DVDcoin - Instalador de Watchdog Monitor
:: Configura el watchdog para arrancar automáticamente con Windows
:: ═══════════════════════════════════════════════════════════════════

title DVDcoin - Instalar Watchdog Monitor

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   DVDcoin - Instalador de Watchdog Monitor
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Este script requiere permisos de administrador.
    echo.
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ✅ Permisos de administrador verificados
echo.

:: Obtener rutas
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%dvdcoin_bank_windows\venv\Scripts\python.exe"
set "WATCHDOG_SCRIPT=%SCRIPT_DIR%watchdog_monitor.py"
set "WATCHDOG_WRAPPER=%SCRIPT_DIR%INICIAR_WATCHDOG.bat"

:: Verificar que Python existe
if not exist "%PYTHON_EXE%" (
    echo ❌ ERROR: No se encontró Python en: %PYTHON_EXE%
    echo.
    echo Por favor, ejecuta primero CONFIGURAR_SERVICIO_FINAL.bat
    pause
    exit /b 1
)

echo ✅ Python encontrado: %PYTHON_EXE%

:: Verificar que el script watchdog existe
if not exist "%WATCHDOG_SCRIPT%" (
    echo ❌ ERROR: No se encontró watchdog_monitor.py
    pause
    exit /b 1
)

echo ✅ Script watchdog encontrado
echo.

:: Crear el script wrapper si no existe
echo 📝 Creando script de inicio del watchdog...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%SCRIPT_DIR%"
echo start /min "" "%PYTHON_EXE%" "%WATCHDOG_SCRIPT%"
) > "%WATCHDOG_WRAPPER%"

echo ✅ Script wrapper creado: INICIAR_WATCHDOG.bat
echo.

:: Instalar como tarea programada
echo 📋 Instalando tarea programada de Windows...
echo.

:: Eliminar tarea existente si existe
schtasks /query /tn "DVDcoin_Watchdog" >nul 2>&1
if %errorLevel% equ 0 (
    echo Eliminando tarea existente...
    schtasks /delete /tn "DVDcoin_Watchdog" /f >nul 2>&1
)

:: Crear nueva tarea programada
schtasks /create ^
    /tn "DVDcoin_Watchdog" ^
    /tr "\"%WATCHDOG_WRAPPER%\"" ^
    /sc onstart ^
    /ru "SYSTEM" ^
    /rl highest ^
    /f

if %errorLevel% equ 0 (
    echo ✅ Tarea programada creada exitosamente
    echo.
    echo 📌 Configuración:
    echo    - Nombre: DVDcoin_Watchdog
    echo    - Se ejecuta: Al iniciar Windows
    echo    - Usuario: SYSTEM
    echo    - Prioridad: Alta
    echo.
) else (
    echo ❌ ERROR al crear la tarea programada
    echo.
    pause
    exit /b 1
)

:: Preguntar si iniciar ahora
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
set /p START_NOW="¿Deseas iniciar el watchdog ahora? (S/N): "

if /i "%START_NOW%"=="S" (
    echo.
    echo 🚀 Iniciando watchdog...
    start "" "%WATCHDOG_WRAPPER%"
    timeout /t 3 >nul
    echo ✅ Watchdog iniciado
) else (
    echo.
    echo ℹ️  El watchdog se iniciará automáticamente en el próximo reinicio
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   ✅ INSTALACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 📊 El watchdog monitoreará el servidor cada 5 minutos
echo 🔄 Si detecta 2 fallos consecutivos (10 min), reiniciará el PC
echo 📝 Los logs se guardan en: logs\watchdog.log
echo.
echo Para ver el estado del watchdog:
echo    - Abre el Administrador de tareas
echo    - Busca "python.exe" ejecutando watchdog_monitor.py
echo.
echo Para desinstalar:
echo    - Ejecuta: DESINSTALAR_WATCHDOG.bat
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
