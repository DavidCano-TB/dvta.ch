@echo off
REM ============================================================
REM DVDCOIN - INSTALACION AUTOMATICA DE CLOUDFLARE TUNNEL
REM Se ejecuta automáticamente al reiniciar Windows
REM ============================================================

REM Verificar si ya somos admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    REM Auto-elevar sin preguntar
    powershell -Command "Start-Process '%~f0' -Verb RunAs" >nul 2>&1
    exit /b
)

:admin
chcp 65001 >nul
title DVDCoin - Instalación Automática Cloudflare Tunnel
cd /d "%~dp0"

REM Verificar si ya se completó la instalación
if exist "%~dp0.cloudflare_instalado" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                                                              ║
    echo ║         ✓ CLOUDFLARE TUNNEL YA ESTÁ INSTALADO               ║
    echo ║                                                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo La instalación ya se completó anteriormente.
    echo.
    echo ¿Quieres reinstalar? (S/N)
    set /p REINSTALL="> "
    if /i not "%REINSTALL%"=="S" (
        echo.
        echo Para iniciar el servidor: ARRANCAR.bat
        echo.
        timeout /t 5
        exit /b 0
    )
    del "%~dp0.cloudflare_instalado" >nul 2>&1
)

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN - INSTALACION AUTOMATICA                     ║
echo ║              CLOUDFLARE TUNNEL                               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Este asistente instalará y configurará Cloudflare Tunnel
echo para que DVDcoin funcione sin límites de conexiones.
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul

REM ============================================================
REM PASO 1: VERIFICAR PYTHON
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 1/7: Verificando Python                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python NO está instalado
    echo.
    echo Por favor, instala Python desde:
    echo https://www.python.org/downloads/
    echo.
    echo Después de instalar Python, ejecuta este script nuevamente.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
    echo ✓ %%i instalado
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 2: INSTALAR CLOUDFLARED
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 2/7: Instalando cloudflared                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cloudflared version >nul 2>&1
if errorlevel 1 (
    echo cloudflared no está instalado. Instalando...
    echo.
    
    REM Intentar instalar con winget
    winget --version >nul 2>&1
    if not errorlevel 1 (
        echo Instalando con winget...
        winget install --id Cloudflare.cloudflared --silent --accept-package-agreements --accept-source-agreements
        
        if errorlevel 1 (
            echo.
            echo ✗ Error al instalar con winget
            echo.
            echo Por favor, descarga cloudflared manualmente desde:
            echo https://github.com/cloudflare/cloudflared/releases/latest
            echo.
            echo Descarga: cloudflared-windows-amd64.exe
            echo Renombra a: cloudflared.exe
            echo Coloca en: c:\dvdcoin\cloudflared.exe
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo winget no está disponible.
        echo.
        echo Por favor, descarga cloudflared manualmente desde:
        echo https://github.com/cloudflare/cloudflared/releases/latest
        echo.
        echo Descarga: cloudflared-windows-amd64.exe
        echo Renombra a: cloudflared.exe
        echo Coloca en: c:\dvdcoin\cloudflared.exe
        echo.
        echo Después de descargar, presiona cualquier tecla...
        pause >nul
    )
)

REM Verificar instalación
cloudflared version >nul 2>&1
if errorlevel 1 (
    echo ✗ cloudflared no se pudo instalar
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('cloudflared version 2^>^&1') do (
    echo ✓ %%i instalado
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 3: AUTENTICAR CON CLOUDFLARE
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 3/7: Autenticar con Cloudflare                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ✓ Ya estás autenticado con Cloudflare
    echo.
    echo ¿Quieres volver a autenticar? (S/N)
    set /p REAUTH="> "
    if /i not "%REAUTH%"=="S" goto :skip_auth
)

echo Se abrirá tu navegador para autenticar con Cloudflare.
echo.
echo INSTRUCCIONES:
echo   1. Se abrirá tu navegador
echo   2. Inicia sesión en Cloudflare (o crea una cuenta gratis)
echo   3. Autoriza el acceso
echo   4. Vuelve a esta ventana
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

cloudflared tunnel login

if errorlevel 1 (
    echo.
    echo ✗ Error al autenticar
    echo.
    pause
    exit /b 1
)

:skip_auth
echo.
echo ✓ Autenticación exitosa
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 4: CREAR TUNEL
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 4/7: Crear túnel                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar si ya existe el túnel
cloudflared tunnel list 2>nul | findstr "dvdcoin" >nul 2>&1
if not errorlevel 1 (
    echo ✓ El túnel 'dvdcoin' ya existe
    echo.
    for /f "tokens=1" %%i in ('cloudflared tunnel list ^| findstr "dvdcoin" ^| findstr /v "NAME"') do (
        set TUNNEL_ID=%%i
    )
) else (
    echo Creando túnel 'dvdcoin'...
    echo.
    
    cloudflared tunnel create dvdcoin
    
    if errorlevel 1 (
        echo.
        echo ✗ Error al crear el túnel
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo ✓ Túnel creado exitosamente
    echo.
    
    REM Obtener el TUNNEL-ID
    for /f "tokens=1" %%i in ('cloudflared tunnel list ^| findstr "dvdcoin" ^| findstr /v "NAME"') do (
        set TUNNEL_ID=%%i
    )
)

echo TUNNEL-ID: %TUNNEL_ID%
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 5: CONFIGURAR DOMINIO
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 5/7: Configurar dominio                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo ¿Tienes un dominio propio? (S/N)
set /p HAS_DOMAIN="> "

if /i "%HAS_DOMAIN%"=="S" (
    echo.
    echo Ingresa tu dominio (ej: midominio.com):
    set /p DOMAIN="> "
    set HOSTNAME=dvdcoin.%DOMAIN%
    
    echo.
    echo ¿Tu dominio ya está en Cloudflare? (S/N)
    set /p DOMAIN_IN_CF="> "
    
    if /i "%DOMAIN_IN_CF%"=="S" (
        echo.
        echo Configurando DNS...
        cloudflared tunnel route dns dvdcoin %HOSTNAME%
        
        if errorlevel 1 (
            echo.
            echo ⚠ No se pudo configurar DNS automáticamente
            echo.
            echo Configura manualmente después con:
            echo   cloudflared tunnel route dns dvdcoin %HOSTNAME%
            echo.
        ) else (
            echo.
            echo ✓ DNS configurado exitosamente
            echo.
        )
    ) else (
        echo.
        echo INSTRUCCIONES:
        echo   1. Ve a: https://dash.cloudflare.com
        echo   2. Click en "Add a Site"
        echo   3. Ingresa tu dominio: %DOMAIN%
        echo   4. Sigue las instrucciones
        echo.
        echo Después ejecuta:
        echo   cloudflared tunnel route dns dvdcoin %HOSTNAME%
        echo.
    )
) else (
    echo.
    echo Se usará un subdominio de Cloudflare (.trycloudflare.com)
    set HOSTNAME=
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 6: CREAR ARCHIVO DE CONFIGURACION
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 6/7: Crear archivo de configuración                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Creando cloudflare-config.yml...

REM Crear backup si existe
if exist "cloudflare-config.yml" (
    copy /Y "cloudflare-config.yml" "cloudflare-config.yml.bak" >nul 2>&1
)

REM Crear nuevo archivo de configuración
(
echo # Configuracion de Cloudflare Tunnel para DVDcoin
echo tunnel: %TUNNEL_ID%
echo credentials-file: %USERPROFILE%\.cloudflared\%TUNNEL_ID%.json
echo.
echo ingress:
if not "%HOSTNAME%"=="" (
    echo   - hostname: %HOSTNAME%
)
echo     service: http://localhost:8000
echo     originRequest:
echo       noTLSVerify: false
echo       connectTimeout: 30s
echo       tlsTimeout: 10s
echo       tcpKeepAlive: 30s
echo       keepAliveConnections: 100
echo       keepAliveTimeout: 90s
echo       httpHostHeader: localhost:8000
echo   - service: http_status:404
echo.
echo metrics: localhost:2000
echo loglevel: info
echo protocol: auto
echo retries: 5
echo grace-period: 30s
) > cloudflare-config.yml

echo ✓ Archivo cloudflare-config.yml creado
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM PASO 7: INSTALAR AUTOSTART
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║ PASO 7/7: Instalar inicio automático                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo ¿Quieres que DVDcoin se inicie automáticamente al encender Windows? (S/N)
set /p INSTALL_AUTOSTART="> "

if /i "%INSTALL_AUTOSTART%"=="S" (
    echo.
    echo Instalando autostart...
    
    REM Eliminar tareas antiguas
    schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
    schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
    schtasks /delete /tn "DVDcoin" /f >nul 2>&1
    schtasks /delete /tn "DVDcoin-Cloudflare" /f >nul 2>&1
    
    REM Crear nueva tarea
    schtasks /create /tn "DVDcoin-Cloudflare" /f ^
      /tr "\"%~dp0INICIAR_CON_CLOUDFLARE.bat\"" ^
      /sc ONLOGON ^
      /delay 0000:30 ^
      /rl HIGHEST
    
    if errorlevel 1 (
        echo ✗ Error al crear tarea de autostart
    ) else (
        echo ✓ Autostart instalado correctamente
    )
) else (
    echo.
    echo Autostart no instalado.
    echo Puedes instalarlo más tarde con: INSTALAR_AUTOSTART.bat
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM ============================================================
REM MARCAR COMO INSTALADO
REM ============================================================
echo INSTALADO > "%~dp0.cloudflare_instalado"

REM ============================================================
REM RESUMEN FINAL
REM ============================================================
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ INSTALACION COMPLETADA                        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ RESUMEN                                                       │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   Túnel ID:     %TUNNEL_ID%
if not "%HOSTNAME%"=="" (
    echo   URL pública:  https://%HOSTNAME%
) else (
    echo   URL pública:  Se asignará automáticamente
)
echo   Config:       cloudflare-config.yml
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ PROXIMOS PASOS                                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   1. Iniciar el servidor:
echo      ARRANCAR.bat
echo.
echo   2. Acceder desde navegador:
if not "%HOSTNAME%"=="" (
    echo      https://%HOSTNAME%
) else (
    echo      Revisa cloudflare_tunnel.log para ver la URL
)
echo.
echo   3. Para detener:
echo      DETENER_SERVIDOR.bat
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ¿Quieres iniciar el servidor ahora? (S/N)
set /p START_NOW="> "

if /i "%START_NOW%"=="S" (
    echo.
    echo Iniciando servidor...
    timeout /t 2 /nobreak >nul
    start "" "%~dp0ARRANCAR.bat"
    timeout /t 3 /nobreak >nul
) else (
    echo.
    echo Para iniciar el servidor más tarde, ejecuta:
    echo   ARRANCAR.bat
    echo.
    timeout /t 10
)

exit /b 0
