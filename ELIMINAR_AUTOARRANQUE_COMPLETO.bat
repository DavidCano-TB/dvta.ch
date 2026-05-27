@echo off
chcp 65001 >nul
title ELIMINAR AUTO-ARRANQUE COMPLETO
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🗑️  ELIMINAR AUTO-ARRANQUE COMPLETO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script eliminará TODOS los métodos de auto-arranque configurados:
echo.
echo   1. Tarea Programada de Windows
echo   2. Registro de Windows
echo   3. Carpeta de Inicio
echo.
echo IMPORTANTE: Requiere permisos de administrador
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo SOLUCIÓN:
    echo   1. Cierra esta ventana
    echo   2. Haz clic derecho en ELIMINAR_AUTOARRANQUE_COMPLETO.bat
    echo   3. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  ELIMINANDO CONFIGURACIONES                                              │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Eliminar tarea programada
echo [1/3] Eliminando tarea programada...
schtasks /Query /TN "DVDcoin_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    schtasks /Delete /TN "DVDcoin_AutoStart" /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo      ✅ Tarea programada eliminada
    ) else (
        echo      ❌ Error al eliminar tarea programada
    )
) else (
    echo      ⚠️  Tarea programada no existía
)
echo.

REM Eliminar entrada del registro
echo [2/3] Eliminando entrada del registro...
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" >nul 2>&1
if %errorlevel% equ 0 (
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" /f >nul 2>&1
    if %errorlevel% equ 0 (
        echo      ✅ Entrada de registro eliminada
    ) else (
        echo      ❌ Error al eliminar entrada de registro
    )
) else (
    echo      ⚠️  Entrada de registro no existía
)
echo.

REM Eliminar acceso directo de carpeta de Inicio
echo [3/3] Eliminando acceso directo de carpeta de Inicio...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if exist "%STARTUP_FOLDER%\DVDcoin System.lnk" (
    del "%STARTUP_FOLDER%\DVDcoin System.lnk" >nul 2>&1
    if %errorlevel% equ 0 (
        echo      ✅ Acceso directo eliminado
    ) else (
        echo      ❌ Error al eliminar acceso directo
    )
) else (
    echo      ⚠️  Acceso directo no existía
)
echo.

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  VERIFICACIÓN                                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Verificando eliminación...
echo.

set ALL_REMOVED=1

REM Verificar tarea programada
schtasks /Query /TN "DVDcoin_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ Tarea programada: AÚN EXISTE
    set ALL_REMOVED=0
) else (
    echo ✅ Tarea programada: ELIMINADA
)

REM Verificar registro
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ Registro de Windows: AÚN EXISTE
    set ALL_REMOVED=0
) else (
    echo ✅ Registro de Windows: ELIMINADO
)

REM Verificar carpeta de Inicio
if exist "%STARTUP_FOLDER%\DVDcoin System.lnk" (
    echo ❌ Carpeta de Inicio: AÚN EXISTE
    set ALL_REMOVED=0
) else (
    echo ✅ Carpeta de Inicio: ELIMINADA
)
echo.

if %ALL_REMOVED% equ 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ AUTO-ARRANQUE COMPLETAMENTE ELIMINADO
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo 📋 RESULTADO:
    echo   • Tarea Programada: ELIMINADA
    echo   • Registro de Windows: ELIMINADO
    echo   • Carpeta de Inicio: ELIMINADA
    echo.
    echo 🔄 COMPORTAMIENTO:
    echo   • El sistema NO se iniciará automáticamente al arrancar Windows
    echo   • Deberás ejecutar ACTIVAR_DVTA_CH_AHORA.bat manualmente
    echo.
    echo 🔄 PARA REACTIVAR:
    echo   • Ejecuta: CONFIGURAR_AUTOARRANQUE_COMPLETO.bat (como admin)
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ⚠️  ELIMINACIÓN PARCIAL
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Algunas configuraciones no se pudieron eliminar.
    echo.
    echo SOLUCIÓN MANUAL:
    echo.
    echo 1. Tarea Programada:
    echo    • Abre: Programador de tareas (taskschd.msc)
    echo    • Busca: DVDcoin_AutoStart
    echo    • Elimina la tarea
    echo.
    echo 2. Registro de Windows:
    echo    • Abre: Editor de registro (regedit)
    echo    • Ve a: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    echo    • Elimina: DVDcoin_System
    echo.
    echo 3. Carpeta de Inicio:
    echo    • Abre: %STARTUP_FOLDER%
    echo    • Elimina: DVDcoin System.lnk
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
)

pause
