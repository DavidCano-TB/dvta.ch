@echo off
chcp 65001 >nul
title DVDcoin Platform - Arranque Completo
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DVDCOIN PLATFORM - ARRANQUE COMPLETO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Matar procesos anteriores
echo [1/5] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

REM Verificar Python
echo [2/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo      ❌ Python no encontrado
    echo.
    echo      Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo      ✅ Python instalado
echo.

REM Verificar dependencias
echo [3/5] Verificando dependencias...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo      ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)
echo      ✅ Dependencias OK
echo.

REM Iniciar módulos
echo [4/5] Iniciando módulos...
echo.
echo      → Bank (puerto 8000)...
start "DVDBank Server" python main.py
timeout /t 3 /nobreak >nul

echo      → Exams (puerto 8001)...
if exist "modules\exams\start_exams.py" (
    start "DVDExams Server" cmd /c "cd modules\exams && python start_exams.py"
    timeout /t 5 /nobreak >nul
    echo      ✅ Exams iniciado
) else (
    echo      ⚠️  Exams no disponible aún
)
echo.

REM Verificar servidores
echo [5/5] Verificando servidores...
timeout /t 2 /nobreak >nul

set SERVER_COUNT=0
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('tasklist ^| findstr "python.exe" ^| find /c /v ""') do set SERVER_COUNT=%%i
)

if %SERVER_COUNT% gtr 0 (
    echo      ✅ %SERVER_COUNT% servidor(es) funcionando
) else (
    echo      ❌ Error: Ningún servidor se inició
    pause
    exit /b 1
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ PLATAFORMA INICIADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 ACCESO LOCAL:
echo   • Bank:  http://localhost:8000
echo   • Exams: http://localhost:8001
echo.
echo 🌐 ACCESO EXTERNO (requiere Cloudflare Tunnel):
echo   • Bank:  https://dvdbank.com
echo   • Exams: https://dvta.ch
echo.
echo 🔧 INICIAR TUNNEL:
echo   • Ejecuta: INICIAR_TUNNEL_DVTA.bat
echo.
echo 🛑 DETENER SERVIDORES:
echo   • Cierra las ventanas de servidor
echo   • O ejecuta: taskkill /F /IM python.exe
echo.
pause
