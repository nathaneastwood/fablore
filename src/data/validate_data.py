"""Validate pipe-delimited data CSVs under ``src/data/``.

Checks that required identifier columns are non-empty on data rows, and that
selected foreign keys resolve (e.g. story junctions to NPCs, heroes, locations, weapons, equipment).
For heroes, each ``heroes-game.csv`` ``CardName`` must resolve to the same ``CanonicalId`` as
``create_heroes_csv.generate_heroes_csv`` would assign given ``heroes-canonical.csv`` (display
``CanonicalHero`` and slug/alias rules); printed titles need not match ``CanonicalHero`` verbatim.
``stories.csv`` ``StoryType`` values must match :data:`ALLOWED_STORY_TYPES` (``src/`` lore roots).

Intended to run after generators such as ``create_heroes_csv.py``, ``create_weapons_csv.py``,
``create_equipment_csv.py``, ``create_sets_csv.py``, ``create_classes_talents_csv.py``, or after using
``story.py`` to update junction data::

    python3 src/data/validate_data.py

Exits with status ``1`` and prints ``ALERT:`` lines to stderr when a rule fails;
exits ``0`` when all checks pass.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

from mdbook_heading_ids import (  # noqa: E402
    collect_heading_anchor_ids_from_path,
    format_fragment_suggestion,
    world_lore_markdown_path,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"
SRC = ROOT / "src"

# Characters mdBook ``normalize_id`` can emit (Unicode ``isalnum()`` letters, plus ``._-``).
_LORE_FRAGMENT_SAFE = re.compile(r"^[\w.-]+\Z", re.UNICODE)


def _check_location_lore_fragments(locations_path: Path) -> list[str]:
    """Flag ``LoreFragment`` values that cannot be mdBook heading ``id`` fragments."""
    if not locations_path.is_file():
        return []
    fieldnames, rows = read_pipe_csv(locations_path)
    if "LoreFragment" not in fieldnames:
        return []
    alerts: list[str] = []
    for row in rows:
        raw = (row.get("LoreFragment") or "").strip().lstrip("#")
        if not raw:
            continue
        if not _LORE_FRAGMENT_SAFE.match(raw):
            lid = (row.get("LocationId") or "").strip()
            alerts.append(
                f"locations.csv LocationId={lid!r}: LoreFragment {raw!r} should use "
                "only characters mdBook allows in heading ids (Unicode letters/digits, "
                "``_``, ``-``, ``.``)."
            )
    return alerts


def _check_location_lore_fragments_match_headings(
    locations_path: Path, regions_path: Path, src_root: Path
) -> list[str]:
    """Ensure each ``LoreFragment`` matches an mdBook heading id on the region's world lore page."""
    alerts: list[str] = []
    if not locations_path.is_file():
        return alerts
    fieldnames, loc_rows = read_pipe_csv(locations_path)
    if "LoreFragment" not in fieldnames:
        return alerts
    cache: dict[str, list[str]] = {}
    for row in loc_rows:
        raw = (row.get("LoreFragment") or "").strip().lstrip("#")
        if not raw or not _LORE_FRAGMENT_SAFE.match(raw):
            continue
        lid = (row.get("LocationId") or "").strip()
        rid = (row.get("RegionId") or "").strip()
        if not rid:
            alerts.append(
                f"locations.csv LocationId={lid!r}: LoreFragment {raw!r} is set but "
                "RegionId is empty (cannot resolve world lore file)."
            )
            continue
        md_path = world_lore_markdown_path(src_root, regions_path, rid)
        if md_path is None:
            alerts.append(
                f"locations.csv LocationId={lid!r}: LoreFragment {raw!r} but region "
                f"{rid!r} has no WorldOfRatheStoryKey in regions.csv."
            )
            continue
        if not md_path.is_file():
            alerts.append(
                f"locations.csv LocationId={lid!r}: LoreFragment {raw!r} but world lore file "
                f"missing: {md_path.relative_to(src_root)}"
            )
            continue
        key = str(md_path.resolve())
        if key not in cache:
            cache[key] = collect_heading_anchor_ids_from_path(md_path)
        ids = cache[key]
        if raw not in ids:
            rel = md_path.relative_to(src_root).as_posix()
            alerts.append(
                f"locations.csv LocationId={lid!r}: LoreFragment {raw!r} is not a heading id "
                f"in {rel}. Valid heading ids include: {format_fragment_suggestion(ids)}"
            )
    return alerts


