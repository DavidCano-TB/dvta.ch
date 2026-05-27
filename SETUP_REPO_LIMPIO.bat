@echo off
chcp 65001 >nul
echo ========================================
echo   CREAR REPOSITORIO LIMPIO
echo ========================================
echo.
echo Este script creará un repositorio completamente nuevo
echo sin historial antiguo ni secretos.
echo.
pause

echo [1/8] Haciendo backup del .git actual...
if exist .git.backup rmdir /s /q .git.backup
move .git .git.backup

echo.
echo [2/8] Inicializando nuevo repositorio...
git init

echo.
echo [3/8] Añadiendo todos los archivos actuales...
git add -A

echo.
echo [4/8] Creando commit inicial limpio...
git commit -m "Initial commit: DVDcoin Bank - Sistema completo funcionando"

echo.
echo [5/8] Renombrando rama a master...
git branch -M master

echo.
echo [6/8] Añadiendo repositorio remoto...
git remote add origin https://github.com/davidcano-tb/dvta.ch.git

echo.
echo [7/8] Haciendo push inicial...
git push -u origin master --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [8/8] Limpiando backup...
    rmdir /s /q .git.backup
    
    echo.
    echo ========================================
    echo   ✓ REPOSITORIO CREADO CON ÉXITO
    echo ========================================
    echo.
    echo Tu repositorio: https://github.com/davidcano-tb/dvta.ch
    echo GitHub Actions: https://github.com/davidcano-tb/dvta.ch/actions
    echo.
    echo El workflow de CI/CD se ejecutará automáticamente.
) else (
    echo.
    echo [ERROR] El push falló
    echo.
    echo Restaurando .git original...
    rmdir /s /q .git
    move .git.backup .git
    echo Repositorio restaurado al estado anterior.
)

echo.
pause
