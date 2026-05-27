@echo off
chcp 65001 >nul
title 🌐 Añadir dvdbank.ch a Cloudflare
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 AÑADIR dvdbank.ch A CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script te guiará para añadir dvdbank.ch a Cloudflare.
echo.
echo ⚠️  IMPORTANTE: Solo ejecuta este script DESPUÉS de que
echo    Hoststar confirme que el dominio está registrado.
echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO 1: Añadir el sitio en Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Abre tu navegador
echo 2. Ve a: https://dash.cloudflare.com
echo 3. Inicia sesión con tu cuenta
echo 4. Haz clic en "Add a Site" (Añadir un sitio)
echo 5. Escribe: dvdbank.ch
echo 6. Haz clic en "Add site"
echo 7. Selecciona el plan FREE (gratis)
echo 8. Haz clic en "Continue"
echo.
pause
echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO 2: Copiar los nameservers de Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.
echo Cloudflare te mostrará 2 nameservers, algo como:
echo.
echo   alice.ns.cloudflare.com
echo   bob.ns.cloudflare.com
echo.
echo ⚠️  IMPORTANTE: Copia estos nameservers ahora.
echo    Los necesitarás en el siguiente paso.
echo.
echo ¿Ya copiaste los nameservers? (S/N)
set /p copiado=
if /i not "%copiado%"=="S" (
    echo.
    echo ⚠️  Por favor, copia los nameservers antes de continuar.
    pause
    exit /b 1
)
echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO 3: Cambiar nameservers en Hoststar
echo ═══════════════════════════════════════════════════════════
echo.
echo Ahora necesitas cambiar los nameservers en Hoststar:
echo.
echo 1. Ve a: https://my.hoststar.ch
echo 2. Inicia sesión
echo 3. Ve a "Mes domaines" o "Domains"
echo 4. Haz clic en "dvdbank.ch"
echo 5. Busca "Nameservers" o "DNS"
echo 6. Cambia a "Nameservers personnalisés" o "Custom nameservers"
echo 7. Pega los 2 nameservers de Cloudflare
echo 8. Guarda los cambios
echo.
echo ⚠️  IMPORTANTE: Este cambio puede tardar 2-48 horas en
echo    propagarse (normalmente 2-4 horas).
echo.
pause
echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 PASO 4: Esperar confirmación de Cloudflare
echo ═══════════════════════════════════════════════════════════
echo.
echo Cloudflare verificará que los nameservers estén configurados.
echo.
echo Recibirás un email cuando esté listo (normalmente 2-4 horas).
echo.
echo El email dirá algo como:
echo   "dvdbank.ch is now active on Cloudflare"
echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ SIGUIENTE PASO
echo ═══════════════════════════════════════════════════════════
echo.
echo Cuando recibas el email de confirmación de Cloudflare:
echo.
echo   Ejecuta: CONFIGURAR_DVDBANK_FINAL.bat
echo.
echo Ese script configurará automáticamente:
echo   • DNS en Cloudflare
echo   • Túnel Cloudflare
echo   • Certificado SSL
echo   • Todo lo necesario para que funcione
echo.
echo ═══════════════════════════════════════════════════════════
echo   📝 RESUMEN
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ Pasos completados:
echo    1. Añadir dvdbank.ch a Cloudflare
echo    2. Copiar nameservers de Cloudflare
echo    3. Cambiar nameservers en Hoststar
echo.
echo ⏱️  Esperando:
echo    • Propagación DNS (2-48 horas, normalmente 2-4 horas)
echo    • Email de confirmación de Cloudflare
echo.
echo 🚀 Próximo paso:
echo    Cuando recibas el email, ejecuta:
echo    CONFIGURAR_DVDBANK_FINAL.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Quieres que abra Cloudflare en tu navegador ahora? (S/N)
set /p abrir=
if /i "%abrir%"=="S" (
    start https://dash.cloudflare.com
    echo.
    echo ✅ Abriendo Cloudflare...
)
echo.
pause
