@echo off
chcp 65001 >nul
title DEPLOY - Actualizar y reiniciar DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DEPLOY - Actualizar desde GitHub y reiniciar
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/3] Descargando últimos cambios de GitHub...
git pull --ff-only
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error al hacer pull. Posibles causas:
    echo    - Sin conexión a internet
    echo    - Conflictos locales (ejecuta: git stash ^&^& git pull)
    echo.
    pause
    exit /b 1
)
echo ✅ Código actualizado
echo.

echo [2/3] Actualizando dependencias (si cambiaron)...
pip install -r requirements.txt -q
echo ✅ Dependencias OK
echo.

echo [3/3] Reiniciando todos los servicios...
echo.
call ARRANCAR_TODO_PARALELO.bat
