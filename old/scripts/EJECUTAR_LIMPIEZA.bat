@echo off
echo ======================================================================
echo   LIMPIEZA AUTOMATICA DE DVDCOIN
echo ======================================================================
echo.
echo   Se liberaran aproximadamente 785 MB
echo   Se creara un backup antes de eliminar
echo.
echo   Presiona Ctrl+C para cancelar o
pause

python LIMPIEZA_SEGURA.py < nul

echo.
echo ======================================================================
echo   LIMPIEZA COMPLETADA
echo ======================================================================
echo.
pause
