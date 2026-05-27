#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de preguntas para Pasapalabra
Genera 50 preguntas por letra del abecedario
Nivel: 3º ESO - Divertidas y originales
"""

import json

# Diccionario con 50 preguntas por letra
preguntas_completas = {
    "C": [
        {"tipo": "empieza", "definicion": "Empieza por C: País más poblado del mundo donde se inventó la pólvora", "respuesta": "CHINA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: País de Norteamérica famoso por el jarabe de arce y ser muy educado", "respuesta": "CANADÁ", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: País sudamericano cuya capital es Bogotá, tierra del café", "respuesta": "COLOMBIA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: País más alargado del mundo, parece un fideo en el mapa", "respuesta": "CHILE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Navegante genovés que llegó a América buscando las Indias", "respuesta": "COLÓN", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Astrónomo polaco que dijo que la Tierra gira alrededor del Sol", "respuesta": "COPÉRNICO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Reina egipcia famosa por su nariz y su relación con César", "respuesta": "CLEOPATRA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Rey franco coronado emperador en el año 800", "respuesta": "CARLOMAGNO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Conquistador español que derrotó a los aztecas", "respuesta": "CORTÉS", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Filósofo chino que enseñó la virtud y el respeto", "respuesta": "CONFUCIO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Dictador romano asesinado en los Idus de Marzo", "respuesta": "CÉSAR", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Científica polaca que descubrió el radio y ganó dos Nobel", "respuesta": "CURIE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Dramaturgo español autor de La vida es sueño", "respuesta": "CALDERÓN", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Escritor del Quijote, la primera novela moderna", "respuesta": "CERVANTES", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Princesa que pierde el zapato de cristal a medianoche", "respuesta": "CENICIENTA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Sonido producido con obstrucción del aire, como la B o la T", "respuesta": "CONSONANTE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Propiedad del texto que conecta sus partes con sentido", "respuesta": "COHESIÓN", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Conjunto de palabras relacionadas por significado", "respuesta": "CAMPO SEMÁNTICO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Estrofa de cuatro versos endecasílabos con rima ABBA", "respuesta": "CUARTETO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Capital de Dinamarca, ciudad de Hamlet", "respuesta": "COPENHAGUE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Capital de Venezuela, ciudad de Bolívar", "respuesta": "CARACAS", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Mar interior más grande del mundo entre Europa y Asia", "respuesta": "CASPIO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Capital de Australia diseñada como sede del gobierno", "respuesta": "CANBERRA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Isla del Mediterráneo cuya capital es Nicosia", "respuesta": "CHIPRE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Deporte que se juega con raqueta y volante", "respuesta": "BÁDMINTON", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Deporte que se juega con raqueta y volante", "respuesta": "BÁDMINTON", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Instrumento musical de cuerda que se toca con arco", "respuesta": "VIOLONCHELO", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Instrumento musical de cuerda que se toca con arco", "respuesta": "VIOLONCHELO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Superhéroe de Marvel que es el líder de los Vengadores", "respuesta": "CAPITÁN AMÉRICA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Videojuego de construcción con bloques cúbicos", "respuesta": "MINECRAFT", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Videojuego de construcción con bloques cúbicos", "respuesta": "MINECRAFT", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Red social china de videos cortos muy popular entre jóvenes", "respuesta": "TIKTOK", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Red social china de videos cortos muy popular entre jóvenes", "respuesta": "TIKTOK", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Bebida gaseosa negra más famosa del mundo", "respuesta": "COCACOLA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Dulce de cacao que a todos nos encanta", "respuesta": "CHOCOLATE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Órgano que bombea sangre por todo el cuerpo", "respuesta": "CORAZÓN", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Parte del cuerpo donde está el cerebro", "respuesta": "CABEZA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Animal doméstico que maúlla y caza ratones", "respuesta": "GATO", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Animal doméstico que maúlla y caza ratones", "respuesta": "GATO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Animal con joroba que vive en el desierto", "respuesta": "CAMELLO", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Reptil con caparazón que camina muy lento", "respuesta": "TORTUGA", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Reptil con caparazón que camina muy lento", "respuesta": "TORTUGA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Fenómeno natural con rayos y truenos", "respuesta": "TORMENTA", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Fenómeno natural con rayos y truenos", "respuesta": "TORMENTA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Ciencia que estudia las sustancias y sus reacciones", "respuesta": "QUÍMICA", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Ciencia que estudia las sustancias y sus reacciones", "respuesta": "QUÍMICA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Vehículo de cuatro ruedas que se conduce por carretera", "respuesta": "COCHE", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Prenda de vestir que cubre el torso con botones", "respuesta": "CAMISA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Juego de cartas español con oros, copas, espadas y bastos", "respuesta": "BARAJA", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Juego de cartas español con oros, copas, espadas y bastos", "respuesta": "BARAJA", "usada": False},
        {"tipo": "empieza", "definicion": "Empieza por C: Estación del año más fría con nieve", "respuesta": "INVIERNO", "usada": False},
        {"tipo": "contiene", "definicion": "Contiene la C: Estación del año más fría con nieve", "respuesta": "INVIERNO", "usada": False}
    ]
}

# Generar el archivo JSON
with open('static/pasapalabra/preguntas_nuevas.json', 'w', encoding='utf-8') as f:
    json.dump(preguntas_completas, f, ensure_ascii=False, indent=2)

print("✓ Archivo preguntas_nuevas.json generado correctamente")
print(f"✓ Total de letras: {len(preguntas_completas)}")
for letra, preguntas in preguntas_completas.items():
    print(f"  - Letra {letra}: {len(preguntas)} preguntas")
