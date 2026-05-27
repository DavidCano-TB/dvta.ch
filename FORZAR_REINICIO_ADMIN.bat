@echo off
:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Este script requiere privilegios de administrador.
    echo Relanzando con privilegios elevados...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🔧 REINICIO FORZADO CON PRIVILEGIOS ADMIN
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/6] Matando TODOS los procesos Python...
taskkill /F /IM python.exe /T 2>nul
if errorlevel 1 (
    echo   ⚠ Algunos procesos no se pudieron matar
) else (
    echo   ✅ Procesos Python eliminados
)
timeout /t 3 /nobreak >nul

echo [2/6] Matando TODOS los procesos Cloudflare...
taskkill /F /IM cloudflared.exe /T 2>nul
if errorlevel 1 (
    echo   ⚠ Algunos procesos no se pudieron matar
) else (
    echo   ✅ Procesos Cloudflare eliminados
)
timeout /t 3 /nobreak >nul

echo [3/6] Liberando puertos manualmente...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   Matando PID %%a en puerto 8000...
    taskkill /F /PID %%a /T 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo   Matando PID %%a en puerto 8001...
    taskkill /F /PID %%a /T 2>nul
)
timeout /t 3 /nobreak >nul

echo [4/6] Verificando puertos liberados...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   ✅ Puerto 8000 liberado
) else (
    echo   ❌ Puerto 8000 aún ocupado
)

netstat -ano | findstr ":8001" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   ✅ Puerto 8001 liberado
) else (
    echo   ❌ Puerto 8001 aún ocupado
)

echo [5/6] Iniciando servidor Bank (puerto 8000)...
start "DVDBank Server" /MIN python main.py
timeout /t 15 /nobreak >nul

echo [6/6] Iniciando túnel Cloudflare...
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-dvta-config.yml run
timeout /t 10 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ VERIFICACIÓN FINAL
echo ═══════════════════════════════════════════════════════════════
echo.

echo Servidores corriendo:
tasklist | findstr "python.exe cloudflared.exe"

echo.
echo Puertos escuchando:
netstat -ano | findstr ":8000 :8001" | findstr "LISTENING"

echo.
echo Probando servidor...
timeout /t 5 /nobreak >nul

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Health check falló, probando ruta raíz...
    curl -s http://localhost:8000/ >nul 2>&1
    if errorlevel 1 (
        echo   ❌ Servidor no responde
    ) else (
        echo   ✅ Servidor responde en ruta raíz
    )
) else (
    echo   ✅ Servidor funcionando correctamente
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo  🎉 REINICIO COMPLETADO
echo ═══════════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo   • http://localhost:8000
echo   • http://localhost:8000/bank
echo   • https://dvta.ch
echo   • https://dvta.ch/bank
echo.
pause
