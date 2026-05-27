@echo off
chcp 65001 >nul
echo ========================================
echo   ESTADO DEL SISTEMA DE BACKUP
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Verificando carpeta de backups...
if exist "backup\" (
    echo     ✓ Carpeta backup\ existe
    for /d %%d in (backup\*) do (
        echo       - %%~nxd
    )
) else (
    echo     ✗ Carpeta backup\ NO existe
)
echo.

echo [2] Verificando tarea programada...
schtasks /Query /TN "DVDCoin_Backup_Diario" >nul 2>&1
if %errorLevel% equ 0 (
    echo     ✓ Tarea programada configurada
    echo.
    schtasks /Query /TN "DVDCoin_Backup_Diario" /FO LIST | findstr /C:"Próxima hora de ejecución" /C:"Última hora de ejecución" /C:"Estado"
) else (
    echo     ✗ Tarea programada NO configurada
    echo.
    echo     Para configurarla, ejecuta como Administrador:
    echo     CONFIGURAR_BACKUP_AUTOMATICO.bat
)
echo.

echo [3] Verificando log de backups...
if exist "logs\backup.log" (
    echo     ✓ Log de backups existe
    echo.
    echo     Últimas 5 líneas del log:
    echo     ----------------------------------------
    powershell -Command "Get-Content logs\backup.log -Tail 5"
    echo     ----------------------------------------
) else (
    echo     ⚠ Log de backups NO existe (aún no se ha ejecutado ningún backup)
)
echo.

echo [4] Espacio utilizado por backups...
if exist "backup\" (
    for /f "tokens=3" %%a in ('dir backup /s /-c ^| findstr /C:"bytes"') do set size=%%a
    echo     Tamaño total: !size! bytes
) else (
    echo     No hay backups
)
echo.

echo ========================================
echo   Verificación completada
echo ========================================
echo.
pause
