"""Generate normalized hero CSV files from CSV card datasets.

This script writes linked outputs:
1) `heroes-canonical.csv` — one row per canonical hero (`CanonicalId`, slug, display name)
2) `heroes-game.csv` — one row per hero card line with reference IDs (``YoungHero``
   is ``true``/``false`` from the upstream *Young* type token; classes/talents use
   ``ClassIds`` / ``TalentIds``)
3) `classes.csv` / `talents.csv` — shared class and talent reference tables (union of
   hero + weapon + non-weapon equipment ``Types`` via :mod:`game_class_talent_csv`;
   regenerate alone with ``python3 src/data/create_classes_talents_csv.py``)
4) `heroes-printings.csv` — one row per upstream printing (``PrintingUniqueId``,
   the id card images are served by) for each game row, with ``Foiling``,
   ``ArtVariation`` and ``Artist``
5) `heroes-ll.csv` — Classic Constructed Living Legend status per adult hero card,
   fetched from the fabtcg.com hero API (``HEROES_API_URL``) and matched against
   ``heroes-game.csv``. The flesh-and-blood-cards ``living-legend-cc.csv`` only
   supplies ``DateInEffect``; it lags the API, so it no longer decides who is a
   Living Legend. Blitz and young heroes are not reported.

Pass ``--ll-only`` to regenerate only ``heroes-ll.csv`` from the committed
``heroes-game.csv`` without touching the other outputs. Both modes need network
access, because ``heroes-ll.csv`` is always fetched.

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

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_types_extract import (  # noqa: E402
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
CARD_PRINTING_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/card-printing.csv"
_LL_CC_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/living-legend-cc.csv"
HEROES_API_URL = "https://fabtcg.com/api/fab/v2/heroes/?lang=en"
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
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


def _is_cc_living_legend(hero: dict) -> bool:
    """True when the API hero has retired from Classic Constructed as a Living Legend."""
    formats = hero.get("format") or {}
    points = (hero.get("status") or "").strip()
    return (
        hero.get("type") != "young"
        and hero.get("is_released") == "yes"
        and (formats.get("cc") or {}).get("status") == "not_legal"
        and (formats.get("living-legend") or {}).get("status") == "legal"
        and points.isdigit()
        and int(points) >= 1000
    )


def living_legend_rows(
    api: dict,
    game_rows: list[dict[str, str]],
    canonical_rows: list[dict[str, str]],
    upstream_cc_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Return ``heroes-ll.csv`` rows for the Classic Constructed Living Legends in ``api``.

    ``api`` is the parsed hero API response (``{"heroes": [...]}``). A hero is a
    CC Living Legend when it is not ``young``, is released, is ``not_legal`` in
    ``cc`` and ``legal`` in ``living-legend``, and has at least 1000 points
    (``status``). Its ``title`` and ``subtitle`` are matched to an adult
    ``CardName`` with :func:`text_utils.normalize_name`, which absorbs the API's
    differences in case, quotes and punctuation; a ``both`` hero therefore lands
    on its adult card. ``DateInEffect`` is the latest ``upstream_cc_rows`` entry
    for the card when that entry is active, else empty.

    Raises:
        ValueError: Naming every Living Legend that matches no adult card, so a
            new or renamed hero cannot drop out of the CSV silently.
    """
    slug_by_id = {row["CanonicalId"]: row["CanonicalSlug"] for row in canonical_rows}
    adult_by_key = {
        normalize_name(row["CardName"]): row for row in game_rows if (row.get("YoungHero") or "").strip() != "true"
    }
    # Upstream keeps a history per card; only its latest entry counts, and only if still active.
    latest: dict[str, tuple[str, str]] = {}
    for row in upstream_cc_rows or []:
        card_name = (row.get("Card Name") or "").strip()
        date = _ll_date(row.get("Date In Effect") or "")
        if card_name not in latest or date > latest[card_name][0]:
            latest[card_name] = (date, (row.get("Status Active") or "").strip())
    dates = {name: date for name, (date, active) in latest.items() if active == "Yes"}

    rows: list[dict[str, str]] = []
    unmatched: list[str] = []
    for hero in api["heroes"]:
        if not _is_cc_living_legend(hero):
            continue
        title = (hero.get("title") or "").strip()
        subtitle = (hero.get("subtitle") or "").strip()
        game = adult_by_key.get(normalize_name(f"{title} {subtitle}"))
        if game is None:
            unmatched.append(f"{title}, {subtitle}" if subtitle else title)
            continue
        card_name = game["CardName"]
        rows.append(
            {
                "CanonicalSlug": slug_by_id[game["CanonicalId"]],
                "CardName": card_name,
                "Format": "CC",
                "DateInEffect": dates.get(card_name, ""),
            }
        )
    if unmatched:
        raise ValueError(
            "Living Legend heroes from the fabtcg.com API match no adult CardName in heroes-game.csv: "
            + "; ".join(unmatched)
        )
    return rows


