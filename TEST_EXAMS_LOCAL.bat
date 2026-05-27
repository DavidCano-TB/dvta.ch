@echo off
chcp 65001 >nul
title Test Exams Local
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🧪 TEST LOCAL - Servidor Exams
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/5] Verificando servidor...
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ❌ Servidor NO está corriendo en puerto 8001
    echo.
    echo      Ejecuta primero: ARRANCAR_DVTA_COMPLETO.bat
    pause
    exit /b 1
)
echo      ✅ Servidor corriendo en puerto 8001
echo.

echo [2/5] Test: http://localhost:8001/
curl -s -o nul -w "HTTP %%{http_code}" http://localhost:8001/
echo.
echo.

echo [3/5] Test: http://localhost:8001/exams
curl -s -o nul -w "HTTP %%{http_code}" http://localhost:8001/exams
echo.
echo.

echo [4/5] Test: http://localhost:8001/health
curl -s http://localhost:8001/health
echo.
echo.

echo [5/5] Test: http://localhost:8001/opo
curl -s -o nul -w "HTTP %%{http_code}" http://localhost:8001/opo
echo.
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Si todos los tests muestran HTTP 200, el servidor funciona correctamente.
echo.
echo 🌐 URLs disponibles:
echo   • http://localhost:8001/         → Redirige a /exams
echo   • http://localhost:8001/exams    → Página principal
echo   • http://localhost:8001/opo      → Oposiciones
echo   • http://localhost:8001/health   → Health check
echo.
echo 🔗 URLs externas (con tunnel):
echo   • https://dvta.ch/exams
echo   • https://dvta.ch/opo
echo   • https://dvta.ch/health
echo.
pause
