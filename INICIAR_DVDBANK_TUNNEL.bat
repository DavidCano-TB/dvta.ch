@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO DVDBANK - dvta.ch (Túnel Configurado)
echo ═══════════════════════════════════════════════════════════════════════════

REM Detener procesos anteriores
echo [1/4] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Crear carpeta de logs
if not exist "logs" mkdir logs

REM Limpiar logs anteriores
del /Q logs\server.log >nul 2>&1
del /Q logs\tunnel.log >nul 2>&1

REM Iniciar servidor Python
echo [2/4] Iniciando servidor Python en puerto 8000...
start "DVDBank Server" /MIN cmd /c "python main.py > logs\server.log 2>&1"
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo
echo [3/4] Verificando servidor...
tasklist | findstr "python.exe" >nul
if errorlevel 1 (
    echo ERROR: El servidor Python no se inició correctamente
    echo Revisa logs\server.log para más detalles
    pause
    exit /b 1
)
echo     Servidor Python: OK

REM Verificar que existe el archivo de configuración
if not exist "cloudflare-dvta-config.yml" (
    echo.
    echo ERROR: Archivo de configuración no encontrado
    echo.
    echo Ejecuta primero: CONFIGURAR_TUNNEL_DVTA_CH.bat
    echo.
    pause
    exit /b 1
)

REM Iniciar túnel Cloudflare con configuración
echo [4/4] Iniciando túnel Cloudflare para dvta.ch...
start "Cloudflare Tunnel" /MIN cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run dvta-tunnel > logs\tunnel.log 2>&1"
timeout /t 10 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ SISTEMA INICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  URLs disponibles:
echo    • https://dvta.ch
echo    • https://www.dvta.ch
echo    • http://localhost:8000 (local)
echo.
echo  Abriendo navegador en https://dvta.ch...
echo ═══════════════════════════════════════════════════════════════════════════

timeout /t 3 /nobreak >nul
start https://dvta.ch

echo.
echo Sistema iniciado. Puedes cerrar esta ventana.
timeout /t 5 /nobreak >nul
exit
