@echo off
REM ============================================================
REM CONFIGURAR INSTALACION AUTOMATICA AL REINICIAR WINDOWS
REM Este script configura la instalación para que se ejecute
REM automáticamente al reiniciar el PC
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    REM Auto-elevar sin preguntar
    powershell -Command "Start-Process '%~f0' -Verb RunAs" >nul 2>&1
    exit /b
)

:admin
chcp 65001 >nul
title DVDCoin - Configurar Instalación al Reinicio
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         CONFIGURAR INSTALACION AL REINICIAR WINDOWS          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Este script configurará la instalación automática de
echo Cloudflare Tunnel para que se ejecute al reiniciar Windows.
echo.
echo ⚠ IMPORTANTE:
echo   - Se eliminará el archivo .cloudflare_instalado
echo   - Al reiniciar, se ejecutará la instalación automática
echo   - El proceso te guiará paso a paso
echo.
echo ¿Deseas continuar? (S/N)
set /p CONTINUE="> "

if /i not "%CONTINUE%"=="S" (
    echo.
    echo Operación cancelada.
    timeout /t 3
    exit /b 0
)

echo.
echo [1/3] Eliminando marca de instalación previa...

if exist "%~dp0.cloudflare_instalado" (
    del "%~dp0.cloudflare_instalado" >nul 2>&1
    echo       ✓ Marca eliminada
) else (
    echo       ○ No había marca previa
)

echo.
echo [2/3] Eliminando tareas de autostart antiguas...

schtasks /delete /tn "DVDcoin-Instalador" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
schtasks /delete /tn "DVDcoin" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Cloudflare" /f >nul 2>&1

echo       ✓ Tareas antiguas eliminadas

echo.
echo [3/3] Creando tarea de instalación al reinicio...

schtasks /create /tn "DVDcoin-Instalador" /f ^
  /tr "\"%~dp0INSTALACION_AUTOMATICA_CLOUDFLARE.bat\"" ^
  /sc ONLOGON ^
  /delay 0000:05 ^
  /rl HIGHEST

if errorlevel 1 (
    echo       ✗ Error al crear tarea
    echo.
    pause
    exit /b 1
)

echo       ✓ Tarea creada correctamente

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ CONFIGURACION COMPLETADA                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ QUE PASARA AL REINICIAR                                      │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   1. Windows se iniciará normalmente
echo   2. 5 segundos después del login
echo   3. Se abrirá una ventana CMD
echo   4. El instalador te guiará paso a paso:
echo      - Verificar Python
echo      - Instalar cloudflared
echo      - Autenticar con Cloudflare
echo      - Crear túnel
echo      - Configurar dominio
echo      - Crear archivo de configuración
echo      - Instalar autostart
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PROXIMOS PASOS                                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   1. Guarda tu trabajo
echo   2. Cierra todas las aplicaciones
echo   3. Reinicia Windows
echo   4. Sigue las instrucciones del instalador
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ¿Quieres reiniciar ahora? (S/N)
set /p RESTART_NOW="> "

if /i "%RESTART_NOW%"=="S" (
    echo.
    echo Reiniciando en 10 segundos...
    echo Presiona Ctrl+C para cancelar
    timeout /t 10
    shutdown /r /t 0
) else (
    echo.
    echo Reinicia Windows cuando estés listo.
    echo La instalación se ejecutará automáticamente.
    echo.
    pause
)

exit /b 0
