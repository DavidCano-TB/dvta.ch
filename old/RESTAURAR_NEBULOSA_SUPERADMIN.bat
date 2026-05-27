@echo off
echo ========================================
echo RESTAURAR PRIVILEGIOS DE NEBULOSA
echo ========================================
echo.
echo Este script restaurara los privilegios de superadmin
echo para el usuario "nebulosa".
echo.
echo Privilegios que se restauraran:
echo - Superadmin completo
echo - Acceso permanente a OPO
echo - Gestion de usuarios y administradores
echo - Gestion de conexiones
echo.
pause
echo.
echo Ejecutando script de restauracion...
python restore_nebulosa_superadmin.py
echo.
echo ========================================
echo CAMBIOS APLICADOS
echo ========================================
echo.
echo Los cambios en la base de datos se han aplicado.
echo.
echo IMPORTANTE: Debes reiniciar el servidor para que
echo los cambios surtan efecto completamente.
echo.
echo Pasos siguientes:
echo 1. Detener el servidor actual (Ctrl+C)
echo 2. Iniciar el servidor nuevamente
echo 3. Iniciar sesion como "nebulosa"
echo 4. Verificar acceso a panel de administracion
echo.
pause
