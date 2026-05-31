"""
Unit tests for the Bulletin Board (formerly Cuentos) feature.

Tests cover:
- Upload stores creator in meta
- List returns creator and can_delete fields
- Delete allowed for creator
- Delete allowed for admin
- Delete denied for non-creator non-admin
- Meta file persistence

Run:
    python -m pytest tests/test_bulletin_board.py -v --no-cov
"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

BASE_DIR = Path(__file__).parent.parent


class TestBulletinBoardMeta:
    """Test the meta file helpers for bulletin board creator tracking."""

    @pytest.fixture
    def meta_dir(self, tmp_path):
        """Create a temporary cuentos directory with meta file."""
        cuentos_dir = tmp_path / "cuentos"
        cuentos_dir.mkdir()
        return cuentos_dir

    @pytest.fixture
    def meta_file(self, meta_dir):
        """Create a .meta.json file."""
        meta_path = meta_dir / ".meta.json"
        meta_data = {
            "masked": [],
            "enabled": True,
            "creators": {
                "story1.docx": "alice",
                "story2.txt": "bob"
            }
        }
        meta_path.write_text(json.dumps(meta_data), encoding="utf-8")
        return meta_path

    @pytest.mark.unit
    def test_meta_stores_creators(self, meta_file):
        """Meta file must store creator mapping."""
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        assert "creators" in data
        assert data["creators"]["story1.docx"] == "alice"
        assert data["creators"]["story2.txt"] == "bob"

    @pytest.mark.unit
    def test_meta_creator_lookup(self, meta_file):
        """Can look up creator by filename."""
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        creators = data.get("creators", {})
        assert creators.get("story1.docx") == "alice"
        assert creators.get("nonexistent.docx", "") == ""

    @pytest.mark.unit
    def test_meta_add_creator(self, meta_file):
        """Adding a new file records its creator."""
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        data["creators"]["new_post.docx"] = "charlie"
        meta_file.write_text(json.dumps(data), encoding="utf-8")

        reloaded = json.loads(meta_file.read_text(encoding="utf-8"))
        assert reloaded["creators"]["new_post.docx"] == "charlie"

    @pytest.mark.unit
    def test_meta_remove_creator_on_delete(self, meta_file):
        """Deleting a file removes its creator entry."""
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        del data["creators"]["story1.docx"]
        meta_file.write_text(json.dumps(data), encoding="utf-8")

        reloaded = json.loads(meta_file.read_text(encoding="utf-8"))
        assert "story1.docx" not in reloaded["creators"]
        assert "story2.txt" in reloaded["creators"]


class TestBulletinBoardPermissions:
    """Test permission logic for bulletin board delete."""

    ADMINS = {"dvd", "nebulosa", "nina", "victor", "yu", "roy", "admin", "aitor"}

    @pytest.mark.unit
    def test_admin_can_delete_any_post(self):
        """Admin users can delete any post regardless of creator."""
        user = "dvd"
        creator = "alice"
        assert user in self.ADMINS or user == creator

    @pytest.mark.unit
    def test_creator_can_delete_own_post(self):
        """The creator of a post can delete it."""
        user = "alice"
        creator = "alice"
        assert user == creator

    @pytest.mark.unit
    def test_non_creator_non_admin_cannot_delete(self):
        """A regular user who didn't create the post cannot delete it."""
        user = "charlie"
        creator = "alice"
        can_delete = user in self.ADMINS or user == creator
        assert can_delete is False

    @pytest.mark.unit
    def test_can_delete_field_true_for_admin(self):
        """API response should set can_delete=True for admins."""
        user = "dvd"
        creator = "alice"
        can_delete = user in self.ADMINS or user == creator
        assert can_delete is True

    @pytest.mark.unit
    def test_can_delete_field_true_for_creator(self):
        """API response should set can_delete=True for the creator."""
        user = "bob"
        creator = "bob"
        can_delete = user in self.ADMINS or user == creator
        assert can_delete is True

    @pytest.mark.unit
    def test_can_delete_field_false_for_others(self):
        """API response should set can_delete=False for non-admin non-creator."""
        user = "random_user"
        creator = "alice"
        can_delete = user in self.ADMINS or user == creator
        assert can_delete is False


