@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  🔄 AUTO-UPDATE DVDBank
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Verificar si hay cambios remotos
echo [1/5] Verificando cambios remotos...
git fetch origin >nul 2>&1

REM Comparar con la rama local
for /f %%i in ('git rev-parse HEAD') do set LOCAL=%%i
for /f %%i in ('git rev-parse @{u}') do set REMOTE=%%i

if "%LOCAL%"=="%REMOTE%" (
    echo     ✅ Ya estás actualizado
    echo.
    echo No hay cambios nuevos en el repositorio.
    timeout /t 3 /nobreak >nul
    exit /b 0
)

echo     ⚠ Hay cambios disponibles

REM Mostrar cambios
echo.
echo [2/5] Cambios disponibles:
echo ───────────────────────────────────────────────────────────────────────────
git log HEAD..@{u} --oneline --decorate --color=always
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Confirmar actualización
set /p CONFIRM="¿Deseas actualizar y reiniciar el servidor? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo Actualización cancelada.
    pause
    exit /b 0
)

REM Hacer backup de la base de datos
echo.
echo [3/5] Haciendo backup de bases de datos...
if not exist "backup_auto" mkdir backup_auto
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=backup_auto\%TIMESTAMP%
mkdir "%BACKUP_DIR%" 2>nul

copy *.db "%BACKUP_DIR%\" >nul 2>&1
echo     ✅ Backup creado en %BACKUP_DIR%

REM Detener servidor
echo.
echo [4/5] Deteniendo servidor...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo     ✅ Servidor detenido

REM Actualizar código
echo.
echo [5/5] Actualizando código...
git pull origin main

if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo actualizar el código
    echo.
    echo Revisa los conflictos manualmente con:
    echo   git status
    echo.
    pause
    exit /b 1
)

echo     ✅ Código actualizado

REM Reinstalar dependencias si requirements.txt cambió
git diff HEAD@{1} HEAD --name-only | findstr "requirements.txt" >nul
if not errorlevel 1 (
    echo.
    echo Actualizando dependencias...
    pip install -r requirements.txt
)

REM Reiniciar servidor
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ ACTUALIZACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Reiniciando servidor...
timeout /t 2 /nobreak >nul

call INICIAR_DVDBANK_DVTA.bat
