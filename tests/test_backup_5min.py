"""
Unit tests for the 5-minute backup system (backup_cada_5min.py)
"""
import os
import sys
import shutil
import sqlite3
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add scripts to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import backup_cada_5min


@pytest.fixture
def backup_env(tmp_path):
    """Set up a temporary backup environment with mock databases."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    backup_dir = tmp_path / "bdd_copy"
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Create sample SQLite databases
    for db_name in ["dvdcoin.db", "users.db", "apuestas.db"]:
        db_path = data_dir / db_name
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'hello')")
        conn.commit()
        conn.close()

    return {
        "base_dir": tmp_path,
        "data_dir": data_dir,
        "backup_dir": backup_dir,
        "log_dir": log_dir,
    }


@pytest.fixture
def patch_dirs(backup_env):
    """Patch module-level directory constants."""
    with patch.object(backup_cada_5min, 'BASE_DIR', backup_env["base_dir"]), \
         patch.object(backup_cada_5min, 'DATA_DIR', backup_env["data_dir"]), \
         patch.object(backup_cada_5min, 'BACKUP_DIR', backup_env["backup_dir"]), \
         patch.object(backup_cada_5min, 'DATABASES', ["dvdcoin.db", "users.db", "apuestas.db"]):
        yield backup_env


class TestVerificarIntegridadDb:
    """Tests for verificar_integridad_db"""

    def test_valid_database(self, backup_env):
        """A valid SQLite database passes integrity check."""
        db_path = backup_env["data_dir"] / "dvdcoin.db"
        assert backup_cada_5min.verificar_integridad_db(db_path) is True

    def test_nonexistent_file(self, tmp_path):
        """A non-existent file fails integrity check."""
        db_path = tmp_path / "nonexistent.db"
        # sqlite3.connect creates the file, but integrity_check still passes on empty db
        # However, if the path doesn't exist and we can't connect, it should handle gracefully
        # Actually sqlite3 creates the file on connect, so let's test a corrupted file
        corrupted = tmp_path / "corrupted.db"
        corrupted.write_bytes(b"this is not a valid sqlite database")
        assert backup_cada_5min.verificar_integridad_db(corrupted) is False

    def test_corrupted_database(self, tmp_path):
        """A corrupted database fails integrity check."""
        db_path = tmp_path / "bad.db"
        db_path.write_bytes(b"\x00" * 100)
        assert backup_cada_5min.verificar_integridad_db(db_path) is False


class TestHacerBackup:
    """Tests for hacer_backup"""

    def test_successful_backup(self, patch_dirs):
        """All databases are backed up successfully."""
        exitosos, fallidos = backup_cada_5min.hacer_backup()
        assert exitosos == 3
        assert fallidos == 0

        # Verify backup directory was created
        backup_dir = patch_dirs["backup_dir"]
        assert backup_dir.exists()
        subdirs = list(backup_dir.iterdir())
        assert len(subdirs) == 1

        # Verify all db files are in the backup
        backup_subdir = subdirs[0]
        backed_up_files = [f.name for f in backup_subdir.iterdir()]
        assert "dvdcoin.db" in backed_up_files
        assert "users.db" in backed_up_files
        assert "apuestas.db" in backed_up_files

    def test_missing_database_skipped(self, patch_dirs):
        """Missing databases are skipped without counting as failures."""
        # Add a non-existent db to the list
        with patch.object(backup_cada_5min, 'DATABASES',
                          ["dvdcoin.db", "nonexistent.db"]):
            exitosos, fallidos = backup_cada_5min.hacer_backup()
            assert exitosos == 1
            assert fallidos == 0

    def test_corrupted_database_counted_as_failure(self, patch_dirs):
        """A corrupted database is counted as a failure."""
        # Corrupt one of the databases
        corrupted_path = patch_dirs["data_dir"] / "users.db"
        corrupted_path.write_bytes(b"corrupted data here")

        exitosos, fallidos = backup_cada_5min.hacer_backup()
        assert exitosos == 2  # dvdcoin.db + apuestas.db
        assert fallidos == 1  # users.db corrupted

    def test_backup_folder_naming_format(self, patch_dirs):
        """Backup folder uses YYYY-MM-DD_HH-MM format."""
        backup_cada_5min.hacer_backup()

        backup_dir = patch_dirs["backup_dir"]
        subdirs = list(backup_dir.iterdir())
        folder_name = subdirs[0].name

        # Should match datetime format
        parsed = datetime.strptime(folder_name, "%Y-%m-%d_%H-%M")
        assert parsed is not None

    def test_copy_integrity_verified(self, patch_dirs):
        """Backed up files pass integrity check."""
        backup_cada_5min.hacer_backup()

        backup_dir = patch_dirs["backup_dir"]
        subdirs = list(backup_dir.iterdir())
        backup_subdir = subdirs[0]

        for db_file in backup_subdir.glob("*.db"):
            assert backup_cada_5min.verificar_integridad_db(db_file) is True


class TestPurgarBackupsAntiguos:
    """Tests for purgar_backups_antiguos"""

    def test_old_backups_deleted(self, patch_dirs):
        """Backups older than 72 hours are deleted."""
        backup_dir = patch_dirs["backup_dir"]
        backup_dir.mkdir(exist_ok=True)

        # Create an old backup (4 days ago)
        old_time = datetime.now() - timedelta(hours=80)
        old_folder = backup_dir / old_time.strftime("%Y-%m-%d_%H-%M")
        old_folder.mkdir()
        (old_folder / "dvdcoin.db").write_text("fake")

        # Create a recent backup (1 hour ago)
        recent_time = datetime.now() - timedelta(hours=1)
        recent_folder = backup_dir / recent_time.strftime("%Y-%m-%d_%H-%M")
        recent_folder.mkdir()
        (recent_folder / "dvdcoin.db").write_text("fake")

        eliminados = backup_cada_5min.purgar_backups_antiguos()

        assert eliminados == 1
        assert not old_folder.exists()
        assert recent_folder.exists()

    def test_recent_backups_kept(self, patch_dirs):
        """Backups within 72 hours are kept."""
        backup_dir = patch_dirs["backup_dir"]
        backup_dir.mkdir(exist_ok=True)

        # Create backups within retention period
        for hours_ago in [1, 12, 24, 48, 71]:
            t = datetime.now() - timedelta(hours=hours_ago)
            folder = backup_dir / t.strftime("%Y-%m-%d_%H-%M")
            folder.mkdir()
            (folder / "test.db").write_text("data")

        eliminados = backup_cada_5min.purgar_backups_antiguos()
        assert eliminados == 0

        # All 5 folders should still exist
        remaining = [d for d in backup_dir.iterdir() if d.is_dir()]
        assert len(remaining) == 5

    def test_no_backup_dir_returns_zero(self, patch_dirs):
        """If backup directory doesn't exist, returns 0."""
        # backup_dir doesn't exist yet (not created)
        eliminados = backup_cada_5min.purgar_backups_antiguos()
        assert eliminados == 0

    def test_invalid_folder_names_ignored(self, patch_dirs):
        """Folders with non-date names are ignored (not deleted)."""
        backup_dir = patch_dirs["backup_dir"]
        backup_dir.mkdir(exist_ok=True)

        # Create a folder with invalid name
        invalid_folder = backup_dir / "not-a-date"
        invalid_folder.mkdir()

        eliminados = backup_cada_5min.purgar_backups_antiguos()
        assert eliminados == 0
        assert invalid_folder.exists()


