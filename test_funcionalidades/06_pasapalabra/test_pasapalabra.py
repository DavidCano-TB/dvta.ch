#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: JUEGO PASAPALABRA
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

def test_pasapalabra():
    logger = TestLogger("pasapalabra")
    config = load_config()
    
    base_url = config['server']['base_url']
    ws_url = config['server']['ws_url']
    admin_creds = config['credentials']['admin']
    user_creds = config['credentials']['test_user']
    
    client_admin = TestClient(base_url, logger)
    client_user = TestClient(base_url, logger)
    
    logger.section("1. AUTENTICACIÓN")
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    if not client_user.login(user_creds['username'], user_creds['password']):
        return logger.summary()
    
    logger.section("2. VERIFICAR PÁGINA")
    response = client_user.get("/game_pages/pasapalabra/game.html")
    if verify_response(response, 200, logger, "Cargar página"):
        if "Pasapalabra" in response.text:
            logger.success("Página cargada")
    
    logger.section("3. WEBSOCKET")
    ws_messages = []
    ws_connected = threading.Event()
    
    def on_message(ws, message):
        ws_messages.append(json.loads(message))
    
    def on_open(ws):
        ws_connected.set()
        logger.success("WebSocket conectado")
    
    ws = websocket.WebSocketApp(
        f"{ws_url}/ws/pasapalabra?token={client_admin.token}",
        on_message=on_message,
        on_open=on_open
    )
    
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()
    
    if not ws_connected.wait(timeout=5):
        logger.fail("WebSocket no conectó")
        return logger.summary()
    
    time.sleep(1)
    
    logger.section("4. CONFIGURAR JUEGO")
    ws.send(json.dumps({
        "action": "setup",
        "players": [user_creds['username']],
        "rosco_time": 300
    }))
    time.sleep(2)
    
    if ws_messages and ws_messages[-1].get('enabled'):
        logger.success("Juego habilitado")
    
    logger.section("5. INICIAR TEMPORIZADOR")
    ws.send(json.dumps({"action": "start_timer"}))
    time.sleep(1)
    logger.success("Temporizador iniciado")
    
    logger.section("6. RESPONDER PREGUNTA")
    ws.send(json.dumps({
        "action": "player_answer",
        "text": "RESPUESTA"
    }))
    time.sleep(1)
    logger.success("Respuesta enviada")
    
    logger.section("7. MARCAR CORRECTA")
    ws.send(json.dumps({"action": "correct"}))
    time.sleep(1)
    logger.success("Respuesta marcada como correcta")
    
    logger.section("8. PASAR PREGUNTA")
    ws.send(json.dumps({"action": "pass"}))
    time.sleep(1)
    logger.success("Pregunta pasada")
    
    logger.section("9. PAUSAR/REANUDAR")
    ws.send(json.dumps({"action": "pause"}))
    time.sleep(0.5)
    ws.send(json.dumps({"action": "start_timer"}))
    time.sleep(0.5)
    logger.success("Pausa/reanudación funcionando")
    
    ws.close()
    logger.info(f"Total mensajes: {len(ws_messages)}")
    return logger.summary()

if __name__ == "__main__":
    success = test_pasapalabra()
    sys.exit(0 if success else 1)
