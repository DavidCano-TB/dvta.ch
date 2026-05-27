@echo off
chcp 65001 >nul
title ACTUALIZAR DESDE GIT
color 0D

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔄 ACTUALIZAR SISTEMA DESDE GIT
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script:
echo   1. Hace backup de las bases de datos
echo   2. Detiene los servicios
echo   3. Descarga los últimos cambios de Git
echo   4. Actualiza las dependencias
echo   5. Reinicia los servicios
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PASO 1: BACKUP DE SEGURIDAD                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Creando backup de seguridad...
call BACKUP_COMPLETO.bat
echo.
echo ✅ Backup completado
echo.

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PASO 2: DETENER SERVICIOS                                               │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Deteniendo servicios...
echo.

REM Detener Cloudflare Tunnel
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Deteniendo Cloudflare Tunnel...
    taskkill /F /IM cloudflared.exe >nul 2>&1
    echo   ✅ Cloudflare Tunnel detenido
) else (
    echo   ⚠️  Cloudflare Tunnel no estaba corriendo
)
echo.

REM Detener servidores Python
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   Deteniendo servidores Python...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo   ✅ Servidores Python detenidos
) else (
    echo   ⚠️  Servidores Python no estaban corriendo
)
echo.

echo ✅ Servicios detenidos
echo.

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PASO 3: ACTUALIZAR DESDE GIT                                            │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Verificando estado de Git...
git status
echo.

echo ¿Hay cambios locales sin commitear?
echo   • Si hay cambios, se guardarán temporalmente (stash)
echo   • Después del pull, se restaurarán
echo.

pause

REM Guardar cambios locales si existen
git diff --quiet
if %errorlevel% neq 0 (
    echo Guardando cambios locales...
    git stash save "Auto-stash antes de actualizar - %date% %time%"
    echo ✅ Cambios guardados
    set STASHED=1
) else (
    echo ✅ No hay cambios locales
    set STASHED=0
)
echo.

echo Descargando últimos cambios...
git pull origin master
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: No se pudo hacer pull desde Git
    echo.
    echo POSIBLES CAUSAS:
    echo   • No hay conexión a internet
    echo   • Conflictos con cambios locales
    echo   • Problemas de autenticación
    echo.
    echo SOLUCIÓN:
    echo   1. Verifica tu conexión a internet
    echo   2. Ejecuta: git status
    echo   3. Resuelve conflictos manualmente si es necesario
    echo.
    pause
    exit /b 1
)
echo.
echo ✅ Cambios descargados
echo.

REM Restaurar cambios locales si se guardaron
if %STASHED% equ 1 (
    echo Restaurando cambios locales...
    git stash pop
    if %errorlevel% neq 0 (
        echo.
        echo ⚠️  ADVERTENCIA: Hubo conflictos al restaurar cambios locales
        echo.
        echo SOLUCIÓN:
        echo   1. Revisa los conflictos con: git status
        echo   2. Resuelve los conflictos manualmente
        echo   3. Ejecuta: git add . && git commit -m "Resolver conflictos"
        echo.
        pause
    ) else (
        echo ✅ Cambios locales restaurados
    )
    echo.
)

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PASO 4: ACTUALIZAR DEPENDENCIAS                                         │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Actualizando dependencias de Python...
echo.

REM Actualizar dependencias de Exams
if exist "modules\exams\requirements.txt" (
    echo   Actualizando dependencias de Exams...
    cd modules\exams
    pip install -r requirements.txt --upgrade
    cd ..\..
    echo   ✅ Dependencias de Exams actualizadas
) else (
    echo   ⚠️  No se encontró modules\exams\requirements.txt
)
echo.

REM Actualizar dependencias principales si existen
if exist "requirements.txt" (
    echo   Actualizando dependencias principales...
    pip install -r requirements.txt --upgrade
    echo   ✅ Dependencias principales actualizadas
) else (
    echo   ⚠️  No se encontró requirements.txt principal
)
echo.

echo ✅ Dependencias actualizadas
echo.

pause

echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │  PASO 5: REINICIAR SERVICIOS                                             │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

echo Reiniciando servicios...
echo.

echo ¿Deseas reiniciar los servicios ahora? (S/N)
choice /C SN /N /M "Selecciona S para Sí o N para No: "
if %errorlevel% equ 1 (
    echo.
    echo Iniciando servicios...
    call ACTIVAR_DVTA_CH_AHORA.bat
) else (
    echo.
    echo ⚠️  Servicios NO reiniciados
    echo.
    echo Para iniciar manualmente:
    echo   • Ejecuta: ACTIVAR_DVTA_CH_AHORA.bat
    echo.
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ ACTUALIZACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   📥 Cambios descargados desde Git
echo   📦 Dependencias actualizadas
echo   💾 Backup de seguridad creado
echo.
echo   Para verificar el estado:
echo     • Ejecuta: STATUS_DVTA.bat
echo     • O ejecuta: git log -5 --oneline (ver últimos commits)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
