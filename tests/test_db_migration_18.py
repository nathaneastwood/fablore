"""Tests for migration 18: group_npcs + group_heroes merge into group_characters.

Same seam and the same reasoning as ``tests/test_db_migration_17.py`` — a raw
``sqlite3.Connection`` plus ``db._schema.migrate()``, never ``Database``,
because the trap is that ``Database.__init__`` runs every pending migration
before it ever seeds. ``character_heroes`` is therefore empty for the whole
multi-version jump, and a migration that resolved ``group_heroes.canonical_id``
through it would drop every hero membership in silence.

Migration 17 running first does **not** solve this. It mints an identity link
for every hero that had a *story* row; a hero with a group row and no story row
still has none when 18 runs, and the fixture below is exactly that case.
"""

from __future__ import annotations

import sqlite3

from db._schema import CURRENT_VERSION, apply_schema, migrate
from registry_ids import lore_character_id


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _build_version_11_schema(conn: sqlite3.Connection) -> None:
    """The historical shape at version 11, groups half included."""
    conn.executescript(
        """
        CREATE TABLE stories (
            story_id TEXT PRIMARY KEY,
            story_key TEXT UNIQUE NOT NULL,
            story_type TEXT NOT NULL,
            title TEXT NOT NULL,
            authors TEXT NOT NULL DEFAULT '',
            artists TEXT NOT NULL DEFAULT '',
            source_link TEXT NOT NULL DEFAULT '',
            publication_date TEXT NOT NULL DEFAULT '',
            thumbnail_image_link TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE npcs (
            character_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unknown',
            other_characters_story_key TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE heroes_canonical (
            canonical_id TEXT PRIMARY KEY,
            canonical_slug TEXT UNIQUE NOT NULL,
            canonical_hero TEXT NOT NULL
        );
        CREATE TABLE story_heroes (
            story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
            canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
            fragment TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (story_id, canonical_id)
        );
        CREATE TABLE story_npcs (
            story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
            character_id TEXT NOT NULL REFERENCES npcs(character_id),
            fragment TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (story_id, character_id)
        );
        CREATE TABLE groups (
            group_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            parent_group_id TEXT NOT NULL DEFAULT '',
            location_id TEXT NOT NULL DEFAULT '',
            lore_story_key TEXT NOT NULL DEFAULT '',
            lore_fragment TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE group_npcs (
            group_id TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
            character_id TEXT NOT NULL REFERENCES npcs(character_id),
            story_key TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (group_id, character_id)
        );
        CREATE TABLE group_heroes (
            group_id TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
            canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
            story_key TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (group_id, canonical_id)
        );
        """
    )
    conn.execute("PRAGMA user_version = 11")
    conn.commit()


def test_migrate_from_version_11_preserves_both_kinds_of_member() -> None:
    """The trap: character_heroes is empty when this migration runs from v11.

    Kayo is deliberately given a group row and **no** story row, so migration
    17 mints nothing for him and migration 18 has to mint the link itself.
    """
    conn = _conn()
    _build_version_11_schema(conn)

    conn.execute(
        "INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero) VALUES ('CN1', 'kayo', 'Kayo')"
    )
    conn.execute("INSERT INTO npcs (character_id, name, status) VALUES ('LCtara', 'Tara VanGeld', 'Alive')")
    conn.execute("INSERT INTO groups (group_id, name, kind) VALUES ('GR1', 'Prowlers', 'guild')")
    conn.execute("INSERT INTO group_heroes (group_id, canonical_id, story_key) VALUES ('GR1', 'CN1', 'a.md')")
    conn.execute("INSERT INTO group_npcs (group_id, character_id, story_key) VALUES ('GR1', 'LCtara', 'b.md')")

    migrate(conn)

    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "group_characters" in tables
    assert "group_npcs" not in tables
    assert "group_heroes" not in tables

    kayo_character_id = conn.execute("SELECT character_id FROM character_heroes WHERE canonical_id = 'CN1'").fetchone()[
        0
    ]
    assert kayo_character_id == lore_character_id("Kayo")

    rows = {
        r["character_id"]: r["story_key"]
        for r in conn.execute("SELECT character_id, story_key FROM group_characters WHERE group_id = 'GR1'")
    }
    assert rows == {kayo_character_id: "a.md", "LCtara": "b.md"}


def test_a_cited_membership_beats_an_uncited_one_whichever_side_carries_it() -> None:
    """One person named on both sides collapses to one row, keeping the citation.

    Not a shape the committed CSVs contain — no group names anybody twice — but
    a database whose rows did not come from those CSVs must not lose the
    evidence column to an empty duplicate.
    """
    conn = _conn()
    _build_version_11_schema(conn)

    conn.execute(
        "INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero) VALUES ('CN1', 'kano', 'Kano')"
    )
    # The character row *is* the hero's character row: same name, so same hash.
    conn.execute(
        "INSERT INTO npcs (character_id, name, status) VALUES (?, 'Kano', 'Alive')",
        [lore_character_id("Kano")],
    )
    conn.execute("INSERT INTO groups (group_id, name, kind) VALUES ('GR1', 'Lord Wizards', 'council')")
    conn.execute(
        "INSERT INTO group_npcs (group_id, character_id, story_key) VALUES ('GR1', ?, '')",
        [lore_character_id("Kano")],
    )
    conn.execute("INSERT INTO group_heroes (group_id, canonical_id, story_key) VALUES ('GR1', 'CN1', 'kano-about.md')")

    migrate(conn)

    rows = list(conn.execute("SELECT character_id, story_key FROM group_characters WHERE group_id = 'GR1'"))
    assert len(rows) == 1
    assert rows[0]["character_id"] == lore_character_id("Kano")
    assert rows[0]["story_key"] == "kano-about.md"


def test_migrate_from_version_1_from_scratch_build_reaches_18_cleanly() -> None:
    """A fresh build never creates group_npcs/group_heroes, so 18 has nothing to move."""
    conn = _conn()
    apply_schema(conn)
    conn.execute("PRAGMA user_version = 1")
    conn.commit()

    migrate(conn)

    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "group_characters" in tables
    assert not {"group_npcs", "group_heroes"} & tables


def test_migration_is_idempotent() -> None:
    conn = _conn()
    _build_version_11_schema(conn)
    conn.execute("INSERT INTO groups (group_id, name, kind) VALUES ('GR1', 'Prowlers', 'guild')")
    conn.execute("INSERT INTO npcs (character_id, name) VALUES ('LCtara', 'Tara VanGeld')")
    conn.execute("INSERT INTO group_npcs (group_id, character_id, story_key) VALUES ('GR1', 'LCtara', 'b.md')")

    migrate(conn)
    before = list(conn.execute("SELECT * FROM group_characters"))
    migrate(conn)
    assert list(conn.execute("SELECT * FROM group_characters")) == before
