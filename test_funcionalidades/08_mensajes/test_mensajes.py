#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE MENSAJES
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time

def test_mensajes():
    logger = TestLogger("mensajes")
    config = load_config()
    
    base_url = config['server']['base_url']
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
    
    logger.section("2. VERIFICAR ESTADO DEL SISTEMA")
    response = client_user1.get("/api/messages/status")
    if verify_response(response, 200, logger, "Obtener estado"):
        status = response.json()
        logger.info(f"Sistema habilitado: {status.get('enabled', False)}")
    
    logger.section("3. LISTAR SALAS")
    response = client_user1.get("/api/messages/rooms")
    if verify_response(response, 200, logger, "Listar salas"):
        rooms = response.json()
        logger.info(f"Salas disponibles: {len(rooms)}")
    
    logger.section("4. ENVIAR MENSAJE DIRECTO")
    response = client_user1.post("/api/messages/send", json={
        "to_user": user2_creds['username'],
        "message": "Hola, este es un mensaje de prueba",
        "room": "dm"
    })
    if verify_response(response, 200, logger, "Enviar mensaje"):
        logger.success("Mensaje enviado correctamente")
    
    logger.section("5. OBTENER MENSAJES")
    response = client_user2.get(f"/api/messages/room/dm/{user1_creds['username']}")
    if verify_response(response, 200, logger, "Obtener mensajes"):
        messages = response.json()
        logger.info(f"Mensajes recibidos: {len(messages)}")
        
        if messages:
            msg = messages[-1]
            required_fields = ['id', 'from_user', 'message', 'timestamp']
            verify_json_fields(msg, required_fields, logger, "Estructura de mensaje")
    
    logger.section("6. MENSAJE GRUPAL")
    response = client_user1.post("/api/messages/send", json={
        "message": "Mensaje para el grupo",
        "room": "general"
    })
    if verify_response(response, 200, logger, "Enviar mensaje grupal"):
        logger.success("Mensaje grupal enviado")
    
    logger.section("7. MARCAR COMO LEÍDO")
    response = client_user2.post("/api/messages/mark-read", json={
        "room": "dm",
        "other_user": user1_creds['username']
    })
    if verify_response(response, 200, logger, "Marcar como leído"):
        logger.success("Mensajes marcados como leídos")
    
    logger.section("8. MENSAJES NO LEÍDOS")
    response = client_user1.get("/api/messages/unread")
    if verify_response(response, 200, logger, "Obtener no leídos"):
        unread = response.json()
        logger.info(f"Mensajes no leídos: {unread.get('count', 0)}")
    
    logger.section("9. BUSCAR MENSAJES")
    response = client_user1.get("/api/messages/search?query=prueba")
    if verify_response(response, 200, logger, "Buscar mensajes"):
        results = response.json()
        logger.info(f"Resultados de búsqueda: {len(results)}")
    
    logger.section("10. ELIMINAR MENSAJE (ADMIN)")
    # Obtener ID del último mensaje
    response = client_admin.get("/api/messages/room/general")
    if response and response.status_code == 200:
        messages = response.json()
        if messages:
            msg_id = messages[-1]['id']
            
            response = client_admin.delete(f"/api/messages/{msg_id}")
            if verify_response(response, 200, logger, "Eliminar mensaje"):
                logger.success("Mensaje eliminado")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_mensajes()
    sys.exit(0 if success else 1)
