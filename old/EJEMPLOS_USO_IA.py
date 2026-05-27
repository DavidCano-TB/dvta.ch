#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJEMPLOS DE USO DE LA IA (GEMINI) PARA TUS NEGOCIOS

Este archivo muestra cómo usar la IA para diferentes casos de uso:
1. Juego "¿Quién soy?" (MEJORADO con verificación de personajes y ortografía)
2. Generar preguntas de examen (para negocio de oposiciones)
3. Explicar respuestas (para estudiantes)
4. Generar trivias (para negocio de restaurantes)
5. Y más...

MEJORAS EN "¿QUIÉN SOY?":
- Verifica si el personaje existe (real, ficticio u otro)
- Corrige errores ortográficos en el nombre del personaje
- Responde basándose en características PRINCIPALES, no secundarias
- Identifica lo más importante por lo que el personaje es conocido
"""

from ai_helper import get_gemini, ask_gemini

# ============================================================================
# EJEMPLO 1: JUEGO "¿QUIÉN SOY?" (YA IMPLEMENTADO)
# ============================================================================

def ejemplo_quien_soy():
    """Ejemplo del juego ¿Quién soy? con verificación de personaje"""
    print("\n" + "="*60)
    print("EJEMPLO 1: JUEGO ¿QUIÉN SOY? (MEJORADO)")
    print("="*60 + "\n")
    
    gemini = get_gemini()
    
    # Ejemplo 1: Personaje real con error ortográfico
    print("🔍 PRUEBA 1: Verificación de personaje con error ortográfico")
    print("-" * 60)
    personaje_mal = "Albert Einsten"  # Error intencional
    print(f"Personaje ingresado: {personaje_mal}")
    
    char_info = gemini.verify_character(personaje_mal)
    print(f"✅ Existe: {char_info.get('exists')}")
    print(f"📝 Nombre correcto: {char_info.get('corrected_name')}")
    print(f"👤 Es real: {char_info.get('is_real')}")
    print(f"🎭 Es ficticio: {char_info.get('is_fictional')}")
    print(f"⭐ Conocido por: {char_info.get('main_known_for')}\n")
    
    # Preguntas sobre características principales
    personaje = char_info.get('corrected_name', personaje_mal)
    preguntas_principales = [
        "¿Es hombre?",
        "¿Es científico?",
        "¿Es físico?",
        "¿Desarrolló teorías importantes?"
    ]
    
    print(f"Preguntas sobre características PRINCIPALES de {personaje}:")
    print("-" * 60)
    for pregunta in preguntas_principales:
        respuesta = gemini.ask_quien_soy(personaje, pregunta)
        print(f"❓ {pregunta}")
        print(f"🤖 {respuesta}\n")
    
    # Preguntas sobre características secundarias (deberían dar "Ni sí ni no")
    preguntas_secundarias = [
        "¿Tocaba el violín?",
        "¿Le gustaba navegar?",
        "¿Tenía el pelo despeinado?"
    ]
    
    print(f"Preguntas sobre características SECUNDARIAS (no relevantes):")
    print("-" * 60)
    for pregunta in preguntas_secundarias:
        respuesta = gemini.ask_quien_soy(personaje, pregunta)
        print(f"❓ {pregunta}")
        print(f"🤖 {respuesta} (debería ser 'Ni sí ni no')\n")
    
    # Ejemplo 2: Personaje ficticio
    print("\n" + "="*60)
    print("🔍 PRUEBA 2: Personaje ficticio")
    print("-" * 60)
    personaje_ficticio = "Pikachu"
    print(f"Personaje: {personaje_ficticio}")
    
    char_info2 = gemini.verify_character(personaje_ficticio)
    print(f"✅ Existe: {char_info2.get('exists')}")
    print(f"👤 Es real: {char_info2.get('is_real')}")
    print(f"🎭 Es ficticio: {char_info2.get('is_fictional')}")
    print(f"⭐ Conocido por: {char_info2.get('main_known_for')}\n")
    
    preguntas_pikachu = [
        "¿Es un Pokémon?",
        "¿Es amarillo?",
        "¿Es de tipo eléctrico?",
        "¿Le gusta el ketchup?"  # Detalle secundario
    ]
    
    for pregunta in preguntas_pikachu:
        respuesta = gemini.ask_quien_soy(personaje_ficticio, pregunta)
        print(f"❓ {pregunta}")
        print(f"🤖 {respuesta}\n")
    
    # Ejemplo 3: Personaje que no existe
    print("\n" + "="*60)
    print("🔍 PRUEBA 3: Personaje inexistente")
    print("-" * 60)
    personaje_falso = "Zxqwerty McFakerson"
    print(f"Personaje: {personaje_falso}")
    
    char_info3 = gemini.verify_character(personaje_falso)
    print(f"✅ Existe: {char_info3.get('exists')}")
    print(f"⭐ Conocido por: {char_info3.get('main_known_for')}\n")


# ============================================================================
# EJEMPLO 2: GENERAR PREGUNTAS DE EXAMEN (NEGOCIO OPOSICIONES)
# ============================================================================

def ejemplo_generar_pregunta_examen():
    """Genera preguntas de examen automáticamente"""
    print("\n" + "="*60)
    print("EJEMPLO 2: GENERAR PREGUNTAS DE EXAMEN")
    print("="*60 + "\n")
    
    gemini = get_gemini()
    
    # Generar pregunta de matemáticas
    pregunta = gemini.generate_exam_question(
        subject="Matemáticas",
        topic="Derivadas",
        difficulty="medium"
    )
    
    if pregunta:
        print(f"📚 Asignatura: Matemáticas - Derivadas")
        print(f"\n❓ Pregunta:")
        print(f"   {pregunta['question']}\n")
        print(f"📝 Opciones:")
        for opcion in pregunta['options']:
            print(f"   {opcion}")
        print(f"\n✅ Respuesta correcta: {pregunta['correct_answer']}")
        print(f"\n💡 Explicación:")
        print(f"   {pregunta['explanation']}")
    else:
        print("❌ Error al generar pregunta")


# ============================================================================
# EJEMPLO 3: EXPLICAR RESPUESTAS (PARA ESTUDIANTES)
# ============================================================================

def ejemplo_explicar_respuesta():
    """Explica por qué una respuesta es correcta o incorrecta"""
    print("\n" + "="*60)
    print("EJEMPLO 3: EXPLICAR RESPUESTAS")
    print("="*60 + "\n")
    
    gemini = get_gemini()
    
    pregunta = "¿Cuál es la derivada de f(x) = x²?"
    respuesta_usuario = "2"
    respuesta_correcta = "2x"
    
    print(f"❓ Pregunta: {pregunta}")
    print(f"👤 Respuesta del estudiante: {respuesta_usuario}")
    print(f"✅ Respuesta correcta: {respuesta_correcta}\n")
    
    explicacion = gemini.explain_answer(
        question=pregunta,
        user_answer=respuesta_usuario,
        correct_answer=respuesta_correcta
    )
    
    if explicacion:
        print(f"💡 Explicación de la IA:\n")
        print(f"   {explicacion}")
    else:
        print("❌ Error al generar explicación")


# ============================================================================
# EJEMPLO 4: GENERAR PREGUNTAS DE TRIVIA (NEGOCIO RESTAURANTES)
# ============================================================================

def ejemplo_generar_trivia():
    """Genera preguntas de trivia para restaurantes"""
    print("\n" + "="*60)
    print("EJEMPLO 4: GENERAR TRIVIA PARA RESTAURANTES")
    print("="*60 + "\n")
    
    prompt = """Genera 5 preguntas de trivia para una noche de quiz en un restaurante.
