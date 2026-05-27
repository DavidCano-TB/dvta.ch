@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔧 REINICIO FORZADO DEL SERVIDOR
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/5] Matando TODOS los procesos Python y Cloudflare...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Matando proceso %%a en puerto 8000...
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo [3/5] Verificando que el puerto está libre...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ❌ Puerto 8000 aún ocupado. Ejecuta este script como ADMINISTRADOR.
    pause
    exit /b 1
)
echo ✅ Puerto 8000 liberado

echo [4/5] Iniciando servidor en puerto 8000...
start "DVDBank Server" /MIN python main.py
timeout /t 15 /nobreak >nul

echo [5/5] Verificando servidor...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ Servidor no responde al health check, intentando ruta principal...
    curl -s http://localhost:8000/ >nul 2>&1
    if errorlevel 1 (
        echo ❌ Servidor no responde
        echo.
        echo Revisa los logs o ejecuta como Administrador
        pause
        exit /b 1
    )
)

echo ✅ Servidor funcionando correctamente

echo.
echo [6/6] Iniciando túnel Cloudflare con configuración actualizada...
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
timeout /t 10 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SISTEMA REINICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo   • Local:  http://localhost:8000
echo   • Local:  http://localhost:8000/bank
echo   • Public: https://dvta.ch
echo   • Bank:   https://bank.dvta.ch
echo.
pause
