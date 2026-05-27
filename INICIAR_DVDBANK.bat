@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO DVDBANK - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════

REM Detener procesos anteriores
echo [1/5] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Crear carpeta de logs
if not exist "logs" mkdir logs

REM Limpiar logs anteriores
del /Q logs\server.log >nul 2>&1
del /Q logs\tunnel.log >nul 2>&1
del /Q logs\tunnel_url.txt >nul 2>&1

REM Iniciar servidor Python
echo [2/5] Iniciando servidor Python en puerto 8000...
start "DVDBank Server" /MIN cmd /c "python main.py > logs\server.log 2>&1"
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo
echo [3/5] Verificando servidor...
tasklist | findstr "python.exe" >nul
if errorlevel 1 (
    echo ERROR: El servidor Python no se inició correctamente
    echo Revisa logs\server.log para más detalles
    pause
    exit /b 1
)
echo     Servidor Python: OK

REM Iniciar túnel Cloudflare Quick Tunnel
if exist "cloudflared.exe" (
    echo [4/5] Iniciando túnel Cloudflare...
    start "Cloudflare Tunnel" /MIN cmd /c "cloudflared.exe tunnel --url http://localhost:8000 > logs\tunnel.log 2>&1"
    timeout /t 15 /nobreak >nul
    
    REM Extraer URL del túnel
    echo [5/5] Obteniendo URL del túnel...
    powershell -Command "$content = Get-Content logs\tunnel.log -Raw; if ($content -match 'https://[a-zA-Z0-9-]+\.trycloudflare\.com') { $matches[0] | Out-File -FilePath logs\tunnel_url.txt -Encoding ASCII -NoNewline }"
    
    REM Verificar si se obtuvo la URL
    if exist "logs\tunnel_url.txt" (
        set /p TUNNEL_URL=<logs\tunnel_url.txt
        if defined TUNNEL_URL (
            echo.
            echo ═══════════════════════════════════════════════════════════════════════════
            echo  SISTEMA INICIADO CORRECTAMENTE
            echo ═══════════════════════════════════════════════════════════════════════════
            echo.
            echo  URL del túnel: !TUNNEL_URL!
            echo  URL local:     http://localhost:8000
            echo.
            echo  Abriendo navegador...
            echo ═══════════════════════════════════════════════════════════════════════════
            timeout /t 2 /nobreak >nul
            start !TUNNEL_URL!
            exit
        )
    )
    
    REM Si no se pudo obtener la URL del túnel, abrir localhost
    echo     ADVERTENCIA: No se pudo obtener la URL del túnel
    echo     Abriendo localhost:8000...
    start http://localhost:8000
) else (
    echo [4/5] cloudflared.exe no encontrado
    echo [5/5] Abriendo localhost:8000...
    start http://localhost:8000
)

echo.
echo Sistema iniciado
timeout /t 3 /nobreak >nul
exit
