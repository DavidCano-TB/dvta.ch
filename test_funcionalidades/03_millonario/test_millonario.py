#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: JUEGO MILLONARIO
Verifica todas las funcionalidades del juego ¿Quién quiere ser millonario?
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response
import websocket
import json
import threading
import time

def test_millonario():
    """Test completo del juego Millonario"""
    logger = TestLogger("millonario")
    config = load_config()
    
    base_url = config['server']['base_url']
    ws_url = config['server']['ws_url']
    admin_creds = config['credentials']['admin']
    user_creds = config['credentials']['test_user']
    
    client_admin = TestClient(base_url, logger)
    client_user = TestClient(base_url, logger)
    
    # ========================================================================
    # 1. AUTENTICACIÓN
    # ========================================================================
    logger.section("1. AUTENTICACIÓN")
    
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    
    if not client_user.login(user_creds['username'], user_creds['password']):
        return logger.summary()
    
    # ========================================================================
    # 2. VERIFICAR PÁGINA DEL JUEGO
    # ========================================================================
    logger.section("2. VERIFICAR PÁGINA DEL JUEGO")
    
    response = client_user.get("/game_pages/millonario/game.html")
    if verify_response(response, 200, logger, "Cargar página del juego"):
        html = response.text
        if "Millonario" in html:
            logger.success("Página del juego cargada correctamente")
        else:
            logger.fail("Contenido de la página incorrecto")
    
    # ========================================================================
    # 3. WEBSOCKET: CONEXIÓN
    # ========================================================================
    logger.section("3. WEBSOCKET: CONEXIÓN")
    
    ws_messages_admin = []
    ws_messages_user = []
    ws_connected_admin = threading.Event()
    ws_connected_user = threading.Event()
    
    def on_message_admin(ws, message):
        data = json.loads(message)
        ws_messages_admin.append(data)
        logger.debug(f"Admin WS recibió: {data.get('type', 'unknown')}")
    
    def on_open_admin(ws):
        ws_connected_admin.set()
        logger.success("WebSocket admin conectado")
    
    def on_message_user(ws, message):
        data = json.loads(message)
        ws_messages_user.append(data)
        logger.debug(f"User WS recibió: {data.get('type', 'unknown')}")
    
    def on_open_user(ws):
        ws_connected_user.set()
        logger.success("WebSocket user conectado")
    
    # Conectar WebSockets
    ws_admin = websocket.WebSocketApp(
        f"{ws_url}/ws/millonario?token={client_admin.token}",
        on_message=on_message_admin,
        on_open=on_open_admin
    )
    
    ws_user = websocket.WebSocketApp(
        f"{ws_url}/ws/millonario?token={client_user.token}",
        on_message=on_message_user,
        on_open=on_open_user
    )
    
    # Iniciar WebSockets en threads
    ws_thread_admin = threading.Thread(target=ws_admin.run_forever, daemon=True)
    ws_thread_user = threading.Thread(target=ws_user.run_forever, daemon=True)
    
    ws_thread_admin.start()
    ws_thread_user.start()
    
    # Esperar conexión
    if not ws_connected_admin.wait(timeout=5):
        logger.fail("WebSocket admin no se conectó")
        return logger.summary()
    
    if not ws_connected_user.wait(timeout=5):
        logger.fail("WebSocket user no se conectó")
        return logger.summary()
    
    time.sleep(1)  # Esperar estado inicial
    
    # ========================================================================
    # 4. CONFIGURAR JUEGO (ADMIN)
    # ========================================================================
    logger.section("4. CONFIGURAR JUEGO")
    
    ws_admin.send(json.dumps({
        "action": "setup",
        "player": user_creds['username']
    }))
    
    time.sleep(2)
    
    # Verificar que se recibió el estado
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        if last_state.get('type') == 'state':
            logger.success("Estado del juego recibido")
            if last_state.get('enabled'):
                logger.success("Juego habilitado correctamente")
            else:
                logger.fail("Juego no se habilitó")
        else:
            logger.fail("No se recibió estado del juego")
    
    # ========================================================================
    # 5. VERIFICAR PREGUNTA INICIAL
    # ========================================================================
    logger.section("5. VERIFICAR PREGUNTA INICIAL")
    
    time.sleep(1)
    
    if ws_messages_user:
        last_state = ws_messages_user[-1]
        if last_state.get('pregunta'):
            pregunta = last_state['pregunta']
            logger.success(f"Pregunta recibida: {pregunta.get('pregunta', '')[:50]}...")
            logger.info(f"Premio: {pregunta.get('premio', 'N/A')}")
            logger.info(f"Opciones: {len(pregunta.get('opciones', {}))}")
        else:
            logger.fail("No se recibió pregunta")
    
    # ========================================================================
    # 6. SELECCIONAR OPCIÓN (ADMIN)
    # ========================================================================
    logger.section("6. SELECCIONAR OPCIÓN")
    
    ws_admin.send(json.dumps({
        "action": "select_option",
        "letter": "A"
    }))
    
    time.sleep(1)
    
    # Verificar que se actualizó el estado
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        if last_state.get('selected_option') == 'A':
            logger.success("Opción seleccionada correctamente")
        else:
            logger.warning("Opción no reflejada en el estado")
    
    # ========================================================================
    # 7. MARCAR RESPUESTA CORRECTA
    # ========================================================================
    logger.section("7. MARCAR RESPUESTA CORRECTA")
    
    ws_admin.send(json.dumps({
        "action": "correct"
    }))
    
    time.sleep(2)
    
    # Verificar que avanzó de nivel
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        nivel = last_state.get('nivel', 0)
        if nivel > 1:
            logger.success(f"Avanzó al nivel {nivel}")
        else:
            logger.fail("No avanzó de nivel")
    
    # ========================================================================
    # 8. USAR COMODÍN 50/50
    # ========================================================================
    logger.section("8. USAR COMODÍN 50/50")
    
    ws_admin.send(json.dumps({
        "action": "comodin_50"
    }))
    
    time.sleep(1)
    
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        if last_state.get('comodin_50'):
            logger.success("Comodín 50/50 usado")
            eliminadas = last_state.get('eliminadas', [])
            logger.info(f"Opciones eliminadas: {eliminadas}")
        else:
            logger.fail("Comodín no se activó")
    
    # ========================================================================
    # 9. PLANTARSE
    # ========================================================================
    logger.section("9. PLANTARSE")
    
    # Primero marcar correcta para tener opción de plantarse
    ws_admin.send(json.dumps({"action": "correct"}))
    time.sleep(1)
    
    ws_admin.send(json.dumps({
        "action": "plantarse"
    }))
    
    time.sleep(2)
    
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        if last_state.get('status') == 'plantado':
            logger.success("Jugador se plantó correctamente")
            logger.info(f"Premio final: {last_state.get('ultimo_premio', 'N/A')}")
        else:
            logger.warning(f"Estado: {last_state.get('status')}")
    
    # ========================================================================
    # 10. REINICIAR JUEGO
    # ========================================================================
    logger.section("10. REINICIAR JUEGO")
    
    ws_admin.send(json.dumps({
        "action": "reset"
    }))
    
    time.sleep(1)
    
    if ws_messages_admin:
        last_state = ws_messages_admin[-1]
        if last_state.get('status') == 'waiting':
            logger.success("Juego reiniciado correctamente")
        else:
            logger.fail(f"Estado después de reset: {last_state.get('status')}")
    
    # ========================================================================
    # 11. CERRAR WEBSOCKETS
    # ========================================================================
    logger.section("11. CERRAR CONEXIONES")
    
    ws_admin.close()
    ws_user.close()
    time.sleep(1)
    
    logger.success("WebSockets cerrados")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    logger.info(f"Total mensajes admin: {len(ws_messages_admin)}")
    logger.info(f"Total mensajes user: {len(ws_messages_user)}")
    
    return logger.summary()


if __name__ == "__main__":
    success = test_millonario()
    sys.exit(0 if success else 1)
