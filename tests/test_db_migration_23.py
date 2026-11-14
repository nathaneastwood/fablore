"""Tests for migration 23: the ``heroes_ll`` table is dropped.

Migration 5 created ``heroes_ll`` and the seeder filled it from
``heroes-ll.csv``, but nothing ever read it: ``mdbook_hero_meta`` reads the CSV
directly, and no exporter writes it back (``create_heroes_csv.py`` owns the
file). Version 23 drops the table, and the seeder no longer loads it.

Same seam as ``tests/test_db_migration_22.py`` — a raw ``sqlite3.Connection``
plus ``db._schema.migrate()`` — and, for the fresh-seed case, ``Database``
pointed at the committed CSVs.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from db import Database
from db._schema import CURRENT_VERSION, migrate


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _build_version_22_heroes_ll(conn: sqlite3.Connection) -> None:
    """``heroes_ll`` as migration 5 left it, holding one Living Legend row."""
    conn.execute(
        """
        CREATE TABLE heroes_ll (
            canonical_slug TEXT NOT NULL,
            card_name      TEXT NOT NULL,
            format         TEXT NOT NULL,
            date_in_effect TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (card_name, format)
        )
        """
    )
    conn.execute("INSERT INTO heroes_ll VALUES ('bravo', 'Bravo, Showstopper', 'CC', '2022-08-26')")
    conn.execute("PRAGMA user_version = 22")
    conn.commit()


def test_upgrade_from_version_22_drops_heroes_ll() -> None:
    conn = _conn()
    _build_version_22_heroes_ll(conn)
    migrate(conn)

    assert "heroes_ll" not in _tables(conn)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION == 23


def test_a_fresh_seed_has_no_heroes_ll_table(tmp_path: Path) -> None:
    db = Database(tmp_path / "fablore.db")
    try:
        assert "heroes_ll" not in _tables(db.conn)
        assert db.conn.execute("SELECT COUNT(*) FROM heroes_printings").fetchone()[0] > 0
    finally:
        db.conn.close()
