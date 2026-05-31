"""
Unit tests for the Exams Anuncios (Announcements) system.

Tests cover:
- Database schema creation
- API endpoints exist in app_exams.py
- Permission logic (creator + admin can delete)
- Frontend page has required elements
- File upload and write endpoints
- Comments system
- Archive on delete (old/ folder)

Run:
    python -m pytest tests/test_exams_anuncios.py -v --no-cov
"""
import json
import os
import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent
EXAMS_DIR = BASE_DIR / "modules" / "exams"
APP_FILE = EXAMS_DIR / "app_exams.py"
ANUNCIOS_HTML = EXAMS_DIR / "anuncios" / "anuncios.html"


class TestExamsAnunciosEndpoints:
    """Test that all anuncios API endpoints exist in app_exams.py."""

    @pytest.fixture(autouse=True)
    def load_app(self):
        self.content = APP_FILE.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_list_endpoint_exists(self):
        """GET /api/anuncios endpoint must exist."""
        assert '@app.get("/api/anuncios")' in self.content

    @pytest.mark.unit
    def test_upload_endpoint_exists(self):
        """POST /api/anuncios/upload endpoint must exist."""
        assert '@app.post("/api/anuncios/upload")' in self.content

    @pytest.mark.unit
    def test_write_endpoint_exists(self):
        """POST /api/anuncios/write endpoint must exist."""
        assert '@app.post("/api/anuncios/write")' in self.content

    @pytest.mark.unit
    def test_delete_endpoint_exists(self):
        """DELETE /api/anuncios/{id} endpoint must exist."""
        assert '@app.delete("/api/anuncios/{anuncio_id}")' in self.content

    @pytest.mark.unit
    def test_get_comments_endpoint_exists(self):
        """GET /api/anuncios/{id}/comments endpoint must exist."""
        assert '@app.get("/api/anuncios/{anuncio_id}/comments")' in self.content

    @pytest.mark.unit
    def test_post_comment_endpoint_exists(self):
        """POST /api/anuncios/{id}/comments endpoint must exist."""
        assert '@app.post("/api/anuncios/{anuncio_id}/comments")' in self.content

    @pytest.mark.unit
    def test_delete_comment_endpoint_exists(self):
        """DELETE /api/anuncios/comments/{id} endpoint must exist."""
        assert '@app.delete("/api/anuncios/comments/{comment_id}")' in self.content

    @pytest.mark.unit
    def test_page_route_exists(self):
        """GET /anuncios page route must exist."""
        assert '@app.get("/anuncios")' in self.content


class TestExamsAnunciosDatabase:
    """Test the anuncios database schema."""

    @pytest.fixture(autouse=True)
    def load_app(self):
        self.content = APP_FILE.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_anuncios_table_schema(self):
        """Schema must define anuncios table with required columns."""
        assert "CREATE TABLE IF NOT EXISTS anuncios" in self.content
        assert "title TEXT NOT NULL" in self.content
        assert "body TEXT" in self.content
        assert "creator TEXT NOT NULL" in self.content
        assert "created_at TEXT" in self.content
        assert "expires_at TEXT" in self.content
        assert "deleted INTEGER" in self.content
        assert "has_file INTEGER" in self.content
        assert "filename TEXT" in self.content

    @pytest.mark.unit
    def test_comments_table_schema(self):
        """Schema must define anuncios_comments table."""
        assert "CREATE TABLE IF NOT EXISTS anuncios_comments" in self.content
        assert "anuncio_id INTEGER NOT NULL" in self.content
        assert "username TEXT NOT NULL" in self.content
        assert "body TEXT NOT NULL" in self.content

    @pytest.mark.unit
    def test_database_file_path(self):
        """Database must be stored in data/ directory."""
        assert 'DB_ANUNCIOS = os.path.join(DATA_DIR, "anuncios.db")' in self.content

    @pytest.mark.unit
    def test_database_initialized(self):
        """Database must be initialized with create_tables."""
        assert "db_anuncios = DatabaseHelper(DB_ANUNCIOS)" in self.content
        assert "db_anuncios.create_tables(SCHEMA_ANUNCIOS)" in self.content


