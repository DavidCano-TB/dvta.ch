@echo off
echo ========================================
echo  Instalando Graphify para DVDcoin Bank
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

echo Instalando Graphify...
pip install graphifyy

echo.
echo Instalando dependencias de Graphify...
graphify install

echo.
echo ========================================
echo  Graphify instalado correctamente!
echo ========================================
echo.
echo Para generar el grafo de conocimiento:
echo   graphify ./
echo.
echo Los resultados se guardaran en: graphify-out/
echo.
pause
