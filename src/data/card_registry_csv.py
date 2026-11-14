"""Shared generator for the card-backed registry CSVs (weapons, equipment) and the
upstream-printing helpers the hero generator also uses.

``create_weapons_csv.py`` and ``create_equipment_csv.py`` differ only in which
cards they select, how they split ``Types`` into classes/talents, which stat
column they carry (``Power`` vs ``Defense``), their id prefixes and their output
paths. Each describes that in a :class:`CardRegistrySpec` and calls
:func:`generate_card_registry_csvs`, which writes three pipe CSVs:

1. ``<kind>-canonical.csv`` — one row per canonical card (slug from full printed ``Name``)
2. ``<kind>-game.csv`` — one row per selected card line
3. ``<kind>-printings.csv`` — one row per set printing per game row

and refreshes the shared ``classes.csv`` / ``talents.csv`` from the full upstream
``card.csv`` (see :mod:`game_class_talent_csv`).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_name_slug import slugify_card_name_stem  # noqa: E402
from card_types_extract import dedupe_preserving_order, parse_tokens  # noqa: E402
from create_sets_csv import SETS_CSV_PATH, generate_sets_csv  # noqa: E402
from game_class_talent_csv import (  # noqa: E402
    UPSTREAM_CARD_CSV_PATH,
    UPSTREAM_CARD_PRINTING_CSV_PATH,
    merge_classes_and_talents_from_card_rows,
)
from pipe_csv_io import read_pipe_csv, write_pipe_csv_autogen  # noqa: E402
from registry_ids import assert_unique_ids, make_hash_id  # noqa: E402
from tab_csv_io import read_tab_csv  # noqa: E402
from text_utils import normalize_name  # noqa: E402


def ensure_sets_csv() -> None:
    """Generate ``sets.csv`` first when it does not exist yet (release dates come from it)."""
    if not SETS_CSV_PATH.exists():
        generate_sets_csv()


def set_release_by_id() -> dict[str, str]:
    """Map each ``SetId`` in ``sets.csv`` to its ``InitialReleaseDate`` (may be empty)."""
    _, sets_rows = read_pipe_csv(SETS_CSV_PATH)
    release_by_id: dict[str, str] = {}
    for row in sets_rows:
        set_id = row.get("SetId", "").strip()
        if set_id:
            release_by_id[set_id] = row.get("InitialReleaseDate", "").strip()
    return release_by_id


def printings_by_card_unique_id(card_printing_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group raw upstream ``card-printing.csv`` rows by their ``Card Unique ID``."""
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in card_printing_rows:
        card_unique = row.get("Card Unique ID", "")
        if card_unique:
            grouped.setdefault(card_unique, []).append(row)
    return grouped


def earliest_release(set_ids: Iterable[str], release_by_id: dict[str, str]) -> str:
    """Return the earliest non-empty release date among ``set_ids``, or ``""``."""
    earliest = ""
    for set_id in set_ids:
        release = release_by_id.get(set_id, "")
        if release and (not earliest or release < earliest):
            earliest = release
    return earliest


@dataclass(frozen=True)
class CardRegistrySpec:
    """What distinguishes one card registry (weapons, equipment) from another.

    ``noun`` names the id columns: ``Canonical{noun}Id``, ``Canonical{noun}`` and
    ``{noun}GameId``. ``stat_column`` is both the upstream ``card.csv`` column and
    the output column name.
    """

    noun: str
    includes_card: Callable[[str], bool]
    extract_classes_and_talents: Callable[[str], tuple[list[str], list[str]]]
    stat_column: str
    canonical_id_prefix: str
    game_id_prefix: str
    canonical_csv_path: Path
    game_csv_path: Path
    printings_csv_path: Path
    regenerate_command: str
    missing_cards_hint: str


