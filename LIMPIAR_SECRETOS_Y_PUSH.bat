@echo off
chcp 65001 >nul
echo ========================================
echo   LIMPIEZA DE SECRETOS Y PUSH
echo ========================================
echo.
echo Este script eliminará los archivos con secretos del historial
echo y hará push limpio al repositorio.
echo.
pause

echo [1/3] Eliminando archivos con secretos del historial...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch old/docs/INSTALACION_FINAL_COMPLETADA.txt old/docs/MIGRACION_COMPLETADA.txt old/docs/RESUMEN_MIGRACION.txt" --prune-empty --tag-name-filter cat -- --all

echo.
echo [2/3] Forzando limpieza de referencias...
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo.
echo [3/3] Haciendo push forzado...
git push -u origin master --force

echo.
echo ========================================
echo   ✓ PUSH COMPLETADO
echo ========================================
echo.
echo Tu repositorio: https://github.com/davidcano-tb/dvta.ch
echo GitHub Actions: https://github.com/davidcano-tb/dvta.ch/actions
echo.
pause
