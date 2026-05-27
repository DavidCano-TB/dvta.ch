@echo off
chcp 65001 >nul
title Desinstalar Servicios Windows - DVDcoin
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🗑️  DESINSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script eliminará todos los servicios Windows de DVDcoin
echo.
echo ⚠️  IMPORTANTE: Se requieren privilegios de administrador
echo.
pause

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0services\uninstall_services.ps1"

pause
