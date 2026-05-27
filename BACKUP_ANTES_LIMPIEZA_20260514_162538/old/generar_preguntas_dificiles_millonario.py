#!/usr/bin/env python3
"""
Genera 100 bloques de 10 preguntas para el millonario con dificultad progresiva.
- Preguntas 1-7: Nivel 4 (difíciles)
- Preguntas 8-9: Muy difíciles
- Pregunta 10: Extremadamente difícil
"""

import json
import random

# Categorías de preguntas
CATEGORIAS = [
    "historia", "ciencia", "geografia", "literatura", "arte", 
    "musica", "cine", "deportes", "tecnologia", "cultura_general"
]

# Banco de preguntas difíciles por categoría
PREGUNTAS_DIFICILES = {
    "historia": [
        {"p": "¿En qué año se firmó el Tratado de Tordesillas?", "A": "1492", "B": "1494", "C": "1498", "D": "1500", "r": "B"},
        {"p": "¿Quién fue el último emperador del Sacro Imperio Romano Germánico?", "A": "Carlos V", "B": "Francisco I", "C": "Francisco II", "D": "José II", "r": "C"},
        {"p": "¿En qué batalla murió el rey Gustavo II Adolfo de Suecia?", "A": "Breitenfeld", "B": "Lützen", "C": "Nördlingen", "D": "Rocroi", "r": "B"},
        {"p": "¿Qué faraón construyó la primera pirámide escalonada?", "A": "Keops", "B": "Zoser", "C": "Snefru", "D": "Micerino", "r": "B"},
        {"p": "¿En qué año cayó Constantinopla en manos otomanas?", "A": "1453", "B": "1456", "C": "1461", "D": "1468", "r": "A"},
    ],
    "ciencia": [
        {"p": "¿Cuál es el número atómico del wolframio?", "A": "72", "B": "74", "C": "76", "D": "78", "r": "B"},
        {"p": "¿Qué científico propuso la teoría de la panspermia?", "A": "Arrhenius", "B": "Oparin", "C": "Miller", "D": "Pasteur", "r": "A"},
        {"p": "¿Cuántos pares de nervios craneales tiene el ser humano?", "A": "10", "B": "12", "C": "14", "D": "16", "r": "B"},
        {"p": "¿Qué partícula subatómica fue descubierta por James Chadwick?", "A": "Electrón", "B": "Protón", "C": "Neutrón", "D": "Positrón", "r": "C"},
        {"p": "¿Cuál es la constante de Planck aproximadamente?", "A": "6.626×10⁻³⁴ J·s", "B": "6.626×10⁻²⁴ J·s", "C": "6.626×10⁻¹⁴ J·s", "D": "6.626×10⁻⁴ J·s", "r": "A"},
    ],
    "geografia": [
        {"p": "¿Cuál es la capital de Burkina Faso?", "A": "Uagadugú", "B": "Bobo-Dioulasso", "C": "Koudougou", "D": "Banfora", "r": "A"},
        {"p": "¿En qué país se encuentra el lago Titicaca?", "A": "Solo Perú", "B": "Solo Bolivia", "C": "Perú y Bolivia", "D": "Chile y Bolivia", "r": "C"},
        {"p": "¿Cuál es el río más caudaloso del mundo?", "A": "Nilo", "B": "Amazonas", "C": "Congo", "D": "Yangtsé", "r": "B"},
        {"p": "¿Qué país tiene más islas en el mundo?", "A": "Indonesia", "B": "Filipinas", "C": "Suecia", "D": "Noruega", "r": "C"},
        {"p": "¿Cuál es el desierto más antiguo del mundo?", "A": "Sahara", "B": "Gobi", "C": "Atacama", "D": "Namib", "r": "D"},
    ],
    "literatura": [
        {"p": "¿Quién escribió 'Los hermanos Karamázov'?", "A": "Tolstói", "B": "Dostoievski", "C": "Chéjov", "D": "Turguénev", "r": "B"},
        {"p": "¿En qué año se publicó 'Ulises' de James Joyce?", "A": "1918", "B": "1920", "C": "1922", "D": "1924", "r": "C"},
        {"p": "¿Quién escribió 'El proceso'?", "A": "Kafka", "B": "Musil", "C": "Hesse", "D": "Mann", "r": "A"},
        {"p": "¿Cuál es el verdadero nombre de George Orwell?", "A": "Eric Blair", "B": "David Cornwell", "C": "Charles Dodgson", "D": "Samuel Clemens", "r": "A"},
        {"p": "¿Quién escribió 'En busca del tiempo perdido'?", "A": "Flaubert", "B": "Proust", "C": "Balzac", "D": "Zola", "r": "B"},
    ],
    "arte": [
        {"p": "¿Quién pintó 'El jardín de las delicias'?", "A": "El Bosco", "B": "Brueghel", "C": "Van Eyck", "D": "Memling", "r": "A"},
        {"p": "¿En qué museo se encuentra 'Las meninas'?", "A": "Louvre", "B": "Prado", "C": "Uffizi", "D": "Hermitage", "r": "B"},
        {"p": "¿Quién esculpió 'El pensador'?", "A": "Rodin", "B": "Bernini", "C": "Miguel Ángel", "D": "Donatello", "r": "A"},
        {"p": "¿Qué artista fundó el movimiento suprematista?", "A": "Kandinsky", "B": "Malévich", "C": "Mondrian", "D": "Tatlin", "r": "B"},
        {"p": "¿Quién pintó 'La persistencia de la memoria'?", "A": "Miró", "B": "Magritte", "C": "Dalí", "D": "Ernst", "r": "C"},
    ],
    "musica": [
        {"p": "¿Cuántas sinfonías compuso Beethoven?", "A": "7", "B": "9", "C": "11", "D": "13", "r": "B"},
        {"p": "¿Quién compuso 'Las cuatro estaciones'?", "A": "Bach", "B": "Handel", "C": "Vivaldi", "D": "Corelli", "r": "C"},
        {"p": "¿En qué año murió Mozart?", "A": "1789", "B": "1791", "C": "1793", "D": "1795", "r": "B"},
        {"p": "¿Qué compositor escribió la ópera 'El anillo del nibelungo'?", "A": "Verdi", "B": "Wagner", "C": "Puccini", "D": "Strauss", "r": "B"},
        {"p": "¿Cuántas cuerdas tiene un violonchelo?", "A": "4", "B": "5", "C": "6", "D": "7", "r": "A"},
    ],
    "cine": [
        {"p": "¿Quién dirigió '2001: Una odisea del espacio'?", "A": "Kubrick", "B": "Spielberg", "C": "Scott", "D": "Lucas", "r": "A"},
        {"p": "¿En qué año se estrenó 'El padrino'?", "A": "1970", "B": "1972", "C": "1974", "D": "1976", "r": "B"},
        {"p": "¿Quién compuso la banda sonora de 'Psicosis'?", "A": "Herrmann", "B": "Williams", "C": "Morricone", "D": "Goldsmith", "r": "A"},
        {"p": "¿Qué película ganó el Oscar a mejor película en 1994?", "A": "Pulp Fiction", "B": "Forrest Gump", "C": "Cadena perpetua", "D": "El rey león", "r": "B"},
        {"p": "¿Quién dirigió 'El séptimo sello'?", "A": "Fellini", "B": "Bergman", "C": "Kurosawa", "D": "Tarkovski", "r": "B"},
    ],
    "deportes": [
        {"p": "¿En qué año se celebraron los primeros Juegos Olímpicos modernos?", "A": "1892", "B": "1894", "C": "1896", "D": "1900", "r": "C"},
        {"p": "¿Quién tiene más Grand Slams en tenis masculino?", "A": "Federer", "B": "Nadal", "C": "Djokovic", "D": "Sampras", "r": "C"},
        {"p": "¿Cuántos jugadores forman un equipo de rugby?", "A": "13", "B": "15", "C": "17", "D": "19", "r": "B"},
        {"p": "¿En qué año ganó España su primer Mundial de fútbol?", "A": "2006", "B": "2008", "C": "2010", "D": "2012", "r": "C"},
        {"p": "¿Quién ostenta el récord mundial de 100 metros lisos?", "A": "Bolt", "B": "Powell", "C": "Gay", "D": "Blake", "r": "A"},
    ],
    "tecnologia": [
        {"p": "¿En qué año se fundó Microsoft?", "A": "1973", "B": "1975", "C": "1977", "D": "1979", "r": "B"},
        {"p": "¿Quién inventó la World Wide Web?", "A": "Tim Berners-Lee", "B": "Vint Cerf", "C": "Marc Andreessen", "D": "Larry Page", "r": "A"},
        {"p": "¿Qué significa CPU?", "A": "Central Processing Unit", "B": "Computer Personal Unit", "C": "Central Program Unit", "D": "Computer Processing Unit", "r": "A"},
        {"p": "¿En qué año se lanzó el primer iPhone?", "A": "2005", "B": "2006", "C": "2007", "D": "2008", "r": "C"},
        {"p": "¿Quién fundó Tesla Motors?", "A": "Elon Musk", "B": "Martin Eberhard", "C": "JB Straubel", "D": "Marc Tarpenning", "r": "B"},
    ],
    "cultura_general": [
        {"p": "¿Cuántos huesos tiene el cuerpo humano adulto?", "A": "196", "B": "206", "C": "216", "D": "226", "r": "B"},
        {"p": "¿Cuál es el idioma más hablado del mundo?", "A": "Inglés", "B": "Español", "C": "Mandarín", "D": "Hindi", "r": "C"},
        {"p": "¿En qué año cayó el Muro de Berlín?", "A": "1987", "B": "1988", "C": "1989", "D": "1990", "r": "C"},
        {"p": "¿Cuál es la montaña más alta de África?", "A": "Kilimanjaro", "B": "Monte Kenia", "C": "Ruwenzori", "D": "Ras Dashen", "r": "A"},
        {"p": "¿Quién escribió 'La divina comedia'?", "A": "Petrarca", "B": "Boccaccio", "C": "Dante", "D": "Ariosto", "r": "C"},
    ]
}

