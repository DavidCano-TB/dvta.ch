@echo off
chcp 65001 >nul
title Instalación Completa Automática - DVDBank
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 INSTALACIÓN COMPLETA AUTOMÁTICA - DVDBANK
echo   Sistema: dvta.ch con Cloudflare Tunnel
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

cd /d "%~dp0"

echo Este script realizará la instalación completa:
echo   1. Configurar inicio automático con Windows
echo   2. Configurar arranque desde disco C:
echo   3. Mover archivos ngrok a backup
echo   4. Verificar el sistema
echo.
set /p CONFIRMAR="¿Deseas continuar? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo.
    echo ❌ Instalación cancelada
    echo.
    pause
    exit /b 0
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1/4: Configurando inicio automático con Windows
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Eliminar tareas existentes
schtasks /Delete /TN "DVDBank_AutoStart" /F 2>nul
schtasks /Delete /TN "DVDcoin-Autostart" /F 2>nul
schtasks /Delete /TN "DVDcoin" /F 2>nul
schtasks /Delete /TN "DVDcoin-Cloudflare" /F 2>nul

REM Crear nueva tarea programada
schtasks /Create /TN "DVDBank_AutoStart" /TR "\"%~dp0INICIAR_SISTEMA_DVTA.bat\"" /SC ONLOGON /RL HIGHEST /F >nul 2>&1

if %errorLevel% equ 0 (
    echo    ✅ Tarea programada creada
) else (
    echo    ⚠️  Error al crear tarea programada
)

REM Eliminar entradas antiguas del registro
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f 2>nul

REM Agregar nueva entrada
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank_dvta" /t REG_SZ /d "\"%~dp0INICIAR_SISTEMA_DVTA.bat\"" /f >nul 2>&1

if %errorLevel% equ 0 (
    echo    ✅ Entrada de registro creada
) else (
    echo    ⚠️  Error al crear entrada de registro
)

REM Eliminar accesos directos antiguos
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del "%STARTUP_FOLDER%\DVDBank.lnk" 2>nul
del "%STARTUP_FOLDER%\DVDcoin.lnk" 2>nul

REM Crear nuevo acceso directo
set "SHORTCUT=%STARTUP_FOLDER%\DVDBank_dvta.lnk"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = '%~dp0INICIAR_SISTEMA_DVTA.bat'; $SC.WorkingDirectory = '%~dp0'; $SC.WindowStyle = 7; $SC.Description = 'Inicia DVDBank automáticamente (dvta.ch)'; $SC.Save()" >nul 2>&1

if exist "%SHORTCUT%" (
    echo    ✅ Acceso directo creado
) else (
    echo    ⚠️  Error al crear acceso directo
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2/4: Configurando arranque desde disco C:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Obtener el identificador del gestor de arranque de Windows
for /f "tokens=2 delims={}" %%i in ('bcdedit /enum ^| findstr /C:"identifier" ^| findstr /C:"{bootmgr}"') do (
    set BOOTMGR_ID={%%i}
)

if defined BOOTMGR_ID (
    bcdedit /default %BOOTMGR_ID% >nul 2>&1
    if %errorLevel% equ 0 (
        echo    ✅ Gestor de arranque configurado
    ) else (
        echo    ⚠️  No se pudo configurar el gestor de arranque
    )
) else (
    echo    ⚠️  No se pudo identificar el gestor de arranque
)

bcdedit /timeout 5 >nul 2>&1
if %errorLevel% equ 0 (
    echo    ✅ Tiempo de espera configurado (5 segundos)
) else (
    echo    ⚠️  No se pudo configurar el tiempo de espera
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3/4: Moviendo archivos ngrok a backup
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set "BACKUP_FOLDER=BACKUP_NGROK_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_FOLDER=%BACKUP_FOLDER: =0%"

if not exist "%BACKUP_FOLDER%" (
    mkdir "%BACKUP_FOLDER%" 2>nul
    mkdir "%BACKUP_FOLDER%\scripts_bat" 2>nul
    mkdir "%BACKUP_FOLDER%\scripts_py" 2>nul
    mkdir "%BACKUP_FOLDER%\config" 2>nul
    
    move "*ngrok*.bat" "%BACKUP_FOLDER%\scripts_bat\" >nul 2>&1
    move "*ngrok*.py" "%BACKUP_FOLDER%\scripts_py\" >nul 2>&1
    move "actualizar_url_ngrok.py" "%BACKUP_FOLDER%\scripts_py\" >nul 2>&1
    
    if exist "conf\.ngrok_token" move "conf\.ngrok_token" "%BACKUP_FOLDER%\config\" >nul 2>&1
    if exist "config\ngrok_config.txt" move "config\ngrok_config.txt" "%BACKUP_FOLDER%\config\" >nul 2>&1
    if exist "ngrok_url.txt" move "ngrok_url.txt" "%BACKUP_FOLDER%\config\" >nul 2>&1
    if exist "ngrok.exe" move "ngrok.exe" "%BACKUP_FOLDER%\" >nul 2>&1
    
    echo    ✅ Archivos ngrok movidos a: %BACKUP_FOLDER%
) else (
    echo    ℹ️  Backup ya existe, omitiendo...
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4/4: Verificando sistema
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "INICIAR_SISTEMA_DVTA.bat" (
    echo    ✅ Script de inicio: OK
) else (
    echo    ❌ Script de inicio: NO ENCONTRADO
)

if exist "main.py" (
    echo    ✅ Servidor Python: OK
) else (
    echo    ❌ Servidor Python: NO ENCONTRADO
)

if exist "cloudflare-dvta-config.yml" (
    echo    ✅ Configuración Cloudflare: OK
) else (
    echo    ⚠️  Configuración Cloudflare: Pendiente
)

if exist "cloudflared.exe" (
    echo    ✅ cloudflared.exe: Instalado
) else (
    echo    ⚠️  cloudflared.exe: No instalado
    echo       Descarga: https://github.com/cloudflare/cloudflared/releases
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ INSTALACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Configuración aplicada:
echo   ✅ Inicio automático con Windows (3 métodos)
echo   ✅ Arranque desde disco C: configurado
echo   ✅ Archivos ngrok movidos a backup
echo   ✅ Sistema verificado
echo.
echo Próximos pasos:
echo   1. Reinicia Windows para probar el inicio automático
echo   2. O ejecuta manualmente: INICIAR_SISTEMA_DVTA.bat
echo   3. Verifica el estado: VER_ESTADO_SISTEMA.bat
echo.
echo Cuando el dominio dvta.ch esté activo en Cloudflare:
echo   • Ejecuta: CONFIGURAR_EMAIL_CLOUDFLARE.bat
echo   • Ejecuta: CONFIGURAR_TUNNEL_DVTA.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
