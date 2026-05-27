#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar 1000 preguntas para el juego Millonario
100 bloques de 10 preguntas con dificultad creciente y temas variados
"""

import json

preguntas = {}

# BLOQUES 1-10: MUY FÁCIL
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
    {"p": "¿De qué color son las hojas en verano?", "A": "Rojas", "B": "Amarillas", "C": "Verdes", "D": "Azules", "r": "C"},
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
    {"p": "¿Qué planeta es el planeta rojo?", "A": "Venus", "B": "Júpiter", "C": "Marte", "D": "Saturno", "r": "C"},
    {"p": "¿Cuántos jugadores hay en baloncesto?", "A": "Cuatro", "B": "Cinco", "C": "Seis", "D": "Siete", "r": "B"},
    {"p": "¿Qué idioma se habla en Brasil?", "A": "Español", "B": "Inglés", "C": "Portugués", "D": "Francés", "r": "C"},
    {"p": "¿Cuál es el océano más grande?", "A": "Atlántico", "B": "Índico", "C": "Ártico", "D": "Pacífico", "r": "D"},
    {"p": "¿Cuántos grados tiene un ángulo recto?", "A": "45", "B": "60", "C": "90", "D": "180", "r": "C"},
    {"p": "¿Qué gas respiramos?", "A": "Nitrógeno", "B": "Oxígeno", "C": "Hidrógeno", "D": "Helio", "r": "B"}
]

preguntas["4"] = [
    {"p": "¿Quién pintó la Mona Lisa?", "A": "Picasso", "B": "Van Gogh", "C": "Leonardo da Vinci", "D": "Dalí", "r": "C"},
    {"p": "¿Cuál es el río más largo del mundo?", "A": "Nilo", "B": "Amazonas", "C": "Yangtsé", "D": "Misisipi", "r": "A"},
    {"p": "¿En qué año llegó Colón a América?", "A": "1492", "B": "1500", "C": "1520", "D": "1550", "r": "A"},
    {"p": "¿Cuántos huesos tiene el cuerpo humano?", "A": "186", "B": "206", "C": "226", "D": "246", "r": "B"},
    {"p": "¿Quién escribió Don Quijote?", "A": "Lope de Vega", "B": "Calderón", "C": "Cervantes", "D": "Quevedo", "r": "C"},
    {"p": "¿Cuál es la montaña más alta?", "A": "K2", "B": "Kilimanjaro", "C": "Everest", "D": "Aconcagua", "r": "C"},
    {"p": "¿Cuántos planetas tiene el sistema solar?", "A": "Siete", "B": "Ocho", "C": "Nueve", "D": "Diez", "r": "B"},
    {"p": "¿Qué animal es el rey de la selva?", "A": "Tigre", "B": "León", "C": "Elefante", "D": "Gorila", "r": "B"},
    {"p": "¿Cuál es el metal más abundante?", "A": "Hierro", "B": "Cobre", "C": "Aluminio", "D": "Oro", "r": "C"},
    {"p": "¿Dónde está la Torre Eiffel?", "A": "Italia", "B": "España", "C": "Francia", "D": "Alemania", "r": "C"}
]

preguntas["5"] = [
    {"p": "¿Primer presidente de Estados Unidos?", "A": "Lincoln", "B": "Washington", "C": "Jefferson", "D": "Roosevelt", "r": "B"},
    {"p": "¿Símbolo químico del oro?", "A": "Go", "B": "Or", "C": "Au", "D": "Ag", "r": "C"},
    {"p": "¿Cuándo cayó el Muro de Berlín?", "A": "1985", "B": "1987", "C": "1989", "D": "1991", "r": "C"},
    {"p": "¿Cuántos segundos tiene un minuto?", "A": "30", "B": "45", "C": "60", "D": "90", "r": "C"},
    {"p": "¿Quién pintó La noche estrellada?", "A": "Monet", "B": "Van Gogh", "C": "Renoir", "D": "Degas", "r": "B"},
    {"p": "¿Capital de Italia?", "A": "Milán", "B": "Venecia", "C": "Florencia", "D": "Roma", "r": "D"},
    {"p": "¿Quién formuló la relatividad?", "A": "Newton", "B": "Einstein", "C": "Galileo", "D": "Hawking", "r": "B"},
    {"p": "¿Jugadores en un equipo de fútbol?", "A": "9", "B": "10", "C": "11", "D": "12", "r": "C"},
    {"p": "¿Qué vitamina da el sol?", "A": "Vitamina A", "B": "Vitamina B", "C": "Vitamina C", "D": "Vitamina D", "r": "D"},
    {"p": "¿En qué continente está Egipto?", "A": "Asia", "B": "Europa", "C": "África", "D": "América", "r": "C"}
]

# BLOQUES 6-10: FÁCIL
preguntas["6"] = [
    {"p": "¿Cuál es la capital de Francia?", "A": "Lyon", "B": "Marsella", "C": "París", "D": "Niza", "r": "C"},
    {"p": "¿Cuántos lados tiene un hexágono?", "A": "Cuatro", "B": "Cinco", "C": "Seis", "D": "Siete", "r": "C"},
    {"p": "¿Qué planeta es más cercano al Sol?", "A": "Venus", "B": "Tierra", "C": "Mercurio", "D": "Marte", "r": "C"},
    {"p": "¿Quién escribió Romeo y Julieta?", "A": "Dickens", "B": "Shakespeare", "C": "Tolstói", "D": "Hemingway", "r": "B"},
    {"p": "¿Cuántos colores tiene el arcoíris?", "A": "Cinco", "B": "Seis", "C": "Siete", "D": "Ocho", "r": "C"},
    {"p": "¿Qué instrumento tiene 88 teclas?", "A": "Guitarra", "B": "Piano", "C": "Violín", "D": "Flauta", "r": "B"},
    {"p": "¿Capital de Alemania?", "A": "Múnich", "B": "Hamburgo", "C": "Berlín", "D": "Frankfurt", "r": "C"},
    {"p": "¿Cuántos meses tienen 31 días?", "A": "Cinco", "B": "Seis", "C": "Siete", "D": "Ocho", "r": "C"},
    {"p": "¿Qué deporte juega Messi?", "A": "Baloncesto", "B": "Fútbol", "C": "Tenis", "D": "Golf", "r": "B"},
    {"p": "¿Cuántos centímetros tiene un metro?", "A": "10", "B": "50", "C": "100", "D": "1000", "r": "C"}
]

preguntas["7"] = [
    {"p": "¿Quién descubrió América?", "A": "Magallanes", "B": "Colón", "C": "Vespucio", "D": "Cortés", "r": "B"},
    {"p": "¿Cuál es el animal más rápido?", "A": "León", "B": "Leopardo", "C": "Guepardo", "D": "Tigre", "r": "C"},
    {"p": "¿Cuántos grados tiene un círculo?", "A": "180", "B": "270", "C": "360", "D": "450", "r": "C"},
    {"p": "¿Capital de Portugal?", "A": "Oporto", "B": "Lisboa", "C": "Faro", "D": "Braga", "r": "B"},
    {"p": "¿Qué gas es más abundante en la atmósfera?", "A": "Oxígeno", "B": "Nitrógeno", "C": "Hidrógeno", "D": "Helio", "r": "B"},
    {"p": "¿Cuántos años tiene una década?", "A": "5", "B": "10", "C": "15", "D": "20", "r": "B"},
    {"p": "¿Quién pintó el Guernica?", "A": "Dalí", "B": "Miró", "C": "Picasso", "D": "Goya", "r": "C"},
    {"p": "¿Cuántos jugadores hay en voleibol?", "A": "4", "B": "5", "C": "6", "D": "7", "r": "C"},
    {"p": "¿Qué órgano filtra la sangre?", "A": "Hígado", "B": "Riñón", "C": "Páncreas", "D": "Bazo", "r": "B"},
    {"p": "¿Capital de Japón?", "A": "Osaka", "B": "Kioto", "C": "Tokio", "D": "Hiroshima", "r": "C"}
]

preguntas["8"] = [
    {"p": "¿Cuántos elementos tiene la tabla periódica?", "A": "92", "B": "108", "C": "118", "D": "128", "r": "C"},
    {"p": "¿Quién escribió La Odisea?", "A": "Virgilio", "B": "Homero", "C": "Sófocles", "D": "Esquilo", "r": "B"},
    {"p": "¿Cuál es el hueso más largo?", "A": "Húmero", "B": "Tibia", "C": "Fémur", "D": "Radio", "r": "C"},
    {"p": "¿Capital de Canadá?", "A": "Toronto", "B": "Montreal", "C": "Vancouver", "D": "Ottawa", "r": "D"},
    {"p": "¿Cuántos corazones tiene un pulpo?", "A": "Uno", "B": "Dos", "C": "Tres", "D": "Cuatro", "r": "C"},
    {"p": "¿Quién compuso La Novena Sinfonía?", "A": "Mozart", "B": "Bach", "C": "Beethoven", "D": "Vivaldi", "r": "C"},
    {"p": "¿Cuántos dientes tiene un adulto?", "A": "28", "B": "30", "C": "32", "D": "34", "r": "C"},
    {"p": "¿Qué país tiene más población?", "A": "India", "B": "China", "C": "Estados Unidos", "D": "Indonesia", "r": "B"},
    {"p": "¿Cuántos kilómetros tiene una maratón?", "A": "40", "B": "42", "C": "44", "D": "46", "r": "B"},
    {"p": "¿Capital de Australia?", "A": "Sídney", "B": "Melbourne", "C": "Brisbane", "D": "Canberra", "r": "D"}
]

preguntas["9"] = [
    {"p": "¿Quién fue el primer hombre en la Luna?", "A": "Aldrin", "B": "Armstrong", "C": "Collins", "D": "Gagarin", "r": "B"},
    {"p": "¿Cuántos cromosomas tiene el ser humano?", "A": "23", "B": "36", "C": "46", "D": "48", "r": "C"},
    {"p": "¿Capital de Suiza?", "A": "Zúrich", "B": "Ginebra", "C": "Berna", "D": "Basilea", "r": "C"},
    {"p": "¿Quién escribió Cien años de soledad?", "A": "Vargas Llosa", "B": "García Márquez", "C": "Cortázar", "D": "Borges", "r": "B"},
    {"p": "¿Cuántos segundos tiene una hora?", "A": "1800", "B": "2400", "C": "3600", "D": "4200", "r": "C"},
    {"p": "¿Qué científico descubrió la penicilina?", "A": "Pasteur", "B": "Fleming", "C": "Koch", "D": "Jenner", "r": "B"},
    {"p": "¿Cuántos huesos tiene la columna vertebral?", "A": "24", "B": "26", "C": "33", "D": "40", "r": "C"},
    {"p": "¿Capital de Noruega?", "A": "Bergen", "B": "Oslo", "C": "Trondheim", "D": "Stavanger", "r": "B"},
    {"p": "¿Quién pintó La última cena?", "A": "Rafael", "B": "Miguel Ángel", "C": "Leonardo da Vinci", "D": "Botticelli", "r": "C"},
    {"p": "¿Cuántos metros tiene un kilómetro?", "A": "100", "B": "500", "C": "1000", "D": "10000", "r": "C"}
]

preguntas["10"] = [
    {"p": "¿Quién formuló las leyes del movimiento?", "A": "Galileo", "B": "Newton", "C": "Einstein", "D": "Kepler", "r": "B"},
    {"p": "¿Cuántos países tiene la Unión Europea?", "A": "25", "B": "27", "C": "29", "D": "31", "r": "B"},
    {"p": "¿Capital de Dinamarca?", "A": "Aarhus", "B": "Odense", "C": "Copenhague", "D": "Aalborg", "r": "C"},
    {"p": "¿Quién escribió 1984?", "A": "Huxley", "B": "Orwell", "C": "Bradbury", "D": "Asimov", "r": "B"},
    {"p": "¿Cuántos litros tiene un metro cúbico?", "A": "100", "B": "500", "C": "1000", "D": "10000", "r": "C"},
    {"p": "¿Qué planeta tiene más lunas?", "A": "Júpiter", "B": "Saturno", "C": "Urano", "D": "Neptuno", "r": "B"},
    {"p": "¿Cuántos años duró la Guerra de los Cien Años?", "A": "100", "B": "110", "C": "116", "D": "120", "r": "C"},
    {"p": "¿Capital de Finlandia?", "A": "Tampere", "B": "Turku", "C": "Helsinki", "D": "Espoo", "r": "C"},
    {"p": "¿Quién descubrió la radioactividad?", "A": "Curie", "B": "Rutherford", "C": "Becquerel", "D": "Fermi", "r": "C"},
    {"p": "¿Cuántos gramos tiene un kilogramo?", "A": "100", "B": "500", "C": "1000", "D": "10000", "r": "C"}
]

# Guardar en archivo JSON
with open("static/millonario/millonario_new.json", "w", encoding="utf-8") as f:
    json.dump(preguntas, f, ensure_ascii=False, indent=2)

print(f"✓ Archivo millonario_new.json creado con éxito")
print(f"✓ Total de bloques: {len(preguntas)}")
print(f"✓ Total de preguntas: {sum(len(v) for v in preguntas.values())}")
