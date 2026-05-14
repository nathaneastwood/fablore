"""Tests for :mod:`create_stories_index` title inference and discovery."""

from __future__ import annotations

from pathlib import Path

import create_stories_index as csi
import pytest


def test_title_from_filename_stem() -> None:
    """Slug stems become title-cased words."""
    assert csi.title_from_filename_stem("a-lost-tome") == "A Lost Tome"
    assert csi.title_from_filename_stem("data_doll") == "Data Doll"


def test_first_h1_title_from_markdown() -> None:
    """First ATX H1 is parsed; H2-only bodies yield None."""
    assert csi.first_h1_title_from_markdown("# Hello\n\n") == "Hello"
    assert csi.first_h1_title_from_markdown("## H2\n\n# H1\n") == "H1"
    assert csi.first_h1_title_from_markdown("# Title {#anchor}\n") == "Title"
    assert csi.first_h1_title_from_markdown("## Only H2\n") is None


def test_infer_story_title_prefers_h1(tmp_path: Path) -> None:
    """infer_story_title reads the first H1 from disk."""
    md = tmp_path / "x.md"
    md.write_text("# File Head\nBody\n", encoding="utf-8")
    assert csi.infer_story_title(md) == "File Head"


def test_infer_story_title_fallback_to_stem(tmp_path: Path) -> None:
    """Without H1, the filename stem is title-cased."""
    md = tmp_path / "no-heading.md"
    md.write_text("Just prose.\n", encoding="utf-8")
    assert csi.infer_story_title(md) == "No Heading"


def test_discover_preserves_existing_title(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Non-default Title in existing metadata is kept when rescanning."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From File\n", encoding="utf-8")
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    existing = {
        "main-story/sample.md": {
            "title": "Kept Title",
            "authors": "Author A",
            "artists": "",
            "source_link": "",
            "publication_date": "",
            "thumbnail_image_link": "",
        }
    }
    rows = csi.discover_story_keys(existing)
    assert len(rows) == 1
    assert rows[0]["title"] == "Kept Title"
    assert rows[0]["authors"] == "Author A"


def test_discover_refreshes_when_title_is_only_stem_placeholder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If title matches filename stem capwords, re-infer (e.g. after adding H1)."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From H1\n", encoding="utf-8")
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    existing = {"main-story/sample.md": {"title": "Sample"}}
    rows = csi.discover_story_keys(existing)
    assert len(rows) == 1
    assert rows[0]["title"] == "From H1"


def test_discover_infers_when_existing_title_blank(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Blank title in existing metadata is replaced by inference from the markdown file."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From File\n", encoding="utf-8")
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    existing = {"main-story/sample.md": {"title": ""}}
    rows = csi.discover_story_keys(existing)
    assert len(rows) == 1
    assert rows[0]["title"] == "From File"
