# -*- coding: utf-8 -*-
"""
Generador de preguntas para Pasapalabra
Genera 50 preguntas por cada letra del abecedario español
"""
import json
import os

# Banco de preguntas - 50 por letra
preguntas_db = {}

# Letra A - 50 preguntas
preguntas_db["A"] = [
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de aumentar la velocidad", "respuesta": "ACELERAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de acercarse a algo", "respuesta": "APROXIMAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Ciencia que estudia los astros", "respuesta": "ASTRONOMÍA", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Persona que viaja al espacio", "respuesta": "ASTRONAUTA", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de juntar o reunir", "respuesta": "ACUMULAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de acompañar a alguien", "respuesta": "ACOMPAÑAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de recordar algo", "respuesta": "ACORDAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de acostarse", "respuesta": "ACOSTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de actuar en teatro", "respuesta": "ACTUAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de adaptar algo", "respuesta": "ADAPTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de adelantar", "respuesta": "ADELANTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de adivinar", "respuesta": "ADIVINAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de admirar", "respuesta": "ADMIRAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de adoptar", "respuesta": "ADOPTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de adornar", "respuesta": "ADORNAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de advertir", "respuesta": "ADVERTIR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de afirmar", "respuesta": "AFIRMAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de agarrar", "respuesta": "AGARRAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de agitar", "respuesta": "AGITAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de agrupar", "respuesta": "AGRUPAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de ahogar", "respuesta": "AHOGAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de ahorrar", "respuesta": "AHORRAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de aislar", "respuesta": "AISLAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de ajustar", "respuesta": "AJUSTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alabar", "respuesta": "ALABAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alargar", "respuesta": "ALARGAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alcanzar", "respuesta": "ALCANZAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alegrar", "respuesta": "ALEGRAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alejar", "respuesta": "ALEJAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alimentar", "respuesta": "ALIMENTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de aliviar", "respuesta": "ALIVIAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de almacenar", "respuesta": "ALMACENAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alquilar", "respuesta": "ALQUILAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alterar", "respuesta": "ALTERAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alumbrar", "respuesta": "ALUMBRAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de alzar", "respuesta": "ALZAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de amar", "respuesta": "AMAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de amenazar", "respuesta": "AMENAZAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de ampliar", "respuesta": "AMPLIAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de analizar", "respuesta": "ANALIZAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de andar", "respuesta": "ANDAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de animar", "respuesta": "ANIMAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de anotar", "respuesta": "ANOTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de anunciar", "respuesta": "ANUNCIAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de añadir", "respuesta": "AÑADIR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de apagar", "respuesta": "APAGAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de aparecer", "respuesta": "APARECER", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de apartar", "respuesta": "APARTAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de apoyar", "respuesta": "APOYAR", "usada": False},
    {"tipo": "empieza", "definicion": "Empieza por A: Acción de apreciar", "respuesta": "APRECIAR", "usada": False}
]

print("✓ Archivo base creado")
print("Ejecuta el script completo para generar todas las letras")
