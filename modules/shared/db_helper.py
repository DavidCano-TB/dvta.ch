"""
Shared Database Helper - Reutilizable para todos los módulos
Maneja conexiones y operaciones comunes de SQLite
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseHelper:
    """Helper para manejar bases de datos SQLite de forma consistente"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el helper de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Crea el directorio de la BD si no existe"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            Conexión SQLite configurada
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    @contextmanager
    def connection(self):
        """
        Context manager para conexiones automáticas
        
        Usage:
            with db.connection() as conn:
                conn.execute("SELECT * FROM users")
        """
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """
        Ejecuta una query y retorna el cursor
        
        Args:
            query: Query SQL
            params: Parámetros de la query
        
        Returns:
            Cursor con los resultados
        """
        with self.connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor
    
    def fetchone(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una query y retorna una fila
        
        Args:
            query: Query SQL
            params: Parámetros de la query
        
        Returns:
            Diccionario con la fila o None
        """
        with self.connection() as conn:
            cursor = conn.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetchall(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una query y retorna todas las filas
        
        Args:
            query: Query SQL
            params: Parámetros de la query
        
        Returns:
            Lista de diccionarios con las filas
        """
        with self.connection() as conn:
            cursor = conn.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Inserta una fila en una tabla
        
        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a insertar
        
        Returns:
            ID de la fila insertada
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.connection() as conn:
            cursor = conn.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = None) -> int:
        """
        Actualiza filas en una tabla
        
        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a actualizar
            where: Cláusula WHERE
            where_params: Parámetros de la cláusula WHERE
        
        Returns:
            Número de filas actualizadas
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (where_params or ())
        
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def delete(self, table: str, where: str, where_params: tuple = None) -> int:
        """
        Elimina filas de una tabla
        
        Args:
            table: Nombre de la tabla
            where: Cláusula WHERE
            where_params: Parámetros de la cláusula WHERE
        
        Returns:
            Número de filas eliminadas
        """
        query = f"DELETE FROM {table} WHERE {where}"
        
        with self.connection() as conn:
            cursor = conn.execute(query, where_params or ())
            conn.commit()
            return cursor.rowcount
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe
        
        Args:
            table_name: Nombre de la tabla
        
        Returns:
            True si existe, False si no
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetchone(query, (table_name,))
        return result is not None
    
    def create_tables(self, schema: str):
        """
        Crea tablas desde un schema SQL
        
        Args:
            schema: Script SQL con CREATE TABLE statements
        """
        with self.connection() as conn:
            conn.executescript(schema)
            conn.commit()
        logger.info(f"Tables created in {self.db_path}")
    
    def backup(self, backup_path: str):
        """
        Crea un backup de la base de datos
        
        Args:
            backup_path: Ruta donde guardar el backup
        """
        import shutil
        backup_dir = os.path.dirname(backup_path)
        if backup_dir:
            os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
    
    def vacuum(self):
        """Optimiza la base de datos (VACUUM)"""
        with self.connection() as conn:
            conn.execute("VACUUM")
        logger.info(f"Database vacuumed: {self.db_path}")


def create_database(db_path: str, schema: str) -> DatabaseHelper:
    """
    Crea una base de datos con un schema
    
    Args:
        db_path: Ruta al archivo de base de datos
        schema: Script SQL con CREATE TABLE statements
    
    Returns:
        DatabaseHelper configurado
    """
    db = DatabaseHelper(db_path)
    db.create_tables(schema)
    return db
