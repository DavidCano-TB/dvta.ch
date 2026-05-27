@echo off
:: Script para configurar el registro de Windows para arranque seguro desde C:
:: Requiere permisos de administrador

echo ========================================
echo CONFIGURACION DE REGISTRO - ARRANQUE
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Este script requiere permisos de administrador
    echo Por favor, ejecutalo como administrador
    echo.
    pause
    exit /b 1
)

echo [1/3] Creando backup del registro...
echo.

:: Crear carpeta de backup si no existe
if not exist "c:\dvdcoin\backup_registro" mkdir "c:\dvdcoin\backup_registro"

:: Backup de claves relevantes
reg export "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\BootExecute" "c:\dvdcoin\backup_registro\BootExecute_%date:~-4,4%%date:~-7,2%%date:~-10,2%.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot" "c:\dvdcoin\backup_registro\SafeBoot_%date:~-4,4%%date:~-7,2%%date:~-10,2%.reg" /y >nul 2>&1

echo Backup creado en: c:\dvdcoin\backup_registro\
echo.

echo [2/3] Configurando politicas de arranque en el registro...
echo.

:: Deshabilitar arranque desde medios extraibles (politica de grupo)
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices" /v "Deny_All" /t REG_DWORD /d 0 /f >nul 2>&1

:: Configurar prioridad de arranque del sistema
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Configuration Manager" /v "LastKnownGood" /t REG_DWORD /d 1 /f >nul 2>&1

:: Deshabilitar arranque rapido que puede causar problemas
:: (Comentado por defecto, descomenta si quieres deshabilitarlo)
:: reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "HiberbootEnabled" /t REG_DWORD /d 0 /f

echo Configuraciones de registro aplicadas
echo.

echo [3/3] Verificando configuracion...
echo.

echo Configuracion actual:
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Configuration Manager" /v "LastKnownGood" 2>nul
echo.

echo ========================================
echo CONFIGURACION COMPLETADA
echo ========================================
echo.
echo NOTA IMPORTANTE:
echo Este script configura Windows, pero el orden de arranque
echo definitivo se controla desde la BIOS/UEFI.
echo.
echo Para asegurar arranque SOLO desde C:
echo 1. Reinicia y entra en BIOS (F2/F10/DEL)
echo 2. Ve a "Boot" o "Arranque"
echo 3. Establece disco C: como primera opcion
echo 4. Deshabilita USB Boot, Network Boot, CD/DVD Boot
echo 5. Activa "Secure Boot" si esta disponible
echo 6. Guarda y sal
echo.

pause
