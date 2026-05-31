@echo off
chcp 65001 >nul
title DVDcoin - REINICIO FORZADO
color 0C

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   🔥 REINICIO FORZADO - DVDcoin Platform                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo ═══ PASO 1: Escaneando puertos del proyecto ═══
echo.

echo [8000] Bank principal:
netstat -ano | findstr ":8000 " | findstr "LISTENING"
echo.
echo [8001] Exams / Hub:
netstat -ano | findstr ":8001 " | findstr "LISTENING"
echo.
echo [8002] Games:
netstat -ano | findstr ":8002 " | findstr "LISTENING"
echo.

echo ═══ PASO 2: MATANDO TODO (forzado) ═══
echo.

REM Matar todos los python
echo   → Matando todos los procesos Python...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Matar cloudflared
echo   → Matando Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe >nul 2>&1

REM Matar por PID en puertos específicos
echo   → Matando PIDs en puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo     Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo   → Matando PIDs en puerto 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001 " ^| findstr "LISTENING"') do (
    echo     Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo   → Matando PIDs en puerto 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002 " ^| findstr "LISTENING"') do (
    echo     Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo   ✓ Todo muerto.
echo.

REM Esperar a que los puertos se liberen
echo ═══ PASO 3: Esperando liberación de puertos... ═══
timeout /t 3 /nobreak >nul
echo   ✓ Puertos libres.
echo.

echo ═══ PASO 4: Git pull (actualizar código) ═══
echo.
git pull
echo.

echo ═══ PASO 5: DESPLEGANDO ═══
echo.

echo   → Iniciando Bank (puerto 8000)...
start "DVDcoin Bank [8000]" /min cmd /c "cd /d %~dp0 && python main.py"
timeout /t 4 /nobreak >nul

echo   → Iniciando Exams/Hub (puerto 8001)...
start "DVDcoin Exams [8001]" /min cmd /c "cd /d %~dp0modules\exams && python app_exams.py"
timeout /t 4 /nobreak >nul

echo   → Iniciando Cloudflare Tunnel...
where cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%~dp0cloudflare-dvta-config.yml" (
        start "Cloudflare Tunnel" /min cmd /c "cloudflared tunnel --config %~dp0cloudflare-dvta-config.yml run"
        timeout /t 3 /nobreak >nul
        echo   ✓ Tunnel iniciado
    ) else (
        echo   ⚠ No se encontró cloudflare-dvta-config.yml
    )
) else (
    echo   ⚠ cloudflared no instalado
)

echo.
echo ═══ PASO 6: Verificación ═══
echo.
timeout /t 2 /nobreak >nul

set OK=0
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Puerto 8000 - Bank OK & set /a OK+=1) else (echo   ❌ Puerto 8000 - Bank FALLO)

netstat -ano | findstr ":8001 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Puerto 8001 - Exams OK & set /a OK+=1) else (echo   ❌ Puerto 8001 - Exams FALLO)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (echo   ✅ Cloudflare Tunnel activo & set /a OK+=1) else (echo   ⚠ Tunnel no activo)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
if %OK% geq 2 (
    echo ║   ✅ DESPLIEGUE COMPLETADO - %OK% servicios activos          ║
) else (
    echo ║   ⚠  DESPLIEGUE PARCIAL - %OK% servicios activos             ║
)
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   URLs:
echo     Local:  http://localhost:8000/bank
echo     Web:    https://dvta.ch
echo.
pause
