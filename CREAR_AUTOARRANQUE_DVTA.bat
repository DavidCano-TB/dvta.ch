@echo off
chcp 65001 >nul
title Crear Auto-Arranque dvta.ch
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ⚙️  CONFIGURAR AUTO-ARRANQUE DE dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script creará una tarea programada en Windows para que dvta.ch
echo se inicie automáticamente al arrancar el sistema.
echo.
echo IMPORTANTE:
echo   • Requiere permisos de administrador
echo   • La tarea se ejecutará al iniciar sesión
echo   • Los servicios se iniciarán en segundo plano
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause

cd /d "%~dp0"

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo SOLUCIÓN:
    echo   1. Cierra esta ventana
    echo   2. Haz clic derecho en CREAR_AUTOARRANQUE_DVTA.bat
    echo   3. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

REM Eliminar tarea anterior si existe
schtasks /Query /TN "DVDcoin_DVTA_AutoStart" >nul 2>&1
if %errorlevel% equ 0 (
    echo Eliminando tarea anterior...
    schtasks /Delete /TN "DVDcoin_DVTA_AutoStart" /F >nul 2>&1
    echo ✅ Tarea anterior eliminada
    echo.
)

REM Crear la tarea programada
echo Creando tarea programada...
echo.

schtasks /Create ^
    /TN "DVDcoin_DVTA_AutoStart" ^
    /TR "\"%~dp0ACTIVAR_DVTA_CH_AHORA.bat\"" ^
    /SC ONLOGON ^
    /RL HIGHEST ^
    /F

if %errorlevel% equ 0 (
    echo ✅ Tarea programada creada exitosamente
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ AUTO-ARRANQUE CONFIGURADO
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo 📋 DETALLES DE LA TAREA:
    echo   • Nombre: DVDcoin_DVTA_AutoStart
    echo   • Trigger: Al iniciar sesión
    echo   • Script: ACTIVAR_DVTA_CH_AHORA.bat
    echo   • Permisos: Máximos
    echo.
    echo 🔄 PRÓXIMOS PASOS:
    echo   • Al reiniciar Windows, dvta.ch se iniciará automáticamente
    echo   • Verás dos ventanas minimizadas: "DVDExams Server" y "Cloudflare Tunnel"
    echo   • Espera 30-60 segundos después del inicio para acceder a dvta.ch
    echo.
    echo 🛑 PARA DESACTIVAR:
    echo   • Ejecuta: ELIMINAR_AUTOARRANQUE_DVTA.bat
    echo   • O manualmente: Panel de Control → Tareas Programadas
    echo.
    echo 🧪 PARA PROBAR AHORA:
    echo   • Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
    echo   • O reinicia Windows
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
) else (
    echo ❌ ERROR: No se pudo crear la tarea programada
    echo.
    echo POSIBLES CAUSAS:
    echo   • Permisos insuficientes
    echo   • Ruta del script incorrecta
    echo   • Servicio de Programador de Tareas deshabilitado
    echo.
    echo SOLUCIÓN MANUAL:
    echo   1. Abre "Programador de tareas" (taskschd.msc)
    echo   2. Crea una tarea básica
    echo   3. Trigger: Al iniciar sesión
    echo   4. Acción: Iniciar programa
    echo   5. Programa: %~dp0ACTIVAR_DVTA_CH_AHORA.bat
    echo.
)

pause
