@echo off
chcp 65001 >nul
title 🔍 Verificación de Conexión DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICANDO CONEXIÓN DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo 📊 Verificando procesos...
echo.

REM Verificar Python
tasklist | findstr python.exe >nul
if errorlevel 1 (
    echo ❌ Servidor Python: NO CORRIENDO
    set PYTHON_OK=0
) else (
    echo ✅ Servidor Python: CORRIENDO
    set PYTHON_OK=1
)

REM Verificar Cloudflare
tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ❌ Túnel Cloudflare: NO CORRIENDO
    set CF_OK=0
) else (
    echo ✅ Túnel Cloudflare: CORRIENDO
    set CF_OK=1
)

REM Verificar puerto 8000
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ❌ Puerto 8000: NO ESCUCHANDO
    set PORT_OK=0
) else (
    echo ✅ Puerto 8000: ESCUCHANDO
    set PORT_OK=1
)

echo.
echo 🌐 Verificando DNS...
echo.
nslookup app.david.ch | findstr "80.74.152.80" >nul
if errorlevel 1 (
    echo ⚠️  DNS app.david.ch: No resuelve correctamente
    set DNS_OK=0
) else (
    echo ✅ DNS app.david.ch: CORRECTO (80.74.152.80)
    set DNS_OK=1
)

echo.
echo 🔗 Probando conexión HTTP local...
echo.
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -Method Head -TimeoutSec 5 -UseBasicParsing; if ($r.StatusCode -eq 200) { Write-Host '✅ Servidor local responde: HTTP' $r.StatusCode } else { Write-Host '⚠️  Servidor responde con código:' $r.StatusCode } } catch { Write-Host '❌ Error al conectar al servidor local:' $_.Exception.Message }"

echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 RESUMEN
echo ═══════════════════════════════════════════════════════════
echo.

if %PYTHON_OK%==1 if %CF_OK%==1 if %PORT_OK%==1 if %DNS_OK%==1 (
    echo ✅ SISTEMA FUNCIONANDO CORRECTAMENTE
    echo.
    echo 🌐 URLs disponibles:
    echo    • https://app.david.ch
    echo    • https://localhost.david.ch
    echo.
    echo 🔒 Certificado SSL: Activo (Cloudflare)
    echo 🌍 Acceso: Desde cualquier red y dispositivo
    echo.
) else (
    echo ⚠️  SISTEMA CON PROBLEMAS
    echo.
    if %PYTHON_OK%==0 echo    • Servidor Python no está corriendo
    if %CF_OK%==0 echo    • Túnel Cloudflare no está corriendo
    if %PORT_OK%==0 echo    • Puerto 8000 no está escuchando
    if %DNS_OK%==0 echo    • DNS no está configurado correctamente
    echo.
    echo 💡 Solución: Ejecuta INICIAR_SERVIDOR.bat
    echo.
)

echo ═══════════════════════════════════════════════════════════
echo.
pause
