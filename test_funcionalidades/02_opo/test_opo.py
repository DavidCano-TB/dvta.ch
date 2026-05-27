#!/usr/bin/env python3
"""
🧪 TEST COMPLETO: SISTEMA DE OPOSICIONES (OPO)
Verifica todas las funcionalidades del sistema de oposiciones
"""
import sys
import os

# Importar desde directorio local primero
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_utils import TestLogger, TestClient, load_config, verify_response, verify_json_fields
import time
import json

def test_opo():
    """Test completo del sistema OPO"""
    logger = TestLogger("opo")
    config = load_config()
    
    base_url = config['server']['base_url']
    admin_creds = config['credentials']['admin']
    user_creds = config['credentials']['test_user']
    
    client_admin = TestClient(base_url, logger)
    client_user = TestClient(base_url, logger)
    
    # ========================================================================
    # 1. AUTENTICACIÓN
    # ========================================================================
    logger.section("1. AUTENTICACIÓN")
    
    if not client_admin.login(admin_creds['username'], admin_creds['password']):
        return logger.summary()
    
    if not client_user.login(user_creds['username'], user_creds['password']):
        return logger.summary()
    
    # ========================================================================
    # 2. VERIFICAR ESTADO INICIAL
    # ========================================================================
    logger.section("2. VERIFICAR ESTADO INICIAL DEL SISTEMA OPO")
    
    response = client_admin.get("/api/opo/status")
    if verify_response(response, 200, logger, "Obtener estado OPO"):
        status = response.json()
        logger.info(f"OPO habilitado: {status.get('enabled', False)}")
        logger.info(f"Jugadores registrados: {len(status.get('players', []))}")
    
    # ========================================================================
    # 3. GESTIÓN DE JUGADORES (ADMIN)
    # ========================================================================
    logger.section("3. GESTIÓN DE JUGADORES")
    
    # 3.1 Añadir jugador
    response = client_admin.post("/api/opo/players/add", json={
        "username": user_creds['username']
    })
    if verify_response(response, 200, logger, "Añadir jugador"):
        logger.success(f"Jugador {user_creds['username']} añadido")
    
    # 3.2 Listar jugadores
    response = client_admin.get("/api/opo/players")
    if verify_response(response, 200, logger, "Listar jugadores"):
        players = response.json()
        logger.info(f"Total de jugadores: {len(players)}")
        if any(p['username'] == user_creds['username'] for p in players):
            logger.success("Jugador encontrado en la lista")
        else:
            logger.fail("Jugador NO encontrado en la lista")
    
    # ========================================================================
    # 4. GESTIÓN DE PREGUNTAS
    # ========================================================================
    logger.section("4. GESTIÓN DE PREGUNTAS")
    
    # 4.1 Cargar preguntas de prueba
    test_questions = [
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "opciones": {"A": "Londres", "B": "París", "C": "Berlín", "D": "Madrid"},
            "respuesta": "B",
            "tema": "Geografía"
        },
        {
            "pregunta": "¿En qué año llegó el hombre a la Luna?",
            "opciones": {"A": "1965", "B": "1967", "C": "1969", "D": "1971"},
            "respuesta": "C",
            "tema": "Historia"
        },
        {
            "pregunta": "¿Cuál es el resultado de 2+2?",
            "opciones": {"A": "3", "B": "4", "C": "5", "D": "6"},
            "respuesta": "B",
            "tema": "Matemáticas"
        }
    ]
    
    response = client_admin.post("/api/opo/questions/bulk", json={
        "questions": test_questions
    })
    if verify_response(response, 200, logger, "Cargar preguntas en bulk"):
        logger.success(f"Cargadas {len(test_questions)} preguntas de prueba")
    
    # 4.2 Listar preguntas
    response = client_admin.get("/api/opo/questions")
    if verify_response(response, 200, logger, "Listar preguntas"):
        questions = response.json()
        logger.info(f"Total de preguntas en el sistema: {len(questions)}")
        
        if questions:
            q = questions[0]
            required_fields = ['id', 'pregunta', 'opciones', 'respuesta', 'tema']
            verify_json_fields(q, required_fields, logger, "Estructura de pregunta")
    
    # ========================================================================
    # 5. INICIAR SESIÓN DE OPO
    # ========================================================================
    logger.section("5. INICIAR SESIÓN DE OPO")
    
    response = client_admin.post("/api/opo/session/start", json={
        "num_questions": 3,
        "time_per_question": 30
    })
    if verify_response(response, 200, logger, "Iniciar sesión OPO"):
        session_data = response.json()
        logger.success("Sesión OPO iniciada")
        logger.info(f"ID de sesión: {session_data.get('session_id')}")
    
    # ========================================================================
    # 6. RESPONDER PREGUNTAS (USUARIO)
    # ========================================================================
    logger.section("6. RESPONDER PREGUNTAS")
    
    # Obtener pregunta actual
    response = client_user.get("/api/opo/current-question")
    if verify_response(response, 200, logger, "Obtener pregunta actual"):
        question = response.json()
        logger.info(f"Pregunta: {question.get('pregunta', '')[:50]}...")
        
        # Responder pregunta
        response = client_user.post("/api/opo/answer", json={
            "question_id": question.get('id'),
            "answer": "B"
        })
        if verify_response(response, 200, logger, "Enviar respuesta"):
            result = response.json()
            logger.info(f"Respuesta {'correcta' if result.get('correct') else 'incorrecta'}")
    
    # ========================================================================
    # 7. RESULTADOS Y ESTADÍSTICAS
    # ========================================================================
    logger.section("7. RESULTADOS Y ESTADÍSTICAS")
    
    # Finalizar sesión
    response = client_admin.post("/api/opo/session/end")
    if verify_response(response, 200, logger, "Finalizar sesión"):
        logger.success("Sesión finalizada")
    
    # Obtener resultados
    response = client_admin.get("/api/opo/results")
    if verify_response(response, 200, logger, "Obtener resultados"):
        results = response.json()
        logger.info(f"Resultados de {len(results)} jugadores")
        
        for result in results:
            logger.info(f"  {result.get('username')}: {result.get('score')} puntos")
    
    # ========================================================================
    # 8. HISTORIAL DE SESIONES
    # ========================================================================
    logger.section("8. HISTORIAL DE SESIONES")
    
    response = client_admin.get("/api/opo/sessions")
    if verify_response(response, 200, logger, "Obtener historial de sesiones"):
        sessions = response.json()
        logger.info(f"Total de sesiones: {len(sessions)}")
        
        if sessions:
            session = sessions[0]
            required_fields = ['id', 'start_time', 'end_time', 'num_questions']
            verify_json_fields(session, required_fields, logger, "Estructura de sesión")
    
    # ========================================================================
    # 9. ESTADÍSTICAS POR JUGADOR
    # ========================================================================
    logger.section("9. ESTADÍSTICAS POR JUGADOR")
    
    response = client_admin.get(f"/api/opo/player-stats/{user_creds['username']}")
    if verify_response(response, 200, logger, "Obtener estadísticas de jugador"):
        stats = response.json()
        logger.info(f"Sesiones jugadas: {stats.get('sessions_played', 0)}")
        logger.info(f"Puntuación media: {stats.get('average_score', 0)}")
        logger.info(f"Mejor puntuación: {stats.get('best_score', 0)}")
    
    # ========================================================================
    # 10. LIMPIEZA
    # ========================================================================
    logger.section("10. LIMPIEZA")
    
    # Eliminar jugador de prueba
    response = client_admin.delete(f"/api/opo/players/{user_creds['username']}")
    if verify_response(response, 200, logger, "Eliminar jugador"):
        logger.success("Jugador eliminado correctamente")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    return logger.summary()


if __name__ == "__main__":
    success = test_opo()
    sys.exit(0 if success else 1)
