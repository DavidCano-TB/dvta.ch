@echo off
chcp 65001 >nul
cls
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA
echo ═══════════════════════════════════════════════════════════
echo.
echo Verificando que el sistema funcione correctamente...
echo.

echo [1/4] Verificando servidor Python...
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Servidor Python: CORRIENDO
) else (
    echo   ⚠️  Servidor Python: NO ACTIVO
    echo       Para iniciar: INICIAR_SISTEMA_DVTA.bat
)

echo.
echo [2/4] Verificando túnel Cloudflare...
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Túnel Cloudflare: CORRIENDO
) else (
    echo   ⚠️  Túnel Cloudflare: NO ACTIVO
    echo       Para iniciar: INICIAR_TUNNEL_DVTA.bat
)

echo.
echo [3/4] Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✅ Puerto 8000: ESCUCHANDO
) else (
    echo   ⚠️  Puerto 8000: NO DISPONIBLE
)

echo.
echo [4/4] Verificando archivos principales...
if exist "main.py" (
    echo   ✅ main.py: Encontrado
) else (
    echo   ❌ main.py: NO ENCONTRADO
)

if exist "cloudflared.exe" (
    echo   ✅ cloudflared.exe: Encontrado
) else (
    echo   ⚠️  cloudflared.exe: NO ENCONTRADO
)

if exist "cloudflare-dvta-config.yml" (
    echo   ✅ cloudflare-dvta-config.yml: Encontrado
) else (
    echo   ⚠️  cloudflare-dvta-config.yml: NO ENCONTRADO
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════
echo.

REM Contar servicios activos
set ACTIVOS=0
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 set /a ACTIVOS+=1

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 set /a ACTIVOS+=1

if %ACTIVOS% equ 2 (
    echo   Estado: ✅ SISTEMA COMPLETAMENTE OPERATIVO
    echo.
    echo   Acceso:
    echo     • Local: http://localhost:8000
    echo     • Público: https://dvta.ch
    echo     • Público: https://www.dvta.ch
) else if %ACTIVOS% equ 1 (
    echo   Estado: ⚠️  SISTEMA PARCIALMENTE ACTIVO
    echo.
    echo   Acción: Ejecuta INICIAR_SISTEMA_DVTA.bat
) else (
    echo   Estado: ⚠️  SISTEMA DETENIDO
    echo.
    echo   Acción: Ejecuta INICIAR_SISTEMA_DVTA.bat
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 SCRIPTS DISPONIBLES
echo ═══════════════════════════════════════════════════════════
echo.
echo   • MENU_PRINCIPAL.bat - Menú principal
echo   • INICIAR_SISTEMA_DVTA.bat - Iniciar todo
echo   • INICIAR_TUNNEL_DVTA.bat - Solo túnel
echo   • CONFIGURAR_TODO_DVTA.bat - Configuración
echo   • MOSTRAR_RESUMEN.bat - Ver resumen de correcciones
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
