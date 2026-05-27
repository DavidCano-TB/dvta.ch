@echo off
chcp 65001 >nul
title ACTIVAR dvta.ch - SOLUCIÓN DEFINITIVA
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 ACTIVAR dvta.ch - SOLUCIÓN DEFINITIVA Y ROBUSTA
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ============================================================================
REM PASO 1: LIMPIAR PROCESOS ANTERIORES
REM ============================================================================
echo [1/6] Limpiando procesos anteriores...
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq DVDExams Server*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos anteriores detenidos
echo.

REM ============================================================================
REM PASO 2: VERIFICAR E INSTALAR DEPENDENCIAS
REM ============================================================================
echo [2/6] Verificando dependencias de Python...
cd modules\exams

python -c "import fastapi, uvicorn, pydantic, bcrypt, jose" >nul 2>&1
if %errorlevel% neq 0 (
    echo      ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo      ❌ ERROR: No se pudieron instalar las dependencias
        echo.
        echo      SOLUCIÓN:
        echo        1. Verifica que Python esté instalado
        echo        2. Ejecuta manualmente: pip install -r modules\exams\requirements.txt
        echo.
        cd ..\..
        pause
        exit /b 1
    )
    echo      ✅ Dependencias instaladas correctamente
) else (
    echo      ✅ Todas las dependencias están instaladas
)

cd ..\..
echo.

REM ============================================================================
REM PASO 3: VERIFICAR ESTRUCTURA DE DIRECTORIOS
REM ============================================================================
echo [3/6] Verificando estructura de directorios...

if not exist "modules\exams\data" mkdir "modules\exams\data"
if not exist "modules\exams\config" mkdir "modules\exams\config"
if not exist "modules\exams\static" mkdir "modules\exams\static"
if not exist "modules\exams\opo" mkdir "modules\exams\opo"

echo      ✅ Estructura de directorios OK
echo.

REM ============================================================================
REM PASO 4: INICIAR SERVIDOR EXAMS
REM ============================================================================
echo [4/6] Iniciando servidor Exams en puerto 8001...
echo      ⏳ Esto puede tardar unos segundos...
echo.

start "DVDExams Server - dvta.ch" cmd /c "cd /d %~dp0modules\exams && python start_exams.py"

REM Esperar a que el servidor inicie
timeout /t 8 /nobreak >nul

REM Verificar que el servidor está corriendo
netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Exams corriendo en puerto 8001
) else (
    echo      ⚠️  Esperando más tiempo para que el servidor inicie...
    timeout /t 7 /nobreak >nul
    
    netstat -ano | findstr ":8001" >nul 2>&1
    if %errorlevel% equ 0 (
        echo      ✅ Servidor Exams corriendo en puerto 8001
    ) else (
        echo      ❌ ERROR: El servidor no se inició en puerto 8001
        echo.
        echo      DIAGNÓSTICO:
        echo        • Verifica la ventana "DVDExams Server" para ver errores
        echo        • Puede haber un error en el código Python
        echo        • Verifica que el puerto 8001 no esté ocupado
        echo.
        echo      COMANDOS ÚTILES:
        echo        netstat -ano ^| findstr ":8001"  (ver qué usa el puerto)
        echo        tasklist ^| findstr "python"      (ver procesos Python)
        echo.
        pause
        exit /b 1
    )
)
echo.

REM ============================================================================
REM PASO 5: INICIAR CLOUDFLARE TUNNEL
REM ============================================================================
echo [5/6] Iniciando Cloudflare Tunnel...

if not exist "cloudflare-dvta-config.yml" (
    echo      ❌ ERROR: No se encuentra cloudflare-dvta-config.yml
    echo.
    echo      SOLUCIÓN:
    echo        Verifica que el archivo cloudflare-dvta-config.yml existe
    echo.
    pause
    exit /b 1
)

start "Cloudflare Tunnel - dvta.ch" cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run"
timeout /t 5 /nobreak >nul

REM Verificar que cloudflared está corriendo
tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel activo
) else (
    echo      ⚠️  Cloudflare Tunnel puede no estar corriendo
    echo      Verifica la ventana "Cloudflare Tunnel - dvta.ch"
)
echo.

REM ============================================================================
REM PASO 6: VERIFICACIÓN FINAL
REM ============================================================================
echo [6/6] Verificación final...
echo.

REM Verificar servidor local
curl -s http://localhost:8001 >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor local responde en http://localhost:8001
) else (
    echo      ⚠️  Servidor local no responde (puede ser normal si curl no está instalado)
)

REM Verificar procesos
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Proceso Python corriendo
) else (
    echo      ❌ Proceso Python NO encontrado
)

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Proceso Cloudflare corriendo
) else (
    echo      ❌ Proceso Cloudflare NO encontrado
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ ACTIVACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 ACCESO:
echo   • Externo:  https://dvta.ch
echo   • Local:    http://localhost:8001
echo.
echo 📊 SERVICIOS ACTIVOS:
echo   • DVDExams Server (puerto 8001)
echo   • Cloudflare Tunnel
echo.
echo ⏱️  IMPORTANTE:
echo   • Espera 10-30 segundos para que el tunnel se conecte
echo   • Si dvta.ch da error, espera 1 minuto y recarga
echo   • La primera conexión puede tardar más
echo.
echo 🛑 MANTENER CORRIENDO:
echo   • NO cierres las ventanas de servidor y tunnel
echo   • Déjalas minimizadas en segundo plano
echo   • Si cierras las ventanas, los servicios se detendrán
echo.
echo 🔄 PARA DETENER:
echo   • Cierra las ventanas "DVDExams Server" y "Cloudflare Tunnel"
echo   • O ejecuta: taskkill /F /IM python.exe ^&^& taskkill /F /IM cloudflared.exe
echo.
echo 📝 LOGS:
echo   • Ventana "DVDExams Server" - logs del servidor
echo   • Ventana "Cloudflare Tunnel" - logs del tunnel
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Abrir navegador automáticamente
echo ¿Deseas abrir dvta.ch en el navegador? (S/N)
choice /C SN /N /T 10 /D S /M "Abriendo en 10 segundos..."
if %errorlevel% equ 1 (
    echo.
    echo 🌐 Abriendo https://dvta.ch en el navegador...
    start https://dvta.ch
    echo.
    echo ⏱️  Espera 10-30 segundos para que cargue
)

echo.
pause
