@echo off
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  📊 ESTADO RÁPIDO DEL SISTEMA
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Cloudflared instalado
if exist "cloudflared.exe" (
    echo  ✅ cloudflared.exe instalado
) else (
    echo  ❌ cloudflared.exe NO instalado
)

REM Autenticación
if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo  ✅ Autenticado con Cloudflare
) else (
    echo  ❌ NO autenticado con Cloudflare
    echo     👉 Ejecuta: cloudflared.exe tunnel login
)

REM Configuración
if exist "cloudflare-dvta-config.yml" (
    findstr /C:"TUNNEL_ID_AQUI" "cloudflare-dvta-config.yml" >nul
    if errorlevel 1 (
        echo  ✅ Configuración completada
    ) else (
        echo  ⚠️  Configuración incompleta
        echo     👉 Ejecuta: CONFIGURAR_TUNNEL_DVTA_CH.bat
    )
) else (
    echo  ⚠️  Archivo de configuración no encontrado
)

REM Servidor Python
tasklist | findstr "python.exe" >nul
if errorlevel 1 (
    echo  ❌ Servidor Python NO está corriendo
) else (
    echo  ✅ Servidor Python corriendo
)

REM Túnel Cloudflare
tasklist | findstr "cloudflared.exe" >nul
if errorlevel 1 (
    echo  ❌ Túnel Cloudflare NO está corriendo
) else (
    echo  ✅ Túnel Cloudflare corriendo
)

REM DNS
echo.
echo  🌐 Verificando DNS...
nslookup dvta.ch 2>nul | findstr "104.21" >nul
if errorlevel 1 (
    nslookup dvta.ch 2>nul | findstr "172.67" >nul
    if errorlevel 1 (
        echo  ❌ DNS NO resuelve
        echo     👉 Configura el túnel primero
    ) else (
        echo  ✅ DNS resuelve a Cloudflare
    )
) else (
    echo  ✅ DNS resuelve a Cloudflare
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  📖 Guía completa: PASOS_SIMPLES_ACTIVAR_DVTA_CH.txt
echo  🔍 Verificación detallada: GUIA_COMPLETA_DNS_DVTA_CH.txt
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
