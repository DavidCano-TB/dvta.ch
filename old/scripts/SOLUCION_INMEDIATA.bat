@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ⚡ SOLUCIÓN INMEDIATA - URL FUNCIONANDO AHORA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo El DNS de dvta.ch está propagando (puede tardar horas).
echo.
echo Voy a crear una URL temporal que funciona AHORA MISMO.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo Generando URL temporal de Cloudflare...
echo.
echo ⚠️  IMPORTANTE: Esta ventana debe quedar ABIERTA
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cloudflared tunnel --url http://localhost:8000

pause
