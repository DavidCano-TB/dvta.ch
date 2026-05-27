@echo off
chcp 65001 >nul
title DVDBank - Verificación Completa
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python VERIFICAR_TODO.py

echo.
echo Presiona cualquier tecla para salir...
pause >nul
