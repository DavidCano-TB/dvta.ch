"""
Sistema de backup automático cada 30 minutos
Mantiene las últimas 48 copias (24 horas de backups)
"""
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuración
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup_30min"
MAX_BACKUPS = 48  # 24 horas de backups (cada 30 min)

# Configurar logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'backup_30min.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def verificar_integridad_db(db_path):
    """Verifica que la base de datos no esté corrupta"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] == "ok"
    except Exception as e:
        logging.error(f"Error verificando integridad de {db_path}: {e}")
        return False

def hacer_backup():
    """Realiza backup de todas las bases de datos"""
    # Crear directorio de backup si no existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Timestamp para el nombre del backup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_timestamp_dir = BACKUP_DIR / timestamp
    backup_timestamp_dir.mkdir(exist_ok=True)
    
    # Lista de bases de datos a respaldar
    bases_datos = [
        "dvdcoin.db",
        "users.db",
        "apuestas.db",
        "messages.db",
        "opo.db",
        "oposiciones.db",
        "rights.db",
        "stats.db",
        "transactions.db",
        "votaciones.db"
    ]
    
    backups_exitosos = 0
    backups_fallidos = 0
    
    logging.info(f"=== Backup {timestamp} ===")
    
    for db_name in bases_datos:
        db_path = DATA_DIR / db_name
        
        if not db_path.exists():
            continue
        
        # Verificar integridad antes de copiar
        if not verificar_integridad_db(db_path):
            logging.error(f"BD corrupta, saltando: {db_name}")
            backups_fallidos += 1
            continue
        
        try:
            # Copiar base de datos
            backup_path = backup_timestamp_dir / db_name
            shutil.copy2(db_path, backup_path)
            
            # Verificar que la copia sea válida
            if verificar_integridad_db(backup_path):
                backups_exitosos += 1
            else:
                logging.error(f"Copia corrupta: {db_name}")
                backup_path.unlink()
                backups_fallidos += 1
                
        except Exception as e:
            logging.error(f"Error en backup de {db_name}: {e}")
            backups_fallidos += 1
    
    logging.info(f"Exitosos: {backups_exitosos}, Fallidos: {backups_fallidos}")
    return backups_exitosos > 0

def purgar_backups_antiguos():
    """Mantiene solo los últimos MAX_BACKUPS backups"""
    if not BACKUP_DIR.exists():
        return
    
    # Obtener todas las carpetas de backup ordenadas por fecha
    backups = sorted([d for d in BACKUP_DIR.iterdir() if d.is_dir()])
    
    # Si hay más de MAX_BACKUPS, eliminar los más antiguos
    if len(backups) > MAX_BACKUPS:
        backups_a_eliminar = backups[:-MAX_BACKUPS]
        
        for backup in backups_a_eliminar:
            try:
                shutil.rmtree(backup)
                logging.info(f"Eliminado backup antiguo: {backup.name}")
            except Exception as e:
                logging.error(f"Error eliminando {backup.name}: {e}")

def main():
    """Función principal"""
    logging.info("=" * 60)
    logging.info("BACKUP CADA 30 MINUTOS")
    logging.info("=" * 60)
    
    # Realizar backup
    if hacer_backup():
        logging.info("[OK] Backup completado")
    else:
        logging.error("[ERROR] Backup falló")
        return 1
    
    # Purgar backups antiguos
    purgar_backups_antiguos()
    
    logging.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
