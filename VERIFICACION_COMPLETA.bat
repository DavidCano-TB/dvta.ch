@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     VERIFICACIÓN COMPLETA - REPOSITORIO DVTA.CH            ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/6] Verificando Git instalado...
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git está instalado
    git --version
) else (
    echo ❌ Git NO está instalado
    goto :error
)
echo.

echo [2/6] Verificando repositorio local...
if exist ".git" (
    echo ✅ Repositorio Git inicializado
) else (
    echo ❌ No se encontró repositorio Git
    goto :error
)
echo.

echo [3/6] Verificando remote configurado...
git remote -v | findstr "dvta.ch" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Remote configurado correctamente
    git remote -v
) else (
    echo ❌ Remote NO configurado
    goto :error
)
echo.

echo [4/6] Verificando estado del repositorio...
git status
echo.

echo [5/6] Verificando último commit...
git log -1 --oneline
echo.

echo [6/6] Verificando workflow de CI/CD...
if exist ".github\workflows\deploy.yml" (
    echo ✅ Workflow de deploy configurado
) else (
    echo ❌ Workflow NO encontrado
    goto :error
)
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║                  ✅ TODO ESTÁ CORRECTO                     ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 REPOSITORIO GITHUB
echo    https://github.com/davidcano-tb/dvta.ch
echo.
echo 🔄 GITHUB ACTIONS (CI/CD)
echo    https://github.com/davidcano-tb/dvta.ch/actions
echo.
echo 📝 COMMITS
echo    https://github.com/davidcano-tb/dvta.ch/commits/master
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  CÓMO FUNCIONA EL DEPLOY AUTOMÁTICO                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. Editas archivos en tu proyecto
echo 2. git add [archivos]
echo 3. git commit -m "descripción"
echo 4. git push
echo 5. 🚀 GitHub Actions ejecuta automáticamente:
echo    - Instala Python 3.11
echo    - Instala dependencias (requirements.txt)
echo    - Verifica sintaxis
echo    - Crea directorios necesarios
echo    - Ejecuta tests
echo    - Notifica resultado
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  SCRIPTS DISPONIBLES                                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo • ABRIR_GIT_GRAFICO.bat    - Abre herramienta gráfica de Git
echo • VERIFICAR_GITHUB.bat     - Verifica estado del repositorio
echo • GUIA_COMPLETA_GIT.md     - Guía completa de uso
echo • ARRANCAR.bat             - Inicia el servidor DVDcoin Bank
echo.
goto :end

:error
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║                  ❌ ERROR DETECTADO                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Por favor, revisa los mensajes de error anteriores.
echo.

:end
pause
