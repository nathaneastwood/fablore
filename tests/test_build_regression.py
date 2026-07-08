"""Regression tests that guard against mdBook upgrade breakage.

Two categories:

  Static checks (fast, no build required)
    Run in < 1 s. Scan source files for patterns that caused breakage
    during the 0.4 → 0.5 upgrade.

  Build checks (slow, require ``mdbook build``)
    Marked ``@pytest.mark.slow``. Run the full build and assert the output
    is clean. Skip with ``pytest -m "not slow"`` for faster local iteration.

To run only slow tests:  pytest -m slow
To skip slow tests:      pytest -m "not slow"
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DATA_DIR = SRC_DIR / "data"
BUILD_DIR = ROOT / "book"
PREPROCESSORS = sorted(DATA_DIR.glob("mdbook_*.py"))


# ===========================================================================
# Static checks
# ===========================================================================


class TestPreprocessorProtocol:
    """The mdBook preprocessor JSON protocol changed in 0.5.3:
    ``book["sections"]`` was renamed to ``book["items"]``.
    Using the old key silently processes 0 chapters."""

    def test_no_preprocessor_uses_old_sections_key(self) -> None:
        """No preprocessor must call book.get('sections') or book['sections']."""
        bad_patterns = [
            'book.get("sections")',
            "book.get('sections')",
            'book["sections"]',
            "book['sections']",
        ]
        violations: list[str] = []
        for f in PREPROCESSORS:
            text = f.read_text()
            for pat in bad_patterns:
                if pat in text:
                    violations.append(f"{f.name}: {pat!r}")
        assert violations == [], (
            "Preprocessors using deprecated book['sections'] key — "
            "must be book['items'] (renamed in mdBook 0.5.3):\n" + "\n".join(violations)
        )

    def test_preprocessors_use_items_key(self) -> None:
        """Each preprocessor that walks the book must use book.get('items')."""
        for f in PREPROCESSORS:
            text = f.read_text()
            if "_walk" in text or "sub_items" in text:
                assert (
                    'book.get("items")' in text or "book.get('items')" in text
                ), f"{f.name} walks chapters but doesn't call book.get('items')"


class TestFontAwesomeIcons:
    """mdBook 0.5.3 converts <i class="..."> elements to inline SVG.
    Using the bare 'fa' FA4 prefix defaults to FA6 'regular' and emits a
    build warning for icons that only exist in solid or brands.
    All preprocessor-generated icons must carry an explicit FA6 prefix."""

    def test_no_preprocessor_generates_bare_fa_prefix(self) -> None:
        """Preprocessors must not emit class=\"fa fa-...\" (FA4 bare prefix)."""
        violations: list[str] = []
        for f in PREPROCESSORS:
            text = f.read_text()
            # Look for string literals that produce the bare FA4 pattern
            matches = re.findall(r'class=\\"fa fa-|class="fa fa-', text)
            if matches:
                violations.append(f"{f.name}: {matches}")
        assert (
            violations == []
        ), "Preprocessors generating bare FA4 'fa' prefix — causes mdBook build warnings:\n" + "\n".join(violations)


class TestArchiveNotices:
    """Archive notices must be injected by the preprocessor, not hardcoded in
    source files. Hardcoded notices drift out of sync and leak markup into
    what should be clean content files."""

    def test_no_hardcoded_archive_notice_divs(self) -> None:
        violations = [
            str(f.relative_to(ROOT)) for f in SRC_DIR.rglob("*.md") if '<div class="archive-notice"' in f.read_text()
        ]
        assert violations == [], (
            "Archive notice HTML hardcoded in source files — "
            "must be injected by mdbook_archive_notice.py preprocessor:\n" + "\n".join(violations)
        )

    def test_no_hardcoded_warning_admonitions_in_archive_files(self) -> None:
        """'> [!WARNING]' blocks in archive/ source files should be injected
        by the preprocessor, not written by hand."""
        violations = [
            str(f.relative_to(ROOT)) for f in (SRC_DIR / "archive").rglob("*.md") if "> [!WARNING]" in f.read_text()
        ]
        assert violations == [], (
            "Manual [!WARNING] admonitions in archive source files — "
            "the preprocessor injects these automatically:\n" + "\n".join(violations)
        )

    def test_archive_preprocessor_handles_items_not_sections(self) -> None:
        """Redundant with TestPreprocessorProtocol but explicit for archive notice."""
        text = (DATA_DIR / "mdbook_archive_notice.py").read_text()
        assert 'book.get("items")' in text