def fetch_heroes_api() -> dict:
    """Fetch the fabtcg.com hero API (the same request ``../fab-ll`` makes).

    Uses :mod:`urllib` rather than ``requests``, which ``requirements-data.txt``
    does not provide.
    """
    request = urllib.request.Request(HEROES_API_URL, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def generate_heroes_ll_csv(
    game_rows: list[dict[str, str]] | None = None,
    canonical_rows: list[dict[str, str]] | None = None,
) -> None:
    """Write ``heroes-ll.csv`` from the fabtcg.com hero API.

    Living Legend status comes from the API (see :func:`living_legend_rows`);
    the flesh-and-blood-cards ``living-legend-cc.csv`` only supplies
    ``DateInEffect`` where it has an active row for the card, and may be absent.

    When called with no arguments reads directly from the committed
    ``heroes-game.csv`` and ``heroes-canonical.csv``, so it can be run standalone
    (``python3 src/data/create_heroes_csv.py --ll-only``) without regenerating all
    other hero CSVs from the upstream flesh-and-blood-cards data.
    """
    if game_rows is None:
        _, game_rows = read_pipe_csv(HEROES_GAME_CSV_PATH)
    if canonical_rows is None:
        _, canonical_rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)
    upstream_cc_rows = read_tab_csv(_LL_CC_CSV_PATH) if _LL_CC_CSV_PATH.exists() else None

    ll_rows = living_legend_rows(fetch_heroes_api(), game_rows, canonical_rows, upstream_cc_rows)
    ll_rows.sort(key=lambda r: (r["CanonicalSlug"], r["CardName"]))
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


def apply_lore_canonical_override(base_slug: str, hero_name: str, hero_variant: str) -> str:
    """Apply lore-specific canonical split overrides.

    The table is looked up by ``base_slug`` first, then by the normalized base
    hero name. Both are needed: ``base_slug`` is only the bare name when that
    name is absent from the roster, and for a hero whose forms are already
    rostered — Arakni — it has instead been resolved to whichever of those rows
    the name index happened to yield, so a name-keyed table would never be hit.
    """
    override_table = LORE_CANONICAL_OVERRIDES.get(base_slug) or LORE_CANONICAL_OVERRIDES.get(normalize_name(hero_name))
    if not override_table:
        return base_slug
    full_name = f"{hero_name}, {hero_variant}" if hero_variant else hero_name
    return override_table.get(normalize_name(full_name), base_slug)


