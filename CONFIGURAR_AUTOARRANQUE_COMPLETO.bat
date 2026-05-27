@echo off
chcp 65001 >nul
title CONFIGURAR AUTO-ARRANQUE COMPLETO
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ⚙️  CONFIGURAR AUTO-ARRANQUE COMPLETO CON WINDOWS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script configurará el sistema para que se inicie automáticamente
echo al arrancar Windows usando MÚLTIPLES MÉTODOS para garantizar que funcione:
echo.
echo   1. Tarea Programada de Windows (Método principal)
echo   2. Registro de Windows (Método de respaldo)
echo   3. Carpeta de Inicio (Método adicional)
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
    echo   2. Haz clic derecho en CONFIGURAR_AUTOARRANQUE_COMPLETO.bat
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
echo │  MÉTODO 1: TAREA PROGRAMADA DE WINDOWS                                   │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Eliminar tarea anterior si existe
schtasks /Query /TN "DVDcoin_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo Eliminando tarea anterior...
    schtasks /Delete /TN "DVDcoin_AutoStart" /F >nul 2>&1
    echo ✅ Tarea anterior eliminada
    echo.
)

echo Creando tarea programada...
echo.

REM Crear XML de configuración de la tarea
echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%TEMP%\dvdcoin_task.xml"
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^<RegistrationInfo^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<Description^>Auto-arranque del sistema DVDcoin completo^</Description^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^</RegistrationInfo^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^<Triggers^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<LogonTrigger^> >> "%TEMP%\dvdcoin_task.xml"
echo       ^<Enabled^>true^</Enabled^> >> "%TEMP%\dvdcoin_task.xml"
echo       ^<Delay^>PT30S^</Delay^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^</LogonTrigger^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^</Triggers^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^<Settings^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<AllowHardTerminate^>false^</AllowHardTerminate^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<Enabled^>true^</Enabled^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<Hidden^>false^</Hidden^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<WakeToRun^>false^</WakeToRun^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<Priority^>7^</Priority^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^</Settings^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^<Actions Context="Author"^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^<Exec^> >> "%TEMP%\dvdcoin_task.xml"
echo       ^<Command^>"%~dp0ACTIVAR_DVTA_CH_AHORA.bat"^</Command^> >> "%TEMP%\dvdcoin_task.xml"
echo       ^<WorkingDirectory^>%~dp0^</WorkingDirectory^> >> "%TEMP%\dvdcoin_task.xml"
echo     ^</Exec^> >> "%TEMP%\dvdcoin_task.xml"
echo   ^</Actions^> >> "%TEMP%\dvdcoin_task.xml"
echo ^</Task^> >> "%TEMP%\dvdcoin_task.xml"

REM Importar la tarea
schtasks /Create /TN "DVDcoin_AutoStart" /XML "%TEMP%\dvdcoin_task.xml" /F

if %errorlevel% equ 0 (
    echo ✅ Tarea programada creada exitosamente
    del "%TEMP%\dvdcoin_task.xml" >nul 2>&1
) else (
    echo ❌ ERROR: No se pudo crear la tarea programada
    echo.
    pause
    exit /b 1
)
echo.

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MÉTODO 2: REGISTRO DE WINDOWS (RESPALDO)                                │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Añadiendo entrada al registro de Windows...
echo.

REM Crear entrada en el registro para auto-arranque
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" /t REG_SZ /d "\"%~dp0ACTIVAR_DVTA_CH_AHORA.bat\"" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Entrada de registro creada exitosamente
) else (
    echo ⚠️  No se pudo crear entrada de registro (no crítico)
)
echo.

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  MÉTODO 3: CARPETA DE INICIO (ADICIONAL)                                 │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Creando acceso directo en carpeta de Inicio...
echo.

REM Obtener ruta de carpeta de Inicio
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Crear script VBS para crear acceso directo
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%STARTUP_FOLDER%\DVDcoin System.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%~dp0ACTIVAR_DVTA_CH_AHORA.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "DVDcoin System Auto-Start" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WindowStyle = 7 >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"

if %errorlevel% equ 0 (
    echo ✅ Acceso directo creado en carpeta de Inicio
    del "%TEMP%\CreateShortcut.vbs" >nul 2>&1
) else (
    echo ⚠️  No se pudo crear acceso directo (no crítico)
)
echo.

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  VERIFICACIÓN                                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Verificando configuración...
echo.

REM Verificar tarea programada
schtasks /Query /TN "DVDcoin_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tarea programada: CONFIGURADA
) else (
    echo ❌ Tarea programada: NO CONFIGURADA
)

REM Verificar registro
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin_System" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Registro de Windows: CONFIGURADO
) else (
    echo ⚠️  Registro de Windows: NO CONFIGURADO
)

REM Verificar carpeta de Inicio
if exist "%STARTUP_FOLDER%\DVDcoin System.lnk" (
    echo ✅ Carpeta de Inicio: CONFIGURADA
) else (
    echo ⚠️  Carpeta de Inicio: NO CONFIGURADA
)
echo.

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ AUTO-ARRANQUE CONFIGURADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📋 MÉTODOS CONFIGURADOS:
echo   1. ✅ Tarea Programada de Windows (Principal)
echo   2. ✅ Registro de Windows (Respaldo)
echo   3. ✅ Carpeta de Inicio (Adicional)
echo.
echo 🔄 COMPORTAMIENTO:
echo   • Al iniciar sesión en Windows, el sistema se iniciará automáticamente
echo   • Espera 30 segundos después del login para iniciar
echo   • Se abrirán 2 ventanas: "DVDExams Server" y "Cloudflare Tunnel"
echo   • Las ventanas se pueden minimizar
echo   • El sistema estará disponible en https://dvta.ch
echo.
echo ⏱️  TIEMPO DE INICIO:
echo   • Login en Windows → 30 segundos de espera
echo   • Inicio de servicios → 15-30 segundos
echo   • Total: ~1 minuto después del login
echo.
echo 🛑 PARA DESACTIVAR:
echo   • Ejecuta: ELIMINAR_AUTOARRANQUE_COMPLETO.bat (como admin)
echo.
echo 🧪 PARA PROBAR AHORA:
echo   • Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
echo   • O reinicia Windows
echo.
echo 📊 PARA VERIFICAR ESTADO:
echo   • Ejecuta: STATUS_DVTA.bat
echo   • O ejecuta: MONITOR_SISTEMA.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
