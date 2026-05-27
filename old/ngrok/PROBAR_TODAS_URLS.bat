@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 PROBANDO TODAS LAS URLs
echo ═══════════════════════════════════════════════════════════
echo.

echo 1. Probando localhost:8000...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -Method Get -TimeoutSec 5 -UseBasicParsing; Write-Host '   ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo 2. Probando dvdbank.david.ch...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://dvdbank.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '   ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo 3. Probando app.david.ch...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://app.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '   ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo 4. Probando localhost.david.ch...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://localhost.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '   ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo 5. Probando dvdbank.ch...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'https://dvdbank.ch' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '   ✅ Status:' $r.StatusCode '- Size:' $r.Content.Length 'bytes' -ForegroundColor Green } catch { Write-Host '   ❌ Error:' $_.Exception.Message -ForegroundColor Red }"
echo.

echo ═══════════════════════════════════════════════════════════
echo   🌐 ABRIENDO URLs EN EL NAVEGADOR
echo ═══════════════════════════════════════════════════════════
echo.

echo Abriendo dvdbank.david.ch en el navegador...
start https://dvdbank.david.ch
timeout /t 2 /nobreak >nul

echo Abriendo app.david.ch en el navegador...
start https://app.david.ch
timeout /t 2 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ URLs abiertas en el navegador
echo ═══════════════════════════════════════════════════════════
echo.
echo Si ves "Site Temporarily Closed" o errores, presiona cualquier
echo tecla para reiniciar todo el sistema...
echo.
pause
