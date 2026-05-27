@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🗑️  LIMPIEZA DE ARCHIVOS NGROK (MIGRACIÓN A CLOUDFLARE)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo Este script moverá todos los archivos relacionados con ngrok a una carpeta
echo de backup, ya que el sistema ahora usa Cloudflare Tunnel.
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
echo Creando carpeta de backup...
set "BACKUP_FOLDER=BACKUP_NGROK_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_FOLDER=%BACKUP_FOLDER: =0%"
mkdir "%BACKUP_FOLDER%" 2>nul
mkdir "%BACKUP_FOLDER%\scripts_bat" 2>nul
mkdir "%BACKUP_FOLDER%\scripts_py" 2>nul
mkdir "%BACKUP_FOLDER%\config" 2>nul
echo    ✅ Carpeta creada: %BACKUP_FOLDER%
echo.

echo Moviendo archivos .bat relacionados con ngrok...
move "*ngrok*.bat" "%BACKUP_FOLDER%\scripts_bat\" 2>nul
echo    ✅ Archivos .bat movidos
echo.

echo Moviendo archivos .py relacionados con ngrok...
move "*ngrok*.py" "%BACKUP_FOLDER%\scripts_py\" 2>nul
move "actualizar_url_ngrok.py" "%BACKUP_FOLDER%\scripts_py\" 2>nul
echo    ✅ Archivos .py movidos
echo.

echo Moviendo archivos de configuración...
if exist "conf\.ngrok_token" move "conf\.ngrok_token" "%BACKUP_FOLDER%\config\" 2>nul
if exist "config\ngrok_config.txt" move "config\ngrok_config.txt" "%BACKUP_FOLDER%\config\" 2>nul
if exist "ngrok_url.txt" move "ngrok_url.txt" "%BACKUP_FOLDER%\config\" 2>nul
echo    ✅ Archivos de configuración movidos
echo.

echo Moviendo ejecutable ngrok.exe (si existe)...
if exist "ngrok.exe" move "ngrok.exe" "%BACKUP_FOLDER%\" 2>nul
echo    ✅ Ejecutable movido
echo.

echo Creando archivo README en el backup...
(
echo ═══════════════════════════════════════════════════════════════════════════
echo   BACKUP DE ARCHIVOS NGROK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Fecha: %date% %time%
echo.
echo Este backup contiene todos los archivos relacionados con ngrok que fueron
echo utilizados antes de la migración a Cloudflare Tunnel.
echo.
echo NUEVO SISTEMA:
echo   • Dominio: dvta.ch
echo   • Tecnología: Cloudflare Tunnel
echo   • Script de inicio: INICIAR_SISTEMA_DVTA.bat
echo.
echo ARCHIVOS EN ESTE BACKUP:
echo   • scripts_bat\: Scripts .bat de ngrok
echo   • scripts_py\: Scripts Python de ngrok
echo   • config\: Archivos de configuración de ngrok
echo   • ngrok.exe: Ejecutable de ngrok (si existía)
echo.
echo Para restaurar ngrok (no recomendado):
echo   1. Copia los archivos de vuelta a c:\dvdcoin\
echo   2. Ejecuta los scripts de ngrok manualmente
echo.
echo ═══════════════════════════════════════════════════════════════════════════
) > "%BACKUP_FOLDER%\README.txt"
echo    ✅ README creado
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ LIMPIEZA COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Archivos movidos a: %BACKUP_FOLDER%
echo.
echo El sistema ahora usa exclusivamente Cloudflare Tunnel.
echo.
echo Scripts principales:
echo   • INICIAR_SISTEMA_DVTA.bat - Iniciar el sistema
echo   • DETENER_SISTEMA.bat - Detener el sistema
echo   • VER_ESTADO_SISTEMA.bat - Ver estado en tiempo real
echo   • INSTALAR_INICIO_AUTOMATICO.bat - Configurar inicio automático
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
