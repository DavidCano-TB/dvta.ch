"""
Sistema de backup automático cada 5 minutos
Mantiene copias durante 72 horas (3 días) y purga las más antiguas.
Los backups se guardan en: bdd_copy/<YYYY-MM-DD_HH-MM>/<nombre_db>.db
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
BACKUP_DIR = BASE_DIR / "bdd_copy"
RETENTION_HOURS = 72  # 72 horas = 3 días

# Bases de datos a respaldar
DATABASES = [
    "dvdcoin.db",
    "users.db",
    "apuestas.db",
    "messages.db",
    "opo.db",
    "oposiciones.db",
    "rights.db",
    "stats.db",
    "transactions.db",
    "votaciones.db",
]

# Configurar logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'backup_5min.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def verificar_integridad_db(db_path: Path) -> bool:
    """Verifica que la base de datos SQLite no esté corrupta."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] == "ok"
    except Exception as e:
        logger.error(f"Error verificando integridad de {db_path.name}: {e}")
        return False


def hacer_backup() -> tuple[int, int]:
    """
    Realiza backup de todas las bases de datos.
    
    Returns:
        Tupla (exitosos, fallidos)
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    # Timestamp para el nombre de la carpeta
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_timestamp_dir = BACKUP_DIR / timestamp
    backup_timestamp_dir.mkdir(exist_ok=True)

    backups_exitosos = 0
    backups_fallidos = 0

    logger.info(f"=== Backup 5min: {timestamp} ===")

    for db_name in DATABASES:
        db_path = DATA_DIR / db_name

        if not db_path.exists():
            logger.debug(f"BD no encontrada, saltando: {db_name}")
            continue

        # Verificar integridad antes de copiar
        if not verificar_integridad_db(db_path):
            logger.error(f"BD corrupta, saltando: {db_name}")
            backups_fallidos += 1
            continue

        try:
            backup_path = backup_timestamp_dir / db_name
            shutil.copy2(str(db_path), str(backup_path))

            # Verificar que la copia sea válida
            if verificar_integridad_db(backup_path):
                backups_exitosos += 1
            else:
                logger.error(f"Copia corrupta, eliminando: {db_name}")
                backup_path.unlink()
                backups_fallidos += 1

        except Exception as e:
            logger.error(f"Error en backup de {db_name}: {e}")
            backups_fallidos += 1

    logger.info(f"Resultado: {backups_exitosos} exitosos, {backups_fallidos} fallidos")
    return backups_exitosos, backups_fallidos


def purgar_backups_antiguos() -> int:
    """
    Elimina backups con más de RETENTION_HOURS horas de antigüedad.
    
    Returns:
        Número de carpetas eliminadas
    """
    if not BACKUP_DIR.exists():
        return 0

    fecha_limite = datetime.now() - timedelta(hours=RETENTION_HOURS)
    eliminados = 0

    for carpeta in sorted(BACKUP_DIR.iterdir()):
        if not carpeta.is_dir():
            continue

        try:
            # Parsear timestamp del nombre de la carpeta
            fecha_backup = datetime.strptime(carpeta.name, "%Y-%m-%d_%H-%M")

            if fecha_backup < fecha_limite:
                shutil.rmtree(carpeta)
                logger.info(f"Eliminado backup antiguo: {carpeta.name}")
                eliminados += 1

        except ValueError:
            # No es una carpeta con formato de timestamp válido
            logger.warning(f"Carpeta con formato no reconocido: {carpeta.name}")
        except Exception as e:
            logger.error(f"Error eliminando {carpeta.name}: {e}")

    if eliminados > 0:
        logger.info(f"Total eliminados: {eliminados}")

    return eliminados


def main() -> int:
    """Función principal. Retorna 0 si éxito, 1 si fallo."""
    logger.info("=" * 50)
    logger.info("BACKUP CADA 5 MINUTOS (retención 72h)")
    logger.info("=" * 50)

    exitosos, fallidos = hacer_backup()

    if exitosos == 0 and fallidos > 0:
        logger.error("[ERROR] Backup falló completamente")
        return 1

    # Purgar backups antiguos
    purgar_backups_antiguos()

    logger.info("=" * 50)
    return 0


if __name__ == "__main__":
    exit(main())
