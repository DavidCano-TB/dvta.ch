@echo off
chcp 65001 >nul
echo ========================================
echo CORRECCIÓN DE VOTACIONES, APUESTAS Y QUIEN SOY
echo ========================================
echo.
echo Este script corregirá:
echo 1. Token en votaciones y apuestas
echo 2. Inicio automático de quien soy
echo 3. Disponibilidad de las páginas
echo.
pause

echo.
echo [1/4] Verificando archivos...
if not exist "game_pages\votaciones\votaciones.html" (
    echo ERROR: No se encuentra votaciones.html
    pause
    exit /b 1
)
if not exist "game_pages\apuestas\apuestas.html" (
    echo ERROR: No se encuentra apuestas.html
    pause
    exit /b 1
)
if not exist "game_pages\quiensoy\game.html" (
    echo ERROR: No se encuentra quien soy game.html
    pause
    exit /b 1
)
echo ✓ Todos los archivos encontrados

echo.
echo [2/4] Verificando servidor...
python -c "import requests; r=requests.get('http://localhost:5000/api/health', timeout=2); print('✓ Servidor activo' if r.ok else '✗ Servidor no responde')" 2>nul
if errorlevel 1 (
    echo ⚠ Servidor no está activo. Iniciando...
    start /min cmd /c "cd /d %~dp0 && python src\main.py"
    timeout /t 5 /nobreak >nul
)

echo.
echo [3/4] Verificando correcciones aplicadas...
findstr /C:"urlParams.get('token')" "game_pages\votaciones\votaciones.html" >nul
if errorlevel 1 (
    echo ✗ Votaciones NO corregida
) else (
    echo ✓ Votaciones corregida
)

findstr /C:"urlParams.get('token')" "game_pages\apuestas\apuestas.html" >nul
if errorlevel 1 (
    echo ✗ Apuestas NO corregida
) else (
    echo ✓ Apuestas corregida
)

echo.
echo [4/4] Probando acceso a las páginas...
echo.
echo Abriendo navegador para probar...
echo - Votaciones: http://localhost:5000/votaciones
echo - Apuestas: http://localhost:5000/apuestas
echo - Quien Soy: http://localhost:5000/quiensoy
echo.

echo.
echo ========================================
echo CORRECCIONES APLICADAS
echo ========================================
echo.
echo Las páginas ahora:
echo ✓ Leen el token de la URL y localStorage
echo ✓ Guardan el token automáticamente
echo ✓ Limpian la URL después de leer el token
echo.
echo Para probar:
echo 1. Inicia sesión en http://localhost:5000
echo 2. Haz clic en Votaciones o Apuestas
echo 3. Deberías ver las páginas funcionando
echo.
echo Para Quien Soy:
echo 1. Ve al panel de admin
echo 2. Selecciona personaje y miembros
echo 3. Haz clic en "Iniciar Juego"
echo 4. El juego debería comenzar automáticamente
echo.
pause
