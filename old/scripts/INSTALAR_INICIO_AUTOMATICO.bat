@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 INSTALANDO INICIO AUTOMÁTICO CON WINDOWS
echo   Sistema: DVDBank - dvta.ch
echo ═══════════════════════════════════════════════════════════
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

cd /d "%~dp0"

echo MÉTODO 1: Creando tarea programada en Windows...
echo.

REM Eliminar tareas existentes
schtasks /Delete /TN "DVDBank_AutoStart" /F 2>nul
schtasks /Delete /TN "DVDcoin-Autostart" /F 2>nul
schtasks /Delete /TN "DVDcoin" /F 2>nul
schtasks /Delete /TN "DVDcoin-Cloudflare" /F 2>nul

REM Crear nueva tarea programada
schtasks /Create /TN "DVDBank_AutoStart" /TR "\"%~dp0INICIAR_SISTEMA_DVTA.bat\"" /SC ONLOGON /RL HIGHEST /F

if %errorLevel% equ 0 (
    echo    ✅ Tarea programada creada exitosamente
) else (
    echo    ❌ Error al crear tarea programada
)
echo.

echo MÉTODO 2: Agregando al registro de inicio...
echo.

REM Eliminar entradas antiguas
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f 2>nul

REM Agregar nueva entrada
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank_dvta" /t REG_SZ /d "\"%~dp0INICIAR_SISTEMA_DVTA.bat\"" /f

if %errorLevel% equ 0 (
    echo    ✅ Entrada de registro creada exitosamente
) else (
    echo    ❌ Error al crear entrada de registro
)
echo.

echo MÉTODO 3: Creando acceso directo en carpeta de inicio...
echo.

REM Eliminar accesos directos antiguos
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del "%STARTUP_FOLDER%\DVDBank.lnk" 2>nul
del "%STARTUP_FOLDER%\DVDcoin.lnk" 2>nul

REM Crear nuevo acceso directo
set "SHORTCUT=%STARTUP_FOLDER%\DVDBank_dvta.lnk"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = '%~dp0INICIAR_SISTEMA_DVTA.bat'; $SC.WorkingDirectory = '%~dp0'; $SC.WindowStyle = 7; $SC.Description = 'Inicia DVDBank automáticamente (dvta.ch)'; $SC.Save()"

if exist "%SHORTCUT%" (
    echo    ✅ Acceso directo creado en carpeta de inicio
) else (
    echo    ❌ Error al crear acceso directo
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ INSTALACIÓN COMPLETA
echo ═══════════════════════════════════════════════════════════
echo.
echo DVDBank se iniciará automáticamente cuando:
echo   • Inicies sesión en Windows
echo   • Reinicies el ordenador
echo.
echo Se han configurado 3 métodos de inicio automático:
echo   1. ✅ Tarea programada (más confiable)
echo   2. ✅ Registro de Windows
echo   3. ✅ Carpeta de inicio
echo.
echo Para desinstalar el inicio automático:
echo   DESINSTALAR_INICIO_AUTOMATICO.bat
echo.
echo Para probar el inicio ahora:
echo   INICIAR_SISTEMA_DVTA.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
