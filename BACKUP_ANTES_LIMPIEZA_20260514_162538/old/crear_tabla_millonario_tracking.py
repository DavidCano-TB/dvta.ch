#!/usr/bin/env python3
"""Create the missing millonario_used_questions table."""
import sqlite3

def crear_tabla():
    print("=" * 60)
    print("CREANDO TABLA millonario_used_questions")
    print("=" * 60)
    
    conn = sqlite3.connect("data/oposiciones.db")
    c = conn.cursor()
    
    # Check if table exists
    exists = c.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='millonario_used_questions'
    """).fetchone()
    
    if exists:
        print("\n✅ La tabla ya existe")
    else:
        print("\n⚠️  La tabla NO existe - creándola ahora...")
        
        # Create table
        c.execute("""
            CREATE TABLE millonario_used_questions (
                nivel INTEGER NOT NULL,
                question_idx INTEGER NOT NULL,
                PRIMARY KEY (nivel, question_idx)
            )
        """)
        conn.commit()
        
        print("✅ Tabla creada exitosamente")
        
        # Verify
        schema = c.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='millonario_used_questions'
        """).fetchone()
        
        print(f"\nEsquema creado:\n{schema[0]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)
    print("""
✅ Sistema de tracking configurado correctamente

Ahora el juego Millonario:
- Trackeará qué preguntas se han usado en cada nivel
- NO repetirá preguntas hasta que todas se hayan usado
- Reseteará automáticamente cuando se agoten las preguntas
- Funcionará igual que Pasapalabra pero usando BD en vez de JSON
""")

if __name__ == "__main__":
    crear_tabla()
