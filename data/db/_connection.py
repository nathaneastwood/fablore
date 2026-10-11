"""SQLite connection factory for the fablore database.

Opens the database at ``path``, enables foreign keys, and applies schema
migrations. All callers should go through :func:`open_db`; never call
``sqlite3.connect`` directly so FK enforcement is always present.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from db._schema import migrate


def open_db(path: str | Path) -> sqlite3.Connection:
    """Return a connection with FK enforcement and current schema applied.

    Args:
        path: Filesystem path for the database file, or ``":memory:"`` for
            an in-process test database.

    Returns:
        Open :class:`sqlite3.Connection` with ``row_factory`` set to
        :class:`sqlite3.Row` so columns are accessible by name.
    """
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn
