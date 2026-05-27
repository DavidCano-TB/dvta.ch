@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   🚀 INICIANDO DVDBANK
echo ═══════════════════════════════════════════════════════════
echo.

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

REM Matar procesos antiguos
echo [1/5] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Liberar puerto 8000
netstat -ano | findstr ":8000" > temp_port.txt 2>nul
for /f "tokens=5" %%a in (temp_port.txt) do (
    taskkill /F /PID %%a >nul 2>&1
)
del temp_port.txt 2>nul

REM Iniciar servidor Python
echo [2/5] Iniciando servidor Python...
start "DVDBank Server" /MIN cmd /c "python main.py > logs\python_server.log 2>&1"

REM Esperar a que el servidor esté listo
echo [3/5] Esperando servidor (8 segundos)...
timeout /t 8 /nobreak >nul

REM Verificar que el servidor esté corriendo
python -c "import requests; requests.get('http://localhost:8000', timeout=2)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ El servidor no responde
    echo Abriendo localhost de todas formas...
    start http://localhost:8000
    timeout /t 3 >nul
    exit /b 1
)

echo ✅ Servidor corriendo en puerto 8000

REM Iniciar Quick Tunnel de Cloudflare
if exist "cloudflared.exe" (
    echo [4/5] Iniciando túnel Cloudflare...
    del logs\cloudflare_quick.log 2>nul
    start "Cloudflare Tunnel" /MIN cmd /c "cloudflared tunnel --url http://localhost:8000 > logs\cloudflare_quick.log 2>&1"
    
    echo [5/5] Esperando URL del túnel (15 segundos)...
    timeout /t 15 /nobreak >nul
    
    REM Intentar obtener la URL del túnel
    if exist "logs\cloudflare_quick.log" (
        for /f "tokens=*" %%i in ('findstr /C:"https://" logs\cloudflare_quick.log') do (
            set "LINE=%%i"
            goto :FOUND_URL
        )
    )
    
    :FOUND_URL
    if defined LINE (
        REM Extraer solo la URL usando PowerShell
        for /f "delims=" %%j in ('powershell -Command "$line='%LINE%'; if($line -match 'https://[a-z0-9-]+\.trycloudflare\.com'){$matches[0]}"') do (
            set "TUNNEL_URL=%%j"
        )
    )
    
    if defined TUNNEL_URL (
        echo.
        echo ═══════════════════════════════════════════════════════════
        echo   ✅ SISTEMA INICIADO
        echo ═══════════════════════════════════════════════════════════
        echo.
        echo   Local:   http://localhost:8000
        echo   Público: %TUNNEL_URL%
        echo.
        echo   Abriendo navegador...
        echo ═══════════════════════════════════════════════════════════
        echo.
        start %TUNNEL_URL%
    ) else (
        echo.
        echo ⚠️  No se pudo obtener URL del túnel
        echo    Abriendo localhost...
        echo.
        start http://localhost:8000
    )
) else (
    echo [4/5] cloudflared.exe no encontrado
    echo [5/5] Abriendo localhost...
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   ✅ SERVIDOR INICIADO
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo   Local: http://localhost:8000
    echo.
    echo   Abriendo navegador...
    echo ═══════════════════════════════════════════════════════════
    echo.
    start http://localhost:8000
)

timeout /t 2 >nul
exit
