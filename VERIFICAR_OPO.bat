@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN SISTEMA OPO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo [1/5] Verificando servidores...
echo.
netstat -ano | findstr "LISTENING" | findstr "8000 8001"
echo.

echo [2/5] Verificando procesos Python...
echo.
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,StartTime | Format-Table"
echo.

echo [3/5] Verificando Cloudflare Tunnel...
echo.
powershell -Command "Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,StartTime | Format-Table"
echo.

echo [4/5] Probando health endpoint...
echo.
curl http://localhost:8001/health
echo.
echo.

echo [5/5] URLs disponibles:
echo.
echo   ✅ https://dvta.ch/opo
echo   ✅ https://dvta.ch/opo/exam-types
echo   ✅ https://dvta.ch/opo/exam
echo   ✅ https://dvta.ch/health
echo   ✅ https://bank.dvta.ch
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ VERIFICACIÓN COMPLETA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Si todos los servicios están activos, el sistema está funcionando correctamente.
echo.
echo Para probar el sistema OPO:
echo   1. Abre: https://dvta.ch/opo
echo   2. Clic en "Comenzar" en una oposición
echo   3. Elige tipo de examen
echo   4. Realiza el examen
echo.
pause