class TestExamsAnunciosPermissions:
    """Test permission logic for anuncios."""

    @pytest.fixture(autouse=True)
    def load_app(self):
        self.content = APP_FILE.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_creator_can_delete(self):
        """Creator of an anuncio must be able to delete it."""
        assert 'user["username"] == creator' in self.content

    @pytest.mark.unit
    def test_admin_can_delete(self):
        """Admin users must be able to delete any anuncio."""
        assert 'user["username"] in ADMINS' in self.content

    @pytest.mark.unit
    def test_admin_email_can_delete(self):
        """davidcno.ch@gmail.com must be able to delete any anuncio."""
        assert 'ANUNCIOS_ADMIN_EMAIL = "davidcno.ch@gmail.com"' in self.content
        assert 'user["email"] == ANUNCIOS_ADMIN_EMAIL' in self.content

    @pytest.mark.unit
    def test_delete_archives_to_old(self):
        """Deleted anuncios must be moved to old/ folder."""
        # Find the delete endpoint
        del_start = self.content.find('@app.delete("/api/anuncios/{anuncio_id}")')
        assert del_start != -1
        next_dec = self.content.find("\n@app.", del_start + 10)
        del_body = self.content[del_start:next_dec]
        assert "ANUNCIOS_OLD" in del_body or "old" in del_body
        assert "shutil.move" in del_body or "_shutil.move" in del_body

    @pytest.mark.unit
    def test_delete_marks_as_deleted(self):
        """Delete must mark the anuncio as deleted=1 in DB."""
        del_start = self.content.find('@app.delete("/api/anuncios/{anuncio_id}")')
        next_dec = self.content.find("\n@app.", del_start + 10)
        del_body = self.content[del_start:next_dec]
        assert '"deleted": 1' in del_body or "'deleted': 1" in del_body


class TestExamsAnunciosWriteLogic:
    """Test the write endpoint logic."""

    @pytest.fixture(autouse=True)
    def load_app(self):
        self.content = APP_FILE.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_write_validates_empty_title(self):
        """Write endpoint must reject empty title."""
        write_start = self.content.find('@app.post("/api/anuncios/write")')
        next_dec = self.content.find("\n@app.", write_start + 10)
        write_body = self.content[write_start:next_dec]
        assert "título no puede estar vacío" in write_body

    @pytest.mark.unit
    def test_write_validates_empty_body(self):
        """Write endpoint must reject empty body."""
        write_start = self.content.find('@app.post("/api/anuncios/write")')
        next_dec = self.content.find("\n@app.", write_start + 10)
        write_body = self.content[write_start:next_dec]
        assert "contenido no puede estar vacío" in write_body

    @pytest.mark.unit
    def test_write_creates_txt_file(self):
        """Write endpoint must create a .txt file."""
        write_start = self.content.find('@app.post("/api/anuncios/write")')
        next_dec = self.content.find("\n@app.", write_start + 10)
        write_body = self.content[write_start:next_dec]
        assert ".txt" in write_body

    @pytest.mark.unit
    def test_write_stores_in_db(self):
        """Write endpoint must insert into anuncios table."""
        write_start = self.content.find('@app.post("/api/anuncios/write")')
        next_dec = self.content.find("\n@app.", write_start + 10)
        write_body = self.content[write_start:next_dec]
        assert 'db_anuncios.insert("anuncios"' in write_body

    @pytest.mark.unit
    def test_upload_validates_extension(self):
        """Upload endpoint must reject unsupported file types."""
        upload_start = self.content.find('@app.post("/api/anuncios/upload")')
        next_dec = self.content.find("\n@app.", upload_start + 10)
        upload_body = self.content[upload_start:next_dec]
        assert ".docx" in upload_body
        assert ".odt" in upload_body
        assert ".txt" in upload_body