Categorías: Cultura general, Deportes, Cine, Música, Historia.
Dificultad: Media.

Formato para cada pregunta:
Pregunta: [texto]
A) [opción]
B) [opción]
C) [opción]
D) [opción]
Respuesta correcta: [letra]

Genera las 5 preguntas ahora:"""
    
    respuesta = ask_gemini(prompt, max_tokens=1000)
    
    if respuesta:
        print("🎮 Preguntas de trivia generadas:\n")
        print(respuesta)
    else:
        print("❌ Error al generar trivia")


# ============================================================================
# EJEMPLO 5: TUTOR PERSONALIZADO (CHATBOT EDUCATIVO)
# ============================================================================

def ejemplo_tutor_personalizado():
    """Simula un tutor que responde dudas de estudiantes"""
    print("\n" + "="*60)
    print("EJEMPLO 5: TUTOR PERSONALIZADO")
    print("="*60 + "\n")
    
    system_prompt = """Eres un tutor universitario experto en matemáticas.
Tu trabajo es ayudar a estudiantes a entender conceptos difíciles.
Explica de forma clara, con ejemplos, y paso a paso."""
    
    duda_estudiante = "No entiendo qué es una integral. ¿Me lo puedes explicar con un ejemplo simple?"
    
    print(f"👤 Estudiante: {duda_estudiante}\n")
    
    respuesta = ask_gemini(
        prompt=duda_estudiante,
        system=system_prompt,
        max_tokens=500
    )
    
    if respuesta:
        print(f"🎓 Tutor IA:\n")
        print(f"   {respuesta}")
    else:
        print("❌ Error al generar respuesta")


# ============================================================================
# EJEMPLO 6: PREDICTOR DE NOTA (ANÁLISIS DE RENDIMIENTO)
# ============================================================================

def ejemplo_predictor_nota():
    """Predice la nota de un estudiante basándose en sus simulacros"""
    print("\n" + "="*60)
    print("EJEMPLO 6: PREDICTOR DE NOTA")
    print("="*60 + "\n")
    
    resultados_simulacros = [
        {"examen": 1, "nota": 6.5, "temas": ["Derivadas", "Integrales"]},
        {"examen": 2, "nota": 7.0, "temas": ["Límites", "Continuidad"]},
        {"examen": 3, "nota": 5.5, "temas": ["Derivadas", "Optimización"]},
        {"examen": 4, "nota": 7.5, "temas": ["Integrales", "Áreas"]},
    ]
    
    prompt = f"""Eres un sistema de predicción de notas para estudiantes.

