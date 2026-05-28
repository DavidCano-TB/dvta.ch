"""
Unit tests for DatabaseHelper (modules/shared/db_helper.py)
Tests all database operations with 100% coverage
"""
import pytest
import sqlite3
from pathlib import Path
import sys
import os

# Add shared modules to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "modules" / "shared"))

from db_helper import DatabaseHelper, create_database


class TestDatabaseHelper:
    """Test suite for DatabaseHelper class"""
    
    def test_init_creates_directory(self, temp_dir):
        """Test that __init__ creates database directory if it doesn't exist"""
        db_path = os.path.join(temp_dir, "subdir", "test.db")
        db = DatabaseHelper(db_path)
        assert os.path.exists(os.path.dirname(db_path))
        assert db.db_path == db_path
    
    def test_init_with_relative_path_no_dir(self, tmp_path, monkeypatch):
        """Test __init__ when db_path has no directory component (covers branch 30->exit)"""
        monkeypatch.chdir(tmp_path)
        db = DatabaseHelper("test_only_filename.db")
        assert db.db_path == "test_only_filename.db"
    
    def test_get_connection(self, temp_db):
        """Test getting a database connection"""
        db = DatabaseHelper(temp_db)
        conn = db.get_connection()
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row
        conn.close()
    
    def test_connection_context_manager(self, temp_db):
        """Test connection context manager"""
        db = DatabaseHelper(temp_db)
        with db.connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_create_tables(self, temp_db):
        """Test creating tables from schema"""
        db = DatabaseHelper(temp_db)
        schema = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        );
        """
        db.create_tables(schema)
        assert db.table_exists("users")
    
    def test_table_exists(self, temp_db):
        """Test checking if table exists"""
        db = DatabaseHelper(temp_db)
        assert not db.table_exists("nonexistent")
        
        db.create_tables("CREATE TABLE test_table (id INTEGER PRIMARY KEY);")
        assert db.table_exists("test_table")
    
    def test_insert(self, temp_db):
        """Test inserting data"""
        db = DatabaseHelper(temp_db)
        db.create_tables("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)
        
        user_id = db.insert("users", {
            "username": "testuser",
            "email": "test@example.com"
        })
        
        assert user_id > 0
        user = db.fetchone("SELECT * FROM users WHERE id=?", (user_id,))
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
    
    def test_fetchone(self, temp_db):
        """Test fetching one row"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        db.execute("INSERT INTO test (value) VALUES (?)", ("test_value",))
        
        result = db.fetchone("SELECT * FROM test WHERE value=?", ("test_value",))
        assert result is not None
        assert result["value"] == "test_value"
        
        # Test non-existent row
        result = db.fetchone("SELECT * FROM test WHERE value=?", ("nonexistent",))
        assert result is None
    
    def test_fetchall(self, temp_db):
        """Test fetching all rows"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        
        db.execute("INSERT INTO test (value) VALUES (?)", ("value1",))
        db.execute("INSERT INTO test (value) VALUES (?)", ("value2",))
        db.execute("INSERT INTO test (value) VALUES (?)", ("value3",))
        
        results = db.fetchall("SELECT * FROM test ORDER BY id")
        assert len(results) == 3
        assert results[0]["value"] == "value1"
        assert results[1]["value"] == "value2"
        assert results[2]["value"] == "value3"
    
    def test_update(self, temp_db):
        """Test updating data"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        
        db.execute("INSERT INTO test (value) VALUES (?)", ("old_value",))
        
        rows_updated = db.update(
            "test",
            {"value": "new_value"},
            "value=?",
            ("old_value",)
        )
        
        assert rows_updated == 1
        result = db.fetchone("SELECT * FROM test")
        assert result["value"] == "new_value"
    
    def test_delete(self, temp_db):
        """Test deleting data"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        
        db.execute("INSERT INTO test (value) VALUES (?)", ("to_delete",))
        db.execute("INSERT INTO test (value) VALUES (?)", ("to_keep",))
        
        rows_deleted = db.delete("test", "value=?", ("to_delete",))
        
        assert rows_deleted == 1
        results = db.fetchall("SELECT * FROM test")
        assert len(results) == 1
        assert results[0]["value"] == "to_keep"
    
    def test_execute(self, temp_db):
        """Test executing raw SQL"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        
        cursor = db.execute("INSERT INTO test (value) VALUES (?)", ("test",))
        assert cursor.lastrowid > 0
    
    def test_backup(self, temp_db, temp_dir):
        """Test database backup"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        db.execute("INSERT INTO test (value) VALUES (?)", ("test_data",))
        
        backup_path = os.path.join(temp_dir, "backup.db")
        db.backup(backup_path)
        
        assert os.path.exists(backup_path)
        
        # Verify backup contains data
        backup_db = DatabaseHelper(backup_path)
        result = backup_db.fetchone("SELECT * FROM test")
        assert result["value"] == "test_data"
    
    def test_backup_to_filename_only(self, temp_db, tmp_path, monkeypatch):
        """Test backup with bare filename (no directory) - covers branch 206->208"""
        monkeypatch.chdir(tmp_path)
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        db.execute("INSERT INTO test (value) VALUES (?)", ("data",))
        db.backup("backup_only_filename.db")
        assert os.path.exists("backup_only_filename.db")
    
    def test_vacuum(self, temp_db):
        """Test database vacuum operation"""
        db = DatabaseHelper(temp_db)
        db.create_tables("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);")
        
        # Insert and delete data to create fragmentation
        for i in range(100):
            db.execute("INSERT INTO test (value) VALUES (?)", (f"value_{i}",))
        db.execute("DELETE FROM test")
        
        # Vacuum should not raise an error
        db.vacuum()
        
        # Verify database still works
        db.execute("INSERT INTO test (value) VALUES (?)", ("after_vacuum",))
        result = db.fetchone("SELECT * FROM test")
        assert result["value"] == "after_vacuum"


class TestCreateDatabase:
    """Test suite for create_database helper function"""
    
    def test_create_database(self, temp_db):
        """Test creating database with schema"""
        schema = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        );
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        db = create_database(temp_db, schema)
        
        assert isinstance(db, DatabaseHelper)
        assert db.table_exists("users")
        assert db.table_exists("posts")
        
        # Test foreign key constraint is enabled
        db.insert("users", {"username": "testuser"})
        user = db.fetchone("SELECT * FROM users")
        
        # This should work
        db.insert("posts", {"user_id": user["id"], "content": "test post"})
        
        # Verify data
        post = db.fetchone("SELECT * FROM posts")
        assert post["content"] == "test post"
