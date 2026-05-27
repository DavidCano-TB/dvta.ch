@echo off
title Desinstalar DVDcoin Bank - Arranque Automatico
cd /d "%~dp0"

echo ============================================
echo  DESINSTALANDO ARRANQUE AUTOMATICO
echo ============================================
echo.

REM Obtener la carpeta de inicio de Windows
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\DVDcoin Bank.lnk"

REM Verificar si existe el acceso directo
if exist "%SHORTCUT_PATH%" (
    echo Eliminando acceso directo...
    del "%SHORTCUT_PATH%"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ============================================
        echo  DESINSTALACION COMPLETADA
        echo ============================================
        echo.
        echo DVDcoin Bank ya no se iniciara automaticamente
        echo al arrancar Windows.
        echo.
    ) else (
        echo.
        echo ============================================
        echo  ERROR AL ELIMINAR
        echo ============================================
        echo.
        echo No se pudo eliminar el acceso directo.
        echo Intenta eliminarlo manualmente desde:
        echo %SHORTCUT_PATH%
        echo.
    )
) else (
    echo.
    echo ============================================
    echo  NO INSTALADO
    echo ============================================
    echo.
    echo No se encontro el acceso directo de arranque automatico.
    echo Es posible que ya haya sido eliminado.
    echo.
)

pause
