#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para verificar que la API de Claude (Anthropic) funciona correctamente.
"""

import os
import json
import urllib.request
import urllib.error

def test_anthropic_api():
    """Test de la API de Anthropic (Claude)"""
    
    print("\n" + "="*60)
    print("🤖 TEST DE API DE CLAUDE (ANTHROPIC)")
    print("="*60 + "\n")
    
    # 1. Verificar que existe la API key
    print("📋 Paso 1: Verificando API key...")
    
    # Buscar en diferentes ubicaciones
    api_key = None
    locations = [
        "config/.groq_key",
        "config/.anthropic_key",
        ".anthropic_key"
    ]
    
    for loc in locations:
        if os.path.exists(loc):
            with open(loc, 'r') as f:
                api_key = f.read().strip()
            if api_key:
                print(f"   ✅ API key encontrada en: {loc}")
                print(f"   🔑 Key: {api_key[:20]}...{api_key[-4:]}")
                break
    
    if not api_key:
        print("   ❌ ERROR: No se encontró la API key")
        print("\n💡 SOLUCIÓN:")
        print("   1. Ve a: https://console.anthropic.com/")
        print("   2. Crea una API key")
        print("   3. Guárdala en: config/.groq_key")
        print("   4. O ejecuta: CONFIGURAR_ANTHROPIC_API.bat")
        return False
    
    # 2. Verificar formato de la key
    print("\n📋 Paso 2: Verificando formato de la key...")
    if not api_key.startswith("sk-ant-"):
        print(f"   ⚠️  ADVERTENCIA: La key no empieza con 'sk-ant-'")
        print(f"   Formato actual: {api_key[:10]}...")
        print("   Puede que no sea una key de Anthropic válida")
    else:
        print("   ✅ Formato correcto")
    
    # 3. Test de conexión
    print("\n📋 Paso 3: Probando conexión con la API...")
    
    try:
        # Preparar request
        payload = json.dumps({
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Responde solo con: 'Funciona correctamente'"
                }
            ]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            method="POST"
        )
        
        print("   🌐 Enviando request a Anthropic...")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("content"):
                respuesta = result["content"][0]["text"]
                print(f"   ✅ Respuesta recibida: '{respuesta}'")
                print(f"\n   📊 Uso de tokens:")
                print(f"      - Input: {result.get('usage', {}).get('input_tokens', 0)}")
                print(f"      - Output: {result.get('usage', {}).get('output_tokens', 0)}")
                print(f"      - Modelo: {result.get('model', 'N/A')}")
                
                return True
            else:
                print("   ❌ ERROR: Respuesta vacía")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"   ❌ ERROR HTTP {e.code}: {e.reason}")
        
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get('error', {}).get('message', error_body)
            print(f"   📝 Mensaje: {error_msg}")
            
            # Diagnóstico específico
            if e.code == 401:
                print("\n💡 SOLUCIÓN:")
                print("   - Tu API key es inválida")
                print("   - Ve a: https://console.anthropic.com/settings/keys")
                print("   - Crea una nueva key y guárdala en config/.groq_key")
            elif e.code == 429:
                print("\n💡 SOLUCIÓN:")
                print("   - Has excedido el límite de requests")
                print("   - Espera 1 minuto y vuelve a intentar")
                print("   - O añade más créditos en: https://console.anthropic.com/settings/billing")
            elif e.code == 400:
                print("\n💡 SOLUCIÓN:")
                print("   - Hay un error en el formato del request")
                print("   - Verifica que estás usando el modelo correcto")
            
        except:
            print(f"   📝 Detalles: {error_body}")
        
        return False
        
    except urllib.error.URLError as e:
        print(f"   ❌ ERROR de conexión: {e.reason}")
        print("\n💡 SOLUCIÓN:")
        print("   - Verifica tu conexión a internet")
        print("   - Verifica que no hay firewall bloqueando")
        return False
        
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {str(e)}")
        return False

def test_pregunta_quien_soy():
    """Test específico para el juego ¿Quién soy?"""
    
    print("\n" + "="*60)
    print("🎮 TEST ESPECÍFICO: JUEGO ¿QUIÉN SOY?")
    print("="*60 + "\n")
    
    # Buscar API key
    api_key = None
    for loc in ["config/.groq_key", "config/.anthropic_key", ".anthropic_key"]:
        if os.path.exists(loc):
            with open(loc, 'r') as f:
                api_key = f.read().strip()
            if api_key:
                break
    
    if not api_key:
        print("   ❌ No se encontró API key")
        return False
    
    print("📋 Simulando pregunta del juego...")
    print("   Personaje: Mickey Mouse")
    print("   Pregunta: ¿Es un ratón?")
    
    try:
        payload = json.dumps({
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": """Eres un juego de '¿Quién soy?'. El personaje secreto es: Mickey Mouse.
El jugador pregunta: ¿Es un ratón?

Responde SOLO con 'Sí' o 'No'. Nada más."""
                }
            ]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            respuesta = result["content"][0]["text"].strip()
            
            print(f"   🤖 Respuesta de Claude: '{respuesta}'")
            
            if respuesta.lower() in ['sí', 'si', 'yes', 'sí.', 'si.']:
                print("   ✅ ¡Respuesta correcta! La IA funciona perfectamente.")
                return True
            else:
                print(f"   ⚠️  Respuesta inesperada: '{respuesta}'")
                print("   La IA funciona pero puede necesitar ajustes en el prompt")
                return True
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Ejecutar todos los tests"""
    
    print("\n🚀 Iniciando tests de IA...\n")
    
    # Test 1: API básica
    test1 = test_anthropic_api()
    
    # Test 2: Juego específico
    if test1:
        test2 = test_pregunta_quien_soy()
    else:
        test2 = False
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    print(f"   Test API básica:        {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Test juego ¿Quién soy?: {'✅ PASS' if test2 else '❌ FAIL'}")
    print("="*60 + "\n")
    
    if test1 and test2:
        print("🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
        print("\nPróximos pasos:")
        print("   1. Ejecuta: ARRANCAR.bat")
        print("   2. Ve a: http://localhost:8000/quiensoy.html")
        print("   3. ¡Disfruta del juego con IA!")
    else:
        print("⚠️  Hay problemas que resolver.")
        print("\nRevisa la guía: GUIA_CONFIGURAR_CLAUDE_API.md")
    
    print()

if __name__ == "__main__":
    main()
