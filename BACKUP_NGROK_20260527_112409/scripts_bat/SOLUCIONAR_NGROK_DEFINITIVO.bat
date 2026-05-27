@echo off
REM ============================================================
REM SOLUCIÓN DEFINITIVA PARA PROBLEMAS DE NGROK
REM ============================================================
title Solucionando ngrok...
color 0A

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║      SOLUCIÓN DEFINITIVA DE NGROK                ║
echo ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── PASO 1: Detener todo ──
echo [PASO 1/7] Deteniendo procesos existentes...
echo ════════════════════════════════════════════════════

taskkill /F /IM ngrok.exe >nul 2>&1
if errorlevel 1 (
    echo   ✓ No había procesos ngrok corriendo
) else (
    echo   ✓ Procesos ngrok detenidos
)

timeout /t 2 /nobreak >nul
echo.

REM ── PASO 2: Verificar configuración principal ──
echo [PASO 2/7] Verificando configuración principal...
echo ════════════════════════════════════════════════════

if not exist "config" mkdir config

if not exist "config\ngrok_config.txt" (
    echo   ✗ ERROR: config\ngrok_config.txt no existe
    echo.
    echo   Creando archivo de plantilla...
    (
        echo # Configuración de ngrok para DVDcoin Bank
        echo # Este archivo contiene el token y dominio reservado de ngrok
        echo # Formato: VARIABLE=valor ^(sin espacios alrededor del =^)
        echo.
        echo NGROK_TOKEN=TU_TOKEN_AQUI
        echo NGROK_DOMAIN=tu-dominio.ngrok-free.dev
        echo.
        echo.
    ) > config\ngrok_config.txt
    
    echo   ✓ Archivo creado: config\ngrok_config.txt
    echo.
    echo   ACCIÓN REQUERIDA:
    echo   1. Abre config\ngrok_config.txt
    echo   2. Reemplaza TU_TOKEN_AQUI con tu token de ngrok
    echo   3. Reemplaza tu-dominio.ngrok-free.dev con tu dominio reservado
    echo   4. Vuelve a ejecutar este script
    echo.
    notepad config\ngrok_config.txt
    pause
    exit /b 1
)

REM Leer configuración
for /f "tokens=1,2 delims==" %%a in (config\ngrok_config.txt) do (
    if "%%a"=="NGROK_TOKEN" set NGROK_TOKEN=%%b
    if "%%a"=="NGROK_DOMAIN" set NGROK_DOMAIN=%%b
)

if "%NGROK_TOKEN%"=="" (
    echo   ✗ ERROR: NGROK_TOKEN no configurado
    echo.
    echo   Abre config\ngrok_config.txt y configura tu token
    notepad config\ngrok_config.txt
    pause
    exit /b 1
)

if "%NGROK_TOKEN%"=="TU_TOKEN_AQUI" (
    echo   ✗ ERROR: Debes reemplazar TU_TOKEN_AQUI con tu token real
    echo.
    notepad config\ngrok_config.txt
    pause
    exit /b 1
)

if "%NGROK_DOMAIN%"=="" (
    echo   ✗ ERROR: NGROK_DOMAIN no configurado
    echo.
    echo   Abre config\ngrok_config.txt y configura tu dominio
    notepad config\ngrok_config.txt
    pause
    exit /b 1
)

if "%NGROK_DOMAIN%"=="tu-dominio.ngrok-free.dev" (
    echo   ✗ ERROR: Debes reemplazar tu-dominio.ngrok-free.dev con tu dominio real
    echo.
    notepad config\ngrok_config.txt
    pause
    exit /b 1
)

echo   ✓ Token configurado: %NGROK_TOKEN:~0,20%...
echo   ✓ Dominio configurado: %NGROK_DOMAIN%
echo.

REM ── PASO 3: Sincronizar archivos ──
echo [PASO 3/7] Sincronizando archivos de configuración...
echo ════════════════════════════════════════════════════

if not exist "conf" mkdir conf

REM Crear backup si existe
if exist "conf\.ngrok_token" (
    copy /Y "conf\.ngrok_token" "conf\.ngrok_token.backup" >nul 2>&1
    echo   ✓ Backup creado: conf\.ngrok_token.backup
)

REM Escribir configuración sincronizada
(
    echo NGROK_TOKEN=%NGROK_TOKEN%
    echo NGROK_DOMAIN=%NGROK_DOMAIN%
) > conf\.ngrok_token

echo   ✓ conf\.ngrok_token actualizado
echo.

REM ── PASO 4: Limpiar archivos temporales ──
echo [PASO 4/7] Limpiando archivos temporales...
echo ════════════════════════════════════════════════════

if exist "ngrok_url.txt" (
    del /F /Q "ngrok_url.txt" >nul 2>&1
    echo   ✓ ngrok_url.txt eliminado
)

if exist "ngrok_temp.json" (
    del /F /Q "ngrok_temp.json" >nul 2>&1
    echo   ✓ ngrok_temp.json eliminado
)

REM Limpiar logs antiguos de ngrok
for %%f in (ngrok_*.log) do (
    del /F /Q "%%f" >nul 2>&1
)
echo   ✓ Logs antiguos limpiados

echo.

REM ── PASO 5: Configurar authtoken ──
echo [PASO 5/7] Configurando authtoken en ngrok...
echo ════════════════════════════════════════════════════

