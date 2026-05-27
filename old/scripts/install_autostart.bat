@echo off
title Instalar DVDcoin Bank - Arranque Automatico
cd /d "%~dp0"

echo ============================================
echo  INSTALANDO ARRANQUE AUTOMATICO
echo ============================================
echo.

REM Obtener la ruta completa del script VBS
set "VBS_PATH=%~dp0start_dvdcoin_hidden.vbs"

REM Obtener la carpeta de inicio de Windows
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Crear un acceso directo en la carpeta de inicio
echo Creando acceso directo en la carpeta de inicio...
echo.

REM Usar PowerShell para crear el acceso directo
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\DVDcoin Bank.lnk'); $Shortcut.TargetPath = '%VBS_PATH%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'DVDcoin Bank - Arranque Automatico'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo  INSTALACION COMPLETADA
    echo ============================================
    echo.
    echo DVDcoin Bank se iniciara automaticamente
    echo cada vez que arranques Windows.
    echo.
    echo Ubicacion del acceso directo:
    echo %STARTUP_FOLDER%\DVDcoin Bank.lnk
    echo.
    echo Para desinstalar, simplemente elimina el
    echo acceso directo de la carpeta de inicio.
    echo.
) else (
    echo ============================================
    echo  ERROR EN LA INSTALACION
    echo ============================================
    echo.
    echo No se pudo crear el acceso directo.
    echo Intenta ejecutar este script como administrador.
    echo.
)

pause
