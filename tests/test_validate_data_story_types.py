"""Tests for ``stories.csv`` ``StoryType`` allowlist in :mod:`validate_data`."""

from __future__ import annotations

from pathlib import Path

import pytest

from validate_data import ALLOWED_STORY_TYPES, _check_stories_story_type_allowlist


def test_story_type_unknown_emits_alert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A StoryType not in the allowlist is reported."""
    stories = tmp_path / "stories.csv"
    stories.write_text(
        "StoryId|StoryKey|StoryType|Title\n"
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
