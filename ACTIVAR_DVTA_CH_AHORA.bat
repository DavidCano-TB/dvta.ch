@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ACTIVAR dvta.ch - PROCESO GUIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este asistente te guiará paso a paso para activar dvta.ch
echo.
echo Tiempo estimado: 5 minutos
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

REM Abrir dashboard
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 1: ABRIR CLOUDFLARE DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Se abrirá el dashboard de Cloudflare en tu navegador.
echo.
echo SIGUE ESTOS PASOS EN EL NAVEGADOR:
echo.
echo 1. Inicia sesión en Cloudflare
echo 2. Selecciona tu cuenta
echo 3. En el menú lateral, busca "Zero Trust" o "Access"
echo 4. Ve a: Networks → Tunnels
echo 5. Haz clic en "Create a tunnel"
echo 6. Selecciona "Cloudflared"
echo 7. Nombre del túnel: dvta-tunnel
echo 8. Haz clic en "Save tunnel"
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

echo Abriendo dashboard...
start https://one.dash.cloudflare.com/

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 2: COPIAR TOKEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo En la siguiente pantalla del dashboard verás un comando como:
echo.
echo   cloudflared.exe service install eyJhbGc...
echo.
echo COPIA TODO el token (la parte larga después de "install ")
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Ya tienes el token copiado? (S/N)
set /p LISTO=

if /i not "%LISTO%"=="S" (
    echo.
    echo Vuelve cuando tengas el token copiado.
    pause
    exit /b
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 3: PEGAR TOKEN
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Pega el token aquí y presiona Enter:
echo.
set /p TOKEN=

if not defined TOKEN (
    echo.
    echo ❌ No se proporcionó ningún token
    pause
    exit /b 1
)

echo.
echo Instalando túnel...
cloudflared.exe service install %TOKEN%

if errorlevel 1 (
    echo.
    echo ❌ Error al instalar el túnel
    echo.
    echo Verifica que el token sea correcto.
    pause
    exit /b 1
)

echo ✅ Túnel instalado

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  PASO 4: CONFIGURAR RUTAS PÚBLICAS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Vuelve al dashboard de Cloudflare y configura las rutas públicas:
echo.
echo 1. En la página del túnel, ve a la pestaña "Public Hostname"
echo 2. Haz clic en "Add a public hostname"
echo 3. Configura la primera ruta:
echo    - Subdomain: (dejar vacío)
echo    - Domain: dvta.ch
echo    - Service Type: HTTP
echo    - URL: localhost:8000
echo 4. Haz clic en "Save hostname"
echo.
echo 5. Haz clic en "Add a public hostname" de nuevo
echo 6. Configura la segunda ruta:
echo    - Subdomain: www
echo    - Domain: dvta.ch
echo    - Service Type: HTTP
echo    - URL: localhost:8000
echo 7. Haz clic en "Save hostname"
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Has completado la configuración de rutas? (S/N)
set /p RUTAS=

if /i not "%RUTAS%"=="S" (
    echo.
    echo Completa la configuración y vuelve a ejecutar este script.
    pause
    exit /b
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo dvta.ch está ahora configurado y activo.
echo.
echo El túnel se iniciará automáticamente como servicio de Windows.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  INICIANDO SISTEMA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Deteniendo procesos actuales...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo.
echo Iniciando servidor Python...
start "DVDBank Server" /MIN cmd /c "python main.py > logs\server.log 2>&1"
timeout /t 8 /nobreak >nul

echo.
echo Abriendo navegador en https://dvta.ch...
timeout /t 5 /nobreak >nul
start https://dvta.ch

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  ✅ SISTEMA INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Accede a: https://dvta.ch
echo.
echo NOTA: Los cambios DNS pueden tardar 5-10 minutos en propagarse.
echo       Si no funciona inmediatamente, espera unos minutos.
echo.
echo ═══════════════════════════════════════════════════════════════════════════
pause
