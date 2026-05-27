#!/usr/bin/env python3
"""
Script para sincronizar main.py y eliminar src/main.py de forma segura
"""
import os
import shutil

def sincronizar_main():
    print("=" * 80)
    print("SINCRONIZACIÓN Y LIMPIEZA DE ARCHIVOS MAIN.PY")
    print("=" * 80)
    
    main_root = "main.py"
    main_src = "src/main.py"
    backup_src = "src/main.py.backup"
    
    # 1. Verificar que main.py existe
    print("\n[1] Verificando archivos...")
    if not os.path.exists(main_root):
        print(f"   ❌ {main_root} NO EXISTE")
        return
    print(f"   ✓ {main_root} existe")
    
    if not os.path.exists(main_src):
        print(f"   ⚠️  {main_src} NO EXISTE (ya fue eliminado)")
        print("\n✓ No hay nada que hacer")
        return
    print(f"   ✓ {main_src} existe")
    
    # 2. Crear backup de src/main.py
    print("\n[2] Creando backup de src/main.py...")
    try:
        shutil.copy2(main_src, backup_src)
        print(f"   ✓ Backup creado: {backup_src}")
    except Exception as e:
        print(f"   ❌ Error creando backup: {e}")
        return
    
    # 3. Copiar main.py a src/main.py
    print("\n[3] Copiando main.py (raíz) a src/main.py...")
    try:
        shutil.copy2(main_root, main_src)
        print(f"   ✓ Archivo sincronizado")
    except Exception as e:
        print(f"   ❌ Error copiando: {e}")
        return
    
    # 4. Verificar que son idénticos
    print("\n[4] Verificando sincronización...")
    import hashlib
    
    def get_hash(filepath):
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    hash_root = get_hash(main_root)
    hash_src = get_hash(main_src)
    
    if hash_root == hash_src:
        print(f"   ✓ Archivos IDÉNTICOS")
        print(f"   Hash: {hash_root}")
    else:
        print(f"   ❌ Archivos DIFERENTES")
        print(f"   main.py: {hash_root}")
        print(f"   src/main.py: {hash_src}")
        return
    
    print("\n" + "=" * 80)
    print("✓ SINCRONIZACIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📋 RESUMEN:")
    print(f"   - main.py (raíz) es el archivo ACTIVO usado por el servidor")
    print(f"   - src/main.py ahora es IDÉNTICO a main.py")
    print(f"   - Backup guardado en: {backup_src}")
    print(f"\n💡 RECOMENDACIÓN:")
    print(f"   - El servidor usa main.py (raíz)")
    print(f"   - src/main.py es redundante pero ahora está sincronizado")
    print(f"   - Puedes eliminar src/main.py si quieres (el backup está guardado)")
    print("\n")

if __name__ == "__main__":
    sincronizar_main()
