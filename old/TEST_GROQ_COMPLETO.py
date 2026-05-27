#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del sistema Quién Soy con Groq
"""

import sys
sys.path.insert(0, '.')
from ai_helper import GroqAI

print("\n" + "="*70)
print("TEST COMPLETO SISTEMA QUIÉN SOY CON GROQ")
print("="*70)

ai = GroqAI()

# Test 1: Personajes con errores ortográficos
print("\n" + "="*70)
print("TEST 1: DETECCIÓN CON ERRORES ORTOGRÁFICOS")
print("="*70)

test_cases = [
    ("pikachu", "Pikachu"),
    ("miki maus", "Mickey Mouse"),
    ("spider man", "Spider-Man"),
    ("supermen", "Superman"),
    ("dedpol", "Deadpool"),
    ("pato donald", "Donald Duck"),
    ("bob esponja", "SpongeBob"),
    ("sonic", "Sonic"),
]

passed = 0
for input_name, expected in test_cases:
    result = ai.verify_character(input_name)
    corrected = result.get('corrected_name', '')
    exists = result.get('exists', False)
    confidence = result.get('confidence', 'unknown')
    
    # Verificar si el nombre corregido contiene el esperado (flexible)
    success = exists and (expected.lower() in corrected.lower() or corrected.lower() in expected.lower())
    
    status = "✅" if success else "❌"
    print(f"{status} '{input_name}' → '{corrected}' (esperado: {expected}, confidence: {confidence})")
    
    if success:
        passed += 1

print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados ({passed*100//len(test_cases)}%)")

# Test 2: Respuestas a preguntas
print("\n" + "="*70)
print("TEST 2: RESPUESTAS A PREGUNTAS")
print("="*70)

# Primero verificar Pikachu
pikachu_info = ai.verify_character("pikachu")
print(f"\nPersonaje: {pikachu_info.get('corrected_name')}")
print(f"Conocido por: {pikachu_info.get('main_known_for')}")
print(f"Características: {pikachu_info.get('key_characteristics')}")

# Hacer preguntas
questions = [
    ("¿Eres amarillo?", ["Sí"]),
    ("¿Eres un Pokémon?", ["Sí"]),
    ("¿Eres humano?", ["No"]),
    ("¿Tienes poderes eléctricos?", ["Sí"]),
]

print("\nPreguntas:")
passed_q = 0
for question, expected_answers in questions:
    answer = ai.ask_quien_soy(pikachu_info, question)
    success = answer in expected_answers
    status = "✅" if success else "⚠️"
    print(f"{status} '{question}' → '{answer}' (esperado: {expected_answers})")
    if success:
        passed_q += 1

print(f"\n📊 Resultado: {passed_q}/{len(questions)} preguntas correctas ({passed_q*100//len(questions)}%)")

# Resumen final
print("\n" + "="*70)
print("RESUMEN FINAL")
print("="*70)
print(f"✅ Detección de personajes: {passed}/{len(test_cases)} ({passed*100//len(test_cases)}%)")
print(f"✅ Respuestas a preguntas: {passed_q}/{len(questions)} ({passed_q*100//len(questions)}%)")

if passed >= len(test_cases) * 0.8 and passed_q >= len(questions) * 0.7:
    print("\n🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
else:
    print("\n⚠️  Sistema necesita ajustes")

print("="*70)