# First path segment under ``src/`` for lore markdown; keep in sync when adding a new
# top-level story directory. ``story.py`` / ``create_stories_index.py`` should use these
# values for ``StoryType``.
ALLOWED_STORY_TYPES: frozenset[str] = frozenset(
    {
        "archive",
        "digital-tiles",
        "equipment",
        "flavour",
        "heroes-of-rathe",
        "main-story",
        "other-characters",
        "short-stories",
        "weapons",
        "world-of-rathe",
    }
)


def _pipe_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Load a pipe-delimited CSV into header fieldnames and row dicts.

    Leading ``#`` comment lines (e.g. auto-generation banners) are skipped.

    Args:
        path: CSV file path.

    Returns:
        A tuple ``(fieldnames, rows)``. If the file is missing, returns
        ``([], [])``.
    """
    return read_pipe_csv(path)


def _check_ids(path: Path, id_columns: tuple[str, ...], label: str) -> list[str]:
    """Verify required id columns are present and non-empty for each data row.

    Args:
        path: CSV file to validate.
        id_columns: Column names that must be non-blank on every row.
        label: Human-readable category for error messages.

    Returns:
        A list of alert strings (empty if all checks pass).
    """
    alerts: list[str] = []
    fieldnames, rows = _pipe_rows(path)
    if not fieldnames:
        return alerts
    for col in id_columns:
        if col not in fieldnames:
            alerts.append(
                f"{label}: column {col!r} missing in {path.name} (cannot validate)"
            )
    cols_present = [c for c in id_columns if c in fieldnames]
    if not cols_present or not rows:
        return alerts
    for row_num, row in enumerate(rows, start=2):
        for col in cols_present:
            val = (row.get(col) or "").strip()
            if not val:
                alerts.append(
                    f"{label}: {path.name} row {row_num}: empty {col!r} "
                    f"(expected a generated ID)"
                )
    return alerts


def _id_set_from_column(path: Path, column: str) -> set[str]:
    """Collect distinct non-empty values for one column.

    Args:
        path: CSV file path.
        column: Header name to read.

    Returns:
        Set of stripped cell values. Returns an empty set if the column is
        missing or the file does not exist.
    """
    fieldnames, rows = _pipe_rows(path)
    if column not in fieldnames:
        return set()
    return {(r.get(column) or "").strip() for r in rows if (r.get(column) or "").strip()}


def _check_stories_story_type_allowlist(stories_path: Path) -> list[str]:
    """Ensure ``StoryType`` is in :data:`ALLOWED_STORY_TYPES` and dirs exist under ``src/``.

    Args:
        stories_path: ``stories.csv`` path.

    Returns:
        Alert strings; empty when all rows and allowlist layout are valid.
    """
    alerts: list[str] = []
    for story_type in sorted(ALLOWED_STORY_TYPES):
        seg = SRC / story_type
        if not seg.is_dir():
            alerts.append(
                "Stories: ALLOWED_STORY_TYPES in validate_data.py includes "
                f"{story_type!r} but {seg} is not a directory"
            )

    fieldnames, rows = _pipe_rows(stories_path)
    if not fieldnames or "StoryType" not in fieldnames or not rows:
        return alerts
    for row_num, row in enumerate(rows, start=2):
        st = (row.get("StoryType") or "").strip()
        if not st:
            continue
        if st not in ALLOWED_STORY_TYPES:
            alerts.append(
                f"Stories: {stories_path.name} row {row_num}: unknown StoryType {st!r} "
                f"(not in validate_data.ALLOWED_STORY_TYPES)"
            )
    return alerts


def _check_fk_column(
    child_path: Path,
    fk_column: str,
    parent_ids: set[str],
    parent_desc: str,
    label: str,
) -> list[str]:
    """Flag child rows whose FK value is absent from the parent id set.

    Args:
        child_path: Junction or child CSV path.
        fk_column: Foreign-key column name on the child file.
        parent_ids: Acceptable parent id values.
        parent_desc: Short description of the parent table (for messages).
        label: Human-readable category for error messages.

    Returns:
        A list of alert strings (empty if all FK values are valid).
    """
    alerts: list[str] = []
    fieldnames, rows = _pipe_rows(child_path)
    if not fieldnames or fk_column not in fieldnames or not rows:
        return alerts
    for row_num, row in enumerate(rows, start=2):
        fk = (row.get(fk_column) or "").strip()
        if fk and fk not in parent_ids:
            alerts.append(
                f"{label}: {child_path.name} row {row_num}: {fk_column}={fk!r} "
                f"not in {parent_desc}"
            )
    return alerts


def _check_heroes_game_cardname_resolution(
    canonical_path: Path, game_path: Path
) -> list[str]:
    """Flag ``heroes-game`` rows whose ``CardName`` does not map to the row ``CanonicalId``.

    Replays the slug resolution used by :func:`create_heroes_csv.generate_heroes_csv`
    so hand-edited ``heroes-game.csv`` rows cannot drift from canonical + card-name
    rules without ``create_heroes_csv`` being re-run. Card-name aliases from
    ``hero-card-name-aliases.csv`` are applied only when the target slug exists
    on the given canonical file (so minimal fixtures stay self-contained); see
    :func:`_check_hero_card_name_alias_slugs_in_canonical` for full-roster alias checks.

    Args:
        canonical_path: ``heroes-canonical.csv`` path.
        game_path: ``heroes-game.csv`` path.

    Returns:
        Alert strings; empty when every game row is consistent.
    """
    from create_heroes_csv import apply_lore_canonical_override, split_name_variant
    from hero_overrides import load_canonical_hero_card_name_aliases
    from text_utils import normalize_name

    aliases = load_canonical_hero_card_name_aliases()

    alerts: list[str] = []
    c_fields, canonical_rows = _pipe_rows(canonical_path)
    g_fields, game_rows = _pipe_rows(game_path)
    if not c_fields or not g_fields:
        return alerts
    if not all(
        col in c_fields
        for col in ("CanonicalId", "CanonicalSlug", "CanonicalHero")
    ):
        return alerts
    if "CardName" not in g_fields or "CanonicalId" not in g_fields:
        return alerts

    canonical_id_by_slug: dict[str, str] = {}
    canonical_slug_by_name: dict[str, str] = {}
    for row in canonical_rows:
        slug = (row.get("CanonicalSlug") or "").strip()
        cid = (row.get("CanonicalId") or "").strip()
        hero = (row.get("CanonicalHero") or "").strip()
        if slug and cid:
            canonical_id_by_slug[slug] = cid
        if slug and hero:
            name_key = normalize_name(hero)
            canonical_slug_by_name.setdefault(name_key, slug)

    for alt_name_key, slug in aliases.items():
        if slug in canonical_id_by_slug:
            canonical_slug_by_name[alt_name_key] = slug

    for row_num, row in enumerate(game_rows, start=2):
        card_name = (row.get("CardName") or "").strip()
        cid = (row.get("CanonicalId") or "").strip()
        if not card_name or not cid:
            continue
        name, comma_subtitle = split_name_variant(card_name)
        name_key = normalize_name(name)
        base_slug = canonical_slug_by_name.get(name_key, name_key)
        canonical_slug = apply_lore_canonical_override(base_slug, name, comma_subtitle)
        expected_id = canonical_id_by_slug.get(canonical_slug, "")
        if not expected_id:
            alerts.append(
                "Heroes game: "
                f"{game_path.name} row {row_num}: CardName {card_name!r} resolves to "
                f"unknown slug {canonical_slug!r} (check heroes-canonical.csv and "
                "hero_overrides.LORE_CANONICAL_OVERRIDES / hero-card-name-aliases.csv)"
            )
        elif expected_id != cid:
            alerts.append(
                "Heroes game: "
                f"{game_path.name} row {row_num}: CardName {card_name!r} resolves to "
                f"CanonicalId {expected_id!r} but row has {cid!r}"
            )
    return alerts


def _check_heroes_game_young_hero_column(game_path: Path) -> list[str]:
    """Ensure ``heroes-game.csv`` ``YoungHero`` is ``true`` or ``false`` on every row.

    Args:
        game_path: ``heroes-game.csv`` path.

    Returns:
        Alert strings; empty when the column is absent (legacy file) or all values are valid.
    """
    allowed = frozenset({"true", "false"})
    alerts: list[str] = []
    fieldnames, rows = _pipe_rows(game_path)
    if not fieldnames or "YoungHero" not in fieldnames or not rows:
        return alerts
    for row_num, row in enumerate(rows, start=2):
        val = (row.get("YoungHero") or "").strip().lower()
        if val not in allowed:
            alerts.append(
                "Heroes game: "
                f"{game_path.name} row {row_num}: YoungHero must be 'true' or 'false', "
                f"got {row.get('YoungHero')!r}"
            )
    return alerts


def _check_hero_card_name_alias_slugs_in_canonical(canonical_path: Path) -> list[str]:
    """Ensure every ``hero-card-name-aliases.csv`` target slug exists on disk.

    The alias map is data in ``src/data/hero-card-name-aliases.csv`` (loaded via
    :func:`hero_overrides.load_canonical_hero_card_name_aliases`); this check
    runs against the committed ``heroes-canonical.csv`` so typos in alias targets
    are caught without requiring a full card export run.

    Args:
        canonical_path: ``heroes-canonical.csv`` path.

    Returns:
        Alert strings; empty when every alias slug is present.
    """
    from hero_overrides import load_canonical_hero_card_name_aliases

    alerts: list[str] = []
    fieldnames, rows = _pipe_rows(canonical_path)
    if not fieldnames or "CanonicalSlug" not in fieldnames:
        return alerts
    slugs = {
        (r.get("CanonicalSlug") or "").strip()
        for r in rows
        if (r.get("CanonicalSlug") or "").strip()
    }
    for alt_name_key, slug in load_canonical_hero_card_name_aliases().items():
        if slug not in slugs:
            alerts.append(
                f"Heroes canonical: hero-card-name-aliases.csv maps "
                f"{alt_name_key!r} to unknown CanonicalSlug {slug!r}"
            )
    return alerts


def collect_alerts() -> list[str]:
    """Run all non-empty-id checks and foreign-key checks.

    Includes story junction FKs to ``heroes-canonical``, ``weapons-canonical``,
    and ``equipment-canonical`` where applicable. Hero ``CardName`` values must
    resolve to each row's ``CanonicalId`` under the same rules as ``create_heroes_csv``.
    ``stories.csv`` ``StoryType`` must be a member of :data:`ALLOWED_STORY_TYPES`.

    Returns:
        A flat list of human-readable problem strings (empty when valid).
    """
    alerts: list[str] = []

    checks: list[tuple[Path, tuple[str, ...], str]] = [
        (DATA / "set-types.csv", ("SetTypeId",), "Set types"),
        (DATA / "sets.csv", ("SetId", "SetTypeId"), "Sets"),
        (DATA / "heroes-canonical.csv", ("CanonicalId", "CanonicalSlug", "CanonicalHero"), "Heroes canonical"),
        (DATA / "heroes-game.csv", ("HeroGameId", "CardName", "CanonicalId"), "Heroes game"),
        (DATA / "classes.csv", ("ClassId", "ClassName"), "Classes (shared)"),
        (DATA / "talents.csv", ("TalentId", "TalentName"), "Talents (shared)"),
        (DATA / "heroes-printings.csv", ("HeroGameId", "SetId", "CardId"), "Heroes printings"),
        (
            DATA / "weapons-canonical.csv",
            ("CanonicalWeaponId", "CanonicalSlug"),
            "Weapons canonical",
        ),
        (
            DATA / "weapons-game.csv",
            ("WeaponGameId", "CardName", "CanonicalWeaponId"),
            "Weapons game",
        ),
        (DATA / "weapons-printings.csv", ("WeaponGameId", "SetId", "CardId"), "Weapons printings"),
        (
            DATA / "equipment-canonical.csv",
            ("CanonicalEquipmentId", "CanonicalSlug"),
            "Equipment canonical",
        ),
        (
            DATA / "equipment-game.csv",
            ("EquipmentGameId", "CardName", "CanonicalEquipmentId"),
            "Equipment game",
        ),
        (
            DATA / "equipment-printings.csv",
            ("EquipmentGameId", "SetId", "CardId"),
            "Equipment printings",
        ),
        (DATA / "npcs.csv", ("CharacterId", "Name", "Status"), "NPCs"),
        (DATA / "locations.csv", ("LocationId", "Name"), "Locations"),
        (DATA / "regions.csv", ("RegionId",), "Regions"),
        (DATA / "flora.csv", ("FloraId",), "Flora"),
        (DATA / "fauna.csv", ("FaunaId",), "Fauna"),
        (DATA / "food-and-drink.csv", ("FoodDrinkId",), "Food and drink"),
        (DATA / "monsters.csv", ("MonsterId",), "Monsters"),
        (DATA / "stories.csv", ("StoryId", "StoryKey", "StoryType"), "Stories"),
        (DATA / "story-npcs.csv", ("StoryId", "CharacterId"), "Story ↔ NPC links"),
        (DATA / "story-heroes.csv", ("StoryId", "CanonicalId"), "Story ↔ hero links"),
        (DATA / "story-locations.csv", ("StoryId", "LocationId"), "Story ↔ location links"),
        (DATA / "story-monsters.csv", ("StoryId", "MonsterId"), "Story ↔ monster links"),
        (DATA / "story-fauna.csv", ("StoryId", "FaunaId"), "Story ↔ fauna links"),
        (DATA / "story-flora.csv", ("StoryId", "FloraId"), "Story ↔ flora links"),
        (DATA / "story-food-drink.csv", ("StoryId", "FoodDrinkId"), "Story ↔ food/drink links"),
        (DATA / "story-weapons.csv", ("StoryId", "CanonicalWeaponId"), "Story ↔ weapon links"),
        (DATA / "story-equipment.csv", ("StoryId", "CanonicalEquipmentId"), "Story ↔ equipment links"),
    ]

    for path, cols, label in checks:
        if not path.is_file():
            continue
        _, rows = _pipe_rows(path)
        if len(rows) == 0 and path.name.startswith("story-"):
            # Header-only junction files are allowed until filled.
            continue
        alerts.extend(_check_ids(path, cols, label))

    stories_path = DATA / "stories.csv"
    if stories_path.is_file():
        alerts.extend(_check_stories_story_type_allowlist(stories_path))

    canonical_path = DATA / "heroes-canonical.csv"
    game_path = DATA / "heroes-game.csv"
    printings_path = DATA / "heroes-printings.csv"
    story_heroes_path = DATA / "story-heroes.csv"

    canonical_ids = _id_set_from_column(canonical_path, "CanonicalId")
    hero_game_ids = _id_set_from_column(game_path, "HeroGameId")

    if canonical_ids:
        alerts.extend(
            _check_fk_column(
                story_heroes_path,
                "CanonicalId",
                canonical_ids,
                "heroes-canonical.csv CanonicalId",
                "Story ↔ hero links",
            )
        )
    if hero_game_ids:
        alerts.extend(
            _check_fk_column(
                printings_path,
                "HeroGameId",
                hero_game_ids,
                "heroes-game.csv HeroGameId",
                "Heroes printings",
            )
        )

    if canonical_path.is_file() and game_path.is_file():
        alerts.extend(_check_heroes_game_cardname_resolution(canonical_path, game_path))

    if game_path.is_file():
        alerts.extend(_check_heroes_game_young_hero_column(game_path))

    if canonical_path.is_file():
        alerts.extend(_check_hero_card_name_alias_slugs_in_canonical(canonical_path))

    weapons_game_path = DATA / "weapons-game.csv"
    weapons_printings_path = DATA / "weapons-printings.csv"
    weapon_game_ids = _id_set_from_column(weapons_game_path, "WeaponGameId")
    if weapon_game_ids:
        alerts.extend(
            _check_fk_column(
                weapons_printings_path,
                "WeaponGameId",
                weapon_game_ids,
                "weapons-game.csv WeaponGameId",
                "Weapons printings",
            )
        )

    weapons_canonical_path = DATA / "weapons-canonical.csv"
    canonical_weapon_ids = _id_set_from_column(weapons_canonical_path, "CanonicalWeaponId")
    if canonical_weapon_ids:
        alerts.extend(
            _check_fk_column(
                weapons_game_path,
                "CanonicalWeaponId",
                canonical_weapon_ids,
                "weapons-canonical.csv CanonicalWeaponId",
                "Weapons game",
            )
        )
        story_weapons_path = DATA / "story-weapons.csv"
        alerts.extend(
            _check_fk_column(
                story_weapons_path,
                "CanonicalWeaponId",
                canonical_weapon_ids,
                "weapons-canonical.csv CanonicalWeaponId",
                "Story ↔ weapon links",
            )
        )

    equipment_game_path = DATA / "equipment-game.csv"
    equipment_printings_path = DATA / "equipment-printings.csv"
    equipment_canonical_path = DATA / "equipment-canonical.csv"
    equipment_game_ids = _id_set_from_column(equipment_game_path, "EquipmentGameId")
    canonical_equipment_ids = _id_set_from_column(
        equipment_canonical_path, "CanonicalEquipmentId"
    )
    if canonical_equipment_ids:
        alerts.extend(
            _check_fk_column(
                equipment_game_path,
                "CanonicalEquipmentId",
                canonical_equipment_ids,
                "equipment-canonical.csv CanonicalEquipmentId",
                "Equipment game",
            )
        )
        story_equipment_path = DATA / "story-equipment.csv"
        alerts.extend(
            _check_fk_column(
                story_equipment_path,
                "CanonicalEquipmentId",
                canonical_equipment_ids,
                "equipment-canonical.csv CanonicalEquipmentId",
                "Story ↔ equipment links",
            )
        )
    if equipment_game_ids:
        alerts.extend(
            _check_fk_column(
                equipment_printings_path,
                "EquipmentGameId",
                equipment_game_ids,
                "equipment-game.csv EquipmentGameId",
                "Equipment printings",
            )
        )

    fauna_path = DATA / "fauna.csv"
    story_fauna_path = DATA / "story-fauna.csv"
    fauna_ids = _id_set_from_column(fauna_path, "FaunaId")
    if fauna_ids:
        alerts.extend(
            _check_fk_column(
                story_fauna_path,
                "FaunaId",
                fauna_ids,
                "fauna.csv FaunaId",
                "Story ↔ fauna links",
            )
        )

    region_ids = _id_set_from_column(DATA / "regions.csv", "RegionId")
    locations_path = DATA / "locations.csv"
    if region_ids and locations_path.is_file():
        alerts.extend(
            _check_fk_column(
                locations_path,
                "RegionId",
                region_ids,
                "regions.csv RegionId",
                "Locations",
            )
        )

    alerts.extend(_check_location_lore_fragments(DATA / "locations.csv"))
    alerts.extend(
        _check_location_lore_fragments_match_headings(
            DATA / "locations.csv", DATA / "regions.csv", SRC
        )
    )

    return alerts


def main() -> int:
    """CLI entry: print alerts to stderr; return process exit code.

    Returns:
        ``0`` if no alerts, ``1`` otherwise.
    """
    alerts = collect_alerts()
    for msg in alerts:
        print(f"ALERT: {msg}", file=sys.stderr)
    if alerts:
        print(
            f"\nALERT: {len(alerts)} data validation issue(s). Fix generators or source CSVs.",
            file=sys.stderr,
        )
        return 1
    print("validate_data: OK (no empty required IDs or broken FK links in checked files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
