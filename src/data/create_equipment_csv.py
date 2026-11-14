"""Generate equipment registry CSVs from the upstream flesh-and-blood-cards ``card.csv`` export.

Writes pipe-delimited outputs:

1. ``equipment-canonical.csv`` — one row per canonical equipment piece (slug from full printed ``Name``)
2. ``equipment-game.csv`` — one row per equipment card line (``Types`` contains
   *equipment* but not *weapon* — hybrid weapon-equipment cards are listed only in
   weapons outputs)
3. Refreshes shared ``classes.csv`` / ``talents.csv`` from the full upstream ``card.csv``
   (same class/talent union as other generators; see :mod:`game_class_talent_csv`)
4. ``equipment-printings.csv`` — one row per set printing per game row

The generation itself is shared with ``create_weapons_csv.py``; see
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
    extract_equipment_classes_and_talents,
    is_non_weapon_equipment_card,
)
from generator_utils import run_validate_data_and_exit  # noqa: E402
from pipe_csv_io import REGENERATE_CREATE_EQUIPMENT  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EQUIPMENT_CANONICAL_CSV_PATH = ROOT / "src/data/csv/equipment-canonical.csv"
EQUIPMENT_GAME_CSV_PATH = ROOT / "src/data/csv/equipment-game.csv"
EQUIPMENT_PRINTINGS_CSV_PATH = ROOT / "src/data/csv/equipment-printings.csv"


def generate_equipment_csv() -> None:
    """Regenerate equipment-related pipe CSVs from ``card.csv`` + ``card-printing.csv``.

    Refreshes shared ``classes.csv`` / ``talents.csv`` from the full ``card.csv`` scan.

    Raises:
        FileNotFoundError: If no qualifying equipment rows exist in the upstream CSV.
        ValueError: On id hash collisions in canonical or game rows.
    """
    generate_card_registry_csvs(
        CardRegistrySpec(
            noun="Equipment",
            includes_card=is_non_weapon_equipment_card,
            extract_classes_and_talents=extract_equipment_classes_and_talents,
            stat_column="Defense",
            canonical_id_prefix="CE",
            game_id_prefix="EG",
            canonical_csv_path=EQUIPMENT_CANONICAL_CSV_PATH,
            game_csv_path=EQUIPMENT_GAME_CSV_PATH,
            printings_csv_path=EQUIPMENT_PRINTINGS_CSV_PATH,
            regenerate_command=REGENERATE_CREATE_EQUIPMENT,
            missing_cards_hint=(
                "``Types`` containing *equipment* but not *weapon* (slot gear; hybrids go to weapons CSV)."
            ),
        )
    )


if __name__ == "__main__":
    generate_equipment_csv()
    run_validate_data_and_exit()
