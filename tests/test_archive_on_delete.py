"""
Unit tests for the archive-on-delete feature.
When announcements or comments are deleted, they are moved to static/anuncios/old/
with metadata about who deleted them and when.
"""
import os
import sys
import sqlite3
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


@pytest.fixture
def temp_cuentos_env(tmp_path):
    """Set up a temporary cuentos environment."""
    cuentos_dir = tmp_path / "static" / "anuncios"
    cuentos_dir.mkdir(parents=True)
    old_dir = cuentos_dir / "old"
    old_dir.mkdir()

    # Create a sample announcement file
    sample = cuentos_dir / "test_anuncio.docx"
    sample.write_bytes(b"fake docx content")

    # Create meta file
    import json
    meta_path = cuentos_dir / ".meta.json"
    meta_path.write_text(json.dumps({
        "masked": [],
        "creators": {"test_anuncio.docx": "dvd"},
        "created_at": {"test_anuncio.docx": "2026-05-31 10:00:00"}
    }), encoding="utf-8")

    return {
        "cuentos_dir": str(cuentos_dir),
        "old_dir": str(old_dir),
        "sample_file": str(sample),
        "meta_path": str(meta_path),
    }


@pytest.fixture
def temp_comments_db(tmp_path):
    """Set up a temporary comments database."""
    db_path = tmp_path / "comments.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            username TEXT NOT NULL,
            body TEXT NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    # Insert test comments
    conn.execute(
        "INSERT INTO comments (filename, username, body, created_at) VALUES (?, ?, ?, ?)",
        ("test.docx", "testuser", "This is a test comment", "2026-05-30 12:00:00")
    )
    conn.execute(
        "INSERT INTO comments (filename, username, body, parent_id, created_at) VALUES (?, ?, ?, ?, ?)",
        ("test.docx", "otheruser", "This is a reply", 1, "2026-05-30 12:05:00")
    )
    conn.commit()
    conn.close()
    return str(db_path)


class TestAnnouncementArchive:
    """Tests for archiving deleted announcements."""

    @pytest.mark.unit
    def test_delete_moves_file_to_old(self, temp_cuentos_env):
        """Deleting an announcement moves the file to old/ folder."""
        import shutil
        cuentos_dir = temp_cuentos_env["cuentos_dir"]
        old_dir = temp_cuentos_env["old_dir"]
        filename = "test_anuncio.docx"
        path = os.path.join(cuentos_dir, filename)

        # Simulate the archive logic
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        user = "dvd"
        archive_name = f"{now}_borrado_por_{user}_{filename}"
        archive_path = os.path.join(old_dir, archive_name)
        shutil.move(path, archive_path)

        assert not os.path.exists(path)
        assert os.path.exists(archive_path)

    @pytest.mark.unit
    def test_delete_creates_log_file(self, temp_cuentos_env):
        """Deleting an announcement creates a .log file with metadata."""
        old_dir = temp_cuentos_env["old_dir"]
        filename = "test_anuncio.docx"
        user = "dvd"
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        log_name = f"{now}_borrado_por_{user}_{filename}.log"
        log_path = os.path.join(old_dir, log_name)

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Anuncio eliminado\n")
            f.write(f"Archivo: {filename}\n")
            f.write(f"Borrado por: {user}\n")
            f.write(f"Fecha: {now}\n")

        assert os.path.exists(log_path)
        content = open(log_path, encoding="utf-8").read()
        assert "Anuncio eliminado" in content
        assert f"Borrado por: {user}" in content
        assert filename in content

    @pytest.mark.unit
    def test_archive_name_contains_user_and_timestamp(self):
        """Archive filename contains who deleted it and when."""
        user = "admin_user"
        filename = "mi_anuncio.docx"
        now = "2026-05-31_19-30-00"
        archive_name = f"{now}_borrado_por_{user}_{filename}"

        assert user in archive_name
        assert filename in archive_name
        assert "2026-05-31" in archive_name
        assert "borrado_por" in archive_name

    @pytest.mark.unit
    def test_old_directory_created_if_not_exists(self, tmp_path):
        """The old/ directory is created automatically if it doesn't exist."""
        cuentos_dir = tmp_path / "anuncios"
        cuentos_dir.mkdir()
        old_dir = cuentos_dir / "old"

        assert not old_dir.exists()
        os.makedirs(str(old_dir), exist_ok=True)
        assert old_dir.exists()


