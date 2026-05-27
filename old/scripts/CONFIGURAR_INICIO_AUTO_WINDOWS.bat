@echo off
REM ============================================================
REM CONFIGURAR INICIO AUTOMATICO EN WINDOWS
REM DVDcoin + ngrok se iniciaran automaticamente al arrancar
REM ============================================================

echo ============================================================
echo CONFIGURAR INICIO AUTOMATICO DE DVDCOIN
echo ============================================================
echo.
echo Este script creara un acceso directo en la carpeta de inicio
echo para que DVDcoin y ngrok se inicien automaticamente al arrancar Windows.
echo.
pause

echo.
echo ============================================================
echo CREANDO ACCESO DIRECTO
echo ============================================================

REM Obtener ruta de la carpeta de inicio
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Obtener ruta del script
set SCRIPT_PATH=%CD%\KILL_ALL_AND_RESTART.bat

REM Crear acceso directo usando PowerShell
echo Creando acceso directo en: %STARTUP_FOLDER%
echo.

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%STARTUP_FOLDER%\DVDcoin_AutoStart.lnk'); $SC.TargetPath = '%SCRIPT_PATH%'; $SC.WorkingDirectory = '%CD%'; $SC.WindowStyle = 7; $SC.Description = 'Inicio automatico de DVDcoin Bank + ngrok'; $SC.Save()"

if exist "%STARTUP_FOLDER%\DVDcoin_AutoStart.lnk" (
    echo [OK] Acceso directo creado correctamente
    echo.
    echo Ubicacion: %STARTUP_FOLDER%\DVDcoin_AutoStart.lnk
    echo Script: %SCRIPT_PATH%
) else (
    echo [ERROR] No se pudo crear el acceso directo
    echo.
    echo Verifica que tienes permisos de escritura en:
    echo %STARTUP_FOLDER%
    pause
    exit /b 1
)

echo.
echo ============================================================
echo CONFIGURACION COMPLETADA
echo ============================================================
echo.
echo [OK] DVDcoin se iniciara automaticamente al arrancar Windows
echo.
echo IMPORTANTE:
echo - Al reiniciar Windows, DVDcoin y ngrok se iniciaran automaticamente
echo - El navegador se abrira con la URL de ngrok
echo - El proceso tardara unos 10-15 segundos
echo.
echo Para desactivar el inicio automatico:
echo - Ve a: %STARTUP_FOLDER%
echo - Elimina el archivo: DVDcoin_AutoStart.lnk
echo.
echo Presiona cualquier tecla para salir
pause >nul
