@echo off
chcp 65001 >nul
cls
echo ═══════════════════════════════════════════════════════════
echo   🚀 CONFIGURACIÓN AUTOMÁTICA DNS CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script configurará TODOS los registros DNS de email
echo para dvta.ch en Cloudflare automáticamente.
echo.
echo Registros que se configurarán:
echo   • MX (servidor de correo)
echo   • SPF (autorización de envío)
echo   • DKIM (firma digital)
echo   • DMARC (política de seguridad)
echo   • Autoconfig (Thunderbird)
echo   • Autodiscover (Outlook)
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo.
    pause
    exit /b 1
)

REM Verificar si el script existe
if not exist "configurar_dns_cloudflare_dvta.py" (
    echo ❌ No se encuentra configurar_dns_cloudflare_dvta.py
    echo.
    pause
    exit /b 1
)

echo Ejecutando configuración...
echo.
python configurar_dns_cloudflare_dvta.py

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   ✅ CONFIGURACIÓN COMPLETADA
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Los registros DNS han sido configurados en Cloudflare.
    echo.
    echo ⏳ Los cambios pueden tardar 5-10 minutos en propagarse.
    echo.
    echo Tu email @dvta.ch debería seguir funcionando normalmente.
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   ⚠️  HUBO ALGÚN PROBLEMA
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Revisa los mensajes de error arriba.
    echo.
    echo Si necesitas ayuda:
    echo   1. Verifica que el token de Cloudflare sea correcto
    echo   2. Verifica que el token tenga permisos de DNS
    echo   3. Verifica que el Zone ID sea correcto
    echo.
)

echo.
pause
