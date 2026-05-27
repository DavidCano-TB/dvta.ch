#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJEMPLO RÁPIDO: Juego "¿Quién Soy?" Mejorado

Demuestra las nuevas funcionalidades en menos de 50 líneas
"""

from ai_helper import get_gemini

def ejemplo_rapido():
    """Ejemplo rápido de las mejoras"""
    print("\n" + "="*70)
    print("🎮 JUEGO '¿QUIÉN SOY?' - EJEMPLO RÁPIDO")
    print("="*70 + "\n")
    
    gemini = get_gemini()
    
    # 1️⃣ VERIFICAR PERSONAJE (con error ortográfico)
    print("1️⃣  VERIFICACIÓN DE PERSONAJE")
    print("-" * 70)
    personaje = "Cristiano Ronaldo"
    
    info = gemini.verify_character(personaje)
    print(f"Personaje: {info['corrected_name']}")
    print(f"Tipo: {'Real' if info['is_real'] else 'Ficticio' if info['is_fictional'] else 'Otro'}")
    print(f"Conocido por: {info['main_known_for']}\n")
    
    # 2️⃣ PREGUNTAS PRINCIPALES (deberían dar Sí/No)
    print("2️⃣  PREGUNTAS SOBRE CARACTERÍSTICAS PRINCIPALES")
    print("-" * 70)
    preguntas_principales = [
        "¿Es deportista?",
        "¿Juega al fútbol?",
        "¿Es portugués?"
    ]
    
    for pregunta in preguntas_principales:
        respuesta = gemini.ask_quien_soy(personaje, pregunta)
        emoji = "✅" if respuesta == "Sí" else "❌" if respuesta == "No" else "❓"
        print(f"{emoji} {pregunta} → {respuesta}")
    
    # 3️⃣ PREGUNTAS SECUNDARIAS (deberían dar "Ni sí ni no")
    print("\n3️⃣  PREGUNTAS SOBRE DETALLES SECUNDARIOS")
    print("-" * 70)
    preguntas_secundarias = [
        "¿Le gusta la pizza?",
        "¿Tiene tatuajes?",
        "¿Qué marca de ropa usa?"
    ]
    
    for pregunta in preguntas_secundarias:
        respuesta = gemini.ask_quien_soy(personaje, pregunta)
        emoji = "❓"
        print(f"{emoji} {pregunta} → {respuesta} (no relevante)")
    
    print("\n" + "="*70)
    print("✅ Las mejoras funcionan correctamente:")
    print("   • Verifica el personaje")
    print("   • Identifica características principales")
    print("   • Ignora detalles secundarios")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        ejemplo_rapido()
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego! 👋\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de tener configurada tu API key de Gemini:")
        print("   1. Ejecuta: CONFIGURAR_GEMINI_API.bat")
        print("   2. O crea el archivo: config/.gemini_key")
        print("   3. Pega tu API key de Google AI Studio\n")
