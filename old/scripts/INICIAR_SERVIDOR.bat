@echo off
chcp 65001 >nul
title 🚀 DVDcoin - Servidor Principal
color 0A

echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 INICIANDO SERVIDOR DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Detener procesos anteriores
echo 🛑 Deteniendo procesos anteriores...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no instalado
    pause
    exit /b 1
)
echo ✅ Python encontrado
echo.

REM Verificar main.py
if not exist "main.py" (
    echo ❌ ERROR: main.py no encontrado
    pause
    exit /b 1
)
echo ✅ main.py encontrado
echo.

REM Iniciar servidor Python con Uvicorn
echo 🐍 Iniciando servidor FastAPI en 0.0.0.0:8000...
echo.
start "DVDcoin Server" /MIN python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ❌ ERROR: Servidor no está corriendo en puerto 8000
    echo.
    pause
    exit /b 1
)
echo ✅ Servidor iniciado correctamente en puerto 8000
echo.

REM Verificar cloudflared
if not exist "cloudflared.exe" (
    echo ⚠️  cloudflared.exe no encontrado
    echo 📥 Descargando cloudflared.exe...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if not exist "cloudflared.exe" (
        echo ❌ No se pudo descargar cloudflared.exe
        pause
        exit /b 1
    )
    echo ✅ cloudflared.exe descargado
    echo.
)
echo ✅ cloudflared.exe encontrado
echo.

REM Verificar configuración
if not exist "cloudflare-config.yml" (
    echo ❌ ERROR: cloudflare-config.yml no encontrado
    pause
    exit /b 1
)
echo ✅ cloudflare-config.yml encontrado
echo.

REM Iniciar túnel Cloudflare
echo 🌐 Iniciando túnel Cloudflare...
echo.
start "Cloudflare Tunnel" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin
timeout /t 8 /nobreak >nul

REM Verificar cloudflared
tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ❌ ERROR: cloudflared no está corriendo
    pause
    exit /b 1
)
echo ✅ Túnel Cloudflare iniciado correctamente
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ SISTEMA INICIADO CORRECTAMENTE
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 Tu aplicación está disponible en:
echo.
echo    ✅ https://app.david.ch
echo    ✅ https://localhost.david.ch
echo.
echo 🔒 Certificado SSL: Automático (Cloudflare)
echo 🌍 Acceso: Desde cualquier red y dispositivo
echo 📱 Compatible: PC, móvil, tablet, in-app browsers
echo.
echo 📊 Para verificar estado: VERIFICAR_DVD_CH.bat
echo 🛑 Para detener: DETENER_TODO.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo Los servicios están corriendo en segundo plano.
echo Puedes cerrar esta ventana.
echo.
timeout /t 15
exit
