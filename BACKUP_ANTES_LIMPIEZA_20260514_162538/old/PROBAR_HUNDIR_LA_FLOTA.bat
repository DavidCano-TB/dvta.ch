@echo off
echo ========================================
echo PRUEBA: HUNDIR LA FLOTA - MEJORAS
echo ========================================
echo.
echo PASOS PARA PROBAR:
echo.
echo 1. INICIAR SERVIDOR
echo    - Ejecutar: ABRIR_APUESTAS.bat
echo    - Esperar a que el servidor este listo
echo.
echo 2. LOGIN COMO ADMIN
echo    - Abrir: http://localhost:8000
echo    - Usuario: dvd
echo    - Password: [tu password]
echo.
echo 3. CONFIGURAR PARTIDA
echo    - Ir a Admin Panel
echo    - Click en "Hundir la Flota"
echo    - Configurar:
echo      * Tablero: 10x10
echo      * Tiempo: 60s
echo      * Barcos personalizados:
echo        - Portaaviones: 2
echo        - Acorazado: 1
echo        - Crucero: 2
echo        - Submarino: 1
echo        - Destructor: 0
echo      * Jugadores: Anadir 2 usuarios
echo    - Click "Iniciar partida"
echo.
echo 4. FASE DE COLOCACION (en cada ventana)
echo    - Seleccionar orientacion (H/V)
echo    - Click en tipo de barco
echo    - Click en tablero para colocar
echo    - Probar "Mover" un barco
echo    - Probar "Borrar" un barco
echo    - Click "Validar" cuando todos esten colocados
echo.
echo 5. FASE DE BATALLA
echo    - En tu turno:
echo      * Click en celda del tablero enemigo
echo      * Click "Atacar"
echo      * Ver animacion y mensaje
echo    - Verificar:
echo      * Puntos rojos en tu tablero (ataques recibidos)
echo      * Puntos rojos/azules en tablero enemigo (tus ataques)
echo      * Cambio de turnos
echo      * Mensajes de TOCADO/HUNDIDO/AGUA
echo.
echo 6. VERIFICAR VICTORIA
echo    - Hundir todos los barcos del enemigo
echo    - Ver mensaje de victoria
echo.
echo ========================================
echo MEJORAS IMPLEMENTADAS:
echo ========================================
echo [X] Solo tablero propio en fase de colocacion
echo [X] Rotacion de barcos (H/V)
echo [X] Boton Mover barco
echo [X] Boton Borrar barco
echo [X] Boton Validar (se habilita al terminar)
echo [X] Configuracion de unidades por tipo (admin)
echo [X] Sistema de ataque por turnos
echo [X] Feedback visual de ataques
echo [X] Animaciones de impacto/fallo/hundido
echo [X] Mensajes descriptivos
echo [X] Puntos rojos en tablero propio
echo ========================================
echo.
pause
