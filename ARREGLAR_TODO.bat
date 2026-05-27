@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔧 ARREGLANDO SISTEMA COMPLETO
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/4] Deteniendo TODOS los procesos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul

echo [2/4] Verificando puertos...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ⚠ Puerto 8000 aún ocupado, intentando liberar...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a 2>nul
    )
    timeout /t 2 /nobreak >nul
)

echo [3/4] Iniciando servidor Bank (puerto 8000)...
start "DVDBank Server" /MIN python main.py
timeout /t 10 /nobreak >nul

echo [4/4] Iniciando túnel Cloudflare...
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-dvta-config.yml run dvta-tunnel
timeout /t 10 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SISTEMA REINICIADO
echo ═══════════════════════════════════════════════════════════════
echo.

echo Verificando...
timeout /t 5 /nobreak >nul

REM Verificar servidor
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Servidor no responde
    echo.
    echo Revisa los logs o ejecuta este script como Administrador
) else (
    echo ✅ Servidor funcionando
    echo.
    echo URLs disponibles:
    echo   • https://dvta.ch
    echo   • http://localhost:8000
)

echo.
pause
