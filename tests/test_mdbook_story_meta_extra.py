"""Additional tests for ``mdbook_story_meta`` to improve coverage of
_format_date, _build_meta_html branches, _load_story_meta, _inject_after_heading,
and _walk_sections.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_story_meta import (  # noqa: E402
    MARK_END,
    MARK_START,
    _build_meta_html,
    _format_date,
    _inject_after_heading,
    _load_story_meta,
    _walk_sections,
)


# ---------------------------------------------------------------------------
# _format_date
# ---------------------------------------------------------------------------


def test_format_date_empty_string() -> None:
    assert _format_date("") == ""


def test_format_date_whitespace_only() -> None:
    assert _format_date("   ") == ""


def test_format_date_normal() -> None:
    assert _format_date("2023-01-15") == "15 January 2023"


def test_format_date_swapped_month_day() -> None:
    # "2019-29-08" fails normal parse; fallback tries year=2019, month=8, day=29
    assert _format_date("2019-29-08") == "29 August 2019"


def test_format_date_garbage_returns_raw() -> None:
    assert _format_date("not-a-date") == "not-a-date"


def test_format_date_three_parts_unparseable() -> None:
    # Three parts that still can't be parsed as a date (e.g. all zeros)
    assert _format_date("0000-00-00") == "0000-00-00"


# ---------------------------------------------------------------------------
# _build_meta_html — artists, date, and source_link branches
# ---------------------------------------------------------------------------


def test_build_meta_html_with_artists() -> None:
    result = _build_meta_html(
        authors="",
        artists="Alice",
        publication_date="",
        source_link="",
        word_count=0,
    )
    assert "Alice" in result
    assert "fa-image" in result


def test_build_meta_html_with_date() -> None:
    result = _build_meta_html(
        authors="",
        artists="",
        publication_date="2023-01-15",
        source_link="",
        word_count=0,
    )
    assert "January" in result
    assert "fa-calendar" in result


def test_build_meta_html_with_source_link() -> None:
    result = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="https://example.com",
        word_count=0,
    )
    assert "https://example.com" in result
    assert "Original article" in result
    assert "fa-external-link" in result


def test_build_meta_html_word_count_above_min() -> None:
    result = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=300,
        show_word_count=True,
    )
    assert "words" in result
    assert "min read" in result


def test_build_meta_html_word_count_below_min() -> None:
    # Under _MIN_WORDS_FOR_READTIME (50) — shows count but no "min read"
    result = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=30,
        show_word_count=True,
    )
    assert "words" in result
    assert "min read" not in result


# ---------------------------------------------------------------------------
# _load_story_meta
# ---------------------------------------------------------------------------


def test_load_story_meta_missing_csv(tmp_path: Path) -> None:
    # tmp_path has no csv/stories.csv — should return {}
    result = _load_story_meta(tmp_path)
    assert result == {}


def test_load_story_meta_filters_empty_story_keys(tmp_path: Path) -> None:
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    # Write a stories.csv with one valid row and one with an empty StoryKey
    (csv_dir / "stories.csv").write_text(
        "StoryId|StoryKey|Title|Authors|Artists|PublicationDate|SourceLink|StoryType|ThumbnailImageLink\n"
        "ST001|main-story/foo.md|Foo|Alice||||\n"
        "ST002||Empty Key|Bob||||\n",
        encoding="utf-8",
    )
    result = _load_story_meta(tmp_path)
    assert "main-story/foo.md" in result
    # The empty-key row must be excluded
    assert "" not in result
    assert len(result) == 1


# ---------------------------------------------------------------------------
# _inject_after_heading
# ---------------------------------------------------------------------------


def test_inject_after_heading_no_h1_prepends_block() -> None:
    result = _inject_after_heading("No heading here.", "<p>meta</p>")
    assert MARK_START in result
    assert "<p>meta</p>" in result
    # Block comes before the original content
    assert result.index(MARK_START) < result.index("No heading here.")


def test_inject_after_heading_with_h1_inserts_after() -> None:
    result = _inject_after_heading("# Title\n\nContent", "<p>meta</p>")
    assert "# Title" in result
    assert MARK_START in result
    assert "<p>meta</p>" in result
    # Heading must come before the meta block
    assert result.index("# Title") < result.index(MARK_START)


def test_inject_after_heading_replaces_existing() -> None:
    existing = f"# Title\n\n{MARK_START}\nOLD\n{MARK_END}\n\nContent"
    result = _inject_after_heading(existing, "<p>NEW</p>")
    assert "OLD" not in result
    assert "<p>NEW</p>" in result


def test_inject_after_heading_empty_inner_returns_bare() -> None:
    # When inner_html is blank, the function returns the stripped bare content
    content = "# Title\n\nBody."
    result = _inject_after_heading(content, "   ")
    assert MARK_START not in result
    assert "Body." in result


# ---------------------------------------------------------------------------
# _walk_sections
# ---------------------------------------------------------------------------


def test_walk_sections_injects_for_matching_chapter() -> None:
    meta = {
        "main-story/foo.md": {
            "Authors": "Alice",
            "Artists": "",
            "PublicationDate": "",
            "SourceLink": "",
            "StoryType": "main-story",
        }
    }
    sections = [
        {
            "Chapter": {
                "path": "main-story/foo.md",
                "content": "# Foo\n\nHello world.",
                "sub_items": [],
            }
        }
    ]
    _walk_sections(sections, meta)
    assert MARK_START in sections[0]["Chapter"]["content"]


def test_walk_sections_skips_unmatched_chapter() -> None:
    meta: dict = {}
    sections = [
        {
            "Chapter": {
                "path": "main-story/bar.md",
                "content": "# Bar\n\nContent.",
                "sub_items": [],
            }
        }
    ]
    _walk_sections(sections, meta)
    assert MARK_START not in sections[0]["Chapter"]["content"]


def test_walk_sections_recurses_into_sub_items() -> None:
    meta = {
        "main-story/child.md": {
            "Authors": "Bob",
            "Artists": "",
            "PublicationDate": "",
            "SourceLink": "",
            "StoryType": "main-story",
        }
    }
    sections = [
        {
            "Chapter": {
                "path": "main-story/parent.md",
                "content": "# Parent",
                "sub_items": [
                    {
                        "Chapter": {
                            "path": "main-story/child.md",
                            "content": "# Child\n\nText.",
                            "sub_items": [],
                        }
                    }
                ],
            }
        }
    ]
    _walk_sections(sections, meta)
    inner = sections[0]["Chapter"]["sub_items"][0]["Chapter"]["content"]
    assert MARK_START in inner
    # Parent was not in meta, so no injection there
    assert MARK_START not in sections[0]["Chapter"]["content"]


def test_walk_sections_ignores_non_dict_items() -> None:
    meta: dict = {}
    sections: list = ["not a dict", None, 42]
    # Should not raise
    _walk_sections(sections, meta)


def test_walk_sections_chapter_with_empty_path() -> None:
    meta: dict = {}
    sections = [
        {
            "Chapter": {
                "path": "",
                "content": "# No Path",
                "sub_items": [],
            }
        }
    ]
    # Should not raise; nothing injected
    _walk_sections(sections, meta)
    assert MARK_START not in sections[0]["Chapter"]["content"]
