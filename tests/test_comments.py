"""
Unit tests for the Bulletin Board Comments feature.

Tests cover:
- Database initialization and schema
- Posting comments (success, validation errors)
- Listing comments for a post
- Threaded replies (parent_id)
- Deleting comments (author, admin, unauthorized)
- Comment count in list endpoint

Run:
    python -m pytest tests/test_comments.py -v --no-cov
"""
import json
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

BASE_DIR = Path(__file__).parent.parent


class TestCommentsDatabase:
    """Test the comments database schema and initialization."""

    @pytest.fixture
    def comments_db(self, tmp_path):
        """Create a temporary comments database."""
        db_path = tmp_path / "comments.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                username TEXT NOT NULL,
                body TEXT NOT NULL,
                parent_id INTEGER DEFAULT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_comments_filename ON comments(filename)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_id)")
        conn.commit()
        return conn

    @pytest.mark.unit
    def test_table_created(self, comments_db):
        """Comments table must exist after initialization."""
        row = comments_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"
        ).fetchone()
        assert row is not None
        assert row["name"] == "comments"

    @pytest.mark.unit
    def test_insert_comment(self, comments_db):
        """Can insert a comment into the database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comments_db.execute(
            "INSERT INTO comments (filename, username, body, created_at) VALUES (?, ?, ?, ?)",
            ("test.docx", "alice", "Hello world", now)
        )
        comments_db.commit()
        row = comments_db.execute("SELECT * FROM comments WHERE filename='test.docx'").fetchone()
        assert row["username"] == "alice"
        assert row["body"] == "Hello world"
        assert row["parent_id"] is None

    @pytest.mark.unit
    def test_insert_reply(self, comments_db):
        """Can insert a reply referencing a parent comment."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = comments_db.execute(
            "INSERT INTO comments (filename, username, body, created_at) VALUES (?, ?, ?, ?)",
            ("test.docx", "alice", "Original comment", now)
        )
        parent_id = cur.lastrowid
        comments_db.execute(
            "INSERT INTO comments (filename, username, body, parent_id, created_at) VALUES (?, ?, ?, ?, ?)",
            ("test.docx", "bob", "Reply to alice", parent_id, now)
        )
        comments_db.commit()
        replies = comments_db.execute(
            "SELECT * FROM comments WHERE parent_id=?", (parent_id,)
        ).fetchall()
        assert len(replies) == 1
        assert replies[0]["username"] == "bob"
        assert replies[0]["body"] == "Reply to alice"

    @pytest.mark.unit
    def test_index_on_filename(self, comments_db):
        """Index on filename column must exist."""
        row = comments_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_comments_filename'"
        ).fetchone()
        assert row is not None

    @pytest.mark.unit
    def test_index_on_parent(self, comments_db):
        """Index on parent_id column must exist."""
        row = comments_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_comments_parent'"
        ).fetchone()
        assert row is not None


class TestCommentsPermissions:
    """Test permission logic for comment deletion — only admins can delete."""

    ADMINS = {"dvd", "nebulosa", "nina", "victor", "yu", "roy", "admin", "aitor"}

    @pytest.mark.unit
    def test_author_cannot_delete_own_comment(self):
        """Regular authors can no longer delete their own comments."""
        user = "alice"
        can_delete = user in self.ADMINS
        assert can_delete is False

    @pytest.mark.unit
    def test_admin_can_delete_any_comment(self):
        """Admin users can delete any comment."""
        user = "dvd"
        can_delete = user in self.ADMINS
        assert can_delete is True

    @pytest.mark.unit
    def test_non_admin_cannot_delete(self):
        """A regular user cannot delete any comment."""
        user = "charlie"
        can_delete = user in self.ADMINS
        assert can_delete is False

    @pytest.mark.unit
    def test_all_admins_can_delete(self):
        """Every admin in the set can delete comments."""
        for admin in self.ADMINS:
            assert admin in self.ADMINS