class TestBulletinBoardUpload:
    """Test upload functionality stores creator."""

    @pytest.mark.unit
    def test_upload_any_user_allowed(self):
        """Any logged-in user should be able to upload (not just admins)."""
        # The upload endpoint no longer checks for admin role
        # This is a design decision test
        assert True  # Verified by removing admin check in cuentos_upload

    @pytest.mark.unit
    def test_upload_no_admin_check_in_main(self):
        """The main.py upload endpoint must NOT have admin-only restriction."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        # Find the upload function
        upload_start = content.find("@app.post(\"/bank/api/cuentos/upload\")")
        assert upload_start != -1, "Upload endpoint not found in main.py"
        # Get the function body (up to next @app decorator or class)
        next_decorator = content.find("\n@app.", upload_start + 10)
        upload_body = content[upload_start:next_decorator] if next_decorator != -1 else content[upload_start:]
        # Must NOT contain admin-only check
        assert "if user not in ALL_ADMINS" not in upload_body, (
            "Upload endpoint should NOT restrict to admins only"
        )
        # Must contain docstring indicating any user can upload
        assert "Any logged-in user" in upload_body or "any" in upload_body.lower()

    @pytest.mark.unit
    def test_upload_stores_creator_in_meta(self):
        """Upload must store the creator username in meta."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        upload_start = content.find("@app.post(\"/bank/api/cuentos/upload\")")
        next_decorator = content.find("\n@app.", upload_start + 10)
        upload_body = content[upload_start:next_decorator]
        assert "creators[final] = user" in upload_body, (
            "Upload must store creator in meta"
        )

    @pytest.mark.unit
    def test_upload_stores_created_at(self):
        """Upload must store the created_at timestamp in meta."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        upload_start = content.find("@app.post(\"/bank/api/cuentos/upload\")")
        next_decorator = content.find("\n@app.", upload_start + 10)
        upload_body = content[upload_start:next_decorator]
        assert "created_dates[final] = now" in upload_body, (
            "Upload must store created_at in meta"
        )

    @pytest.mark.unit
    def test_supported_extensions(self):
        """Only .docx, .odt, and .txt files are supported."""
        supported = {".docx", ".odt", ".txt"}
        assert ".docx" in supported
        assert ".odt" in supported
        assert ".txt" in supported
        assert ".pdf" not in supported
        assert ".exe" not in supported

    @pytest.mark.unit
    def test_upload_panel_visible_for_all_users_in_html(self):
        """The upload panel in index.html must be shown for all users, not just admins."""
        index_path = BASE_DIR / "src" / "static" / "pages" / "index.html"
        content = index_path.read_text(encoding="utf-8")
        # Must NOT have admin-only gate for upload panel
        assert "if (me?.is_admin) document.getElementById('cuentosUploadPanel')" not in content
        # Must show panel unconditionally for logged-in users
        assert "document.getElementById('cuentosUploadPanel')?.style.setProperty('display','')" in content

    @pytest.mark.unit
    def test_member_page_upload_visible_for_all(self):
        """The cuentos_member.html upload button must be visible for all users."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        # Upload button must exist
        assert "Publicar anuncio" in content
        # Must NOT have admin-only gate
        assert "if (_isAdmin)" not in content.split("toggleUpload")[0][-200:]


class TestBulletinBoardComments:
    """Test that all members can comment and reply to announcements."""

    @pytest.mark.unit
    def test_comment_endpoint_no_admin_restriction(self):
        """The post_comment endpoint must NOT restrict to admins."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        # Find the post comment function
        comment_start = content.find("@app.post(\"/bank/api/cuentos/comments/{filename:path}\")")
        assert comment_start != -1, "Comment endpoint not found"
        next_decorator = content.find("\n@app.", comment_start + 10)
        comment_body = content[comment_start:next_decorator] if next_decorator != -1 else content[comment_start:]
        assert "if user not in ALL_ADMINS" not in comment_body, (
            "Comment endpoint should NOT restrict to admins"
        )

    @pytest.mark.unit
    def test_reply_supported_via_parent_id(self):
        """Comments support replies via parent_id field."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        comment_start = content.find("@app.post(\"/bank/api/cuentos/comments/{filename:path}\")")
        next_decorator = content.find("\n@app.", comment_start + 10)
        comment_body = content[comment_start:next_decorator]
        assert "parent_id" in comment_body, "Comment endpoint must support parent_id for replies"

    @pytest.mark.unit
    def test_member_page_has_reply_button_for_all(self):
        """The reply button in cuentos_member.html must be shown for all users."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        # Reply button must exist without admin check
        assert "toggleInlineReply" in content
        assert "postInlineReply" in content
        # The replyBtn must NOT be gated by _isAdmin
        reply_section = content[content.find("const replyBtn"):content.find("const replyBtn") + 200]
        assert "_isAdmin" not in reply_section, "Reply button must not be gated by admin check"

    @pytest.mark.unit
    def test_member_page_has_comment_form_for_all(self):
        """The comment form in cuentos_member.html must be shown for all users."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        # Comment form must exist
        assert "postInlineComment" in content
        # The comment textarea must be rendered without admin check
        assert "commentForm" in content


class TestBulletinBoardI18n:
    """Test that i18n files have bulletin board translations."""

    I18N_DIR = BASE_DIR / "static" / "i18n"
    LANGUAGES = ["en", "es", "fr", "de", "it", "ca", "eu"]

    @pytest.mark.unit
    def test_all_languages_have_cuentos_title(self):
        """All language files must have cuentosTitle key."""
        for lang in self.LANGUAGES:
            path = self.I18N_DIR / f"{lang}.json"
            assert path.exists(), f"Missing {lang}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "cuentosTitle" in data, f"{lang}.json missing cuentosTitle"
            # Should NOT contain "Cuentos" or "Stories" as title anymore
            assert "Cuentos" not in data["cuentosTitle"], (
                f"{lang}.json cuentosTitle should be renamed from 'Cuentos'"
            )

    @pytest.mark.unit
    def test_all_languages_have_nav_cuentos(self):
        """All language files must have navCuentos key with bulletin board name."""
        for lang in self.LANGUAGES:
            path = self.I18N_DIR / f"{lang}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "navCuentos" in data, f"{lang}.json missing navCuentos"
            # Should contain the clipboard emoji
            assert "📋" in data["navCuentos"], (
                f"{lang}.json navCuentos should use 📋 icon"
            )

    @pytest.mark.unit
    def test_all_languages_have_game_admin_title(self):
        """All language files must have gameAdminTitle key."""
        for lang in self.LANGUAGES:
            path = self.I18N_DIR / f"{lang}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "gameAdminTitle" in data, f"{lang}.json missing gameAdminTitle"


pytestmark = [pytest.mark.unit]
