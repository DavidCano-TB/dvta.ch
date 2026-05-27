@echo off
chcp 65001 >nul
echo ========================================
echo   AGREGAR USUARIO A OPO
echo ========================================
echo.

if "%1"=="" (
    echo Uso: AGREGAR_USUARIO_OPO.bat ^<nombre_usuario^>
    echo.
    echo Ejemplo: AGREGAR_USUARIO_OPO.bat nina
    echo.
    echo Usuarios actuales con acceso OPO:
    python -c "import sqlite3; conn = sqlite3.connect('data/rights.db'); rows = conn.execute('SELECT username FROM opo_players ORDER BY username').fetchall(); [print(f'  - {r[0]}') for r in rows]; conn.close()"
    echo.
    pause
    exit /b 1
)

echo Agregando usuario: %1
echo.
python add_opo_user.py %1

echo.
echo ========================================
echo   IMPORTANTE: Reinicia el servidor
echo   para que los cambios tengan efecto
echo ========================================
echo.
pause