def generate_card_registry_csvs(spec: CardRegistrySpec) -> None:
    """Regenerate one registry's pipe CSVs from ``card.csv`` + ``card-printing.csv``.

    Refreshes shared ``classes.csv`` / ``talents.csv`` from the full ``card.csv``
    scan (same class/talent union as all card generators), not selected rows only.

    Raises:
        FileNotFoundError: If no selected rows exist in the upstream card CSV.
        ValueError: On id hash collisions in canonical or game rows.
    """
    canonical_id_col = f"Canonical{spec.noun}Id"
    canonical_name_col = f"Canonical{spec.noun}"
    game_id_col = f"{spec.noun}GameId"
    stat = spec.stat_column

    ensure_sets_csv()

    card_rows = read_tab_csv(UPSTREAM_CARD_CSV_PATH)
    printings_by_card_unique = printings_by_card_unique_id(read_tab_csv(UPSTREAM_CARD_PRINTING_CSV_PATH))
    release_by_id = set_release_by_id()

    cards_by_slug: dict[str, list[dict[str, str]]] = {}
    for card in card_rows:
        if not spec.includes_card(card.get("Types", "")):
            continue
        full_name = card.get("Name", "").strip()
        if not full_name:
            continue
        cards_by_slug.setdefault(slugify_card_name_stem(full_name), []).append(card)

    if not cards_by_slug:
        raise FileNotFoundError(
            f"No {spec.noun.lower()} cards found. Expected rows in {UPSTREAM_CARD_CSV_PATH} with "
            + spec.missing_cards_hint
        )

    canonical_rows: list[dict[str, str]] = []
    for slug in sorted(cards_by_slug):
        display = min(c.get("Name", "").strip() for c in cards_by_slug[slug] if c.get("Name", "").strip())
        canonical_rows.append(
            {
                canonical_id_col: make_hash_id(spec.canonical_id_prefix, slug),
                "CanonicalSlug": slug,
                canonical_name_col: display,
            }
        )

    canonical_id_by_slug = {row["CanonicalSlug"]: row[canonical_id_col] for row in canonical_rows}
    assert_unique_ids(
        [(row[canonical_id_col], row["CanonicalSlug"]) for row in canonical_rows],
        f"Canonical {spec.noun.lower()}",
    )

    unsorted_rows: list[dict] = []
    for slug, cards in cards_by_slug.items():
        for card in cards:
            class_names, talent_names = spec.extract_classes_and_talents(card.get("Types", ""))
            # A printing is keyed on "Set|Card|Rarity|URL"; repeats collapse in upstream order.
            printings = dedupe_preserving_order(
                [
                    "|".join((entry.get(k) or "").strip() for k in ("Set ID", "Card ID", "Rarity", "Image URL"))
                    for entry in printings_by_card_unique.get(card.get("Unique ID", ""), [])
                    if (entry.get("Set ID") or "").strip() and (entry.get("Card ID") or "").strip()
                ]
            )
            unsorted_rows.append(
                {
                    "SourceCardUniqueId": card.get("Unique ID", "").strip(),
                    canonical_id_col: canonical_id_by_slug[slug],
                    "CanonicalSlug": slug,
                    "CardName": card.get("Name", "").strip(),
                    "ClassNames": class_names,
                    "TalentNames": talent_names,
                    "Cost": (card.get("Cost") or "").strip(),
                    stat: (card.get(stat) or "").strip(),
                    "AbilityText": (card.get("Functional Text") or "").strip().replace("\n", " "),
                    "Types": ", ".join(parse_tokens(card.get("Types", ""))),
                    "Printings": printings,
                    "EarliestRelease": earliest_release((p.split("|", 1)[0] for p in printings), release_by_id),
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
        source_unique = row["SourceCardUniqueId"] or "|".join(
            [row["CanonicalSlug"], row["CardName"], row["Types"], row["Cost"], row[stat]]
        )
        game_id = make_hash_id(spec.game_id_prefix, source_unique)
        class_ids = [class_id_by_name[n] for n in row["ClassNames"] if n in class_id_by_name]
        talent_ids = [talent_id_by_name[n] for n in row["TalentNames"] if n in talent_id_by_name]
        game_rows.append(
            {
                game_id_col: game_id,
                "CardName": row["CardName"],
                canonical_id_col: row[canonical_id_col],
                "ClassIds": ", ".join(class_ids),
                "TalentIds": ", ".join(talent_ids),
                "Cost": row["Cost"],
                stat: row[stat],
                "AbilityText": row["AbilityText"],
                "Types": row["Types"],
            }
        )
        for entry in row["Printings"]:
            set_id, card_id, rarity, image_url = entry.split("|")
            printings_rows.append(
                {
                    game_id_col: game_id,
                    "SetId": set_id,
                    "CardId": card_id,
                    "Rarity": rarity,
                    "ImageURL": image_url,
                }
            )

    assert_unique_ids(
        [(r[game_id_col], r["CardName"]) for r in game_rows],
        f"{spec.noun} game",
    )

    canonical_fieldnames = [canonical_id_col, "CanonicalSlug", canonical_name_col]
    game_fieldnames = [
        game_id_col,
        "CardName",
        canonical_id_col,
        "ClassIds",
        "TalentIds",
        "Cost",
        stat,
        "AbilityText",
        "Types",
    ]
    printings_fieldnames = [game_id_col, "SetId", "CardId", "Rarity", "ImageURL"]

    # Sort to match db._export's printings ORDER BY, so regenerating from the API
    # and round-tripping through the database produce byte-identical files.
    printings_rows.sort(key=lambda r: (r[game_id_col], r["SetId"], r["CardId"], r["ImageURL"]))

    for path, fieldnames, rows in [
        (spec.canonical_csv_path, canonical_fieldnames, canonical_rows),
        (spec.game_csv_path, game_fieldnames, game_rows),
        (spec.printings_csv_path, printings_fieldnames, printings_rows),
    ]:
        write_pipe_csv_autogen(path, fieldnames, rows, regenerate_command=spec.regenerate_command)
