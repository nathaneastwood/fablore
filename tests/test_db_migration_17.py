"""Tests for migration 17: story_npcs + story_heroes merge into story_characters.

Seam: raw ``sqlite3.Connection`` + ``db._schema.migrate()``, not ``Database`` —
the trap this migration has to survive is specifically that
``Database.__init__`` runs every pending migration before it ever seeds
(``open_db`` calls ``migrate()``; seeding happens afterwards, only if
``_needs_seed()``), so ``character_heroes`` is empty throughout a multi-version
jump. Going through ``Database`` would seed in between and hide exactly that.

Two starting points are exercised, for the reason the module docstring on this
stage's task gives: "a previous stage nearly shipped a migration that was
correct only from one starting version."

- version 11: the real historical shape just before migration 12's identity
  spine — no ``character_heroes`` table at all yet. This is the trap's exact
  precondition, and it is the one that can carry real fragment data, since the
  ``fragment`` column has existed on both old junctions since migration 4.
- version 1: a from-scratch build using the *current* ``apply_schema()``,
  which already creates ``story_characters`` directly and never creates
  ``story_npcs``/``story_heroes`` at all. There is nothing to preserve on this
  path (a fresh build starts empty) — what this proves is that migrations 2
  through 17 do not error when those two tables never existed, which is
  exactly the case migration 4's guard (see _schema.py) exists for.
"""

from __future__ import annotations

import sqlite3

import pytest