class TestExamsAnunciosFrontend:
    """Test the anuncios HTML page."""

    @pytest.fixture(autouse=True)
    def load_html(self):
        self.content = ANUNCIOS_HTML.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_page_has_login_overlay(self):
        """Page must have a login overlay for authentication."""
        assert 'id="loginOverlay"' in self.content

    @pytest.mark.unit
    def test_page_has_username_field(self):
        """Login must use username (not email) as identity."""
        assert 'id="loginUser"' in self.content
        assert "Nombre de usuario" in self.content

    @pytest.mark.unit
    def test_page_has_publish_tabs(self):
        """Page must have file upload and write text tabs."""
        assert "Subir archivo" in self.content
        assert "Escribir texto" in self.content

    @pytest.mark.unit
    def test_page_has_postit_style(self):
        """Page must use post-it style cards."""
        assert "postit" in self.content
        assert "POSTIT_COLORS" in self.content

    @pytest.mark.unit
    def test_page_has_comments_system(self):
        """Page must have inline comments."""
        assert "toggleComments" in self.content
        assert "postComment" in self.content
        assert "deleteComment" in self.content

    @pytest.mark.unit
    def test_page_shows_creator_and_date(self):
        """Post-it cards must show creator username and date."""
        assert "a.creator" in self.content
        assert "a.created_at" in self.content

    @pytest.mark.unit
    def test_page_has_delete_button(self):
        """Page must have delete button for authorized users."""
        assert "deleteAnuncio" in self.content
        assert "canDelete" in self.content or "can_delete" in self.content

    @pytest.mark.unit
    def test_page_calls_correct_api(self):
        """Page must call /api/anuncios endpoints."""
        assert "/api/anuncios" in self.content
        assert "/api/anuncios/upload" in self.content
        assert "/api/anuncios/write" in self.content

    @pytest.mark.unit
    def test_page_uses_exams_auth(self):
        """Page must use exams auth system (exams_token)."""
        assert "exams_token" in self.content
        assert "/api/auth/login" in self.content
        assert "/api/auth/me" in self.content

    @pytest.mark.unit
    def test_page_never_shows_email(self):
        """Page must never display user email, only username."""
        # The page should show username from /api/auth/me, not email
        assert "d.user.username" in self.content
        # Should not display email field
        assert 'type="email"' not in self.content

    @pytest.mark.unit
    def test_page_has_expiry_date(self):
        """Page must have optional expiry date field."""
        assert 'id="expiryDate"' in self.content

    @pytest.mark.unit
    def test_page_has_register_link(self):
        """Page must link to registration for new users."""
        assert "Regístrate" in self.content or "register" in self.content


class TestExamsAnunciosDirectories:
    """Test that required directories exist."""

    @pytest.mark.unit
    def test_anuncios_dir_exists(self):
        """modules/exams/anuncios/ directory must exist."""
        assert (EXAMS_DIR / "anuncios").is_dir()

    @pytest.mark.unit
    def test_uploads_dir_exists(self):
        """modules/exams/anuncios/uploads/ directory must exist."""
        assert (EXAMS_DIR / "anuncios" / "uploads").is_dir()

    @pytest.mark.unit
    def test_old_dir_exists(self):
        """modules/exams/anuncios/old/ directory must exist."""
        assert (EXAMS_DIR / "anuncios" / "old").is_dir()

    @pytest.mark.unit
    def test_html_page_exists(self):
        """modules/exams/anuncios/anuncios.html must exist."""
        assert ANUNCIOS_HTML.is_file()


class TestExamsAnunciosHubLink:
    """Test that the hub page links to anuncios."""

    @pytest.mark.unit
    def test_hub_links_to_anuncios(self):
        """Hub page must link to /anuncios (not external URL)."""
        hub_path = EXAMS_DIR / "static" / "hub.html"
        content = hub_path.read_text(encoding="utf-8")
        assert 'href="/anuncios"' in content
        # Must NOT link to external dvta.ch for anuncios
        assert 'href="https://dvta.ch" target="_blank"' not in content or "Anuncios" not in content.split('href="https://dvta.ch"')[0][-100:]


pytestmark = [pytest.mark.unit]
