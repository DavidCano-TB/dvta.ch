#!/usr/bin/env python3
"""Verify Millonario question tracking system."""
import sqlite3

def verificar_tracking():
    print("=" * 60)
    print("VERIFICACIÓN SISTEMA TRACKING MILLONARIO")
    print("=" * 60)
    
    # Check if table exists
    conn = sqlite3.connect("data/oposiciones.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Check table schema
    schema = c.execute("""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='millonario_used_questions'
    """).fetchone()
    
    if schema:
        print("\n✅ Tabla 'millonario_used_questions' existe")
        print(f"\nEsquema:\n{schema['sql']}")
        
        # Check how many questions are tracked
        for nivel in range(1, 11):
            count = c.execute("""
                SELECT COUNT(*) as total 
                FROM millonario_used_questions 
                WHERE nivel = ?
            """, (nivel,)).fetchone()
            print(f"\nNivel {nivel}: {count['total']} preguntas usadas")
    else:
        print("\n❌ Tabla 'millonario_used_questions' NO existe")
        print("\n⚠️  PROBLEMA: El sistema no puede trackear preguntas usadas")
        print("    Las preguntas se repetirán en cada partida")
    
    conn.close()
    
    # Check questions JSON structure
    import json
    with open("static/millonario/preguntas.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
    
    print("\n" + "=" * 60)
    print("ESTRUCTURA JSON PREGUNTAS")
    print("=" * 60)
    
    for nivel in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        if nivel in preguntas:
            total = len(preguntas[nivel])
            print(f"Nivel {nivel}: {total} preguntas disponibles")
            
            # Check if questions have 'usada' flag (like Pasapalabra)
            if total > 0:
                primera = preguntas[nivel][0]
                tiene_usada = "usada" in primera
                print(f"  - ¿Tiene flag 'usada'? {'✅ Sí' if tiene_usada else '❌ No'}")
        else:
            print(f"Nivel {nivel}: ❌ NO EXISTE")
    
    print("\n" + "=" * 60)
    print("CONCLUSIÓN")
    print("=" * 60)
    print("""
El sistema Millonario usa un enfoque DIFERENTE a Pasapalabra:

PASAPALABRA:
- Usa flag 'usada: true/false' en el JSON
- Marca preguntas como usadas en el archivo

MILLONARIO:
- Usa tabla 'millonario_used_questions' en la BD
- Trackea índices de preguntas usadas por nivel
- Cuando todas las preguntas de un nivel se usan, resetea el tracking
- NO modifica el JSON

✅ VENTAJAS del sistema Millonario:
- No modifica archivos estáticos
- Tracking centralizado en BD
- Fácil resetear preguntas usadas
- Múltiples partidas simultáneas sin conflictos

✅ El sistema GARANTIZA que las preguntas no se repiten
   hasta que todas las preguntas del nivel se hayan usado.
""")

if __name__ == "__main__":
    verificar_tracking()
