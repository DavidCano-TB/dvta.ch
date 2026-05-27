@echo off
chcp 65001 >nul
title DVDBank - Estado del Sistema
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📊 ESTADO DEL SISTEMA DVDBANK
═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [1/5] Verificando servidor Python...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Python: EJECUTÁNDOSE
    for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
        echo         PID: %%a
    )
) else (
    echo      ❌ Servidor Python: NO ACTIVO
    echo         Para iniciar: ARRANCAR.bat
)
echo.

echo [2/5] Verificando Cloudflare Tunnel...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel: EJECUTÁNDOSE
    for /f "tokens=2" %%a in ('tasklist ^| findstr "cloudflared.exe"') do (
        echo         PID: %%a
    )
) else (
    echo      ❌ Cloudflare Tunnel: NO ACTIVO
    echo         Para iniciar: INICIAR_TUNNEL_DVTA.bat
)
echo.

echo [3/5] Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Puerto 8000: EN USO (servidor escuchando)
) else (
    echo      ❌ Puerto 8000: LIBRE (servidor no escuchando)
)
echo.

echo [4/5] Verificando archivos de configuración...
if exist "cloudflare-tunnel-dvta.yml" (
    echo      ✅ cloudflare-tunnel-dvta.yml: EXISTE
) else (
    echo      ❌ cloudflare-tunnel-dvta.yml: NO ENCONTRADO
)

if exist "cloudflared.exe" (
    echo      ✅ cloudflared.exe: EXISTE
) else (
    echo      ❌ cloudflared.exe: NO ENCONTRADO
)

if exist "main.py" (
    echo      ✅ main.py: EXISTE
) else (
    echo      ❌ main.py: NO ENCONTRADO
)
echo.

echo [5/5] Verificando bases de datos...
if exist "users.db" (
    echo      ✅ users.db: EXISTE
) else (
    echo      ❌ users.db: NO ENCONTRADO
)

if exist "apuestas.db" (
    echo      ✅ apuestas.db: EXISTE
) else (
    echo      ❌ apuestas.db: NO ENCONTRADO
)

if exist "data\" (
    echo      ✅ Carpeta data\: EXISTE
) else (
    echo      ❌ Carpeta data\: NO ENCONTRADA
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   📍 URLs DE ACCESO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   • Local:    http://localhost:8000
echo   • Público:  https://dvta.ch
echo   • Público:  https://www.dvta.ch
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 ACCIONES DISPONIBLES
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   • Iniciar servidor:        ARRANCAR.bat
echo   • Iniciar túnel:           INICIAR_TUNNEL_DVTA.bat
echo   • Iniciar todo:            INICIAR_SISTEMA_DVTA.bat
echo   • Detener todo:            DETENER_SISTEMA.bat
echo   • Configurar email:        CONFIGURAR_EMAIL_CLOUDFLARE.bat
echo   • Ver este estado:         VER_ESTADO.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