# ===========================================================================
# book.toml integrity
# ===========================================================================


class TestBookToml:
    """additional-css and additional-js entries must reference files that exist.
    A missing file produces a 404 in the browser (or a build error when hashing
    is enabled), with no warning from mdBook itself."""

    @pytest.fixture(scope="class")
    def toml_config(self):
        import tomllib  # Python 3.11+

        with open(ROOT / "book.toml", "rb") as f:
            return tomllib.load(f)

    def test_additional_css_files_exist(self, toml_config) -> None:
        css_files = toml_config.get("output", {}).get("html", {}).get("additional-css", [])
        missing = [p for p in css_files if not (ROOT / p).is_file()]
        assert missing == [], "additional-css entries in book.toml point to missing files:\n" + "\n".join(missing)

    def test_additional_js_files_exist(self, toml_config) -> None:
        js_files = toml_config.get("output", {}).get("html", {}).get("additional-js", [])
        missing = [p for p in js_files if not (ROOT / p).is_file()]
        assert missing == [], "additional-js entries in book.toml point to missing files:\n" + "\n".join(missing)

    def test_pagetoc_not_in_book_toml(self, toml_config) -> None:
        """pagetoc was removed in favour of the built-in mdBook 0.5 sidebar heading nav.
        It must not reappear in additional-css or additional-js."""
        html = toml_config.get("output", {}).get("html", {})
        css = html.get("additional-css", [])
        js = html.get("additional-js", [])
        pagetoc_refs = [p for p in css + js if "pagetoc" in p]
        assert (
            pagetoc_refs == []
        ), "pagetoc removed — must not be in book.toml additional-css/additional-js:\n" + "\n".join(pagetoc_refs)


class TestThemeAssets:
    """Guards for theme file integrity after the mdBook 0.5 upgrade."""

    def test_fonts_css_not_in_index_hbs(self) -> None:
        """fonts.css was conditionally loaded via copy_fonts (removed in 0.5.0).
        The unconditional link was removed because no fonts/ directory exists.
        Ensure it does not reappear in the template."""
        text = (ROOT / "theme" / "index.hbs").read_text()
        assert "fonts/fonts.css" not in text, (
            "theme/index.hbs references fonts/fonts.css but no fonts/ directory exists — "
            "this produces a 404 on every page load"
        )

    def test_pagetoc_files_deleted(self) -> None:
        """pagetoc.js and pagetoc.css were deleted when switching to the built-in
        mdBook 0.5 sidebar heading nav. They must not be re-added."""
        assert not (
            ROOT / "theme" / "pagetoc.js"
        ).exists(), "theme/pagetoc.js exists — pagetoc was removed; use the built-in sidebar heading nav"
        assert not (
            ROOT / "theme" / "pagetoc.css"
        ).exists(), "theme/pagetoc.css exists — pagetoc was removed; use the built-in sidebar heading nav"

    def test_hints_js_renders_card_header(self) -> None:
        """hints.js must render a hint-card-header for object entries with a type field.
        This is the shaded header introduced in the rich card redesign."""
        text = (ROOT / "theme" / "hints.js").read_text()
        assert "hint-card-header" in text, (
            "theme/hints.js does not render hint-card-header — " "rich card header is missing from renderHintContent()"
        )

    def test_hints_js_renders_link_icon(self) -> None:
        """hints.js must conditionally render a read-more link icon when entry.url is set."""
        text = (ROOT / "theme" / "hints.js").read_text()
        assert "entry.url" in text, "theme/hints.js does not check entry.url — read-more link icon will never render"
        assert "hint-card-link" in text, "theme/hints.js does not produce a hint-card-link element"

    def test_hints_js_uses_theme_and_offset(self) -> None:
        """hints.js must use the hint-card Tippy theme (for CSS-variable colours) and
        a small offset so the tooltip sits close to the reference text."""
        text = (ROOT / "theme" / "hints.js").read_text()
        assert 'theme: "hint-card"' in text, (
            "theme/hints.js does not set Tippy theme to 'hint-card' — " "tooltip will not inherit mdBook CSS variables"
        )
        assert "offset:" in text, (
            "theme/hints.js does not set a Tippy offset — "
            "tooltip will use the default 10px gap instead of sitting close to the text"
        )

    def test_hints_js_anchors_to_first_line(self) -> None:
        """hints.js must use getReferenceClientRect with getClientRects()[0] so the
        tooltip anchors to the first line of the span rather than the full multi-line
        bounding box (which can be several lines tall for wrapped multi-word hints)."""
        text = (ROOT / "theme" / "hints.js").read_text()
        assert "getReferenceClientRect" in text, (
            "theme/hints.js does not use getReferenceClientRect — tooltip will anchor to "
            "the full bounding box of a wrapped span rather than its first line"
        )
        assert "getClientRects" in text, (
            "theme/hints.js does not use getClientRects() — tooltip will not anchor to "
            "the first line of a multi-line hint span"
        )

    def test_hints_css_uses_mdbook_variables(self) -> None:
        """hints.css must use mdBook CSS variables for colours so the tooltip
        respects the active theme (light/dark/coal/ayu etc.)."""
        text = (ROOT / "theme" / "hints.css").read_text()
        assert (
            "var(--bg)" in text
        ), "hints.css does not use var(--bg) — tooltip background will not match the active theme"
        assert "var(--fg)" in text, "hints.css does not use var(--fg) — tooltip text will not match the active theme"
        assert (
            "var(--sidebar-bg)" in text
        ), "hints.css does not use var(--sidebar-bg) — card header will not match the active theme"


