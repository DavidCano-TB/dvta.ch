@echo off
chcp 65001 >nul
title Actualizar Cloudflared
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔄 ACTUALIZAR CLOUDFLARED
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo Este script descargará la última versión de cloudflared.
echo.

if exist "cloudflared.exe" (
    echo Versión actual:
    cloudflared.exe --version
    echo.
)

set /p CONFIRMAR="¿Deseas continuar? (S/N): "
if /i not "%CONFIRMAR%"=="S" (
    echo.
    echo ❌ Actualización cancelada
    echo.
    pause
    exit /b 0
)

echo.
echo [1/4] Deteniendo Cloudflare Tunnel...
taskkill /F /IM cloudflared.exe 2>nul
if %errorLevel% equ 0 (
    echo    ✅ Cloudflare detenido
) else (
    echo    ℹ️  Cloudflare no estaba corriendo
)
timeout /t 2 /nobreak >nul

echo.
echo [2/4] Creando backup de la versión actual...
if exist "cloudflared.exe" (
    copy "cloudflared.exe" "cloudflared.exe.backup" >nul 2>&1
    echo    ✅ Backup creado: cloudflared.exe.backup
) else (
    echo    ℹ️  No hay versión actual para respaldar
)

echo.
echo [3/4] Descargando última versión...
echo.
echo    Abriendo página de descargas en tu navegador...
echo    URL: https://github.com/cloudflare/cloudflared/releases/latest
echo.
start https://github.com/cloudflare/cloudflared/releases/latest
echo.
echo    Por favor:
echo      1. Descarga: cloudflared-windows-amd64.exe
echo      2. Guárdalo como: c:\dvdcoin\cloudflared.exe
echo      3. Presiona cualquier tecla cuando hayas terminado
echo.
pause

echo.
echo [4/4] Verificando nueva versión...
if exist "cloudflared.exe" (
    echo.
    echo    Nueva versión instalada:
    cloudflared.exe --version
    echo.
    echo    ✅ Actualización completada
) else (
    echo.
    echo    ❌ No se encontró cloudflared.exe
    echo.
    echo    Si creaste el backup, puedes restaurarlo:
    echo       copy cloudflared.exe.backup cloudflared.exe
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ PROCESO COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Para iniciar el sistema con la nueva versión:
echo    INICIAR_SISTEMA_DVTA.bat
echo.
pause
