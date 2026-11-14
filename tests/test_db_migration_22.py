"""Tests for migration 22: ``heroes_printings`` is keyed on the printing, not the card.

Until version 22 the table was keyed on ``(hero_game_id, set_id, card_id)``, so
EVR017's standard, cold-foil and full-art printings were one row and the card
image for each (served by its printing unique id) had nowhere to come from.
The table is rebuilt with ``printing_unique_id``, ``foiling``,
``art_variation`` and ``artist``, keyed on ``(hero_game_id,
printing_unique_id)``. The old rows carry no printing id to recover, so the
table is left empty and the reseed repopulates it — migration 7's shape.

Same seam as ``tests/test_db_migration_20.py`` — a raw ``sqlite3.Connection``
plus ``db._schema.migrate()``, never ``Database``.
"""

from __future__ import annotations

import sqlite3

from db._schema import CURRENT_VERSION, migrate


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _build_version_21_heroes_printings(conn: sqlite3.Connection) -> None:
    """``heroes_printings`` as it stood at version 21, holding Bravo's one EVR017 row."""
    conn.executescript(
        """
        CREATE TABLE heroes_game (hero_game_id TEXT PRIMARY KEY, card_name TEXT NOT NULL);
        CREATE TABLE heroes_printings (
            hero_game_id TEXT NOT NULL REFERENCES heroes_game(hero_game_id) ON DELETE CASCADE,
            set_id       TEXT NOT NULL,
            card_id      TEXT NOT NULL,
            rarity       TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (hero_game_id, set_id, card_id)
        );
        """
    )
    conn.execute("INSERT INTO heroes_game VALUES ('HG871c3ec849', 'Bravo, Star of the Show')")
    conn.execute("INSERT INTO heroes_printings VALUES ('HG871c3ec849', 'EVR', 'EVR017', 'M')")
    conn.execute("PRAGMA user_version = 21")
    conn.commit()


def test_upgrade_keys_heroes_printings_on_the_printing_id() -> None:
    conn = _conn()
    _build_version_21_heroes_printings(conn)
    migrate(conn)

    info = {r["name"]: r["pk"] for r in conn.execute("PRAGMA table_info(heroes_printings)")}
    assert {"printing_unique_id", "foiling", "art_variation", "artist"} <= set(info)
    assert sorted((pk, name) for name, pk in info.items() if pk) == [
        (1, "hero_game_id"),
        (2, "printing_unique_id"),
    ]
    assert conn.execute("PRAGMA user_version").fetchone()[0] >= 22


def test_upgrade_holds_three_printings_of_one_card_id() -> None:
    conn = _conn()
    _build_version_21_heroes_printings(conn)
    migrate(conn)

    for printing_id, foiling, art in (
        ("FKC8qdBgdwgfrLmkq8htq", "S", ""),
        ("DFjQGNbTkNqjWhJPFL78C", "C", ""),
        ("nRMnPD6nnmCpFf7WkwTN7", "C", "FA"),
    ):
        conn.execute(
            "INSERT INTO heroes_printings"
            " (hero_game_id, set_id, card_id, rarity, printing_unique_id, foiling, art_variation, artist)"
            " VALUES ('HG871c3ec849', 'EVR', 'EVR017', 'M', ?, ?, ?, 'Marco Wulfr')",
            (printing_id, foiling, art),
        )
    assert conn.execute("SELECT COUNT(*) FROM heroes_printings WHERE card_id = 'EVR017'").fetchone()[0] == 3
