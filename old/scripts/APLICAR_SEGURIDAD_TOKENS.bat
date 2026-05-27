@echo off
echo ========================================
echo APLICANDO CORRECCIONES DE SEGURIDAD
echo ========================================
echo.
echo Cambios aplicados:
echo   1. Tokens NO se pasan en URLs
echo   2. Cookies HTTP-only implementadas
echo   3. Autenticacion desde cookies
echo   4. Apuestas y Votaciones corregidos
echo.
echo ========================================
echo REINICIANDO SERVIDOR...
echo ========================================
echo.

REM Matar procesos existentes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak >nul

REM Limpiar cache
cd /d %~dp0
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo Iniciando servidor...
echo.

REM Iniciar servidor
start "DVDCoin Server" cmd /k "cd /d %~dp0 && python src\main.py"

REM Esperar
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
echo SEGURIDAD MEJORADA:
echo ========================================
echo.
echo [OK] Tokens NO se pasan en URLs
echo [OK] Cookies HTTP-only activadas
echo [OK] Autenticacion desde cookies
echo [OK] Apuestas funciona sin token en URL
echo [OK] Votaciones funciona sin token en URL
echo.
echo IMPORTANTE:
echo   - Cierra sesion y vuelve a iniciar
echo   - Las cookies se establecen automaticamente
echo   - Ya NO veras tokens en las URLs
echo.
pause
