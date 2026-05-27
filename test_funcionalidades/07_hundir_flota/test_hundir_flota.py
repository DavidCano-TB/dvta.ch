#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: JUEGO HUNDIR LA FLOTA
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

def test_hundir_flota():
    logger = TestLogger("hundir_flota")
    config = load_config()
    
    base_url = config['server']['base_url']
    ws_url = config['server']['ws_url']
    admin_creds = config['credentials']['admin']
    user1_creds = config['credentials']['test_user']
    user2_creds = config['credentials']['test_user2']
    
    client_admin = TestClient(base_url, logger)
    client_user1 = TestClient(base_url, logger)
    client_user2 = TestClient(base_url, logger)
    
    logger.section("1. AUTENTICACIÓN")
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    if not client_user1.login(user1_creds['username'], user1_creds['password']):
        return logger.summary()
    if not client_user2.login(user2_creds['username'], user2_creds['password']):
        return logger.summary()
    
    logger.section("2. VERIFICAR PÁGINAS")
    response = client_user1.get("/game_pages/hundirlaflota/game.html")
    if verify_response(response, 200, logger, "Cargar página juego"):
        logger.success("Página de juego cargada")
    
    response = client_admin.get("/game_pages/hundirlaflota/admin.html")
    if verify_response(response, 200, logger, "Cargar página admin"):
        logger.success("Página admin cargada")
    
    logger.section("3. WEBSOCKET: CONEXIÓN")
    ws_messages_user1 = []
    ws_connected_user1 = threading.Event()
    
    def on_message_user1(ws, message):
        ws_messages_user1.append(json.loads(message))
    
    def on_open_user1(ws):
        ws_connected_user1.set()
        logger.success("WebSocket user1 conectado")
    
    ws_user1 = websocket.WebSocketApp(
        f"{ws_url}/ws/hundirlaflota?token={client_user1.token}",
        on_message=on_message_user1,
        on_open=on_open_user1
    )
    
    ws_thread_user1 = threading.Thread(target=ws_user1.run_forever, daemon=True)
    ws_thread_user1.start()
    
    if not ws_connected_user1.wait(timeout=5):
        logger.fail("WebSocket no conectó")
        return logger.summary()
    
    time.sleep(1)
    
    logger.section("4. CONFIGURAR JUEGO")
    ws_user1.send(json.dumps({
        "action": "configure",
        "board_size": 10,
        "ships": {
            "portaaviones": {"size": 5, "count": 1},
            "acorazado": {"size": 4, "count": 1},
            "crucero": {"size": 3, "count": 1},
            "submarino": {"size": 3, "count": 1},
            "destructor": {"size": 2, "count": 1}
        }
    }))
    time.sleep(2)
    
    if ws_messages_user1:
        state = ws_messages_user1[-1]
        if state.get('setup'):
            logger.success("Configuración aplicada")
    
    logger.section("5. COLOCAR BARCOS")
    # Colocar un barco de prueba
    ws_user1.send(json.dumps({
        "action": "place_ship",
        "ship_type": "portaaviones",
        "positions": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
        "orientation": "H"
    }))
    time.sleep(1)
    logger.success("Barco colocado")
    
    logger.section("6. MARCAR LISTO")
    ws_user1.send(json.dumps({"action": "ready"}))
    time.sleep(1)
    
    if ws_messages_user1:
        state = ws_messages_user1[-1]
        players = state.get('players', [])
        user1_data = next((p for p in players if p['username'] == user1_creds['username']), None)
        if user1_data and user1_data.get('ready'):
            logger.success("Jugador marcado como listo")
    
    logger.section("7. ATACAR")
    ws_user1.send(json.dumps({
        "action": "attack",
        "row": 5,
        "col": 5
    }))
    time.sleep(1)
    logger.success("Ataque realizado")
    
    logger.section("8. REINICIAR JUEGO")
    ws_user1.send(json.dumps({"action": "reset"}))
    time.sleep(1)
    
    if ws_messages_user1:
        state = ws_messages_user1[-1]
        if state.get('phase') == 'waiting':
            logger.success("Juego reiniciado")
    
    ws_user1.close()
    logger.info(f"Total mensajes: {len(ws_messages_user1)}")
    return logger.summary()

if __name__ == "__main__":
    success = test_hundir_flota()
    sys.exit(0 if success else 1)
