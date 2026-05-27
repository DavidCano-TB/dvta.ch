#!/usr/bin/env python3
"""
Script para forzar la recarga del servidor matando procesos y limpiando caché
"""
import os
import sys
import subprocess
import time
import shutil

def forzar_recarga():
    print("=" * 80)
    print("FORZANDO RECARGA DEL SERVIDOR")
    print("=" * 80)
    
    # 1. Matar todos los procesos de Python
    print("\n[1] Deteniendo procesos de Python...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/T'], 
                         capture_output=True, check=False)
        else:  # Linux/Mac
            subprocess.run(['pkill', '-9', 'python'], 
                         capture_output=True, check=False)
        print("   ✓ Procesos detenidos")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # 2. Limpiar caché de Python
    print("\n[2] Limpiando caché de Python...")
    cache_dirs = ['__pycache__', 'src/__pycache__']
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✓ {cache_dir} eliminado")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {cache_dir}: {e}")
    
    # 3. Limpiar archivos .pyc
    print("\n[3] Limpiando archivos .pyc...")
    count = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    count += 1
                except:
                    pass
    print(f"   ✓ {count} archivos .pyc eliminados")
    
    # 4. Esperar
    print("\n[4] Esperando 2 segundos...")
    time.sleep(2)
    print("   ✓ Listo")
    
    print("\n" + "=" * 80)
    print("✓ LIMPIEZA COMPLETADA")
    print("=" * 80)
    print("\nAhora puedes iniciar el servidor con:")
    print("   python main.py")
    print("\nO ejecutar:")
    print("   REINICIAR_SERVIDOR_LIMPIO.bat")
    print("\n")

if __name__ == "__main__":
    forzar_recarga()
