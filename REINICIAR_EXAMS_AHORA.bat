@echo off
chcp 65001 >nul
title Reiniciar Exams AHORA
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔄 REINICIAR EXAMS - APLICAR CAMBIOS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/3] Deteniendo servidor Exams...
taskkill /F /FI "WINDOWTITLE eq DVDExams*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Servidor detenido
echo.

echo [2/3] Iniciando servidor Exams...
start "DVDExams Server" cmd /c "cd modules\exams && python start_exams.py"
timeout /t 8 /nobreak >nul
echo      ✅ Servidor iniciado
echo.

echo [3/3] Verificando...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8001 activo
) else (
    echo      ❌ Puerto 8001 no responde
    echo.
    echo      Verifica la ventana "DVDExams Server" para ver errores
    pause
    exit /b 1
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SERVIDOR REINICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 PRUEBA AHORA:
echo   • https://dvta.ch/exams
echo   • https://dvta.ch/opo
echo   • https://dvta.ch/health
echo.
echo ⏱️  Espera 10-30 segundos para que se propague
echo.
pause
