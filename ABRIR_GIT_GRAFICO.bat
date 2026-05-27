@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ABRIR GESTIÓN GRÁFICA DE GIT
echo ========================================
echo.
echo Intentando abrir herramientas gráficas de Git...
echo.

REM Intentar abrir Git GUI (incluido con Git)
where git-gui >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Abriendo Git GUI...
    start git-gui
    goto :end
)

REM Intentar abrir GitHub Desktop
if exist "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe" (
    echo ✓ Abriendo GitHub Desktop...
    start "" "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe"
    goto :end
)

REM Intentar abrir GitKraken
if exist "%LOCALAPPDATA%\gitkraken\gitkraken.exe" (
    echo ✓ Abriendo GitKraken...
    start "" "%LOCALAPPDATA%\gitkraken\gitkraken.exe"
    goto :end
)

REM Intentar abrir VS Code
where code >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Abriendo Visual Studio Code...
    code .
    goto :end
)

REM Si no se encuentra ninguna herramienta
echo.
echo ⚠️  No se encontró ninguna herramienta gráfica de Git instalada.
echo.
echo Opciones disponibles:
echo.
echo 1. Git GUI (incluido con Git)
echo    Ejecuta: git gui
echo.
echo 2. GitHub Desktop (Recomendado)
echo    Descarga: https://desktop.github.com/
echo.
echo 3. GitKraken
echo    Descarga: https://www.gitkraken.com/
echo.
echo 4. Visual Studio Code
echo    Descarga: https://code.visualstudio.com/
echo.
echo Después de instalar cualquiera, ejecuta este script de nuevo.
echo.

:end
echo.
echo ========================================
echo   INFORMACIÓN DEL REPOSITORIO
echo ========================================
echo.
echo 📦 Repositorio: https://github.com/davidcano-tb/dvta.ch
echo 🔄 GitHub Actions: https://github.com/davidcano-tb/dvta.ch/actions
echo 📂 Directorio local: %CD%
echo.
pause
