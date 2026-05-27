@echo off
echo ========================================
echo APLICAR CAMBIOS - NEBULOSA A USUARIO NORMAL
echo ========================================
echo.
echo Este script aplicara los cambios en la base de datos
echo para convertir a nebulosa en un usuario normal.
echo.
echo IMPORTANTE: Asegurate de que el servidor este DETENIDO
echo antes de continuar.
echo.
pause

echo.
echo Ejecutando script de Python...
python remove_nebulosa_privileges.py

echo.
echo ========================================
echo CAMBIOS APLICADOS
echo ========================================
echo.
echo Ahora puedes reiniciar el servidor con:
echo   python -m uvicorn src.main:app --reload
echo.
echo O usando el script ARRANCAR.bat
echo.
pause