# ===========================================================================
# JavaScript compatibility checks
# ===========================================================================

# Custom JS files that interact with the mdBook DOM.
_CUSTOM_JS = sorted(list(ROOT.glob("*.js")) + list((ROOT / "theme").glob("*.js")))

# mdBook 0.4.x IDs that were all renamed with an "mdbook-" prefix in 0.5.x.
# Using the old IDs silently produces broken behaviour (querySelector returns null).
_OLD_MDBOOK_IDS = [
    '"sidebar"',
    '"menu-bar"',
    '"body-container"',
    '"content"',
    '"search-toggle"',
    '"search-wrapper"',
    '"searchbar"',
    '"theme-toggle"',
    '"theme-list"',
    '"sidebar-toggle-anchor"',
]


class TestJavaScriptCompatibility:
    """Static guards for custom JavaScript files against mdBook upgrade breakage.

    These tests document the exact patterns that caused silent regressions
    during the 0.4 → 0.5 upgrade, so the same mistakes can't recur.
    """

    def test_no_old_mdbook_element_ids_in_custom_js(self) -> None:
        """mdBook 0.5.3 added an 'mdbook-' prefix to all element IDs.
        getElementById/querySelector with the old IDs returns null silently."""
        violations: list[str] = []
        for js_file in _CUSTOM_JS:
            text = js_file.read_text()
            for old_id in _OLD_MDBOOK_IDS:
                if old_id in text:
                    violations.append(f"{js_file.relative_to(ROOT)}: {old_id}")
        assert violations == [], (
            "Old mdBook 0.4 element IDs found in custom JS "
            "(all IDs gained an 'mdbook-' prefix in 0.5.3):\n" + "\n".join(violations)
        )

    def test_read_tracking_uses_chapter_fold_toggle(self) -> None:
        """mdBook 0.5.3 renamed the sidebar fold toggle from 'a.toggle' to
        'a.chapter-fold-toggle'. Using the old selector makes isSectionHeader
        always false, so folder/section pages get incorrectly marked as read.

        We check the variable assignment that holds the selector string, not
        the whole file text, to avoid false-positives from comments that
        mention the old name for documentation purposes.
        """
        text = (ROOT / "theme" / "read-tracking.js").read_text()
        assert "chapter-fold-toggle" in text, "Expected 'a.chapter-fold-toggle' selector not found in read-tracking.js"
        # The selector must be assigned as a string constant — not just appear in a comment.
        import re as _re

        assigned = _re.search(r"""(?:var|const|let)\s+\w+\s*=\s*['"]a\.toggle['"]""", text)
        assert assigned is None, (
            "read-tracking.js assigns 'a.toggle' as a selector — "
            "must be 'a.chapter-fold-toggle' (renamed in mdBook 0.5.3)"
        )

    def test_read_tracking_handles_async_sidebar(self) -> None:
        """In mdBook 0.5.3 the sidebar is populated async via a toc.html fetch.
        Querying sidebar links at script-execution time always returns nothing.
        A MutationObserver (or equivalent) is required to wait for the links."""
        text = (ROOT / "theme" / "read-tracking.js").read_text()
        assert "MutationObserver" in text, (
            "read-tracking.js does not use MutationObserver — "
            "sidebar links are populated async in mdBook 0.5.3 and will not "
            "exist when the script runs synchronously"
        )

    def test_toolbar_uses_mdbook_page_wrapper_id(self) -> None:
        """mdBook 0.5.3 renamed #page-wrapper to #mdbook-page-wrapper.
        toolbar.js appends the back-to-top button to this element."""
        text = (ROOT / "theme" / "toolbar.js").read_text()
        assert "mdbook-page-wrapper" in text
        # The old ID must not appear in an actual getElementById call
        import re as _re

        old_call = _re.search(r"""getElementById\(\s*['"]page-wrapper['"]\s*\)""", text)
        assert old_call is None, (
            "toolbar.js calls getElementById('page-wrapper') — " "renamed to 'mdbook-page-wrapper' in mdBook 0.5.3"
        )

    def test_theme_js_uses_path_to_root_not_window_property(self) -> None:
        """The template sets 'const path_to_root' — a top-level const does NOT
        attach to window, so window.path_to_root is always undefined on nested
        pages. Theme JS files (which run on every page) must not use it."""
        theme_js = sorted((ROOT / "theme").glob("*.js"))
        for js_file in theme_js:
            text = js_file.read_text()
            assert "window.path_to_root" not in text, (
                f"theme/{js_file.name} uses window.path_to_root " "(undefined — template uses 'const', not 'var')"
            )