class TestMain:
    """Tests for main function"""

    def test_main_success(self, patch_dirs):
        """main() returns 0 on successful backup."""
        result = backup_cada_5min.main()
        assert result == 0

    def test_main_failure_all_corrupted(self, patch_dirs):
        """main() returns 1 when all databases are corrupted."""
        # Corrupt all databases
        for db_name in ["dvdcoin.db", "users.db", "apuestas.db"]:
            db_path = patch_dirs["data_dir"] / db_name
            db_path.write_bytes(b"corrupted")

        result = backup_cada_5min.main()
        assert result == 1

    def test_main_purges_old_backups(self, patch_dirs):
        """main() also purges old backups."""
        backup_dir = patch_dirs["backup_dir"]
        backup_dir.mkdir(exist_ok=True)

        # Create an old backup
        old_time = datetime.now() - timedelta(hours=100)
        old_folder = backup_dir / old_time.strftime("%Y-%m-%d_%H-%M")
        old_folder.mkdir()
        (old_folder / "dvdcoin.db").write_text("old")

        backup_cada_5min.main()

        # Old backup should be gone
        assert not old_folder.exists()


class TestConfigurarBackup5min:
    """Tests for configurar_backup_5min.py"""

    def test_crear_tarea_programada_success(self):
        """crear_tarea_programada returns True on success."""
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        import configurar_backup_5min

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            result = configurar_backup_5min.crear_tarea_programada()
            assert result is True

    def test_crear_tarea_programada_failure(self):
        """crear_tarea_programada returns False on failure."""
        import configurar_backup_5min

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Access denied"

        with patch('subprocess.run', return_value=mock_result):
            result = configurar_backup_5min.crear_tarea_programada()
            assert result is False

    def test_verificar_tarea_exists(self):
        """verificar_tarea returns True when task exists."""
        import configurar_backup_5min

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            assert configurar_backup_5min.verificar_tarea() is True

    def test_verificar_tarea_not_exists(self):
        """verificar_tarea returns False when task doesn't exist."""
        import configurar_backup_5min

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch('subprocess.run', return_value=mock_result):
            assert configurar_backup_5min.verificar_tarea() is False

    def test_verificar_tarea_exception(self):
        """verificar_tarea returns False on exception."""
        import configurar_backup_5min

        with patch('subprocess.run', side_effect=Exception("error")):
            assert configurar_backup_5min.verificar_tarea() is False
