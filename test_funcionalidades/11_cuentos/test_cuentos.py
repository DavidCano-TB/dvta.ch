#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE CUENTOS
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response
import io

def test_cuentos():
    logger = TestLogger("cuentos")
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
    
    logger.section("2. VERIFICAR ESTADO")
    response = client_user.get("/api/cuentos/status")
    if verify_response(response, 200, logger, "Obtener estado"):
        status = response.json()
        logger.info(f"Cuentos habilitados: {status.get('enabled', False)}")
    
    logger.section("3. HABILITAR CUENTOS (ADMIN)")
    response = client_admin.post("/api/cuentos/toggle", json={"enabled": True})
    if verify_response(response, 200, logger, "Habilitar cuentos"):
        logger.success("Cuentos habilitados")
    
    logger.section("4. LISTAR CUENTOS")
    response = client_user.get("/api/cuentos/list")
    if verify_response(response, 200, logger, "Listar cuentos"):
        cuentos = response.json()
        logger.info(f"Cuentos disponibles: {len(cuentos)}")
    
    logger.section("5. SUBIR CUENTO (ADMIN)")
    # Crear archivo de prueba
    test_content = "Érase una vez en un lugar muy lejano..."
    test_file = io.BytesIO(test_content.encode('utf-8'))
    
    files = {'file': ('cuento_prueba.txt', test_file, 'text/plain')}
    
    # Nota: requests maneja multipart/form-data automáticamente
    response = client_admin.session.post(
        f"{base_url}/api/cuentos/upload",
        files=files,
        headers={'Authorization': f'Bearer {client_admin.token}'}
    )
    
    if verify_response(response, 200, logger, "Subir cuento"):
        logger.success("Cuento subido correctamente")
    
    logger.section("6. OBTENER CUENTO")
    response = client_user.get("/api/cuentos/file/cuento_prueba.txt")
    if verify_response(response, 200, logger, "Obtener cuento"):
        content = response.text
        if "Érase una vez" in content:
            logger.success("Contenido del cuento correcto")
        else:
            logger.fail("Contenido del cuento incorrecto")
    
    logger.section("7. ENMASCARAR CUENTO (ADMIN)")
    response = client_admin.post("/api/cuentos/mask/cuento_prueba.txt")
    if verify_response(response, 200, logger, "Enmascarar cuento"):
        logger.success("Cuento enmascarado")
    
    # Verificar que el usuario no puede verlo
    response = client_user.get("/api/cuentos/list")
    if response and response.status_code == 200:
        cuentos = response.json()
        if "cuento_prueba.txt" not in cuentos:
            logger.success("Cuento enmascarado correctamente para usuarios")
        else:
            logger.fail("Cuento aún visible para usuarios")
    
    logger.section("8. DESENMASCARAR CUENTO (ADMIN)")
    response = client_admin.post("/api/cuentos/unmask/cuento_prueba.txt")
    if verify_response(response, 200, logger, "Desenmascarar cuento"):
        logger.success("Cuento desenmascarado")
    
    logger.section("9. ELIMINAR CUENTO (ADMIN)")
    response = client_admin.delete("/api/cuentos/file/cuento_prueba.txt")
    if verify_response(response, 200, logger, "Eliminar cuento"):
        logger.success("Cuento eliminado")
    
    logger.section("10. DESHABILITAR CUENTOS (ADMIN)")
    response = client_admin.post("/api/cuentos/toggle", json={"enabled": False})
    if verify_response(response, 200, logger, "Deshabilitar cuentos"):
        logger.success("Cuentos deshabilitados")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_cuentos()
    sys.exit(0 if success else 1)
