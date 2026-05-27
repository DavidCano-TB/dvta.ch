@echo off
chcp 65001 >nul
title Push a GitHub - DVDBank
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 PUSH A GITHUB - DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script te ayudará a publicar el proyecto en GitHub.
echo.
echo REQUISITOS:
echo   1. Tener una cuenta de GitHub
echo   2. Haber creado el repositorio en GitHub (https://github.com/new)
echo   3. Tener tu usuario de GitHub
echo.
pause
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Configurar remote de GitHub
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p GITHUB_USER="Ingresa tu usuario de GitHub: "

if "%GITHUB_USER%"=="" (
    echo.
    echo ❌ Error: Debes ingresar tu usuario de GitHub
    pause
    exit /b 1
)

echo.
echo Configurando remote para: https://github.com/%GITHUB_USER%/dvdbank.git
echo.

git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/dvdbank.git

if %errorlevel% neq 0 (
    echo ❌ Error al configurar el remote
    pause
    exit /b 1
)

echo ✅ Remote configurado correctamente
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Verificar remote
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

git remote -v
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Push a GitHub
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ⚠️  IMPORTANTE: Necesitarás autenticarte con GitHub
echo.
echo    • Usuario: %GITHUB_USER%
echo    • Password: Tu TOKEN PERSONAL (NO tu contraseña)
echo.
echo    Para crear un token:
echo    1. Ve a: https://github.com/settings/tokens
echo    2. Clic en [Generate new token] → [Generate new token (classic)]
echo    3. Nombre: DVDBank Push Token
echo    4. Scopes: Marca "repo"
echo    5. Clic en [Generate token]
echo    6. Copia el token y úsalo como contraseña
echo.
pause
echo.

echo Haciendo push a GitHub...
echo.

git push -u origin master

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ✅ PUSH COMPLETADO EXITOSAMENTE
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Tu proyecto está ahora en GitHub:
    echo   https://github.com/%GITHUB_USER%/dvdbank
    echo.
    echo Verifica que todo esté correcto:
    echo   • README.md visible
    echo   • 7 commits en el historial
    echo   • Todos los archivos presentes
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   ❌ ERROR EN EL PUSH
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Posibles causas:
    echo   • El repositorio no existe en GitHub
    echo   • Credenciales incorrectas
    echo   • No tienes permisos de escritura
    echo.
    echo Soluciones:
    echo   1. Verifica que creaste el repositorio en GitHub
    echo   2. Verifica tu usuario: %GITHUB_USER%
    echo   3. Usa un token personal, no tu contraseña
    echo   4. Verifica que el token tenga permisos "repo"
    echo.
)

pause
