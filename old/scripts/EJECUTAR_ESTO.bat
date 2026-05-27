@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 MIGRACIÓN A dvta.ch - INICIO RÁPIDO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este es el archivo principal para configurar tu dominio dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Qué quieres hacer?
echo.
echo   1. Configurar TODO automáticamente (RECOMENDADO)
echo   2. Ver instrucciones detalladas
echo   3. Verificar estado actual
echo   4. Salir
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p opcion="Elige una opción (1-4): "

if "%opcion%"=="1" goto configurar
if "%opcion%"=="2" goto instrucciones
if "%opcion%"=="3" goto verificar
if "%opcion%"=="4" goto salir

echo.
echo ❌ Opción inválida
pause
exit /b 1

:configurar
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN AUTOMÁTICA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Voy a configurar TODO automáticamente:
echo   ✅ Crear túnel de Cloudflare
echo   ✅ Configurar DNS
echo   ✅ Crear archivo de configuración
echo.
echo Cuando se abra el navegador, haz clic en "Authorize"
echo.
pause

call CONFIGURAR_TODO_DVTA.bat

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo ¿Quieres iniciar el túnel ahora? (S/N)
set /p iniciar="Respuesta: "

if /i "%iniciar%"=="S" (
    echo.
    echo Iniciando túnel...
    echo.
    call INICIAR_TUNNEL_DVTA.bat
) else (
    echo.
    echo Para iniciar el túnel más tarde, ejecuta:
    echo    INICIAR_TUNNEL_DVTA.bat
    echo.
    pause
)

goto fin

:instrucciones
cls
type LEER_PRIMERO.txt
echo.
pause
goto fin

:verificar
cls
call VERIFICAR_TODO.bat
goto fin

:salir
echo.
echo Adiós!
echo.
exit /b 0

:fin
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
