"""
Limpia los archivos de backup antiguos del directorio data/
Elimina archivos .db con formato de fecha en el nombre
"""
import os
import re
from pathlib import Path
from datetime import datetime
import logging

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def es_backup_antiguo(nombre_archivo):
    """
    Detecta si un archivo es un backup antiguo basándose en su nombre
    Ejemplos: dvdcoin_2026-03-20_09-39.db, messages - Copie.db, users_backup.db
    """
    # Patrones de backups antiguos
    patrones = [
        r'.*_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.db$',  # dvdcoin_2026-03-20_09-39.db
        r'.*\s*-\s*Copie.*\.db$',  # messages - Copie.db
        r'.*_backup\.db$',  # users_backup.db
        r'.*_\d{4}-\d{2}-\d{2}\.db$',  # dvdcoin_2026-03-20.db
    ]
    
    for patron in patrones:
        if re.match(patron, nombre_archivo, re.IGNORECASE):
            return True
    return False

def listar_backups_antiguos():
    """Lista todos los archivos de backup antiguos"""
    if not DATA_DIR.exists():
        logging.error(f"Directorio no encontrado: {DATA_DIR}")
        return []
    
    backups = []
    for archivo in DATA_DIR.glob("*.db"):
        if es_backup_antiguo(archivo.name):
            backups.append(archivo)
    
    return sorted(backups)

def eliminar_backups_antiguos(confirmar=True):
    """Elimina los archivos de backup antiguos"""
    backups = listar_backups_antiguos()
    
    if not backups:
        logging.info("No se encontraron backups antiguos para eliminar")
        return 0
    
    logging.info(f"Se encontraron {len(backups)} archivos de backup antiguos:")
    print()
    
    tamaño_total = 0
    for backup in backups:
        tamaño = backup.stat().st_size
        tamaño_total += tamaño
        print(f"  - {backup.name} ({tamaño / 1024 / 1024:.2f} MB)")
    
    print()
    print(f"Espacio total a liberar: {tamaño_total / 1024 / 1024:.2f} MB")
    print()
    
    if confirmar:
        respuesta = input("¿Deseas eliminar estos archivos? (s/n): ").strip().lower()
        if respuesta != 's':
            logging.info("Operación cancelada por el usuario")
            return 0
    
    print()
    
    eliminados = 0
    errores = 0
    
    for backup in backups:
        try:
            backup.unlink()
            logging.info(f"✓ Eliminado: {backup.name}")
            eliminados += 1
        except Exception as e:
            logging.error(f"✗ Error eliminando {backup.name}: {e}")
            errores += 1
    
    print()
    logging.info(f"Archivos eliminados: {eliminados}")
    if errores > 0:
        logging.warning(f"Errores: {errores}")
    
    return eliminados

def main():
    import sys
    
    print("=" * 60)
    print("LIMPIEZA DE BACKUPS ANTIGUOS")
    print("=" * 60)
    print()
    print("Este script eliminará los siguientes tipos de archivos:")
    print("  - Backups con fecha en el nombre (dvdcoin_2026-03-20_09-39.db)")
    print("  - Copias (messages - Copie.db)")
    print("  - Backups explícitos (users_backup.db)")
    print()
    print(f"Directorio: {DATA_DIR}")
    print()
    print("=" * 60)
    print()
    
    # Verificar si se pasó el argumento --auto para confirmación automática
    confirmar = "--auto" not in sys.argv
    
    eliminados = eliminar_backups_antiguos(confirmar=confirmar)
    
    print()
    print("=" * 60)
    if eliminados > 0:
        print("✓ LIMPIEZA COMPLETADA")
    else:
        print("✓ NO HAY ARCHIVOS PARA LIMPIAR")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