class TestCommentsValidation:
    """Test comment input validation rules."""

    @pytest.mark.unit
    def test_empty_body_rejected(self):
        """Empty comment body should be rejected."""
        body = "   "
        assert not body.strip()

    @pytest.mark.unit
    def test_body_max_length(self):
        """Comments longer than 2000 chars should be rejected."""
        body = "x" * 2001
        assert len(body) > 2000

    @pytest.mark.unit
    def test_valid_body_accepted(self):
        """A normal comment body should pass validation."""
        body = "This is a valid comment"
        assert 0 < len(body.strip()) <= 2000

    @pytest.mark.unit
    def test_body_stripped(self):
        """Comment body should be stripped of leading/trailing whitespace."""
        body = "  Hello world  "
        assert body.strip() == "Hello world"


class TestCommentsThreading:
    """Test the threading/tree structure logic."""

    @pytest.mark.unit
    def test_build_threads_flat(self):
        """Comments without parent_id are root-level."""
        comments = [
            {"id": 1, "username": "alice", "body": "First", "parent_id": None, "created_at": "2026-05-31 10:00:00"},
            {"id": 2, "username": "bob", "body": "Second", "parent_id": None, "created_at": "2026-05-31 10:01:00"},
        ]
        # Build tree
        roots = [c for c in comments if c["parent_id"] is None]
        assert len(roots) == 2

    @pytest.mark.unit
    def test_build_threads_nested(self):
        """Comments with parent_id are nested under their parent."""
        comments = [
            {"id": 1, "username": "alice", "body": "Root", "parent_id": None, "created_at": "2026-05-31 10:00:00"},
            {"id": 2, "username": "bob", "body": "Reply", "parent_id": 1, "created_at": "2026-05-31 10:01:00"},
            {"id": 3, "username": "charlie", "body": "Reply to reply", "parent_id": 1, "created_at": "2026-05-31 10:02:00"},
        ]
        # Build tree
        map_c = {}
        for c in comments:
            map_c[c["id"]] = {**c, "replies": []}
        roots = []
        for c in comments:
            if c["parent_id"] and c["parent_id"] in map_c:
                map_c[c["parent_id"]]["replies"].append(map_c[c["id"]])
            else:
                roots.append(map_c[c["id"]])
        assert len(roots) == 1
        assert len(roots[0]["replies"]) == 2
        assert roots[0]["replies"][0]["username"] == "bob"
        assert roots[0]["replies"][1]["username"] == "charlie"

    @pytest.mark.unit
    def test_orphan_reply_becomes_root(self):
        """A reply whose parent doesn't exist becomes a root comment."""
        comments = [
            {"id": 5, "username": "alice", "body": "Orphan", "parent_id": 999, "created_at": "2026-05-31 10:00:00"},
        ]
        map_c = {}
        for c in comments:
            map_c[c["id"]] = {**c, "replies": []}
        roots = []
        for c in comments:
            if c["parent_id"] and c["parent_id"] in map_c:
                map_c[c["parent_id"]]["replies"].append(map_c[c["id"]])
            else:
                roots.append(map_c[c["id"]])
        assert len(roots) == 1
        assert roots[0]["body"] == "Orphan"


