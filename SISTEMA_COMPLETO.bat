@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

:MENU
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  🏦 DVDBANK - SISTEMA COMPLETO DE GESTIÓN
echo ═══════════════════════════════════════════════════════════════
echo.
echo  SERVIDORES:
echo  ───────────────────────────────────────────────────────────────
echo   1. Iniciar todos los servidores
echo   2. Detener todos los servidores
echo   3. Ver estado de servidores
echo   4. Reiniciar todos los servidores
echo.
echo  SERVIDORES INDIVIDUALES:
echo  ───────────────────────────────────────────────────────────────
echo   5. Iniciar servidor Bank (puerto 8000)
echo   6. Iniciar servidor Exams (puerto 8001)
echo   7. Iniciar servidor Games (puerto 8002)
echo   8. Iniciar servidor Social (puerto 8003)
echo.
echo  CLOUDFLARE TUNNEL:
echo  ───────────────────────────────────────────────────────────────
echo   9. Iniciar túnel Cloudflare
echo   10. Detener túnel Cloudflare
echo   11. Reiniciar túnel Cloudflare
echo.
echo  SISTEMA COMPLETO:
echo  ───────────────────────────────────────────────────────────────
echo   12. Iniciar sistema completo (servidores + túnel)
echo   13. Detener sistema completo
echo   14. Reiniciar sistema completo
echo.
echo  MONITOREO:
echo  ───────────────────────────────────────────────────────────────
echo   15. Monitor automático (reinicia si falla)
echo.
echo   0. Salir
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
set /p OPCION="Selecciona una opción (0-15): "

if "%OPCION%"=="1" goto START_ALL_SERVERS
if "%OPCION%"=="2" goto STOP_ALL_SERVERS
if "%OPCION%"=="3" goto STATUS
if "%OPCION%"=="4" goto RESTART_ALL_SERVERS
if "%OPCION%"=="5" goto START_BANK
if "%OPCION%"=="6" goto START_EXAMS
if "%OPCION%"=="7" goto START_GAMES
if "%OPCION%"=="8" goto START_SOCIAL
if "%OPCION%"=="9" goto START_TUNNEL
if "%OPCION%"=="10" goto STOP_TUNNEL
if "%OPCION%"=="11" goto RESTART_TUNNEL
if "%OPCION%"=="12" goto START_COMPLETE
if "%OPCION%"=="13" goto STOP_COMPLETE
if "%OPCION%"=="14" goto RESTART_COMPLETE
if "%OPCION%"=="15" goto MONITOR
if "%OPCION%"=="0" goto EXIT

echo.
echo Opción no válida
timeout /t 2 /nobreak >nul
goto MENU

:START_ALL_SERVERS
cls
echo.
echo Iniciando todos los servidores...
python arquitectura_servidores.py start-all
pause
goto MENU

:STOP_ALL_SERVERS
cls
echo.
echo Deteniendo todos los servidores...
python arquitectura_servidores.py stop-all
pause
goto MENU

:STATUS
cls
echo.
python arquitectura_servidores.py status
pause
goto MENU

:RESTART_ALL_SERVERS
cls
echo.
echo Reiniciando todos los servidores...
python arquitectura_servidores.py stop-all
timeout /t 3 /nobreak >nul
python arquitectura_servidores.py start-all
pause
goto MENU

:START_BANK
cls
echo.
python arquitectura_servidores.py start bank
pause
goto MENU

:START_EXAMS
cls
echo.
python arquitectura_servidores.py start exams
pause
goto MENU

:START_GAMES
cls
echo.
python arquitectura_servidores.py start games
pause
goto MENU

:START_SOCIAL
cls
echo.
python arquitectura_servidores.py start social
pause
goto MENU

:START_TUNNEL
cls
echo.
echo Iniciando túnel Cloudflare...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-multi-server.yml run dvta-tunnel
timeout /t 5 /nobreak >nul
echo.
echo ✅ Túnel iniciado
echo.
echo URLs disponibles:
echo   • https://dvta.ch (Bank)
echo   • https://bank.dvta.ch (Bank)
echo   • https://exams.dvta.ch (Exams)
echo   • https://games.dvta.ch (Games)
echo   • https://social.dvta.ch (Social)
pause
goto MENU

:STOP_TUNNEL
cls
echo.
echo Deteniendo túnel Cloudflare...
taskkill /F /IM cloudflared.exe >nul 2>&1
echo ✅ Túnel detenido
pause
goto MENU

:RESTART_TUNNEL
cls
echo.
echo Reiniciando túnel Cloudflare...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-multi-server.yml run dvta-tunnel
timeout /t 5 /nobreak >nul
echo ✅ Túnel reiniciado
pause
goto MENU

:START_COMPLETE
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  🚀 INICIANDO SISTEMA COMPLETO
echo ═══════════════════════════════════════════════════════════════
echo.
echo [1/2] Iniciando servidores...
python arquitectura_servidores.py start-all
echo.
echo [2/2] Iniciando túnel Cloudflare...
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-multi-server.yml run dvta-tunnel
timeout /t 5 /nobreak >nul
echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SISTEMA COMPLETO INICIADO
echo ═══════════════════════════════════════════════════════════════
echo.
echo URLs disponibles:
echo   • https://dvta.ch
echo   • https://bank.dvta.ch
echo   • https://exams.dvta.ch
echo   • https://games.dvta.ch
echo   • https://social.dvta.ch
echo.
pause
goto MENU

:STOP_COMPLETE
cls
echo.
echo Deteniendo sistema completo...
echo.
echo [1/2] Deteniendo túnel...
taskkill /F /IM cloudflared.exe >nul 2>&1
echo.
echo [2/2] Deteniendo servidores...
python arquitectura_servidores.py stop-all
echo.
echo ✅ Sistema completo detenido
pause
goto MENU

:RESTART_COMPLETE
cls
echo.
echo Reiniciando sistema completo...
call :STOP_COMPLETE
timeout /t 3 /nobreak >nul
call :START_COMPLETE
goto MENU

:MONITOR
cls
echo.
echo Iniciando monitor automático...
echo.
python arquitectura_servidores.py monitor
pause
goto MENU

:EXIT
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  👋 ¡Hasta luego!
echo ═══════════════════════════════════════════════════════════════
echo.
timeout /t 2 /nobreak >nul
exit /b 0
