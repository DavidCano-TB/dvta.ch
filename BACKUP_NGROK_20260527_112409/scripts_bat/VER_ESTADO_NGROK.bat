@echo off
title ESTADO DEL SISTEMA NGROK
cd /d "%~dp0"
color 0B

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║         ESTADO DEL SISTEMA - NGROK               ║
echo ╚══════════════════════════════════════════════════╝
echo.

echo [1] SERVIDOR LOCAL (Puerto 8000)
echo ────────────────────────────────────────────────────
curl -s http://127.0.0.1:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   Estado: ✓ ACTIVO
    echo   URL:    http://localhost:8000
) else (
    echo   Estado: ✗ INACTIVO
    echo   Accion: Ejecuta "python start.py" para iniciar
)

echo.
echo [2] NGROK (Puerto 4040)
echo ────────────────────────────────────────────────────
curl -s http://127.0.0.1:4040/api/tunnels >nul 2>&1
if %errorlevel% equ 0 (
    echo   Estado: ✓ ACTIVO
    echo   Panel:  http://localhost:4040
    
    REM Obtener URL publica
    curl -s http://127.0.0.1:4040/api/tunnels > ngrok_temp.json
    for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_temp.json | ConvertFrom-Json; if ($json.tunnels.Count -gt 0) { $json.tunnels[0].public_url } else { '' }"') do set NGROK_URL=%%i
    del ngrok_temp.json
    
    if not "%NGROK_URL%"=="" (
        echo   URL:    %NGROK_URL%
    ) else (
        echo   URL:    No disponible
    )
) else (
    echo   Estado: ✗ INACTIVO
    echo   Accion: Ejecuta "python start.py" para iniciar
)

echo.
echo [3] CONFIGURACION
echo ────────────────────────────────────────────────────
if exist "config\ngrok_config.txt" (
    echo   Archivo: ✓ Encontrado
    
    REM Verificar token
    type config\ngrok_config.txt | findstr "NGROK_TOKEN" | findstr /V "TU_TOKEN_AQUI" >nul
    if %errorlevel% equ 0 (
        echo   Token:   ✓ Configurado
    ) else (
        echo   Token:   ✗ No configurado
        echo   Accion:  Edita config\ngrok_config.txt
    )
    
    REM Mostrar dominio
    for /f "tokens=2 delims==" %%i in ('type config\ngrok_config.txt ^| findstr "NGROK_DOMAIN"') do (
        echo   Dominio: %%i
    )
) else (
    echo   Archivo: ✗ No encontrado
    echo   Accion:  Ejecuta SOLUCIONAR_NGROK_AHORA.bat
)

echo.
echo [4] PROCESOS ACTIVOS
echo ────────────────────────────────────────────────────

REM Verificar procesos Python
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Python:  ✓ Corriendo
    tasklist | findstr "python.exe" > temp_py_pid.txt
    for /f "tokens=2" %%a in (temp_py_pid.txt) do (
        echo            PID: %%a
    )
    del temp_py_pid.txt 2>nul
) else (
    echo   Python:  ✗ No activo
)

REM Verificar procesos ngrok
tasklist | findstr "ngrok.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Ngrok:   ✓ Corriendo
    tasklist | findstr "ngrok.exe" > temp_ng_pid.txt
    for /f "tokens=2" %%a in (temp_ng_pid.txt) do (
        echo            PID: %%a
    )
    del temp_ng_pid.txt 2>nul
) else (
    echo   Ngrok:   ✗ No activo
)

echo.
echo [5] CONECTIVIDAD
echo ────────────────────────────────────────────────────

REM Verificar dominio publico si existe
if not "%NGROK_URL%"=="" (
    curl -s -o nul -w "%%{http_code}" %NGROK_URL% > http_code.txt 2>&1
    set /p HTTP_CODE=<http_code.txt
    del http_code.txt
    
    if "%HTTP_CODE%"=="200" (
        echo   Dominio: ✓ ACCESIBLE
        echo   Codigo:  200 OK
    ) else if "%HTTP_CODE%"=="000" (
        echo   Dominio: ✗ NO RESPONDE
        echo   Error:   ERR_NGROK_3200 (Endpoint offline)
    ) else (
        echo   Dominio: ⚠ RESPONDE CON ERROR
        echo   Codigo:  %HTTP_CODE%
    )
) else (
    echo   Dominio: - No disponible para verificar
)

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║              RESUMEN Y ACCIONES                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

REM Determinar estado general
curl -s http://127.0.0.1:8000 >nul 2>&1
set SERVER_OK=%errorlevel%

curl -s http://127.0.0.1:4040/api/tunnels >nul 2>&1
set NGROK_OK=%errorlevel%

if %SERVER_OK% equ 0 if %NGROK_OK% equ 0 (
    echo   Estado General: ✓ TODO FUNCIONANDO
    echo.
    echo   Acciones disponibles:
    echo   - Abrir navegador: start "" "%NGROK_URL%"
    echo   - Ver panel ngrok: start "" "http://localhost:4040"
    echo   - Ver logs: type server.log
) else if %SERVER_OK% neq 0 if %NGROK_OK% neq 0 (
    echo   Estado General: ✗ SISTEMA DETENIDO
    echo.
    echo   Accion recomendada:
    echo   - Ejecuta: SOLUCIONAR_NGROK_AHORA.bat
    echo   - O manualmente: python start.py
) else if %SERVER_OK% equ 0 (
    echo   Estado General: ⚠ SERVIDOR OK, NGROK INACTIVO
    echo.
    echo   Accion recomendada:
    echo   - Ejecuta: SOLUCIONAR_NGROK_AHORA.bat
) else (
    echo   Estado General: ⚠ NGROK OK, SERVIDOR INACTIVO
    echo.
    echo   Accion recomendada:
    echo   - Ejecuta: python start.py
)

echo.
echo ────────────────────────────────────────────────────
echo   Scripts disponibles:
echo   - SOLUCIONAR_NGROK_AHORA.bat (solucion automatica)
echo   - DIAGNOSTICAR_Y_REPARAR_NGROK.bat (diagnostico)
echo   - REINICIAR_TODO.bat (reinicio completo)
echo ────────────────────────────────────────────────────
echo.
pause
