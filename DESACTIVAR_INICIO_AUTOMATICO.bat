@echo off
chcp 65001 >nul

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cls
echo ═══════════════════════════════════════════════════════════
echo   DESACTIVAR INICIO AUTOMÁTICO
echo ═══════════════════════════════════════════════════════════
echo.

schtasks /query /tn "DVDBank_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo Eliminando tarea programada...
    schtasks /delete /tn "DVDBank_AutoStart" /f
    echo.
    echo ✅ Inicio automático desactivado
) else (
    echo ⚠️  No hay tarea programada configurada
)

echo.
pause
