@echo off
echo ========================================
echo PRUEBA DE VIDEO GRUPAL
echo ========================================
echo.
echo Este script te ayudara a probar el video grupal corregido.
echo.
echo PASOS:
echo 1. Asegurate de que el servidor este corriendo
echo 2. Abre el navegador en: http://localhost:8000
echo 3. Inicia sesion con un usuario
echo 4. Ve a Videollamadas
echo 5. Crea una sala
echo 6. Abre otra ventana de incognito
echo 7. Inicia sesion con otro usuario
echo 8. Unete a la misma sala
echo 9. Verifica que se vean ambos videos en pantalla partida
echo.
echo DIAGNOSTICO:
echo - Abre DevTools (F12) en ambos navegadores
echo - Busca logs: [PC] ontrack EVENT
echo - Busca logs: [STREAM] Attaching stream
echo - Ejecuta en consola: window.videoDiagnostic()
echo.
echo ========================================
echo.
pause
start http://localhost:8000
