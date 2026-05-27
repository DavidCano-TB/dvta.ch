#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE VIDEO
Verifica todas las funcionalidades del sistema de videollamadas WebRTC
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import websocket
import json
import threading
import time

def test_video():
    """Test completo del sistema de video"""
    logger = TestLogger("video")
    config = load_config()
    
    base_url = config['server']['base_url']
    ws_url = config['server']['ws_url']
    admin_creds = config['credentials']['admin']
    user1_creds = config['credentials']['test_user']
    user2_creds = config['credentials']['test_user2']
    
    client_admin = TestClient(base_url, logger)
    client_user1 = TestClient(base_url, logger)
    client_user2 = TestClient(base_url, logger)
    
    # ========================================================================
    # 1. AUTENTICACIÓN
    # ========================================================================
    logger.section("1. AUTENTICACIÓN")
    
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    
    if not client_user1.login(user1_creds['username'], user1_creds['password']):
        return logger.summary()
    
    if not client_user2.login(user2_creds['username'], user2_creds['password']):
        return logger.summary()
    
    # ========================================================================
    # 2. VERIFICAR PÁGINA DE VIDEO
    # ========================================================================
    logger.section("2. VERIFICAR PÁGINA DE VIDEO")
    
    response = client_user1.get(f"/video?token={client_user1.token}")
    if verify_response(response, 200, logger, "Cargar página de video"):
        html = response.text
        if "WebRTC" in html or "video" in html.lower():
            logger.success("Página de video cargada correctamente")
        else:
            logger.warning("Contenido de la página podría ser incorrecto")
    
    # ========================================================================
    # 3. ICE SERVERS
    # ========================================================================
    logger.section("3. ICE SERVERS")
    
    response = client_user1.get("/api/ice-servers")
    if verify_response(response, 200, logger, "Obtener ICE servers"):
        ice_servers = response.json()
        logger.info(f"ICE servers disponibles: {len(ice_servers)}")
        
        if ice_servers:
            server = ice_servers[0]
            if 'urls' in server:
                logger.success(f"ICE server configurado: {server['urls']}")
            else:
                logger.fail("ICE server sin URLs")
    
    # ========================================================================
    # 4. SALAS DE VIDEO
    # ========================================================================
    logger.section("4. SALAS DE VIDEO")
    
    # 4.1 Crear sala
    response = client_admin.post("/api/video/rooms/create", json={
        "room_name": "Sala de Prueba",
        "max_participants": 4
    })
    if verify_response(response, 200, logger, "Crear sala de video"):
        room_data = response.json()
        room_id = room_data.get('room_id')
        logger.success(f"Sala creada con ID: {room_id}")
    else:
        room_id = "test_room"
    
    # 4.2 Listar salas
    response = client_user1.get("/api/video/rooms")
    if verify_response(response, 200, logger, "Listar salas de video"):
        rooms = response.json()
        logger.info(f"Salas disponibles: {len(rooms)}")
        
        if rooms:
            room = rooms[0]
            required_fields = ['room_id', 'room_name', 'participants']
            verify_json_fields(room, required_fields, logger, "Estructura de sala")
    
    # ========================================================================
    # 5. WEBSOCKET: SEÑALIZACIÓN
    # ========================================================================
    logger.section("5. WEBSOCKET: SEÑALIZACIÓN")
    
    ws_messages_user1 = []
    ws_messages_user2 = []
    ws_connected_user1 = threading.Event()
    ws_connected_user2 = threading.Event()
    
    def on_message_user1(ws, message):
        data = json.loads(message)
        ws_messages_user1.append(data)
        logger.debug(f"User1 WS: {data.get('type', 'unknown')}")
    
    def on_open_user1(ws):
        ws_connected_user1.set()
        logger.success("WebSocket user1 conectado")
    
    def on_message_user2(ws, message):
        data = json.loads(message)
        ws_messages_user2.append(data)
        logger.debug(f"User2 WS: {data.get('type', 'unknown')}")
    
    def on_open_user2(ws):
        ws_connected_user2.set()
        logger.success("WebSocket user2 conectado")
    
    # Conectar WebSockets
    ws_user1 = websocket.WebSocketApp(
        f"{ws_url}/ws/video/{room_id}?token={client_user1.token}",
        on_message=on_message_user1,
        on_open=on_open_user1
    )
    
    ws_user2 = websocket.WebSocketApp(
        f"{ws_url}/ws/video/{room_id}?token={client_user2.token}",
        on_message=on_message_user2,
        on_open=on_open_user2
    )
    
    # Iniciar WebSockets
    ws_thread_user1 = threading.Thread(target=ws_user1.run_forever, daemon=True)
    ws_thread_user2 = threading.Thread(target=ws_user2.run_forever, daemon=True)
    
    ws_thread_user1.start()
    ws_thread_user2.start()
    
    # Esperar conexión
    if not ws_connected_user1.wait(timeout=5):
        logger.fail("WebSocket user1 no se conectó")
        return logger.summary()
    
    if not ws_connected_user2.wait(timeout=5):
        logger.fail("WebSocket user2 no se conectó")
        return logger.summary()
    
    time.sleep(2)
    
    # ========================================================================
    # 6. SEÑALIZACIÓN: OFFER/ANSWER
    # ========================================================================
    logger.section("6. SEÑALIZACIÓN: OFFER/ANSWER")
    
    # User1 envía offer
    test_offer = {
        "type": "offer",
        "sdp": "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
    }
    
    ws_user1.send(json.dumps({
        "type": "offer",
        "target": user2_creds['username'],
        "offer": test_offer
    }))
    
    time.sleep(1)
    
    # Verificar que user2 recibió el offer
    offer_received = any(
        msg.get('type') == 'offer' 
        for msg in ws_messages_user2
    )
    
    if offer_received:
        logger.success("Offer recibido por user2")
    else:
        logger.fail("Offer NO recibido por user2")
    
    # User2 envía answer
    test_answer = {
        "type": "answer",
        "sdp": "v=0\r\no=- 987654321 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
    }
    
    ws_user2.send(json.dumps({
        "type": "answer",
        "target": user1_creds['username'],
        "answer": test_answer
    }))
    
    time.sleep(1)
    
    # Verificar que user1 recibió el answer
    answer_received = any(
        msg.get('type') == 'answer'
        for msg in ws_messages_user1
    )
    
    if answer_received:
        logger.success("Answer recibido por user1")
    else:
        logger.fail("Answer NO recibido por user1")
    
    # ========================================================================
    # 7. ICE CANDIDATES
    # ========================================================================
    logger.section("7. ICE CANDIDATES")
    
    test_candidate = {
        "candidate": "candidate:1 1 UDP 2130706431 192.168.1.1 54321 typ host",
        "sdpMLineIndex": 0,
        "sdpMid": "0"
    }
    
    ws_user1.send(json.dumps({
        "type": "ice-candidate",
        "target": user2_creds['username'],
        "candidate": test_candidate
    }))
    
    time.sleep(1)
    
    # Verificar que user2 recibió el candidate
    candidate_received = any(
        msg.get('type') == 'ice-candidate'
        for msg in ws_messages_user2
    )
    
    if candidate_received:
        logger.success("ICE candidate recibido")
    else:
        logger.fail("ICE candidate NO recibido")
    
    # ========================================================================
    # 8. PARTICIPANTES EN SALA
    # ========================================================================
    logger.section("8. PARTICIPANTES EN SALA")
    
    response = client_admin.get(f"/api/video/rooms/{room_id}/participants")
    if verify_response(response, 200, logger, "Obtener participantes"):
        participants = response.json()
        logger.info(f"Participantes en sala: {len(participants)}")
        
        expected_users = {user1_creds['username'], user2_creds['username']}
        actual_users = {p['username'] for p in participants}
        
        if expected_users.issubset(actual_users):
            logger.success("Todos los usuarios esperados están en la sala")
        else:
            logger.fail(f"Usuarios faltantes: {expected_users - actual_users}")
    
    # ========================================================================
    # 9. CONTROL DE CÁMARA Y MICRÓFONO
    # ========================================================================
    logger.section("9. CONTROL DE CÁMARA Y MICRÓFONO")
    
    # Desactivar cámara
    ws_user1.send(json.dumps({
        "type": "camera-toggle",
        "enabled": False
    }))
    
    time.sleep(0.5)
    
    # Desactivar micrófono
    ws_user1.send(json.dumps({
        "type": "mic-toggle",
        "enabled": False
    }))
    
    time.sleep(0.5)
    
    logger.success("Comandos de control enviados")
    
    # ========================================================================
    # 10. SALIR DE LA SALA
    # ========================================================================
    logger.section("10. SALIR DE LA SALA")
    
    ws_user1.send(json.dumps({
        "type": "leave"
    }))
    
    time.sleep(1)
    
    # Verificar que user2 fue notificado
    leave_notified = any(
        msg.get('type') == 'user-left'
        for msg in ws_messages_user2
    )
    
    if leave_notified:
        logger.success("Salida notificada a otros participantes")
    else:
        logger.warning("Notificación de salida no detectada")
    
    # ========================================================================
    # 11. CERRAR CONEXIONES
    # ========================================================================
    logger.section("11. CERRAR CONEXIONES")
    
    ws_user1.close()
    ws_user2.close()
    time.sleep(1)
    
    logger.success("WebSockets cerrados")
    
    # ========================================================================
    # 12. ELIMINAR SALA
    # ========================================================================
    logger.section("12. ELIMINAR SALA")
    
    response = client_admin.delete(f"/api/video/rooms/{room_id}")
    if verify_response(response, 200, logger, "Eliminar sala"):
        logger.success("Sala eliminada correctamente")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    logger.info(f"Total mensajes user1: {len(ws_messages_user1)}")
    logger.info(f"Total mensajes user2: {len(ws_messages_user2)}")
    
    return logger.summary()


if __name__ == "__main__":
    success = test_video()
    sys.exit(0 if success else 1)
