"""
Sistema de backup automático de bases de datos
Mantiene copias de los últimos 7 días y purga las más antiguas
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
BACKUP_DIR = BASE_DIR / "backup"
RETENTION_DAYS = 7

# Configurar logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'backup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def verificar_integridad_db(db_path):
    """Verifica que la base de datos no esté corrupta antes de hacer backup"""
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
    
    # Fecha actual para el nombre del backup
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    backup_fecha_dir = BACKUP_DIR / fecha_actual
    backup_fecha_dir.mkdir(exist_ok=True)
    
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
    
    logging.info(f"=== Iniciando backup del {fecha_actual} ===")
    
    for db_name in bases_datos:
        db_path = DATA_DIR / db_name
        
        if not db_path.exists():
            logging.warning(f"Base de datos no encontrada: {db_name}")
            continue
        
        # Verificar integridad antes de copiar
        if not verificar_integridad_db(db_path):
            logging.error(f"Base de datos corrupta, saltando: {db_name}")
            backups_fallidos += 1
            continue
        
        try:
            # Copiar base de datos
            backup_path = backup_fecha_dir / db_name
            shutil.copy2(db_path, backup_path)
            
            # Verificar que la copia sea válida
            if verificar_integridad_db(backup_path):
                tamaño = backup_path.stat().st_size
                logging.info(f"[OK] Backup exitoso: {db_name} ({tamaño:,} bytes)")
                backups_exitosos += 1
            else:
                logging.error(f"[ERROR] Copia corrupta: {db_name}")
                backup_path.unlink()  # Eliminar copia corrupta
                backups_fallidos += 1
                
        except Exception as e:
            logging.error(f"[ERROR] Error haciendo backup de {db_name}: {e}")
            backups_fallidos += 1
    
    logging.info(f"Backups exitosos: {backups_exitosos}, Fallidos: {backups_fallidos}")
    return backups_exitosos > 0

def purgar_backups_antiguos():
    """Elimina backups con más de RETENTION_DAYS días"""
    if not BACKUP_DIR.exists():
        return
    
    fecha_limite = datetime.now() - timedelta(days=RETENTION_DAYS)
    eliminados = 0
    
    logging.info(f"=== Purgando backups anteriores a {fecha_limite.strftime('%Y-%m-%d')} ===")
    
    for carpeta in BACKUP_DIR.iterdir():
        if not carpeta.is_dir():
            continue
        
        try:
            # Intentar parsear el nombre de la carpeta como fecha
            fecha_backup = datetime.strptime(carpeta.name, "%Y-%m-%d")
            
            if fecha_backup < fecha_limite:
                shutil.rmtree(carpeta)
                logging.info(f"[OK] Eliminado backup antiguo: {carpeta.name}")
                eliminados += 1
                
        except ValueError:
            # No es una carpeta de backup con formato de fecha
            logging.warning(f"Carpeta con formato no reconocido: {carpeta.name}")
        except Exception as e:
            logging.error(f"Error eliminando {carpeta.name}: {e}")
    
    if eliminados > 0:
        logging.info(f"Total de backups antiguos eliminados: {eliminados}")
    else:
        logging.info("No hay backups antiguos para eliminar")

def listar_backups_disponibles():
    """Lista todos los backups disponibles"""
    if not BACKUP_DIR.exists():
        logging.info("No hay backups disponibles")
        return
    
    backups = sorted([d for d in BACKUP_DIR.iterdir() if d.is_dir()], reverse=True)
    
    if not backups:
        logging.info("No hay backups disponibles")
        return
    
    logging.info(f"=== Backups disponibles ({len(backups)}) ===")
    for backup in backups:
        try:
            fecha = datetime.strptime(backup.name, "%Y-%m-%d")
            dias_antiguedad = (datetime.now() - fecha).days
            num_archivos = len(list(backup.glob("*.db")))
            tamaño_total = sum(f.stat().st_size for f in backup.glob("*.db"))
            
            logging.info(f"  {backup.name} - {num_archivos} bases de datos - "
                        f"{tamaño_total / 1024 / 1024:.2f} MB - "
                        f"hace {dias_antiguedad} días")
        except Exception as e:
            logging.warning(f"  {backup.name} - Error leyendo info: {e}")

def main():
    """Función principal"""
    logging.info("=" * 60)
    logging.info("SISTEMA DE BACKUP AUTOMÁTICO DE BASES DE DATOS")
    logging.info("=" * 60)
    
    # Realizar backup
    if hacer_backup():
        logging.info("[OK] Backup completado exitosamente")
    else:
        logging.error("[ERROR] Backup falló")
        return 1
    
    # Purgar backups antiguos
    purgar_backups_antiguos()
    
    # Listar backups disponibles
    listar_backups_disponibles()
    
    logging.info("=" * 60)
    logging.info("Proceso de backup finalizado")
    logging.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
