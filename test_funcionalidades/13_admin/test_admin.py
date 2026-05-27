#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: FUNCIONALIDADES DE ADMINISTRACIÓN
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time

def test_admin():
    logger = TestLogger("admin")
    config = load_config()
    
    base_url = config['server']['base_url']
    admin_creds = config['credentials']['admin']
    user_creds = config['credentials']['test_user']
    
    client_admin = TestClient(base_url, logger)
    client_user = TestClient(base_url, logger)
    
    logger.section("1. AUTENTICACIÓN")
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    if not client_user.login(user_creds['username'], user_creds['password']):
        return logger.summary()
    
    logger.section("2. LISTAR USUARIOS (ADMIN)")
    response = client_admin.get("/api/admin/users")
    if verify_response(response, 200, logger, "Listar usuarios"):
        users = response.json()
        logger.info(f"Total usuarios en el sistema: {len(users)}")
        
        if users:
            user = users[0]
            required_fields = ['username', 'balance', 'is_admin']
            verify_json_fields(user, required_fields, logger, "Estructura de usuario")
    
    logger.section("3. VERIFICAR PERMISOS (NO ADMIN)")
    response = client_user.get("/api/admin/users")
    if response and response.status_code == 403:
        logger.success("Acceso denegado correctamente para usuario no admin")
    else:
        logger.fail("Usuario no admin pudo acceder a endpoint de admin")
    
    logger.section("4. LEDGER COMPLETO")
    response = client_admin.get("/api/admin/ledger?limit=50")
    if verify_response(response, 200, logger, "Obtener ledger"):
        ledger = response.json()
        logger.info(f"Transacciones en ledger: {len(ledger)}")
        
        if ledger:
            tx = ledger[0]
            required_fields = ['id', 'from_user', 'to_user', 'amount', 'timestamp']
            verify_json_fields(tx, required_fields, logger, "Estructura de transacción")
    
    logger.section("5. ACTIVIDAD DEL SISTEMA")
    response = client_admin.get("/api/admin/activity?limit=50")
    if verify_response(response, 200, logger, "Obtener actividad"):
        activity = response.json()
        logger.info(f"Eventos de actividad: {len(activity)}")
        
        if activity:
            event = activity[0]
            required_fields = ['username', 'section', 'timestamp']
            verify_json_fields(event, required_fields, logger, "Estructura de evento")
    
    logger.section("6. USUARIOS CONECTADOS")
    response = client_admin.get("/api/admin/connected")
    if verify_response(response, 200, logger, "Obtener usuarios conectados"):
        connected = response.json()
        logger.info(f"Usuarios conectados: {len(connected)}")
        
        if admin_creds['username'] in connected:
            logger.success("Admin aparece en lista de conectados")
    
    logger.section("7. CREAR USUARIO TEMPORAL")
    test_username = f"test_temp_{int(time.time())}"
    response = client_admin.post("/api/admin/create-user", json={
        "username": test_username,
        "password": "temp123",
        "initial_balance": 50
    })
    
    if response and response.status_code == 200:
        logger.success(f"Usuario temporal creado: {test_username}")
    else:
        logger.warning("No se pudo crear usuario temporal (puede no estar implementado)")
        test_username = user_creds['username']  # Usar usuario existente
    
    logger.section("8. BLOQUEAR USUARIO")
    response = client_admin.post(f"/api/admin/block/{test_username}")
    if verify_response(response, 200, logger, "Bloquear usuario"):
        logger.success(f"Usuario {test_username} bloqueado")
    
    logger.section("9. DESBLOQUEAR USUARIO")
    response = client_admin.post(f"/api/admin/unblock/{test_username}")
    if verify_response(response, 200, logger, "Desbloquear usuario"):
        logger.success(f"Usuario {test_username} desbloqueado")
    
    logger.section("10. RESETEAR CONTRASEÑA")
    response = client_admin.post(f"/api/admin/reset-pwd/{test_username}")
    if verify_response(response, 200, logger, "Resetear contraseña"):
        logger.success("Contraseña reseteada correctamente")
    
    logger.section("11. GESTIÓN DE ADMINS")
    
    # Listar admins
    response = client_admin.get("/api/admin/list-admins")
    if verify_response(response, 200, logger, "Listar admins"):
        admins = response.json()
        logger.info(f"Administradores en el sistema: {len(admins)}")
    
    # Crear admin (solo superadmin)
    if admin_creds['username'] in ['dvd', 'nebulosa']:
        response = client_admin.post("/api/admin/create-admin", json={
            "username": "test_admin_temp",
            "password": "admin123"
        })
        
        if response and response.status_code == 200:
            logger.success("Admin temporal creado")
            
            # Eliminar admin temporal
            response = client_admin.delete("/api/admin/delete-admin/test_admin_temp")
            if verify_response(response, 200, logger, "Eliminar admin"):
                logger.success("Admin temporal eliminado")
        else:
            logger.info("Creación de admin requiere permisos de superadmin")
    else:
        logger.info("Usuario no es superadmin, saltando creación de admin")
    
    logger.section("12. ESTADÍSTICAS DEL SISTEMA")
    
    # Resumen de estadísticas
    response = client_admin.get("/api/stats/summary")
    if verify_response(response, 200, logger, "Obtener resumen de stats"):
        stats = response.json()
        logger.info(f"Usuarios con sesiones: {len(stats)}")
    
    # Estadísticas de juegos
    response = client_admin.get("/api/stats/games")
    if verify_response(response, 200, logger, "Obtener stats de juegos"):
        games = response.json()
        logger.info(f"Juegos con estadísticas: {len(games)}")
    
    # Estadísticas de transacciones
    response = client_admin.get("/api/stats/transactions-summary")
    if verify_response(response, 200, logger, "Obtener stats de transacciones"):
        tx_stats = response.json()
        logger.info(f"Total enviado: {tx_stats.get('total_sent', 0)} DVDcoins")
        logger.info(f"Total recibido: {tx_stats.get('total_received', 0)} DVDcoins")
    
    # Estadísticas avanzadas
    response = client_admin.get("/api/stats/advanced")
    if verify_response(response, 200, logger, "Obtener stats avanzadas"):
        advanced = response.json()
        logger.info(f"Secciones con datos: {len(advanced.get('by_section', []))}")
    
    # Estadísticas de apuestas
    response = client_admin.get("/api/stats/apuestas-summary")
    if verify_response(response, 200, logger, "Obtener stats de apuestas"):
        apuestas_stats = response.json()
        logger.info(f"Total apostado: {apuestas_stats.get('total_apostado', 0)}")
    
    # Overview de miembros
    response = client_admin.get("/api/stats/members-overview")
    if verify_response(response, 200, logger, "Obtener overview de miembros"):
        members = response.json()
        logger.info(f"Miembros en overview: {len(members)}")
    
    logger.section("13. ELIMINAR USUARIO TEMPORAL")
    if test_username != user_creds['username']:
        response = client_admin.delete(f"/api/admin/delete/{test_username}")
        if verify_response(response, 200, logger, "Eliminar usuario temporal"):
            logger.success("Usuario temporal eliminado")
    else:
        logger.info("Saltando eliminación de usuario de prueba principal")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_admin()
    sys.exit(0 if success else 1)
