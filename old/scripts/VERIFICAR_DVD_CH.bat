@echo off
chcp 65001 >nul
title 🔍 Verificar dvd.ch
color 0E

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICANDO DOMINIO dvd.ch
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo 📊 Verificando DNS de dvd.ch...
echo.

nslookup dvd.ch

echo.
echo ═══════════════════════════════════════════════════════════
echo   📋 INTERPRETACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Si ves una dirección IP (Address):
echo   ✅ El dominio EXISTE y está configurado
echo.
echo Si ves "Non-existent domain" o "No entries found":
echo   ❌ El dominio NO EXISTE o no está configurado
echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 VERIFICAR EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo Para verificar si tienes dvd.ch en Cloudflare:
echo.
echo 1. Ve a: https://dash.cloudflare.com
echo 2. Inicia sesión
echo 3. Busca "dvd.ch" en la lista de dominios
echo.
echo ¿Aparece dvd.ch en la lista?
echo   ✅ SÍ  → Puedes configurarlo (ejecuta: CONFIGURAR_DVD_CH_FINAL.bat)
echo   ❌ NO  → Necesitas añadirlo o comprarlo
echo.
echo ═══════════════════════════════════════════════════════════
echo   💰 COMPRAR dvd.ch
echo ═══════════════════════════════════════════════════════════
echo.
echo Si NO tienes dvd.ch, puedes comprarlo en:
echo.
echo 1. Infomaniak (Suizo, recomendado)
echo    https://www.infomaniak.com/es/dominios
echo    Precio: ~15 CHF/año (~15€)
echo.
echo 2. Cloudflare Registrar
echo    https://dash.cloudflare.com
echo    Precio: ~15 CHF/año (precio al costo)
echo.
echo 3. Hostpoint (Suizo)
echo    https://www.hostpoint.ch
echo    Precio: ~20 CHF/año
echo.
echo ═══════════════════════════════════════════════════════════
echo   🆓 ALTERNATIVA GRATIS
echo ═══════════════════════════════════════════════════════════
echo.
echo Si NO quieres pagar por dvd.ch, puedes usar:
echo.
echo ✅ app.david.ch (YA CONFIGURADO Y FUNCIONANDO)
echo    https://app.david.ch
echo.
echo ✅ Otros subdominios de david.ch (GRATIS):
echo    https://dvd.david.ch
echo    https://bank.david.ch
echo    https://coin.david.ch
echo.
echo Para configurar un subdominio gratis:
echo    Ejecuta: CONFIGURAR_SUBDOMINIO.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