# Preguntas MUY difíciles (para posiciones 8-9)
PREGUNTAS_MUY_DIFICILES = {
    "historia": [
        {"p": "¿Qué emperador bizantino reconquistó temporalmente Italia en el siglo VI?", "A": "Justiniano I", "B": "Heraclio", "C": "Basilio II", "D": "Constantino VII", "r": "A"},
        {"p": "¿En qué año se produjo la Batalla de Lepanto?", "A": "1569", "B": "1571", "C": "1573", "D": "1575", "r": "B"},
    ],
    "ciencia": [
        {"p": "¿Cuál es el isótopo más común del uranio?", "A": "U-233", "B": "U-235", "C": "U-238", "D": "U-239", "r": "C"},
        {"p": "¿Qué científico propuso el principio de exclusión?", "A": "Heisenberg", "B": "Pauli", "C": "Schrödinger", "D": "Dirac", "r": "B"},
    ],
    "geografia": [
        {"p": "¿Cuál es el punto más bajo de la Tierra?", "A": "Mar Muerto", "B": "Fosa de las Marianas", "C": "Valle de la Muerte", "D": "Depresión de Qattara", "r": "B"},
        {"p": "¿Qué país tiene la mayor reserva de agua dulce del mundo?", "A": "Canadá", "B": "Rusia", "C": "Brasil", "D": "Estados Unidos", "r": "C"},
    ],
    "literatura": [
        {"p": "¿Quién escribió 'El hombre sin atributos'?", "A": "Musil", "B": "Broch", "C": "Roth", "D": "Zweig", "r": "A"},
        {"p": "¿En qué año se publicó 'Finnegans Wake'?", "A": "1937", "B": "1939", "C": "1941", "D": "1943", "r": "B"},
    ],
    "arte": [
        {"p": "¿Quién pintó 'La ronda de noche'?", "A": "Vermeer", "B": "Rembrandt", "C": "Hals", "D": "Rubens", "r": "B"},
        {"p": "¿En qué ciudad nació Pablo Picasso?", "A": "Barcelona", "B": "Madrid", "C": "Málaga", "D": "Sevilla", "r": "C"},
    ],
    "musica": [
        {"p": "¿Cuántas óperas completas compuso Mozart?", "A": "18", "B": "22", "C": "26", "D": "30", "r": "B"},
        {"p": "¿Quién compuso 'El arte de la fuga'?", "A": "Bach", "B": "Handel", "C": "Telemann", "D": "Vivaldi", "r": "A"},
    ],
    "cine": [
        {"p": "¿Quién dirigió 'El acorazado Potemkin'?", "A": "Eisenstein", "B": "Pudovkin", "C": "Vertov", "D": "Dovzhenko", "r": "A"},
        {"p": "¿En qué año se estrenó 'Ciudadano Kane'?", "A": "1939", "B": "1941", "C": "1943", "D": "1945", "r": "B"},
    ],
    "deportes": [
        {"p": "¿Quién ganó más Tours de Francia?", "A": "Merckx", "B": "Hinault", "C": "Indurain", "D": "Armstrong (anulado)", "r": "A"},
        {"p": "¿En qué año se celebró el primer Mundial de fútbol?", "A": "1928", "B": "1930", "C": "1932", "D": "1934", "r": "B"},
    ],
    "tecnologia": [
        {"p": "¿Quién inventó el transistor?", "A": "Shockley, Bardeen y Brattain", "B": "Kilby y Noyce", "C": "Turing y von Neumann", "D": "Shannon y Wiener", "r": "A"},
        {"p": "¿En qué año se lanzó el primer satélite artificial?", "A": "1955", "B": "1957", "C": "1959", "D": "1961", "r": "B"},
    ],
    "cultura_general": [
        {"p": "¿Cuántos elementos químicos hay en la tabla periódica?", "A": "112", "B": "116", "C": "118", "D": "120", "r": "C"},
        {"p": "¿Qué filósofo escribió 'Crítica de la razón pura'?", "A": "Hegel", "B": "Kant", "C": "Fichte", "D": "Schelling", "r": "B"},
    ]
}

