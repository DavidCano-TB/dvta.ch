@echo off
REM ============================================================
REM DESACTIVAR PIN Y CODIGOS AL ARRANQUE DE WINDOWS
REM Requiere permisos de ADMINISTRADOR
REM ============================================================

echo ============================================================
echo DESACTIVAR PIN Y CODIGOS AL ARRANQUE
echo ============================================================
echo.
echo Este script desactivara:
echo - PIN al iniciar sesion
echo - Contraseña al despertar del suspension
echo - Pantalla de bloqueo
echo.
echo IMPORTANTE: Requiere permisos de ADMINISTRADOR
echo.
pause

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Este script requiere permisos de ADMINISTRADOR
    echo.
    echo Haz clic derecho en el archivo y selecciona:
    echo "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo APLICANDO CAMBIOS
echo ============================================================

REM 1. Desactivar requerimiento de contraseña al despertar
echo [1/5] Desactivando contraseña al despertar...
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0 >nul 2>&1
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0 >nul 2>&1
powercfg /SETACTIVE SCHEME_CURRENT >nul 2>&1
echo      [OK] Contraseña al despertar desactivada

REM 2. Desactivar pantalla de bloqueo
echo [2/5] Desactivando pantalla de bloqueo...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization" /v NoLockScreen /t REG_DWORD /d 1 /f >nul 2>&1
echo      [OK] Pantalla de bloqueo desactivada

REM 3. Desactivar requerimiento de contraseña al reanudar
echo [3/5] Desactivando contraseña al reanudar...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Power\PowerSettings\0e796bdb-100d-47d6-a2d5-f7d2daa51f51" /v ACSettingIndex /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Power\PowerSettings\0e796bdb-100d-47d6-a2d5-f7d2daa51f51" /v DCSettingIndex /t REG_DWORD /d 0 /f >nul 2>&1
echo      [OK] Contraseña al reanudar desactivada

REM 4. Desactivar Windows Hello
echo [4/5] Desactivando Windows Hello...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WinBio\Credential Provider" /v Domain /t REG_DWORD /d 0 /f >nul 2>&1
echo      [OK] Windows Hello desactivado

REM 5. Configurar inicio de sesion automatico (opcional)
echo [5/5] Configurar inicio de sesion automatico? (S/N)
set /p AUTOLOGIN="Respuesta: "

if /i "%AUTOLOGIN%"=="S" (
    echo.
    echo Ingresa tus credenciales de Windows:
    set /p USERNAME="Usuario: "
    set /p PASSWORD="Contraseña: "
    
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /t REG_SZ /d 1 /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName /t REG_SZ /d "%USERNAME%" /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /t REG_SZ /d "%PASSWORD%" /f >nul 2>&1
    
    echo      [OK] Inicio de sesion automatico configurado
) else (
    echo      [OMITIDO] Inicio de sesion automatico no configurado
)

echo.
echo ============================================================
echo CAMBIOS APLICADOS CORRECTAMENTE
echo ============================================================
echo.
echo Se han desactivado:
echo [OK] PIN al iniciar sesion
echo [OK] Contraseña al despertar
echo [OK] Pantalla de bloqueo
echo [OK] Windows Hello
if /i "%AUTOLOGIN%"=="S" echo [OK] Inicio de sesion automatico configurado
echo.
echo IMPORTANTE:
echo - Los cambios se aplicaran en el proximo reinicio
echo - Para revertir, ejecuta REACTIVAR_PIN_WINDOWS.bat
echo.
echo Presiona cualquier tecla para salir
pause >nul
