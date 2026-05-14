"""Tests for :meth:`Story.remove`."""

from __future__ import annotations

import io
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


def test_remove_dry_run_reports_junction_and_registry_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dry run lists rows that would be deleted per file without writing."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "archive" / "sample.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Sample\n", encoding="utf-8")

    s = story.Story(md, "archive", "Sample title")
    sid = s.story_id
    sk = s.story_key

    (data / "story-npcs.csv").write_text(
        "StoryId|CharacterId\n"
        f"{sid}|LCaaaaaaaaaa|\n"
        f"{sid}|LCbbbbbbbbbb|\n"
        f"ST9999999999|LCcccccccccc|\n",
        encoding="utf-8",
    )

    buf = io.StringIO()
    report = s.remove(dry_run=True, file=buf)
    text = buf.getvalue()

    assert report["dry_run"] is True
    assert report["story_key"] == sk
    assert report["story_id"] == sid
    assert report["files"]["story-npcs.csv"]["removed_count"] == 2
    assert report["files"]["stories.csv"]["removed_count"] == 1
    assert "story-npcs.csv: 2 row(s)" in text
    assert "DRY RUN" in text


def test_remove_applies_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-dry run strips junction rows and the ``stories.csv`` row."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "main-story" / "x.md"
    md.parent.mkdir(parents=True)
    md.write_text("# X\n", encoding="utf-8")

    s = story.Story(md, "main-story", "X")
    sid = s.story_id

    (data / "story-npcs.csv").write_text(
        "StoryId|CharacterId\n" f"{sid}|LC1111111111|\n",
        encoding="utf-8",
    )

    report = s.remove(dry_run=False, run_validate=False)
    assert report["dry_run"] is False
    assert report["files"]["story-npcs.csv"]["removed_count"] == 1

    _, npc_rows = story.read_pipe_csv(data / "story-npcs.csv")
    assert npc_rows == []

    _, story_rows = story.read_pipe_csv(data / "stories.csv")
    assert all((r.get("StoryKey") or "").strip() != s.story_key for r in story_rows)


def test_remove_second_pass_is_no_op(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A second :meth:`remove` after data is already cleared does not rewrite files."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "flavour" / "twice.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Twice\n", encoding="utf-8")

    s = story.Story(md, "flavour", "Twice")
    sid = s.story_id
    (data / "story-npcs.csv").write_text(
        "StoryId|CharacterId\n" f"{sid}|LCffffffffff|\n",
        encoding="utf-8",
    )

    s.remove(dry_run=False, run_validate=False)
    snap_stories = (data / "stories.csv").read_text(encoding="utf-8")
    snap_npcs = (data / "story-npcs.csv").read_text(encoding="utf-8")

    report2 = s.remove(dry_run=False, run_validate=False)
    assert sum(v["removed_count"] for v in report2["files"].values()) == 0
    assert (data / "stories.csv").read_text(encoding="utf-8") == snap_stories
    assert (data / "story-npcs.csv").read_text(encoding="utf-8") == snap_npcs
