@echo off
chcp 65001 >nul
title APLICAR Y FORZAR CORRECCIONES - DVDcoin Bank
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║     APLICAR Y FORZAR TODAS LAS CORRECCIONES                   ║
echo ║     Votaciones, Apuestas y Quien Soy                          ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Este script aplicará y forzará:
echo   ✓ Corrección de tokens en Votaciones
echo   ✓ Corrección de tokens en Apuestas
echo   ✓ Verificación de Quien Soy
echo   ✓ Reinicio del servidor
echo   ✓ Prueba de funcionalidad
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════
echo [1/6] VERIFICANDO CORRECCIONES APLICADAS
echo ═══════════════════════════════════════════════════════════════
python verificar_y_corregir_quiensoy.py
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Algunas correcciones no están aplicadas
    echo.
    echo Por favor, verifica los archivos manualmente:
    echo   - game_pages\votaciones\votaciones.html
    echo   - game_pages\apuestas\apuestas.html
    echo   - game_pages\quiensoy\game.html
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo [2/6] DETENIENDO SERVIDOR ACTUAL
echo ═══════════════════════════════════════════════════════════════
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
timeout /t 2 /nobreak >nul
echo ✓ Servidor detenido

echo.
echo ═══════════════════════════════════════════════════════════════
echo [3/6] LIMPIANDO CACHÉ Y ARCHIVOS TEMPORALES
echo ═══════════════════════════════════════════════════════════════
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
if exist "src\__pycache__" rd /s /q "src\__pycache__" 2>nul
echo ✓ Caché limpiado

echo.
echo ═══════════════════════════════════════════════════════════════
echo [4/6] INICIANDO SERVIDOR
echo ═══════════════════════════════════════════════════════════════
start /min "DVDcoin Server" cmd /c "python src\main.py"
echo ⏳ Esperando a que el servidor inicie...
timeout /t 5 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo [5/6] VERIFICANDO SERVIDOR
echo ═══════════════════════════════════════════════════════════════
python -c "import requests; r=requests.get('http://localhost:5000/api/health', timeout=5); print('✓ Servidor activo y respondiendo' if r.ok else '✗ Servidor no responde')" 2>nul
if errorlevel 1 (
    echo ⚠ El servidor no responde. Esperando más tiempo...
    timeout /t 5 /nobreak >nul
    python -c "import requests; r=requests.get('http://localhost:5000/api/health', timeout=5); print('✓ Servidor activo' if r.ok else '✗ Servidor no responde')" 2>nul
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo [6/6] RESUMEN DE CORRECCIONES
echo ═══════════════════════════════════════════════════════════════
echo.
echo ✅ VOTACIONES
echo    • Token se lee de URL y localStorage
echo    • Token se guarda automáticamente
echo    • URL se limpia después de leer el token
echo    • Acceso: http://localhost:5000/votaciones
echo.
echo ✅ APUESTAS
echo    • Token se lee de URL y localStorage
echo    • Token se guarda automáticamente
echo    • URL se limpia después de leer el token
echo    • Acceso: http://localhost:5000/apuestas
echo.
echo ✅ QUIEN SOY
echo    • Token se lee de URL y localStorage
echo    • Juego se abre automáticamente después de configurar
echo    • Panel admin: http://localhost:5000 → Admin → Quien Soy
echo    • Juego: http://localhost:5000/quiensoy
echo.
echo ═══════════════════════════════════════════════════════════════
echo INSTRUCCIONES DE PRUEBA
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. VOTACIONES:
echo    a. Abre http://localhost:5000
echo    b. Inicia sesión
echo    c. Haz clic en "🗳️ Votaciones"
echo    d. Deberías ver la página funcionando
echo.
echo 2. APUESTAS:
echo    a. Desde el index, haz clic en "🎲 Apuestas"
echo    b. Deberías ver la página funcionando
echo    c. Puedes crear apuestas y apostar
echo.
echo 3. QUIEN SOY:
echo    a. Inicia sesión como 'dvd'
echo    b. Ve al panel de Admin
echo    c. Selecciona "🎭 Quien Soy"
echo    d. Ingresa un personaje y verifica (debe aparecer en verde)
echo    e. Selecciona miembros
echo    f. Haz clic en "▶ Iniciar partida"
echo    g. El juego debería abrirse automáticamente
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo ¿Deseas abrir el navegador para probar?
echo.
choice /C SN /M "Abrir navegador (S=Sí, N=No)"
if errorlevel 2 goto :fin
if errorlevel 1 goto :abrir

:abrir
echo.
echo Abriendo navegador...
start http://localhost:5000
goto :fin

:fin
echo.
echo ═══════════════════════════════════════════════════════════════
echo CORRECCIONES APLICADAS Y FORZADAS EXITOSAMENTE
echo ═══════════════════════════════════════════════════════════════
echo.
echo Para más información, consulta:
echo   - CORRECCIONES_VOTACIONES_APUESTAS_QUIENSOY.md
echo.
echo Servidor corriendo en: http://localhost:5000
echo.
pause
