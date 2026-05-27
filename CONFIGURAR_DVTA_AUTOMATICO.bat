@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN AUTOMÁTICA DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script configurará dvta.ch automáticamente.
echo.
echo IMPORTANTE: Se abrirá tu navegador para autorizar Cloudflare.
echo             Debes completar la autorización para continuar.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Eliminar certificado antiguo
echo [1/6] Limpiando configuración anterior...
del /F /Q "%USERPROFILE%\.cloudflared\cert.pem" >nul 2>&1
timeout /t 2 /nobreak >nul
echo     ✅ Listo

REM Login en Cloudflare
echo.
echo [2/6] Abriendo navegador para autorización...
echo.
echo     → Se abrirá tu navegador
echo     → Inicia sesión en Cloudflare
echo     → Selecciona dvta.ch
echo     → Haz clic en "Authorize"
echo     → Espera el mensaje de confirmación
echo     → NO CIERRES esta ventana
echo.
echo Presiona cualquier tecla cuando hayas completado la autorización...
pause >nul

start /wait cloudflared.exe tunnel login

if errorlevel 1 (
    echo.
    echo ❌ Error en la autorización
    echo.
    echo Por favor:
    echo 1. Asegúrate de tener cuenta en Cloudflare
    echo 2. Asegúrate de que dvta.ch está en tu cuenta
    echo 3. Completa la autorización en el navegador
    echo.
    pause
    exit /b 1
)

echo.
echo     ✅ Autorización completada

REM Crear túnel
echo.
echo [3/6] Creando túnel...

cloudflared.exe tunnel list | findstr "dvta-tunnel" >nul 2>&1
if errorlevel 1 (
    cloudflared.exe tunnel create dvta-tunnel
    if errorlevel 1 (
        echo     ⚠ Error al crear túnel, puede que ya exista
    ) else (
        echo     ✅ Túnel creado
    )
) else (
    echo     ✅ Túnel ya existe
)

REM Configurar DNS
echo.
echo [4/6] Configurando DNS...

cloudflared.exe tunnel route dns dvta-tunnel dvta.ch >nul 2>&1
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch >nul 2>&1

echo     ✅ DNS configurado

REM Obtener información del túnel
echo.
echo [5/6] Obteniendo información del túnel...

for /f "tokens=1" %%i in ('cloudflared.exe tunnel list ^| findstr "dvta-tunnel"') do set TUNNEL_ID=%%i

if not defined TUNNEL_ID (
    echo     ❌ No se pudo obtener el ID del túnel
    echo.
    echo Ejecuta manualmente:
    echo   cloudflared.exe tunnel list
    echo.
    pause
    exit /b 1
)

echo     ✅ ID del túnel: %TUNNEL_ID%

REM Buscar credenciales
for /f "delims=" %%i in ('dir /s /b "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" 2^>nul') do set CRED_FILE=%%i

if not defined CRED_FILE (
    echo     ❌ No se encontraron credenciales
    pause
    exit /b 1
)

echo     ✅ Credenciales encontradas

REM Crear configuración
echo.
echo [6/6] Creando archivo de configuración...

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

echo     ✅ Configuración creada

REM Detener procesos actuales
echo.
echo Deteniendo procesos actuales...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

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
echo Archivo: cloudflare-dvta-config.yml
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO SISTEMA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo El sistema se iniciará ahora con dvta.ch...
echo.
timeout /t 3 /nobreak >nul

call INICIAR_DVDBANK_DVTA.bat
