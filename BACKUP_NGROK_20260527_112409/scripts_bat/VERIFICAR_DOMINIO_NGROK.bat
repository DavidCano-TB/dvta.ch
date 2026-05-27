@echo off
chcp 65001 >nul
REM ============================================================
REM VERIFICAR DOMINIO EN DASHBOARD DE NGROK
REM ============================================================
title Verificar dominio ngrok
color 0B

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║      VERIFICAR DOMINIO EN NGROK                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Leer configuración
if exist "config\ngrok_config.txt" (
    for /f "tokens=1,2 delims==" %%a in (config\ngrok_config.txt) do (
        if "%%a"=="NGROK_DOMAIN" set NGROK_DOMAIN=%%b
    )
)

if "%NGROK_DOMAIN%"=="" (
    echo   ⚠ No se encontró NGROK_DOMAIN en la configuración
    echo.
    set NGROK_DOMAIN=tu-dominio
)

echo   Dominio configurado: %NGROK_DOMAIN%
echo.
echo ════════════════════════════════════════════════════
echo.
echo   PASOS PARA VERIFICAR:
echo.
echo   1. Se abrirá el dashboard de ngrok en tu navegador
echo.
echo   2. Inicia sesión si es necesario
echo.
echo   3. Ve a "Domains" en el menú lateral
echo.
echo   4. Busca tu dominio: %NGROK_DOMAIN%
echo.
echo   5. Verifica que esté:
echo      ✓ Activo (Active)
echo      ✓ No expirado
echo      ✓ Asignado a tu cuenta
echo.
echo   6. Si NO aparece o está inactivo:
echo      - Crea un nuevo dominio reservado
echo      - Copia el nuevo dominio
echo      - Edita config\ngrok_config.txt
echo      - Actualiza NGROK_DOMAIN=nuevo-dominio.ngrok-free.dev
echo      - Ejecuta ARREGLAR_NGROK_AHORA.bat
echo.
echo ════════════════════════════════════════════════════
echo.
echo   Presiona cualquier tecla para abrir el dashboard...
pause >nul

REM Abrir dashboard de ngrok
start "" "https://dashboard.ngrok.com/domains"

echo.
echo   ✓ Dashboard abierto en el navegador
echo.
echo   También puedes verificar:
echo   - Tu authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
echo   - Tus túneles activos: https://dashboard.ngrok.com/tunnels/agents
echo.
echo ════════════════════════════════════════════════════
echo.
pause
