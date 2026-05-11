"""Generate normalized hero CSV files from CSV card datasets.

This script writes linked outputs:
1) `heroes-canonical.csv` — one row per canonical hero (`CanonicalId`, slug, display name)
2) `heroes-game.csv` — one row per hero card line with reference IDs
3) `classes.csv` / `talents.csv` — shared class and talent reference tables (union of
   hero + weapon + non-weapon equipment ``Types`` via :mod:`game_class_talent_csv`;
   regenerate alone with ``python3 src/data/create_classes_talents_csv.py``)
4) `heroes-printings.csv` — one row per set/card printing for each game row

Canonical IDs are normalized to deterministic hash IDs from `CanonicalSlug`.

``CanonicalHero`` (in ``heroes-canonical.csv``) is the curated **display** label used in
lore tooling and story junctions. It is **not** the same field as ``CardName`` in
``heroes-game.csv`` (the exact printed card title from upstream ``card.csv``): many
cards use a comma subtitle (e.g. ``Bravo, Showstopper``) while ``CanonicalHero`` may
stay short (``Bravo``). The generator still maps each ``CardName`` to a ``CanonicalId``
using the first segment of the title plus ``LORE_CANONICAL_OVERRIDES`` and
``CANONICAL_HERO_CARD_NAME_ALIASES``, and it builds a name→slug index from
``normalize_name(CanonicalHero)`` so slug resolution stays aligned with the roster.
``validate_data._check_heroes_game_cardname_resolution`` replays that mapping to catch
drift between committed canonical and game rows.

``heroes-game.csv`` primary key is ``HeroGameId`` (``HG`` + hash). It stores the upstream hero card ``Name`` as ``CardName`` (full
printed title) plus ``CanonicalId`` so each printing links back to one canonical
identity from ``heroes-canonical.csv``. ``CardName`` is never derived from
``CanonicalHero``; if the committed CSV was back-filled from legacy ``Variant``
rows, regenerate from ``card.csv`` to restore exact printed titles.

When run as a script, generation is followed by ``validate_data.py`` (non-zero exit
if any expected generated ID column is blank in the checked data CSVs).

Each generated CSV begins with a ``#`` banner line marking it as auto-generated.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_types_extract import (
    dedupe_preserving_order,
    extract_card_classes_and_talents,
    parse_tokens,
)
from create_sets_csv import SETS_CSV_PATH, generate_sets_csv
from tab_csv_io import read_tab_csv
from game_class_talent_csv import (
    UPSTREAM_CARD_CSV_PATH as CARD_CSV_PATH,
    merge_classes_and_talents_from_card_rows,
)
from pipe_csv_io import REGENERATE_CREATE_HEROES, read_pipe_csv, write_pipe_csv_autogen

ROOT = Path(__file__).resolve().parents[2]
HEROES_CANONICAL_CSV_PATH = ROOT / "src/data/heroes-canonical.csv"
HEROES_GAME_CSV_PATH = ROOT / "src/data/heroes-game.csv"
HEROES_PRINTINGS_CSV_PATH = ROOT / "src/data/heroes-printings.csv"
CARD_PRINTING_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/card-printing.csv"

# Extra ``normalize_name`` keys for the text *before the first comma* on the card
# ``Name`` → ``CanonicalSlug`` when that segment does not match
# ``normalize_name(CanonicalHero)`` from ``heroes-canonical.csv``.
#
# This table only affects slug / ``CanonicalId`` resolution (and
# ``LORE_CANONICAL_OVERRIDES`` lookup). It does **not** change ``CardName``, which is
# always the full upstream card title—so wrong ``CardName`` values in hand-migrated
# CSV rows are not caused by these aliases.
CANONICAL_HERO_CARD_NAME_ALIASES: dict[str, str] = {
    "dorintheaironsong": "dorinthea",
    "dashio": "dash",
    "fightmasterkox": "kox",
    "groundbreakercrix": "crix",
    "kassaiofthegoldensand": "kassai",
    "maxxnitro": "maxx",
    "maxxthehypenitro": "maxx",
    "professorteklovossen": "teklovossen",
    "valdabrightaxe": "valda",
    "serboltyn": "boltyn",
}

# Lore-specific canonical split overrides that are not represented in game data.
LORE_CANONICAL_OVERRIDES = {
    "arakni": {
        "araknihuntsman": "arakni-huntsman",
        "arakni": "arakni-huntsman",
        "arakni5lp3d7hru7h3cr4x": "arakni-solitary-confinement",
        "araknisolitaryconfinement": "arakni-solitary-confinement",
        "araknimarionette": "arakni-web-of-deceit",
        "arakniwebofdeceit": "arakni-web-of-deceit",
    }
}


def normalize_name(value: str) -> str:
    """Lowercase alphanumeric-only fold for hero name matching and hashing.

    Args:
        value: Raw display or card name string.

    Returns:
        Lowercase string with non-alphanumeric characters removed.
    """
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def split_name_variant(heading: str) -> tuple[str, str]:
    """Split the printed card ``Name`` on the first comma.

    Args:
        heading: Full ``Name`` field from the card CSV.

    Returns:
        ``(name_before_comma, subtitle_after_comma)``. If there is no comma, the
        whole string is returned as the first element and the second is an empty
        string.
    """
    clean = heading.strip()
    if "," in clean:
        name, variant = [part.strip() for part in clean.split(",", 1)]
        return name, variant
    return clean, ""


def make_hash_id(prefix: str, unique_value: str, digest_len: int = 10) -> str:
    """Return ``prefix`` + truncated SHA-1 hex of ``unique_value``.

    Args:
        prefix: Two-letter uppercase id family (``HG``, ``CN``, etc.).
        unique_value: Stable UTF-8 string to hash.
        digest_len: Hex characters to keep (default ``10``).

    Returns:
        Deterministic identifier.
    """
    digest = hashlib.sha1(unique_value.encode("utf-8")).hexdigest()[:digest_len]
    return f"{prefix}{digest}"


def apply_lore_canonical_override(base_slug: str, hero_name: str, hero_variant: str) -> str:
    """Apply lore-specific canonical split overrides."""
    override_table = LORE_CANONICAL_OVERRIDES.get(base_slug)
    if not override_table:
        return base_slug
    full_name = f"{hero_name}, {hero_variant}" if hero_variant else hero_name
    return override_table.get(normalize_name(full_name), base_slug)


def generate_heroes_csv() -> None:
    """Regenerate hero-related pipe CSVs from canonical roster + upstream card data.

    Writes ``heroes-canonical.csv`` (with recomputed ``CanonicalId`` hashes),
    ``heroes-game.csv``, ``heroes-printings.csv``, and refreshes shared ``classes.csv``
    / ``talents.csv`` from the full upstream ``card.csv`` (hero + weapon +
    non-weapon equipment ``Types`` union; same as ``create_classes_talents_csv.py``).

    Raises:
        FileNotFoundError: If no hero rows exist in the upstream card CSV.
        ValueError: On id hash collisions in canonical, class, talent, or game ids.
    """
    if not SETS_CSV_PATH.exists():
        generate_sets_csv()

    _, canonical_rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)

    for row in canonical_rows:
        slug = row.get("CanonicalSlug", "").strip()
        if not slug:
            continue
        row["CanonicalId"] = make_hash_id("CN", slug)

    canonical_ids = [row.get("CanonicalId", "") for row in canonical_rows if row.get("CanonicalId", "")]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("Canonical ID hash collision detected")

    canonical_id_by_slug = {row["CanonicalSlug"]: row["CanonicalId"] for row in canonical_rows}
    canonical_slug_by_name: dict[str, str] = {}
    for row in canonical_rows:
        name_key = normalize_name(row["CanonicalHero"])
        canonical_slug_by_name.setdefault(name_key, row["CanonicalSlug"])

    for alt_name_key, slug in CANONICAL_HERO_CARD_NAME_ALIASES.items():
        if slug not in canonical_id_by_slug:
            raise ValueError(
                f"CANONICAL_HERO_CARD_NAME_ALIASES[{alt_name_key!r}] -> {slug!r} is not a CanonicalSlug in heroes-canonical.csv"
            )
        canonical_slug_by_name[alt_name_key] = slug

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

    hero_cards_by_name: dict[str, list[dict[str, str]]] = {}
    for card in card_rows:
        types = parse_tokens(card.get("Types", ""))
        if "Hero" not in types:
            continue
        full_name = card.get("Name", "").strip()
        if not full_name:
            continue
        hero_cards_by_name.setdefault(normalize_name(full_name), []).append(card)

    if not hero_cards_by_name:
        raise FileNotFoundError(
            f"No hero cards found. Expected hero rows in {CARD_CSV_PATH} "
            "(tab-separated ``Name`` with ``Types`` containing Hero)."
        )

    unsorted_rows: list[dict[str, str]] = []
    for cards_for_name in hero_cards_by_name.values():
        for card in cards_for_name:
            full_name = card.get("Name", "").strip()
            name, comma_subtitle = split_name_variant(full_name)
            name_key = normalize_name(name)
            base_slug = canonical_slug_by_name.get(name_key, name_key)
            canonical_slug = apply_lore_canonical_override(base_slug, name, comma_subtitle)
            canonical_id = canonical_id_by_slug.get(canonical_slug, "")
            class_names, talent_names = extract_card_classes_and_talents(card.get("Types", ""))
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

            unsorted_rows.append(
                {
                    "SourceCardUniqueId": card.get("Unique ID", "").strip(),
                    "CanonicalId": canonical_id,
                    "CanonicalSlug": canonical_slug,
                    "CardName": full_name,
                    "ClassNames": class_names,
                    "TalentNames": talent_names,
                    "Health": card.get("Health", "").strip(),
                    "Intellect": card.get("Intelligence", "").strip(),
                    "AbilityText": card.get("Functional Text", "").strip().replace("\n", " "),
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
                    row.get("Health", ""),
                    row.get("Intellect", ""),
                ]
            )
        hero_game_id = make_hash_id("HG", source_unique)
        class_ids = [class_id_by_name[name] for name in row["ClassNames"] if name in class_id_by_name]
        talent_ids = [talent_id_by_name[name] for name in row["TalentNames"] if name in talent_id_by_name]
        game_rows.append(
            {
                "HeroGameId": hero_game_id,
                "CardName": row["CardName"],
                "CanonicalId": row["CanonicalId"],
                "ClassIds": ", ".join(class_ids),
                "TalentIds": ", ".join(talent_ids),
                "Health": row["Health"],
                "Intellect": row["Intellect"],
                "AbilityText": row["AbilityText"],
                "Types": row["Types"],
            }
        )
        for entry in row["Printings"]:
            set_id, card_id, rarity = [part.strip() for part in entry.split("|")]
            printings_rows.append(
                {
                    "HeroGameId": hero_game_id,
                    "SetId": set_id,
                    "CardId": card_id,
                    "Rarity": rarity,
                }
            )

    hero_game_ids = [row["HeroGameId"] for row in game_rows]
    if len(hero_game_ids) != len(set(hero_game_ids)):
        raise ValueError("Hero game ID hash collision detected")

    canonical_fieldnames = ["CanonicalId", "CanonicalSlug", "CanonicalHero"]
    game_fieldnames = [
        "HeroGameId",
        "CardName",
        "CanonicalId",
        "ClassIds",
        "TalentIds",
        "Health",
        "Intellect",
        "AbilityText",
        "Types",
    ]
    printings_fieldnames = ["HeroGameId", "SetId", "CardId", "Rarity"]

    for path, fieldnames, rows in [
        (HEROES_CANONICAL_CSV_PATH, canonical_fieldnames, canonical_rows),
        (HEROES_GAME_CSV_PATH, game_fieldnames, game_rows),
        (HEROES_PRINTINGS_CSV_PATH, printings_fieldnames, printings_rows),
    ]:
        write_pipe_csv_autogen(
            path,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_CREATE_HEROES,
        )


if __name__ == "__main__":
    generate_heroes_csv()
    _vd = Path(__file__).resolve().parent / "validate_data.py"
    _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
    raise SystemExit(_rc.returncode)
