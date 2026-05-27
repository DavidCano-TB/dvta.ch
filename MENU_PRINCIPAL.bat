@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

:MENU
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  🏦 DVDBANK - MENÚ PRINCIPAL
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  SERVIDOR Y SISTEMA:
echo  ───────────────────────────────────────────────────────────────────────────
echo   1. Iniciar servidor y túnel
echo   2. Ver estado del sistema
echo   3. Configurar inicio automático con Windows
echo.
echo  DEPLOY Y ACTUALIZACIONES:
echo  ───────────────────────────────────────────────────────────────────────────
echo   4. Configurar deploy con email (GitHub Secrets)
echo   5. Verificar configuración de deploy
echo   6. Actualizar servidor ahora (git pull + reinicio)
echo   7. Iniciar monitor de actualizaciones
echo.
echo  CLOUDFLARE Y TÚNEL:
echo  ───────────────────────────────────────────────────────────────────────────
echo   8. Activar túnel permanente dvta.ch
echo   9. Abrir dashboard de Cloudflare
echo.
echo  DOCUMENTACIÓN:
echo  ───────────────────────────────────────────────────────────────────────────
echo   10. Ver resumen completo del sistema
echo   11. Ver instrucciones de deploy con email
echo   12. Ver instrucciones de túnel dvta.ch
echo.
echo  ACCESOS RÁPIDOS:
echo  ───────────────────────────────────────────────────────────────────────────
echo   13. Abrir GitHub
echo   14. Abrir historial de Git
echo.
echo   0. Salir
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
set /p OPCION="Selecciona una opción (0-14): "

if "%OPCION%"=="1" goto INICIAR_SERVIDOR
if "%OPCION%"=="2" goto VER_ESTADO
if "%OPCION%"=="3" goto CONFIGURAR_INICIO
if "%OPCION%"=="4" goto CONFIGURAR_SECRETS
if "%OPCION%"=="5" goto VERIFICAR_DEPLOY
if "%OPCION%"=="6" goto ACTUALIZAR_AHORA
if "%OPCION%"=="7" goto MONITOR_UPDATES
if "%OPCION%"=="8" goto ACTIVAR_TUNEL
if "%OPCION%"=="9" goto ABRIR_CLOUDFLARE
if "%OPCION%"=="10" goto VER_RESUMEN
if "%OPCION%"=="11" goto VER_INSTRUCCIONES_DEPLOY
if "%OPCION%"=="12" goto VER_INSTRUCCIONES_TUNEL
if "%OPCION%"=="13" goto ABRIR_GITHUB
if "%OPCION%"=="14" goto ABRIR_GIT_GRAFICO
if "%OPCION%"=="0" goto SALIR

echo.
echo Opción no válida. Presiona cualquier tecla para continuar...
pause >nul
goto MENU

:INICIAR_SERVIDOR
cls
echo.
echo Iniciando servidor y túnel...
echo.
call INICIAR_DVDBANK_DVTA.bat
pause
goto MENU

:VER_ESTADO
cls
echo.
call VER_ESTADO_SISTEMA.bat
pause
goto MENU

:CONFIGURAR_INICIO
cls
echo.
call CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
pause
goto MENU

:CONFIGURAR_SECRETS
cls
echo.
call CONFIGURAR_SECRETS_GITHUB.bat
pause
goto MENU

:VERIFICAR_DEPLOY
cls
echo.
call VERIFICAR_DEPLOY_EMAIL.bat
goto MENU

:ACTUALIZAR_AHORA
cls
echo.
call AUTO_UPDATE.bat
pause
goto MENU

:MONITOR_UPDATES
cls
echo.
echo Iniciando monitor de actualizaciones...
echo (Presiona Ctrl+C para detener)
echo.
timeout /t 3 /nobreak >nul
call WATCH_UPDATES.bat
pause
goto MENU

:ACTIVAR_TUNEL
cls
echo.
call ACTIVAR_DVTA_CH_AHORA.bat
pause
goto MENU

:ABRIR_CLOUDFLARE
cls
echo.
echo Abriendo dashboard de Cloudflare...
call ABRIR_CLOUDFLARE_DASHBOARD.bat
timeout /t 2 /nobreak >nul
goto MENU

:VER_RESUMEN
cls
echo.
if exist "RESUMEN_SISTEMA_COMPLETO.txt" (
    type RESUMEN_SISTEMA_COMPLETO.txt
) else (
    echo Archivo no encontrado: RESUMEN_SISTEMA_COMPLETO.txt
)
echo.
pause
goto MENU

:VER_INSTRUCCIONES_DEPLOY
cls
echo.
if exist "PASOS_CONFIGURAR_EMAIL_DEPLOY.txt" (
    type PASOS_CONFIGURAR_EMAIL_DEPLOY.txt
) else (
    echo Archivo no encontrado: PASOS_CONFIGURAR_EMAIL_DEPLOY.txt
)
echo.
pause
goto MENU

:VER_INSTRUCCIONES_TUNEL
cls
echo.
if exist "EJECUTA_ESTO_PARA_DVTA_CH.txt" (
    type EJECUTA_ESTO_PARA_DVTA_CH.txt
) else (
    echo Archivo no encontrado: EJECUTA_ESTO_PARA_DVTA_CH.txt
)
echo.
pause
goto MENU

:ABRIR_GITHUB
cls
echo.
echo Abriendo GitHub...
call ABRIR_GITHUB.bat
timeout /t 2 /nobreak >nul
goto MENU

:ABRIR_GIT_GRAFICO
cls
echo.
echo Abriendo historial de Git...
call ABRIR_GIT_GRAFICO.bat
timeout /t 2 /nobreak >nul
goto MENU

:SALIR
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  👋 ¡Hasta luego!
echo ═══════════════════════════════════════════════════════════════════════════
echo.
timeout /t 2 /nobreak >nul
exit /b 0
