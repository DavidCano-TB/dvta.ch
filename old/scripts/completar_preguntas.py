#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para completar el archivo preguntas.json con 50 preguntas por letra
"""
import json
import os

# Ruta del archivo
archivo = r"c:\dvdcoin\static\pasapalabra\preguntas.json"

# Leer el archivo actual
try:
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
        # Intentar cargar como JSON
        try:
            data = json.loads(contenido)
            print(f"✓ Archivo JSON válido")
            print(f"✓ Letras actuales: {list(data.keys())}")
            print(f"✓ Preguntas por letra: {{{k: len(v) for k, v in data.items()}}}")
        except json.JSONDecodeError as e:
            print(f"✗ Error JSON: {e}")
            print(f"✗ Posición del error: línea {e.lineno}, columna {e.colno}")
            print(f"✗ Contenido alrededor del error:")
            lines = contenido.split('\n')
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            for i in range(start, end):
                marker = " >>> " if i == e.lineno - 1 else "     "
                print(f"{marker}{i+1}: {lines[i]}")
except Exception as e:
    print(f"✗ Error al leer archivo: {e}")
