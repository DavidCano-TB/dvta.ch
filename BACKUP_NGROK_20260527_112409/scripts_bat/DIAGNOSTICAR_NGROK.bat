@echo off
REM ============================================================
REM DIAGNÓSTICO COMPLETO DE NGROK
REM ============================================================
title Diagnóstico de ngrok
color 0E

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║          DIAGNÓSTICO DE NGROK                    ║
echo ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── 1. Verificar archivos de configuración ──
echo [1] ARCHIVOS DE CONFIGURACIÓN
echo ════════════════════════════════════════════════════
echo.

if exist "config\ngrok_config.txt" (
    echo   ✓ config\ngrok_config.txt existe
    echo.
    echo   Contenido:
    echo   ────────────────────────────────────────────────
    type config\ngrok_config.txt | findstr /V "^#" | findstr /V "^$"
    echo   ────────────────────────────────────────────────
    echo.
    
    REM Extraer valores
    for /f "tokens=1,2 delims==" %%a in (config\ngrok_config.txt) do (
        if "%%a"=="NGROK_TOKEN" set CONFIG_TOKEN=%%b
        if "%%a"=="NGROK_DOMAIN" set CONFIG_DOMAIN=%%b
    )
) else (
    echo   ✗ config\ngrok_config.txt NO EXISTE
    echo.
)

if exist "conf\.ngrok_token" (
    echo   ✓ conf\.ngrok_token existe
    echo.
    echo   Contenido:
    echo   ────────────────────────────────────────────────
    type conf\.ngrok_token
    echo   ────────────────────────────────────────────────
    echo.
    
    REM Extraer valores
    for /f "tokens=1,2 delims==" %%a in (conf\.ngrok_token) do (
        if "%%a"=="NGROK_TOKEN" set CONF_TOKEN=%%b
        if "%%a"=="NGROK_DOMAIN" set CONF_DOMAIN=%%b
    )
) else (
    echo   ✗ conf\.ngrok_token NO EXISTE
    echo.
)

REM Verificar consistencia
if defined CONFIG_TOKEN if defined CONF_TOKEN (
    if "%CONFIG_TOKEN%"=="%CONF_TOKEN%" (
        echo   ✓ Tokens coinciden
    ) else (
        echo   ✗ TOKENS NO COINCIDEN
        echo     config: %CONFIG_TOKEN:~0,20%...
        echo     conf:   %CONF_TOKEN:~0,20%...
    )
)

if defined CONFIG_DOMAIN if defined CONF_DOMAIN (
    if "%CONFIG_DOMAIN%"=="%CONF_DOMAIN%" (
        echo   ✓ Dominios coinciden: %CONFIG_DOMAIN%
    ) else (
        echo   ✗ DOMINIOS NO COINCIDEN
        echo     config: %CONFIG_DOMAIN%
        echo     conf:   %CONF_DOMAIN%
    )
)

echo.

REM ── 2. Verificar procesos ──
echo [2] PROCESOS ACTIVOS
echo ════════════════════════════════════════════════════
echo.

tasklist | findstr "ngrok.exe" >nul 2>&1
if errorlevel 1 (
    echo   ✗ ngrok.exe NO está corriendo
) else (
    echo   ✓ ngrok.exe está corriendo
    echo.
    echo   Procesos:
    tasklist | findstr "ngrok.exe"
)

echo.

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Servidor NO está en puerto 8000
) else (
    echo   ✓ Servidor activo en puerto 8000
)

echo.

REM ── 3. Verificar API de ngrok ──
echo [3] API DE NGROK (localhost:4040)
echo ════════════════════════════════════════════════════
echo.

