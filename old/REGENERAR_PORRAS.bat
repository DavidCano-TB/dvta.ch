@echo off
title DVDcoin - Regenerar Páginas de Porras
cd /d "%~dp0"

echo ============================================
echo  Regenerando páginas de porras...
echo ============================================
echo.

python fix_and_regenerate.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo regenerar las páginas
    echo Verifica que Python esté instalado correctamente
    pause
    exit /b 1
)

echo.
echo ============================================
echo  ¡Listo!
echo ============================================
echo.
echo Las páginas HTML de las porras han sido regeneradas
echo con el template actualizado que incluye:
echo.
echo   - Botones de selección arreglados
echo   - Estadísticas globales completas
echo   - Estadísticas personales mejoradas
echo   - 12 nuevas métricas estadísticas
echo.
echo Ahora ejecuta APLICAR_CAMBIOS.bat para reiniciar
echo el servidor y aplicar todos los cambios.
echo.
pause
