@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 ARREGLANDO DNS EN CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo El problema es que hay registros DNS tipo A apuntando a
echo 80.74.152.80 que están interfiriendo con el túnel.
echo.
echo NECESITAS HACER ESTO MANUALMENTE:
echo.
echo 1. Ve a: https://dash.cloudflare.com
echo 2. Selecciona el dominio: david.ch
echo 3. Ve a la sección: DNS ^> Records
echo 4. BUSCA y ELIMINA estos registros tipo A:
echo    - dvdbank.david.ch → 80.74.152.80 (ELIMINAR)
echo    - app.david.ch → 80.74.152.80 (ELIMINAR)
echo    - localhost.david.ch → 80.74.152.80 (ELIMINAR)
echo.
echo 5. Los registros CNAME correctos ya están creados por cloudflared:
echo    - dvdbank.david.ch → CNAME → 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.cfargotunnel.com
echo    - app.david.ch → CNAME → 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.cfargotunnel.com
echo    - localhost.david.ch → CNAME → 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.cfargotunnel.com
echo.
echo 6. Asegúrate de que el "Proxy status" esté en NARANJA (Proxied)
echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚠️  IMPORTANTE
echo ═══════════════════════════════════════════════════════════
echo.
echo NO puedo eliminar los registros DNS automáticamente porque
echo necesito tu API token de Cloudflare.
echo.
echo Después de eliminar los registros A incorrectos, espera
echo 1-2 minutos y ejecuta: PROBAR_TODAS_URLS.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Quieres que te ayude a obtener el API token de Cloudflare
echo para automatizar esto? (S/N)
echo.
set /p respuesta="Tu respuesta: "
if /i "%respuesta%"=="S" goto :mostrar_instrucciones
if /i "%respuesta%"=="SI" goto :mostrar_instrucciones
goto :fin

:mostrar_instrucciones
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔑 CÓMO OBTENER EL API TOKEN
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Ve a: https://dash.cloudflare.com/profile/api-tokens
echo 2. Haz clic en "Create Token"
echo 3. Usa la plantilla "Edit zone DNS"
echo 4. Selecciona:
echo    - Zone Resources: Include → Specific zone → david.ch
echo 5. Haz clic en "Continue to summary"
echo 6. Haz clic en "Create Token"
echo 7. COPIA el token (solo se muestra una vez)
echo 8. Guárdalo en: c:\dvdcoin\config\cloudflare_token.txt
echo.
echo Después ejecuta: APLICAR_DNS_AUTOMATICO.bat
echo.

:fin
echo.
pause
