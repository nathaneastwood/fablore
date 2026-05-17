"""Regenerate shared ``classes.csv`` and ``talents.csv`` from upstream ``card.csv``.

Builds the union of class and talent display names from hero, weapon, and
non-weapon equipment rows (same rules as
:func:`game_class_talent_csv.merge_classes_and_talents_from_card_rows`).
Card generators call that helper automatically; this script refreshes the two
reference tables alone.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from game_class_talent_csv import (  # noqa: E402
    UPSTREAM_CARD_CSV_PATH,
    merge_classes_and_talents_from_card_rows,
)
from registry_ids import make_hash_id  # noqa: E402
from tab_csv_io import read_tab_csv  # noqa: E402
from text_utils import normalize_name  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def generate_classes_talents_csv() -> None:
    """Write ``classes.csv`` and ``talents.csv`` from the card export.

    Raises:
        FileNotFoundError: If ``card.csv`` is missing or empty.
    """
    card_rows = read_tab_csv(UPSTREAM_CARD_CSV_PATH)
    if not card_rows:
        raise FileNotFoundError(f"No rows read from {UPSTREAM_CARD_CSV_PATH}")

    merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )


if __name__ == "__main__":
    generate_classes_talents_csv()
    _vd = Path(__file__).resolve().parent / "validate_data.py"
    _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
    raise SystemExit(_rc.returncode)