where ngrok >nul 2>&1
if errorlevel 1 (
    if exist "ngrok.exe" (
        set NGROK_CMD=ngrok.exe
        echo   ✓ Usando ngrok.exe local
    ) else (
        echo   ✗ ERROR: ngrok no encontrado
        echo.
        echo   Descarga ngrok desde: https://ngrok.com/download
        echo   Coloca ngrok.exe en esta carpeta: %CD%
        pause
        exit /b 1
    )
) else (
    set NGROK_CMD=ngrok
    echo   ✓ Usando ngrok del PATH
)

%NGROK_CMD% config add-authtoken %NGROK_TOKEN% >nul 2>&1
if errorlevel 1 (
    echo   ⚠ No se pudo configurar authtoken automáticamente
    echo     Continuando de todas formas...
) else (
    echo   ✓ Authtoken configurado en ngrok
)

echo.

REM ── PASO 6: Verificar/Iniciar servidor ──
echo [PASO 6/7] Verificando servidor local...
echo ════════════════════════════════════════════════════

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Servidor no está corriendo en puerto 8000
    echo.
    echo   Iniciando servidor...
    
    if not exist "main.py" (
        echo   ✗ ERROR: main.py no encontrado
        pause
        exit /b 1
    )
    
    start "DVDcoin Server" /MIN python main.py
    
    REM Esperar a que el servidor arranque
    set /a WAIT_COUNT=0
    :WAIT_SERVER
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        set /a WAIT_COUNT+=1
        if %WAIT_COUNT% LSS 15 goto WAIT_SERVER
        
        echo   ✗ El servidor no arrancó después de 15 segundos
        echo     Verifica server.log para más detalles
        pause
        exit /b 1
    )
    
    echo   ✓ Servidor iniciado correctamente
) else (
    echo   ✓ Servidor ya está corriendo en puerto 8000
)

echo.

REM ── PASO 7: Iniciar ngrok ──
echo [PASO 7/7] Iniciando ngrok con dominio reservado...
echo ════════════════════════════════════════════════════
echo.
echo   Dominio: %NGROK_DOMAIN%
echo   Puerto:  8000
echo.

start "ngrok - %NGROK_DOMAIN%" %NGROK_CMD% http 8000 --domain=%NGROK_DOMAIN% --log=stdout --log-level=info

REM Esperar a que ngrok se conecte
echo   Esperando conexión de ngrok...
set /a WAIT_COUNT=0
:WAIT_NGROK
timeout /t 1 /nobreak >nul
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    set /a WAIT_COUNT+=1
    if %WAIT_COUNT% LSS 15 goto WAIT_NGROK
    
    echo   ✗ ngrok no se conectó después de 15 segundos
    echo.
    echo   Verifica:
    echo   1. Que tu token sea válido
    echo   2. Que tu dominio esté activo en https://dashboard.ngrok.com
    echo   3. Que no haya firewall bloqueando ngrok
    echo.
    pause
    exit /b 1
)

echo   ✓ ngrok conectado

REM Obtener URL pública
timeout /t 2 /nobreak >nul
curl -s http://localhost:4040/api/tunnels > ngrok_temp.json 2>nul
for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_temp.json | ConvertFrom-Json; if ($json.tunnels.Count -gt 0) { $json.tunnels[0].public_url } else { '' }"') do set PUBLIC_URL=%%i
del ngrok_temp.json >nul 2>&1

if "%PUBLIC_URL%"=="" (
    echo   ⚠ No se pudo obtener la URL pública
    echo.
    echo   Abre el panel de ngrok para ver el estado:
    echo   http://localhost:4040
    echo.
    start "" "http://localhost:4040"
) else (
    echo   ✓ URL pública obtenida
    echo.
    
    REM Guardar URL
    echo %PUBLIC_URL% > ngrok_url.txt
    
    REM Verificar accesibilidad
    echo   Verificando accesibilidad...
    curl -s -o nul -w "%%{http_code}" "%PUBLIC_URL%" > http_code_temp.txt 2>&1
    set /p HTTP_CODE=<http_code_temp.txt
    del http_code_temp.txt >nul 2>&1
    
    echo.
    echo ╔══════════════════════════════════════════════════╗
    echo ║           ✓ NGROK CONFIGURADO                    ║
    echo ╚══════════════════════════════════════════════════╝
    echo.
    echo   URL PÚBLICA:  %PUBLIC_URL%
    echo   LOCAL:        http://localhost:8000
    echo   PANEL NGROK:  http://localhost:4040
    echo.
    
    if "%HTTP_CODE%"=="200" (
        echo   ✓ El sitio responde correctamente
        echo.
        echo   Abriendo en navegador...
        start "" "%PUBLIC_URL%"
    ) else if "%HTTP_CODE%"=="000" (
        echo   ⚠ ADVERTENCIA: Endpoint offline (ERR_NGROK_3200)
        echo.
        echo   Esto puede significar:
        echo   1. El dominio reservado expiró o fue revocado
        echo   2. Hay un problema con tu cuenta de ngrok
        echo.
        echo   Verifica tu cuenta en: https://dashboard.ngrok.com
        echo   Panel de ngrok: http://localhost:4040
        echo.
        start "" "http://localhost:4040"
    ) else (
        echo   ⚠ El sitio responde con código HTTP: %HTTP_CODE%
        echo.
        start "" "%PUBLIC_URL%"
    )
)

echo ════════════════════════════════════════════════════
echo.
echo   Presiona cualquier tecla para cerrar...
pause >nul
