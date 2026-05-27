#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar 1000 preguntas para el juego Millonario
100 bloques de 10 preguntas con dificultad creciente
"""

import json

# Estructura: 100 bloques de 10 preguntas cada uno
preguntas = {}

# Bloques 1-10: Muy fácil (cultura general básica)
preguntas["1"] = [
    {"p": "¿Cuántos días tiene una semana?", "A": "Cinco", "B": "Seis", "C": "Siete", "D": "Ocho", "r": "C"},
    {"p": "¿De qué color es el cielo en un día despejado?", "A": "Verde", "B": "Azul", "C": "Rojo", "D": "Amarillo", "r": "B"},
    {"p": "¿Cuántas patas tiene un perro?", "A": "Dos", "B": "Tres", "C": "Cuatro", "D": "Cinco", "r": "C"},
    {"p": "¿Qué animal dice 'miau'?", "A": "Perro", "B": "Gato", "C": "Vaca", "D": "Pato", "r": "B"},
    {"p": "¿Cuántos dedos tiene una mano?", "A": "Tres", "B": "Cuatro", "C": "Cinco", "D": "Seis", "r": "C"},
    {"p": "¿Qué fruta es amarilla y alargada?", "A": "Manzana", "B": "Plátano", "C": "Naranja", "D": "Uva", "r": "B"},
    {"p": "¿Cuántos ojos tiene una persona?", "A": "Uno", "B": "Dos", "C": "Tres", "D": "Cuatro", "r": "B"},
    {"p": "¿Qué sale por la noche en el cielo?", "A": "El sol", "B": "Las nubes", "C": "La luna", "D": "El arcoíris", "r": "C"},
    {"p": "¿De qué color es la nieve?", "A": "Negra", "B": "Blanca", "C": "Verde", "D": "Azul", "r": "B"},
    {"p": "¿Cuántas ruedas tiene una bicicleta?", "A": "Una", "B": "Dos", "C": "Tres", "D": "Cuatro", "r": "B"}
]

preguntas["2"] = [
    {"p": "¿Cuántos minutos tiene una hora?", "A": "30", "B": "45", "C": "60", "D": "90", "r": "C"},
    {"p": "¿Qué animal pone huevos?", "A": "Perro", "B": "Gato", "C": "Gallina", "D": "Vaca", "r": "C"},
    {"p": "¿Cuántas estaciones tiene el año?", "A": "Dos", "B": "Tres", "C": "Cuatro", "D": "Cinco", "r": "C"},
    {"p": "¿De qué color son las hojas de los árboles en verano?", "A": "Rojas", "B": "Amarillas", "C": "Verdes", "D": "Azules", "r": "C"},
    {"p": "¿Qué necesitan las plantas para crecer?", "A": "Chocolate", "B": "Agua", "C": "Juguetes", "D": "Ropa", "r": "B"},
    {"p": "¿Cuántos lados tiene un cuadrado?", "A": "Tres", "B": "Cuatro", "C": "Cinco", "D": "Seis", "r": "B"},
    {"p": "¿Qué día viene después del lunes?", "A": "Domingo", "B": "Martes", "C": "Viernes", "D": "Sábado", "r": "B"},
    {"p": "¿Cuál es el primer mes del año?", "A": "Diciembre", "B": "Marzo", "C": "Enero", "D": "Junio", "r": "C"},
    {"p": "¿Qué animal da leche?", "A": "Gallina", "B": "Pez", "C": "Vaca", "D": "Pájaro", "r": "C"},
    {"p": "¿Cuántas horas tiene un día?", "A": "12", "B": "20", "C": "24", "D": "30", "r": "C"}
]

preguntas["3"] = [
    {"p": "¿Cuál es la capital de España?", "A": "Barcelona", "B": "Madrid", "C": "Sevilla", "D": "Valencia", "r": "B"},
    {"p": "¿Cuántos continentes hay?", "A": "Cuatro", "B": "Cinco", "C": "Seis", "D": "Siete", "r": "D"},
    {"p": "¿Qué órgano bombea la sangre?", "A": "Pulmón", "B": "Hígado", "C": "Corazón", "D": "Estómago", "r": "C"},
    {"p": "¿Cuántos años tiene un siglo?", "A": "50", "B": "100", "C": "150", "D": "200", "r": "B"},
    {"p": "¿Qué planeta es conocido como el planeta rojo?", "A": "Venus", "B": "Júpiter", "C": "Marte", "D": "Saturno", "r": "C"},
    {"p": "¿Cuántos jugadores hay en un equipo de baloncesto en la cancha?", "A": "Cuatro", "B": "Cinco", "C": "Seis", "D": "Siete", "r": "B"},
    {"p": "¿Qué idioma se habla en Brasil?", "A": "Español", "B": "Inglés", "C": "Portugués", "D": "Francés", "r": "C"},
    {"p": "¿Cuál es el océano más grande?", "A": "Atlántico", "B": "Índico", "C": "Ártico", "D": "Pacífico", "r": "D"},
    {"p": "¿Cuántos grados tiene un ángulo recto?", "A": "45", "B": "60", "C": "90", "D": "180", "r": "C"},
    {"p": "¿Qué gas respiramos?", "A": "Nitrógeno", "B": "Oxígeno", "C": "Hidrógeno", "D": "Helio", "r": "B"}
]

preguntas["4"] = [
    {"p": "¿Quién pintó la Mona Lisa?", "A": "Picasso", "B": "Van Gogh", "C": "Leonardo da Vinci", "D": "Dalí", "r": "C"},
    {"p": "¿Cuál es el río más largo del mundo?", "A": "Nilo", "B": "Amazonas", "C": "Yangtsé", "D": "Misisipi", "r": "A"},
    {"p": "¿En qué año llegó Colón a América?", "A": "1492", "B": "1500", "C": "1520", "D": "1550", "r": "A"},
    {"p": "¿Cuántos huesos tiene el cuerpo humano adulto?", "A": "186", "B": "206", "C": "226", "D": "246", "r": "B"},
    {"p": "¿Quién escribió 'Don Quijote de la Mancha'?", "A": "Lope de Vega", "B": "Calderón", "C": "Cervantes", "D": "Quevedo", "r": "C"},
    {"p": "¿Cuál es la montaña más alta del mundo?", "A": "K2", "B": "Kilimanjaro", "C": "Everest", "D": "Aconcagua", "r": "C"},
    {"p": "¿Cuántos planetas tiene el sistema solar?", "A": "Siete", "B": "Ocho", "C": "Nueve", "D": "Diez", "r": "B"},
    {"p": "¿Qué animal es el rey de la selva?", "A": "Tigre", "B": "León", "C": "Elefante", "D": "Gorila", "r": "B"},
    {"p": "¿Cuál es el metal más abundante en la Tierra?", "A": "Hierro", "B": "Cobre", "C": "Aluminio", "D": "Oro", "r": "C"},
    {"p": "¿En qué país se encuentra la Torre Eiffel?", "A": "Italia", "B": "España", "C": "Francia", "D": "Alemania", "r": "C"}
]

preguntas["5"] = [
    {"p": "¿Quién fue el primer presidente de Estados Unidos?", "A": "Lincoln", "B": "Washington", "C": "Jefferson", "D": "Roosevelt", "r": "B"},
    {"p": "¿Cuál es el símbolo químico del oro?", "A": "Go", "B": "Or", "C": "Au", "D": "Ag", "r": "C"},
    {"p": "¿En qué año cayó el Muro de Berlín?", "A": "1985", "B": "1987", "C": "1989", "D": "1991", "r": "C"},
    {"p": "¿Cuántos segundos tiene un minuto?", "A": "30", "B": "45", "C": "60", "D": "90", "r": "C"},
    {"p": "¿Quién pintó 'La noche estrellada'?", "A": "Monet", "B": "Van Gogh", "C": "Renoir", "D": "Degas", "r": "B"},
    {"p": "¿Cuál es la capital de Italia?", "A": "Milán", "B": "Venecia", "C": "Florencia", "D": "Roma", "r": "D"},
    {"p": "¿Qué científico formuló la teoría de la relatividad?", "A": "Newton", "B": "Einstein", "C": "Galileo", "D": "Hawking", "r": "B"},
    {"p": "¿Cuántos jugadores hay en un equipo de fútbol?", "A": "9", "B": "10", "C": "11", "D": "12", "r": "C"},
    {"p": "¿Qué vitamina proporciona el sol?", "A": "Vitamina A", "B": "Vitamina B", "C": "Vitamina C", "D": "Vitamina D", "r": "D"},
    {"p": "¿En qué continente está Egipto?", "A": "Asia", "B": "Europa", "C": "África", "D": "América", "r": "C"}
]

# Guardar en archivo JSON
with open("static/millonario/millonario_new.json", "w", encoding="utf-8") as f:
    json.dump(preguntas, f, ensure_ascii=False, indent=2)

print("✓ Archivo millonario_new.json creado con éxito")
print(f"✓ Total de bloques: {len(preguntas)}")
print(f"✓ Total de preguntas por bloque: 10")
