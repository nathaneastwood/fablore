"""Extra tests for :mod:`create_stories_index` — targeting uncovered branches."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

import create_stories_index as csi
import pytest


# ---------------------------------------------------------------------------
# title_from_filename_stem — empty stem (line 85)
# ---------------------------------------------------------------------------


def test_title_from_filename_stem_empty() -> None:
    """Empty stem returns empty string (line 85 branch)."""
    assert csi.title_from_filename_stem("") == ""


# ---------------------------------------------------------------------------
# _strip_wrapping_emphasis — bold (line 68) and italic (line 71)
# ---------------------------------------------------------------------------


def test_strip_wrapping_emphasis_bold() -> None:
    """Double-asterisk bold wrapper is stripped (line 68)."""
    result = csi._strip_wrapping_emphasis("**My Title**")
    assert result == "My Title"


def test_strip_wrapping_emphasis_italic() -> None:
    """Single-asterisk italic wrapper is stripped (line 71)."""
    result = csi._strip_wrapping_emphasis("*My Title*")
    assert result == "My Title"


def test_strip_wrapping_emphasis_no_wrapper() -> None:
    """Plain text is returned unchanged (fall-through after both matches fail)."""
    result = csi._strip_wrapping_emphasis("Plain Title")
    assert result == "Plain Title"


# ---------------------------------------------------------------------------
# first_h1_title_from_markdown — H1 after stripping is empty (line 110)
# ---------------------------------------------------------------------------


def test_first_h1_title_empty_after_strip() -> None:
    """An H1 whose inner text becomes empty after stripping is skipped (line 110).

    The heading ``# {#anchor}`` strips to an empty string, so the function
    continues scanning and returns None when no further headings exist.
    """
    result = csi.first_h1_title_from_markdown("# {#anchor}\n")
    assert result is None


def test_first_h1_title_bold_wrapped() -> None:
    """H1 with bold-wrapped title is unwrapped correctly."""
    result = csi.first_h1_title_from_markdown("# **Bold Title**\n")
    assert result == "Bold Title"


def test_first_h1_title_italic_wrapped() -> None:
    """H1 with italic-wrapped title is unwrapped correctly."""
    result = csi.first_h1_title_from_markdown("# *Italic Title*\n")
    assert result == "Italic Title"


# ---------------------------------------------------------------------------
# infer_story_title — file does not exist (line 127) and OSError (lines 130-131)
# ---------------------------------------------------------------------------


def test_infer_story_title_missing_file(tmp_path: Path) -> None:
    """When the file does not exist, fall back to stem title-casing (line 127)."""
    md = tmp_path / "missing-file.md"
    # Do not create the file
    result = csi.infer_story_title(md)
    assert result == "Missing File"


def test_infer_story_title_oserror(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """OSError when reading is caught and stem is used as fallback (lines 130-131)."""
    md = tmp_path / "my-story.md"
    md.write_text("# Real Title\n", encoding="utf-8")

    def _raise(*args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise OSError("simulated read error")

    monkeypatch.setattr(Path, "read_text", _raise)
    result = csi.infer_story_title(md)
    assert result == "My Story"


# ---------------------------------------------------------------------------
# discover_story_keys — None existing (line 156) and missing root dir (line 162)
# ---------------------------------------------------------------------------


def test_discover_story_keys_none_existing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Passing existing=None is handled the same as passing {} (line 156)."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    md = src / "main-story" / "intro.md"
    md.write_text("# Intro\n", encoding="utf-8")
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))

    rows = csi.discover_story_keys(None)
    assert len(rows) == 1
    assert rows[0]["story_key"] == "main-story/intro.md"


def test_discover_story_keys_skips_missing_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Roots that do not exist as directories are silently skipped (line 162)."""
    src = tmp_path / "src"
    src.mkdir()
    # "main-story" does NOT exist
    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))

    rows = csi.discover_story_keys({})
    assert rows == []


# ---------------------------------------------------------------------------
# main() — lines 199-219 (and the __name__ guard at line 222-223)
# ---------------------------------------------------------------------------


def test_main_raises_when_src_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """main() raises FileNotFoundError when src/ does not exist (line 199-200)."""
    monkeypatch.setattr(csi, "SRC", tmp_path / "nonexistent")
    with pytest.raises(FileNotFoundError, match="Missing src directory"):
        csi.main()


def test_main_runs_successfully(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """main() upserts stories and exports CSV without error (lines 202-219)."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    (src / "main-story" / "episode-one.md").write_text("# Episode One\n", encoding="utf-8")

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    monkeypatch.setattr(csi, "SRC", src)
    monkeypatch.setattr(csi, "DATA", data_dir)
    monkeypatch.setattr(csi, "STORY_ROOTS", ("main-story",))

    # Patch the db import inside main() to avoid needing fablore.db on disk
    import db
    import db._queries as q

    real_db_class = db.Database

    class _FakeDB:
        def __init__(self, path, **kwargs):  # noqa: ANN001, ANN002, ANN003
            csv_dir = data_dir / "csv"
            csv_dir.mkdir(exist_ok=True)
            self._inner = real_db_class(":memory:", data_dir=data_dir)
            self.conn = self._inner.conn

        def export_to_csv(self):  # noqa: ANN201
            pass  # skip filesystem export in the unit test

    monkeypatch.setattr(db, "Database", _FakeDB)

    captured: list[str] = []
    monkeypatch.setattr("builtins.print", lambda *a, **kw: captured.append(str(a[0])))

    csi.main()

    assert any("Upserted" in line for line in captured)
    assert any("1 stories" in line for line in captured)
