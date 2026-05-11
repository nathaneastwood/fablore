"""Tests for :mod:`tab_csv_io`."""

from __future__ import annotations

from pathlib import Path

from tab_csv_io import read_tab_csv


def test_read_tab_csv_missing_returns_empty(tmp_path: Path) -> None:
    """Missing files yield an empty list."""
    assert read_tab_csv(tmp_path / "missing.tsv") == []


def test_read_tab_csv_parses_rows(tmp_path: Path) -> None:
    """Tab-separated headers become dict keys."""
    path = tmp_path / "card.tsv"
    path.write_text("A\tB\nx\ty\n", encoding="utf-8")
    rows = read_tab_csv(path)
    assert rows == [{"A": "x", "B": "y"}]
