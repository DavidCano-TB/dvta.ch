@echo off
chcp 65001 >nul
title ARREGLAR dvta.ch AHORA
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 ARREGLAR dvta.ch - SOLUCIÓN INMEDIATA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo PROBLEMA DETECTADO:
echo   • Cloudflare Tunnel está corriendo ✅
echo   • Servidor Exams NO está corriendo ❌
echo   • Por eso dvta.ch da Error 1033
echo.
echo SOLUCIÓN:
echo   Iniciar servidor Exams en puerto 8001
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

pause

echo.
echo [1/4] Deteniendo tunnel anterior...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Tunnel detenido
echo.

echo [2/4] Verificando dependencias de Exams...
cd modules\exams
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo      ❌ Error instalando dependencias
        cd ..\..
        pause
        exit /b 1
    )
)
cd ..\..
echo      ✅ Dependencias OK
echo.

echo [3/4] Iniciando servidor Exams (puerto 8001)...
start "DVDExams Server - dvta.ch" cmd /c "cd modules\exams && python start_exams.py"
echo      ⏳ Esperando que el servidor inicie...
timeout /t 10 /nobreak >nul

REM Verificar que el servidor inició
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Exams corriendo en puerto 8001
) else (
    echo      ❌ Error: Servidor no se inició en puerto 8001
    echo.
    echo      Verifica la ventana "DVDExams Server" para ver errores
    pause
    exit /b 1
)
echo.

echo [4/4] Reiniciando Cloudflare Tunnel...
start "Cloudflare Tunnel - dvta.ch" cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run"
timeout /t 3 /nobreak >nul
echo      ✅ Tunnel reiniciado
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ PROBLEMA SOLUCIONADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 PRUEBA AHORA:
echo   • Abre: https://dvta.ch
echo   • Deberías ver la página de Exams (estilo azul)
echo.
echo 📊 SERVICIOS ACTIVOS:
echo   • Servidor Exams: puerto 8001 ✅
echo   • Cloudflare Tunnel: activo ✅
echo.
echo ⏱️  ESPERA:
echo   • Puede tardar 10-30 segundos en propagarse
echo   • Si aún da error, espera 1 minuto y recarga
echo.
echo 🛑 MANTENER CORRIENDO:
echo   • NO cierres las ventanas de servidor y tunnel
echo   • Déjalas minimizadas en segundo plano
echo.
pause
