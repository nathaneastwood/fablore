"""Generate weapon registry CSVs from the upstream ``card.csv`` export.

Writes pipe-delimited outputs:

1. ``weapons-canonical.csv`` — one row per canonical weapon (slug from full printed ``Name``)
2. ``weapons-game.csv`` — one row per weapon card line (``Types`` contains ``weapon``)
3. Refreshes shared ``classes.csv`` / ``talents.csv`` from the full upstream ``card.csv``
   (hero + weapon + non-weapon equipment ``Types``; see :mod:`game_class_talent_csv`)
4. ``weapons-printings.csv`` — one row per set printing per game row

A card is treated as a **weapon** card if any comma-separated ``Types`` token matches
``\\bweapon\\b`` (case-insensitive), e.g. ``Weapon``, ``2H Weapon``, ``1H Weapon``.

The generation itself is shared with ``create_equipment_csv.py``; see
:mod:`card_registry_csv`. When run as a script, generation is followed by
``validate_data.py``. Each output CSV starts with an auto-generation ``#`` banner
(see :mod:`pipe_csv_io`).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_registry_csv import CardRegistrySpec, generate_card_registry_csvs  # noqa: E402
from card_types_extract import (  # noqa: E402
    extract_weapon_classes_and_talents,
    types_include_weapon,
)
from generator_utils import run_validate_data_and_exit  # noqa: E402
from pipe_csv_io import REGENERATE_CREATE_WEAPONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WEAPONS_CANONICAL_CSV_PATH = ROOT / "src/data/csv/weapons-canonical.csv"
WEAPONS_GAME_CSV_PATH = ROOT / "src/data/csv/weapons-game.csv"
WEAPONS_PRINTINGS_CSV_PATH = ROOT / "src/data/csv/weapons-printings.csv"


def generate_weapons_csv() -> None:
    """Regenerate weapon-related pipe CSVs from ``card.csv`` + ``card-printing.csv``.

    Refreshes shared ``classes.csv`` / ``talents.csv`` from the full ``card.csv`` scan
    (same class/talent union as all card generators), not weapon rows only.

    Raises:
        FileNotFoundError: If no weapon rows exist in the upstream card CSV.
        ValueError: On id hash collisions in canonical or game rows.
    """
    generate_card_registry_csvs(
        CardRegistrySpec(
            noun="Weapon",
            includes_card=types_include_weapon,
            extract_classes_and_talents=extract_weapon_classes_and_talents,
            stat_column="Power",
            canonical_id_prefix="CW",
            game_id_prefix="WG",
            canonical_csv_path=WEAPONS_CANONICAL_CSV_PATH,
            game_csv_path=WEAPONS_GAME_CSV_PATH,
            printings_csv_path=WEAPONS_PRINTINGS_CSV_PATH,
            regenerate_command=REGENERATE_CREATE_WEAPONS,
            missing_cards_hint="``Types`` containing a *weapon* token (e.g. ``Weapon``, ``2H Weapon``).",
        )
    )


if __name__ == "__main__":
    generate_weapons_csv()
    run_validate_data_and_exit()
