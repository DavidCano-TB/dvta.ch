#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE TRANSFERENCIAS
Verifica todas las funcionalidades del sistema de transacciones DVDcoin
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time

def test_transferencias():
    """Test completo del sistema de transferencias"""
    logger = TestLogger("transferencias")
    config = load_config()
    
    base_url = config['server']['base_url']
    admin_creds = config['credentials']['admin']
    user1_creds = config['credentials']['test_user']
    user2_creds = config['credentials']['test_user2']
    
    client_admin = TestClient(base_url, logger)
    client_user1 = TestClient(base_url, logger)
    client_user2 = TestClient(base_url, logger)
    
    # ========================================================================
    # 1. AUTENTICACIÓN
    # ========================================================================
    logger.section("1. AUTENTICACIÓN Y SETUP")
    
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        logger.fail("No se pudo autenticar como admin")
        return logger.summary()
    
    if not client_user1.login(user1_creds['username'], user1_creds['password']):
        logger.fail("No se pudo autenticar como user1")
        return logger.summary()
    
    if not client_user2.login(user2_creds['username'], user2_creds['password']):
        logger.fail("No se pudo autenticar como user2")
        return logger.summary()
    
    # ========================================================================
    # 2. VERIFICAR BALANCE INICIAL
    # ========================================================================
    logger.section("2. VERIFICAR BALANCE INICIAL")
    
    response = client_user1.get("/api/me")
    if verify_response(response, 200, logger, "Obtener perfil user1"):
        data = response.json()
        balance_inicial_user1 = data.get('balance', 0)
        logger.info(f"Balance inicial user1: {balance_inicial_user1} DVDcoins")
    else:
        return logger.summary()
    
    response = client_user2.get("/api/me")
    if verify_response(response, 200, logger, "Obtener perfil user2"):
        data = response.json()
        balance_inicial_user2 = data.get('balance', 0)
        logger.info(f"Balance inicial user2: {balance_inicial_user2} DVDcoins")
    else:
        return logger.summary()
    
    # ========================================================================
    # 3. LISTAR USUARIOS DISPONIBLES
    # ========================================================================
    logger.section("3. LISTAR USUARIOS DISPONIBLES")
    
    response = client_user1.get("/api/users")
    if verify_response(response, 200, logger, "Listar usuarios"):
        users = response.json()
        logger.info(f"Usuarios disponibles: {len(users)}")
        if user2_creds['username'] in users:
            logger.success(f"Usuario {user2_creds['username']} encontrado en la lista")
        else:
            logger.fail(f"Usuario {user2_creds['username']} NO encontrado en la lista")
    
    # ========================================================================
    # 4. TRANSFERENCIA BÁSICA
    # ========================================================================
    logger.section("4. TRANSFERENCIA BÁSICA")
    
    monto_transferencia = 10
    response = client_user1.post("/api/transfer", json={
        "to_user": user2_creds['username'],
        "amount": monto_transferencia,
        "message": "Test de transferencia básica"
    })
    
    if verify_response(response, 200, logger, "Realizar transferencia"):
        data = response.json()
        logger.info(f"Transferencia exitosa: {data.get('message')}")
        
        # Verificar nuevo balance user1
        response = client_user1.get("/api/me")
        if response and response.status_code == 200:
            nuevo_balance = response.json().get('balance', 0)
            esperado = balance_inicial_user1 - monto_transferencia
            if nuevo_balance == esperado:
                logger.success(f"Balance user1 actualizado correctamente: {nuevo_balance}")
            else:
                logger.fail(f"Balance user1 incorrecto: {nuevo_balance}, esperado: {esperado}")
        
        # Verificar nuevo balance user2
        response = client_user2.get("/api/me")
        if response and response.status_code == 200:
            nuevo_balance = response.json().get('balance', 0)
            esperado = balance_inicial_user2 + monto_transferencia
            if nuevo_balance == esperado:
                logger.success(f"Balance user2 actualizado correctamente: {nuevo_balance}")
            else:
                logger.fail(f"Balance user2 incorrecto: {nuevo_balance}, esperado: {esperado}")
    
    # ========================================================================
    # 5. VALIDACIONES DE TRANSFERENCIA
    # ========================================================================
    logger.section("5. VALIDACIONES DE TRANSFERENCIA")
    
    # 5.1 Transferencia a sí mismo
    response = client_user1.post("/api/transfer", json={
        "to_user": user1_creds['username'],
        "amount": 5,
        "message": "Transferencia a mí mismo"
    })
    if response and response.status_code != 200:
        logger.success("Transferencia a sí mismo bloqueada correctamente")
    else:
        logger.fail("Se permitió transferencia a sí mismo")
    
    # 5.2 Monto negativo
    response = client_user1.post("/api/transfer", json={
        "to_user": user2_creds['username'],
        "amount": -10,
        "message": "Monto negativo"
    })
    if response and response.status_code != 200:
        logger.success("Monto negativo bloqueado correctamente")
    else:
        logger.fail("Se permitió monto negativo")
    
    # 5.3 Monto cero
    response = client_user1.post("/api/transfer", json={
        "to_user": user2_creds['username'],
        "amount": 0,
        "message": "Monto cero"
    })
    if response and response.status_code != 200:
        logger.success("Monto cero bloqueado correctamente")
    else:
        logger.fail("Se permitió monto cero")
    
    # 5.4 Usuario inexistente
    response = client_user1.post("/api/transfer", json={
        "to_user": "usuario_que_no_existe_12345",
        "amount": 5,
        "message": "Usuario inexistente"
    })
    if response and response.status_code != 200:
        logger.success("Transferencia a usuario inexistente bloqueada")
    else:
        logger.fail("Se permitió transferencia a usuario inexistente")
    
    # 5.5 Saldo insuficiente
    response = client_user1.get("/api/me")
    if response and response.status_code == 200:
        balance_actual = response.json().get('balance', 0)
        monto_excesivo = balance_actual + 1000
        
        response = client_user1.post("/api/transfer", json={
            "to_user": user2_creds['username'],
            "amount": monto_excesivo,
            "message": "Saldo insuficiente"
        })
        if response and response.status_code != 200:
            logger.success("Transferencia con saldo insuficiente bloqueada")
        else:
            logger.fail("Se permitió transferencia con saldo insuficiente")
    
    # ========================================================================
    # 6. HISTORIAL DE TRANSACCIONES
    # ========================================================================
    logger.section("6. HISTORIAL DE TRANSACCIONES")
    
    response = client_user1.get("/api/history")
    if verify_response(response, 200, logger, "Obtener historial user1"):
        history = response.json()
        logger.info(f"Transacciones en historial user1: {len(history)}")
        
        # Verificar que la última transacción sea la que hicimos
        if history:
            ultima = history[0]
            required_fields = ['id', 'from_user', 'to_user', 'amount', 'timestamp']
            if verify_json_fields(ultima, required_fields, logger, "Campos de transacción"):
                logger.info(f"Última transacción: {ultima['from_user']} → {ultima['to_user']}: {ultima['amount']} DVDcoins")
    
    response = client_user2.get("/api/history")
    if verify_response(response, 200, logger, "Obtener historial user2"):
        history = response.json()
        logger.info(f"Transacciones en historial user2: {len(history)}")
    
    # ========================================================================
    # 7. ADMIN: LEDGER COMPLETO
    # ========================================================================
    logger.section("7. ADMIN: LEDGER COMPLETO")
    
    response = client_admin.get("/api/admin/ledger")
    if verify_response(response, 200, logger, "Obtener ledger completo"):
        ledger = response.json()
        logger.info(f"Total de transacciones en el sistema: {len(ledger)}")
        
        if ledger:
            # Verificar estructura de transacción
            tx = ledger[0]
            required_fields = ['id', 'from_user', 'to_user', 'amount', 'timestamp', 'message']
            verify_json_fields(tx, required_fields, logger, "Estructura de transacción en ledger")
    
    # ========================================================================
    # 8. TRANSFERENCIAS MÚLTIPLES
    # ========================================================================
    logger.section("8. TRANSFERENCIAS MÚLTIPLES")
    
    for i in range(3):
        response = client_user2.post("/api/transfer", json={
            "to_user": user1_creds['username'],
            "amount": 2,
            "message": f"Transferencia múltiple #{i+1}"
        })
        if response and response.status_code == 200:
            logger.success(f"Transferencia múltiple #{i+1} exitosa")
        else:
            logger.fail(f"Transferencia múltiple #{i+1} falló")
        time.sleep(0.5)
    
    # ========================================================================
    # 9. LÍMITES DE RATE LIMITING
    # ========================================================================
    logger.section("9. LÍMITES DE RATE LIMITING")
    
    logger.info("Probando límites de rate limiting (30/minuto)...")
    rate_limit_hit = False
    
    for i in range(35):
        response = client_user1.post("/api/transfer", json={
            "to_user": user2_creds['username'],
            "amount": 1,
            "message": f"Rate limit test #{i+1}"
        })
        if response and response.status_code == 429:
            rate_limit_hit = True
            logger.success(f"Rate limit activado en intento #{i+1}")
            break
        time.sleep(0.1)
    
    if not rate_limit_hit:
        logger.warning("No se alcanzó el rate limit en 35 intentos")
    
    # ========================================================================
    # 10. ESTADÍSTICAS DE TRANSACCIONES
    # ========================================================================
    logger.section("10. ESTADÍSTICAS DE TRANSACCIONES")
    
    response = client_admin.get("/api/stats/transactions-summary")
    if verify_response(response, 200, logger, "Obtener estadísticas de transacciones"):
        stats = response.json()
        logger.info(f"Total enviado: {stats.get('total_sent', 0)} DVDcoins")
        logger.info(f"Total recibido: {stats.get('total_received', 0)} DVDcoins")
        logger.info(f"Top senders: {len(stats.get('top_senders', []))}")
        logger.info(f"Top receivers: {len(stats.get('top_receivers', []))}")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    return logger.summary()


if __name__ == "__main__":
    success = test_transferencias()
    sys.exit(0 if success else 1)
