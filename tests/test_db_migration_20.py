"""Tests for migration 20: the non-character `kind` columns get their own names.

`kind` carried four unrelated meanings on this schema. Sense 1 — what a
character *is* (``character_kinds`` / ``kinds``) — is the real, intrinsic
sense and keeps the name. The other three are renamed so `kind` means only
that from here on:

- ``groups.kind`` (what body a group is — clan, house, guild, order) -> ``groups.category``
- ``character_epithets.kind`` (epithet or short-name) -> ``character_epithets.label``

``food_and_drink`` carries no ``kind`` column on disk — its column has always
been ``type`` — so this migration does not touch it; only the Python-side
``FoodDrinkEntry.kind`` attribute is renamed (to ``form``), which is not a
schema change.

Same seam as ``tests/test_db_migration_19.py`` — a raw ``sqlite3.Connection``
plus ``db._schema.migrate()``, never ``Database``.
"""

from __future__ import annotations

import sqlite3

from db._schema import CURRENT_VERSION, apply_schema, migrate


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _build_version_19_tables(conn: sqlite3.Connection) -> None:
    """``groups`` and ``character_epithets`` as they stood at version 19."""
    conn.executescript(
        """
        CREATE TABLE characters (
            character_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unknown'
        );
        CREATE TABLE groups (
            group_id        TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            kind            TEXT NOT NULL DEFAULT '',
            notes           TEXT NOT NULL DEFAULT '',
            parent_group_id TEXT NOT NULL DEFAULT '',
            location_id     TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE character_epithets (
            character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
            name         TEXT NOT NULL,
            kind         TEXT NOT NULL DEFAULT 'epithet',
            sort_order   INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (character_id, name)
        );
        """
    )
    conn.execute("INSERT INTO characters (character_id, name) VALUES ('LCbellona', 'Bellona')")
    conn.execute("INSERT INTO groups VALUES ('GRvangeld', 'VanGeld', 'clan', '', '', '')")
    conn.execute("INSERT INTO character_epithets VALUES ('LCbellona', 'the Wartune Herald', 'epithet', 0)")
    conn.execute("INSERT INTO character_epithets VALUES ('LCbellona', 'Archangel of War', 'short-name', 1)")
    conn.execute("PRAGMA user_version = 19")
    conn.commit()


def test_upgrade_renames_groups_kind_to_category() -> None:
    conn = _conn()
    _build_version_19_tables(conn)
    migrate(conn)

    cols = {r[1] for r in conn.execute("PRAGMA table_info(groups)")}
    assert "category" in cols
    assert "kind" not in cols


def test_upgrade_renames_character_epithets_kind_to_label() -> None:
    conn = _conn()
    _build_version_19_tables(conn)
    migrate(conn)

    cols = {r[1] for r in conn.execute("PRAGMA table_info(character_epithets)")}
    assert "label" in cols
    assert "kind" not in cols


def test_upgrade_carries_every_row_and_value() -> None:
    conn = _conn()
    _build_version_19_tables(conn)
    migrate(conn)

    assert conn.execute("SELECT category FROM groups WHERE group_id='GRvangeld'").fetchone()[0] == "clan"
    assert conn.execute("SELECT COUNT(*) FROM character_epithets").fetchone()[0] == 2
    ordered = [
        r[0]
        for r in conn.execute("SELECT label FROM character_epithets WHERE character_id='LCbellona' ORDER BY sort_order")
    ]
    assert ordered == ["epithet", "short-name"]


def test_a_from_scratch_build_lands_on_the_new_columns() -> None:
    conn = _conn()
    apply_schema(conn)
    migrate(conn)

    group_cols = {r[1] for r in conn.execute("PRAGMA table_info(groups)")}
    epithet_cols = {r[1] for r in conn.execute("PRAGMA table_info(character_epithets)")}
    assert "category" in group_cols
    assert "kind" not in group_cols
    assert "label" in epithet_cols
    assert "kind" not in epithet_cols
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


def test_foreign_keys_are_enforced_and_clean_afterwards() -> None:
    conn = _conn()
    _build_version_19_tables(conn)
    migrate(conn)

    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert list(conn.execute("PRAGMA foreign_key_check")) == []
