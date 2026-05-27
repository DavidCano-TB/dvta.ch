@echo off
chcp 65001 >nul
color 0A
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║           VERIFICACIÓN Y APLICACIÓN DE CORRECCIONES                ║
echo ║                                                                    ║
echo ║  Este script aplicará todas las correcciones necesarias:          ║
echo ║  • Tablas de votaciones                                            ║
echo ║  • Tablas de apuestas                                              ║
echo ║  • Corrección de "Quien Soy" (solo Sí/No)                          ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo.
pause

cls
echo ════════════════════════════════════════════════════════════════════
echo  PASO 1: Aplicando correcciones...
echo ════════════════════════════════════════════════════════════════════
echo.

python APLICAR_CORRECCIONES_COMPLETAS.py

echo.
echo.
echo ════════════════════════════════════════════════════════════════════
echo  CORRECCIONES APLICADAS
echo ════════════════════════════════════════════════════════════════════
echo.
echo  ✓ Tablas de votaciones creadas
echo  ✓ Tablas de apuestas verificadas
echo  ✓ Código de "Quien Soy" corregido
echo.
echo ════════════════════════════════════════════════════════════════════
echo  IMPORTANTE: REINICIAR EL SERVIDOR
echo ════════════════════════════════════════════════════════════════════
echo.
echo  Para que los cambios tomen efecto, debes:
echo.
echo  1. Detener el servidor actual (DETENER_TODO.bat)
echo  2. Iniciar el servidor nuevamente (ARRANCAR.bat)
echo.
echo ════════════════════════════════════════════════════════════════════
echo  VERIFICACIÓN DESPUÉS DEL REINICIO
echo ════════════════════════════════════════════════════════════════════
echo.
echo  • /votaciones - Debe cargar sin errores
echo  • /apuestas - Debe funcionar correctamente
echo  • Quien Soy - Solo debe responder "Sí" o "No"
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

pause
