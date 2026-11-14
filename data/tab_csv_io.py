"""Tab-separated text helpers for reading upstream CSV-style exports."""

from __future__ import annotations

import csv
from pathlib import Path


def read_tab_csv(path: Path) -> list[dict[str, str]]:
    """Read a tab-delimited file into row dicts.

    Args:
        path: Any tab-separated table with a header row (e.g. exported ``card.csv``,
            ``card-printing.csv``, ``set.csv``).

    Returns:
        List of dict rows keyed by header cells; empty list if ``path`` is missing.
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file, delimiter="\t"))
