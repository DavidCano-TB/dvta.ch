@echo off
chcp 65001 >nul
title DVDcoin - Sistema Completo
color 0B

:MENU
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🏦 DVDcoin - Sistema de Gestión Completo
echo ═══════════════════════════════════════════════════════════════
echo.
echo   [1] 🚀 Iniciar TODOS los servidores
echo   [2] 🔍 Verificar estado de servidores
echo   [3] 🛑 Detener TODOS los servidores
echo   [4] 🔄 Reiniciar sistema completo
echo   [5] 🌐 Abrir URLs en navegador
echo   [6] 📊 Ver logs en tiempo real
echo   [7] ❌ Salir
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
set /p opcion="Selecciona una opción (1-7): "

if "%opcion%"=="1" goto INICIAR
if "%opcion%"=="2" goto VERIFICAR
if "%opcion%"=="3" goto DETENER
if "%opcion%"=="4" goto REINICIAR
if "%opcion%"=="5" goto ABRIR_URLS
if "%opcion%"=="6" goto LOGS
if "%opcion%"=="7" goto SALIR
goto MENU

:INICIAR
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🚀 Iniciando Sistema Completo
echo ═══════════════════════════════════════════════════════════════
echo.
call INICIAR_TODOS_SERVIDORES.bat
goto MENU

:VERIFICAR
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔍 Verificando Estado de Servidores
echo ═══════════════════════════════════════════════════════════════
echo.
call VERIFICAR_SERVIDORES.bat
goto MENU

:DETENER
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🛑 Deteniendo Sistema Completo
echo ═══════════════════════════════════════════════════════════════
echo.
call DETENER_TODOS_SERVIDORES.bat
goto MENU

:REINICIAR
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔄 Reiniciando Sistema Completo
echo ═══════════════════════════════════════════════════════════════
echo.
echo [1/2] Deteniendo servidores...
call DETENER_TODOS_SERVIDORES.bat
echo.
echo [2/2] Iniciando servidores...
timeout /t 3 /nobreak >nul
call INICIAR_TODOS_SERVIDORES.bat
goto MENU

:ABRIR_URLS
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🌐 Abriendo URLs en Navegador
echo ═══════════════════════════════════════════════════════════════
echo.
echo Abriendo Bank...
start https://dvta.ch/bank
timeout /t 2 /nobreak >nul

echo Abriendo Exams...
start https://exams.dvta.ch
timeout /t 2 /nobreak >nul

echo Abriendo Games...
start https://games.dvta.ch
timeout /t 2 /nobreak >nul

echo Abriendo Social...
start https://social.dvta.ch
timeout /t 2 /nobreak >nul

echo.
echo ✅ Todas las URLs abiertas
echo.
pause
goto MENU

:LOGS
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📊 Logs en Tiempo Real
echo ═══════════════════════════════════════════════════════════════
echo.
echo Los logs se muestran en las ventanas individuales de cada servidor
echo.
echo Para ver logs:
echo   1. Busca las ventanas con títulos:
echo      - DVDcoin Bank (8000)
echo      - DVDcoin Exams (8001)
echo      - DVDcoin Games (8002)
echo      - DVDcoin Social (8003)
echo.
echo   2. Cada ventana muestra los logs de su servidor
echo.
pause
goto MENU

:SALIR
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   👋 Saliendo del Sistema
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚠️  Los servidores seguirán corriendo en segundo plano
echo.
echo Para detenerlos, ejecuta: DETENER_TODOS_SERVIDORES.bat
echo.
pause
exit