# ===========================================================================
# Build checks (slow)
# ===========================================================================


@pytest.mark.slow
class TestBuildOutput:
    """Run ``mdbook build`` and validate the output.

    These tests catch any remaining issues not covered by unit tests —
    template changes, preprocessor interactions, new mdBook behaviour, etc.
    """

    @pytest.fixture(scope="class")
    def build_result(self):
        result = subprocess.run(
            ["mdbook", "build"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return result

    def test_build_exits_zero(self, build_result) -> None:
        assert build_result.returncode == 0, f"mdbook build failed:\n{build_result.stderr}"

    def test_build_no_warnings(self, build_result) -> None:
        """A clean build must emit zero WARN lines.
        Any warning indicates a misconfiguration or an icon/template issue."""
        warn_lines = [line for line in build_result.stderr.splitlines() if line.strip().startswith("WARN")]
        assert warn_lines == [], f"mdbook build produced {len(warn_lines)} warning(s):\n" + "\n".join(warn_lines)

    def test_browse_json_is_valid(self, build_result) -> None:
        """The browse page embeds a large JSON object. Any hint injection
        inside the <script> block breaks the JSON and silently hides all
        stories from the browse UI."""
        browse_html = (BUILD_DIR / "browse.html").read_text()
        m = re.search(r"window\.FABLORE_BROWSE=({.*?});</script>", browse_html, re.DOTALL)
        assert m, "window.FABLORE_BROWSE not found in browse.html"
        data = json.loads(m.group(1))  # raises json.JSONDecodeError if corrupted
        assert len(data["stories"]) > 0, "Browse index is empty"
        assert len(data["heroes"]) > 0
        assert len(data["regions"]) > 0

    def test_archive_pages_have_injected_notices(self, build_result) -> None:
        """Every built individual archive page must have a notice injected.

        Index/category pages (stem matches parent dir, or top-level archive.html)
        intentionally have no notice — the preprocessor skips them.
        """
        archive_pages = list((BUILD_DIR / "archive").rglob("*.html"))
        assert archive_pages, "No archive pages were built"

        missing: list[str] = []
        for page in archive_pages:
            html_content = page.read_text()
            has_notice = "fablore-archive-notice:start" in html_content or "blockquote-tag-warning" in html_content
            # Skip category/index pages that the preprocessor intentionally omits:
            #   - index.html / README.html (directory listings)
            #   - stem matches parent dir name (e.g. heroes-of-rathe.html in heroes-of-rathe/)
            #   - top-level archive.html
            is_category = (
                page.stem in ("index", "README")
                or page.stem == page.parent.name
                or page.parent == BUILD_DIR / "archive"
            )
            if not has_notice and not is_category:
                missing.append(str(page.relative_to(BUILD_DIR)))

        assert missing == [], "Archive pages missing injected notice:\n" + "\n".join(missing)

    def test_story_pages_have_metadata(self, build_result) -> None:
        """Spot-check that story-meta preprocessor ran on a known story page."""
        page = BUILD_DIR / "main-story" / "welcome-to-rathe" / "a-rising-star.html"
        assert page.exists(), "a-rising-star.html was not built"
        html = page.read_text()
        assert "story-share" in html, "Share buttons missing — story-meta preprocessor may not have run"
        assert "fablore-story-meta" in html, "Story-meta markers missing"
