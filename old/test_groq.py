#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from ai_helper import GroqAI

print("\n" + "="*60)
print("TEST GROQ")
print("="*60)

ai = GroqAI()
print(f"✓ API key: {ai.api_key[:20]}...")
print(f"✓ Modelo: {ai.model}")

# Test 1: Verificar personaje
print("\n--- Test 1: Verificar 'pikachu' ---")
result = ai.verify_character("pikachu")
print(f"exists: {result.get('exists')}")
print(f"corrected_name: {result.get('corrected_name')}")
print(f"confidence: {result.get('confidence')}")
print(f"main_known_for: {result.get('main_known_for')}")

# Test 2: Con errores
print("\n--- Test 2: Verificar 'miki maus' ---")
result2 = ai.verify_character("miki maus")
print(f"exists: {result2.get('exists')}")
print(f"corrected_name: {result2.get('corrected_name')}")
print(f"confidence: {result2.get('confidence')}")

print("\n" + "="*60)
print("✅ TESTS COMPLETADOS")
print("="*60)
