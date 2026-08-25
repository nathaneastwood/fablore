"""Tests for migration 19: the species tables become the kind tables.

Same seam as ``tests/test_db_migration_17.py`` and ``_18`` — a raw
``sqlite3.Connection`` plus ``db._schema.migrate()``, never ``Database``.

Two paths have to work and they are not the same path. An **existing**
database arrives with only the old names and needs a rename that carries every
row. A **from-scratch** build arrives with the new names already created by
``_V1_DDL`` *and* the old ones re-made empty by blocks 10 and 11, which still
create them under their original names because that is what they did. Renaming
onto an existing table fails, so the fold-and-drop branch exists for that case
alone. Migration 4 crashed on this same split.
"""

from __future__ import annotations

import sqlite3

from db._schema import CURRENT_VERSION, apply_schema, migrate


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _build_version_18_kind_tables(conn: sqlite3.Connection) -> None:
    """The four tables as they stood at version 18, under their old names."""
    conn.executescript(
        """
        CREATE TABLE characters (
            character_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unknown',
            summary TEXT NOT NULL DEFAULT '',
            other_characters_story_key TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE species (
            species_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE npc_species (
            character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
            species_id TEXT NOT NULL REFERENCES species(species_id) ON DELETE CASCADE,
            sort_order INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (character_id, species_id)
        );
        CREATE TABLE species_aliases (
            species_id TEXT NOT NULL REFERENCES species(species_id) ON DELETE CASCADE,
            alias TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (species_id, alias)
        );
        CREATE TABLE npc_epithets (
            character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'epithet',
            sort_order INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (character_id, name)
        );
        """
    )
    conn.execute("INSERT INTO characters (character_id, name) VALUES ('LCscooba', 'Scooba')")
    conn.execute("INSERT INTO species VALUES ('SPzombie', 'Zombie', '')")
    conn.execute("INSERT INTO species VALUES ('SPdog', 'Dog', 'A good one.')")
    conn.executemany(
        "INSERT INTO npc_species (character_id, species_id, sort_order) VALUES (?,?,?)",
        [("LCscooba", "SPzombie", 0), ("LCscooba", "SPdog", 1)],
    )
    conn.execute("INSERT INTO species_aliases VALUES ('SPzombie', 'Zombies', 0)")
    conn.execute("INSERT INTO npc_epithets VALUES ('LCscooba', 'the Deckhand', 'epithet', 0)")
    conn.execute("PRAGMA user_version = 18")
    conn.commit()


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def test_upgrade_renames_all_four_tables() -> None:
    conn = _conn()
    _build_version_18_kind_tables(conn)
    migrate(conn)

    tables = _tables(conn)
    assert {"kinds", "character_kinds", "kind_aliases", "character_epithets"} <= tables
    assert not {"species", "npc_species", "species_aliases", "npc_epithets"} & tables


def test_upgrade_carries_every_row() -> None:
    conn = _conn()
    _build_version_18_kind_tables(conn)
    migrate(conn)

    assert conn.execute("SELECT COUNT(*) FROM kinds").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM character_kinds").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM kind_aliases").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM character_epithets").fetchone()[0] == 1
    # Scooba is a Zombie and a Dog, in that declared order.
    ordered = [
        r[0]
        for r in conn.execute(
            "SELECT k.name FROM character_kinds ck JOIN kinds k USING(kind_id) "
            "WHERE ck.character_id = 'LCscooba' ORDER BY ck.sort_order"
        )
    ]
    assert ordered == ["Zombie", "Dog"]
    assert conn.execute("SELECT notes FROM kinds WHERE kind_id='SPdog'").fetchone()[0] == "A good one."


def test_upgrade_renames_the_column_but_never_the_id_prefix() -> None:
    """`SP` is part of every stored id, so the prefix must survive the rename."""
    conn = _conn()
    _build_version_18_kind_tables(conn)
    migrate(conn)

    for table in ("kinds", "character_kinds", "kind_aliases"):
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        assert "kind_id" in cols, table
        assert "species_id" not in cols, table
    assert [r[0] for r in conn.execute("SELECT kind_id FROM kinds ORDER BY kind_id")] == ["SPdog", "SPzombie"]


def test_a_from_scratch_build_keeps_one_set_of_tables() -> None:
    """_V1_DDL makes the new names; blocks 10 and 11 re-make the old ones empty.

    The fold-and-drop branch exists for exactly this, and dropping the wrong
    side of it is silent — the tables simply are not there when seeding runs.
    """
    conn = _conn()
    apply_schema(conn)
    migrate(conn)

    tables = _tables(conn)
    assert {"kinds", "character_kinds", "kind_aliases", "character_epithets"} <= tables
    assert not {"species", "npc_species", "species_aliases", "npc_epithets"} & tables
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


def test_foreign_keys_are_enforced_again_afterwards() -> None:
    """The fold turns enforcement off; leaving it off would silence every later check."""
    conn = _conn()
    _build_version_18_kind_tables(conn)
    migrate(conn)

    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert list(conn.execute("PRAGMA foreign_key_check")) == []
