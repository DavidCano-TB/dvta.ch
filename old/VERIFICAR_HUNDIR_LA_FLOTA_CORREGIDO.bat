@echo off
echo ========================================
echo VERIFICACION: HUNDIR LA FLOTA CORREGIDO
echo ========================================
echo.
echo CORRECCIONES APLICADAS:
echo [X] Fases corregidas (placement/battle)
echo [X] Acciones WebSocket ampliadas
echo [X] Filtrado de barcos con count=0
echo [X] Sincronizacion de estado mejorada
echo [X] Logs de debugging anadidos
echo.
echo ========================================
echo PASOS DE VERIFICACION:
echo ========================================
echo.
echo 1. ABRIR DEVTOOLS (F12)
echo    - Ir a pestana Console
echo    - Dejar abierta para ver logs
echo.
echo 2. INICIAR SERVIDOR
echo    - Ejecutar: ABRIR_APUESTAS.bat
echo    - Esperar mensaje "Application startup complete"
echo.
echo 3. LOGIN COMO ADMIN
echo    - Abrir: http://localhost:8000
echo    - Usuario: dvd
echo    - Password: [tu password]
echo.
echo 4. CONFIGURAR PARTIDA
echo    - Admin Panel ^> Hundir la Flota
echo    - Configurar barcos:
echo      * Portaaviones: 2
echo      * Acorazado: 1
echo      * Crucero: 1
echo      * Submarino: 0
echo      * Destructor: 2
echo    - Anadir 2 jugadores
echo    - Click "Iniciar partida"
echo.
echo 5. VERIFICAR LOGS EN CONSOLE
echo    Deben aparecer:
echo    [OK] "Configuracion de barcos: {...}"
echo    [OK] "Respuesta del servidor: {...}"
echo.
echo 6. EN VENTANA DE JUEGO
echo    Verificar en Console:
echo    [OK] "Renderizando juego - Fase: placement"
echo    [OK] "Renderizando botones de barcos: {...}"
echo    [OK] "Botones renderizados: 4"
echo.
echo 7. VERIFICAR INTERFAZ
echo    [OK] Aparece mensaje "Fase de preparacion"
echo    [OK] Aparecen 4 botones de barcos
echo    [OK] Contadores correctos: [2], [1], [1], [2]
echo    [OK] NO aparece boton de Submarino
echo.
echo 8. PROBAR COLOCACION
echo    - Click en "Horizontal"
echo    - Click en "Portaaviones (5) [2]"
echo    - Click en tablero
echo    Verificar:
echo    [OK] Barco se coloca horizontalmente
echo    [OK] Contador cambia a [1]
echo    [OK] Mensaje "Barco colocado"
echo.
echo 9. PROBAR ROTACION
echo    - Click en "Vertical"
echo    - Click en "Acorazado (4) [1]"
echo    - Click en tablero
echo    Verificar:
echo    [OK] Barco se coloca verticalmente
echo    [OK] Contador cambia a [0]
echo    [OK] Boton se grisea
echo.
echo 10. PROBAR MOVER
echo     - Click en barco ya colocado
echo     - Click en "Mover"
echo     - Click en nueva posicion
echo     Verificar:
echo     [OK] Barco se resalta en dorado
echo     [OK] Aparece boton "Mover"
echo     [OK] Barco se mueve a nueva posicion
echo     [OK] Mensaje "Barco movido correctamente"
echo.
echo 11. PROBAR BORRAR
echo     - Click en barco
echo     - Click en "Borrar"
echo     Verificar:
echo     [OK] Barco desaparece
echo     [OK] Contador aumenta
echo     [OK] Mensaje "Barco eliminado"
echo.
echo 12. PROBAR VALIDAR
echo     - Colocar todos los barcos
echo     Verificar:
echo     [OK] Boton "Validar" se habilita
echo     [OK] Mensaje "Todos los barcos colocados"
echo     - Click en "Validar"
echo     Verificar:
echo     [OK] Mensaje "Listo - Esperando..."
echo     [OK] Controles desaparecen
echo.
echo ========================================
echo ERRORES COMUNES:
echo ========================================
echo.
echo ERROR: No aparecen botones de barcos
echo SOLUCION: Verificar en Console:
echo   - "Renderizando botones de barcos"
echo   - Debe tener datos, no vacio {}
echo.
echo ERROR: No se puede colocar barcos
echo SOLUCION: Verificar en Console:
echo   - Fase debe ser "placement"
echo   - shipConfig debe tener datos
echo.
echo ERROR: Boton Validar no se habilita
echo SOLUCION: Verificar que todos los
echo   contadores esten en [0]
echo.
echo ========================================
echo LOGS ESPERADOS EN CONSOLE:
echo ========================================
echo.
echo Admin Panel:
echo   ^> Configuracion de barcos: {carrier: {...}, ...}
echo   ^> Respuesta del servidor: {ok: true, ...}
echo.
echo Ventana de Juego:
echo   ^> Mensaje recibido: {type: "state", ...}
echo   ^> Renderizando juego - Fase: placement
echo   ^> Renderizando botones de barcos: {...}
echo   ^> Botones renderizados: 4
echo.
echo ========================================
pause
