#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: JUEGO ¿QUIÉN SOY?
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

def test_quien_soy():
    logger = TestLogger("quien_soy")
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
    response = client_user.get("/game_pages/quiensoy/game.html")
    if verify_response(response, 200, logger, "Cargar página"):
        if "Quién soy" in response.text or "quiensoy" in response.text:
            logger.success("Página cargada correctamente")
    
    logger.section("3. WEBSOCKET: CONEXIÓN")
    ws_messages_admin = []
    ws_messages_user = []
    ws_connected_admin = threading.Event()
    ws_connected_user = threading.Event()
    
    def on_message_admin(ws, message):
        data = json.loads(message)
        ws_messages_admin.append(data)
        logger.debug(f"Admin WS: {data.get('type', 'unknown')}")
    
    def on_open_admin(ws):
        ws_connected_admin.set()
        logger.success("WebSocket admin conectado")
    
    def on_message_user(ws, message):
        data = json.loads(message)
        ws_messages_user.append(data)
        logger.debug(f"User WS: {data.get('type', 'unknown')}")
    
    def on_open_user(ws):
        ws_connected_user.set()
        logger.success("WebSocket user conectado")
    
    ws_admin = websocket.WebSocketApp(
        f"{ws_url}/ws/quiensoy?token={client_admin.token}",
        on_message=on_message_admin,
        on_open=on_open_admin
    )
    
    ws_user = websocket.WebSocketApp(
        f"{ws_url}/ws/quiensoy?token={client_user.token}",
        on_message=on_message_user,
        on_open=on_open_user
    )
    
    ws_thread_admin = threading.Thread(target=ws_admin.run_forever, daemon=True)
    ws_thread_user = threading.Thread(target=ws_user.run_forever, daemon=True)
    
    ws_thread_admin.start()
    ws_thread_user.start()
    
    if not ws_connected_admin.wait(timeout=5):
        logger.fail("WebSocket admin no conectó")
        return logger.summary()
    
    if not ws_connected_user.wait(timeout=5):
        logger.fail("WebSocket user no conectó")
        return logger.summary()
    
    time.sleep(1)
    
    logger.section("4. CONFIGURAR JUEGO")
    ws_admin.send(json.dumps({
        "action": "setup",
        "character": "Albert Einstein",
        "players": [user_creds['username']],
        "max_guesses": 3
    }))
    time.sleep(2)
    
    if ws_messages_admin:
        state = ws_messages_admin[-1]
        if state.get('enabled'):
            logger.success("Juego configurado y habilitado")
            if state.get('character') == "Albert Einstein":
                logger.success("Personaje configurado correctamente")
    
    logger.section("5. HACER PREGUNTA")
    ws_user.send(json.dumps({
        "action": "ask",
        "question": "¿Eres una persona real?"
    }))
    time.sleep(2)
    
    # Verificar que se recibió la pregunta
    if ws_messages_admin:
        state = ws_messages_admin[-1]
        history = state.get('history', [])
        if history:
            logger.success(f"Pregunta registrada en historial: {len(history)} preguntas")
    
    logger.section("6. RESPONDER PREGUNTA (IA)")
    # La IA debería responder automáticamente
    time.sleep(3)
    
    if ws_messages_user:
        state = ws_messages_user[-1]
        history = state.get('history', [])
        if history and history[-1].get('answer'):
            logger.success(f"Respuesta de IA recibida: {history[-1]['answer'][:50]}...")
    
    logger.section("7. INTENTAR ADIVINAR")
    ws_user.send(json.dumps({
        "action": "guess",
        "guess": "Isaac Newton"
    }))
    time.sleep(2)
    
    if ws_messages_user:
        state = ws_messages_user[-1]
        players = state.get('players', [])
        if players:
            player = next((p for p in players if p['username'] == user_creds['username']), None)
            if player:
                guesses_left = player.get('guesses_left', 3)
                logger.info(f"Intentos restantes: {guesses_left}")
                if guesses_left < 3:
                    logger.success("Intento de adivinanza registrado")
    
    logger.section("8. ADIVINAR CORRECTAMENTE")
    ws_user.send(json.dumps({
        "action": "guess",
        "guess": "Albert Einstein"
    }))
    time.sleep(2)
    
    if ws_messages_user:
        state = ws_messages_user[-1]
        if state.get('winner') == user_creds['username']:
            logger.success("¡Adivinanza correcta! Jugador ganó")
        elif state.get('status') == 'finished':
            logger.success("Juego finalizado")
    
    logger.section("9. FORZAR PREGUNTA (ADMIN)")
    ws_admin.send(json.dumps({"action": "reset"}))
    time.sleep(1)
    
    ws_admin.send(json.dumps({
        "action": "setup",
        "character": "Marie Curie",
        "players": [user_creds['username']]
    }))
    time.sleep(1)
    
    ws_admin.send(json.dumps({
        "action": "force_question",
        "username": user_creds['username']
    }))
    time.sleep(1)
    
    if ws_messages_admin:
        state = ws_messages_admin[-1]
        if state.get('forced_player') == user_creds['username']:
            logger.success("Pregunta forzada correctamente")
    
    logger.section("10. REVELAR PERSONAJE (ADMIN)")
    ws_admin.send(json.dumps({"action": "reveal"}))
    time.sleep(1)
    
    if ws_messages_user:
        state = ws_messages_user[-1]
        if state.get('status') == 'finished':
            logger.success("Personaje revelado, juego finalizado")
    
    logger.section("11. REINICIAR JUEGO")
    ws_admin.send(json.dumps({"action": "reset"}))
    time.sleep(1)
    
    if ws_messages_admin:
        state = ws_messages_admin[-1]
        if state.get('status') == 'waiting':
            logger.success("Juego reiniciado correctamente")
    
    ws_admin.close()
    ws_user.close()
    
    logger.info(f"Total mensajes admin: {len(ws_messages_admin)}")
    logger.info(f"Total mensajes user: {len(ws_messages_user)}")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_quien_soy()
    sys.exit(0 if success else 1)
