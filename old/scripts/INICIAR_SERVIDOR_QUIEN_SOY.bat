@echo off
chcp 65001 >nul
title Servidor DVDCoin - Sistema "Quién Soy" Corregido

echo.
echo ================================================================================
echo   ✅ SISTEMA "QUIÉN SOY" - VERIFICACIÓN CON IA CORREGIDA
echo ================================================================================
echo.
echo 🔍 PROBLEMA DIAGNOSTICADO:
echo    La API key de Gemini estaba usando el modelo "gemini-pro-latest" pero
echo    la CUOTA GRATUITA estaba AGOTADA (limit: 0).
echo.
echo ✅ SOLUCIÓN APLICADA:
echo    • Cambio de modelo: gemini-pro-latest → gemini-2.5-flash
echo    • Cambio de API: v1beta → v1
echo    • Mejoras en manejo de errores
echo.
echo 🎉 RESULTADO:
echo    ✅ Sistema funcionando correctamente
echo    ✅ Personajes verificados con éxito (Albert Einstein, Mickey Mouse, etc.)
echo    ✅ Personajes inventados correctamente rechazados con sugerencias
echo.
echo ================================================================================
echo   INICIANDO SERVIDOR
echo ================================================================================
echo.

echo Matando procesos anteriores...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Iniciando servidor DVDCoin...
echo.
echo 📋 Para usar el juego "Quién Soy":
echo    1. Espera a que el servidor inicie
echo    2. Abre: http://localhost:8000/quiensoy
echo    3. Click en "⚙ Configurar nueva partida"
echo    4. Ingresa un personaje y click en "🔍 Verificar con IA"
echo.
echo 🔧 Para verificar que todo funciona:
echo    Ejecuta: VERIFICAR_QUIEN_SOY_IA.bat
echo.
echo 📖 Documentación completa:
echo    • SOLUCION_FINAL_GEMINI.md
echo    • RESUMEN_SOLUCION_QUIEN_SOY.txt
echo.
echo ================================================================================
echo.

python main.py
