"""Generate normalized hero CSV files from CSV card datasets.

This script writes linked outputs:
1) `heroes-canonical.csv` — one row per canonical hero (`CanonicalId`, slug, display name)
2) `heroes-game.csv` — one row per hero card line with reference IDs (``YoungHero``
   is ``true``/``false`` from the upstream *Young* type token; classes/talents use
   ``ClassIds`` / ``TalentIds``)
3) `classes.csv` / `talents.csv` — shared class and talent reference tables (union of
   hero + weapon + non-weapon equipment ``Types`` via :mod:`game_class_talent_csv`;
   regenerate alone with ``python3 src/data/create_classes_talents_csv.py``)
4) `heroes-printings.csv` — one row per set/card printing for each game row
5) `heroes-ll.csv` — living-legend status per hero variant, derived from the
   flesh-and-blood-cards upstream LL CSVs matched against ``heroes-game.csv``

Pass ``--ll-only`` to regenerate only ``heroes-ll.csv`` from the committed
``heroes-game.csv`` without touching the other outputs (useful when the upstream
card data is incomplete but the LL data has been updated).

Canonical IDs are normalized to deterministic hash IDs from `CanonicalSlug`.

``CanonicalHero`` (in ``heroes-canonical.csv``) is the curated **display** label used in
lore tooling and story junctions. It is **not** the same field as ``CardName`` in
``heroes-game.csv`` (the exact printed card title from upstream ``card.csv``): many
cards use a comma subtitle (e.g. ``Bravo, Showstopper``) while ``CanonicalHero`` may
stay short (``Bravo``). The generator still maps each ``CardName`` to a ``CanonicalId``
using the first segment of the title plus ``LORE_CANONICAL_OVERRIDES`` from
:mod:`hero_overrides` and the card-name aliases in ``hero-card-name-aliases.csv``,
and it builds a name→slug index from
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

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_types_extract import (  # noqa: E402
    dedupe_preserving_order,
    extract_card_classes_and_talents,
    is_young_hero_card,
    parse_tokens,
)
from create_sets_csv import SETS_CSV_PATH, generate_sets_csv  # noqa: E402
from tab_csv_io import read_tab_csv  # noqa: E402
from game_class_talent_csv import (  # noqa: E402
    UPSTREAM_CARD_CSV_PATH as CARD_CSV_PATH,
    merge_classes_and_talents_from_card_rows,
)
from hero_overrides import (  # noqa: E402
    LORE_CANONICAL_OVERRIDES,
    load_canonical_hero_card_name_aliases,
)
from pipe_csv_io import (  # noqa: E402
    REGENERATE_CREATE_HEROES,
    read_pipe_csv,
    write_pipe_csv_autogen,
)
from registry_ids import assert_unique_ids, make_hash_id  # noqa: E402
from text_utils import normalize_name  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HEROES_CANONICAL_CSV_PATH = ROOT / "src/data/csv/heroes-canonical.csv"
HEROES_GAME_CSV_PATH = ROOT / "src/data/csv/heroes-game.csv"
HEROES_PRINTINGS_CSV_PATH = ROOT / "src/data/csv/heroes-printings.csv"
HEROES_LL_CSV_PATH = ROOT / "src/data/csv/heroes-ll.csv"
CARD_PRINTING_CSV_PATH = (
    ROOT.parent / "flesh-and-blood-cards/csvs/english/card-printing.csv"
)
_LL_CC_CSV_PATH = (
    ROOT.parent / "flesh-and-blood-cards/csvs/english/living-legend-cc.csv"
)
_LL_BLITZ_CSV_PATH = (
    ROOT.parent / "flesh-and-blood-cards/csvs/english/living-legend-blitz.csv"
)

# Hero card-name → canonical-slug aliases now live in ``hero-card-name-aliases.csv``
# and are loaded via :func:`hero_overrides.load_canonical_hero_card_name_aliases`.
# Lore-specific canonical split overrides (``LORE_CANONICAL_OVERRIDES``) live in
# :mod:`hero_overrides` alongside the matching lore-file path overrides used by
# the mdBook preprocessor.


def _ll_date(raw: str) -> str:
    """Return YYYY-MM-DD from an ISO datetime string, or the raw value on failure."""
    s = raw.strip()
    return s.split("T")[0] if "T" in s else s


def generate_heroes_ll_csv(
    game_rows: list[dict[str, str]] | None = None,
    canonical_rows: list[dict[str, str]] | None = None,
) -> None:
    """Write ``heroes-ll.csv`` from flesh-and-blood-cards living-legend data.

    Matches LL card names against ``heroes-game.csv`` ``CardName`` values to resolve
    canonical slugs.  Re-legalized entries (``Status Active`` = ``No`` supersedes an
    earlier ``Yes`` for the same card+format) are excluded.  Silently skips if either
    upstream LL CSV is absent.

    When called with no arguments reads directly from the committed
    ``heroes-game.csv`` and ``heroes-canonical.csv``, so it can be run standalone
    (``python3 src/data/create_heroes_csv.py --ll-only``) without regenerating all
    other hero CSVs from the upstream flesh-and-blood-cards data.
    """
    if not _LL_CC_CSV_PATH.exists() or not _LL_BLITZ_CSV_PATH.exists():
        return
    if game_rows is None:
        _, game_rows = read_pipe_csv(HEROES_GAME_CSV_PATH)
    if canonical_rows is None:
        _, canonical_rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)

    canonical_slug_by_id = {
        row["CanonicalId"]: row["CanonicalSlug"]
        for row in canonical_rows
        if row.get("CanonicalId") and row.get("CanonicalSlug")
    }
    slug_by_card_name: dict[str, str] = {}
    for row in game_rows:
        card_name = (row.get("CardName") or "").strip()
        canonical_id = (row.get("CanonicalId") or "").strip()
        if card_name and canonical_id:
            slug = canonical_slug_by_id.get(canonical_id, "")
            if slug:
                slug_by_card_name[card_name] = slug

    ll_rows: list[dict[str, str]] = []
    for fmt, csv_path in [("CC", _LL_CC_CSV_PATH), ("Blitz", _LL_BLITZ_CSV_PATH)]:
        upstream = read_tab_csv(csv_path)
        # For each hero card name keep only the latest entry by date (handles re-legalization).
        latest: dict[str, dict[str, str]] = {}
        for row in upstream:
            card_name = (row.get("Card Name") or "").strip()
            if card_name not in slug_by_card_name:
                continue
            date = _ll_date(row.get("Date In Effect") or "")
            existing = latest.get(card_name)
            if not existing or date > existing["date"]:
                latest[card_name] = {
                    "date": date,
                    "active": (row.get("Status Active") or "").strip(),
                }
        for card_name, entry in latest.items():
            if entry["active"] != "Yes":
                continue
            ll_rows.append(
                {
                    "CanonicalSlug": slug_by_card_name[card_name],
                    "CardName": card_name,
                    "Format": fmt,
                    "DateInEffect": entry["date"],
                }
            )

    ll_rows.sort(key=lambda r: (r["Format"], r["CanonicalSlug"], r["DateInEffect"]))
    write_pipe_csv_autogen(
        HEROES_LL_CSV_PATH,
        ["CanonicalSlug", "CardName", "Format", "DateInEffect"],
        ll_rows,
        regenerate_command=REGENERATE_CREATE_HEROES,
    )


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


def apply_lore_canonical_override(
    base_slug: str, hero_name: str, hero_variant: str
) -> str:
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

    assert_unique_ids(
        [
            (row.get("CanonicalId", ""), row.get("CanonicalSlug", ""))
            for row in canonical_rows
        ],
        "Canonical hero",
    )

    canonical_id_by_slug = {
        row["CanonicalSlug"]: row["CanonicalId"] for row in canonical_rows
    }
    canonical_slug_by_name: dict[str, str] = {}
    for row in canonical_rows:
        name_key = normalize_name(row["CanonicalHero"])
        canonical_slug_by_name.setdefault(name_key, row["CanonicalSlug"])

    for alt_name_key, slug in load_canonical_hero_card_name_aliases().items():
        if slug not in canonical_id_by_slug:
            raise ValueError(
                f"hero-card-name-aliases.csv: {alt_name_key!r} -> {slug!r} "
                "is not a CanonicalSlug in heroes-canonical.csv"
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
            canonical_slug = apply_lore_canonical_override(
                base_slug, name, comma_subtitle
            )
            canonical_id = canonical_id_by_slug.get(canonical_slug, "")
            class_names, talent_names = extract_card_classes_and_talents(
                card.get("Types", "")
            )
            printings = dedupe_preserving_order(
                [
                    f"{entry['SetId']}|{entry['CardId']}|{entry['Rarity']}"
                    for entry in printings_by_card_unique.get(
                        card.get("Unique ID", ""), []
                    )
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
                    "AbilityText": card.get("Functional Text", "")
                    .strip()
                    .replace("\n", " "),
                    "YoungHero": (
                        "true" if is_young_hero_card(card.get("Types", "")) else "false"
                    ),
                    "TypesNormalized": ", ".join(parse_tokens(card.get("Types", ""))),
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
                    row.get("TypesNormalized", ""),
                    row.get("Health", ""),
                    row.get("Intellect", ""),
                ]
            )
        hero_game_id = make_hash_id("HG", source_unique)
        class_ids = [
            class_id_by_name[name]
            for name in row["ClassNames"]
            if name in class_id_by_name
        ]
        talent_ids = [
            talent_id_by_name[name]
            for name in row["TalentNames"]
            if name in talent_id_by_name
        ]
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
                "YoungHero": row["YoungHero"],
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

    assert_unique_ids(
        [(row["HeroGameId"], row["CardName"]) for row in game_rows],
        "Hero game",
    )

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
        "YoungHero",
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

    generate_heroes_ll_csv(game_rows, canonical_rows)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ll-only":
        generate_heroes_ll_csv()
    else:
        generate_heroes_csv()
        _vd = Path(__file__).resolve().parent / "validate_data.py"
        _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
        raise SystemExit(_rc.returncode)
