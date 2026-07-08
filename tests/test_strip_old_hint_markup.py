"""Tests for strip_old_hint_markup.strip_file()."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from strip_old_hint_markup import strip_file  # noqa: E402


def test_strips_single_occurrence(tmp_path):
    f = tmp_path / "story.md"
    f.write_text("The [Hand of Sol](~HandOfSol) marched forth.\n", encoding="utf-8")
    changed = strip_file(f)
    assert changed is True
    assert f.read_text(encoding="utf-8") == "The Hand of Sol marched forth.\n"


def test_strips_multiple_occurrences(tmp_path):
    f = tmp_path / "story.md"
    f.write_text("[Brawnhide](~Brawnhide) and [Sol](~Sol) appear.\n", encoding="utf-8")
    strip_file(f)
    assert f.read_text(encoding="utf-8") == "Brawnhide and Sol appear.\n"


def test_no_markup_returns_false(tmp_path):
    f = tmp_path / "story.md"
    f.write_text("No hint markup here.\n", encoding="utf-8")
    changed = strip_file(f)
    assert changed is False


def test_no_markup_leaves_file_unchanged(tmp_path):
    f = tmp_path / "story.md"
    original = "Just plain [a link](https://example.com) and text.\n"
    f.write_text(original, encoding="utf-8")
    strip_file(f)
    assert f.read_text(encoding="utf-8") == original


def test_preserves_display_text(tmp_path):
    f = tmp_path / "story.md"
    f.write_text("[the ancient city](~SomeKey) stood tall.\n", encoding="utf-8")
    strip_file(f)
    assert f.read_text(encoding="utf-8") == "the ancient city stood tall.\n"


def test_normal_markdown_links_untouched(tmp_path):
    f = tmp_path / "story.md"
    original = "See [this page](../other.md) for details.\n"
    f.write_text(original, encoding="utf-8")
    changed = strip_file(f)
    assert changed is False
    assert f.read_text(encoding="utf-8") == original
