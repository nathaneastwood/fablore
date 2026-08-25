"""Tests for the seed-trigger table list in ``db._seed``.

Auto-seeding (``Database.__init__`` calling ``seed_from_csvs`` when the
database is empty, or when a migration has emptied a derived game-data
table only the CSVs can repopulate) used to decide *whether* to seed with a
hardcoded table list living in ``db._domain``, next to nothing else about
seeding. That knowledge belongs beside ``seed_from_csvs`` itself, so a
future migration that adds a table to the trigger list edits ``db._seed``,
not the domain layer.
"""

from __future__ import annotations

import sqlite3

import pytest

from db._domain import DATA
from db._schema import apply_schema, migrate
from db._seed import needs_seed, seed_from_csvs


def _fresh_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn)
    migrate(conn)
    return conn


def test_needs_seed_lives_in_the_seed_module() -> None:
    """The function the task moved — importable from db._seed, not db._domain."""
    import db._domain as _domain

    assert not hasattr(_domain, "_needs_seed_tables")
    assert callable(needs_seed)


def test_needs_seed_is_true_on_a_freshly_migrated_schema() -> None:
    conn = _fresh_conn()
    assert needs_seed(conn) is True


def test_needs_seed_is_false_once_seeded_from_the_committed_csvs() -> None:
    """Mirrors real startup: apply_schema() then seed_from_csvs() against the
    actual committed CSVs, which populate every trigger table."""
    conn = _fresh_conn()
    seed_from_csvs(conn, DATA)
    assert needs_seed(conn) is False


@pytest.mark.parametrize("table", ["stories", "equipment_printings", "weapons_printings", "kinds", "character_heroes"])
def test_needs_seed_is_true_when_one_trigger_table_is_empty(table: str) -> None:
    """Migration 7 rebuilds both printings tables to widen their primary key,
    which empties them; migration 19 added kinds and migration 12 added
    character_heroes. Each is independently sufficient to force a reseed."""
    conn = _fresh_conn()
    seed_from_csvs(conn, DATA)
    assert needs_seed(conn) is False
    conn.execute(f"DELETE FROM {table}")
    assert needs_seed(conn) is True
