@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   📧 PASO 2: CONFIGURAR EMAIL EN CLOUDFLARE PARA dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script va a configurar TODOS los registros DNS de email automáticamente.
echo.
echo ⚠️  ANTES DE CONTINUAR, necesitas crear un token de Cloudflare:
echo.
echo    1. Abre tu navegador y ve a:
echo       https://dash.cloudflare.com/profile/api-tokens
echo.
echo    2. Haz clic en el botón azul [Create Token]
echo.
echo    3. Busca el template "Edit zone DNS" y haz clic en [Use template]
echo.
echo    4. En "Zone Resources":
echo       - Zone: Include - Specific zone
echo       - Selecciona: dvta.ch
echo.
echo    5. Haz clic en [Continue to summary]
echo.
echo    6. Haz clic en [Create Token]
echo.
echo    7. COPIA el token que aparece (solo se muestra una vez)
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
echo.
echo Ejecutando configuración de DNS...
echo.

python configurar_dns_cloudflare_dvta.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
