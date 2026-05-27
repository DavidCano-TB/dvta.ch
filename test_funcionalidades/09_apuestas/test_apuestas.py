#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE APUESTAS
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time

def test_apuestas():
    logger = TestLogger("apuestas")
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
    
    logger.section("2. VERIFICAR PÁGINA")
    response = client_user.get("/game_pages/apuestas/apuestas.html")
    if verify_response(response, 200, logger, "Cargar página"):
        logger.success("Página de apuestas cargada")
    
    logger.section("3. LISTAR PORRAS")
    response = client_user.get("/api/apuestas/porras")
    if verify_response(response, 200, logger, "Listar porras"):
        porras = response.json()
        logger.info(f"Porras disponibles: {len(porras)}")
        
        if porras:
            porra = porras[0]
            required_fields = ['id', 'titulo', 'estado', 'opciones']
            verify_json_fields(porra, required_fields, logger, "Estructura de porra")
    
    logger.section("4. CREAR PORRA (ADMIN)")
    response = client_admin.post("/api/apuestas/porras/create", json={
        "titulo": "Porra de Prueba",
        "descripcion": "Esta es una porra de prueba",
        "opciones": [
            {"nombre": "Opción A", "cuota": 2.0},
            {"nombre": "Opción B", "cuota": 3.5},
            {"nombre": "Opción C", "cuota": 1.5}
        ],
        "fecha_cierre": "2026-12-31T23:59:59"
    })
    
    porra_id = None
    if verify_response(response, 200, logger, "Crear porra"):
        data = response.json()
        porra_id = data.get('porra_id')
        logger.success(f"Porra creada con ID: {porra_id}")
    
    if not porra_id:
        logger.fail("No se pudo crear la porra")
        return logger.summary()
    
    logger.section("5. OBTENER DETALLES DE PORRA")
    response = client_user.get(f"/api/apuestas/porras/{porra_id}")
    if verify_response(response, 200, logger, "Obtener detalles"):
        porra = response.json()
        logger.info(f"Título: {porra.get('titulo')}")
        logger.info(f"Opciones: {len(porra.get('opciones', []))}")
    
    logger.section("6. REALIZAR APUESTA")
    response = client_user.post(f"/api/apuestas/porras/{porra_id}/apostar", json={
        "opcion_id": 1,
        "cantidad": 10
    })
    if verify_response(response, 200, logger, "Realizar apuesta"):
        logger.success("Apuesta realizada correctamente")
    
    logger.section("7. MIS APUESTAS")
    response = client_user.get("/api/apuestas/mis-apuestas")
    if verify_response(response, 200, logger, "Obtener mis apuestas"):
        apuestas = response.json()
        logger.info(f"Apuestas activas: {len(apuestas)}")
    
    logger.section("8. CERRAR PORRA (ADMIN)")
    response = client_admin.post(f"/api/apuestas/porras/{porra_id}/cerrar")
    if verify_response(response, 200, logger, "Cerrar porra"):
        logger.success("Porra cerrada")
    
    logger.section("9. RESOLVER PORRA (ADMIN)")
    response = client_admin.post(f"/api/apuestas/porras/{porra_id}/resolver", json={
        "opcion_ganadora_id": 1
    })
    if verify_response(response, 200, logger, "Resolver porra"):
        logger.success("Porra resuelta")
    
    logger.section("10. ESTADÍSTICAS")
    response = client_admin.get("/api/apuestas/estadisticas")
    if verify_response(response, 200, logger, "Obtener estadísticas"):
        stats = response.json()
        logger.info(f"Total apostado: {stats.get('total_apostado', 0)}")
        logger.info(f"Porras activas: {stats.get('porras_activas', 0)}")
    
    logger.section("11. ELIMINAR PORRA (ADMIN)")
    response = client_admin.delete(f"/api/apuestas/porras/{porra_id}")
    if verify_response(response, 200, logger, "Eliminar porra"):
        logger.success("Porra eliminada")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_apuestas()
    sys.exit(0 if success else 1)
