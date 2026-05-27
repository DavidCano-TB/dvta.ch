@echo off
chcp 65001 >nul
echo ========================================
echo   BACKUPS CADA 30 MINUTOS
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Ubicación de backups:
echo     C:\dvdcoin\backup_30min\
echo.

echo [2] Backups disponibles:
if exist "backup_30min\" (
    dir backup_30min /AD /O-D | findstr /C:"<DIR>" | findstr /V /C:"." | findstr /V /C:".."
    echo.
    echo Total de backups:
    for /f %%i in ('dir backup_30min /AD ^| find "Dir(s)"') do echo %%i
) else (
    echo     No hay backups aún
)
echo.

echo [3] Estado de la tarea programada:
schtasks /Query /TN "DVDCoin_Backup_30min" >nul 2>&1
if %errorLevel% equ 0 (
    echo     ✓ Tarea programada configurada
    echo.
    schtasks /Query /TN "DVDCoin_Backup_30min" /FO LIST | findstr /C:"Próxima hora de ejecución" /C:"Última hora de ejecución" /C:"Estado"
) else (
    echo     ✗ Tarea programada NO configurada
    echo.
    echo     Para configurarla, ejecuta como Administrador:
    echo     CONFIGURAR_BACKUP_30MIN.bat
)
echo.

echo [4] Último backup:
if exist "backup_30min\" (
    for /f "tokens=*" %%d in ('dir backup_30min /AD /B /O-D 2^>nul') do (
        echo     %%d
        goto :found
    )
    :found
) else (
    echo     No hay backups
)
echo.

echo [5] Log de backups:
if exist "logs\backup_30min.log" (
    echo     Últimas 5 líneas:
    echo     ----------------------------------------
    powershell -Command "Get-Content logs\backup_30min.log -Tail 5"
    echo     ----------------------------------------
) else (
    echo     No hay log aún
)
echo.

echo ========================================
pause
