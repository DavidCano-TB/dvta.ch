@echo off
chcp 65001 >nul
echo ========================================
echo   CONFIGURACIÓN MANUAL DE REPOSITORIO
echo   Repositorio: dvta.ch
echo ========================================
echo.
echo PASO 1: Crea el repositorio en GitHub
echo ----------------------------------------
echo 1. Ve a: https://github.com/new
echo 2. Repository name: dvta.ch
echo 3. Description: DVDcoin Bank - Sistema de gestión bancaria virtual
echo 4. Visibility: Public o Private (tu elección)
echo 5. NO marques ninguna opción adicional
echo 6. Haz clic en "Create repository"
echo.
echo Presiona cualquier tecla cuando hayas creado el repositorio...
pause >nul

echo.
echo PASO 2: Ingresa tu nombre de usuario de GitHub
echo ----------------------------------------
set /p GITHUB_USER="Tu usuario de GitHub: "

echo.
echo [1/4] Configurando repositorio remoto...
git remote add origin https://github.com/%GITHUB_USER%/dvta.ch.git

echo.
echo [2/4] Añadiendo archivos al staging...
git add main.py static/index.html CONFIGURACION_EMAIL_DVTA_CH.txt CONFIGURAR_EMAIL_DVTA.bat LEEME_PRIMERO.txt

echo.
echo [3/4] Creando commit...
git commit -m "Configuración completa de email y deploy automático para dvta.ch"

echo.
echo [4/4] Haciendo push al repositorio...
git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ DEPLOY COMPLETADO CON ÉXITO
    echo ========================================
    echo.
    echo Tu repositorio está en:
    echo https://github.com/%GITHUB_USER%/dvta.ch
    echo.
    echo Para ver el estado del deploy:
    echo https://github.com/%GITHUB_USER%/dvta.ch/actions
    echo.
    echo El workflow de GitHub Actions se ejecutará automáticamente
    echo y verificará:
    echo   ✓ Instalación de dependencias
    echo   ✓ Sintaxis de Python
    echo   ✓ Estructura de base de datos
    echo   ✓ Tests
    echo.
) else (
    echo.
    echo [ERROR] Hubo un problema con el push
    echo.
    echo Posibles causas:
    echo - Usuario de GitHub incorrecto
    echo - Repositorio no creado
    echo - Problemas de autenticación
    echo.
    echo Intenta ejecutar manualmente:
    echo   git push -u origin master
)

echo.
pause