from db._schema import CURRENT_VERSION, apply_schema, migrate
from registry_ids import canonical_id as _canonical_id, lore_character_id


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _build_version_11_schema(conn: sqlite3.Connection) -> None:
    """Recreate the historical shape at version 11 (pre identity-spine).

    Only the tables migrations 12-17 actually touch: stories, npcs (not yet
    renamed to characters), heroes_canonical, story_heroes and story_npcs
    (both already carrying fragment, added by migration 4). No
    character_heroes table — it does not exist until migration 12.
    """
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
        """
    )
    conn.execute("PRAGMA user_version = 11")
    conn.commit()


def test_migrate_from_version_11_preserves_hero_and_npc_fragments() -> None:
    """The trap: character_heroes is empty when this migration runs from v11."""
    conn = _conn()
    _build_version_11_schema(conn)

    conn.execute(
        "INSERT INTO stories (story_id, story_key, story_type, title) VALUES ('ST1', 'main-story/a.md', 'main-story', 'A')"
    )
    conn.execute(
        "INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero) VALUES ('CN1', 'dash', 'Dash')"
    )
    conn.execute("INSERT INTO story_heroes (story_id, canonical_id, fragment) VALUES ('ST1', 'CN1', 'dash-anchor')")

    conn.execute("INSERT INTO npcs (character_id, name, status) VALUES ('LCguard', 'Guard Captain', 'Alive')")
    conn.execute("INSERT INTO story_npcs (story_id, character_id, fragment) VALUES ('ST1', 'LCguard', '')")

    migrate(conn)

    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "story_characters" in tables
    assert "story_heroes" not in tables
    assert "story_npcs" not in tables

    # The hero link survived, with its fragment, via a minted character_heroes
    # row (character_heroes was empty throughout, per the trap).
    dash_character_id = conn.execute("SELECT character_id FROM character_heroes WHERE canonical_id = 'CN1'").fetchone()[
        0
    ]
    assert dash_character_id == lore_character_id("Dash")
    row = conn.execute(
        "SELECT fragment FROM story_characters WHERE story_id = 'ST1' AND character_id = ?",
        [dash_character_id],
    ).fetchone()
    assert row is not None, "hero story link did not survive the migration"
    assert row["fragment"] == "dash-anchor"

    # The NPC link survived too.
    row = conn.execute(
        "SELECT fragment FROM story_characters WHERE story_id = 'ST1' AND character_id = 'LCguard'"
    ).fetchone()
    assert row is not None, "npc story link did not survive the migration"
    assert row["fragment"] == ""

    # Two distinct people -> two distinct rows.
    count = conn.execute("SELECT COUNT(*) FROM story_characters WHERE story_id = 'ST1'").fetchone()[0]
    assert count == 2


def test_migrate_from_version_11_collapses_a_person_named_on_both_sides() -> None:
    """A hero and an ordinary character that are the same person collapse to one row.

    Simulates the real-world shape this merge exists for: an NPC row whose
    name coincides with a hero's canonical name (the pre-migration-12
    databases had no identity link at all, so this is the only way the two
    sides could already name the same person at this point in history).
    lore_character_id hashes the normalised name, so the NPC row and the
    character migration 17 mints for the hero are the *same* row.
    """
    conn = _conn()
    _build_version_11_schema(conn)

    conn.execute(
        "INSERT INTO stories (story_id, story_key, story_type, title) VALUES ('ST1', 'main-story/a.md', 'main-story', 'A')"
    )
    conn.execute(
        "INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero) VALUES ('CN1', 'boltyn', 'Boltyn')"
    )
    conn.execute("INSERT INTO story_heroes (story_id, canonical_id, fragment) VALUES ('ST1', 'CN1', 'hero-anchor')")

    shared_id = lore_character_id("Boltyn")
    conn.execute("INSERT INTO npcs (character_id, name, status) VALUES (?, 'Boltyn', 'Alive')", [shared_id])
    conn.execute("INSERT INTO story_npcs (story_id, character_id, fragment) VALUES ('ST1', ?, '')", [shared_id])

    migrate(conn)

    rows = conn.execute("SELECT character_id, fragment FROM story_characters WHERE story_id = 'ST1'").fetchall()
    assert len(rows) == 1, "hero and ordinary-character sides of the same person did not collapse to one row"
    assert rows[0]["character_id"] == shared_id
    # story_heroes wins the tie per the migration's documented tie-break.
    assert rows[0]["fragment"] == "hero-anchor"


def test_migrate_from_version_1_from_scratch_build_reaches_17_cleanly() -> None:
    """A from-scratch build (apply_schema, then migrate) never had story_heroes
    or story_npcs at all — proves migrations 2-17 do not error on that path
    (migration 4's guard specifically exists for this)."""
    conn = _conn()
    apply_schema(conn)
    conn.execute("PRAGMA user_version = 1")
    conn.commit()

    migrate(conn)

    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "story_characters" in tables
    assert "story_heroes" not in tables
    assert "story_npcs" not in tables


def test_migrate_from_version_11_hero_with_no_npc_row_still_mints_identity() -> None:
    """A hero with no matching character row at all still gets a character + link."""
    conn = _conn()
    _build_version_11_schema(conn)
    conn.execute(
        "INSERT INTO stories (story_id, story_key, story_type, title) VALUES ('ST1', 'main-story/a.md', 'main-story', 'A')"
    )
    conn.execute(
        "INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero) VALUES " "('CN2', 'kano', 'Kano')"
    )
    conn.execute("INSERT INTO story_heroes (story_id, canonical_id, fragment) VALUES ('ST1', 'CN2', '')")

    migrate(conn)

    linked = conn.execute("SELECT character_id FROM character_heroes WHERE canonical_id = 'CN2'").fetchone()
    assert linked is not None
    cid = linked["character_id"]
    assert cid == lore_character_id("Kano")
    assert conn.execute("SELECT COUNT(*) FROM characters WHERE character_id = ?", [cid]).fetchone()[0] == 1
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM story_characters WHERE story_id = 'ST1' AND character_id = ?", [cid]
        ).fetchone()[0]
        == 1
    )


def test_canonical_id_helper_is_available() -> None:
    """Sanity check the import used to build heroes_canonical rows above."""
    assert _canonical_id("dash") != _canonical_id("boltyn")


@pytest.mark.parametrize("bad_start", [11])
def test_migrate_is_idempotent_when_called_twice(bad_start: int) -> None:
    """Calling migrate() again on an already-migrated db is a no-op, not an error."""
    conn = _conn()
    _build_version_11_schema(conn)
    migrate(conn)
    migrate(conn)  # second call must not raise (tables already exist / dropped)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION
