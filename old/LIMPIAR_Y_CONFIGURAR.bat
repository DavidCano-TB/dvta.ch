@echo off
:: ============================================================
:: LIMPIAR_Y_CONFIGURAR.bat
:: Elimina TODOS los mecanismos de arranque duplicados y deja
:: solo el servicio DVDcoinBank configurado correctamente.
:: EJECUTAR COMO ADMINISTRADOR
:: ============================================================
title DVDcoin - Limpieza y Configuracion
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    exit /b
)

echo.
echo ============================================================
echo  DVDcoin - Limpieza de arranques duplicados
echo ============================================================
echo.

:: ── 1. Eliminar entrada de registro (causa doble arranque) ──
echo [1/6] Eliminando entrada de registro...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin-Bank" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin-Bank" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDcoin" /f >nul 2>&1
echo    OK - Registro limpiado

:: ── 2. Eliminar tarea programada duplicada ──────────────────
echo [2/6] Eliminando tareas programadas duplicadas...
schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
schtasks /delete /tn "DVDcoin" /f >nul 2>&1
echo    OK - Tareas eliminadas

:: ── 3. Matar todos los procesos actuales ────────────────────
echo [3/6] Deteniendo procesos actuales...
nssm.exe stop DVDcoinBank force >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "0.0.0.0:8000 "') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 3 /nobreak >nul
echo    OK - Procesos detenidos

:: ── 4. Encontrar Python del sistema ─────────────────────────
echo [4/6] Buscando Python del sistema...
set PYEXE=
for /f "tokens=*" %%P in ('where python 2^>nul') do (
    if "%%P" neq "" if "!PYEXE!"=="" set PYEXE=%%P
)
if "%PYEXE%"=="" (
    echo    ERROR: Python no encontrado en PATH
    pause
    exit /b 1
)
echo    OK - Python: %PYEXE%

:: ── 5. Configurar servicio DVDcoinBank con Python del sistema
echo [5/6] Configurando servicio DVDcoinBank...
nssm.exe set DVDcoinBank Application "%PYEXE%"
nssm.exe set DVDcoinBank AppParameters "start.py"
nssm.exe set DVDcoinBank AppDirectory "%~dp0"
nssm.exe set DVDcoinBank AppStdout "%~dp0server.log"
nssm.exe set DVDcoinBank AppStderr "%~dp0server.log"
nssm.exe set DVDcoinBank AppRestartDelay 5000
nssm.exe set DVDcoinBank Start SERVICE_AUTO_START
:: Importante: solo una instancia
nssm.exe set DVDcoinBank AppThrottle 1500
echo    OK - Servicio configurado

:: ── 6. Iniciar el servicio ───────────────────────────────────
echo [6/6] Iniciando servicio...
nssm.exe start DVDcoinBank
timeout /t 10 /nobreak >nul

:: Verificar
%PYEXE% -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5); print('   SERVIDOR OK:', r.read().decode())" 2>&1

echo.
echo ============================================================
echo  CONFIGURACION COMPLETADA
echo.
echo  - Registro de inicio: ELIMINADO
echo  - Tarea programada:   ELIMINADA
echo  - Servicio Windows:   DVDcoinBank (unico mecanismo)
echo  - Arranque:           start.py (servidor + ngrok)
echo  - Al reiniciar PC:    el servicio arranca automaticamente
echo ============================================================
echo.
pause
