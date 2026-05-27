@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   APLICAR CAMBIOS Y REINICIAR DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/5] Deteniendo servidor actual...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✓ Servidor detenido

echo.
echo [2/5] Creando backup de seguridad...
set BACKUP_DIR=backup_deploy_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul
xcopy *.db "%BACKUP_DIR%\" /Y >nul 2>&1
echo       ✓ Backup creado en %BACKUP_DIR%

echo.
echo [3/5] Verificando cambios en Git...
git status --short
if errorlevel 1 (
    echo       ⚠ No es un repositorio Git
) else (
    echo       ✓ Estado de Git verificado
)

echo.
echo [4/5] Instalando/actualizando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo       ⚠ Error al instalar dependencias
) else (
    echo       ✓ Dependencias actualizadas
)

echo.
echo [5/5] Reiniciando servidor...
start /B python main.py
timeout /t 5 /nobreak >nul

REM Verificar que el servidor está corriendo
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: El servidor no se inició correctamente
    echo       Revisa server.log para más detalles
    pause
    exit /b 1
) else (
    echo       ✓ Servidor reiniciado correctamente
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✓ CAMBIOS APLICADOS EXITOSAMENTE
echo ═══════════════════════════════════════════════════════════
echo.
echo Servidor corriendo en: http://localhost:8000
echo.
echo Para iniciar Cloudflare Tunnel:
echo   OBTENER_URL_PUBLICA.bat
echo.
pause
