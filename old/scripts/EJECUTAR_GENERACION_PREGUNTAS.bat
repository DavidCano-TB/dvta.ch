@echo off
cd /d c:\dvdcoin
echo Generando preguntas de Pasapalabra...
python generar_preguntas_pasapalabra.py > generacion_log.txt 2>&1
echo.
echo Proceso completado. Revisa generacion_log.txt para ver el resultado.
type generacion_log.txt
pause
