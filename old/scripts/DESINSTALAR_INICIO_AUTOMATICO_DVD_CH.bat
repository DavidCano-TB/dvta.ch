@echo off
chcp 65001 >nul
title ⚙️ Desinstalar Inicio Automático - dvd.ch
color 0C

echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚙️ DESINSTALAR INICIO AUTOMÁTICO DE DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script eliminará el inicio automático de DVDcoin.
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
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_FOLDER%\DVDcoin_DVD_CH.lnk"
set "VBS_FILE=%SCRIPT_DIR%inicio_silencioso.vbs"

REM Eliminar acceso directo
if exist "%SHORTCUT%" (
    echo Eliminando acceso directo...
    del "%SHORTCUT%" >nul 2>&1
    echo ✅ Acceso directo eliminado
) else (
    echo ℹ️  Acceso directo no encontrado
)
echo.

REM Eliminar archivo VBS
if exist "%VBS_FILE%" (
    echo Eliminando script VBS...
    del "%VBS_FILE%" >nul 2>&1
    echo ✅ Script VBS eliminado
) else (
    echo ℹ️  Script VBS no encontrado
)
echo.

REM Eliminar tarea programada
echo Eliminando tarea programada...
schtasks /Delete /TN "DVDcoin_DVD_CH_Startup" /F >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Tarea programada no encontrada
) else (
    echo ✅ Tarea programada eliminada
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ INICIO AUTOMÁTICO DESINSTALADO
echo ═══════════════════════════════════════════════════════════
echo.
echo DVDcoin ya no se iniciará automáticamente.
echo.
echo Para iniciarlo manualmente:
echo    INICIO.bat
echo.
echo Para reinstalar el inicio automático:
echo    INSTALAR_INICIO_AUTOMATICO_DVD_CH.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
