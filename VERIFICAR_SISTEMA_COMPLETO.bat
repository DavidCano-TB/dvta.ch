@echo off
chcp 65001 >nul
title Verificación Completa del Sistema DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════
echo    🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DVDCOIN
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/5] Verificando servidores locales...
echo.

echo 📊 Bank (Puerto 8000):
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank
if %errorlevel% neq 0 (
    echo    ❌ ERROR - Servidor no responde
) else (
    echo    ✅ OK
)

echo.
echo 📚 Exams (Puerto 8001):
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8001/exams
if %errorlevel% neq 0 (
    echo    ❌ ERROR - Servidor no responde
) else (
    echo    ✅ OK
)

echo.
echo [2/5] Verificando Cloudflare Tunnel...
echo.
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find /I "cloudflared.exe" >nul
if %errorlevel% equ 0 (
    echo    ✅ Cloudflare Tunnel está corriendo
) else (
    echo    ❌ Cloudflare Tunnel NO está corriendo
    echo    💡 Ejecuta: cloudflared tunnel run dvta
)

echo.
echo [3/5] Verificando URLs públicas...
echo.

echo 🌐 https://dvta.ch/bank
curl -s -o nul -w "   Status: %%{http_code}\n" https://dvta.ch/bank
if %errorlevel% neq 0 (
    echo    ⚠️  No se pudo verificar (puede ser problema de red)
)

echo.
echo 🌐 https://dvta.ch/exams
curl -s -o nul -w "   Status: %%{http_code}\n" https://dvta.ch/exams  
if %errorlevel% neq 0 (
    echo    ⚠️  No se pudo verificar (puede ser problema de red)
)

echo.
echo [4/5] Verificando endpoints de API...
echo.

echo 🔌 /bank/api/gallery
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank/api/gallery

echo.
echo 🔌 /bank/api/health
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank/api/health

echo.
echo 🔌 /exams/api/health
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8001/exams/api/health

echo.
echo [5/5] Verificando funcionalidades integradas...
echo.

echo 🎮 Games (integrado en Bank):
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank/pasapalabra
if %errorlevel% neq 0 (
    echo    ❌ ERROR
) else (
    echo    ✅ OK
)

echo.
echo 💬 Social (integrado en Bank):
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank/messages
if %errorlevel% neq 0 (
    echo    ❌ ERROR
) else (
    echo    ✅ OK
)

echo.
echo 🎲 Apuestas (integrado en Bank):
curl -s -o nul -w "   Status: %%{http_code}\n" http://localhost:8000/bank/apuestas
if %errorlevel% neq 0 (
    echo    ❌ ERROR
) else (
    echo    ✅ OK
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo    ✅ VERIFICACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📝 Resumen:
echo    • Bank: Servidor principal en puerto 8000
echo    • Exams: Servidor independiente en puerto 8000
echo    • Games: Integrado en Bank (pasapalabra, millonario, etc.)
echo    • Social: Integrado en Bank (mensajes, videollamadas)
echo    • Apuestas: Integrado en Bank
echo.
echo 🌐 URLs públicas:
echo    • https://dvta.ch/bank - Dashboard principal
echo    • https://dvta.ch/exams - Oposiciones
echo    • https://bank.dvta.ch - Alias del dashboard
echo    • https://exams.dvta.ch - Alias de oposiciones
echo.

pause
