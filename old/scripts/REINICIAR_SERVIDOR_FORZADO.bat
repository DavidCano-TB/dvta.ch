@echo off
echo ========================================
echo REINICIO FORZADO DEL SERVIDOR
echo ========================================
echo.
echo Matando todos los procesos Python y ngrok...
echo.

REM Matar TODOS los procesos Python
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
taskkill /F /IM py.exe 2>nul

REM Matar TODOS los procesos ngrok
taskkill /F /IM ngrok.exe 2>nul

REM Esperar a que los procesos terminen
timeout /t 3 /nobreak >nul

echo.
echo Limpiando cache de Python...
echo.

REM Eliminar archivos .pyc y __pycache__
cd /d %~dp0
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo Cache limpiado. Iniciando servidor...
echo.

REM Iniciar servidor en una nueva ventana
start "DVDCoin Server" cmd /k "cd /d %~dp0 && python src\main.py"

REM Esperar a que el servidor inicie
timeout /t 5 /nobreak >nul

echo.
echo Iniciando ngrok...
echo.

REM Iniciar ngrok en una nueva ventana
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
echo CAMBIOS APLICADOS:
echo   - Eliminada opcion "Ni si ni no"
echo   - Solo respuestas "Si" o "No"
echo   - Cache de Python limpiado
echo ========================================
echo.
pause
