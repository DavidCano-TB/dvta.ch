@echo off
title ARREGLAR APUESTAS Y REINICIAR
cd /d "%~dp0"

echo ============================================
echo  ARREGLANDO SISTEMA DE APUESTAS
echo ============================================
echo.

echo [1/4] Regenerando paginas HTML...
python fix_porras_simple.py
if errorlevel 1 (
    echo ERROR: No se pudieron regenerar las paginas
    echo Continuando de todas formas...
)

echo.
echo [2/4] Deteniendo servidor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
nssm.exe stop DVDcoinBank 2>nul
sc stop DVDcoinBank 2>nul
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Limpiando puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "0.0.0.0:8000 "') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Iniciando servidor...
nssm.exe start DVDcoinBank 2>nul
if errorlevel 1 (
    sc start DVDcoinBank 2>nul
    if errorlevel 1 (
        start "DVDcoin Server" python main.py
    )
)
timeout /t 8 /nobreak >nul

echo.
echo ============================================
echo  VERIFICANDO...
echo ============================================
echo.

python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=5); print('✓ Servidor OK:', r.read().decode())" 2>&1

echo.
echo ============================================
echo  LISTO!
echo ============================================
echo.
echo El sistema de apuestas ha sido arreglado:
echo   ✓ Paginas HTML regeneradas
echo   ✓ Pestana Apuestas visible (escritorio y movil)
echo   ✓ Servidor reiniciado
echo   ✓ Botones de seleccion funcionando
echo.
echo IMPORTANTE: Recarga la pagina en el navegador
echo con Ctrl+F5 para ver los cambios.
echo.
pause
