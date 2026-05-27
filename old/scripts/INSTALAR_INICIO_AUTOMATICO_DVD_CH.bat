@echo off
chcp 65001 >nul
title ⚙️ Instalar Inicio Automático - dvd.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚙️ INSTALAR INICIO AUTOMÁTICO DE DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará DVDcoin para que se inicie
echo automáticamente cuando arranque Windows.
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo Haz clic derecho en el archivo y selecciona:
    echo "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

REM Obtener la ruta actual
set "SCRIPT_DIR=%~dp0"
set "INICIO_BAT=%SCRIPT_DIR%INICIO.bat"

REM Verificar que INICIO.bat existe
if not exist "%INICIO_BAT%" (
    echo ❌ ERROR: INICIO.bat no encontrado
    echo.
    pause
    exit /b 1
)

echo ✅ INICIO.bat encontrado
echo.

REM Crear VBS para inicio silencioso
echo Creando script de inicio silencioso...
(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.Run chr^(34^) ^& "%INICIO_BAT%" ^& Chr^(34^), 0
    echo Set WshShell = Nothing
) > "%SCRIPT_DIR%inicio_silencioso.vbs"

echo ✅ Script de inicio silencioso creado
echo.

REM Crear acceso directo en la carpeta de inicio
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_FOLDER%\DVDcoin_DVD_CH.lnk"

echo Creando acceso directo en carpeta de inicio...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%SCRIPT_DIR%inicio_silencioso.vbs'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Inicio automático de DVDcoin con dvd.ch'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Acceso directo creado en carpeta de inicio
    echo.
) else (
    echo ❌ ERROR: No se pudo crear el acceso directo
    echo.
    pause
    exit /b 1
)

REM Crear tarea programada como respaldo
echo Creando tarea programada...

schtasks /Create /TN "DVDcoin_DVD_CH_Startup" /TR "\"%INICIO_BAT%\"" /SC ONLOGON /RL HIGHEST /F >nul 2>&1

if errorlevel 1 (
    echo ⚠️  No se pudo crear la tarea programada (no crítico)
) else (
    echo ✅ Tarea programada creada
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ INICIO AUTOMÁTICO INSTALADO
echo ═══════════════════════════════════════════════════════════
echo.
echo DVDcoin se iniciará automáticamente cuando arranque Windows.
echo.
echo 📝 Archivos creados:
echo    - %SHORTCUT%
echo    - %SCRIPT_DIR%inicio_silencioso.vbs
echo.
echo 📊 Tarea programada:
echo    - DVDcoin_DVD_CH_Startup
echo.
echo 🚀 Para probar ahora:
echo    INICIO.bat
echo.
echo 🛑 Para desinstalar:
echo    DESINSTALAR_INICIO_AUTOMATICO_DVD_CH.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
