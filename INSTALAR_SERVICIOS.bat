@echo off
chcp 65001 >nul
title Instalar Servicios Windows - DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📦 INSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script instalará servicios Windows para:
echo   • DVDcoin Bank (Puerto 8000)
echo   • DVDcoin Exams (Puerto 8001)
echo   • Cloudflare Tunnel (dvta.ch)
echo.
echo Los servicios se iniciarán automáticamente con Windows
echo.
echo ⚠️  IMPORTANTE: Se requieren privilegios de administrador
echo.
pause

cd /d "%~dp0"

echo.
echo Ejecutando instalador...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0services\install_services.ps1"

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ INSTALACIÓN COMPLETADA
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Los servicios están instalados y corriendo
    echo.
    echo Para gestionar los servicios:
    echo   • Ejecuta: GESTIONAR_SERVICIOS.bat
    echo   • O usa: services.msc (Administrador de servicios de Windows)
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ❌ ERROR EN LA INSTALACIÓN
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Verifica que:
    echo   1. Ejecutaste como Administrador
    echo   2. Python está instalado
    echo   3. No hay otros servicios usando los puertos 8000 y 8001
    echo.
)

pause
