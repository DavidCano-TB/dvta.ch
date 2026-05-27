@echo off
:: Script maestro para configurar arranque desde disco C:
:: Ejecuta configuracion de BCD y Registro
:: Requiere permisos de administrador

echo ========================================
echo CONFIGURACION COMPLETA DE ARRANQUE
echo Disco C: como predeterminado
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Este script requiere permisos de administrador
    echo.
    echo Haz clic derecho sobre este archivo y selecciona:
    echo "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo Este script configurara Windows para arrancar desde C:
echo.
echo Que hara:
echo - Configurar BCD (Boot Configuration Data)
echo - Establecer disco C: como predeterminado
echo - Ajustar configuraciones de registro
echo - Crear backups de seguridad
echo.
echo IMPORTANTE: La configuracion definitiva requiere
echo cambios en la BIOS que debes hacer manualmente.
echo.
set /p CONTINUAR="Deseas continuar? (S/N): "
if /i not "%CONTINUAR%"=="S" (
    echo Operacion cancelada
    pause
    exit /b 0
)

echo.
echo ========================================
echo PASO 1: CONFIGURACION BCD
echo ========================================
echo.
call "%~dp0CONFIGURAR_ARRANQUE_DISCO_C.bat"

echo.
echo.
echo ========================================
echo PASO 2: CONFIGURACION REGISTRO
echo ========================================
echo.
call "%~dp0CONFIGURAR_REGISTRO_ARRANQUE.bat"

echo.
echo.
echo ========================================
echo CONFIGURACION FINALIZADA
echo ========================================
echo.
echo RESUMEN:
echo [OK] Configuracion BCD actualizada
echo [OK] Registro de Windows configurado
echo [OK] Backups creados
echo.
echo SIGUIENTE PASO - CONFIGURACION BIOS:
echo =====================================
echo Para garantizar que SIEMPRE arranque desde C:
echo.
echo 1. Reinicia el ordenador
echo 2. Presiona repetidamente la tecla de BIOS al iniciar:
echo    - DEL o F2 (placas ASUS, MSI, Gigabyte)
echo    - F10 (HP)
echo    - F12 (Dell)
echo    - ESC (Lenovo, algunos HP)
echo.
echo 3. Busca la seccion "Boot" o "Arranque"
echo.
echo 4. Configura el orden de arranque:
echo    1ra opcion: Windows Boot Manager (disco C:)
echo    Deshabilita o mueve al final:
echo    - USB Boot
echo    - CD/DVD Boot
echo    - Network Boot (PXE)
echo.
echo 5. Opcional pero recomendado:
echo    - Activa "Secure Boot" (arranque seguro)
echo    - Establece contrasena de BIOS
echo.
echo 6. Guarda cambios (normalmente F10) y sal
echo.
echo NOTA: Estos cambios en BIOS son permanentes hasta
echo que tu los cambies manualmente de nuevo.
echo.

pause
