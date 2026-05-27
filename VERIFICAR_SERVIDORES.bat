@echo off
chcp 65001 >nul
title DVDcoin - Verificación de Servidores
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔍 DVDcoin - Verificación de Servidores
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/4] Verificando servidor Bank (8000)...
curl -s http://localhost:8000/bank/api/health >nul 2>&1
if errorlevel 1 (
    echo   ❌ Bank NO está corriendo
) else (
    echo   ✅ Bank está corriendo
)

echo.
echo [2/4] Verificando servidor Exams (8001)...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo   ❌ Exams NO está corriendo
) else (
    echo   ✅ Exams está corriendo
)

echo.
echo [3/4] Verificando servidor Games (8002)...
curl -s http://localhost:8002/api/health >nul 2>&1
if errorlevel 1 (
    echo   ❌ Games NO está corriendo
) else (
    echo   ✅ Games está corriendo
)

echo.
echo [4/4] Verificando servidor Social (8003)...
curl -s http://localhost:8003/api/health >nul 2>&1
if errorlevel 1 (
    echo   ❌ Social NO está corriendo
) else (
    echo   ✅ Social está corriendo
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📊 Estado de Puertos
echo ═══════════════════════════════════════════════════════════════
echo.
netstat -ano | findstr ":8000 :8001 :8002 :8003" | findstr "LISTENING"

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🌐 URLs de Acceso
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Bank:   https://dvta.ch/bank
echo   Exams:  https://exams.dvta.ch
echo   Games:  https://games.dvta.ch
echo   Social: https://social.dvta.ch
echo.
pause
