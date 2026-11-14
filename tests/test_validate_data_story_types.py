"""Tests for ``stories.csv`` ``StoryType`` allowlist in :mod:`validate_data`."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_data import ALLOWED_STORY_TYPES, _check_stories_publication_dates, _check_stories_story_type_allowlist


def test_story_type_unknown_emits_alert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A StoryType not in the allowlist is reported."""
    stories = tmp_path / "stories.csv"
    stories.write_text(
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink|NarratedVideos\n"
        "ST1111111111|main-story/x.md|mainn-story|Title\n",
        encoding="utf-8",
    )
    src = tmp_path / "src"
    for name in ALLOWED_STORY_TYPES:
        (src / name).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("validate_data.SRC", src)
    alerts = _check_stories_story_type_allowlist(stories)
    assert len(alerts) == 1
    assert "mainn-story" in alerts[0]


def test_story_type_allowlist_matches_src_directories() -> None:
    """Every allowlisted type is a real directory under the repo ``src/``."""
    repo_root = Path(__file__).resolve().parent.parent
    src = repo_root / "src"
    for name in ALLOWED_STORY_TYPES:
        assert (src / name).is_dir(), f"missing src/{name}/ for ALLOWED_STORY_TYPES"


def test_publication_date_that_is_not_iso_emits_alert(tmp_path: Path) -> None:
    """A swapped, unpadded or impossible PublicationDate is reported; blank and ISO dates pass."""
    stories = tmp_path / "stories.csv"
    stories.write_text(
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink\n"
        "ST0000000001|main-story/a.md|main-story|A||||2019-08-29|\n"
        "ST0000000002|main-story/b.md|main-story|B|||||\n"
        "ST0000000003|main-story/c.md|main-story|C||||2019-29-08|\n"
        "ST0000000004|main-story/d.md|main-story|D||||2019-8-29|\n"
        "ST0000000005|main-story/e.md|main-story|E||||2019-02-30|\n",
        encoding="utf-8",
    )
    alerts = _check_stories_publication_dates(stories)
    assert len(alerts) == 3
    assert all("PublicationDate" in a for a in alerts)
    for alert, key in zip(alerts, ("main-story/c.md", "main-story/d.md", "main-story/e.md")):
        assert key in alert


def test_committed_publication_dates_are_iso() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    assert _check_stories_publication_dates(repo_root / "src/data/csv/stories.csv") == []