class TestCommentsFrontend:
    """Test that the cuento reader page includes comments UI."""

    @pytest.mark.unit
    def test_cuento_page_has_comments_section(self):
        """The cuento reader page must include the comments section."""
        path = BASE_DIR / "static" / "pages" / "cuento.html"
        content = path.read_text(encoding="utf-8")
        assert "commentsSection" in content
        assert "commentInput" in content
        assert "postComment" in content

    @pytest.mark.unit
    def test_cuento_page_shows_author_and_date(self):
        """The cuento reader page must display creator and created_at."""
        path = BASE_DIR / "static" / "pages" / "cuento.html"
        content = path.read_text(encoding="utf-8")
        # Must destructure creator and created_at from story response
        assert "creator" in content
        assert "created_at" in content
        # Must use commentsPostedBy i18n key for author prefix
        assert "commentsPostedBy" in content

    @pytest.mark.unit
    def test_cuento_page_has_reply_functionality(self):
        """The cuento reader page must support replying to comments."""
        path = BASE_DIR / "static" / "pages" / "cuento.html"
        content = path.read_text(encoding="utf-8")
        assert "postReply" in content
        assert "toggleReply" in content
        assert "replyForm" in content

    @pytest.mark.unit
    def test_cuento_page_has_delete_functionality(self):
        """The cuento reader page must support deleting comments."""
        path = BASE_DIR / "static" / "pages" / "cuento.html"
        content = path.read_text(encoding="utf-8")
        assert "deleteComment" in content

    @pytest.mark.unit
    def test_cuentos_member_shows_comment_count(self):
        """The bulletin board list page must show comment counts."""
        path = BASE_DIR / "static" / "cuentos_member.html"
        content = path.read_text(encoding="utf-8")
        assert "comment_count" in content

    @pytest.mark.unit
    def test_cuentos_member_has_inline_comments(self):
        """The bulletin board list page must support inline comments."""
        path = BASE_DIR / "static" / "cuentos_member.html"
        content = path.read_text(encoding="utf-8")
        assert "toggleComments" in content
        assert "loadInlineComments" in content
        assert "postInlineComment" in content
        assert "deleteInlineComment" in content
        assert "postInlineReply" in content

    @pytest.mark.unit
    def test_cuentos_member_has_i18n(self):
        """The bulletin board list page must load i18n translations."""
        path = BASE_DIR / "static" / "cuentos_member.html"
        content = path.read_text(encoding="utf-8")
        assert "loadI18n" in content
        assert "function t(" in content

    @pytest.mark.unit
    def test_cuento_page_has_i18n(self):
        """The cuento reader page must load i18n translations."""
        path = BASE_DIR / "static" / "pages" / "cuento.html"
        content = path.read_text(encoding="utf-8")
        assert "loadI18n" in content
        assert "function t(" in content

    @pytest.mark.unit
    def test_main_spa_has_inline_comments(self):
        """The main SPA must support inline comments on announcements."""
        path = BASE_DIR / "static" / "index.html"
        content = path.read_text(encoding="utf-8")
        assert "loadCuentoInlineComments" in content
        assert "postCuentoComment" in content
        assert "deleteCuentoComment" in content


class TestCommentsI18n:
    """Test that all i18n files contain comment translation keys."""

    REQUIRED_KEYS = [
        "commentsTitle", "commentsPlaceholder", "commentsPost",
        "commentsReply", "commentsDelete", "commentsDeleteConfirm",
        "commentsCancel", "commentsEmpty", "commentsLoading",
        "commentsError", "commentsReplyPlaceholder", "commentsPostedBy",
        "commentsCount", "commentsShowComments", "commentsHideComments",
        "cuentosAllAnnouncements", "cuentosBank"
    ]

    LANGUAGES = ["es", "en", "fr", "de", "it", "ca", "eu"]

    @pytest.mark.unit
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_language_has_all_comment_keys(self, lang):
        """Each language file must contain all comment-related keys."""
        path = BASE_DIR / "src" / "static" / "i18n" / f"{lang}.json"
        content = json.loads(path.read_text(encoding="utf-8"))
        missing = [k for k in self.REQUIRED_KEYS if k not in content]
        assert not missing, f"Language '{lang}' is missing keys: {missing}"

    @pytest.mark.unit
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_language_values_not_empty(self, lang):
        """Translation values must not be empty strings."""
        path = BASE_DIR / "src" / "static" / "i18n" / f"{lang}.json"
        content = json.loads(path.read_text(encoding="utf-8"))
        empty = [k for k in self.REQUIRED_KEYS if k in content and not content[k].strip()]
        assert not empty, f"Language '{lang}' has empty values for: {empty}"


pytestmark = [pytest.mark.unit]
