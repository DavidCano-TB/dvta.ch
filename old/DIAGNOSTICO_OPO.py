#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo del sistema OPO
Muestra el estado de todos los componentes
"""

import json
import os
import sys
import requests

def check_server():
    """Verificar que el servidor está corriendo"""
    print("\n[1/6] Verificando servidor...")
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("  ✓ Servidor corriendo en http://localhost:8000")
            return True
        else:
            print(f"  ✗ Servidor responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Servidor NO está corriendo")
        print(f"     Error: {e}")
        print("\n  SOLUCIÓN: Ejecuta 'python main.py' en otra terminal")
        return False

def check_questions():
    """Verificar archivo de preguntas"""
    print("\n[2/6] Verificando archivo de preguntas...")
    path = "static/opo/preguntas_opo_nebulosa.json"
    
    if not os.path.exists(path):
        print(f"  ✗ Archivo NO existe: {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            preguntas = json.load(f)
        
        if len(preguntas) > 0:
            print(f"  ✓ Archivo existe: {len(preguntas)} preguntas")
            print(f"     Bloques esperados: {(len(preguntas) + 9) // 10}")
            return True
        else:
            print(f"  ✗ Archivo vacío")
            return False
    except Exception as e:
        print(f"  ✗ Error al leer: {e}")
        return False

def check_main_py():
    """Verificar main.py"""
    print("\n[3/6] Verificando main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        count = contenido.count('def get_opo_manager')
        
        if count == 1:
            print(f"  ✓ get_opo_manager definido 1 vez (correcto)")
            return True
        elif count > 1:
            print(f"  ✗ get_opo_manager definido {count} veces (debe ser 1)")
            print(f"     SOLUCIÓN: Hay código duplicado en main.py")
            return False
        else:
            print(f"  ✗ get_opo_manager NO encontrado")
            return False
    except Exception as e:
        print(f"  ✗ Error al leer main.py: {e}")
        return False

def check_html():
    """Verificar game.html"""
    print("\n[4/6] Verificando game.html...")
    
    path = "static/opo/game.html"
    if not os.path.exists(path):
        print(f"  ✗ Archivo NO existe: {path}")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        checks = [
            ('waitBlockGrid', 'div#waitBlockGrid'),
            ('renderWaiting', 'función renderWaiting'),
            ('blockBtn', 'clase .blockBtn'),
        ]
        
        all_ok = True
        for buscar, nombre in checks:
            if buscar in contenido:
                print(f"  ✓ {nombre} encontrado")
            else:
                print(f"  ✗ {nombre} NO encontrado")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ✗ Error al leer game.html: {e}")
        return False

def check_opo_endpoint():
    """Verificar endpoint /opo"""
    print("\n[5/6] Verificando endpoint /opo...")
    
    try:
        response = requests.get("http://localhost:8000/opo", timeout=2)
        if response.status_code == 200:
            html = response.text
            if 'waitBlockGrid' in html:
                print("  ✓ Endpoint /opo responde correctamente")
                print("  ✓ HTML contiene waitBlockGrid")
                return True
            else:
                print("  ✗ HTML NO contiene waitBlockGrid")
                return False
        else:
            print(f"  ✗ Endpoint responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error al conectar: {e}")
        return False

def check_database():
    """Verificar base de datos"""
    print("\n[6/6] Verificando base de datos...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('data/rights.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM opo_players")
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("SELECT username FROM opo_players")
            usuarios = [row[0] for row in cursor.fetchall()]
            print(f"  ✓ {count} usuarios con acceso OPO:")
            print(f"     {', '.join(usuarios)}")
            conn.close()
            return True
        else:
            print(f"  ✗ No hay usuarios con acceso OPO")
            conn.close()
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("="*60)
    print("DIAGNÓSTICO COMPLETO DEL SISTEMA OPO")
    print("="*60)
    
    checks = [
        check_server(),
        check_questions(),
        check_main_py(),
        check_html(),
        check_opo_endpoint(),
        check_database(),
    ]
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nTests pasados: {passed}/{total}")
    
    if all(checks):
        print("\n✓ TODOS LOS TESTS PASAN")
        print("\nEl sistema OPO está correctamente configurado.")
        print("\nPróximos pasos:")
        print("  1. Abre http://localhost:8000/opo en tu navegador")
        print("  2. Inicia sesión si es necesario")
        print("  3. Deberías ver 30 bloques numerados")
        print("\nSi NO ves los bloques:")
        print("  1. Abre la consola del navegador (F12)")
        print("  2. Ve a la pestaña Console")
        print("  3. Busca errores en rojo")
        print("  4. Copia los errores y repórtalos")
    else:
        print("\n✗ ALGUNOS TESTS FALLARON")
        print("\nRevisa los errores arriba y corrígelos.")
        
        if not checks[0]:
            print("\n⚠️ CRÍTICO: El servidor NO está corriendo")
            print("   Ejecuta: python main.py")

if __name__ == "__main__":
    main()
