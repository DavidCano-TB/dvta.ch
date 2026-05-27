@echo off
REM ============================================================
REM VERIFICAR ESTADO DEL SERVIDOR DVDCOIN
REM ============================================================

echo ============================================================
echo VERIFICACION DEL SERVIDOR DVDCOIN
echo ============================================================
echo.

echo Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El servidor NO esta corriendo en el puerto 8000
    echo.
    echo Para iniciar el servidor, ejecuta:
    echo   ARRANCAR.bat
    echo.
    echo O para iniciar servidor + ngrok:
    echo   ARRANQUE_AUTOMATICO_COMPLETO.bat
) else (
    echo [OK] Servidor corriendo en puerto 8000
    echo.
    echo Probando conexion local...
    curl -s -o nul -w "Codigo HTTP: %%{http_code}\n" http://localhost:8000
    echo.
    echo URL local: http://localhost:8000
)

echo.
echo Verificando ngrok...
netstat -ano | findstr ":4040" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ngrok NO esta corriendo
    echo.
    echo Para iniciar ngrok, ejecuta:
    echo   ADMIN_INICIAR_NGROK.bat
) else (
    echo [OK] Ngrok corriendo
    echo Panel ngrok: http://localhost:4040
    echo.
    if exist ngrok_url.txt (
        set /p NGROK_URL=<ngrok_url.txt
        echo URL publica: !NGROK_URL!
    )
)

echo.
echo ============================================================
pause
