@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   VERIFICACIÓN REPOSITORIO GITHUB
echo ========================================
echo.
echo 📦 Repositorio: https://github.com/davidcano-tb/dvta.ch
echo 🔄 GitHub Actions: https://github.com/davidcano-tb/dvta.ch/actions
echo.
echo ========================================
echo   ESTADO LOCAL DEL REPOSITORIO
echo ========================================
echo.
git status
echo.
echo ========================================
echo   ÚLTIMO COMMIT
echo ========================================
echo.
git log -1 --oneline
echo.
echo ========================================
echo   REMOTE CONFIGURADO
echo ========================================
echo.
git remote -v
echo.
echo ========================================
echo   INSTRUCCIONES
echo ========================================
echo.
echo Para hacer cambios y deploy:
echo   1. Edita los archivos que necesites
echo   2. git add [archivos]
echo   3. git commit -m "descripción"
echo   4. git push
echo.
echo El deploy se ejecutará automáticamente al hacer push
echo.
pause
