@echo off
chcp 65001 >nul
title 🌐 Configurar dvd.ch - DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 CONFIGURACIÓN COMPLETA DE DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará tu dominio dvd.ch para que funcione
echo con tu aplicación DVDcoin a través de Cloudflare Tunnel.
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar que cloudflared existe
if not exist "cloudflared.exe" (
    echo ❌ ERROR: cloudflared.exe no encontrado
    echo.
    echo Por favor, descarga cloudflared desde:
    echo https://github.com/cloudflare/cloudflared/releases
    echo.
    pause
    exit /b 1
)

echo ✅ cloudflared.exe encontrado
echo.

REM Verificar que el túnel existe
echo 📡 Verificando túnel existente...
cloudflared.exe tunnel list | findstr "dvdcoin" >nul
if errorlevel 1 (
    echo ❌ ERROR: Túnel 'dvdcoin' no encontrado
    echo.
    echo Ejecuta primero: INICIAR_CON_CLOUDFLARE.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Túnel 'dvdcoin' encontrado
echo.

echo ═══════════════════════════════════════════════════════════
echo   PASO 1: CONFIGURAR DNS PARA DVD.CH
echo ═══════════════════════════════════════════════════════════
echo.
echo Configurando el registro DNS para dvd.ch...
echo.

REM Configurar DNS para dvd.ch
cloudflared.exe tunnel route dns dvdcoin dvd.ch
if errorlevel 1 (
    echo.
    echo ⚠️  ADVERTENCIA: No se pudo configurar el DNS automáticamente
    echo.
    echo Esto puede ser porque:
    echo   1. El dominio aún no está en Cloudflare
    echo   2. Los nameservers no apuntan a Cloudflare
    echo   3. Ya está configurado
    echo.
    echo 📋 PASOS MANUALES NECESARIOS:
    echo.
    echo 1. Ve a https://dash.cloudflare.com
    echo 2. Añade el dominio dvd.ch si no lo has hecho
    echo 3. Cambia los nameservers en tu registrador
    echo 4. Espera 2-4 horas para propagación DNS
    echo 5. Ve a Traffic ^> Cloudflare Tunnel ^> dvdcoin ^> Configure
    echo 6. Añade Public Hostname:
    echo    - Subdomain: (vacío)
    echo    - Domain: dvd.ch
    echo    - Service: HTTP
    echo    - URL: localhost:8000
    echo.
) else (
    echo ✅ DNS configurado para dvd.ch
    echo.
)

echo ═══════════════════════════════════════════════════════════
echo   PASO 2: CONFIGURAR WWW.DVD.CH (OPCIONAL)
echo ═══════════════════════════════════════════════════════════
echo.
echo Configurando el registro DNS para www.dvd.ch...
echo.

cloudflared.exe tunnel route dns dvdcoin www.dvd.ch
if errorlevel 1 (
    echo ⚠️  No se pudo configurar www.dvd.ch (no crítico)
) else (
    echo ✅ DNS configurado para www.dvd.ch
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   PASO 3: VERIFICAR CONFIGURACIÓN
echo ═══════════════════════════════════════════════════════════
echo.

echo 📋 Información del túnel:
echo.
cloudflared.exe tunnel info dvdcoin
echo.

echo ═══════════════════════════════════════════════════════════
echo   PASO 4: REINICIAR TÚNEL CON NUEVA CONFIGURACIÓN
echo ═══════════════════════════════════════════════════════════
echo.

echo Deteniendo túnel actual (si está corriendo)...
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 2 /nobreak >nul
echo.

echo Iniciando túnel con configuración actualizada...
echo.
echo 🚀 El túnel se iniciará en una nueva ventana
echo.

start "Cloudflare Tunnel - dvd.ch" /MIN cloudflared.exe tunnel --config cloudflare-config.yml run dvdcoin

timeout /t 3 /nobreak >nul

echo ✅ Túnel iniciado
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo 1️⃣  VERIFICAR DNS (puede tardar 2-4 horas):
echo    nslookup dvd.ch
echo.
echo 2️⃣  VERIFICAR EN CLOUDFLARE DASHBOARD:
echo    https://dash.cloudflare.com
echo    ^> Selecciona dvd.ch
echo    ^> Traffic ^> Cloudflare Tunnel
echo    ^> Verifica que dvdcoin está conectado
echo.
echo 3️⃣  PROBAR EN NAVEGADOR:
echo    https://dvd.ch
echo.
echo 4️⃣  CONFIGURAR SSL (si es necesario):
echo    Cloudflare Dashboard ^> SSL/TLS ^> Modo "Full"
echo.
echo ═══════════════════════════════════════════════════════════
echo   📊 ESTADO ACTUAL
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ Archivo de configuración actualizado
echo ✅ DNS configurado (si el dominio está en Cloudflare)
echo ✅ Túnel reiniciado con nueva configuración
echo.
echo 🌐 URLs configuradas:
echo    - https://dvd.ch
echo    - https://www.dvd.ch
echo.
echo ⏱️  Tiempo de propagación DNS: 2-4 horas (máximo 24h)
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Verificando DNS actual...
echo.
nslookup dvd.ch
echo.
echo Si ves IPs de Cloudflare (104.x.x.x o 172.x.x.x), ¡está listo!
echo Si no, espera unas horas y vuelve a verificar.
echo.
echo ═══════════════════════════════════════════════════════════
echo   📚 DOCUMENTACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Para más información, consulta:
echo   - CONFIGURAR_DVD_CH.md (guía completa)
echo   - COMO_USAR_DVD_CH.txt (resumen rápido)
echo   - GUIA_RAPIDA_DVD_CH.txt (comandos útiles)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo Presiona cualquier tecla para salir...
pause >nul
