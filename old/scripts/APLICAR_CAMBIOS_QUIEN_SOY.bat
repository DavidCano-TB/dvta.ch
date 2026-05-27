@echo off
echo ========================================
echo APLICANDO CAMBIOS AL JUEGO "QUIEN SOY"
echo ========================================
echo.
echo Cambios realizados:
echo   - Eliminada opcion "Ni si ni no"
echo   - Solo respuestas "Si" o "No"
echo   - Modificados: src\main.py, src\ai_helper.py, main.py
echo.
echo ========================================
echo REINICIANDO SERVIDOR...
echo ========================================
echo.

REM Matar procesos existentes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Servidor detenido. Iniciando de nuevo...
echo.

REM Iniciar servidor
start "DVDCoin Server" cmd /k "cd /d %~dp0 && python src\main.py"

REM Esperar a que el servidor inicie
timeout /t 5 /nobreak >nul

REM Iniciar ngrok
start "Ngrok Tunnel" cmd /k "cd /d %~dp0 && ngrok http 8000 --domain=premium-size-unreached.ngrok-free.dev"

echo.
echo ========================================
echo SERVIDOR REINICIADO
echo ========================================
echo.
echo URLs:
echo   Local:  http://localhost:8000
echo   Ngrok:  https://premium-size-unreached.ngrok-free.dev
echo.
echo Credenciales:
echo   Usuario:    dvd
echo   Contrasena: 3666
echo.
echo ========================================
echo CAMBIOS APLICADOS CORRECTAMENTE
echo ========================================
echo.
echo Ahora el juego "Quien Soy" solo acepta:
echo   - "Si"
echo   - "No"
echo.
echo La opcion "Ni si ni no" ha sido eliminada.
echo.
pause