def hero_printing_rows(hero_game_id: str, upstream_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return one ``heroes-printings.csv`` row per upstream ``card-printing.csv`` row.

    A printing is the upstream ``Unique ID``, not the ``(SetId, CardId)`` pair:
    one card id can carry several printings that differ only in foiling or art
    (EVR017 is a rainbow-foil standard, a cold foil and a cold-foil full art),
    and each has its own card image, served by that id. ``Artist`` and
    ``ArtVariation`` keep upstream's ``", "`` join for several values, the same
    separator ``ClassIds`` uses.
    """
    rows: list[dict[str, str]] = []
    for upstream in upstream_rows:
        printing_unique_id = (upstream.get("Unique ID") or "").strip()
        set_id = (upstream.get("Set ID") or "").strip()
        card_id = (upstream.get("Card ID") or "").strip()
        if not (printing_unique_id and set_id and card_id):
            continue
        rows.append(
            {
                "HeroGameId": hero_game_id,
                "PrintingUniqueId": printing_unique_id,
                "SetId": set_id,
                "CardId": card_id,
                "Rarity": (upstream.get("Rarity") or "").strip(),
                "Foiling": (upstream.get("Foiling") or "").strip(),
                "ArtVariation": (upstream.get("Art Variations") or "").strip(),
                "Artist": (upstream.get("Artists") or "").strip(),
            }
        )
    return rows


def dedupe_printings(printings_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep one row per ``(HeroGameId, PrintingUniqueId)``, the ``heroes_printings`` key.

    Upstream lists a Marvel printing under the same card id as the base printing
    (``SUP002`` is both ``B`` and ``V``). Before the key carried the printing id,
    the generator had to drop the Marvel so the DB export would not drop it
    instead. Each Marvel is its own printing with its own image, so now every
    printing id is kept and only a repeated one collapses.
    """
    kept: dict[tuple[str, str], dict[str, str]] = {}
    for row in printings_rows:
        kept.setdefault((row["HeroGameId"], row["PrintingUniqueId"]), row)
    return list(kept.values())


def sort_like_db_export(
    game_rows: list[dict[str, str]],
    printings_rows: list[dict[str, str]],
    canonical_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Order rows exactly as ``db.export_to_csv()`` writes the same files.

    Two writers own ``heroes-game.csv``, ``heroes-printings.csv`` and
    ``heroes-canonical.csv``: this generator and the DB export, which every
    ``create_stories_index.py`` run triggers. When their orders differed, each
    regeneration reordered the whole file and buried the real changes in the diff.

    The keys mirror the ``ORDER BY`` clauses in ``db/_queries.py``. They compare
    plain ``str`` values, never ``.lower()``: SQLite's default BINARY collation is
    case-sensitive, and code-point order on ``str`` equals byte order on UTF-8.
    """
    return (
        sorted(game_rows, key=lambda r: r["CardName"]),
        sorted(printings_rows, key=lambda r: (r["HeroGameId"], r["SetId"], r["CardId"], r["PrintingUniqueId"])),
        sorted(canonical_rows, key=lambda r: r["CanonicalSlug"]),
    )


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
        [(row.get("CanonicalId", ""), row.get("CanonicalSlug", "")) for row in canonical_rows],
        "Canonical hero",
    )

    canonical_id_by_slug = {row["CanonicalSlug"]: row["CanonicalId"] for row in canonical_rows}
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
        printings_by_card_unique.setdefault(card_unique, []).append(row)

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
            printings = printings_by_card_unique.get(card.get("Unique ID", ""), [])
            earliest_release = ""
            for entry in printings:
                set_id = (entry.get("Set ID") or "").strip()
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
                    "YoungHero": ("true" if is_young_hero_card(card.get("Types", "")) else "false"),
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
                "YoungHero": row["YoungHero"],
            }
        )
        printings_rows.extend(hero_printing_rows(hero_game_id, row["Printings"]))

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
    printings_fieldnames = [
        "HeroGameId",
        "SetId",
        "CardId",
        "Rarity",
        "PrintingUniqueId",
        "Foiling",
        "ArtVariation",
        "Artist",
    ]

    printings_rows = dedupe_printings(printings_rows)
    game_rows, printings_rows, canonical_rows = sort_like_db_export(game_rows, printings_rows, canonical_rows)

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
