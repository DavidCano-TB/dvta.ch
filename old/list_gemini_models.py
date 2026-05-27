#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar los modelos disponibles en Gemini API
"""

import urllib.request
import json

# Cargar API key
with open("config/.gemini_key", "r") as f:
    api_key = f.read().strip()

print("🔍 Listando modelos disponibles en Gemini API...")
print("="*80)

# Probar diferentes versiones de la API
api_versions = [
    ("v1", "https://generativelanguage.googleapis.com/v1/models"),
    ("v1beta", "https://generativelanguage.googleapis.com/v1beta/models")
]

for version, base_url in api_versions:
    print(f"\n📋 API {version}: {base_url}")
    print("-"*80)
    
    try:
        url = f"{base_url}?key={api_key}"
        req = urllib.request.Request(url, method="GET")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            models = data.get("models", [])
            print(f"✅ {len(models)} modelos encontrados:\n")
            
            for model in models:
                name = model.get("name", "").replace("models/", "")
                display_name = model.get("displayName", "")
                supported_methods = model.get("supportedGenerationMethods", [])
                
                # Solo mostrar modelos que soporten generateContent
                if "generateContent" in supported_methods:
                    print(f"  • {name}")
                    print(f"    Display: {display_name}")
                    print(f"    Methods: {', '.join(supported_methods)}")
                    print()
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Error HTTP {e.code}: {e.reason}")
        try:
            error_json = json.loads(error_body)
            print(f"   {error_json.get('error', {}).get('message', error_body)}")
        except:
            print(f"   {error_body}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
print("✅ Listado completo")
