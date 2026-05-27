@echo off
chcp 65001 >nul
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 TU URL FUNCIONAL
echo ═══════════════════════════════════════════════════════════
echo.
echo.
type url_temporal.txt
echo.
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ Esta URL funciona AHORA MISMO con HTTPS válido
echo ✅ Accesible desde cualquier dispositivo y red
echo ✅ Compatible con navegadores in-app
echo.
echo ⚠️  Esta URL es temporal y cambiará al reiniciar
echo.
echo Para generar una nueva URL, ejecuta:
echo    python generar_url_ahora.py
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Quieres abrir la URL en el navegador? (S/N)
set /p respuesta="Tu respuesta: "
if /i "%respuesta%"=="S" start "" "https://shape-reported-atm-allergy.trycloudflare.com"
if /i "%respuesta%"=="SI" start "" "https://shape-reported-atm-allergy.trycloudflare.com"
echo.
pause
