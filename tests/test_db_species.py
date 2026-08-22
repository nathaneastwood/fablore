"""Tests for the species tables (migration 11) — R2.

One free-text column held three different facts and could hold only one of them
at a time. These cover the three things that made the split worth doing: a
character with two species, a plural that reaches the tooltip, and the contract
reversal — species is replace-semantic where status preserves.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import db._queries as q
from db import Database, NPCEntry, SpeciesEntry
from registry_ids import lore_character_id, species_id


def _story(database: Database, **kw):
    return database.upsert_story(
        path="src/main-story/super-slam/feudmasters.md", story_type="main-story", title="T", **kw
    )


def _species_of(database: Database, name: str) -> list[str]:
    cid = lore_character_id(name)
    return [
        r[0]
        for r in database.conn.execute(
            "SELECT s.name FROM npc_species ns JOIN species s USING(species_id)"
            " WHERE ns.character_id = ? ORDER BY ns.sort_order",
            [cid],
        )
    ]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_the_species_tables(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"species", "npc_species", "species_aliases"} <= tables


def test_npcs_has_no_species_column(db: Database) -> None:
    """Retired in stage 4. Two writers on one fact is what this stage ended."""
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(npcs)")}
    assert "species" not in cols


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------


def test_a_species_is_written_from_a_declaration(db: Database) -> None:
    _story(db, characters=[NPCEntry("Biski", species=SpeciesEntry("Dog"))])
    assert _species_of(db, "Biski") == ["Dog"]


def test_an_npc_holds_two_species_in_declared_order(db: Database) -> None:
    """`Zombie Dog` was one value gluing two facts; splitting it needs both halves."""
    _story(db, characters=[NPCEntry("Scooba", species=(SpeciesEntry("Zombie"), SpeciesEntry("Dog")))])
    assert _species_of(db, "Scooba") == ["Zombie", "Dog"]


def test_species_is_replace_semantic(db: Database) -> None:
    _story(db, characters=[NPCEntry("Scooba", species=(SpeciesEntry("Zombie"), SpeciesEntry("Dog")))])
    _story(db, characters=[NPCEntry("Scooba", species=SpeciesEntry("Zombie"))])
    assert _species_of(db, "Scooba") == ["Zombie"]


def test_an_omitted_species_is_a_deletion(db: Database) -> None:
    """The reversal. ``status`` preserves on omission; a junction cannot.

    This is the behaviour that made 32 undeclared species values a migration
    problem rather than a rename.
    """
    _story(db, characters=[NPCEntry("Swabbie", species=SpeciesEntry("Zombie"))])
    _story(db, characters=[NPCEntry("Swabbie")])
    assert _species_of(db, "Swabbie") == []


def test_two_npcs_share_one_species_row(db: Database) -> None:
    """The point of a registry: `Human` is one row, not 207 strings."""
    _story(
        db,
        characters=[
            NPCEntry("Aios", species=SpeciesEntry("Human")),
            NPCEntry("Akuo", species=SpeciesEntry("Human")),
        ],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM species WHERE name = 'Human'").fetchone()[0] == 1


def test_species_aliases_are_stored_and_replace_semantic(db: Database) -> None:
    _story(db, characters=[NPCEntry("Sol", species=SpeciesEntry("Aesir", aliases=("Aesirs",)))])
    assert q.select_species_aliases(db.conn, species_id("Aesir")) == ["Aesirs"]
    _story(db, characters=[NPCEntry("Sol", species=SpeciesEntry("Aesir"))])
    assert q.select_species_aliases(db.conn, species_id("Aesir")) == []


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------


def test_dry_run_reports_a_species_it_would_add(db: Database, capsys) -> None:
    _story(db, characters=[NPCEntry("Biski")])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Biski", species=SpeciesEntry("Dog"))],
        dry_run=True,
    )
    assert "Biski: species 'Dog'" in capsys.readouterr().out


def test_dry_run_reports_a_species_it_would_remove(db: Database, capsys) -> None:
    """An omitted species is a deletion, so the preview has to say so."""
    _story(db, characters=[NPCEntry("Swabbie", species=SpeciesEntry("Zombie"))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Swabbie")],
        dry_run=True,
    )
    assert "Swabbie: species 'Zombie' REMOVED" in capsys.readouterr().out


def test_dry_run_reports_a_species_on_a_group_member(db: Database, capsys) -> None:
    """Ozrim is reachable through the Rosetta roster and through nothing else."""
    from db import GroupEntry

    _story(db, groups=[GroupEntry("Rosetta", members=(NPCEntry("Ozrim"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Rosetta", members=(NPCEntry("Ozrim", species=SpeciesEntry("Rosetta")),))],
        dry_run=True,
    )
    assert "Ozrim: species 'Rosetta'" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_species_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    _story(
        db,
        characters=[
            NPCEntry("Scooba", species=(SpeciesEntry("Zombie"), SpeciesEntry("Dog"))),
            NPCEntry("Sol", species=SpeciesEntry("Aesir", aliases=("Aesirs",))),
        ],
    )
    import db._export as _export

    _export.export_all(db.conn, tmp_path)
    fresh = Database(str(tmp_path / "round-trip.db"), data_dir=tmp_path)
    assert q.select_npc_species(fresh.conn, lore_character_id("Scooba")) == [
        species_id("Zombie"),
        species_id("Dog"),
    ]
    assert q.select_species_aliases(fresh.conn, species_id("Aesir")) == ["Aesirs"]


def test_update_description_writes_species_notes(db: Database) -> None:
    _story(db, characters=[NPCEntry("Ozrim", species=SpeciesEntry("Chanek"))])
    db.update_description("species", "Chanek", "Green-skinned, pointed-eared Rathenfolk of the far west.")
    row = db.conn.execute("SELECT notes FROM species WHERE name = 'Chanek'").fetchone()
    assert row["notes"].startswith("Green-skinned")


def test_update_description_rejects_a_species_with_no_row(db: Database) -> None:
    with pytest.raises(ValueError, match="Species not found"):
        db.update_description("species", "Nonesuch", "…")