curl -s http://localhost:4040/api/tunnels > ngrok_api_temp.json 2>nul
if errorlevel 1 (
    echo   ✗ No se puede conectar a la API de ngrok
    echo     El panel de ngrok no está disponible
) else (
    echo   ✓ API de ngrok responde
    echo.
    
    REM Extraer información de túneles
    for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_api_temp.json | ConvertFrom-Json; $json.tunnels.Count"') do set TUNNEL_COUNT=%%i
    
    if "%TUNNEL_COUNT%"=="0" (
        echo   ⚠ No hay túneles activos
    ) else (
        echo   ✓ Túneles activos: %TUNNEL_COUNT%
        echo.
        
        REM Obtener URL pública
        for /f "delims=" %%i in ('powershell -Command "$json = Get-Content ngrok_api_temp.json | ConvertFrom-Json; if ($json.tunnels.Count -gt 0) { $json.tunnels[0].public_url } else { '' }"') do set PUBLIC_URL=%%i
        
        if not "%PUBLIC_URL%"=="" (
            echo   URL pública: %PUBLIC_URL%
            
            REM Verificar si la URL responde
            echo.
            echo   Verificando accesibilidad...
            curl -s -o nul -w "%%{http_code}" "%PUBLIC_URL%" > http_code_temp.txt 2>&1
            set /p HTTP_CODE=<http_code_temp.txt
            del http_code_temp.txt
            
            if "%HTTP_CODE%"=="200" (
                echo   ✓ URL responde correctamente (HTTP 200)
            ) else if "%HTTP_CODE%"=="000" (
                echo   ✗ URL NO RESPONDE (ERR_NGROK_3200)
                echo     El endpoint está offline
            ) else (
                echo   ⚠ URL responde con código: %HTTP_CODE%
            )
        )
    )
    
    del ngrok_api_temp.json
)

echo.

REM ── 4. Verificar archivo de URL guardada ──
echo [4] ARCHIVO DE URL GUARDADA
echo ════════════════════════════════════════════════════
echo.

if exist "ngrok_url.txt" (
    echo   ✓ ngrok_url.txt existe
    echo.
    set /p SAVED_URL=<ngrok_url.txt
    echo   URL guardada: !SAVED_URL!
    
    if defined PUBLIC_URL (
        if "!SAVED_URL!"=="%PUBLIC_URL%" (
            echo   ✓ URL guardada coincide con la actual
        ) else (
            echo   ✗ URL guardada NO coincide con la actual
            echo     Guardada: !SAVED_URL!
            echo     Actual:   %PUBLIC_URL%
        )
    )
) else (
    echo   ⚠ ngrok_url.txt no existe
)

echo.

REM ── 5. Verificar ejecutable de ngrok ──
echo [5] EJECUTABLE DE NGROK
echo ════════════════════════════════════════════════════
echo.

where ngrok >nul 2>&1
if errorlevel 1 (
    if exist "ngrok.exe" (
        echo   ✓ ngrok.exe encontrado en carpeta local
    ) else (
        echo   ✗ ngrok.exe NO encontrado
        echo     Descarga desde: https://ngrok.com/download
    )
) else (
    echo   ✓ ngrok encontrado en PATH
    for /f "delims=" %%i in ('where ngrok') do echo     Ubicación: %%i
)

echo.

REM ── RESUMEN Y RECOMENDACIONES ──
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║              RESUMEN Y ACCIONES                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

if not defined CONFIG_TOKEN (
    echo   ✗ PROBLEMA: Configuración no encontrada
    echo     ACCIÓN: Edita config\ngrok_config.txt
    echo.
) else if not defined CONFIG_DOMAIN (
    echo   ✗ PROBLEMA: Dominio no configurado
    echo     ACCIÓN: Agrega NGROK_DOMAIN en config\ngrok_config.txt
    echo.
) else if "%CONFIG_TOKEN%" NEQ "%CONF_TOKEN%" (
    echo   ✗ PROBLEMA: Configuraciones inconsistentes
    echo     ACCIÓN: Ejecuta REINICIAR_NGROK_CORRECTAMENTE.bat
    echo.
) else if "%TUNNEL_COUNT%"=="0" (
    echo   ✗ PROBLEMA: ngrok no tiene túneles activos
    echo     ACCIÓN: Ejecuta REINICIAR_NGROK_CORRECTAMENTE.bat
    echo.
) else if "%HTTP_CODE%"=="000" (
    echo   ✗ PROBLEMA: Endpoint offline (ERR_NGROK_3200)
    echo     POSIBLES CAUSAS:
    echo       1. El dominio reservado expiró o fue revocado
    echo       2. El token de ngrok no es válido
    echo       3. Hay múltiples instancias de ngrok corriendo
    echo.
    echo     ACCIONES:
    echo       1. Verifica tu cuenta en https://dashboard.ngrok.com
    echo       2. Confirma que el dominio %CONFIG_DOMAIN% está activo
    echo       3. Ejecuta: REINICIAR_NGROK_CORRECTAMENTE.bat
    echo.
) else if "%HTTP_CODE%"=="200" (
    echo   ✓ TODO FUNCIONA CORRECTAMENTE
    echo     URL: %PUBLIC_URL%
    echo.
) else (
    echo   ⚠ Estado desconocido
    echo     Revisa el panel de ngrok: http://localhost:4040
    echo.
)

echo ════════════════════════════════════════════════════
echo.
pause
