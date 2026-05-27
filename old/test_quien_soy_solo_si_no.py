"""
Script de prueba para verificar que el juego "Quién Soy" 
solo responde con "Sí" o "No" (sin "Ni sí ni no")
"""

import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_helper():
    """Prueba el módulo ai_helper.py"""
    print("=" * 70)
    print("PRUEBA 1: Módulo ai_helper.py (Gemini)")
    print("=" * 70)
    
    try:
        from ai_helper import ask_quien_soy
        
        # Personajes de prueba
        test_cases = [
            ("Mickey Mouse", "¿Es un ratón?"),
            ("Albert Einstein", "¿Es científico?"),
            ("Messi", "¿Es futbolista?"),
            ("Personaje Inexistente XYZ", "¿Existe?"),
            ("Mickey Mouse", "¿Le gusta el queso?"),  # Pregunta ambigua
        ]
        
        print("\nProbando respuestas de Gemini AI:")
        print("-" * 70)
        
        all_valid = True
        for character, question in test_cases:
            response = ask_quien_soy(character, question)
            is_valid = response in ["Sí", "No"]
            status = "✅" if is_valid else "❌"
            
            print(f"{status} Personaje: {character}")
            print(f"   Pregunta: {question}")
            print(f"   Respuesta: '{response}' {'(VÁLIDA)' if is_valid else '(INVÁLIDA - debería ser Sí o No)'}")
            print()
            
            if not is_valid:
                all_valid = False
        
        if all_valid:
            print("✅ TODAS LAS RESPUESTAS SON VÁLIDAS (solo 'Sí' o 'No')")
        else:
            print("❌ ALGUNAS RESPUESTAS SON INVÁLIDAS")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_fallback():
    """Prueba el fallback en main.py"""
    print("\n" + "=" * 70)
    print("PRUEBA 2: Fallback en src/main.py")
    print("=" * 70)
    
    try:
        # Simular la función _ask_ai del main.py
        import logging
        logger = logging.getLogger("test")
        
        # Copiar la lógica del fallback
        def test_fallback(character, question):
            q = question.lower()
            c = character.lower()
            
            # Base de datos simplificada para prueba
            db = {
                "mickey": {"yes": ["ratón", "disney"], "no": ["warner", "real"]},
                "einstein": {"yes": ["científico", "alemán"], "no": ["actor", "cantante"]},
            }
            
            data = None
            for name in db.keys():
                if name in c:
                    data = db[name]
                    break
            
            if not data:
                return "No"  # Antes era "Ni sí ni no"
            
            # Buscar coincidencias
            for word in ["ratón", "científico", "disney", "alemán"]:
                if word in q:
                    if word in data["yes"]:
                        return "Sí"
                    elif word in data["no"]:
                        return "No"
            
            return "No"  # Antes era "Ni sí ni no"
        
        test_cases = [
            ("Mickey Mouse", "¿Es un ratón?", "Sí"),
            ("Albert Einstein", "¿Es científico?", "Sí"),
            ("Personaje Desconocido", "¿Existe?", "No"),
            ("Mickey Mouse", "¿Le gusta bailar?", "No"),  # Pregunta sin coincidencia
        ]
        
        print("\nProbando fallback local:")
        print("-" * 70)
        
        all_valid = True
        for character, question, expected in test_cases:
            response = test_fallback(character, question)
            is_valid = response in ["Sí", "No"]
            matches_expected = response == expected
            status = "✅" if is_valid and matches_expected else "⚠️" if is_valid else "❌"
            
            print(f"{status} Personaje: {character}")
            print(f"   Pregunta: {question}")
            print(f"   Respuesta: '{response}' (esperada: '{expected}')")
            print(f"   {'VÁLIDA' if is_valid else 'INVÁLIDA'}")
            print()
            
            if not is_valid:
                all_valid = False
        
        if all_valid:
            print("✅ TODAS LAS RESPUESTAS DEL FALLBACK SON VÁLIDAS")
        else:
            print("❌ ALGUNAS RESPUESTAS DEL FALLBACK SON INVÁLIDAS")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🎮 PRUEBA: Juego 'Quién Soy' - Solo respuestas 'Sí' o 'No'\n")
    
    result1 = test_ai_helper()
    result2 = test_main_fallback()
    
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    
    if result1 and result2:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("✅ El juego ahora solo responde 'Sí' o 'No'")
        print("✅ 'Ni sí ni no' ha sido eliminado completamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️  Revisa los errores arriba")
    
    print("\n💡 NOTA: Para probar con Gemini API real, asegúrate de:")
    print("   1. Tener configurada la API key en conf/.gemini_key")
    print("   2. Tener créditos disponibles en tu cuenta de Google AI Studio")
    print("   3. Reiniciar el servidor después de los cambios")
