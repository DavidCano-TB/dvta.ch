@echo off
echo ========================================
echo  Generando Grafo de Conocimiento
echo  DVDcoin Bank - Graphify
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Analizando proyecto con Graphify...
echo Esto puede tardar varios minutos...
echo.

graphify ./

echo.
echo ========================================
echo  Grafo generado!
echo ========================================
echo.
echo Archivos generados en: graphify-out/
echo   - graph.html (visualizacion interactiva)
echo   - GRAPH_REPORT.md (reporte de analisis)
echo   - graph.json (grafo consultable)
echo.
echo Abriendo visualizacion...
start graphify-out\graph.html

pause
