#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: GALERÍA DE IMÁGENES
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response
import io
from PIL import Image

def test_galeria():
    logger = TestLogger("galeria")
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
    
    logger.section("2. LISTAR IMÁGENES")
    response = client_user.get("/api/gallery/list")
    if verify_response(response, 200, logger, "Listar imágenes"):
        images = response.json()
        logger.info(f"Imágenes en galería: {len(images)}")
    
    logger.section("3. SUBIR IMAGEN (ADMIN)")
    
    # Crear imagen de prueba
    try:
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('test_image.png', img_bytes, 'image/png')}
        
        response = client_admin.session.post(
            f"{base_url}/api/gallery/upload",
            files=files,
            headers={'Authorization': f'Bearer {client_admin.token}'}
        )
        
        if verify_response(response, 200, logger, "Subir imagen"):
            data = response.json()
            image_filename = data.get('filename', 'test_image.png')
            logger.success(f"Imagen subida: {image_filename}")
        else:
            image_filename = None
    except ImportError:
        logger.warning("PIL no disponible, saltando prueba de subida de imagen")
        image_filename = None
    except Exception as e:
        logger.fail(f"Error al crear imagen de prueba", e)
        image_filename = None
    
    logger.section("4. OBTENER IMAGEN")
    if image_filename:
        response = client_user.get(f"/static/gallery/{image_filename}")
        if verify_response(response, 200, logger, "Obtener imagen"):
            logger.success("Imagen descargada correctamente")
            logger.info(f"Tamaño: {len(response.content)} bytes")
    else:
        logger.info("Saltando obtención de imagen (no se subió)")
    
    logger.section("5. ELIMINAR IMAGEN (ADMIN)")
    if image_filename:
        response = client_admin.delete(f"/api/gallery/delete/{image_filename}")
        if verify_response(response, 200, logger, "Eliminar imagen"):
            logger.success("Imagen eliminada correctamente")
    else:
        logger.info("Saltando eliminación de imagen")
    
    logger.section("6. VERIFICAR PERMISOS")
    # Usuario no admin no debería poder subir
    try:
        img = Image.new('RGB', (50, 50), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('test_user_image.png', img_bytes, 'image/png')}
        
        response = client_user.session.post(
            f"{base_url}/api/gallery/upload",
            files=files,
            headers={'Authorization': f'Bearer {client_user.token}'}
        )
        
        if response and response.status_code == 403:
            logger.success("Usuario no admin no puede subir imágenes")
        elif response and response.status_code == 200:
            logger.fail("Usuario no admin pudo subir imagen")
        else:
            logger.warning(f"Respuesta inesperada: {response.status_code if response else 'None'}")
    except ImportError:
        logger.info("PIL no disponible, saltando prueba de permisos")
    except Exception as e:
        logger.warning(f"Error en prueba de permisos: {str(e)}")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_galeria()
    sys.exit(0 if success else 1)
