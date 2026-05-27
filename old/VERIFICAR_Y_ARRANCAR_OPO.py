#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación completa del sistema OPO
Verifica backend, frontend y arranca el servidor
"""

import json
import os
import sys
import time
import subprocess

def verificar_preguntas():
    """Verificar que el archivo de preguntas existe y tiene contenido"""
    print("\n[1/5] Verificando archivo de preguntas...")
    path = "static/opo/preguntas_opo_nebulosa.json"
    
    if not os.path.exists(path):
        print(f"  ✗ ERROR: No existe {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            preguntas = json.load(f)
        
        if not isinstance(preguntas, list):
            print(f"  ✗ ERROR: El archivo no contiene una lista")
            return False
        
        if len(preguntas) == 0:
            print(f"  ✗ ERROR: El archivo está vacío")
            return False
        
        print(f"  ✓ Archivo existe: {len(preguntas)} preguntas")
        return True
    except Exception as e:
        print(f"  ✗ ERROR al leer: {e}")
        return False

def verificar_main_py():
    """Verificar que main.py no tiene código duplicado"""
    print("\n[2/5] Verificando main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Contar definiciones de get_opo_manager
        count = contenido.count('def get_opo_manager')
        
        if count == 0:
            print(f"  ✗ ERROR: No se encontró get_opo_manager")
            return False
        elif count > 1:
            print(f"  ✗ ERROR: get_opo_manager definido {count} veces (debe ser 1)")
            return False
        else:
            print(f"  ✓ get_opo_manager definido 1 vez")
        
        # Verificar que OpoManager carga preguntas
        if '_load_opo_questions()' not in contenido:
            print(f"  ✗ ERROR: OpoManager no llama a _load_opo_questions()")
            return False
        
        print(f"  ✓ OpoManager configurado correctamente")
        return True
    except Exception as e:
        print(f"  ✗ ERROR al leer main.py: {e}")
        return False

def verificar_html():
    """Verificar que game.html tiene el código necesario"""
    print("\n[3/5] Verificando game.html...")
    
    path = "static/opo/game.html"
    if not os.path.exists(path):
        print(f"  ✗ ERROR: No existe {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar elementos clave
        checks = [
            ('waitBlockGrid', 'div#waitBlockGrid'),
            ('renderWaiting', 'función renderWaiting'),
            ('blockBtn', 'clase .blockBtn'),
            ('connectWS', 'función connectWS'),
        ]
        
        for buscar, nombre in checks:
            if buscar not in contenido:
                print(f"  ✗ ERROR: No se encontró {nombre}")
                return False
        
        print(f"  ✓ HTML contiene todos los elementos necesarios")
        return True
    except Exception as e:
        print(f"  ✗ ERROR al leer game.html: {e}")
        return False

def verificar_base_datos():
    """Verificar que la base de datos tiene usuarios OPO"""
    print("\n[4/5] Verificando base de datos...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('data/rights.db')
        cursor = conn.cursor()
        
        # Verificar tabla opo_players
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opo_players'")
        if not cursor.fetchone():
            print(f"  ✗ ERROR: Tabla opo_players no existe")
            conn.close()
            return False
        
        # Contar usuarios
        cursor.execute("SELECT COUNT(*) FROM opo_players")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"  ✗ ERROR: No hay usuarios con acceso OPO")
            conn.close()
            return False
        
        # Listar usuarios
        cursor.execute("SELECT username FROM opo_players")
        usuarios = [row[0] for row in cursor.fetchall()]
        
        print(f"  ✓ {count} usuarios con acceso: {', '.join(usuarios)}")
        conn.close()
        return True
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def arrancar_servidor():
    """Arrancar el servidor FastAPI"""
    print("\n[5/5] Arrancando servidor...")
    print("  → Ejecutando: python main.py")
    print("  → Servidor en: http://localhost:8000")
    print("  → OPO en: http://localhost:8000/opo")
    print("\n" + "="*60)
    print("SERVIDOR ARRANCANDO...")
    print("="*60 + "\n")
    
    try:
        # Arrancar servidor
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\n✗ ERROR al arrancar servidor: {e}")
        return False
    
    return True

def main():
    print("="*60)
    print("VERIFICACIÓN COMPLETA DEL SISTEMA OPO")
    print("="*60)
    
    # Ejecutar verificaciones
    checks = [
        verificar_preguntas(),
        verificar_main_py(),
        verificar_html(),
        verificar_base_datos(),
    ]
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    if all(checks):
        print("✓ TODAS LAS VERIFICACIONES PASARON")
        print("\nEl sistema OPO está correctamente configurado.")
        print("Arrancando servidor...\n")
        arrancar_servidor()
    else:
        print("✗ ALGUNAS VERIFICACIONES FALLARON")
        print("\nPor favor, corrige los errores antes de arrancar el servidor.")
        sys.exit(1)

if __name__ == "__main__":
    main()
