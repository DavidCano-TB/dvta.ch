@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 APLICANDO CORRECCIONES DNS AUTOMÁTICAS
echo ═══════════════════════════════════════════════════════════
echo.

python arreglar_dns_cloudflare.py

echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
