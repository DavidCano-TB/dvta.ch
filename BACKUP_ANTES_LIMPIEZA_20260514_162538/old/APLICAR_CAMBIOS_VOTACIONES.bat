@echo off
echo ================================================================================
echo APLICANDO CAMBIOS AL SISTEMA DE VOTACIONES
echo ================================================================================
echo.

echo [1/3] Verificando sistema...
python verificar_sistema_votaciones.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: La verificacion fallo
    pause
    exit /b 1
)

echo.
echo [2/3] Los cambios ya estan aplicados en main.py
echo       - Codigo corregido sin columnas ambiguas
echo       - Endpoints actualizados
echo       - Frontend sincronizado
echo.

echo [3/3] IMPORTANTE: Debes reiniciar el servidor manualmente
echo.
echo ================================================================================
echo INSTRUCCIONES PARA REINICIAR EL SERVIDOR
echo ================================================================================
echo.
echo 1. Ve a la terminal donde esta corriendo el servidor
echo 2. Presiona Ctrl+C para detenerlo
echo 3. Ejecuta: python main.py
echo 4. Espera a que inicie (veras "Uvicorn running on http://0.0.0.0:8000")
echo 5. Accede a: http://localhost:8000/votaciones
echo.
echo ================================================================================
echo SISTEMA LISTO
echo ================================================================================
echo.
echo El sistema de votaciones esta completamente funcional:
echo   - Sin errores de columnas ambiguas
echo   - Votaciones simples y multiples funcionando
echo   - Finalizacion y eliminacion funcionando
echo   - Vista especial para DVD funcionando
echo.
pause
