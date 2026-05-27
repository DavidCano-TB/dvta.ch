@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN DE dvta.ch - PASO A PASO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este asistente te guiará para configurar dvta.ch permanentemente.
echo.
echo IMPORTANTE: Necesitas tener el dominio dvta.ch en tu cuenta de Cloudflare.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

REM ═══════════════════════════════════════════════════════════════════════════
REM PASO 1: Verificar cloudflared.exe
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 1/5: Verificando cloudflared.exe
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    echo Descarga cloudflared desde:
    echo https://github.com/cloudflare/cloudflared/releases
    echo.
    pause
    exit /b 1
)

echo ✅ cloudflared.exe encontrado
echo.
timeout /t 2 /nobreak >nul

REM ═══════════════════════════════════════════════════════════════════════════
REM PASO 2: Login en Cloudflare
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 2/5: Iniciar sesión en Cloudflare
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Se abrirá tu navegador para autorizar cloudflared.
echo.
echo INSTRUCCIONES:
echo   1. Inicia sesión en tu cuenta de Cloudflare
echo   2. Selecciona el dominio dvta.ch
echo   3. Haz clic en "Authorize"
echo   4. Espera el mensaje de confirmación
echo   5. Cierra la pestaña del navegador
echo   6. Vuelve a esta ventana
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo.
echo Abriendo navegador...
echo.
cloudflared.exe tunnel login

if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo iniciar sesión
    echo.
    echo Posibles causas:
    echo   - No tienes cuenta en Cloudflare
    echo   - No autorizaste la aplicación
    echo   - Problemas de conexión
    echo.
    echo Intenta de nuevo o visita: https://dash.cloudflare.com
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sesión iniciada correctamente
echo.
timeout /t 2 /nobreak >nul

REM ═══════════════════════════════════════════════════════════════════════════
REM PASO 3: Crear túnel
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 3/5: Creando túnel
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Verificar si el túnel ya existe
cloudflared.exe tunnel list | findstr "dvta-tunnel" >nul 2>&1
if errorlevel 1 (
    echo Creando nuevo túnel "dvta-tunnel"...
    echo.
    cloudflared.exe tunnel create dvta-tunnel
    
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: No se pudo crear el túnel
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Túnel creado exitosamente
) else (
    echo ✅ El túnel "dvta-tunnel" ya existe
)

echo.
timeout /t 2 /nobreak >nul

REM ═══════════════════════════════════════════════════════════════════════════
REM PASO 4: Configurar DNS
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 4/5: Configurando DNS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo Configurando dvta.ch...
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
echo.

echo Configurando www.dvta.ch...
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch
echo.

echo ✅ DNS configurado
echo.
timeout /t 2 /nobreak >nul

REM ═══════════════════════════════════════════════════════════════════════════
REM PASO 5: Crear archivo de configuración
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 5/5: Creando configuración
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Obtener ID del túnel
echo Obteniendo información del túnel...
for /f "tokens=1" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if not defined TUNNEL_ID (
    echo ❌ ERROR: No se pudo obtener el ID del túnel
    echo.
    echo Ejecuta: cloudflared.exe tunnel list
    echo Y verifica que "dvta-tunnel" existe
    echo.
    pause
    exit /b 1
)

echo ✅ ID del túnel: %TUNNEL_ID%
echo.

REM Buscar archivo de credenciales
echo Buscando archivo de credenciales...
set CRED_FILE=
for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i

if not defined CRED_FILE (
    echo ❌ ERROR: No se encontró el archivo de credenciales
    echo.
    echo Busca manualmente en: %USERPROFILE%\.cloudflared\
    echo.
    pause
    exit /b 1
)

echo ✅ Credenciales encontradas
echo.

REM Crear archivo de configuración
echo Creando cloudflare-dvta-config.yml...
(
echo tunnel: %TUNNEL_ID%
echo credentials-file: %CRED_FILE%
echo.
echo ingress:
echo   - hostname: dvta.ch
echo     service: http://127.0.0.1:8000
echo   - hostname: www.dvta.ch
echo     service: http://127.0.0.1:8000
echo   - service: http_status:404
) > cloudflare-dvta-config.yml

echo ✅ Configuración creada
echo.
timeout /t 2 /nobreak >nul

REM ═══════════════════════════════════════════════════════════════════════════
REM RESUMEN FINAL
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Túnel ID: %TUNNEL_ID%
echo.
echo Dominios configurados:
echo   ✅ https://dvta.ch
echo   ✅ https://www.dvta.ch
echo.
echo Archivo de configuración: cloudflare-dvta-config.yml
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PRÓXIMOS PASOS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 1. Los cambios DNS pueden tardar 5-10 minutos en propagarse
echo.
echo 2. Inicia el sistema con:
echo    INICIAR_DVDBANK_DVTA.bat
echo.
echo 3. El navegador se abrirá automáticamente en https://dvta.ch
echo.
echo 4. Para inicio automático con Windows:
echo    CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Quieres iniciar el sistema ahora? (S/N)
set /p INICIAR=
if /i "%INICIAR%"=="S" (
    echo.
    echo Iniciando sistema...
    call INICIAR_DVDBANK_DVTA.bat
) else (
    echo.
    echo Puedes iniciar el sistema cuando quieras con:
    echo INICIAR_DVDBANK_DVTA.bat
    echo.
    pause
)