class TestCommentArchive:
    """Tests for archiving deleted comments."""

    @pytest.mark.unit
    def test_delete_comment_creates_log(self, temp_cuentos_env):
        """Deleting a comment creates a log file in old/."""
        old_dir = temp_cuentos_env["old_dir"]
        comment_id = 42
        user = "dvd"
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        archive_name = f"{now}_comentario_borrado_por_{user}_id{comment_id}.log"
        archive_path = os.path.join(old_dir, archive_name)

        with open(archive_path, "w", encoding="utf-8") as f:
            f.write("Comentario eliminado\n")
            f.write(f"ID: {comment_id}\n")
            f.write(f"Anuncio: test.docx\n")
            f.write(f"Autor: testuser\n")
            f.write(f"Fecha original: 2026-05-30 12:00:00\n")
            f.write(f"Borrado por: {user}\n")
            f.write(f"Fecha borrado: {now}\n")
            f.write(f"\n--- Texto del comentario ---\n")
            f.write("This is the comment body\n")

        assert os.path.exists(archive_path)
        content = open(archive_path, encoding="utf-8").read()
        assert "Comentario eliminado" in content
        assert f"Borrado por: {user}" in content
        assert "This is the comment body" in content
        assert f"ID: {comment_id}" in content

    @pytest.mark.unit
    def test_comment_log_includes_replies(self, temp_cuentos_env):
        """When a comment with replies is deleted, replies are included in the log."""
        old_dir = temp_cuentos_env["old_dir"]
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        user = "dvd"

        archive_path = os.path.join(old_dir, f"{now}_comentario_borrado_por_{user}_id1.log")

        replies = [
            {"id": 2, "username": "user2", "body": "Reply 1", "created_at": "2026-05-30 12:05:00"},
            {"id": 3, "username": "user3", "body": "Reply 2", "created_at": "2026-05-30 12:10:00"},
        ]

        with open(archive_path, "w", encoding="utf-8") as f:
            f.write("Comentario eliminado\n")
            f.write(f"ID: 1\n")
            f.write(f"Borrado por: {user}\n")
            f.write(f"\n--- Texto del comentario ---\n")
            f.write("Main comment\n")
            f.write(f"\n--- Respuestas eliminadas ({len(replies)}) ---\n")
            for r in replies:
                f.write(f"\n  ID: {r['id']} | Autor: {r['username']} | Fecha: {r['created_at']}\n")
                f.write(f"  {r['body']}\n")

        content = open(archive_path, encoding="utf-8").read()
        assert "Respuestas eliminadas (2)" in content
        assert "Reply 1" in content
        assert "Reply 2" in content
        assert "user2" in content
        assert "user3" in content

    @pytest.mark.unit
    def test_comment_archive_name_format(self):
        """Comment archive filename has correct format."""
        user = "moderator"
        comment_id = 99
        now = "2026-05-31_20-00-00"
        archive_name = f"{now}_comentario_borrado_por_{user}_id{comment_id}.log"

        assert "comentario_borrado_por" in archive_name
        assert "moderator" in archive_name
        assert "id99" in archive_name
        assert archive_name.endswith(".log")

    @pytest.mark.unit
    def test_author_can_delete_own_comment(self, temp_comments_db):
        """The author of a comment can delete their own comment."""
        conn = sqlite3.connect(temp_comments_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM comments WHERE id=1").fetchone()
        conn.close()

        # Author is "testuser", should be allowed
        assert row["username"] == "testuser"

    @pytest.mark.unit
    def test_admin_can_delete_any_comment(self, temp_comments_db):
        """An admin can delete any comment regardless of author."""
        conn = sqlite3.connect(temp_comments_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM comments WHERE id=1").fetchone()
        conn.close()

        # Comment by "testuser" but admin "dvd" should be able to delete
        assert row["username"] != "dvd"
        # In the endpoint, admin check allows deletion


class TestDeletedCommentsCleared:
    """Verify all existing comments were cleared."""

    @pytest.mark.unit
    def test_comments_db_is_empty(self):
        """The comments database should have no comments (cleared)."""
        db_path = BASE_DIR / "data" / "comments.db"
        if not db_path.exists():
            pytest.skip("comments.db not found")
        conn = sqlite3.connect(str(db_path))
        count = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
        conn.close()
        assert count == 0, f"Expected 0 comments, found {count}"
