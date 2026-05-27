@echo off
chcp 65001 >nul
cls
echo ========================================
echo   AGREGAR USUARIO A OPO Y REINICIAR
echo ========================================
echo.

if "%1"=="" (
    echo Uso: AGREGAR_USUARIO_Y_REINICIAR.bat ^<nombre_usuario^>
    echo.
    echo Ejemplo: AGREGAR_USUARIO_Y_REINICIAR.bat dvd
    echo.
    echo Usuarios actuales con acceso OPO:
    python -c "import sqlite3; conn = sqlite3.connect('data/rights.db'); rows = conn.execute('SELECT username FROM opo_players ORDER BY username').fetchall(); [print(f'  - {r[0]}') for r in rows]; conn.close()"
    echo.
    pause
    exit /b 1
)

echo [1/3] Agregando usuario: %1
echo.
python add_opo_user.py %1

if errorlevel 1 (
    echo.
    echo ❌ Error al agregar usuario
    pause
    exit /b 1
)

echo.
echo [2/3] Deteniendo servidor...
echo.

REM Buscar y matar procesos de Python que ejecutan main.py
tasklist /FI "IMAGENAME eq python.exe" /FO LIST 2>nul | findstr /C:"PID:" > temp_kill_python.txt
for /f "tokens=2" %%a in (temp_kill_python.txt) do (
    taskkill /F /PID %%a >nul 2>&1
)
del temp_kill_python.txt 2>nul

REM Esperar un momento
timeout /t 2 /nobreak >nul

echo.
echo [3/3] Iniciando servidor...
echo.

REM Iniciar el servidor en una nueva ventana
start "DVDcoin Server" cmd /k "python main.py"

echo.
echo ========================================
echo   ✅ COMPLETADO
echo.
echo   Usuario agregado: %1
echo   Servidor reiniciado
echo.
echo   Ahora puedes acceder a /opo
echo ========================================
echo.
timeout /t 3 /nobreak
