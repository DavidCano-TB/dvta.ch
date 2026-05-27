#!/usr/bin/env python3
import json
import os

print("=" * 70)
print("  VERIFICACIÓN DE PREGUNTAS OPO")
print("=" * 70)
print()

archivo = "static/opo/preguntas_opo_nebulosa.json"

if not os.path.exists(archivo):
    print(f"❌ El archivo NO existe: {archivo}")
    exit(1)

print(f"✓ Archivo encontrado: {archivo}")
print()

try:
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total de preguntas: {len(data)}")
    print()
    
    if len(data) == 0:
        print("❌ El archivo está VACÍO")
        exit(1)
    
    # Verificar estructura de la primera pregunta
    print("Estructura de la primera pregunta:")
    primera = data[0]
    for key, value in primera.items():
        if isinstance(value, str) and len(value) > 50:
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    print()
    
    # Verificar que todas las preguntas tengan los campos necesarios
    campos_requeridos = ['n', 'p', 'A', 'B', 'C', 'D', 'r']
    preguntas_validas = 0
    preguntas_invalidas = 0
    
    for i, pregunta in enumerate(data):
        valida = all(campo in pregunta for campo in campos_requeridos)
        if valida:
            preguntas_validas += 1
        else:
            preguntas_invalidas += 1
            if preguntas_invalidas <= 5:  # Mostrar solo las primeras 5
                faltantes = [c for c in campos_requeridos if c not in pregunta]
                print(f"❌ Pregunta {i+1} inválida. Faltan campos: {faltantes}")
    
    print()
    print(f"Preguntas válidas: {preguntas_validas}")
    print(f"Preguntas inválidas: {preguntas_invalidas}")
    print()
    
    # Calcular bloques
    total_bloques = (len(data) + 9) // 10
    print(f"Total de bloques (10 preguntas cada uno): {total_bloques}")
    print()
    
    if preguntas_validas > 0:
        print("✅ El archivo de preguntas es VÁLIDO")
    else:
        print("❌ El archivo de preguntas es INVÁLIDO")
        
except json.JSONDecodeError as e:
    print(f"❌ Error al parsear JSON: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
