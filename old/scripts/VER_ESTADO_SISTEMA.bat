@echo off
chcp 65001 >nul
title Estado del Sistema DVDBank
color 0B

:LOOP
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 ESTADO DEL SISTEMA DVDBANK - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Actualizado: %date% %time%
echo.

cd /d "%~dp0"

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [1] SERVIDOR PYTHON (Puerto 8000)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Estado:  ✅ CORRIENDO
    tasklist | findstr "python.exe" > temp_pid.txt
    for /f "tokens=2" %%a in (temp_pid.txt) do (
        echo   PID:     %%a
        del temp_pid.txt 2>nul
        goto :PYTHON_FOUND
    )
    :PYTHON_FOUND
    
    curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000 > temp_http.txt 2>&1
    set /p HTTP_CODE=<temp_http.txt
    del temp_http.txt 2>nul
    
    if "%HTTP_CODE%"=="200" (
        echo   HTTP:    ✅ Respondiendo ^(200 OK^)
        echo   URL:     http://localhost:8000
    ) else if "%HTTP_CODE%"=="000" (
        echo   HTTP:    ⚠️  No responde
    ) else (
        echo   HTTP:    ⚠️  Código %HTTP_CODE%
    )
) else (
    echo   Estado:  ❌ NO ACTIVO
    echo   Acción:  Ejecuta INICIAR_SISTEMA_DVTA.bat
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [2] CLOUDFLARE TUNNEL
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Estado:  ✅ CORRIENDO
    tasklist | findstr "cloudflared.exe" > temp_cf_pid.txt
    for /f "tokens=2" %%a in (temp_cf_pid.txt) do (
        echo   PID:     %%a
        del temp_cf_pid.txt 2>nul
        goto :CF_FOUND
    )
    :CF_FOUND
    
    if exist "cloudflare-dvta-config.yml" (
        echo   Tipo:    Named Tunnel ^(dvta-tunnel^)
        echo   Config:  cloudflare-dvta-config.yml
        echo   Dominio: https://dvta.ch
        echo   Dominio: https://www.dvta.ch
    ) else (
        echo   Tipo:    Quick Tunnel ^(temporal^)
        echo   Log:     logs\cloudflare_quick.log
    )
) else (
    echo   Estado:  ❌ NO ACTIVO
    echo   Acción:  Ejecuta INICIAR_SISTEMA_DVTA.bat
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [3] ARCHIVOS DE CONFIGURACIÓN
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist "cloudflared.exe" (
    echo   cloudflared.exe:              ✅ Instalado
) else (
    echo   cloudflared.exe:              ❌ No encontrado
)

if exist "cloudflare-dvta-config.yml" (
    echo   cloudflare-dvta-config.yml:   ✅ Configurado
) else (
    echo   cloudflare-dvta-config.yml:   ⚠️  No encontrado ^(usando Quick Tunnel^)
)

if exist "main.py" (
    echo   main.py:                      ✅ Encontrado
) else (
    echo   main.py:                      ❌ No encontrado
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [4] LOGS RECIENTES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist "logs\python_server.log" (
    echo   Python ^(últimas 3 líneas^):
    powershell -Command "Get-Content logs\python_server.log -Tail 3 | ForEach-Object { Write-Host '     ' $_ }"
) else (
    echo   Python: Sin logs
)
echo.

if exist "logs\cloudflare_tunnel.log" (
    echo   Cloudflare ^(últimas 3 líneas^):
    powershell -Command "Get-Content logs\cloudflare_tunnel.log -Tail 3 | ForEach-Object { Write-Host '     ' $_ }"
) else if exist "logs\cloudflare_quick.log" (
    echo   Cloudflare Quick ^(últimas 3 líneas^):
    powershell -Command "Get-Content logs\cloudflare_quick.log -Tail 3 | ForEach-Object { Write-Host '     ' $_ }"
) else (
    echo   Cloudflare: Sin logs
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   Presiona Ctrl+C para salir, o espera 10 segundos para actualizar...
echo ═══════════════════════════════════════════════════════════════════════════
echo.

timeout /t 10 /nobreak >nul
goto :LOOP
