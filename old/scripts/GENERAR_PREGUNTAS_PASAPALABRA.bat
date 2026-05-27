@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   GENERADOR DE PREGUNTAS PASAPALABRA
echo ═══════════════════════════════════════════════════════════
echo.
echo Generando archivo con 50 preguntas por letra...
echo.

python generar_preguntas_completo.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Archivo generado exitosamente
    echo.
    echo Ubicación: static\pasapalabra\preguntas.json
    echo.
) else (
    echo.
    echo ✗ Error al generar el archivo
    echo.
)

pause
