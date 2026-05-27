@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚡ SOLUCIÓN RÁPIDA TEMPORAL
echo ═══════════════════════════════════════════════════════════
echo.
echo Esta solución crea una URL temporal de Cloudflare que
echo funciona INMEDIATAMENTE sin configuración DNS.
echo.
echo ⚠️  La URL cambiará cada vez que reinicies el servidor.
echo ⚠️  Para una URL permanente, necesitas arreglar el DNS.
echo.
echo ═══════════════════════════════════════════════════════════
echo.

echo 1. Deteniendo túnel actual...
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 2 /nobreak >nul
echo    ✅ Túnel detenido
echo.

echo 2. Iniciando Quick Tunnel (URL temporal)...
echo    Esto generará una URL como: https://xxx-yyy-zzz.trycloudflare.com
echo.
start /B cloudflared tunnel --url http://localhost:8000 > cloudflare_quick_tunnel.log 2>&1
timeout /t 5 /nobreak >nul

echo 3. Buscando la URL generada...
echo.
powershell -Command "Get-Content cloudflare_quick_tunnel.log | Select-String 'trycloudflare.com' | Select-Object -First 1"
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ QUICK TUNNEL INICIADO
echo ═══════════════════════════════════════════════════════════
echo.
echo La URL temporal está en el archivo: cloudflare_quick_tunnel.log
echo.
echo Para ver la URL completa:
echo    type cloudflare_quick_tunnel.log
echo.
echo ⚠️  IMPORTANTE:
echo    - Esta URL es TEMPORAL
echo    - Cambiará cada vez que reinicies
echo    - Para URL permanente, arregla el DNS con ARREGLAR_DNS_CLOUDFLARE.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
