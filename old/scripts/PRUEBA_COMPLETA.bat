@echo off
REM ============================================================
REM PRUEBA COMPLETA DEL SISTEMA DVDCOIN
REM ============================================================

echo ============================================================
echo PRUEBA COMPLETA DEL SISTEMA DVDCOIN
echo ============================================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    goto :error
)
python --version
echo [OK] Python instalado
echo.

echo [2/6] Verificando uvicorn...
pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uvicorn no esta instalado
    echo Ejecuta: INSTALAR_DEPENDENCIAS.bat
    goto :error
)
echo [OK] uvicorn instalado
echo.

echo [3/6] Verificando FastAPI...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [ERROR] fastapi no esta instalado
    echo Ejecuta: INSTALAR_DEPENDENCIAS.bat
    goto :error
)
echo [OK] FastAPI instalado
echo.

echo [4/6] Verificando estructura de archivos...
if not exist "src\main.py" (
    echo [ERROR] No se encuentra src\main.py
    goto :error
)
echo [OK] src\main.py existe
echo.

echo [5/6] Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [ADVERTENCIA] El puerto 8000 ya esta en uso
    echo Ejecuta DETENER_TODO.bat para liberar el puerto
    echo.
) else (
    echo [OK] Puerto 8000 disponible
    echo.
)

echo [6/6] Verificando ngrok...
ngrok version >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] ngrok no esta instalado o no esta en PATH
    echo El servidor funcionara localmente, pero no podras acceder remotamente
    echo Descarga ngrok desde: https://ngrok.com/download
    echo.
) else (
    ngrok version
    echo [OK] ngrok instalado
    echo.
    
    if not exist "config\.ngrok_token" (
        echo [ADVERTENCIA] Token de ngrok no configurado
        echo Crea el archivo config\.ngrok_token con tu token
        echo.
    ) else (
        echo [OK] Token de ngrok configurado
        echo.
    )
)

echo ============================================================
echo RESUMEN DE LA PRUEBA
echo ============================================================
echo.
echo Sistema listo para usar.
echo.
echo Puedes ejecutar:
echo   - ARRANCAR.bat (solo servidor local)
echo   - ARRANQUE_AUTOMATICO_COMPLETO.bat (servidor + ngrok)
echo.
goto :end

:error
echo.
echo ============================================================
echo PRUEBA FALLIDA
echo ============================================================
echo.
echo Hay problemas que deben resolverse antes de continuar.
echo Revisa los errores anteriores.
echo.
pause
exit /b 1

:end
pause
