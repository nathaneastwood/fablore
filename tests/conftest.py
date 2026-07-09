"""Pytest configuration: ensure ``src/data`` is importable as flat modules.

Only adjusts ``sys.path`` (see also ``pythonpath`` in ``pytest.ini``); it does not
write under ``src/data/``. Tests that create CSVs or Markdown use ``tmp_path``
and, where needed, ``monkeypatch`` on module path constants so the working tree
is not modified. The integration test
``test_collect_alerts_empty_when_repository_consistent`` reads the committed
datasets under ``src/data/csv/`` via ``validate_data.collect_alerts()`` only
(assertions, no writes).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))


@pytest.fixture
def db(tmp_path: Path):
    """In-memory Database with schema applied; CSV dir created for write-through exports."""
    (tmp_path / "csv").mkdir()
    from db import Database

    return Database(":memory:", data_dir=tmp_path)
