@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚡ GENERANDO URL TEMPORAL FUNCIONAL
echo ═══════════════════════════════════════════════════════════
echo.

del quick_tunnel_url.txt 2>nul

echo Iniciando Quick Tunnel...
echo.
start /B cmd /c "cloudflared tunnel --url http://localhost:8000 > quick_tunnel_output.txt 2>&1"

echo Esperando que se genere la URL (15 segundos)...
timeout /t 15 /nobreak >nul

if exist quick_tunnel_output.txt (
    findstr /C:"https://" quick_tunnel_output.txt > quick_tunnel_url.txt 2>nul
)

if exist quick_tunnel_url.txt (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   ✅ URL GENERADA
    echo ═══════════════════════════════════════════════════════════
    echo.
    type quick_tunnel_url.txt
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Esta URL funciona AHORA MISMO con HTTPS válido.
    echo Cópiala y ábrela en tu navegador.
    echo.
    echo ⚠️  IMPORTANTE: Esta URL es temporal y cambiará al reiniciar.
    echo.
    del quick_tunnel_output.txt 2>nul
) else (
    echo.
    echo ❌ No se pudo generar la URL automáticamente.
    echo.
    if exist quick_tunnel_output.txt (
        echo Salida del comando:
        type quick_tunnel_output.txt
        del quick_tunnel_output.txt 2>nul
    )
    echo.
    echo Ejecuta manualmente:
    echo    cloudflared tunnel --url http://localhost:8000
    echo.
    echo Y busca la línea que dice: https://xxx-yyy-zzz.trycloudflare.com
    echo.
)

pause
