@echo off
chcp 65001 >nul
title DVDBank - Menú Principal
color 0B

:MENU
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🏦 DVDBANK - MENÚ PRINCIPAL
echo   Sistema: dvta.ch con Cloudflare Tunnel
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   [1] Iniciar Sistema
echo   [2] Detener Sistema
echo   [3] Ver Estado del Sistema (Tiempo Real)
echo   [4] Diagnóstico Completo
echo.
echo   [5] Configurar Inicio Automático
echo   [6] Desinstalar Inicio Automático
echo   [7] Instalación Completa Automática
echo.
echo   [8] Configurar Cloudflare Tunnel (cuando DNS esté activo)
echo   [9] Configurar Email en Cloudflare (cuando DNS esté activo)
echo   [10] Actualizar Cloudflared
echo.
echo   [11] Backup del Sistema
echo   [12] Limpiar Archivos Ngrok
echo   [13] Configurar Arranque desde C:
echo.
echo   [14] Ver Documentación
echo   [15] Abrir Servidor Local en Navegador
echo.
echo   [0] Salir
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p OPCION="Selecciona una opción: "

if "%OPCION%"=="1" goto INICIAR
if "%OPCION%"=="2" goto DETENER
if "%OPCION%"=="3" goto ESTADO
if "%OPCION%"=="4" goto DIAGNOSTICO
if "%OPCION%"=="5" goto INSTALAR_AUTO
if "%OPCION%"=="6" goto DESINSTALAR_AUTO
if "%OPCION%"=="7" goto INSTALACION_COMPLETA
if "%OPCION%"=="8" goto CONFIG_TUNNEL
if "%OPCION%"=="9" goto CONFIG_EMAIL
if "%OPCION%"=="10" goto ACTUALIZAR
if "%OPCION%"=="11" goto BACKUP
if "%OPCION%"=="12" goto LIMPIAR_NGROK
if "%OPCION%"=="13" goto CONFIG_ARRANQUE
if "%OPCION%"=="14" goto DOCUMENTACION
if "%OPCION%"=="15" goto ABRIR_NAVEGADOR
if "%OPCION%"=="0" goto SALIR

echo.
echo ❌ Opción no válida
timeout /t 2 /nobreak >nul
goto MENU

:INICIAR
cls
call INICIAR_SISTEMA_DVTA.bat
pause
goto MENU

:DETENER
cls
call DETENER_SISTEMA.bat
goto MENU

:ESTADO
cls
call VER_ESTADO_SISTEMA.bat
goto MENU

:DIAGNOSTICO
cls
call DIAGNOSTICO_COMPLETO.bat
goto MENU

:INSTALAR_AUTO
cls
echo.
echo ⚠️  Este script requiere permisos de administrador.
echo.
echo Por favor, ejecuta como administrador:
echo    INSTALAR_INICIO_AUTOMATICO.bat
echo.
pause
goto MENU

:DESINSTALAR_AUTO
cls
echo.
echo ⚠️  Este script requiere permisos de administrador.
echo.
echo Por favor, ejecuta como administrador:
echo    DESINSTALAR_INICIO_AUTOMATICO.bat
echo.
pause
goto MENU

:INSTALACION_COMPLETA
cls
echo.
echo ⚠️  Este script requiere permisos de administrador.
echo.
echo Por favor, ejecuta como administrador:
echo    INSTALACION_COMPLETA_AUTOMATICA.bat
echo.
pause
goto MENU

:CONFIG_TUNNEL
cls
call CONFIGURAR_TUNNEL_DVTA.bat
goto MENU

:CONFIG_EMAIL
cls
call CONFIGURAR_EMAIL_CLOUDFLARE.bat
goto MENU

:ACTUALIZAR
cls
call ACTUALIZAR_CLOUDFLARED.bat
goto MENU

:BACKUP
cls
call BACKUP_SISTEMA.bat
goto MENU

:LIMPIAR_NGROK
cls
call LIMPIAR_ARCHIVOS_NGROK.bat
goto MENU

:CONFIG_ARRANQUE
cls
echo.
echo ⚠️  Este script requiere permisos de administrador.
echo.
echo Por favor, ejecuta como administrador:
echo    CONFIGURAR_ARRANQUE_DISCO_C.bat
echo.
pause
goto MENU

:DOCUMENTACION
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📚 DOCUMENTACIÓN DISPONIBLE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   [1] RESUMEN_MIGRACION.txt
echo       → Resumen ejecutivo de la migración
echo.
echo   [2] MIGRACION_COMPLETADA.txt
echo       → Guía completa de la migración
echo.
echo   [3] PASOS_CONFIGURACION_CLOUDFLARE_DVTA_CH.txt
echo       → Pasos detallados para configurar Cloudflare
echo.
echo   [4] REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt
echo       → Backup de registros DNS de Infomaniak
echo.
echo   [0] Volver al menú
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
set /p DOC="Selecciona un documento (0-4): "

if "%DOC%"=="1" (
    cls
    type RESUMEN_MIGRACION.txt
    echo.
    pause
    goto DOCUMENTACION
)
if "%DOC%"=="2" (
    cls
    type MIGRACION_COMPLETADA.txt
    echo.
    pause
    goto DOCUMENTACION
)
if "%DOC%"=="3" (
    cls
    type PASOS_CONFIGURACION_CLOUDFLARE_DVTA_CH.txt
    echo.
    pause
    goto DOCUMENTACION
)
if "%DOC%"=="4" (
    cls
    type REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt
    echo.
    pause
    goto DOCUMENTACION
)
if "%DOC%"=="0" goto MENU

echo.
echo ❌ Opción no válida
timeout /t 2 /nobreak >nul
goto DOCUMENTACION

:ABRIR_NAVEGADOR
start http://localhost:8000
echo.
echo ✅ Navegador abierto en: http://localhost:8000
echo.
timeout /t 2 /nobreak >nul
goto MENU

:SALIR
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   👋 Hasta luego
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Para volver a abrir este menú:
echo    MENU_PRINCIPAL.bat
echo.
timeout /t 2 /nobreak >nul
exit /b 0
