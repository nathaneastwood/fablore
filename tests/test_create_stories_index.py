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


def test_discover_preserves_existing_csv_title(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Non-empty Title in stories.csv is kept when rescanning."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From File\n", encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    stories = data / "stories.csv"
    stories.write_text(
        "# AUTO\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink|NarratedVideos\n"
        "ST1111111111|main-story/sample.md|main-story|Kept Title|Author A|||||\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "DATA", data)
    monkeypatch.setattr(csi, "STORIES_CSV_PATH", stories)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    rows = csi.discover_story_keys()
    assert len(rows) == 1
    assert rows[0]["Title"] == "Kept Title"
    assert rows[0]["Authors"] == "Author A"


def test_discover_refreshes_when_csv_title_is_only_stem_placeholder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If Title matches filename stem capwords, re-infer (e.g. after adding H1)."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From H1\n", encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    stories = data / "stories.csv"
    stories.write_text(
        "# AUTO\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink|NarratedVideos\n"
        "ST1111111111|main-story/sample.md|main-story|Sample\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "DATA", data)
    monkeypatch.setattr(csi, "STORIES_CSV_PATH", stories)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    rows = csi.discover_story_keys()
    assert len(rows) == 1
    assert rows[0]["Title"] == "From H1"


def test_discover_infers_when_csv_title_blank(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Blank Title in CSV is replaced by inference from the markdown file."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "sample.md"
    md.write_text("# From File\n", encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    stories = data / "stories.csv"
    stories.write_text(
        "# AUTO\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink|NarratedVideos\n"
        "ST1111111111|main-story/sample.md|main-story|\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "DATA", data)
    monkeypatch.setattr(csi, "STORIES_CSV_PATH", stories)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))
    rows = csi.discover_story_keys()
    assert len(rows) == 1
    assert rows[0]["Title"] == "From File"
