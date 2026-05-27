#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE VOTACIONES
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields

def test_votaciones():
    logger = TestLogger("votaciones")
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
    response = client_user.get("/game_pages/votaciones/votaciones.html")
    if verify_response(response, 200, logger, "Cargar página"):
        logger.success("Página de votaciones cargada")
    
    logger.section("3. LISTAR VOTACIONES")
    response = client_user.get("/api/votaciones/list")
    if verify_response(response, 200, logger, "Listar votaciones"):
        votaciones = response.json()
        logger.info(f"Votaciones disponibles: {len(votaciones)}")
    
    logger.section("4. CREAR VOTACIÓN (ADMIN)")
    response = client_admin.post("/api/votaciones/create", json={
        "titulo": "Votación de Prueba",
        "descripcion": "Esta es una votación de prueba",
        "opciones": ["Opción A", "Opción B", "Opción C"],
        "tipo": "simple",
        "fecha_fin": "2026-12-31T23:59:59"
    })
    
    votacion_id = None
    if verify_response(response, 200, logger, "Crear votación"):
        data = response.json()
        votacion_id = data.get('votacion_id')
        logger.success(f"Votación creada con ID: {votacion_id}")
    
    if not votacion_id:
        logger.fail("No se pudo crear la votación")
        return logger.summary()
    
    logger.section("5. OBTENER DETALLES")
    response = client_user.get(f"/api/votaciones/{votacion_id}")
    if verify_response(response, 200, logger, "Obtener detalles"):
        votacion = response.json()
        logger.info(f"Título: {votacion.get('titulo')}")
        logger.info(f"Opciones: {len(votacion.get('opciones', []))}")
    
    logger.section("6. VOTAR")
    response = client_user.post(f"/api/votaciones/{votacion_id}/votar", json={
        "opcion_id": 1
    })
    if verify_response(response, 200, logger, "Emitir voto"):
        logger.success("Voto emitido correctamente")
    
    logger.section("7. VERIFICAR VOTO DUPLICADO")
    response = client_user.post(f"/api/votaciones/{votacion_id}/votar", json={
        "opcion_id": 2
    })
    if response and response.status_code != 200:
        logger.success("Voto duplicado bloqueado correctamente")
    else:
        logger.fail("Se permitió voto duplicado")
    
    logger.section("8. RESULTADOS")
    response = client_user.get(f"/api/votaciones/{votacion_id}/resultados")
    if verify_response(response, 200, logger, "Obtener resultados"):
        resultados = response.json()
        logger.info(f"Total votos: {resultados.get('total_votos', 0)}")
    
    logger.section("9. CERRAR VOTACIÓN (ADMIN)")
    response = client_admin.post(f"/api/votaciones/{votacion_id}/cerrar")
    if verify_response(response, 200, logger, "Cerrar votación"):
        logger.success("Votación cerrada")
    
    logger.section("10. ELIMINAR VOTACIÓN (ADMIN)")
    response = client_admin.delete(f"/api/votaciones/{votacion_id}")
    if verify_response(response, 200, logger, "Eliminar votación"):
        logger.success("Votación eliminada")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_votaciones()
    sys.exit(0 if success else 1)
