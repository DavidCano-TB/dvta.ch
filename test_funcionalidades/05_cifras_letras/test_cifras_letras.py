#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: JUEGO CIFRAS Y LETRAS
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

def test_cifras_letras():
    logger = TestLogger("cifras_letras")
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
    
    logger.section("2. VERIFICAR PÁGINA DEL JUEGO")
    response = client_user.get("/game_pages/cifrasletras/game.html")
    if verify_response(response, 200, logger, "Cargar página"):
        if "Cifras y Letras" in response.text:
            logger.success("Página cargada correctamente")
    
    logger.section("3. WEBSOCKET: CONEXIÓN")
    ws_messages = []
    ws_connected = threading.Event()
    
    def on_message(ws, message):
        ws_messages.append(json.loads(message))
    
    def on_open(ws):
        ws_connected.set()
        logger.success("WebSocket conectado")
    
    ws = websocket.WebSocketApp(
        f"{ws_url}/ws/cifrasletras?token={client_admin.token}",
        on_message=on_message,
        on_open=on_open
    )
    
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()
    
    if not ws_connected.wait(timeout=5):
        logger.fail("WebSocket no se conectó")
        return logger.summary()
    
    time.sleep(1)
    
    logger.section("4. CONFIGURAR JUEGO")
    ws.send(json.dumps({
        "action": "setup",
        "max_rounds": 3,
        "round_time": 30
    }))
    time.sleep(2)
    
    if ws_messages and ws_messages[-1].get('enabled'):
        logger.success("Juego configurado y habilitado")
    
    logger.section("5. INICIAR RONDA DE LETRAS")
    ws.send(json.dumps({
        "action": "start_letters",
        "vowels": 4
    }))
    time.sleep(1)
    
    if ws_messages:
        state = ws_messages[-1]
        if state.get('letters'):
            logger.success(f"Letras generadas: {len(state['letters'])}")
    
    logger.section("6. INICIAR TEMPORIZADOR")
    ws.send(json.dumps({"action": "start_timer"}))
    time.sleep(1)
    logger.success("Temporizador iniciado")
    
    logger.section("7. ENVIAR RESPUESTA")
    ws.send(json.dumps({
        "action": "submit",
        "username": user_creds['username'],
        "answer": "CASA"
    }))
    time.sleep(1)
    logger.success("Respuesta enviada")
    
    logger.section("8. REVELAR RESPUESTAS")
    ws.send(json.dumps({"action": "reveal"}))
    time.sleep(1)
    
    if ws_messages:
        state = ws_messages[-1]
        if state.get('results'):
            logger.success(f"Resultados revelados: {len(state['results'])} respuestas")
    
    logger.section("9. RONDA DE NÚMEROS")
    ws.send(json.dumps({"action": "start_numbers"}))
    time.sleep(1)
    
    if ws_messages:
        state = ws_messages[-1]
        if state.get('numbers') and state.get('target'):
            logger.success(f"Números: {state['numbers']}, Objetivo: {state['target']}")
    
    logger.section("10. FINALIZAR JUEGO")
    ws.send(json.dumps({"action": "finish"}))
    time.sleep(1)
    
    ws.close()
    logger.success("WebSocket cerrado")
    
    logger.info(f"Total mensajes recibidos: {len(ws_messages)}")
    return logger.summary()

if __name__ == "__main__":
    success = test_cifras_letras()
    sys.exit(0 if success else 1)
