@echo off
chcp 65001 >nul
title Configurar Cloudflare Tunnel para dvta.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 CONFIGURACIÓN DE CLOUDFLARE TUNNEL PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo REQUISITOS PREVIOS:
echo   ✅ Dominio dvta.ch debe estar ACTIVO en Cloudflare (no "pending")
echo   ✅ cloudflared.exe debe estar instalado en c:\dvdcoin\
echo   ✅ Debes haber ejecutado: cloudflared tunnel login
echo.
set /p CONFIRMAR="¿Has completado los requisitos previos? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo.
    echo ❌ Completa los requisitos previos primero.
    echo.
    echo Ver instrucciones completas en:
    echo    PASOS_CONFIGURACION_CLOUDFLARE_DVTA_CH.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Verificando cloudflared.exe
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if not exist "cloudflared.exe" (
    echo ❌ cloudflared.exe no encontrado
    echo.
    echo Descarga desde:
    echo    https://github.com/cloudflare/cloudflared/releases/latest
    echo.
    echo Busca: cloudflared-windows-amd64.exe
    echo Guarda como: c:\dvdcoin\cloudflared.exe
    echo.
    pause
    exit /b 1
)

cloudflared.exe --version
echo    ✅ cloudflared.exe encontrado
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Creando tunnel "dvta-tunnel"
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared.exe tunnel create dvta-tunnel

if %errorLevel% neq 0 (
    echo.
    echo ⚠️  Error al crear el tunnel.
    echo.
    echo Posibles causas:
    echo   • El tunnel ya existe (no es un error)
    echo   • No has ejecutado: cloudflared tunnel login
    echo   • El dominio no está activo en Cloudflare
    echo.
    set /p CONTINUAR="¿Deseas continuar de todos modos? (S/N): "
    if /i not "%CONTINUAR%"=="S" (
        pause
        exit /b 1
    )
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Listando tunnels disponibles
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared.exe tunnel list
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4: Configurando rutas DNS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Configurando ruta para dvta.ch...
cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
echo.

echo Configurando ruta para www.dvta.ch...
cloudflared.exe tunnel route dns dvta-tunnel www.dvta.ch
echo.

if %errorLevel% equ 0 (
    echo    ✅ Rutas DNS configuradas
) else (
    echo    ⚠️  Error al configurar rutas DNS
    echo.
    echo Verifica que el dominio esté activo en Cloudflare.
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 5: Obteniendo información del tunnel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cloudflared.exe tunnel info dvta-tunnel > tunnel_info.txt 2>&1
type tunnel_info.txt
echo.

echo ⚠️  IMPORTANTE: Copia el TUNNEL ID de arriba
echo.
set /p TUNNEL_ID="Pega el TUNNEL ID aquí: "

if "%TUNNEL_ID%"=="" (
    echo.
    echo ❌ No se proporcionó el TUNNEL ID
    echo.
    echo Puedes configurarlo manualmente editando:
    echo    cloudflare-dvta-config.yml
    echo.
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 6: Actualizando archivo de configuración
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Obtener el usuario actual
for /f "tokens=*" %%a in ('echo %USERPROFILE%') do set USER_PROFILE=%%a

REM Actualizar el archivo de configuración
powershell -Command "(Get-Content cloudflare-dvta-config.yml) -replace 'tunnel: TUNNEL_ID_AQUI', 'tunnel: %TUNNEL_ID%' | Set-Content cloudflare-dvta-config.yml"
powershell -Command "(Get-Content cloudflare-dvta-config.yml) -replace 'TUNNEL_ID_AQUI', '%TUNNEL_ID%' | Set-Content cloudflare-dvta-config.yml"
powershell -Command "(Get-Content cloudflare-dvta-config.yml) -replace 'C:\\Users\\PC', '%USER_PROFILE%' | Set-Content cloudflare-dvta-config.yml"

echo    ✅ Archivo cloudflare-dvta-config.yml actualizado
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 7: Probando el tunnel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Iniciando tunnel en modo prueba (presiona Ctrl+C para detener)...
echo.
timeout /t 3 /nobreak >nul

cloudflared.exe tunnel --config cloudflare-dvta-config.yml run dvta-tunnel

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo El tunnel está configurado y listo para usar.
echo.
echo Próximos pasos:
echo   1. Verifica que https://dvta.ch funcione
echo   2. Verifica que https://www.dvta.ch funcione
echo   3. Ejecuta: INICIAR_SISTEMA_DVTA.bat (usará el tunnel configurado)
echo   4. Ejecuta: INSTALAR_INICIO_AUTOMATICO.bat (inicio automático)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
