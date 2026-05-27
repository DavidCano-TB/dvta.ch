@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔄 REINICIANDO SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/3] Deteniendo procesos actuales...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul

echo [2/3] Iniciando servidor principal (puerto 8000)...
start "DVDBank Server" /MIN python main.py
timeout /t 10 /nobreak >nul

echo [3/3] Iniciando túnel Cloudflare...
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-multi-server.yml run dvta-tunnel
timeout /t 10 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SISTEMA REINICIADO
echo ═══════════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo   • https://dvta.ch
echo   • https://www.dvta.ch
echo   • https://bank.dvta.ch
echo   • http://localhost:8000 (local)
echo.
echo Verificando estado...
timeout /t 5 /nobreak >nul

REM Verificar servidor
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ Servidor no responde aún, espera unos segundos más
) else (
    echo ✅ Servidor funcionando correctamente
)

echo.
pause
