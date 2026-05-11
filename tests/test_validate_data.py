"""Integration checks for :mod:`validate_data`."""

from __future__ import annotations

import validate_data


def test_collect_alerts_empty_when_repository_consistent() -> None:
    """Committed CSVs under ``src/data`` satisfy validation rules."""
    assert validate_data.collect_alerts() == []
