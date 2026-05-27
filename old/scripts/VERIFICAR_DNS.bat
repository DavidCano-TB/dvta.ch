@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICAR REGISTROS DNS EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script verificará que todos los registros de email se crearon bien.
echo.
pause
echo.

python verificar_dns_cloudflare.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
