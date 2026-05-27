@echo off
chcp 65001 >nul
title Configurar DNS para bank.dvta.ch
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 CONFIGURAR DNS PARA bank.dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM ============================================================================
REM PASO 1: VERIFICAR SERVIDORES
REM ============================================================================
echo [1/4] Verificando servidores locales...
echo.

netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Bank ^(puerto 8000^): ACTIVO
    netstat -ano | findstr ":8000" | findstr "LISTENING"
) else (
    echo      ❌ Servidor Bank ^(puerto 8000^): NO ACTIVO
    echo.
    echo      ⚠️  El servidor Bank debe estar corriendo
    echo      Ejecuta: python main.py
    echo.
    pause
    exit /b 1
)

netstat -ano | findstr ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor Exams ^(puerto 8001^): ACTIVO
) else (
    echo      ⚠️  Servidor Exams ^(puerto 8001^): NO ACTIVO
)

echo.

REM ============================================================================
REM PASO 2: CONFIGURAR DNS CON CLOUDFLARE CLI
REM ============================================================================
echo [2/4] Configurando DNS en Cloudflare...
echo.

echo      Ejecutando: cloudflared tunnel route dns ...
echo.

cloudflared tunnel route dns b75039b1-7b54-4da0-b2ab-0a338bfccdc5 bank.dvta.ch

if %errorlevel% equ 0 (
    echo.
    echo      ✅ DNS configurado correctamente
) else (
    echo.
    echo      ⚠️  No se pudo configurar automáticamente
    echo.
    echo      SOLUCIÓN MANUAL:
    echo        1. Ve a: https://dash.cloudflare.com
    echo        2. Selecciona: dvta.ch
    echo        3. Ve a: DNS ^> Records
    echo        4. Add record:
    echo           - Type: CNAME
    echo           - Name: bank
    echo           - Target: b75039b1-7b54-4da0-b2ab-0a338bfccdc5.cfargotunnel.com
    echo           - Proxy: ON ^(naranja^)
    echo        5. Save
    echo.
)

echo.

REM ============================================================================
REM PASO 3: REINICIAR TUNNEL
REM ============================================================================
echo [3/4] Reiniciando Cloudflare Tunnel...
echo.

taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 3 /nobreak >nul

start "Cloudflare Tunnel - dvta.ch" cmd /c "cloudflared.exe tunnel --config cloudflare-dvta-config.yml run"
timeout /t 5 /nobreak >nul

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel reiniciado
) else (
    echo      ❌ Error al reiniciar Cloudflare Tunnel
)

echo.

REM ============================================================================
REM PASO 4: VERIFICACIÓN
REM ============================================================================
echo [4/4] Verificación final...
echo.

echo      Estado de servicios:
echo.

netstat -ano | findstr ":8000 :8001" | findstr "LISTENING"

echo.

tasklist | findstr "cloudflared.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Cloudflare Tunnel: ACTIVO
) else (
    echo      ❌ Cloudflare Tunnel: NO ACTIVO
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 URLs configuradas:
echo.
echo   • https://dvta.ch           → Exams ^(puerto 8001^)
echo   • https://bank.dvta.ch      → Bank ^(puerto 8000^)
echo.
echo ⏱️  IMPORTANTE:
echo   • Espera 1-2 minutos para propagación DNS
echo   • Limpia caché del navegador ^(Ctrl+Shift+Del^)
echo   • Luego accede a: https://bank.dvta.ch
echo.
echo 📝 Si no funciona:
echo   • Lee: CONFIGURAR_BANK_DVTA_CH.md
echo   • Configura manualmente en Cloudflare Dashboard
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo ¿Deseas abrir bank.dvta.ch en el navegador? ^(S/N^)
choice /C SN /N /T 15 /D N /M "Esperando 15 segundos..."
if %errorlevel% equ 1 (
    echo.
    echo 🌐 Abriendo https://bank.dvta.ch...
    start https://bank.dvta.ch
    echo.
    echo ⏱️  Si da error, espera 1 minuto más y recarga
)

echo.
pause
