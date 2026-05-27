@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🖥️  CREAR ACCESO DIRECTO EN EL ESCRITORIO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo Creando acceso directo al Menú Principal en el escritorio...
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\DVDBank Menu.lnk"

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = '%~dp0MENU_PRINCIPAL.bat'; $SC.WorkingDirectory = '%~dp0'; $SC.WindowStyle = 1; $SC.Description = 'Menú Principal de DVDBank'; $SC.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Acceso directo creado en el escritorio
    echo.
    echo Nombre: DVDBank Menu.lnk
    echo Ubicación: %DESKTOP%
) else (
    echo ❌ Error al crear el acceso directo
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
