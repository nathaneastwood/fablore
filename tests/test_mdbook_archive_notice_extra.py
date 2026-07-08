"""Additional tests for ``mdbook_archive_notice`` to cover _walk (lines 77-88)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_archive_notice import MARK_START, _walk  # noqa: E402


# ---------------------------------------------------------------------------
# _walk
# ---------------------------------------------------------------------------


def test_walk_injects_notice_for_archive_chapter(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    src_root.mkdir()
    # Provide a current world-of-rathe page so the "with link" variant is used
    (src_root / "world-of-rathe").mkdir()
    (src_root / "world-of-rathe" / "solana.md").write_text("# Solana")

    sections = [
        {
            "Chapter": {
                "path": "archive/world-of-rathe/solana/history.md",
                "content": "# Old Solana\n\nOld lore.",
                "sub_items": [],
            }
        }
    ]
    _walk(sections, src_root)
    content = sections[0]["Chapter"]["content"]
    assert MARK_START in content
    assert "archive-notice" in content


def test_walk_skips_non_archive_chapter(tmp_path: Path) -> None:
    sections = [
        {
            "Chapter": {
                "path": "main-story/foo.md",
                "content": "# Story\n\nContent.",
                "sub_items": [],
            }
        }
    ]
    _walk(sections, tmp_path)
    assert MARK_START not in sections[0]["Chapter"]["content"]


def test_walk_recurses_into_sub_items(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    src_root.mkdir()

    sections = [
        {
            "Chapter": {
                "path": "main-story/foo.md",
                "content": "# Outer",
                "sub_items": [
                    {
                        "Chapter": {
                            "path": "archive/world-of-rathe/metrix/intro.md",
                            "content": "# Old Metrix\n\nContent.",
                            "sub_items": [],
                        }
                    }
                ],
            }
        }
    ]
    _walk(sections, src_root)
    inner = sections[0]["Chapter"]["sub_items"][0]["Chapter"]["content"]
    assert MARK_START in inner
    # Outer chapter is not an archive path, so no notice injected there
    assert MARK_START not in sections[0]["Chapter"]["content"]


def test_walk_handles_separator(tmp_path: Path) -> None:
    # Separator items have no "Chapter" key — _walk should skip them silently
    sections: list = [{"Separator": None}]
    _walk(sections, tmp_path)  # must not raise


def test_walk_handles_non_dict_items(tmp_path: Path) -> None:
    sections: list = ["not a dict", 42, None]
    _walk(sections, tmp_path)  # must not raise


def test_walk_chapter_with_empty_path(tmp_path: Path) -> None:
    sections = [
        {
            "Chapter": {
                "path": "",
                "content": "# No Path",
                "sub_items": [],
            }
        }
    ]
    _walk(sections, tmp_path)
    # Empty path → no region detected → no notice injected
    assert MARK_START not in sections[0]["Chapter"]["content"]


def test_walk_injects_notice_without_current_page(tmp_path: Path) -> None:
    # src_root exists but has no world-of-rathe/lost-land.md → fallback notice
    src_root = tmp_path / "src"
    src_root.mkdir()

    sections = [
        {
            "Chapter": {
                "path": "archive/world-of-rathe/lost-land/intro.md",
                "content": "# Lost Land\n\nAncient text.",
                "sub_items": [],
            }
        }
    ]
    _walk(sections, src_root)
    content = sections[0]["Chapter"]["content"]
    assert MARK_START in content
    assert "historical reference" in content
