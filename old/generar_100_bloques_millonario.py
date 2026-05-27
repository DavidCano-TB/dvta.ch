#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera 100 bloques de 10 preguntas cada uno para el juego Millonario.
Cada pregunta tiene 4 opciones (A, B, C, D) y una respuesta correcta.
"""

import json
import random

# Plantillas de preguntas por categoría
CATEGORIAS = {
    "geografia": [
        ("¿Cuál es la capital de {pais}?", ["{capital}", "{ciudad1}", "{ciudad2}", "{ciudad3}"]),
        ("¿En qué continente está {pais}?", ["{continente}", "{cont1}", "{cont2}", "{cont3}"]),
        ("¿Qué océano baña las costas de {pais}?", ["{oceano}", "{oc1}", "{oc2}", "{oc3}"]),
    ],
    "historia": [
        ("¿En qué año ocurrió {evento}?", ["{anio}", "{anio1}", "{anio2}", "{anio3}"]),
        ("¿Quién fue {personaje}?", ["{descripcion}", "{desc1}", "{desc2}", "{desc3}"]),
    ],
    "ciencia": [
        ("¿Cuál es el símbolo químico del {elemento}?", ["{simbolo}", "{sim1}", "{sim2}", "{sim3}"]),
        ("¿Cuántos {organo} tiene el cuerpo humano?", ["{numero}", "{num1}", "{num2}", "{num3}"]),
    ],
    "cultura": [
        ("¿Quién escribió {obra}?", ["{autor}", "{aut1}", "{aut2}", "{aut3}"]),
        ("¿De qué país es típico {plato}?", ["{pais}", "{p1}", "{p2}", "{p3}"]),
    ],
    "deportes": [
        ("¿En qué deporte destaca {deportista}?", ["{deporte}", "{dep1}", "{dep2}", "{dep3}"]),
        ("¿Cuántos jugadores tiene un equipo de {deporte}?", ["{numero}", "{n1}", "{n2}", "{n3}"]),
    ],
    "general": [
        ("¿Cuántos días tiene {periodo}?", ["{dias}", "{d1}", "{d2}", "{d3}"]),
        ("¿De qué color es {objeto}?", ["{color}", "{c1}", "{c2}", "{c3}"]),
        ("¿Cuántas {parte} tiene {objeto}?", ["{numero}", "{n1}", "{n2}", "{n3}"]),
    ]
}

# Datos para rellenar las plantillas
DATOS = {
    "paises": ["España", "Francia", "Italia", "Alemania", "Portugal", "Reino Unido", "Grecia", "Suecia"],
    "capitales": ["Madrid", "París", "Roma", "Berlín", "Lisboa", "Londres", "Atenas", "Estocolmo"],
    "ciudades": ["Barcelona", "Lyon", "Milán", "Múnich", "Oporto", "Manchester", "Tesalónica", "Gotemburgo"],
    "continentes": ["Europa", "Asia", "África", "América", "Oceanía"],
    "oceanos": ["Atlántico", "Pacífico", "Índico", "Ártico"],
    "elementos": ["Oro", "Plata", "Hierro", "Cobre", "Carbono", "Oxígeno", "Hidrógeno"],
    "simbolos": ["Au", "Ag", "Fe", "Cu", "C", "O", "H"],
    "colores": ["Rojo", "Azul", "Verde", "Amarillo", "Negro", "Blanco", "Naranja"],
    "numeros": ["Uno", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Ocho", "Nueve", "Diez"],
}

def generar_pregunta_simple(nivel):
    """Genera una pregunta simple basada en el nivel."""
    preguntas_faciles = [
        ("¿Cuántos días tiene una semana?", "Siete", ["Cinco", "Seis", "Ocho"]),
        ("¿De qué color es el cielo en un día despejado?", "Azul", ["Verde", "Rojo", "Amarillo"]),
        ("¿Cuántas patas tiene un perro?", "Cuatro", ["Dos", "Tres", "Cinco"]),
        ("¿Qué animal dice 'miau'?", "Gato", ["Perro", "Vaca", "Pato"]),
        ("¿Cuántos dedos tiene una mano?", "Cinco", ["Tres", "Cuatro", "Seis"]),
        ("¿Qué fruta es amarilla y alargada?", "Plátano", ["Manzana", "Naranja", "Uva"]),
        ("¿Cuántas ruedas tiene una bicicleta?", "Dos", ["Una", "Tres", "Cuatro"]),
        ("¿Qué planeta es conocido como el planeta rojo?", "Marte", ["Venus", "Júpiter", "Saturno"]),
        ("¿Cuántos meses tiene un año?", "Doce", ["Diez", "Once", "Trece"]),
        ("¿Qué animal es el rey de la selva?", "León", ["Tigre", "Elefante", "Gorila"]),
    ]
    
    preguntas_medias = [
        ("¿Cuál es la capital de España?", "Madrid", ["Barcelona", "Sevilla", "Valencia"]),
        ("¿En qué año llegó el hombre a la Luna?", "1969", ["1959", "1979", "1989"]),
        ("¿Quién pintó la Mona Lisa?", "Leonardo da Vinci", ["Miguel Ángel", "Rafael", "Donatello"]),
        ("¿Cuál es el océano más grande?", "Pacífico", ["Atlántico", "Índico", "Ártico"]),
        ("¿Cuántos continentes hay?", "Seis", ["Cinco", "Siete", "Ocho"]),
        ("¿Qué gas respiramos?", "Oxígeno", ["Nitrógeno", "Hidrógeno", "Dióxido de carbono"]),
        ("¿Cuál es el río más largo del mundo?", "Amazonas", ["Nilo", "Yangtsé", "Misisipi"]),
        ("¿Quién escribió Don Quijote?", "Cervantes", ["Lope de Vega", "Quevedo", "Góngora"]),
        ("¿Cuántos huesos tiene el cuerpo humano adulto?", "206", ["186", "226", "246"]),
        ("¿Qué instrumento tiene 88 teclas?", "Piano", ["Órgano", "Acordeón", "Sintetizador"]),
    ]
    
    preguntas_dificiles = [
        ("¿En qué año cayó el Muro de Berlín?", "1989", ["1979", "1985", "1991"]),
        ("¿Cuál es el elemento químico más abundante en el universo?", "Hidrógeno", ["Helio", "Oxígeno", "Carbono"]),
        ("¿Quién fue el primer presidente de Estados Unidos?", "George Washington", ["Thomas Jefferson", "John Adams", "Benjamin Franklin"]),
        ("¿Cuántos satélites naturales tiene Marte?", "Dos", ["Uno", "Tres", "Ninguno"]),
        ("¿En qué ciudad se encuentra la Torre Eiffel?", "París", ["Londres", "Roma", "Berlín"]),
        ("¿Cuál es la montaña más alta del mundo?", "Everest", ["K2", "Kilimanjaro", "Mont Blanc"]),
        ("¿Qué científico propuso la teoría de la relatividad?", "Einstein", ["Newton", "Galileo", "Hawking"]),
        ("¿Cuántos jugadores tiene un equipo de fútbol?", "Once", ["Diez", "Doce", "Nueve"]),
        ("¿En qué año comenzó la Segunda Guerra Mundial?", "1939", ["1914", "1941", "1945"]),
        ("¿Cuál es la velocidad de la luz?", "300.000 km/s", ["150.000 km/s", "450.000 km/s", "600.000 km/s"]),
    ]
    
    if nivel <= 5:
        pool = preguntas_faciles
    elif nivel <= 10:
        pool = preguntas_medias
    else:
        pool = preguntas_dificiles
    
    pregunta, correcta, incorrectas = random.choice(pool)
    opciones = [correcta] + incorrectas
    random.shuffle(opciones)
    
    letra_correcta = chr(65 + opciones.index(correcta))  # A, B, C, D
    
    return {
        "p": pregunta,
        "A": opciones[0],
        "B": opciones[1],
        "C": opciones[2],
        "D": opciones[3],
        "r": letra_correcta
    }

def generar_bloque(bloque_num):
    """Genera un bloque de 10 preguntas."""
    preguntas = []
    for i in range(10):
        # Distribuir las preguntas entre los 15 niveles
        nivel = ((bloque_num - 1) % 15) + 1
        pregunta = generar_pregunta_simple(nivel)
        preguntas.append(pregunta)
    return preguntas

# Generar 100 bloques (distribuidos entre 15 niveles)
print("Generando 100 bloques de preguntas para Millonario...")
preguntas = {}

# Primero generar bloques para cada nivel (1-15)
for nivel in range(1, 16):
    preguntas[str(nivel)] = []

# Distribuir los 100 bloques entre los 15 niveles
for i in range(1, 101):
    nivel = ((i - 1) % 15) + 1
    bloque = generar_bloque(i)
    preguntas[str(nivel)].extend(bloque)
    if i % 10 == 0:
        print(f"  Generados {i} bloques...")

print(f"\nDistribución de preguntas por nivel:")
for nivel in range(1, 16):
    print(f"  Nivel {nivel}: {len(preguntas[str(nivel)])} preguntas")

# Guardar en archivo JSON
with open("static/millonario/preguntas.json", "w", encoding="utf-8") as f:
    json.dump(preguntas, f, ensure_ascii=False, indent=2)

print("✓ Archivo preguntas.json creado con éxito")
print(f"✓ Total de bloques: {len(preguntas)}")
print(f"✓ Total de preguntas: {sum(len(v) for v in preguntas.values())}")
print(f"✓ Preguntas por bloque: 10")
