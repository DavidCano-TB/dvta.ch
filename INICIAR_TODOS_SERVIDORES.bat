@echo off
chcp 65001 >nul
title DVDcoin - Iniciando Todos los Servidores
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🚀 DVDcoin - Iniciando Todos los Servidores
echo ═══════════════════════════════════════════════════════════════
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Crear directorios necesarios
if not exist "modules\games\data" mkdir "modules\games\data"
if not exist "modules\games\config" mkdir "modules\games\config"
if not exist "modules\social\data" mkdir "modules\social\data"
if not exist "modules\social\config" mkdir "modules\social\config"

echo 📁 Directorios creados
echo.

REM Iniciar servidor Bank (8000)
echo [1/4] Iniciando servidor Bank (puerto 8000)...
start "DVDcoin Bank (8000)" cmd /k "cd /d %~dp0src && python main.py"
timeout /t 3 /nobreak >nul

REM Iniciar servidor Exams (8001)
echo [2/4] Iniciando servidor Exams (puerto 8001)...
start "DVDcoin Exams (8001)" cmd /k "cd /d %~dp0modules\exams && python start_exams.py"
timeout /t 3 /nobreak >nul

REM Iniciar servidor Games (8002)
echo [3/4] Iniciando servidor Games (puerto 8002)...
start "DVDcoin Games (8002)" cmd /k "cd /d %~dp0modules\games && python start_games.py"
timeout /t 3 /nobreak >nul

REM Iniciar servidor Social (8003)
echo [4/4] Iniciando servidor Social (puerto 8003)...
start "DVDcoin Social (8003)" cmd /k "cd /d %~dp0modules\social && python start_social.py"
timeout /t 3 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ Todos los servidores iniciados
echo ═══════════════════════════════════════════════════════════════
echo.
echo   📍 Bank:   http://localhost:8000  →  https://dvta.ch
echo   📍 Exams:  http://localhost:8001  →  https://exams.dvta.ch
echo   📍 Games:  http://localhost:8002  →  https://games.dvta.ch
echo   📍 Social: http://localhost:8003  →  https://social.dvta.ch
echo.
echo   💡 Cada servidor se ejecuta en su propia ventana
echo   💡 Cierra las ventanas individuales para detener cada servidor
echo.

REM Esperar 5 segundos y verificar que los servidores están corriendo
echo Verificando servidores en 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo Verificando puertos...
netstat -ano | findstr ":8000 :8001 :8002 :8003" | findstr "LISTENING"

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🌐 Abriendo navegador...
echo ═══════════════════════════════════════════════════════════════
timeout /t 2 /nobreak >nul

REM Abrir el navegador en la página principal
start https://dvta.ch/bank

echo.
echo ✅ Sistema completo iniciado
echo.
pause
