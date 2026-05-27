@echo off
REM ============================================================
REM CONFIGURAR INICIO AUTOMATICO EN WINDOWS
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:admin
cd /d "%~dp0"

echo ============================================================
echo CONFIGURANDO INICIO AUTOMATICO
echo ============================================================
echo.

REM Crear script de inicio
set STARTUP_SCRIPT=%~dp0INICIO_AUTOMATICO.bat

echo @echo off > "%STARTUP_SCRIPT%"
echo REM Script de inicio automatico >> "%STARTUP_SCRIPT%"
echo. >> "%STARTUP_SCRIPT%"
echo REM Esperar 10 segundos para que Windows termine de cargar >> "%STARTUP_SCRIPT%"
echo timeout /t 10 /nobreak ^>nul >> "%STARTUP_SCRIPT%"
echo. >> "%STARTUP_SCRIPT%"
echo REM Desactivar Windows Defender >> "%STARTUP_SCRIPT%"
echo powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" 2^>nul >> "%STARTUP_SCRIPT%"
echo. >> "%STARTUP_SCRIPT%"
echo REM Ejecutar el script principal >> "%STARTUP_SCRIPT%"
echo cd /d "%~dp0" >> "%STARTUP_SCRIPT%"
echo start "" "%~dp0DESACTIVAR_ANTIVIRUS_Y_ARRANCAR.bat" >> "%STARTUP_SCRIPT%"

echo [OK] Script de inicio creado: INICIO_AUTOMATICO.bat
echo.

REM Agregar al inicio de Windows usando registro
set SCRIPT_PATH=%~dp0INICIO_AUTOMATICO.bat

reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoinBank" /t REG_SZ /d "\"%SCRIPT_PATH%\"" /f >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] Agregado al inicio de Windows (usuario actual)
) else (
    echo [ADVERTENCIA] No se pudo agregar al registro
)

echo.

REM Crear tarea programada como alternativa
schtasks /create /tn "DVDcoin Bank Startup" /tr "\"%SCRIPT_PATH%\"" /sc onlogon /rl highest /f >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] Tarea programada creada
) else (
    echo [ADVERTENCIA] No se pudo crear la tarea programada
)

echo.
echo ============================================================
echo CONFIGURACION DE EXCLUSIONES DE WINDOWS DEFENDER
echo ============================================================
echo.

REM Agregar carpeta a exclusiones de Windows Defender
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0'" 2>nul

if %errorLevel% == 0 (
    echo [OK] Carpeta agregada a exclusiones de Windows Defender
) else (
    echo [ADVERTENCIA] No se pudo agregar a exclusiones
)

REM Agregar procesos a exclusiones
powershell -Command "Add-MpPreference -ExclusionProcess 'python.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'pythonw.exe'" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'ngrok.exe'" 2>nul

echo [OK] Procesos agregados a exclusiones

echo.
echo ============================================================
echo CONFIGURACION COMPLETADA
echo ============================================================
echo.
echo Se han configurado las siguientes opciones:
echo.
echo 1. Script de inicio automatico: INICIO_AUTOMATICO.bat
echo 2. Entrada en el registro de Windows (inicio de sesion)
echo 3. Tarea programada de Windows
echo 4. Exclusiones de Windows Defender para:
echo    - Carpeta: %~dp0
echo    - Procesos: python.exe, pythonw.exe, ngrok.exe
echo.
echo Al reiniciar Windows, el sistema se iniciara automaticamente
echo y Windows Defender estara desactivado.
echo.
echo ============================================================
echo OPCIONES
echo ============================================================
echo.
echo Para DESACTIVAR el inicio automatico, ejecuta:
echo    DESACTIVAR_INICIO_WINDOWS.bat
echo.
pause
