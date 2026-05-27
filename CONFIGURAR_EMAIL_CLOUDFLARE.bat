@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 CONFIGURANDO EMAIL EN CLOUDFLARE PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python c:\dvdcoin\configurar_dns_cloudflare_dvta.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ PROCESO COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
