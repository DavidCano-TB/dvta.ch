@echo off
chcp 65001 >nul
echo ========================================
echo   CONFIGURACIÓN AUTOMÁTICA DE DEPLOY
echo   Repositorio: dvta.ch
echo ========================================
echo.

REM Verificar si gh está instalado
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] GitHub CLI no está instalado.
    echo.
    echo Por favor, instala GitHub CLI desde:
    echo https://cli.github.com/
    echo.
    echo O crea el repositorio manualmente en:
    echo https://github.com/new
    echo.
    echo Nombre del repositorio: dvta.ch
    echo.
    pause
    exit /b 1
)

echo [1/5] Verificando autenticación de GitHub...
gh auth status
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Necesitas autenticarte en GitHub
    echo Ejecutando: gh auth login
    echo.
    gh auth login
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Autenticación fallida
        pause
        exit /b 1
    )
)

echo.
echo [2/5] Creando repositorio 'dvta.ch' en GitHub...
gh repo create dvta.ch --public --source=. --remote=origin --description="DVDcoin Bank - Sistema de gestión bancaria virtual"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] El repositorio puede ya existir o hubo un error
    echo Intentando añadir remote manualmente...
    git remote add origin https://github.com/%USERNAME%/dvta.ch.git
)

echo.
echo [3/5] Añadiendo archivos al staging...
git add main.py static/index.html CONFIGURACION_EMAIL_DVTA_CH.txt CONFIGURAR_EMAIL_DVTA.bat LEEME_PRIMERO.txt

echo.
echo [4/5] Creando commit...
git commit -m "Configuración completa de email y deploy automático para dvta.ch"

echo.
echo [5/5] Haciendo push al repositorio...
git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ DEPLOY COMPLETADO CON ÉXITO
    echo ========================================
    echo.
    echo Tu repositorio está en:
    gh repo view --web
    echo.
    echo Para ver el estado del deploy:
    echo https://github.com/TU_USUARIO/dvta.ch/actions
    echo.
) else (
    echo.
    echo [ERROR] Hubo un problema con el push
    echo Verifica tu conexión y permisos
)

echo.
pause
