@echo off
chcp 65001 >nul
title Verificar Sistema "Quién Soy" con IA

echo.
echo ================================================================================
echo   VERIFICACIÓN DEL SISTEMA "QUIÉN SOY" CON IA
echo ================================================================================
echo.
echo Este script verificará que el sistema de verificación de personajes
echo con Gemini AI está funcionando correctamente.
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul

echo.
echo ================================================================================
echo   EJECUTANDO TESTS DE VERIFICACIÓN
echo ================================================================================
echo.

python TEST_GEMINI_QUIEN_SOY.py

echo.
echo ================================================================================
echo   VERIFICACIÓN COMPLETADA
echo ================================================================================
echo.
echo Si todas las pruebas pasaron (✅ PASS), el sistema está funcionando.
echo.
echo Para usar el juego:
echo   1. Ejecuta: python main.py
echo   2. Abre en navegador: http://localhost:8000/quiensoy
echo   3. Click en "⚙ Configurar nueva partida"
echo   4. Ingresa un personaje y click en "🔍 Verificar con IA"
echo.
echo Para ver la documentación completa, abre: SOLUCION_FINAL_GEMINI.md
echo.
pause
