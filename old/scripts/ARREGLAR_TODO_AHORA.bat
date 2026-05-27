@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔧 ARREGLANDO TODO EL SISTEMA AHORA
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script va a:
echo   1. Detener todos los servicios
echo   2. Limpiar configuraciones conflictivas
echo   3. Reiniciar todo correctamente
echo   4. Verificar que funcione
echo.
echo ═══════════════════════════════════════════════════════════
echo.

echo PASO 1: Deteniendo servicios...
echo.
taskkill /F /IM python.exe 2>nul
taskkill /F /IM cloudflared.exe 2>nul
timeout /t 3 /nobreak >nul
echo    ✅ Servicios detenidos
echo.

echo PASO 2: Eliminando rutas DNS conflictivas...
echo.
cloudflared tunnel route dns delete dvdcoin dvdbank.david.ch 2>nul
cloudflared tunnel route dns delete dvdcoin app.david.ch 2>nul
cloudflared tunnel route dns delete dvdcoin localhost.david.ch 2>nul
timeout /t 2 /nobreak >nul
echo    ✅ Rutas eliminadas
echo.

echo PASO 3: Recreando rutas DNS correctamente...
echo.
cloudflared tunnel route dns dvdcoin dvdbank.david.ch
cloudflared tunnel route dns dvdcoin app.david.ch
cloudflared tunnel route dns dvdcoin localhost.david.ch
echo    ✅ Rutas recreadas
echo.

echo PASO 4: Iniciando servidor Python...
echo.
start /B python main.py > python_server.log 2>&1
timeout /t 5 /nobreak >nul
echo    ✅ Servidor Python iniciado
echo.

echo PASO 5: Iniciando túnel Cloudflare...
echo.
start /B cloudflared tunnel --config cloudflare-config.yml run dvdcoin > cloudflare_tunnel.log 2>&1
timeout /t 10 /nobreak >nul
echo    ✅ Túnel Cloudflare iniciado
echo.

echo PASO 6: Verificando servicios...
echo.
echo    Servidor Python:
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -Method Get -TimeoutSec 5 -UseBasicParsing; Write-Host '      ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '      ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo    Túnel Cloudflare:
cloudflared tunnel info 6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33
echo.

echo PASO 7: Esperando propagación DNS (30 segundos)...
timeout /t 30 /nobreak
echo    ✅ Esperado
echo.

echo PASO 8: Probando URLs...
echo.
echo    dvdbank.david.ch:
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://dvdbank.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '      ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '      ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo    app.david.ch:
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://app.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '      ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '      ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo ═══════════════════════════════════════════════════════════
echo   📊 RESUMEN
echo ═══════════════════════════════════════════════════════════
echo.
echo Si ves errores SSL/TLS arriba, el problema es que hay
echo registros DNS tipo A en Cloudflare que están interfiriendo.
echo.
echo SOLUCIÓN MANUAL (5 minutos):
echo   1. Ve a: https://dash.cloudflare.com
echo   2. Selecciona: david.ch
echo   3. Ve a: DNS ^> Records
echo   4. ELIMINA estos registros tipo A:
echo      - dvdbank.david.ch → 80.74.152.80
echo      - app.david.ch → 80.74.152.80
echo      - localhost.david.ch → 80.74.152.80
echo   5. Deja solo los registros CNAME (creados automáticamente)
echo   6. Espera 2 minutos
echo   7. Ejecuta: PROBAR_TODAS_URLS.bat
echo.
echo SOLUCIÓN AUTOMÁTICA (requiere API token):
echo   1. Ejecuta: ARREGLAR_DNS_CLOUDFLARE.bat
echo   2. Sigue las instrucciones para obtener el API token
echo   3. Ejecuta: APLICAR_DNS_AUTOMATICO.bat
echo.
echo SOLUCIÓN TEMPORAL (funciona YA):
echo   1. Ejecuta: SOLUCION_RAPIDA_TEMPORAL.bat
echo   2. Obtendrás una URL como: https://xxx.trycloudflare.com
echo   3. Esa URL funciona inmediatamente (pero cambia al reiniciar)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
