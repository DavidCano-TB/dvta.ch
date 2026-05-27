@echo off
chcp 65001 >nul
title Backup del Sistema DVDBank
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   💾 BACKUP DEL SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Crear nombre de carpeta de backup con timestamp
set "BACKUP_FOLDER=BACKUP_SISTEMA_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_FOLDER=%BACKUP_FOLDER: =0%"

echo Creando backup en: %BACKUP_FOLDER%
echo.

REM Crear estructura de carpetas
mkdir "%BACKUP_FOLDER%" 2>nul
mkdir "%BACKUP_FOLDER%\data" 2>nul
mkdir "%BACKUP_FOLDER%\config" 2>nul
mkdir "%BACKUP_FOLDER%\logs" 2>nul
mkdir "%BACKUP_FOLDER%\scripts" 2>nul

echo [1/5] Copiando bases de datos...
xcopy "data\*.db" "%BACKUP_FOLDER%\data\" /Y /Q >nul 2>&1
if %errorLevel% equ 0 (
    echo    ✅ Bases de datos copiadas
) else (
    echo    ⚠️  Error al copiar bases de datos
)

echo [2/5] Copiando archivos de configuración...
if exist "cloudflare-dvta-config.yml" copy "cloudflare-dvta-config.yml" "%BACKUP_FOLDER%\config\" >nul 2>&1
if exist "config\jwt_secret.txt" copy "config\jwt_secret.txt" "%BACKUP_FOLDER%\config\" >nul 2>&1
if exist "conf\.jwt_secret" copy "conf\.jwt_secret" "%BACKUP_FOLDER%\config\" >nul 2>&1
echo    ✅ Configuración copiada

echo [3/5] Copiando logs...
xcopy "logs\*.log" "%BACKUP_FOLDER%\logs\" /Y /Q >nul 2>&1
echo    ✅ Logs copiados

echo [4/5] Copiando scripts principales...
copy "INICIAR_SISTEMA_DVTA.bat" "%BACKUP_FOLDER%\scripts\" >nul 2>&1
copy "DETENER_SISTEMA.bat" "%BACKUP_FOLDER%\scripts\" >nul 2>&1
copy "VER_ESTADO_SISTEMA.bat" "%BACKUP_FOLDER%\scripts\" >nul 2>&1
copy "INSTALAR_INICIO_AUTOMATICO.bat" "%BACKUP_FOLDER%\scripts\" >nul 2>&1
copy "main.py" "%BACKUP_FOLDER%\scripts\" >nul 2>&1
echo    ✅ Scripts copiados

echo [5/5] Creando archivo de información...
(
echo ═══════════════════════════════════════════════════════════════════════════
echo   BACKUP DEL SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Fecha: %date% %time%
echo Sistema: DVDBank - dvta.ch
echo.
echo CONTENIDO DEL BACKUP:
echo   • data\          → Bases de datos SQLite
echo   • config\        → Archivos de configuración
echo   • logs\          → Archivos de log
echo   • scripts\       → Scripts principales
echo.
echo PARA RESTAURAR:
echo   1. Detén el sistema: DETENER_SISTEMA.bat
echo   2. Copia los archivos de data\ a c:\dvdcoin\data\
echo   3. Copia los archivos de config\ a c:\dvdcoin\config\
echo   4. Reinicia: INICIAR_SISTEMA_DVTA.bat
echo.
echo BASES DE DATOS INCLUIDAS:
dir /B data 2>nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
) > "%BACKUP_FOLDER%\README.txt"
echo    ✅ Información creada

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ BACKUP COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Backup guardado en: %BACKUP_FOLDER%
echo.

REM Mostrar tamaño del backup
for /f "tokens=3" %%a in ('dir "%BACKUP_FOLDER%" /s /-c ^| findstr "bytes"') do set SIZE=%%a
echo Tamaño total: %SIZE% bytes
echo.

REM Listar archivos incluidos
echo Archivos incluidos:
dir /B /S "%BACKUP_FOLDER%" | findstr /V "README.txt"
echo.

echo Para restaurar este backup:
echo   1. Lee las instrucciones en: %BACKUP_FOLDER%\README.txt
echo   2. Detén el sistema antes de restaurar
echo.
pause
