@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICAR PROPAGACIÓN DNS DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script verifica si tu dominio ya está propagado.
echo.
pause
echo.

python verificar_dns_propagacion.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
