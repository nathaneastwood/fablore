"""Generate equipment registry CSVs from the upstream flesh-and-blood-cards ``card.csv`` export.

Writes pipe-delimited outputs:

1. ``equipment-canonical.csv`` — one row per canonical equipment piece (slug from full printed ``Name``)
2. ``equipment-game.csv`` — one row per equipment card line (``Types`` contains
   *equipment* but not *weapon* — hybrid weapon-equipment cards are listed only in
   weapons outputs)
3. Refreshes shared ``classes.csv`` / ``talents.csv`` from the full upstream ``card.csv``
   (same class/talent union as other generators; see :mod:`game_class_talent_csv`)
4. ``equipment-printings.csv`` — one row per set printing per game row

When run as a script, generation is followed by ``validate_data.py``. Each output CSV
starts with an auto-generation ``#`` banner (see :mod:`pipe_csv_io`).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_name_slug import slugify_card_name_stem
from card_types_extract import (
    dedupe_preserving_order,
    extract_equipment_classes_and_talents,
    is_non_weapon_equipment_card,
    parse_tokens,
)
from create_heroes_csv import make_hash_id, normalize_name
from create_sets_csv import SETS_CSV_PATH, generate_sets_csv
from game_class_talent_csv import (
    UPSTREAM_CARD_CSV_PATH as CARD_CSV_PATH,
)
from game_class_talent_csv import (
    merge_classes_and_talents_from_card_rows,
)
from pipe_csv_io import (
    REGENERATE_CREATE_EQUIPMENT,
    read_pipe_csv,
    write_pipe_csv_autogen,
)
from tab_csv_io import read_tab_csv

ROOT = Path(__file__).resolve().parents[2]
EQUIPMENT_CANONICAL_CSV_PATH = ROOT / "src/data/equipment-canonical.csv"
EQUIPMENT_GAME_CSV_PATH = ROOT / "src/data/equipment-game.csv"
EQUIPMENT_PRINTINGS_CSV_PATH = ROOT / "src/data/equipment-printings.csv"
CARD_PRINTING_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/card-printing.csv"


def generate_equipment_csv() -> None:
    """Regenerate equipment-related pipe CSVs from ``card.csv`` + ``card-printing.csv``.

    Refreshes shared ``classes.csv`` / ``talents.csv`` from the full ``card.csv`` scan.

    Raises:
        FileNotFoundError: If no qualifying equipment rows exist in the upstream CSV.
        ValueError: On id hash collisions in canonical or game rows.
    """
    if not SETS_CSV_PATH.exists():
        generate_sets_csv()

    card_rows = read_tab_csv(CARD_CSV_PATH)
    card_printing_rows = read_tab_csv(CARD_PRINTING_CSV_PATH)

    _, sets_rows = read_pipe_csv(SETS_CSV_PATH)
    set_release_by_identifier: dict[str, str] = {}
    for row in sets_rows:
        set_id = row.get("SetId", "").strip()
        release = row.get("InitialReleaseDate", "").strip()
        if set_id:
            set_release_by_identifier[set_id] = release

    printings_by_card_unique: dict[str, list[dict[str, str]]] = {}
    for row in card_printing_rows:
        card_unique = row.get("Card Unique ID", "")
        if not card_unique:
            continue
        printings_by_card_unique.setdefault(card_unique, []).append(
            {
                "SetId": row.get("Set ID", "").strip(),
                "CardId": row.get("Card ID", "").strip(),
                "Rarity": row.get("Rarity", "").strip(),
            }
        )

    equipment_cards_by_key: dict[str, list[dict[str, str]]] = {}
    for card in card_rows:
        if not is_non_weapon_equipment_card(card.get("Types", "")):
            continue
        full_name = card.get("Name", "").strip()
        if not full_name:
            continue
        slug = slugify_card_name_stem(full_name)
        equipment_cards_by_key.setdefault(slug, []).append(card)

    if not equipment_cards_by_key:
        raise FileNotFoundError(
            f"No equipment cards found. Expected rows in {CARD_CSV_PATH} with "
            "``Types`` containing *equipment* but not *weapon* (slot gear; hybrids "
            "go to weapons CSV)."
        )

    canonical_rows: list[dict[str, str]] = []
    slug_order = sorted(equipment_cards_by_key.keys())
    for slug in slug_order:
        cards = equipment_cards_by_key[slug]
        display = min(c.get("Name", "").strip() for c in cards if c.get("Name", "").strip())
        canonical_rows.append(
            {
                "CanonicalEquipmentId": make_hash_id("CE", slug),
                "CanonicalSlug": slug,
                "CanonicalEquipment": display,
            }
        )

    canonical_id_by_slug = {row["CanonicalSlug"]: row["CanonicalEquipmentId"] for row in canonical_rows}
    canonical_ids = [row["CanonicalEquipmentId"] for row in canonical_rows]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("Canonical equipment ID hash collision detected")

    unsorted_rows: list[dict[str, str]] = []
    for slug, cards in equipment_cards_by_key.items():
        canonical_equipment_id = canonical_id_by_slug[slug]
        for card in cards:
            full_name = card.get("Name", "").strip()
            class_names, talent_names = extract_equipment_classes_and_talents(
                card.get("Types", "")
            )
            printings = dedupe_preserving_order(
                [
                    f"{entry['SetId']}|{entry['CardId']}|{entry['Rarity']}"
                    for entry in printings_by_card_unique.get(card.get("Unique ID", ""), [])
                    if entry.get("SetId") and entry.get("CardId")
                ]
            )
            earliest_release = ""
            for entry in printings:
                set_id = entry.split("|", 1)[0]
                release = set_release_by_identifier.get(set_id, "")
                if release and (not earliest_release or release < earliest_release):
                    earliest_release = release

            cost = (card.get("Cost") or "").strip()
            defense = (card.get("Defense") or "").strip()
            ability = (card.get("Functional Text") or "").strip().replace("\n", " ")

            unsorted_rows.append(
                {
                    "SourceCardUniqueId": card.get("Unique ID", "").strip(),
                    "CanonicalEquipmentId": canonical_equipment_id,
                    "CanonicalSlug": slug,
                    "CardName": full_name,
                    "ClassNames": class_names,
                    "TalentNames": talent_names,
                    "Cost": cost,
                    "Defense": defense,
                    "AbilityText": ability,
                    "Types": ", ".join(parse_tokens(card.get("Types", ""))),
                    "Printings": printings,
                    "EarliestRelease": earliest_release,
                }
            )

    unsorted_rows.sort(
        key=lambda row: (
            row["EarliestRelease"] or "9999-99-99",
            row["CanonicalSlug"],
            row["CardName"].lower(),
        )
    )

    class_id_by_name, talent_id_by_name = merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    game_rows: list[dict[str, str]] = []
    printings_rows: list[dict[str, str]] = []
    for row in unsorted_rows:
        source_unique = row.get("SourceCardUniqueId", "")
        if not source_unique:
            source_unique = "|".join(
                [
                    row.get("CanonicalSlug", ""),
                    row.get("CardName", ""),
                    row.get("Types", ""),
                    row.get("Cost", ""),
                    row.get("Defense", ""),
                ]
            )
        equipment_game_id = make_hash_id("EG", source_unique)
        class_ids = [class_id_by_name[n] for n in row["ClassNames"] if n in class_id_by_name]
        talent_ids = [talent_id_by_name[n] for n in row["TalentNames"] if n in talent_id_by_name]
        game_rows.append(
            {
                "EquipmentGameId": equipment_game_id,
                "CardName": row["CardName"],
                "CanonicalEquipmentId": row["CanonicalEquipmentId"],
                "ClassIds": ", ".join(class_ids),
                "TalentIds": ", ".join(talent_ids),
                "Cost": row["Cost"],
                "Defense": row["Defense"],
                "AbilityText": row["AbilityText"],
                "Types": row["Types"],
            }
        )
        for entry in row["Printings"]:
            set_id, card_id, rarity = [part.strip() for part in entry.split("|")]
            printings_rows.append(
                {
                    "EquipmentGameId": equipment_game_id,
                    "SetId": set_id,
                    "CardId": card_id,
                    "Rarity": rarity,
                }
            )

    equipment_game_ids = [r["EquipmentGameId"] for r in game_rows]
    if len(equipment_game_ids) != len(set(equipment_game_ids)):
        raise ValueError("Equipment game ID hash collision detected")

    canonical_fieldnames = ["CanonicalEquipmentId", "CanonicalSlug", "CanonicalEquipment"]
    game_fieldnames = [
        "EquipmentGameId",
        "CardName",
        "CanonicalEquipmentId",
        "ClassIds",
        "TalentIds",
        "Cost",
        "Defense",
        "AbilityText",
        "Types",
    ]
    printings_fieldnames = ["EquipmentGameId", "SetId", "CardId", "Rarity"]

    for path, fieldnames, rows in [
        (EQUIPMENT_CANONICAL_CSV_PATH, canonical_fieldnames, canonical_rows),
        (EQUIPMENT_GAME_CSV_PATH, game_fieldnames, game_rows),
        (EQUIPMENT_PRINTINGS_CSV_PATH, printings_fieldnames, printings_rows),
    ]:
        write_pipe_csv_autogen(
            path,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_CREATE_EQUIPMENT,
        )


if __name__ == "__main__":
    generate_equipment_csv()
    _vd = Path(__file__).resolve().parent / "validate_data.py"
    _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
    raise SystemExit(_rc.returncode)
