"""Tests that the dry-run preview does not scan a registry it never renders.

``_DryRunReport`` builds every id -> name/slug map it needs as a
``functools.cached_property`` rather than unconditionally at the top of
``Database._dry_run_upsert``, so a preview that never touches (say) titles or
food never issues a query against those tables.

Seam: the public ``Database.upsert_story(..., dry_run=True)``, observed
through a spy on the ``db._queries`` functions the maps are built from. This
is the only way to see "a table was not scanned" from outside the class —
the report's printed text cannot distinguish "empty because the table is
empty" from "never queried" — so the spy is on the query layer's own public
functions, not on any private attribute of the report.
"""

from __future__ import annotations

import db._queries as q
from db import CharacterEntry, Database


def _spy(monkeypatch, name: str) -> list[int]:
    """Wrap ``db._queries.<name>`` to count calls; return the call-count list."""
    calls: list[int] = [0]
    original = getattr(q, name)

    def wrapped(*args, **kwargs):
        calls[0] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(q, name, wrapped)
    return calls


def test_preview_naming_no_titles_does_not_scan_titles_table(db: Database, monkeypatch, capsys) -> None:
    """A story with no ``titles=`` and no title reachable through it never reads ``titles``."""
    calls = _spy(monkeypatch, "select_all_titles")

    db.upsert_story(
        path="src/main-story/foo/bar.md",
        story_type="main-story",
        title="Bar",
        characters=[CharacterEntry("Guard Captain")],
        dry_run=True,
    )
    capsys.readouterr()

    assert calls[0] == 0, "select_all_titles was called even though this declaration never names a title"


def test_preview_naming_no_food_drink_does_not_scan_food_drink_table(db: Database, monkeypatch, capsys) -> None:
    """A story with no ``food_drink=`` never reads ``food_and_drink``."""
    calls = _spy(monkeypatch, "select_all_food_drink")

    db.upsert_story(
        path="src/main-story/foo/bar.md",
        story_type="main-story",
        title="Bar",
        characters=[CharacterEntry("Guard Captain")],
        dry_run=True,
    )
    capsys.readouterr()

    assert calls[0] == 0, "select_all_food_drink was called even though this declaration never names food/drink"


def test_preview_naming_a_title_does_scan_titles_table(db: Database, monkeypatch, capsys) -> None:
    """Sanity check on the spy itself: a declaration that *does* name a title does read it.

    Without this, the two tests above could pass for the wrong reason — a
    spy that never fires regardless of what is declared.
    """
    from db import TitleEntry

    calls = _spy(monkeypatch, "select_all_titles")

    db.upsert_story(
        path="src/main-story/foo/bar.md",
        story_type="main-story",
        title="Bar",
        titles=[TitleEntry("Grand Magister")],
        dry_run=True,
    )
    capsys.readouterr()

    assert calls[0] == 1, "select_all_titles should be read exactly once when a title is declared"


def test_registry_scanned_at_most_once_per_preview(db: Database, monkeypatch, capsys) -> None:
    """The character registry — read by several report sections — is still scanned once.

    ``character_rows`` backs ``character_id_to_name``, used by
    ``show_character_links``, ``show_character_creations``,
    ``show_hero_slug_changes``, ``show_kin_changes`` and
    ``show_attr_changes("Character", ...)``. A ``cached_property`` means
    every one of those reads the same computed dict; this pins that down so
    a future edit that swaps a property read for a fresh query is caught
    here rather than only in a slow-query review.
    """
    calls = _spy(monkeypatch, "select_all_characters")

    db.upsert_story(
        path="src/main-story/foo/bar.md",
        story_type="main-story",
        title="Bar",
        characters=[CharacterEntry("Guard Captain", hero_slug="")],
        dry_run=True,
    )
    capsys.readouterr()

    assert calls[0] == 1, "select_all_characters should be read exactly once even though several sections use it"
