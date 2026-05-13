"""Tests for story metadata persistence in ``stories.csv``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import story


def _patch_story_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Point ``story`` module data dirs at ``tmp_path``."""
    root = tmp_path
    src = root / "src"
    data = src / "data"
    data.mkdir(parents=True)
    monkeypatch.setattr(story, "ROOT", root)
    monkeypatch.setattr(story, "SRC", src)
    monkeypatch.setattr(story, "DATA", data)
    monkeypatch.setattr(story, "STORIES_PATH", data / "stories.csv")
    return src, data


def test_story_constructor_persists_story_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Story metadata kwargs are written to ``stories.csv``."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "main-story" / "meta.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Meta\n", encoding="utf-8")

    story.Story(
        md,
        "main-story",
        "Meta",
        authors="Author A, Author B",
        illustrators="Illustrator A",
        source_link="https://example.com/story",
        publication_date="2026-05-13",
        thumbnail_image_link="https://example.com/thumb.jpg",
        narrated_videos=[
            {"author": "Narrator One", "url": "https://video.example.com/1"}
        ],
    )

    _, rows = story.read_pipe_csv(data / "stories.csv")
    assert len(rows) == 1
    row = rows[0]
    assert row["Authors"] == "Author A, Author B"
    assert row["Illustrators"] == "Illustrator A"
    assert row["SourceLink"] == "https://example.com/story"
    assert row["PublicationDate"] == "2026-05-13"
    assert row["ThumbnailImageLink"] == "https://example.com/thumb.jpg"
    assert json.loads(row["NarratedVideos"]) == [
        {"author": "Narrator One", "url": "https://video.example.com/1"}
    ]


def test_story_constructor_rejects_invalid_narrated_videos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Narrated video entries require both ``author`` and ``url``."""
    src, _ = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "main-story" / "meta.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Meta\n", encoding="utf-8")

    with pytest.raises(ValueError, match="author"):
        story.Story(
            md,
            "main-story",
            "Meta",
            narrated_videos=[{"author": "Narrator Only"}],
        )
