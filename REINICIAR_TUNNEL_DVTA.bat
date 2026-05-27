@echo off
chcp 65001 >nul
title Reiniciar Cloudflare Tunnel DVTA
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔄 REINICIAR CLOUDFLARE TUNNEL - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/3] Deteniendo Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo      ✅ Tunnel detenido
echo.

echo [2/3] Iniciando Cloudflare Tunnel con nueva configuración...
start "Cloudflare Tunnel DVTA" cloudflared tunnel --config cloudflare-dvta-config.yml run
timeout /t 5 /nobreak >nul
echo      ✅ Tunnel iniciado
echo.

echo [3/3] Verificando...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo
) else (
    echo      ❌ Cloudflare Tunnel no está corriendo
    echo.
    echo      Verifica la ventana "Cloudflare Tunnel DVTA" para ver errores
    pause
    exit /b 1
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ TUNNEL REINICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 CONFIGURACIÓN ACTUAL:
echo   • dvta.ch → localhost:8001 (Exams)
echo   • www.dvta.ch → localhost:8001 (Exams)
echo   • bank.dvta.ch → localhost:8000 (Bank)
echo.
echo ⏱️  Espera 10-30 segundos para que se propague
echo.
echo 🧪 PRUEBA AHORA:
echo   • https://dvta.ch/exams
echo   • https://dvta.ch/health
echo   • https://bank.dvta.ch (Bank sigue funcionando)
echo.
pause
