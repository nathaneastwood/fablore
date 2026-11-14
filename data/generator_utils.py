"""Small stdlib-only helpers shared by the ``create_*.py`` generators.

- :func:`write_text_if_changed` — leave an output's mtime alone when its contents
  would not change, so ``mdbook serve`` does not rebuild for a no-op regeneration.
- :func:`run_validate_data_and_exit` — the ``validate_data.py`` tail every CSV
  generator runs from ``__main__``.
- :func:`md_table` / :func:`write_db_markdown` — the database-driven markdown
  pages (``create_character_groups_md.py``, ``create_character_kin_md.py``).
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Callable, NoReturn

_DATA_DIR = Path(__file__).resolve().parent
_ROOT = _DATA_DIR.parents[1]


def write_text_if_changed(path: Path, text: str) -> bool:
    """Write ``text`` to ``path`` (UTF-8) only when it differs; return True if written."""
    try:
        existing = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    if existing == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def run_validate_data_and_exit() -> NoReturn:
    """Run ``validate_data.py`` from the repo root and exit with its return code."""
    result = subprocess.run([sys.executable, str(_DATA_DIR / "validate_data.py")], cwd=str(_ROOT))
    raise SystemExit(result.returncode)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a minimal GFM pipe table — no external padding library.

    A ``|`` inside a header or cell is escaped as ``\\|`` so it stays one cell.
    """

    def _row(cells: list[str]) -> str:
        return "| " + " | ".join(c.replace("|", r"\|") for c in cells) + " |"

    lines = [_row(headers), "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend(_row(row) for row in rows)
    return "\n".join(lines)


def write_db_markdown(
    render: Callable[[sqlite3.Connection], str],
    output_md: Path,
    banner: str,
    db_path: Path,
) -> None:
    """Render a markdown page from ``fablore.db`` and write ``banner + text`` to ``output_md``.

    Opens the database through :class:`db.Database`, not a bare ``sqlite3``
    connection — the DB is a runtime artefact seeded from the CSVs on first open,
    so this works on a fresh clone where ``fablore.db`` does not exist yet.
    """
    from db import Database

    database = Database(db_path)
    try:
        text = render(database.conn)
    finally:
        database.conn.close()
    write_text_if_changed(Path(output_md), banner + text)
