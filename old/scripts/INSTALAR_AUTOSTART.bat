@echo off
:: Instala DVDcoin Bank como tarea de inicio automatico en Windows
:: EJECUTAR COMO ADMINISTRADOR
:: AHORA USA CLOUDFLARE TUNNEL EN LUGAR DE NGROK

title DVDcoin — Instalar Autostart (Cloudflare Tunnel)
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Ejecuta este archivo como Administrador.
    echo  Clic derecho ^> "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN - INSTALAR INICIO AUTOMATICO                 ║
echo ║              (Con Cloudflare Tunnel)                         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Eliminando tareas antiguas...
schtasks /delete /tn "DVDcoin-Autostart" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
schtasks /delete /tn "DVDcoin" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Cloudflare" /f >nul 2>&1
echo       ✓ Tareas antiguas eliminadas

echo.
echo [2/4] Verificando Cloudflare Tunnel...

cloudflared version >nul 2>&1
if errorlevel 1 (
    echo       ✗ cloudflared NO instalado
    echo.
    echo       Antes de continuar, debes:
    echo       1. Instalar cloudflared
    echo       2. Ejecutar: CONFIGURAR_CLOUDFLARE.bat
    echo.
    echo       Consulta: README_CLOUDFLARE.md
    echo.
    pause
    exit /b 1
)

if not exist "cloudflare-config.yml" (
    echo       ✗ cloudflare-config.yml NO encontrado
    echo.
    echo       Ejecuta primero: CONFIGURAR_CLOUDFLARE.bat
    echo.
    pause
    exit /b 1
)

echo       ✓ Cloudflare Tunnel configurado

echo.
echo [3/4] Creando tarea de inicio automatico...

:: Crear tarea que ejecuta INICIAR_CON_CLOUDFLARE.bat
schtasks /create /tn "DVDcoin-Cloudflare" /f ^
  /tr "\"%~dp0INICIAR_CON_CLOUDFLARE.bat\"" ^
  /sc ONLOGON ^
  /delay 0000:30 ^
  /rl HIGHEST

if %errorlevel% equ 0 (
    echo       ✓ Tarea creada correctamente
) else (
    echo       ✗ Error creando tarea. Revisa permisos.
    pause
    exit /b 1
)

echo.
echo [4/4] Verificando...
schtasks /query /tn "DVDcoin-Cloudflare" /fo LIST 2>&1 | findstr /i "nom\|estado\|prox\|nom de"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✓ AUTOSTART INSTALADO CORRECTAMENTE             ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ CONFIGURACION                                                │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   Tarea:       DVDcoin-Cloudflare
echo   Script:      INICIAR_CON_CLOUDFLARE.bat
echo   Inicio:      30 segundos después del login
echo   Sistema:     Cloudflare Tunnel (sin límites)
echo.
echo ┌──────────────────────────────────────────────────────────────┐
echo │ VENTAJAS                                                      │
echo └──────────────────────────────────────────────────────────────┘
echo.
echo   ✓ Sin límites de conexiones
echo   ✓ URL fija que no cambia
echo   ✓ Inicio automático al encender Windows
echo   ✓ Gratis para siempre
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo Para desinstalar el autostart:
echo   DESINSTALAR_AUTOSTART.bat
echo.
pause
