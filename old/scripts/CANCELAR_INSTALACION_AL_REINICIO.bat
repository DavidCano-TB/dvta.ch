@echo off
REM ============================================================
REM CANCELAR INSTALACION AUTOMATICA AL REINICIAR
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
title DVDCoin - Cancelar Instalación al Reinicio
cd /d "%~dp0"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         CANCELAR INSTALACION AL REINICIAR WINDOWS            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Eliminando tarea de instalación automática...
echo.

schtasks /delete /tn "DVDcoin-Instalador" /f >nul 2>&1
if errorlevel 1 (
    echo   ○ No había tarea de instalación configurada
) else (
    echo   ✓ Tarea de instalación eliminada
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo ✓ Instalación automática cancelada
echo.
echo La instalación ya NO se ejecutará al reiniciar Windows.
echo.
echo Para configurarla nuevamente:
echo   CONFIGURAR_INSTALACION_AL_REINICIO.bat
echo.
pause
