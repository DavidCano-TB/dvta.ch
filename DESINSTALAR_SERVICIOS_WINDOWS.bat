@echo off
chcp 65001 >nul
title Desinstalar Servicios Windows - DVDcoin
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🗑️  DESINSTALAR SERVICIOS WINDOWS - DVDcoin Platform
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   ⚠️  REQUIERE EJECUTAR COMO ADMINISTRADOR
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Requiere privilegios de Administrador.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo Deteniendo y eliminando servicios...
echo.

for %%S in (DVDcoin-Bank DVDcoin-Exams DVDcoin-BankProxy DVDcoin-Tunnel) do (
    sc query %%S >nul 2>&1
    if !errorlevel! equ 0 (
        echo   → Deteniendo %%S...
        net stop %%S >nul 2>&1
        sc delete %%S >nul 2>&1
        echo     ✅ %%S eliminado
    ) else (
        echo     — %%S no existía
    )
)

echo.
echo ✅ Todos los servicios DVDcoin eliminados.
echo    Los servidores ya no se iniciarán con Windows.
echo    Usa DEPLOY.bat para arrancar manualmente.
echo.
pause
