@echo off
title DVDcoin Bank - Menu Principal
color 0A

:menu
cls
echo.
echo  ============================================================
echo  ███████╗██╗   ██╗██████╗  ██████╗ ██████╗ ██╗███╗   ██╗
echo  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██║████╗  ██║
echo  █████╗  ██║   ██║██║  ██║██║     ██║   ██║██║██╔██╗ ██║
echo  ██╔══╝  ╚██╗ ██╔╝██║  ██║██║     ██║   ██║██║██║╚██╗██║
echo  ███████╗ ╚████╔╝ ██████╔╝╚██████╗╚██████╔╝██║██║ ╚████║
echo  ╚══════╝  ╚═══╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝
echo  ============================================================
echo                    BANCO VIRTUAL v4.0
echo  ============================================================
echo.
echo  [1] Arrancar Servidor + Ngrok (Automatico)
echo  [2] Arrancar Solo Servidor Local
echo  [3] Arrancar Solo Ngrok
echo.
echo  [4] Verificar Estado del Sistema
echo  [5] Detener Todos los Servicios
echo.
echo  [6] Instalar/Actualizar Dependencias
echo  [7] Prueba Completa del Sistema
echo.
echo  [8] Ver URLs del Sistema
echo  [9] Abrir Documentacion
echo.
echo  [0] Salir
echo.
echo  ============================================================
echo.
set /p opcion="  Selecciona una opcion (0-9): "

if "%opcion%"=="1" goto :opcion1
if "%opcion%"=="2" goto :opcion2
if "%opcion%"=="3" goto :opcion3
if "%opcion%"=="4" goto :opcion4
if "%opcion%"=="5" goto :opcion5
if "%opcion%"=="6" goto :opcion6
if "%opcion%"=="7" goto :opcion7
if "%opcion%"=="8" goto :opcion8
if "%opcion%"=="9" goto :opcion9
if "%opcion%"=="0" goto :salir

echo.
echo  [ERROR] Opcion no valida
timeout /t 2 >nul
goto :menu

:opcion1
cls
echo.
echo  ============================================================
echo  ARRANQUE AUTOMATICO COMPLETO
echo  ============================================================
echo.
call ARRANQUE_AUTOMATICO_COMPLETO.bat
goto :menu

:opcion2
cls
echo.
echo  ============================================================
echo  ARRANCAR SERVIDOR LOCAL
echo  ============================================================
echo.
call ARRANCAR.bat
goto :menu

:opcion3
cls
echo.
echo  ============================================================
echo  ARRANCAR NGROK
echo  ============================================================
echo.
call ADMIN_INICIAR_NGROK.bat
goto :menu

:opcion4
cls
echo.
echo  ============================================================
echo  VERIFICACION DEL SISTEMA
echo  ============================================================
echo.
call VERIFICAR_SERVIDOR.bat
goto :menu

:opcion5
cls
echo.
echo  ============================================================
echo  DETENER SERVICIOS
echo  ============================================================
echo.
call DETENER_TODO.bat
goto :menu

:opcion6
cls
echo.
echo  ============================================================
echo  INSTALAR DEPENDENCIAS
echo  ============================================================
echo.
call INSTALAR_DEPENDENCIAS.bat
goto :menu

:opcion7
cls
echo.
echo  ============================================================
echo  PRUEBA COMPLETA
echo  ============================================================
echo.
call PRUEBA_COMPLETA.bat
goto :menu

:opcion8
cls
echo.
echo  ============================================================
echo  URLS DEL SISTEMA
echo  ============================================================
echo.
echo  Servidor Local:
echo    http://localhost:8000
echo.
echo  Panel de Ngrok:
echo    http://localhost:4040
echo.
echo  OPO Local:
echo    http://localhost:8000/opo
echo.
if exist ngrok_url.txt (
    set /p NGROK_URL=<ngrok_url.txt
    echo  URL Publica de Ngrok:
    echo    !NGROK_URL!
    echo.
    echo  OPO Publico:
    echo    !NGROK_URL!/opo
) else (
    echo  URL Publica: No disponible (ngrok no iniciado)
)
echo.
echo  ============================================================
echo.
pause
goto :menu

:opcion9
cls
echo.
echo  ============================================================
echo  DOCUMENTACION DISPONIBLE
echo  ============================================================
echo.
echo  [1] LEEME.md - Guia de inicio rapido
echo  [2] INSTRUCCIONES_ARRANQUE.txt - Guia detallada
echo  [3] SOLUCION_ERROR_NGROK.md - Solucion de errores
echo.
echo  ============================================================
echo.
set /p doc="  Selecciona documento (1-3) o Enter para volver: "

if "%doc%"=="1" start LEEME.md
if "%doc%"=="2" start INSTRUCCIONES_ARRANQUE.txt
if "%doc%"=="3" start SOLUCION_ERROR_NGROK.md

goto :menu

:salir
cls
echo.
echo  ============================================================
echo  Gracias por usar DVDcoin Bank
echo  ============================================================
echo.
timeout /t 2 >nul
exit

