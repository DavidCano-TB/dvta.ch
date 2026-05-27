@echo off
chcp 65001 >nul
title Eliminar Auto-Arranque dvta.ch
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🗑️  ELIMINAR AUTO-ARRANQUE DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script eliminará la tarea programada de auto-arranque de dvta.ch
echo.
echo IMPORTANTE:
echo   • Requiere permisos de administrador
echo   • Después de esto, dvta.ch NO se iniciará automáticamente
echo   • Deberás ejecutar ACTIVAR_DVTA_CH_AHORA.bat manualmente
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo SOLUCIÓN:
    echo   1. Cierra esta ventana
    echo   2. Haz clic derecho en ELIMINAR_AUTOARRANQUE_DVTA.bat
    echo   3. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

REM Verificar si la tarea existe
schtasks /Query /TN "DVDcoin_DVTA_AutoStart" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  La tarea "DVDcoin_DVTA_AutoStart" no existe
    echo.
    echo No hay nada que eliminar.
    echo.
    pause
    exit /b 0
)

REM Eliminar la tarea
echo Eliminando tarea programada...
schtasks /Delete /TN "DVDcoin_DVTA_AutoStart" /F

if %errorlevel% equ 0 (
    echo ✅ Tarea programada eliminada exitosamente
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ AUTO-ARRANQUE DESACTIVADO
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo 📋 RESULTADO:
    echo   • La tarea "DVDcoin_DVTA_AutoStart" ha sido eliminada
    echo   • dvta.ch NO se iniciará automáticamente al arrancar Windows
    echo.
    echo 🔄 PARA INICIAR MANUALMENTE:
    echo   • Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
    echo.
    echo 🔄 PARA REACTIVAR AUTO-ARRANQUE:
    echo   • Ejecuta: CREAR_AUTOARRANQUE_DVTA.bat
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
) else (
    echo ❌ ERROR: No se pudo eliminar la tarea programada
    echo.
    echo SOLUCIÓN MANUAL:
    echo   1. Abre "Programador de tareas" (taskschd.msc)
    echo   2. Busca "DVDcoin_DVTA_AutoStart"
    echo   3. Haz clic derecho → Eliminar
    echo.
)

pause
