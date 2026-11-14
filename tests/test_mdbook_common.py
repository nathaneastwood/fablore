"""Tests for the helpers the mdBook preprocessors share."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from mdbook_common import (
    arc_display_name,
    arc_release_date,
    book_src_root,
    format_date,
    iter_chapters,
    md_to_html_url,
    relative_href,
    run,
)


def _ch(path: str, *subs: dict) -> dict:
    return {"Chapter": {"path": path, "content": "", "sub_items": list(subs)}}


def test_iter_chapters_is_pre_order_and_skips_separators() -> None:
    items = [_ch("a.md", _ch("a/b.md", _ch("a/b/c.md")), "Separator"), {"PartTitle": "P"}, _ch("d.md")]
    assert [ch["path"] for ch in iter_chapters(items)] == ["a.md", "a/b.md", "a/b/c.md", "d.md"]


def test_relative_href() -> None:
    assert relative_href("main-story/arc/story.md", "heroes-of-rathe/dash-about.md") == (
        "../../heroes-of-rathe/dash-about.md"
    )
    assert relative_href("index.md", "a/b.md") == "a/b.md"


def test_md_to_html_url() -> None:
    assert md_to_html_url(" a/b.md ") == "a/b.html"
    assert md_to_html_url("a/b") == "a/b"
    assert md_to_html_url("  ") == ""


def test_format_date() -> None:
    assert format_date("2019-10-11T00:00:00.000Z") == "11 October 2019"
    assert format_date("not a date") == "not a date"
    assert format_date("  ") == ""


ARCS = {
    "01-welcome": {"Slug": "01-welcome", "SetId": "S1", "DisplayName": ""},
    "02-announced": {"Slug": "02-announced", "SetId": "", "SortDate": "2030-01-02"},
}
SETS = {"S1": {"SetId": "S1", "SetName": "Welcome to Rathe", "InitialReleaseDate": "2019-10-11T00:00:00Z"}}


def test_arc_display_name_falls_back_to_set_then_slug() -> None:
    assert arc_display_name("01-welcome", ARCS, SETS) == "Welcome to Rathe"
    assert arc_display_name("02-announced", ARCS, SETS) == "Announced"


def test_arc_release_date_sort_date_fallback_is_opt_in() -> None:
    """The Sets index shows an unreleased arc's SortDate; the set hubs do not."""
    assert arc_release_date("01-welcome", ARCS, SETS, sort_date_fallback=False) == "11 October 2019"
    assert arc_release_date("02-announced", ARCS, SETS, sort_date_fallback=True) == "2 January 2030"
    assert arc_release_date("02-announced", ARCS, SETS, sort_date_fallback=False) == ""


def test_book_src_root_reads_book_src(tmp_path: Path) -> None:
    assert book_src_root({"root": str(tmp_path)}) == (tmp_path / "src").resolve()
    assert (
        book_src_root({"root": str(tmp_path), "config": {"book": {"src": " docs "}}}) == (tmp_path / "docs").resolve()
    )


def test_run_passes_items_and_src_root(monkeypatch, tmp_path: Path) -> None:
    book = {"items": [_ch("a.md")]}
    monkeypatch.setattr(sys, "argv", ["prog"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps([{"root": str(tmp_path)}, book])))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    seen = []

    def process(items: list, src_root: Path) -> None:
        seen.append(src_root)
        for ch in iter_chapters(items):
            ch["content"] = "done"

    run(process)
    assert seen == [(tmp_path / "src").resolve()]
    assert json.loads(out.getvalue())["items"][0]["Chapter"]["content"] == "done"


def test_run_answers_supports(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "supports", "html"])
    with pytest.raises(SystemExit) as exc:
        run(lambda items, src_root: None)
    assert exc.value.code == 0
