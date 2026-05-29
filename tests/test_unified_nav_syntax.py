"""
Regression test: unified-nav.js must not contain invalid JS escape sequences.

Bug: The file had \' (backslash + single-quote) inside single-quoted JS strings,
which is a SyntaxError in JavaScript. This caused the entire script to fail to
parse, which in turn prevented doLogin from being defined, making the login
button completely non-functional.

Error seen in browser console:
  Uncaught SyntaxError: Invalid or unexpected token  unified-nav.js:21
  Uncaught ReferenceError: doLogin is not defined    bank:1327
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent
NAV_JS = BASE_DIR / "static" / "js" / "unified-nav.js"
INDEX_HTML = BASE_DIR / "static" / "index.html"
SW_JS = BASE_DIR / "static" / "sw.js"


class TestUnifiedNavSyntax:
    """unified-nav.js must be valid JavaScript."""

    @pytest.fixture(scope="class")
    def nav_src(self):
        return NAV_JS.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_no_backslash_single_quote(self, nav_src):
        """\\' inside JS strings is a SyntaxError — must not appear in the file."""
        count = nav_src.count("\\'")
        assert count == 0, (
            f"Found {count} occurrences of \\' in unified-nav.js. "
            "Use double-quoted strings or plain single-quoted strings instead."
        )

    @pytest.mark.unit
    def test_no_backslash_double_quote_outside_template(self, nav_src):
        """\\\" is also suspicious outside template literals."""
        # Allow inside template literals (backtick strings) — just flag raw occurrences
        # that are clearly in regular string context
        lines_with_issue = [
            (i + 1, line.rstrip())
            for i, line in enumerate(nav_src.splitlines())
            if '\\"' in line and '`' not in line
        ]
        assert not lines_with_issue, (
            f"Suspicious \\\" found outside template literals:\n" +
            "\n".join(f"  line {ln}: {txt}" for ln, txt in lines_with_issue)
        )

    @pytest.mark.unit
    def test_balanced_braces(self, nav_src):
        """Curly braces must be balanced."""
        opens = nav_src.count("{")
        closes = nav_src.count("}")
        assert opens == closes, f"Unbalanced braces: {{ = {opens}, }} = {closes}"

    @pytest.mark.unit
    def test_balanced_parens(self, nav_src):
        """Parentheses must be balanced."""
        opens = nav_src.count("(")
        closes = nav_src.count(")")
        assert opens == closes, f"Unbalanced parens: ( = {opens}, ) = {closes}"

    @pytest.mark.unit
    def test_iife_wrapper_present(self, nav_src):
        """File must be wrapped in an IIFE to avoid polluting global scope."""
        assert "(function()" in nav_src or "(function (" in nav_src

    @pytest.mark.unit
    def test_exposes_unified_nav_global(self, nav_src):
        """Must expose window.UnifiedNav for other scripts to call."""
        assert "window.UnifiedNav" in nav_src

    @pytest.mark.unit
    def test_nav_config_has_required_sections(self, nav_src):
        """NAV_CONFIG must define common, member, admin, superadmin, dvd sections."""
        for section in ("common", "member", "admin", "superadmin", "dvd"):
            assert section + ":" in nav_src or f'"{section}"' in nav_src, (
                f"NAV_CONFIG missing section: {section}"
            )

    @pytest.mark.unit
    def test_all_hrefs_use_unescaped_quotes(self, nav_src):
        """href values must use plain quotes, not escaped ones."""
        # All href strings should look like href: '/bank/...' not href: \'/bank/...\'
        bad_hrefs = re.findall(r"href:\s*\\'", nav_src)
        assert not bad_hrefs, f"Found {len(bad_hrefs)} escaped href values"


class TestIndexHtmlReferencesNav:
    """index.html must correctly reference unified-nav.js."""

    @pytest.fixture(scope="class")
    def html(self):
        return INDEX_HTML.read_text(encoding="utf-8")

    @pytest.mark.unit
    def test_unified_nav_script_tag_present(self, html):
        """index.html must load unified-nav.js."""
        assert "unified-nav.js" in html

    @pytest.mark.unit
    def test_sw_version_bumped(self, html):
        """SW registration query string must be updated to force cache invalidation."""
        # After the unified-nav.js fix we bumped to v=20260528b
        assert "sw.js?v=" in html
        # Must not still be on the old broken version
        assert "sw.js?v=20260527" not in html


class TestServiceWorkerVersion:
    """sw.js cache name must be current so browsers pick up the fixed nav file."""

    @pytest.mark.unit
    def test_cache_name_is_current(self):
        """Cache name must be v7 or higher (bumped after nav fixes)."""
        sw = SW_JS.read_text(encoding="utf-8")
        assert "v7-" in sw or "v8-" in sw or "v9-" in sw or "v10" in sw, (
            "SW cache name must be v7+ after the nav fix"
        )
