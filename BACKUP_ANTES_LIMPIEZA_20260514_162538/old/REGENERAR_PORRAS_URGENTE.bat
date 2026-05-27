@echo off
title REGENERAR PORRAS - URGENTE
cd /d "%~dp0"

echo ============================================
echo  REGENERANDO PAGINAS DE PORRAS
echo ============================================
echo.
echo Este script regenerara las paginas HTML de
echo las porras con el template corregido.
echo.
echo Los botones de seleccion funcionaran despues.
echo.
pause

python regenerar_ahora.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo regenerar
    pause
    exit /b 1
)

echo.
echo ============================================
echo  LISTO!
echo ============================================
echo.
echo Las paginas han sido regeneradas.
echo.
echo IMPORTANTE: Recarga la pagina de la porra
echo en el navegador (Ctrl+F5) para ver los cambios.
echo.
pause
