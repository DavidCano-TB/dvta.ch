@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 INICIANDO SISTEMA DVDBANK COMPLETO
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo PASO 1: Matando procesos existentes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 2 /nobreak >nul
echo    ✅ Procesos detenidos
echo.

echo PASO 2: Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo    Matando proceso en puerto 8000: %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 /nobreak >nul
echo    ✅ Puerto 8000 liberado
echo.

echo PASO 3: Iniciando servidor Python...
start /B python main.py > logs\python_server.log 2>&1
timeout /t 5 /nobreak >nul
echo    ✅ Servidor Python iniciado
echo.

echo PASO 4: Verificando servidor Python...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -Method Get -TimeoutSec 5 -UseBasicParsing; Write-Host '   ✅ Servidor OK - Status:' $r.StatusCode -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo PASO 5: Iniciando túnel Cloudflare configurado...
start /B cloudflared tunnel --config cloudflare-config.yml run dvdcoin > logs\cloudflare_tunnel.log 2>&1
timeout /t 10 /nobreak >nul
echo    ✅ Túnel Cloudflare iniciado
echo.

echo PASO 6: Verificando túnel...
cloudflared tunnel info 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo   • https://dvdbank.david.ch (cuando el DNS esté arreglado)
echo   • https://app.david.ch (cuando el DNS esté arreglado)
echo   • http://localhost:8000 (local)
echo.
echo Para obtener una URL temporal que funcione AHORA:
echo   python generar_url_ahora.py
echo.
echo ═══════════════════════════════════════════════════════════
echo.