# Preguntas EXTREMADAMENTE difíciles (para posición 10)
PREGUNTAS_EXTREMAS = {
    "historia": [
        {"p": "¿Qué tratado puso fin a la Guerra de los Treinta Años?", "A": "Paz de Augsburgo", "B": "Paz de Westfalia", "C": "Paz de Utrecht", "D": "Paz de Nimega", "r": "B"},
        {"p": "¿Quién fue el primer califa omeya?", "A": "Muawiya I", "B": "Yazid I", "C": "Abd al-Malik", "D": "Marwan I", "r": "A"},
    ],
    "ciencia": [
        {"p": "¿Cuál es la vida media del neutrón libre?", "A": "~10 minutos", "B": "~15 minutos", "C": "~20 minutos", "D": "~25 minutos", "r": "B"},
        {"p": "¿Qué científico propuso la teoría de la relatividad general?", "A": "Lorentz", "B": "Poincaré", "C": "Einstein", "D": "Minkowski", "r": "C"},
    ],
    "geografia": [
        {"p": "¿Cuál es el lago más profundo del mundo?", "A": "Tanganica", "B": "Baikal", "C": "Malawi", "D": "Cráter", "r": "B"},
        {"p": "¿En qué país se encuentra el volcán Cotopaxi?", "A": "Perú", "B": "Colombia", "C": "Ecuador", "D": "Bolivia", "r": "C"},
    ],
    "literatura": [
        {"p": "¿Quién escribió 'La montaña mágica'?", "A": "Mann", "B": "Hesse", "C": "Kafka", "D": "Musil", "r": "A"},
        {"p": "¿En qué año se publicó 'Moby Dick'?", "A": "1849", "B": "1851", "C": "1853", "D": "1855", "r": "B"},
    ],
    "arte": [
        {"p": "¿Quién pintó 'La escuela de Atenas'?", "A": "Leonardo", "B": "Miguel Ángel", "C": "Rafael", "D": "Tiziano", "r": "C"},
        {"p": "¿En qué año se inauguró el Museo Guggenheim de Bilbao?", "A": "1995", "B": "1997", "C": "1999", "D": "2001", "r": "B"},
    ],
    "musica": [
        {"p": "¿Cuántos conciertos para piano compuso Beethoven?", "A": "3", "B": "5", "C": "7", "D": "9", "r": "B"},
        {"p": "¿Quién compuso 'El mesías'?", "A": "Bach", "B": "Handel", "C": "Haydn", "D": "Mozart", "r": "B"},
    ],
    "cine": [
        {"p": "¿Quién dirigió 'Metrópolis'?", "A": "Lang", "B": "Murnau", "C": "Pabst", "D": "Wiene", "r": "A"},
        {"p": "¿En qué año se estrenó 'El nacimiento de una nación'?", "A": "1913", "B": "1915", "C": "1917", "D": "1919", "r": "B"},
    ],
    "deportes": [
        {"p": "¿Quién tiene el récord de más medallas olímpicas?", "A": "Phelps", "B": "Latynina", "C": "Bjørgen", "D": "Andrianov", "r": "A"},
        {"p": "¿En qué año se celebraron los primeros Juegos Olímpicos de invierno?", "A": "1920", "B": "1924", "C": "1928", "D": "1932", "r": "B"},
    ],
    "tecnologia": [
        {"p": "¿Quién desarrolló el lenguaje de programación C?", "A": "Kernighan", "B": "Ritchie", "C": "Thompson", "D": "Stroustrup", "r": "B"},
        {"p": "¿En qué año se fundó Google?", "A": "1996", "B": "1998", "C": "2000", "D": "2002", "r": "B"},
    ],
    "cultura_general": [
        {"p": "¿Cuántos países forman parte de la ONU?", "A": "191", "B": "193", "C": "195", "D": "197", "r": "B"},
        {"p": "¿Qué filósofo escribió 'Ser y tiempo'?", "A": "Husserl", "B": "Heidegger", "C": "Sartre", "D": "Jaspers", "r": "B"},
    ]
}

