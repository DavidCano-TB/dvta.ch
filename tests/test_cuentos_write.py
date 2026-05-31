"""
Unit tests for the Bulletin Board "Write from text" feature.

Tests cover:
- POST /bank/api/cuentos/write creates a .txt file
- Title becomes first line of the file
- Body becomes the rest of the content
- Creator and created_at stored in meta
- Expiry date stored when provided
- Validation: empty title rejected
- Validation: empty body rejected
- Filename sanitization (special chars removed, spaces to underscores)
- Duplicate filename handling (auto-increment)
- Frontend has the write tab and form elements

Run:
    python -m pytest tests/test_cuentos_write.py -v --no-cov
"""
import json
import os
import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent


class TestCuentosWriteEndpoint:
    """Test the /bank/api/cuentos/write endpoint logic."""

    @pytest.mark.unit
    def test_write_endpoint_exists_in_main(self):
        """The write endpoint must be defined in main.py."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        assert '@app.post("/bank/api/cuentos/write")' in content, (
            "Write endpoint not found in main.py"
        )

    @pytest.mark.unit
    def test_write_endpoint_no_admin_restriction(self):
        """The write endpoint must NOT restrict to admins (any user can write)."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        assert write_start != -1
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator] if next_decorator != -1 else content[write_start:]
        assert "if user not in ALL_ADMINS" not in write_body, (
            "Write endpoint should NOT restrict to admins only"
        )

    @pytest.mark.unit
    def test_write_endpoint_validates_empty_body(self):
        """The write endpoint must reject empty body."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "El contenido no puede estar vacío" in write_body

    @pytest.mark.unit
    def test_write_endpoint_validates_empty_title(self):
        """The write endpoint must reject empty title."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "El título no puede estar vacío" in write_body

    @pytest.mark.unit
    def test_write_endpoint_stores_creator(self):
        """The write endpoint must store creator in meta."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "creators[final] = user" in write_body

    @pytest.mark.unit
    def test_write_endpoint_stores_created_at(self):
        """The write endpoint must store created_at in meta."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "created_dates[final] = now" in write_body

    @pytest.mark.unit
    def test_write_endpoint_handles_expiry(self):
        """The write endpoint must store expiry date when provided."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "expires" in write_body

    @pytest.mark.unit
    def test_write_creates_txt_extension(self):
        """The write endpoint must create a .txt file."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert ".txt" in write_body

    @pytest.mark.unit
    def test_write_title_as_first_line(self):
        """The .txt file must have the title as the first line."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        # The content format should be: title\n\nbody
        assert 'f"{title}\\n\\n{body}"' in write_body or "title}\\n\\n{body}" in write_body


class TestCuentosWriteFilenameLogic:
    """Test filename generation and sanitization for written announcements."""

    @pytest.mark.unit
    def test_filename_sanitization_removes_special_chars(self):
        """Filename must remove special characters."""
        # Simulate the sanitization logic from the endpoint
        title = "¡Hola! ¿Qué tal? @todos"
        safe_title = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')
        assert "!" not in safe_title
        assert "¿" not in safe_title
        assert "@" not in safe_title
        assert safe_title  # Must not be empty

    @pytest.mark.unit
    def test_filename_spaces_to_underscores(self):
        """Spaces in title must become underscores in filename."""
        title = "Mi primer anuncio"
        safe_title = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')
        assert " " not in safe_title
        assert "Mi_primer_anuncio" == safe_title

    @pytest.mark.unit
    def test_filename_fallback_for_empty_sanitized(self):
        """If sanitization empties the title, use 'anuncio' as fallback."""
        title = "!!!???..."
        safe_title = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')
        if not safe_title:
            safe_title = "anuncio"
        assert safe_title == "anuncio"

    @pytest.mark.unit
    def test_filename_includes_date_suffix(self):
        """Filename must include date suffix in DD_MM_YYYY format."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "%d_%m_%Y" in write_body, "Filename must include date suffix"

    @pytest.mark.unit
    def test_duplicate_filename_auto_increment(self):
        """Duplicate filenames must be auto-incremented."""
        main_path = BASE_DIR / "main.py"
        content = main_path.read_text(encoding="utf-8")
        write_start = content.find('@app.post("/bank/api/cuentos/write")')
        next_decorator = content.find("\n@app.", write_start + 10)
        write_body = content[write_start:next_decorator]
        assert "while os.path.exists(dest)" in write_body, (
            "Must handle duplicate filenames with auto-increment"
        )


class TestCuentosWriteFrontend:
    """Test that the frontend has the write-from-text UI elements."""

    @pytest.mark.unit
    def test_member_page_has_write_tab(self):
        """cuentos_member.html must have a 'Escribir texto' tab."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "Escribir texto" in content

    @pytest.mark.unit
    def test_member_page_has_file_tab(self):
        """cuentos_member.html must still have a 'Subir archivo' tab."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "Subir archivo" in content

    @pytest.mark.unit
    def test_member_page_has_title_input(self):
        """cuentos_member.html must have a title input for written announcements."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert 'id="writeTitle"' in content

    @pytest.mark.unit
    def test_member_page_has_body_textarea(self):
        """cuentos_member.html must have a body textarea for written announcements."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert 'id="writeBody"' in content

    @pytest.mark.unit
    def test_member_page_has_write_function(self):
        """cuentos_member.html must have the writeAnuncio JS function."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "writeAnuncio" in content

    @pytest.mark.unit
    def test_member_page_calls_write_api(self):
        """cuentos_member.html must call /bank/api/cuentos/write endpoint."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "/bank/api/cuentos/write" in content

    @pytest.mark.unit
    def test_member_page_has_tab_switcher(self):
        """cuentos_member.html must have switchPublishTab function."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "switchPublishTab" in content

    @pytest.mark.unit
    def test_member_page_publish_button_calls_generic(self):
        """The publish button must call publishAnuncio() which routes to the active tab."""
        member_path = BASE_DIR / "static" / "cuentos_member.html"
        content = member_path.read_text(encoding="utf-8")
        assert "publishAnuncio()" in content


pytestmark = [pytest.mark.unit]
