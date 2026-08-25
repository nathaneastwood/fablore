"""Tests for the kind tables (migration 11) — R2.

One free-text column held three different facts and could hold only one of them
at a time. These cover the three things that made the split worth doing: a
character with two kinds, a plural that reaches the tooltip, and the contract
reversal — kind is replace-semantic where status preserves.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import db._queries as q
from db import Database, CharacterEntry, KindEntry
from registry_ids import lore_character_id, kind_id


def _story(database: Database, **kw):
    return database.upsert_story(
        path="src/main-story/super-slam/feudmasters.md", story_type="main-story", title="T", **kw
    )


def _kind_of(database: Database, name: str) -> list[str]:
    cid = lore_character_id(name)
    return [
        r[0]
        for r in database.conn.execute(
            "SELECT s.name FROM character_kinds ns JOIN kinds s USING(kind_id)"
            " WHERE ns.character_id = ? ORDER BY ns.sort_order",
            [cid],
        )
    ]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_the_kind_tables(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"kinds", "character_kinds", "kind_aliases"} <= tables


def test_characters_has_no_kind_column(db: Database) -> None:
    """Retired in stage 4. Two writers on one fact is what this stage ended.

    Named the ``npcs`` table until stage 6d. Migration 12 had renamed it to
    ``characters`` four stages earlier, so ``PRAGMA table_info(npcs)`` returned
    no rows at all and the assertion held no matter what the schema said.
    """
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(characters)")}
    assert cols, "characters table has no columns — the PRAGMA named the wrong table"
    assert "kind" not in cols


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------


def test_a_kind_is_written_from_a_declaration(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Biski", kinds=KindEntry("Dog"))])
    assert _kind_of(db, "Biski") == ["Dog"]


def test_a_character_holds_two_kind_in_declared_order(db: Database) -> None:
    """`Zombie Dog` was one value gluing two facts; splitting it needs both halves."""
    _story(db, characters=[CharacterEntry("Scooba", kinds=(KindEntry("Zombie"), KindEntry("Dog")))])
    assert _kind_of(db, "Scooba") == ["Zombie", "Dog"]


def test_kind_is_replace_semantic(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Scooba", kinds=(KindEntry("Zombie"), KindEntry("Dog")))])
    _story(db, characters=[CharacterEntry("Scooba", kinds=KindEntry("Zombie"))])
    assert _kind_of(db, "Scooba") == ["Zombie"]


def test_an_omitted_kind_is_a_deletion(db: Database) -> None:
    """The reversal. ``status`` preserves on omission; a junction cannot.

    This is the behaviour that made 32 undeclared kind values a migration
    problem rather than a rename.
    """
    _story(db, characters=[CharacterEntry("Swabbie", kinds=KindEntry("Zombie"))])
    _story(db, characters=[CharacterEntry("Swabbie")])
    assert _kind_of(db, "Swabbie") == []


def test_two_characters_share_one_kind_row(db: Database) -> None:
    """The point of a registry: `Human` is one row, not 207 strings."""
    _story(
        db,
        characters=[
            CharacterEntry("Aios", kinds=KindEntry("Human")),
            CharacterEntry("Akuo", kinds=KindEntry("Human")),
        ],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM kinds WHERE name = 'Human'").fetchone()[0] == 1


def test_kind_aliases_are_stored_and_replace_semantic(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Sol", kinds=KindEntry("Aesir", aliases=("Aesirs",)))])
    assert q.select_kind_aliases(db.conn, kind_id("Aesir")) == ["Aesirs"]
    _story(db, characters=[CharacterEntry("Sol", kinds=KindEntry("Aesir"))])
    assert q.select_kind_aliases(db.conn, kind_id("Aesir")) == []


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------


def test_dry_run_reports_a_kind_it_would_add(db: Database, capsys) -> None:
    _story(db, characters=[CharacterEntry("Biski")])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[CharacterEntry("Biski", kinds=KindEntry("Dog"))],
        dry_run=True,
    )
    assert "Biski: kind 'Dog'" in capsys.readouterr().out


def test_dry_run_reports_a_kind_it_would_remove(db: Database, capsys) -> None:
    """An omitted kind is a deletion, so the preview has to say so."""
    _story(db, characters=[CharacterEntry("Swabbie", kinds=KindEntry("Zombie"))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[CharacterEntry("Swabbie")],
        dry_run=True,
    )
    assert "Swabbie: kind 'Zombie' REMOVED" in capsys.readouterr().out


def test_dry_run_reports_a_kind_on_a_group_member(db: Database, capsys) -> None:
    """Ozrim is reachable through the Rosetta roster and through nothing else."""
    from db import GroupEntry

    _story(db, groups=[GroupEntry("Rosetta", members=(CharacterEntry("Ozrim"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Rosetta", members=(CharacterEntry("Ozrim", kinds=KindEntry("Rosetta")),))],
        dry_run=True,
    )
    assert "Ozrim: kind 'Rosetta'" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_kind_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    _story(
        db,
        characters=[
            CharacterEntry("Scooba", kinds=(KindEntry("Zombie"), KindEntry("Dog"))),
            CharacterEntry("Sol", kinds=KindEntry("Aesir", aliases=("Aesirs",))),
        ],
    )
    import db._export as _export

    _export.export_all(db.conn, tmp_path)
    fresh = Database(str(tmp_path / "round-trip.db"), data_dir=tmp_path)
    assert q.select_character_kinds(fresh.conn, lore_character_id("Scooba")) == [
        kind_id("Zombie"),
        kind_id("Dog"),
    ]
    assert q.select_kind_aliases(fresh.conn, kind_id("Aesir")) == ["Aesirs"]


def test_update_description_writes_kind_notes(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Ozrim", kinds=KindEntry("Chanek"))])
    db.update_description("kind", "Chanek", "Green-skinned, pointed-eared Rathenfolk of the far west.")
    row = db.conn.execute("SELECT notes FROM kinds WHERE name = 'Chanek'").fetchone()
    assert row["notes"].startswith("Green-skinned")


def test_update_description_rejects_a_kind_with_no_row(db: Database) -> None:
    with pytest.raises(ValueError, match="Kind not found"):
        db.update_description("kind", "Nonesuch", "…")
