@echo off
chcp 65001 >nul
title VERIFICAR AUTO-ARRANQUE
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICAR CONFIGURACIÓN DE AUTO-ARRANQUE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo Verificando todos los métodos de auto-arranque...
echo.

set METHODS_ACTIVE=0

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MÉTODO 1: TAREA PROGRAMADA DE WINDOWS                                   │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

schtasks /Query /TN "DVDcoin_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ CONFIGURADA
    echo.
    echo Detalles:
    schtasks /Query /TN "DVDcoin_AutoStart" /FO LIST /V | findstr /C:"Nombre de tarea" /C:"Estado" /C:"Última ejecución" /C:"Próxima ejecución" /C:"Ejecutar como"
    set /a METHODS_ACTIVE+=1
) else (
    echo ❌ NO CONFIGURADA
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MÉTODO 2: REGISTRO DE WINDOWS                                           │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ CONFIGURADO
    echo.
    echo Detalles:
    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System"
    set /a METHODS_ACTIVE+=1
) else (
    echo ❌ NO CONFIGURADO
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MÉTODO 3: CARPETA DE INICIO                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if exist "%STARTUP_FOLDER%\DVDcoin System.lnk" (
    echo ✅ CONFIGURADA
    echo.
    echo Ubicación: %STARTUP_FOLDER%\DVDcoin System.lnk
    set /a METHODS_ACTIVE+=1
) else (
    echo ❌ NO CONFIGURADA
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Métodos activos: %METHODS_ACTIVE% de 3
echo.

if %METHODS_ACTIVE% equ 3 (
    echo   ✅ AUTO-ARRANQUE COMPLETAMENTE CONFIGURADO
    echo.
    echo   El sistema se iniciará automáticamente al arrancar Windows
    echo   usando 3 métodos diferentes para máxima confiabilidad.
) else if %METHODS_ACTIVE% gtr 0 (
    echo   ⚠️  AUTO-ARRANQUE PARCIALMENTE CONFIGURADO
    echo.
    echo   Algunos métodos están configurados, pero no todos.
    echo   Para configurar todos los métodos:
    echo     • Ejecuta: CONFIGURAR_AUTOARRANQUE_COMPLETO.bat (como admin)
) else (
    echo   ❌ AUTO-ARRANQUE NO CONFIGURADO
    echo.
    echo   El sistema NO se iniciará automáticamente.
    echo   Para configurar:
    echo     • Ejecuta: CONFIGURAR_AUTOARRANQUE_COMPLETO.bat (como admin)
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
