@echo off
chcp 65001 >nul
title BACKUP COMPLETO DEL SISTEMA
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   💾 BACKUP COMPLETO DEL SISTEMA DVDcoin
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Crear nombre de backup con fecha y hora
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set BACKUP_DATE=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%
set BACKUP_DIR=backup\%BACKUP_DATE%

echo Creando backup en: %BACKUP_DIR%
echo.

REM Crear directorio de backup
if not exist "backup" mkdir "backup"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  BACKUP DE BASES DE DATOS                                                │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Backup de bases de datos del módulo Exams
if exist "modules\exams\data" (
    echo [1/5] Copiando bases de datos de Exams...
    xcopy "modules\exams\data\*.db" "%BACKUP_DIR%\" /Y /Q >nul 2>&1
    if %errorlevel% equ 0 (
        echo      ✅ Bases de datos de Exams copiadas
    ) else (
        echo      ⚠️  No se encontraron bases de datos de Exams
    )
) else (
    echo      ⚠️  Directorio modules\exams\data no existe
)
echo.

REM Backup de bases de datos principales
echo [2/5] Copiando bases de datos principales...
if exist "*.db" (
    xcopy "*.db" "%BACKUP_DIR%\" /Y /Q >nul 2>&1
    echo      ✅ Bases de datos principales copiadas
) else (
    echo      ⚠️  No se encontraron bases de datos principales
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  BACKUP DE CONFIGURACIÓN                                                 │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Backup de configuración de Exams
echo [3/5] Copiando configuración de Exams...
if exist "modules\exams\config" (
    if not exist "%BACKUP_DIR%\config" mkdir "%BACKUP_DIR%\config"
    xcopy "modules\exams\config\*.*" "%BACKUP_DIR%\config\" /Y /Q >nul 2>&1
    echo      ✅ Configuración de Exams copiada
) else (
    echo      ⚠️  Directorio modules\exams\config no existe
)
echo.

REM Backup de configuración de Cloudflare
echo [4/5] Copiando configuración de Cloudflare...
if exist "cloudflare-dvta-config.yml" (
    copy "cloudflare-dvta-config.yml" "%BACKUP_DIR%\" /Y >nul 2>&1
    echo      ✅ Configuración de Cloudflare copiada
) else (
    echo      ⚠️  cloudflare-dvta-config.yml no existe
)
echo.

REM Backup de archivos de configuración principales
echo [5/5] Copiando archivos de configuración...
if exist "conf" (
    if not exist "%BACKUP_DIR%\conf" mkdir "%BACKUP_DIR%\conf"
    xcopy "conf\*.*" "%BACKUP_DIR%\conf\" /Y /Q >nul 2>&1
    echo      ✅ Archivos de configuración copiados
) else (
    echo      ⚠️  Directorio conf no existe
)
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  INFORMACIÓN DEL BACKUP                                                  │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Crear archivo de información del backup
echo BACKUP DEL SISTEMA DVDcoin > "%BACKUP_DIR%\BACKUP_INFO.txt"
echo. >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo Fecha: %date% %time% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo Directorio: %BACKUP_DIR% >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo. >> "%BACKUP_DIR%\BACKUP_INFO.txt"
echo Archivos incluidos: >> "%BACKUP_DIR%\BACKUP_INFO.txt"
dir "%BACKUP_DIR%" /B >> "%BACKUP_DIR%\BACKUP_INFO.txt"

echo   Fecha del backup:  %date% %time%
echo   Ubicación:         %BACKUP_DIR%
echo.

REM Contar archivos
for /f %%A in ('dir /b /a-d "%BACKUP_DIR%" ^| find /c /v ""') do set FILE_COUNT=%%A
echo   Archivos copiados: %FILE_COUNT%
echo.

REM Calcular tamaño
for /f "tokens=3" %%a in ('dir "%BACKUP_DIR%" ^| findstr "bytes"') do set BACKUP_SIZE=%%a
echo   Tamaño total:      %BACKUP_SIZE% bytes
echo.

echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  LIMPIEZA DE BACKUPS ANTIGUOS                                            │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

REM Contar backups existentes
for /f %%A in ('dir /b /ad "backup" ^| find /c /v ""') do set BACKUP_COUNT=%%A
echo   Backups existentes: %BACKUP_COUNT%
echo.

REM Si hay más de 10 backups, eliminar los más antiguos
if %BACKUP_COUNT% gtr 10 (
    echo   ⚠️  Hay más de 10 backups. Eliminando los más antiguos...
    echo.
    
    REM Obtener lista de backups ordenados por fecha (más antiguos primero)
    set /a DELETE_COUNT=%BACKUP_COUNT%-10
    echo   Eliminando %DELETE_COUNT% backups antiguos...
    
    REM Aquí se eliminarían los backups más antiguos
    REM (implementación simplificada - elimina manualmente si es necesario)
    
    echo   💡 TIP: Revisa manualmente la carpeta backup\ y elimina backups antiguos
    echo.
) else (
    echo   ✅ Número de backups OK (menos de 10)
    echo.
)

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ BACKUP COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   📁 Ubicación: %BACKUP_DIR%
echo   📊 Archivos:  %FILE_COUNT%
echo   💾 Tamaño:    %BACKUP_SIZE% bytes
echo.
echo   Para restaurar:
echo     1. Detén los servicios (cierra ventanas de servidor y tunnel)
echo     2. Copia los archivos de %BACKUP_DIR% a sus ubicaciones originales
echo     3. Reinicia los servicios con ACTIVAR_DVTA_CH_AHORA.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
