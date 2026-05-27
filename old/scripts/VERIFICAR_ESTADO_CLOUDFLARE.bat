@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICANDO ESTADO DE dvta.ch EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python c:\dvdcoin\verificar_estado_cloudflare.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ VERIFICACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
