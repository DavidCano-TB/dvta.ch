#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE AUTENTICACIÓN Y SESIONES
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time

def test_autenticacion():
    logger = TestLogger("autenticacion")
    config = load_config()
    
    base_url = config['server']['base_url']
    admin_creds = config['credentials']['admin']
    user_creds = config['credentials']['test_user']
    
    client = TestClient(base_url, logger)
    
    logger.section("1. HEALTH CHECK")
    response = client.get("/api/health")
    if verify_response(response, 200, logger, "Health check"):
        data = response.json()
        logger.info(f"Estado del servidor: {data.get('status')}")
        logger.info(f"Timestamp: {data.get('time')}")
    
    logger.section("2. LOGIN EXITOSO")
    response = client.post("/api/login", json={
        "username": user_creds['username'],
        "password": user_creds['password']
    })
    
    if verify_response(response, 200, logger, "Login exitoso"):
        data = response.json()
        required_fields = ['token', 'username', 'is_admin', 'is_superadmin']
        if verify_json_fields(data, required_fields, logger, "Respuesta de login"):
            token = data['token']
            logger.success(f"Token obtenido: {token[:20]}...")
            client.token = token
            client.session.headers.update({'Authorization': f'Bearer {token}'})
    
    logger.section("3. LOGIN FALLIDO - CONTRASEÑA INCORRECTA")
    response = client.post("/api/login", json={
        "username": user_creds['username'],
        "password": "contraseña_incorrecta"
    })
    
    if response and response.status_code == 401:
        logger.success("Login con contraseña incorrecta bloqueado")
    else:
        logger.fail("Se permitió login con contraseña incorrecta")
    
    logger.section("4. LOGIN FALLIDO - USUARIO INEXISTENTE")
    response = client.post("/api/login", json={
        "username": "usuario_que_no_existe_12345",
        "password": "cualquier_password"
    })
    
    if response and response.status_code == 401:
        logger.success("Login con usuario inexistente bloqueado")
    else:
        logger.fail("Se permitió login con usuario inexistente")
    
    logger.section("5. OBTENER PERFIL (/api/me)")
    response = client.get("/api/me")
    if verify_response(response, 200, logger, "Obtener perfil"):
        data = response.json()
        required_fields = ['username', 'balance', 'is_admin', 'is_superadmin']
        if verify_json_fields(data, required_fields, logger, "Datos de perfil"):
            logger.info(f"Usuario: {data['username']}")
            logger.info(f"Balance: {data['balance']} DVDcoins")
            logger.info(f"Admin: {data['is_admin']}")
    
    logger.section("6. ACCESO SIN TOKEN")
    client_sin_token = TestClient(base_url, logger)
    response = client_sin_token.get("/api/me")
    
    if response and response.status_code == 401:
        logger.success("Acceso sin token bloqueado correctamente")
    else:
        logger.fail("Se permitió acceso sin token")
    
    logger.section("7. ACCESO CON TOKEN INVÁLIDO")
    client_token_invalido = TestClient(base_url, logger)
    client_token_invalido.token = "token_invalido_12345"
    client_token_invalido.session.headers.update({
        'Authorization': 'Bearer token_invalido_12345'
    })
    
    response = client_token_invalido.get("/api/me")
    
    if response and response.status_code == 401:
        logger.success("Acceso con token inválido bloqueado")
    else:
        logger.fail("Se permitió acceso con token inválido")
    
    logger.section("8. REFRESH TOKEN")
    response = client.post("/api/me/refresh-token")
    if verify_response(response, 200, logger, "Refresh token"):
        data = response.json()
        if 'token' in data:
            new_token = data['token']
            logger.success(f"Nuevo token obtenido: {new_token[:20]}...")
            
            # Verificar que el nuevo token funciona
            client.token = new_token
            client.session.headers.update({'Authorization': f'Bearer {new_token}'})
            
            response = client.get("/api/me")
            if response and response.status_code == 200:
                logger.success("Nuevo token funciona correctamente")
            else:
                logger.fail("Nuevo token no funciona")
    
    logger.section("9. CAMBIAR CONTRASEÑA")
    response = client.post("/api/me/change-password", json={
        "old_password": user_creds['password'],
        "new_password": "nueva_password_temporal"
    })
    
    if verify_response(response, 200, logger, "Cambiar contraseña"):
        logger.success("Contraseña cambiada correctamente")
        
        # Verificar que la nueva contraseña funciona
        client_nuevo = TestClient(base_url, logger)
        response = client_nuevo.post("/api/login", json={
            "username": user_creds['username'],
            "password": "nueva_password_temporal"
        })
        
        if response and response.status_code == 200:
            logger.success("Login con nueva contraseña exitoso")
            
            # Restaurar contraseña original
            client_nuevo.token = response.json()['token']
            client_nuevo.session.headers.update({
                'Authorization': f'Bearer {client_nuevo.token}'
            })
            
            response = client_nuevo.post("/api/me/change-password", json={
                "old_password": "nueva_password_temporal",
                "new_password": user_creds['password']
            })
            
            if response and response.status_code == 200:
                logger.success("Contraseña restaurada a la original")
        else:
            logger.fail("Login con nueva contraseña falló")
    
    logger.section("10. CAMBIAR CONTRASEÑA - CONTRASEÑA ACTUAL INCORRECTA")
    response = client.post("/api/me/change-password", json={
        "old_password": "contraseña_incorrecta",
        "new_password": "nueva_password"
    })
    
    if response and response.status_code != 200:
        logger.success("Cambio de contraseña con contraseña actual incorrecta bloqueado")
    else:
        logger.fail("Se permitió cambio de contraseña con contraseña actual incorrecta")
    
    logger.section("11. PING (MANTENER SESIÓN ACTIVA)")
    response = client.post("/api/ping")
    if verify_response(response, 200, logger, "Ping"):
        logger.success("Ping exitoso - sesión mantenida activa")
    
    logger.section("12. PREFERENCIAS DE IDIOMA")
    
    # Establecer idioma
    response = client.post("/api/me/lang", json={"lang": "es"})
    if verify_response(response, 200, logger, "Establecer idioma"):
        logger.success("Idioma establecido a español")
    
    # Obtener idioma
    response = client.get("/api/me/lang")
    if verify_response(response, 200, logger, "Obtener idioma"):
        data = response.json()
        if data.get('lang') == 'es':
            logger.success("Idioma recuperado correctamente")
        else:
            logger.fail(f"Idioma incorrecto: {data.get('lang')}")
    
    logger.section("13. REGISTRO DE NUEVO USUARIO")
    test_username = f"test_reg_{int(time.time())}"
    
    response = client.post("/api/register", json={
        "username": test_username,
        "password": "test123"
    })
    
    if verify_response(response, 200, logger, "Registrar nuevo usuario"):
        data = response.json()
        logger.success(f"Usuario {test_username} registrado")
        
        # Verificar que puede hacer login
        client_nuevo = TestClient(base_url, logger)
        if client_nuevo.login(test_username, "test123"):
            logger.success("Login con usuario recién registrado exitoso")
            
            # Limpiar: eliminar usuario de prueba (requiere admin)
            client_admin = TestClient(base_url, logger)
            if client_admin.login(admin_creds['username'], admin_creds['password']):
                response = client_admin.delete(f"/api/admin/delete/{test_username}")
                if response and response.status_code == 200:
                    logger.success("Usuario de prueba eliminado")
    
    logger.section("14. REGISTRO - USUARIO DUPLICADO")
    response = client.post("/api/register", json={
        "username": user_creds['username'],
        "password": "cualquier_password"
    })
    
    if response and response.status_code != 200:
        logger.success("Registro de usuario duplicado bloqueado")
    else:
        logger.fail("Se permitió registro de usuario duplicado")
    
    logger.section("15. RATE LIMITING EN LOGIN")
    logger.info("Probando rate limiting (20/minuto)...")
    
    rate_limit_hit = False
    for i in range(25):
        response = client.post("/api/login", json={
            "username": "usuario_inexistente",
            "password": "password"
        })
        
        if response and response.status_code == 429:
            rate_limit_hit = True
            logger.success(f"Rate limit activado en intento #{i+1}")
            break
        
        time.sleep(0.1)
    
    if not rate_limit_hit:
        logger.warning("No se alcanzó el rate limit en 25 intentos")
    
    return logger.summary()

if __name__ == "__main__":
    success = test_autenticacion()
    sys.exit(0 if success else 1)
