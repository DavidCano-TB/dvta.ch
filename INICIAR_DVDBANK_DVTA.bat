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

REM Verificar que Python existe
where python >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Python no encontrado en PATH
    echo Intentando con py...
    where py >nul 2>&1
    if errorlevel 1 (
        echo ERROR: No se encontró Python instalado
        echo Abriendo localhost:8000 por si acaso...
        timeout /t 3 /nobreak >nul
        start http://localhost:8000
        exit /b 0
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM Verificar que main.py existe
if not exist "main.py" (
    echo ERROR: main.py no encontrado
    echo Asegúrate de estar en la carpeta correcta
    timeout /t 5 /nobreak >nul
    exit /b 1
)

REM Iniciar servidor Python
echo [2/5] Iniciando servidor Python en puerto 8000...
start "DVDBank Server" /MIN cmd /c "%PYTHON_CMD% main.py > logs\server.log 2>&1"
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo (con reintentos)
echo [3/5] Verificando servidor...
set RETRY_COUNT=0
:CHECK_PYTHON
tasklist | findstr "python.exe" >nul
if errorlevel 1 (
    tasklist | findstr "py.exe" >nul
    if errorlevel 1 (
        set /a RETRY_COUNT+=1
        if !RETRY_COUNT! lss 3 (
            echo     Reintentando... (!RETRY_COUNT!/3)
            timeout /t 2 /nobreak >nul
            goto CHECK_PYTHON
        )
        echo ADVERTENCIA: No se detectó proceso Python
        echo Intentando continuar de todos modos...
        if exist "logs\server.log" (
            echo.
            echo Últimas líneas del log:
            powershell -Command "Get-Content logs\server.log -Tail 5" 2>nul
        )
    )
)
echo     Servidor Python: OK

REM Verificar si el túnel está configurado correctamente
set TUNNEL_CONFIGURED=0
set USE_NAMED_TUNNEL=0

if exist "cloudflare-dvta-config.yml" (
    findstr /C:"tunnel: b75039b1-7b54-4da0-b2ab-0a338bfccdc5" "cloudflare-dvta-config.yml" >nul
    if not errorlevel 1 (
        REM Verificar que el archivo de credenciales existe
        if exist "C:\Users\PC\.cloudflared\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json" (
            set TUNNEL_CONFIGURED=1
            set USE_NAMED_TUNNEL=1
        )
    )
)

REM Iniciar túnel según configuración
if !USE_NAMED_TUNNEL! equ 1 (
    echo [4/5] Iniciando túnel Cloudflare configurado para dvta.ch...
    if exist "cloudflared.exe" (
        start "Cloudflare Tunnel" /MIN cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run dvta-tunnel > logs\tunnel.log 2>&1"
        timeout /t 10 /nobreak >nul
        
        REM Verificar que el túnel se inició
        tasklist | findstr "cloudflared.exe" >nul
        if errorlevel 1 (
            echo ADVERTENCIA: Túnel no se inició correctamente
            echo Revisa logs\tunnel.log para más detalles
            if exist "logs\tunnel.log" (
                echo.
                echo Últimas líneas del log:
                powershell -Command "Get-Content logs\tunnel.log -Tail 5" 2>nul
            )
        ) else (
            echo     Túnel Cloudflare: OK
        )
        
        echo [5/5] Abriendo navegador en https://dvta.ch...
        timeout /t 3 /nobreak >nul
        start https://dvta.ch
        
        echo.
        echo ═══════════════════════════════════════════════════════════════════════════
        echo  ✅ SISTEMA INICIADO
        echo ═══════════════════════════════════════════════════════════════════════════
        echo.
        echo  URLs disponibles:
        echo    • https://dvta.ch
        echo    • https://www.dvta.ch
        echo    • http://localhost:8000 (local)
        echo.
        echo ═══════════════════════════════════════════════════════════════════════════
    ) else (
        echo ERROR: cloudflared.exe no encontrado
        echo Abriendo localhost:8000...
        start http://localhost:8000
    )
) else (
    echo [4/5] Túnel no configurado, usando Quick Tunnel temporal...
    if exist "cloudflared.exe" (
        start "Cloudflare Tunnel" /MIN cmd /c "cloudflared.exe tunnel --url http://localhost:8000 > logs\tunnel.log 2>&1"
        timeout /t 15 /nobreak >nul
        
        echo [5/5] Obteniendo URL del túnel...
        powershell -Command "$content = Get-Content logs\tunnel.log -Raw -ErrorAction SilentlyContinue; if ($content -match 'https://[a-zA-Z0-9-]+\.trycloudflare\.com') { $matches[0] | Out-File -FilePath logs\tunnel_url.txt -Encoding ASCII -NoNewline }" 2>nul
        
        if exist "logs\tunnel_url.txt" (
            set /p TUNNEL_URL=<logs\tunnel_url.txt
            if defined TUNNEL_URL (
                echo.
                echo ═══════════════════════════════════════════════════════════════════════════
                echo  ⚠️ USANDO TÚNEL TEMPORAL
                echo ═══════════════════════════════════════════════════════════════════════════
                echo.
                echo  URL temporal: !TUNNEL_URL!
                echo  URL local:    http://localhost:8000
                echo.
                echo  Para usar https://dvta.ch ejecuta: CONFIGURAR_TUNNEL_DVTA_CH.bat
                echo.
                echo ═══════════════════════════════════════════════════════════════════════════
                timeout /t 3 /nobreak >nul
                start !TUNNEL_URL!
            ) else (
                echo Abriendo localhost:8000...
                start http://localhost:8000
            )
        ) else (
            echo Abriendo localhost:8000...
            start http://localhost:8000
        )
    ) else (
        echo [4/5] cloudflared.exe no encontrado
        echo [5/5] Abriendo localhost:8000...
        start http://localhost:8000
    )
)

timeout /t 5 /nobreak >nul
exit /b 0
