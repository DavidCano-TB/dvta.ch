@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Iniciando sistema DVDBank...

REM Matar procesos antiguos
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Liberar puerto 8000
netstat -ano | findstr ":8000" > temp_port.txt
for /f "tokens=5" %%a in (temp_port.txt) do (
    taskkill /F /PID %%a >nul 2>&1
)
del temp_port.txt 2>nul

REM Iniciar servidor Python
start "DVDBank Server" /MIN python main.py

REM Esperar a que el servidor esté listo
echo Esperando servidor...
timeout /t 8 /nobreak >nul

REM Iniciar Quick Tunnel de Cloudflare (funciona inmediatamente)
if exist "cloudflared.exe" (
    start "Cloudflare Tunnel" /MIN cloudflared tunnel --url http://localhost:8000
    echo Esperando túnel Cloudflare...
    timeout /t 15 /nobreak >nul
    
    REM Intentar obtener la URL del túnel
    for /f "delims=" %%i in ('powershell -Command "Get-Content logs\cloudflare_quick.log -Tail 50 -ErrorAction SilentlyContinue | Select-String -Pattern 'https://.*\.trycloudflare\.com' | Select-Object -Last 1 | ForEach-Object { $_.Matches.Value }"') do set TUNNEL_URL=%%i
    
    if defined TUNNEL_URL (
        echo Abriendo %TUNNEL_URL%
        start %TUNNEL_URL%
    ) else (
        echo No se pudo obtener URL del túnel, abriendo localhost
        start http://localhost:8000
    )
) else (
    echo cloudflared.exe no encontrado, abriendo localhost
    start http://localhost:8000
)

exit