def generar_pregunta(nivel, categoria):
    """Genera una pregunta según el nivel de dificultad."""
    if nivel <= 7:
        # Preguntas difíciles (nivel 4)
        pool = PREGUNTAS_DIFICILES.get(categoria, [])
    elif nivel <= 9:
        # Preguntas muy difíciles
        pool = PREGUNTAS_MUY_DIFICILES.get(categoria, [])
    else:
        # Pregunta extremadamente difícil
        pool = PREGUNTAS_EXTREMAS.get(categoria, [])
    
    if not pool:
        # Fallback a preguntas difíciles si no hay en esa categoría
        pool = PREGUNTAS_DIFICILES.get(categoria, [])
    
    if not pool:
        # Fallback genérico
        return {
            "p": f"Pregunta de {categoria} nivel {nivel}",
            "A": "Opción A",
            "B": "Opción B",
            "C": "Opción C (correcta)",
            "D": "Opción D",
            "r": "C"
        }
    
    return random.choice(pool).copy()

def generar_bloque():
    """Genera un bloque de 10 preguntas con dificultad progresiva."""
    bloque = []
    categorias_usadas = []
    
    for nivel in range(1, 11):
        # Seleccionar categoría no repetida
        categorias_disponibles = [c for c in CATEGORIAS if c not in categorias_usadas]
        if not categorias_disponibles:
            categorias_disponibles = CATEGORIAS.copy()
            categorias_usadas = []
        
        categoria = random.choice(categorias_disponibles)
        categorias_usadas.append(categoria)
        
        pregunta = generar_pregunta(nivel, categoria)
        bloque.append(pregunta)
    
    return bloque

def main():
    print("Generando 100 bloques de 10 preguntas difíciles para el millonario...")
    
    resultado = {}
    
    for i in range(1, 101):
        print(f"Generando bloque {i}/100...")
        resultado[str(i)] = generar_bloque()
    
    # Guardar en archivo JSON
    output_file = "static/millonario/preguntas.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Generadas 1000 preguntas en {output_file}")
    print("\nCaracterísticas:")
    print("  - Preguntas 1-7: Nivel 4 (difíciles)")
    print("  - Preguntas 8-9: Muy difíciles")
    print("  - Pregunta 10: Extremadamente difícil")
    print("  - 10 categorías diferentes")
    print("  - Sin repetición de categorías en el mismo bloque")

if __name__ == "__main__":
    main()
