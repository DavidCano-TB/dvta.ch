@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  👁 MONITOR DE ACTUALIZACIONES - DVDBank
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script verificará cada 5 minutos si hay actualizaciones disponibles.
echo.
echo Presiona Ctrl+C para detener el monitor.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

:LOOP
    set TIMESTAMP=%date% %time:~0,8%
    echo [%TIMESTAMP%] Verificando actualizaciones...
    
    REM Fetch cambios remotos silenciosamente
    git fetch origin >nul 2>&1
    
    REM Comparar commits
    for /f %%i in ('git rev-parse HEAD') do set LOCAL=%%i
    for /f %%i in ('git rev-parse @{u}') do set REMOTE=%%i
    
    if not "%LOCAL%"=="%REMOTE%" (
        echo.
        echo ═══════════════════════════════════════════════════════════════════════════
        echo  🔔 ¡ACTUALIZACIÓN DISPONIBLE!
        echo ═══════════════════════════════════════════════════════════════════════════
        echo.
        echo Hay cambios nuevos en el repositorio.
        echo.
        echo Cambios disponibles:
        git log HEAD..@{u} --oneline --decorate --color=always
        echo.
        echo ═══════════════════════════════════════════════════════════════════════════
        echo.
        
        REM Reproducir sonido de notificación
        powershell -c "(New-Object Media.SoundPlayer 'C:\Windows\Media\notify.wav').PlaySync();" 2>nul
        
        echo ¿Deseas actualizar ahora? (S/N)
        set /p UPDATE=
        
        if /i "!UPDATE!"=="S" (
            echo.
            echo Ejecutando actualización...
            call AUTO_UPDATE.bat
            exit /b
        ) else (
            echo.
            echo Actualización pospuesta. Seguiré monitoreando...
            echo.
        )
    ) else (
        echo     ✅ Sistema actualizado
    )
    
    REM Esperar 5 minutos (300 segundos)
    timeout /t 300 /nobreak >nul
    
goto LOOP
