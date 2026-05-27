@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   💾 CONFIGURAR ARRANQUE DESDE DISCO C:
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Este script requiere permisos de administrador.
    echo.
    echo Por favor:
    echo   1. Haz clic derecho en este archivo
    echo   2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo Este script configurará Windows para arrancar desde el disco C:
echo.
echo ⚠️  IMPORTANTE:
echo    • Esto modificará la configuración de arranque de Windows
echo    • El cambio es reversible desde la BIOS
echo    • Solo afecta al orden de arranque en Windows, no en BIOS
echo.
set /p CONFIRMAR="¿Deseas continuar? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo.
    echo ❌ Operación cancelada
    echo.
    pause
    exit /b 0
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Identificando discos disponibles
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

wmic diskdrive get Index,Caption,Size /format:table
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Verificando configuración de arranque actual
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

bcdedit /enum firmware
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Configurando disco C: como predeterminado
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Obtener el identificador del gestor de arranque de Windows
for /f "tokens=2 delims={}" %%i in ('bcdedit /enum ^| findstr /C:"identifier" ^| findstr /C:"{bootmgr}"') do (
    set BOOTMGR_ID={%%i}
)

if defined BOOTMGR_ID (
    echo Configurando gestor de arranque: %BOOTMGR_ID%
    bcdedit /default %BOOTMGR_ID%
    
    if %errorLevel% equ 0 (
        echo    ✅ Configuración aplicada correctamente
    ) else (
        echo    ⚠️  No se pudo cambiar la configuración
    )
) else (
    echo    ⚠️  No se pudo identificar el gestor de arranque
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4: Configurando tiempo de espera del menú de arranque
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Configurando tiempo de espera a 5 segundos...
bcdedit /timeout 5

if %errorLevel% equ 0 (
    echo    ✅ Tiempo de espera configurado
) else (
    echo    ⚠️  No se pudo configurar el tiempo de espera
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 5: Verificando configuración final
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

bcdedit /enum | findstr /C:"default" /C:"timeout"
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Windows está configurado para arrancar desde C: por defecto.
echo.
echo 📝 NOTAS IMPORTANTES:
echo.
echo 1. Esta configuración afecta al gestor de arranque de Windows (bootmgr)
echo.
echo 2. Para cambiar el orden de arranque en BIOS/UEFI:
echo    • Reinicia el PC
echo    • Presiona F2, F10, F12 o DEL (depende del fabricante)
echo    • Ve a "Boot Order" o "Orden de arranque"
echo    • Mueve el disco C: a la primera posición
echo    • Guarda y sal (F10)
echo.
echo 3. Si tienes múltiples sistemas operativos:
echo    • Esta configuración solo afecta a Windows
echo    • El orden en BIOS/UEFI sigue siendo el mismo
echo.
echo 4. Para revertir esta configuración:
echo    • Ejecuta: bcdedit /default {current}
echo    • O cambia el orden en BIOS
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