Resultados de simulacros del estudiante:
{resultados_simulacros}

Basándote en estos resultados:
1. Predice la nota probable en el examen final (0-10)
2. Indica la probabilidad de aprobar (%)
3. Identifica los temas más débiles
4. Da 3 recomendaciones específicas para mejorar

Responde en formato claro y estructurado."""
    
    print("📊 Analizando resultados de simulacros...\n")
    
    prediccion = ask_gemini(prompt, max_tokens=400)
    
    if prediccion:
        print(f"🎯 Predicción de la IA:\n")
        print(prediccion)
    else:
        print("❌ Error al generar predicción")


# ============================================================================
# EJEMPLO 7: GENERADOR DE PERSONAJES (PARA JUEGO ¿QUIÉN SOY?)
# ============================================================================

def ejemplo_generar_personajes():
    """Genera lista de personajes para el juego"""
    print("\n" + "="*60)
    print("EJEMPLO 7: GENERAR PERSONAJES PARA EL JUEGO")
    print("="*60 + "\n")
    
    prompt = """Genera una lista de 20 personajes famosos para el juego "¿Quién soy?".

Incluye variedad:
- 5 personajes históricos
- 5 deportistas
- 5 actores/cantantes
- 5 personajes ficticios (películas, series, videojuegos)

Para cada uno indica:
- Nombre
- Categoría
- Nivel de dificultad (Fácil/Medio/Difícil)

Formato:
1. [Nombre] - [Categoría] - [Dificultad]"""
    
    respuesta = ask_gemini(prompt, max_tokens=600)
    
    if respuesta:
        print("🎭 Personajes generados:\n")
        print(respuesta)
    else:
        print("❌ Error al generar personajes")


# ============================================================================
# EJEMPLO 8: ANÁLISIS DE RESPUESTAS (ESTADÍSTICAS INTELIGENTES)
# ============================================================================

def ejemplo_analisis_respuestas():
    """Analiza patrones en las respuestas de estudiantes"""
    print("\n" + "="*60)
    print("EJEMPLO 8: ANÁLISIS INTELIGENTE DE RESPUESTAS")
    print("="*60 + "\n")
    
    datos_estudiante = {
        "nombre": "Juan",
        "exámenes_realizados": 10,
        "nota_media": 6.2,
        "temas_fallados": ["Derivadas (5 veces)", "Límites (3 veces)", "Integrales (2 veces)"],
        "tiempo_medio": "45 minutos",
        "preguntas_en_blanco": 8
    }
    
    prompt = f"""Eres un analista educativo experto.

Datos del estudiante:
{datos_estudiante}

Proporciona:
1. Diagnóstico del rendimiento (2-3 frases)
2. Identificación del problema principal
3. Plan de acción específico (3 pasos concretos)
4. Predicción de mejora si sigue el plan

Sé específico y práctico."""
    
    print(f"📊 Analizando rendimiento de {datos_estudiante['nombre']}...\n")
    
    analisis = ask_gemini(prompt, max_tokens=400)
    
    if analisis:
        print(f"📈 Análisis de la IA:\n")
        print(analisis)
    else:
        print("❌ Error al generar análisis")


# ============================================================================
# EJECUTAR TODOS LOS EJEMPLOS
# ============================================================================

def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*60)
    print("🤖 EJEMPLOS DE USO DE IA (GEMINI) PARA TUS NEGOCIOS")
    print("="*60)
    
    ejemplos = [
        ("Juego ¿Quién soy?", ejemplo_quien_soy),
        ("Generar preguntas de examen", ejemplo_generar_pregunta_examen),
        ("Explicar respuestas", ejemplo_explicar_respuesta),
        ("Generar trivia", ejemplo_generar_trivia),
        ("Tutor personalizado", ejemplo_tutor_personalizado),
        ("Predictor de nota", ejemplo_predictor_nota),
        ("Generar personajes", ejemplo_generar_personajes),
        ("Análisis de respuestas", ejemplo_analisis_respuestas),
    ]
    
    print("\nElige un ejemplo para ejecutar:\n")
    for i, (nombre, _) in enumerate(ejemplos, 1):
        print(f"  {i}. {nombre}")
    print(f"  9. Ejecutar todos")
    print(f"  0. Salir")
    
    try:
        opcion = int(input("\nOpción: "))
        
        if opcion == 0:
            print("\n¡Hasta luego! 👋")
            return
        elif opcion == 9:
            for nombre, func in ejemplos:
                func()
                input("\nPresiona Enter para continuar...")
        elif 1 <= opcion <= len(ejemplos):
            ejemplos[opcion-1][1]()
        else:
            print("\n❌ Opción inválida")
    except ValueError:
        print("\n❌ Opción inválida")
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego! 👋")


if __name__ == "__main__":
    main()
