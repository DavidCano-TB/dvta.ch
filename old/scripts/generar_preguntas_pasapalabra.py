# -*- coding: utf-8 -*-
import json

preguntas = {
    "A": [
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de aumentar la velocidad", "respuesta": "ACELERAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de acercarse a algo", "respuesta": "APROXIMAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Ciencia que estudia los astros", "respuesta": "ASTRONOMÍA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Persona que viaja al espacio", "respuesta": "ASTRONAUTA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de juntar o reunir", "respuesta": "ACUMULAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de acompañar a alguien", "respuesta": "ACOMPAÑAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de recordar algo", "respuesta": "ACORDAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de acostarse o dormir", "respuesta": "ACOSTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de actuar en teatro", "respuesta": "ACTUAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de adaptar algo", "respuesta": "ADAPTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de adelantar en el camino", "respuesta": "ADELANTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de adivinar algo", "respuesta": "ADIVINAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de admirar algo", "respuesta": "ADMIRAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de adoptar un hijo", "respuesta": "ADOPTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de adornar algo", "respuesta": "ADORNAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de advertir un peligro", "respuesta": "ADVERTIR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de afirmar algo", "respuesta": "AFIRMAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de agarrar con fuerza", "respuesta": "AGARRAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de agitar un líquido", "respuesta": "AGITAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de agrupar elementos", "respuesta": "AGRUPAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de ahogar en agua", "respuesta": "AHOGAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de ahorrar dinero", "respuesta": "AHORRAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de aislar algo", "respuesta": "AISLAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de ajustar una pieza", "respuesta": "AJUSTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alabar a alguien", "respuesta": "ALABAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alargar algo", "respuesta": "ALARGAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alcanzar un objetivo", "respuesta": "ALCANZAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alegrar a alguien", "respuesta": "ALEGRAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alejar algo", "respuesta": "ALEJAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alimentar a alguien", "respuesta": "ALIMENTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de aliviar un dolor", "respuesta": "ALIVIAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de almacenar cosas", "respuesta": "ALMACENAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alquilar una casa", "respuesta": "ALQUILAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alterar el orden", "respuesta": "ALTERAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alumbrar con luz", "respuesta": "ALUMBRAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de alzar algo", "respuesta": "ALZAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de amar a alguien", "respuesta": "AMAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de amenazar a alguien", "respuesta": "AMENAZAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de ampliar algo", "respuesta": "AMPLIAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de analizar datos", "respuesta": "ANALIZAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de andar o caminar", "respuesta": "ANDAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de animar a alguien", "respuesta": "ANIMAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de anotar algo", "respuesta": "ANOTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de anunciar noticias", "respuesta": "ANUNCIAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de añadir algo", "respuesta": "AÑADIR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de apagar el fuego", "respuesta": "APAGAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de aparecer en escena", "respuesta": "APARECER", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de apartar algo", "respuesta": "APARTAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de apoyar a alguien", "respuesta": "APOYAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por A: Acción de apreciar algo", "respuesta": "APRECIAR", "usada": False}
    ]
}

# Guardar el archivo JSON
with open('static/pasapalabra/preguntas.json', 'w', encoding='utf-8') as f:
    json.dump(preguntas, f, ensure_ascii=False, indent=2)

print("✓ Archivo preguntas.json generado con éxito")
print(f"Total de letras: {len(preguntas)}")
for letra, lista in preguntas.items():
    print(f"  {letra}: {len(lista)} preguntas")
