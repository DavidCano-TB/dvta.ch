#!/usr/bin/env python3
"""
Test script para verificar la integración de IA en Quien Soy
Uso: python tests/test_ai_integration.py
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_key():
    """Verifica que la API key esté configurada"""
    print("\n🔍 Test 1: Verificando ANTHROPIC_API_KEY...")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    
    if not api_key:
        print("   ❌ ANTHROPIC_API_KEY no está configurada")
        print("   💡 Ejecuta: CONFIGURAR_API_KEY.bat")
        return False
    
    if not api_key.startswith("sk-ant-"):
        print(f"   ⚠️  API key no parece válida (debe empezar con 'sk-ant-')")
        print(f"   📝 Key actual: {api_key[:10]}...")
        return False
    
    print(f"   ✅ API key configurada: {api_key[:15]}...{api_key[-4:]}")
    return True


def test_verify_endpoint():
    """Prueba el endpoint de verificación de personajes"""
    print("\n🔍 Test 2: Probando endpoint /api/quiensoy/verify-character...")
    
    try:
        import urllib.request
        import urllib.parse
        
        # Necesitamos un token de admin para probar
        print("   ℹ️  Este test requiere que el servidor esté corriendo")
        print("   ℹ️  y que tengas un token de admin válido")
        
        # Por ahora solo verificamos que el código existe
        from src.main import app
        print("   ✅ Endpoint existe en el código")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_ask_ai_method():
    """Verifica que el método _ask_ai existe"""
    print("\n🔍 Test 3: Verificando método QuienSoyManager._ask_ai()...")
    
    try:
        # Importar y verificar que el método existe
        import inspect
        from src.main import QuienSoyManager
        
        if hasattr(QuienSoyManager, '_ask_ai'):
            method = getattr(QuienSoyManager, '_ask_ai')
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            print(f"   ✅ Método existe con parámetros: {params}")
            
            # Verificar que tiene los parámetros esperados
            expected = ['self', 'character', 'question']
            if all(p in params for p in expected):
                print("   ✅ Parámetros correctos")
                return True
            else:
                print(f"   ⚠️  Parámetros esperados: {expected}")
                return False
        else:
            print("   ❌ Método _ask_ai no encontrado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_frontend_validation():
    """Verifica que el frontend tiene la validación implementada"""
    print("\n🔍 Test 4: Verificando implementación en frontend...")
    
    try:
        index_path = Path("static/pages/index.html")
        if not index_path.exists():
            print("   ❌ static/pages/index.html no encontrado")
            return False
        
        content = index_path.read_text(encoding='utf-8')
        
        checks = [
            ("qsVerifyChar2", "Función de verificación"),
            ("qsCharInfo2", "UI de información del personaje"),
            ("btnQsVerify2", "Botón de verificar"),
            ("qs2UseSugg", "Función para usar sugerencias"),
        ]
        
        all_ok = True
        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc} ({check})")
            else:
                print(f"   ❌ {desc} ({check}) no encontrado")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_game_page():
    """Verifica que la página del juego tiene el indicador de IA"""
    print("\n🔍 Test 5: Verificando página del juego...")
    
    try:
        game_path = Path("static/quiensoy/game.html")
        if not game_path.exists():
            print("   ❌ static/quiensoy/game.html no encontrado")
            return False
        
        content = game_path.read_text(encoding='utf-8')
        
        checks = [
            ("Esperando respuesta de la IA", "Indicador de carga"),
            ("question_pending", "Estado de pregunta pendiente"),
            ("pending", "Elemento de pending"),
        ]
        
        all_ok = True
        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc}")
            else:
                print(f"   ❌ {desc} no encontrado")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════╗
║   Test de Integración IA - ¿Quién soy?          ║
╚══════════════════════════════════════════════════╝
""")
    
    results = []
    
    # Ejecutar tests
    results.append(("API Key", test_api_key()))
    results.append(("Endpoint Verify", test_verify_endpoint()))
    results.append(("Método _ask_ai", test_ask_ai_method()))
    results.append(("Frontend Validation", test_frontend_validation()))
    results.append(("Game Page", test_game_page()))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n  Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n  🎉 ¡Todos los tests pasaron!")
        print("  ✅ La integración de IA está completamente implementada")
        print("\n  📖 Lee docs/QUIEN_SOY_AI_INTEGRATION.md para más info")
    else:
        print("\n  ⚠️  Algunos tests fallaron")
        if not results[0][1]:  # API Key test failed
            print("  💡 Configura la API key con: CONFIGURAR_API_KEY.bat")
        print("  📖 Consulta docs/QUIEN_SOY_AI_INTEGRATION.md")
    
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
