"""Generate weapon registry CSVs from the upstream ``card.csv`` export.

Writes pipe-delimited outputs:

1. ``weapons-canonical.csv`` — one row per canonical weapon (slug from full printed ``Name``)
2. ``weapons-game.csv`` — one row per weapon card line (``Types`` contains ``weapon``)
3. Refreshes shared ``classes.csv`` / ``talents.csv`` from the full upstream ``card.csv``
   (hero + weapon + non-weapon equipment ``Types``; see :mod:`game_class_talent_csv`)
4. ``weapons-printings.csv`` — one row per set printing per game row

A card is treated as a **weapon** card if any comma-separated ``Types`` token matches
``\\bweapon\\b`` (case-insensitive), e.g. ``Weapon``, ``2H Weapon``, ``1H Weapon``.

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

from card_name_slug import slugify_card_name_stem  # noqa: E402
from card_types_extract import (  # noqa: E402
    dedupe_preserving_order,
    extract_weapon_classes_and_talents,
    parse_tokens,
    types_include_weapon,
)
from create_sets_csv import SETS_CSV_PATH, generate_sets_csv  # noqa: E402
from game_class_talent_csv import (  # noqa: E402
    UPSTREAM_CARD_CSV_PATH as CARD_CSV_PATH,
    merge_classes_and_talents_from_card_rows,
)
from pipe_csv_io import (  # noqa: E402
    REGENERATE_CREATE_WEAPONS,
    read_pipe_csv,
    write_pipe_csv_autogen,
)
from registry_ids import assert_unique_ids, make_hash_id  # noqa: E402
from tab_csv_io import read_tab_csv  # noqa: E402
from text_utils import normalize_name  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WEAPONS_CANONICAL_CSV_PATH = ROOT / "src/data/weapons-canonical.csv"
WEAPONS_GAME_CSV_PATH = ROOT / "src/data/weapons-game.csv"
WEAPONS_PRINTINGS_CSV_PATH = ROOT / "src/data/weapons-printings.csv"
CARD_PRINTING_CSV_PATH = (
    ROOT.parent / "flesh-and-blood-cards/csvs/english/card-printing.csv"
)


def generate_weapons_csv() -> None:
    """Regenerate weapon-related pipe CSVs from ``card.csv`` + ``card-printing.csv``.

    Refreshes shared ``classes.csv`` / ``talents.csv`` from the full ``card.csv`` scan
    (same class/talent union as all card generators), not weapon rows only.

    Raises:
        FileNotFoundError: If no weapon rows exist in the upstream card CSV.
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

    weapon_cards_by_key: dict[str, list[dict[str, str]]] = {}
    for card in card_rows:
        if not types_include_weapon(card.get("Types", "")):
            continue
        full_name = card.get("Name", "").strip()
        if not full_name:
            continue
        slug = slugify_card_name_stem(full_name)
        weapon_cards_by_key.setdefault(slug, []).append(card)

    if not weapon_cards_by_key:
        raise FileNotFoundError(
            f"No weapon cards found. Expected rows in {CARD_CSV_PATH} with "
            "``Types`` containing a *weapon* token (e.g. ``Weapon``, ``2H Weapon``)."
        )

    canonical_rows: list[dict[str, str]] = []
    slug_order = sorted(weapon_cards_by_key.keys())
    for slug in slug_order:
        cards = weapon_cards_by_key[slug]
        display = min(c.get("Name", "").strip() for c in cards if c.get("Name", "").strip())
        canonical_rows.append(
            {
                "CanonicalWeaponId": make_hash_id("CW", slug),
                "CanonicalSlug": slug,
                "CanonicalWeapon": display,
            }
        )

    canonical_id_by_slug = {
        row["CanonicalSlug"]: row["CanonicalWeaponId"] for row in canonical_rows
    }
    assert_unique_ids(
        [(row["CanonicalWeaponId"], row["CanonicalSlug"]) for row in canonical_rows],
        "Canonical weapon",
    )

    unsorted_rows: list[dict[str, str]] = []
    for slug, cards in weapon_cards_by_key.items():
        canonical_weapon_id = canonical_id_by_slug[slug]
        for card in cards:
            full_name = card.get("Name", "").strip()
            class_names, talent_names = extract_weapon_classes_and_talents(
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
            power = (card.get("Power") or "").strip()
            ability = (card.get("Functional Text") or "").strip().replace("\n", " ")

            unsorted_rows.append(
                {
                    "SourceCardUniqueId": card.get("Unique ID", "").strip(),
                    "CanonicalWeaponId": canonical_weapon_id,
                    "CanonicalSlug": slug,
                    "CardName": full_name,
                    "ClassNames": class_names,
                    "TalentNames": talent_names,
                    "Cost": cost,
                    "Power": power,
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
                    row.get("Power", ""),
                ]
            )
        weapon_game_id = make_hash_id("WG", source_unique)
        class_ids = [class_id_by_name[n] for n in row["ClassNames"] if n in class_id_by_name]
        talent_ids = [talent_id_by_name[n] for n in row["TalentNames"] if n in talent_id_by_name]
        game_rows.append(
            {
                "WeaponGameId": weapon_game_id,
                "CardName": row["CardName"],
                "CanonicalWeaponId": row["CanonicalWeaponId"],
                "ClassIds": ", ".join(class_ids),
                "TalentIds": ", ".join(talent_ids),
                "Cost": row["Cost"],
                "Power": row["Power"],
                "AbilityText": row["AbilityText"],
                "Types": row["Types"],
            }
        )
        for entry in row["Printings"]:
            set_id, card_id, rarity = [part.strip() for part in entry.split("|")]
            printings_rows.append(
                {
                    "WeaponGameId": weapon_game_id,
                    "SetId": set_id,
                    "CardId": card_id,
                    "Rarity": rarity,
                }
            )

    assert_unique_ids(
        [(r["WeaponGameId"], r["CardName"]) for r in game_rows],
        "Weapon game",
    )

    canonical_fieldnames = ["CanonicalWeaponId", "CanonicalSlug", "CanonicalWeapon"]
    game_fieldnames = [
        "WeaponGameId",
        "CardName",
        "CanonicalWeaponId",
        "ClassIds",
        "TalentIds",
        "Cost",
        "Power",
        "AbilityText",
        "Types",
    ]
    printings_fieldnames = ["WeaponGameId", "SetId", "CardId", "Rarity"]

    for path, fieldnames, rows in [
        (WEAPONS_CANONICAL_CSV_PATH, canonical_fieldnames, canonical_rows),
        (WEAPONS_GAME_CSV_PATH, game_fieldnames, game_rows),
        (WEAPONS_PRINTINGS_CSV_PATH, printings_fieldnames, printings_rows),
    ]:
        write_pipe_csv_autogen(
            path,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_CREATE_WEAPONS,
        )


if __name__ == "__main__":
    generate_weapons_csv()
    _vd = Path(__file__).resolve().parent / "validate_data.py"
    _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
    raise SystemExit(_rc.returncode)
