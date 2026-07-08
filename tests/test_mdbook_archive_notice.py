"""Tests for mdbook_archive_notice pure-logic helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_archive_notice import (  # noqa: E402
    MARK_END,
    MARK_START,
    _build_notice,
    _inject_notice,
    _region_display,
    _region_from_path,
    _relative_href,
)


# ---------------------------------------------------------------------------
# _region_from_path
# ---------------------------------------------------------------------------


def test_region_from_path_nested():
    assert _region_from_path("archive/world-of-rathe/solana/guide.md") == "solana"


def test_region_from_path_flat():
    assert _region_from_path("archive/world-of-rathe/solana.md") == "solana"


def test_region_from_path_not_archive():
    assert _region_from_path("world-of-rathe/solana/guide.md") is None


def test_region_from_path_wrong_section():
    assert _region_from_path("main-story/set/story.md") is None


def test_region_from_path_too_short():
    assert _region_from_path("archive/other.md") is None


# ---------------------------------------------------------------------------
# _region_display
# ---------------------------------------------------------------------------


def test_region_display_hyphenated():
    assert _region_display("the-savage-lands") == "The Savage Lands"


def test_region_display_single_word():
    assert _region_display("solana") == "Solana"


# ---------------------------------------------------------------------------
# _relative_href
# ---------------------------------------------------------------------------


def test_relative_href_same_depth():
    result = _relative_href("archive/world-of-rathe/solana/guide.md", "world-of-rathe/solana.md")
    assert result == "../../../world-of-rathe/solana.md"


def test_relative_href_flat():
    result = _relative_href("archive/world-of-rathe/solana.md", "world-of-rathe/solana.md")
    assert result == "../../world-of-rathe/solana.md"


# ---------------------------------------------------------------------------
# _build_notice
# ---------------------------------------------------------------------------


def test_build_notice_with_existing_page(tmp_path):
    src_root = tmp_path / "src"
    (src_root / "world-of-rathe").mkdir(parents=True)
    (src_root / "world-of-rathe" / "solana.md").touch()
    notice = _build_notice("archive/world-of-rathe/solana/guide.md", "solana", src_root)
    assert '<div class="archive-notice"' in notice
    assert "<a href=" in notice
    assert "Solana" in notice
    assert "superseded" in notice


def test_build_notice_without_existing_page(tmp_path):
    src_root = tmp_path / "src"
    src_root.mkdir()
    notice = _build_notice("archive/world-of-rathe/lost-region/guide.md", "lost-region", src_root)
    assert '<div class="archive-notice"' in notice
    assert "<a href=" not in notice
    assert "historical reference" in notice


# ---------------------------------------------------------------------------
# _inject_notice
# ---------------------------------------------------------------------------


def test_inject_after_h1():
    content = "# My Title\n\nSome body text.\n"
    notice = '<div class="archive-notice">Note</div>'
    result = _inject_notice(content, notice)
    assert result.index("# My Title") < result.index("archive-notice")
    assert "Some body text." in result


def test_inject_no_h1_prepends():
    content = "No heading here.\n"
    notice = '<div class="archive-notice">Note</div>'
    result = _inject_notice(content, notice)
    assert result.startswith(MARK_START)


def test_inject_replaces_existing_notice():
    old_notice = '<div class="archive-notice">Old</div>'
    new_notice = '<div class="archive-notice">New</div>'
    content = f"# Title\n\n{MARK_START}\n{old_notice}\n{MARK_END}\n\nBody.\n"
    result = _inject_notice(content, new_notice)
    assert "Old" not in result
    assert "New" in result
    assert result.count(MARK_START) == 1


def test_inject_idempotent(tmp_path):
    src_root = tmp_path / "src"
    (src_root / "world-of-rathe").mkdir(parents=True)
    (src_root / "world-of-rathe" / "solana.md").touch()
    notice = _build_notice("archive/world-of-rathe/solana/guide.md", "solana", src_root)
    content = "# Title\n\nBody text.\n"
    once = _inject_notice(content, notice)
    twice = _inject_notice(once, notice)
    assert once == twice
