"""Export the fablore database back to pipe-delimited CSV files and JSON.

CSV output exactly matches the format that the mdBook preprocessors and
``validate_data.py`` expect: pipe-delimited, auto-generation banner as the
first line, column order matching the original CSVs. All files are written
into ``data_dir/csv/``.

The ``NarratedVideos`` column (legacy JSON blob) is **not** re-emitted in
``stories.csv`` — narrated videos live in the ``narrated_videos`` table and are
exported to ``story-narrated-videos.csv`` (and included in :func:`dump_to_json`).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import (  # noqa: E402
    REGENERATE_CLASSES_TALENTS as _CMD_CLASSES,
    REGENERATE_CREATE_EQUIPMENT as _CMD_EQUIPMENT,
    REGENERATE_CREATE_HEROES as _CMD_HEROES,
    REGENERATE_CREATE_SETS as _CMD_SETS,
    REGENERATE_CREATE_STORIES_INDEX as _CMD_STORIES,
    REGENERATE_CREATE_WEAPONS as _CMD_WEAPONS,
    write_pipe_csv_autogen,
)
import db._queries as q  # noqa: E402

_CMD_REGISTRY = "Use the Database class in src/data/db/ (db.upsert_story)."
_CMD_JUNCTIONS = "Use the Database class in src/data/db/ (db.upsert_story / db.remove_story)."


_Columns = tuple[tuple[str, str], ...]
"""``(db_col, Header)`` pairs: one entry per CSV column, in file order."""


def _write(path: Path, banner_cmd: str, cols: _Columns, rows: list[sqlite3.Row]) -> None:
    """Write ``rows`` to ``path`` with one column per ``(db_col, Header)`` pair."""
    write_pipe_csv_autogen(
        path,
        [header for _, header in cols],
        [{header: r[db_col] for db_col, header in cols} for r in rows],
        regenerate_command=banner_cmd,
    )


def _export_story_narrated_videos(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = conn.execute(
        """
        SELECT nv.story_id, nv.author, nv.source_link, nv.channel_link
        FROM narrated_videos nv
        INNER JOIN stories s ON s.story_id = nv.story_id
        ORDER BY s.story_key, nv.narrated_video_id
        """
    ).fetchall()
    _write(
        csv_dir / "story-narrated-videos.csv",
        _CMD_STORIES,
        (
            ("story_id", "StoryId"),
            ("author", "Author"),
            ("source_link", "SourceLink"),
            ("channel_link", "ChannelLink"),
        ),
        rows,
    )


def export_all(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Regenerate every database-backed CSV file in ``data_dir/csv/``.

    Five CSVs in that directory are never written here: ``story-arcs.csv`` and
    ``reviewed-name-pairs.csv`` are hand-maintained, ``heroes-ll.csv`` and
    ``heroes-fabtcg.csv`` are written by ``create_heroes_csv.py`` (from the
    fabtcg.com hero API) and ``hero-card-name-aliases.csv`` is an input to it. Everything else is exported.

    Calls :func:`export_stories`, :func:`export_registry_tables` and
    :func:`export_story_junctions` rather than re-listing their exporters, so
    a new exporter added to one of the narrower functions is covered here too.
    (Re-listing them once let an export run clean and leave groups, aliases,
    kinds, titles, kin and professions stale.)

    Args:
        conn: Open database connection.
        data_dir: Repository ``src/data/`` directory.
    """
    csv_dir = data_dir / "csv"
    export_stories(conn, data_dir)
    export_registry_tables(conn, data_dir)
    _export_heroes_canonical(conn, csv_dir)
    _export_heroes_game(conn, csv_dir)
    _export_heroes_printings(conn, csv_dir)
    _export_weapons_canonical(conn, csv_dir)
    _export_weapons_game(conn, csv_dir)
    _export_weapons_printings(conn, csv_dir)
    _export_equipment_canonical(conn, csv_dir)
    _export_equipment_game(conn, csv_dir)
    _export_equipment_printings(conn, csv_dir)
    _export_classes(conn, csv_dir)
    _export_talents(conn, csv_dir)
    _export_sets(conn, csv_dir)
    _export_set_types(conn, csv_dir)
    export_story_junctions(conn, data_dir)


def export_stories(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Write ``stories.csv`` and ``story-narrated-videos.csv``.

    A narrated video belongs to one story and is written and deleted with it,
    so every write path that exports stories exports the videos too. Leaving
    them out let ``upsert_story(narrated_videos=…)`` change only the DB, and
    left ``remove_story`` a CSV row naming a StoryId that no longer exists —
    which fails the foreign key on the next fresh seed.
    """
    csv_dir = data_dir / "csv"
    _export_stories(conn, csv_dir)
    _export_story_narrated_videos(conn, csv_dir)


def export_registry_tables(conn: sqlite3.Connection, data_dir: Path) -> None:
    csv_dir = data_dir / "csv"
    _export_regions(conn, csv_dir)
    _export_locations(conn, csv_dir)
    _export_characters(conn, csv_dir)
    _export_character_heroes(conn, csv_dir)
    _export_monsters(conn, csv_dir)
    _export_fauna(conn, csv_dir)
    _export_flora(conn, csv_dir)
    _export_food_drink(conn, csv_dir)
    _export_groups(conn, csv_dir)
    _export_group_members(conn, csv_dir)
    _export_alternate_names(conn, csv_dir)
    _export_kinds(conn, csv_dir)
    _export_titles(conn, csv_dir)
    _export_title_holders(conn, csv_dir)
    _export_character_kin(conn, csv_dir)
    _export_professions(conn, csv_dir)


def export_story_junctions(conn: sqlite3.Connection, data_dir: Path) -> None:
    _export_story_junctions(conn, data_dir / "csv")


# ---------------------------------------------------------------------------
# Per-table exporters
# ---------------------------------------------------------------------------


def _export_stories(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "stories.csv",
        _CMD_STORIES,
        (
            ("story_id", "StoryId"),
            ("story_key", "StoryKey"),
            ("story_type", "StoryType"),
            ("title", "Title"),
            ("authors", "Authors"),
            ("artists", "Artists"),
            ("source_link", "SourceLink"),
            ("publication_date", "PublicationDate"),
            ("thumbnail_image_link", "ThumbnailImageLink"),
        ),
        q.select_all_stories(conn),
    )


def _export_regions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "regions.csv",
        _CMD_REGISTRY,
        (
            ("region_id", "RegionId"),
            ("region_name", "RegionName"),
            ("world_of_rathe_story_key", "WorldOfRatheStoryKey"),
        ),
        q.select_all_regions(conn),
    )


def _export_locations(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "locations.csv",
        _CMD_REGISTRY,
        (
            ("location_id", "LocationId"),
            ("name", "Name"),
            ("region_id", "RegionId"),
            ("notes", "Notes"),
            ("lore_fragment", "LoreFragment"),
            ("parent_location_id", "ParentLocationId"),
        ),
        q.select_all_locations(conn),
    )


def _export_groups(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "groups.csv",
        _CMD_REGISTRY,
        (
            ("group_id", "GroupId"),
            ("name", "Name"),
            ("category", "Category"),
            ("notes", "Notes"),
            ("parent_group_id", "ParentGroupId"),
            ("location_id", "LocationId"),
            ("lore_story_key", "LoreStoryKey"),
            ("lore_fragment", "LoreFragment"),
        ),
        q.select_all_groups(conn),
    )


def _export_group_members(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write the membership table (R1).

    Not part of ``_JUNCTION_EXPORT_SPECS``: this hangs off a group, not a story,
    and its ``StoryKey`` is evidence for the membership (D2) rather than the
    link itself. One table since migration 18.
    """
    rows = conn.execute(
        "SELECT group_id, character_id, story_key FROM group_characters ORDER BY group_id, character_id"
    ).fetchall()
    _write(
        csv_dir / "group-characters.csv",
        _CMD_REGISTRY,
        (("group_id", "GroupId"), ("character_id", "CharacterId"), ("story_key", "StoryKey")),
        rows,
    )


def _export_alternate_names(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write the three alternate-name tables (R4, R6).

    Like the membership tables, these hang off their entity rather than a story,
    so they are not story junctions and do not belong in
    ``_JUNCTION_EXPORT_SPECS``.
    """
    for table, csv_name, cols in (
        (
            "character_epithets",
            "character-epithets.csv",
            (("character_id", "CharacterId"), ("name", "Name"), ("label", "Label")),
        ),
        (
            "location_aliases",
            "location-aliases.csv",
            (("location_id", "LocationId"), ("alias", "Alias"), ("era", "Era")),
        ),
        ("group_aliases", "group-aliases.csv", (("group_id", "GroupId"), ("alias", "Alias"))),
    ):
        db_cols = [c for c, _ in cols]
        owner = db_cols[0]
        rows = conn.execute(
            f"SELECT {', '.join(db_cols)} FROM {table} ORDER BY {owner}, sort_order, {db_cols[1]}"
        ).fetchall()
        _write(csv_dir / csv_name, _CMD_REGISTRY, cols, rows)


def _export_kinds(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``kinds.csv``, ``character-kinds.csv`` and ``kind-aliases.csv`` (R2).

    Three files for what was one column, which is the shape of the fix: a kind
    is a registry row, a character's kind is a junction, and a plural is an
    alias.
    """
    _write(
        csv_dir / "kinds.csv",
        _CMD_REGISTRY,
        (("kind_id", "KindId"), ("name", "Name"), ("notes", "Notes")),
        q.select_all_kinds(conn),
    )
    junction = conn.execute(
        "SELECT character_id, kind_id FROM character_kinds ORDER BY character_id, sort_order, kind_id"
    ).fetchall()
    _write(
        csv_dir / "character-kinds.csv",
        _CMD_REGISTRY,
        (("character_id", "CharacterId"), ("kind_id", "KindId")),
        junction,
    )
    aliases = conn.execute("SELECT kind_id, alias FROM kind_aliases ORDER BY kind_id, sort_order, alias").fetchall()
    _write(
        csv_dir / "kind-aliases.csv",
        _CMD_REGISTRY,
        (("kind_id", "KindId"), ("alias", "Alias")),
        aliases,
    )


def _export_titles(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "titles.csv",
        _CMD_REGISTRY,
        (("title_id", "TitleId"), ("name", "Name"), ("group_id", "GroupId"), ("notes", "Notes")),
        q.select_all_titles(conn),
    )


def _export_title_holders(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``title-holders.csv`` (R3).

    Not part of ``_JUNCTION_EXPORT_SPECS``: this hangs off a title, not a story,
    and its ``StoryKey`` is evidence for the holder (like ``group-npcs.csv``'s),
    not the link itself.
    """
    rows = conn.execute(
        "SELECT title_id, character_id, ordinal, story_key FROM title_holders ORDER BY title_id, ordinal, character_id"
    ).fetchall()
    _write(
        csv_dir / "title-holders.csv",
        _CMD_REGISTRY,
        (
            ("title_id", "TitleId"),
            ("character_id", "CharacterId"),
            ("ordinal", "Ordinal"),
            ("story_key", "StoryKey"),
        ),
        rows,
    )


def _export_character_kin(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``character-kin.csv`` (R8).

    Not part of ``_JUNCTION_EXPORT_SPECS``: this hangs off a character, not a
    story, and its ``StoryKey`` is evidence for the kin fact (like
    ``group-npcs.csv``'s), not the link itself. Only the stated direction is
    ever written — the inverse is derived at read time and never stored, so
    this file can never disagree with itself about who is whose parent.

    ``Qualifier`` (migration 21) is ``blood`` or ``adoptive`` — see
    ``db._queries.KIN_QUALIFIERS``.
    """
    rows = conn.execute(
        "SELECT character_id, relative_id, relation, story_key, qualifier FROM character_kin "
        "ORDER BY character_id, relative_id, relation"
    ).fetchall()
    _write(
        csv_dir / "character-kin.csv",
        _CMD_REGISTRY,
        (
            ("character_id", "CharacterId"),
            ("relative_id", "RelativeId"),
            ("relation", "Relation"),
            ("story_key", "StoryKey"),
            ("qualifier", "Qualifier"),
        ),
        rows,
    )


def _export_professions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``professions.csv`` and ``character-professions.csv`` (R9).

    Two files, not three: a profession is a registry row and a character's
    profession is a junction, the same split ``kinds.csv``/``character-kinds.csv``
    make — but there is no third, alias file. See
    ``entries/catalogue/professions.py`` for why.
    """
    _write(
        csv_dir / "professions.csv",
        _CMD_REGISTRY,
        (("profession_id", "ProfessionId"), ("name", "Name"), ("notes", "Notes")),
        q.select_all_professions(conn),
    )
    junction = conn.execute(
        "SELECT character_id, profession_id, sort_order FROM character_professions "
        "ORDER BY character_id, sort_order, profession_id"
    ).fetchall()
    _write(
        csv_dir / "character-professions.csv",
        _CMD_REGISTRY,
        (("character_id", "CharacterId"), ("profession_id", "ProfessionId"), ("sort_order", "SortOrder")),
        junction,
    )


def _export_characters(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "characters.csv",
        _CMD_REGISTRY,
        (
            ("character_id", "CharacterId"),
            ("name", "Name"),
            ("status", "Status"),
            ("other_characters_story_key", "OtherCharactersStoryKey"),
            ("summary", "Summary"),
        ),
        q.select_all_characters(conn),
    )


def _export_character_heroes(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``character-heroes.csv`` — the identity spine (migration 12)."""
    _write(
        csv_dir / "character-heroes.csv",
        _CMD_REGISTRY,
        (("canonical_id", "CanonicalId"), ("character_id", "CharacterId")),
        q.select_all_character_heroes(conn),
    )


def _export_monsters(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "monsters.csv",
        _CMD_REGISTRY,
        (("monster_id", "MonsterId"), ("name", "Name"), ("description", "Description")),
        q.select_all_monsters(conn),
    )


def _export_fauna(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "fauna.csv",
        _CMD_REGISTRY,
        (("fauna_id", "FaunaId"), ("name", "Name"), ("description", "Description")),
        q.select_all_fauna(conn),
    )


def _export_flora(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "flora.csv",
        _CMD_REGISTRY,
        (("flora_id", "FloraId"), ("name", "Name"), ("description", "Description")),
        q.select_all_flora(conn),
    )


def _export_food_drink(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "food-and-drink.csv",
        _CMD_REGISTRY,
        (("food_drink_id", "FoodDrinkId"), ("name", "Name"), ("type", "Type")),
        q.select_all_food_drink(conn),
    )


def _export_heroes_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "heroes-canonical.csv",
        _CMD_HEROES,
        (
            ("canonical_id", "CanonicalId"),
            ("canonical_slug", "CanonicalSlug"),
            ("canonical_hero", "CanonicalHero"),
        ),
        q.select_all_heroes_canonical(conn),
    )


def _export_heroes_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "heroes-game.csv",
        _CMD_HEROES,
        (
            ("hero_game_id", "HeroGameId"),
            ("card_name", "CardName"),
            ("canonical_id", "CanonicalId"),
            ("class_ids", "ClassIds"),
            ("talent_ids", "TalentIds"),
            ("health", "Health"),
            ("intellect", "Intellect"),
            ("ability_text", "AbilityText"),
            ("young_hero", "YoungHero"),
        ),
        q.select_all_heroes_game(conn),
    )


def _export_heroes_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "heroes-printings.csv",
        _CMD_HEROES,
        (
            ("hero_game_id", "HeroGameId"),
            ("set_id", "SetId"),
            ("card_id", "CardId"),
            ("rarity", "Rarity"),
            ("printing_unique_id", "PrintingUniqueId"),
            ("foiling", "Foiling"),
            ("art_variation", "ArtVariation"),
            ("artist", "Artist"),
        ),
        q.select_all_heroes_printings(conn),
    )


def _export_weapons_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "weapons-canonical.csv",
        _CMD_WEAPONS,
        (
            ("canonical_weapon_id", "CanonicalWeaponId"),
            ("canonical_slug", "CanonicalSlug"),
            ("canonical_weapon", "CanonicalWeapon"),
        ),
        q.select_all_weapons_canonical(conn),
    )


def _export_weapons_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "weapons-game.csv",
        _CMD_WEAPONS,
        (
            ("weapon_game_id", "WeaponGameId"),
            ("card_name", "CardName"),
            ("canonical_weapon_id", "CanonicalWeaponId"),
            ("class_ids", "ClassIds"),
            ("talent_ids", "TalentIds"),
            ("cost", "Cost"),
            ("power", "Power"),
            ("ability_text", "AbilityText"),
            ("types", "Types"),
        ),
        q.select_all_weapons_game(conn),
    )


def _export_weapons_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "weapons-printings.csv",
        _CMD_WEAPONS,
        (
            ("weapon_game_id", "WeaponGameId"),
            ("set_id", "SetId"),
            ("card_id", "CardId"),
            ("rarity", "Rarity"),
            ("image_url", "ImageURL"),
        ),
        q.select_all_weapons_printings(conn),
    )


def _export_equipment_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "equipment-canonical.csv",
        _CMD_EQUIPMENT,
        (
            ("canonical_equipment_id", "CanonicalEquipmentId"),
            ("canonical_slug", "CanonicalSlug"),
            ("canonical_equipment", "CanonicalEquipment"),
        ),
        q.select_all_equipment_canonical(conn),
    )


def _export_equipment_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "equipment-game.csv",
        _CMD_EQUIPMENT,
        (
            ("equipment_game_id", "EquipmentGameId"),
            ("card_name", "CardName"),
            ("canonical_equipment_id", "CanonicalEquipmentId"),
            ("class_ids", "ClassIds"),
            ("talent_ids", "TalentIds"),
            ("cost", "Cost"),
            ("defense", "Defense"),
            ("ability_text", "AbilityText"),
            ("types", "Types"),
        ),
        q.select_all_equipment_game(conn),
    )


def _export_equipment_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "equipment-printings.csv",
        _CMD_EQUIPMENT,
        (
            ("equipment_game_id", "EquipmentGameId"),
            ("set_id", "SetId"),
            ("card_id", "CardId"),
            ("rarity", "Rarity"),
            ("image_url", "ImageURL"),
        ),
        q.select_all_equipment_printings(conn),
    )


def _export_classes(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "classes.csv",
        _CMD_CLASSES,
        (("class_id", "ClassId"), ("class_name", "ClassName")),
        q.select_all_classes(conn),
    )


def _export_talents(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "talents.csv",
        _CMD_CLASSES,
        (("talent_id", "TalentId"), ("talent_name", "TalentName")),
        q.select_all_talents(conn),
    )


def _export_sets(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "sets.csv",
        _CMD_SETS,
        (
            ("set_id", "SetId"),
            ("set_type_id", "SetTypeId"),
            ("set_name", "SetName"),
            ("initial_release_date", "InitialReleaseDate"),
        ),
        q.select_all_sets(conn),
    )


def _export_set_types(conn: sqlite3.Connection, csv_dir: Path) -> None:
    _write(
        csv_dir / "set-types.csv",
        _CMD_SETS,
        (("set_type_id", "SetTypeId"), ("set_type", "SetType"), ("set_type_layer", "SetTypeLayer")),
        q.select_all_set_types(conn),
    )


_JUNCTION_EXPORT_SPECS: tuple[tuple[str, str, str, str], ...] = (
    ("story_locations", "story-locations.csv", "location_id", "LocationId"),
    ("story_regions", "story-regions.csv", "region_id", "RegionId"),
    ("story_monsters", "story-monsters.csv", "monster_id", "MonsterId"),
    ("story_fauna", "story-fauna.csv", "fauna_id", "FaunaId"),
    ("story_flora", "story-flora.csv", "flora_id", "FloraId"),
    ("story_food_drink", "story-food-drink.csv", "food_drink_id", "FoodDrinkId"),
    ("story_weapons", "story-weapons.csv", "canonical_weapon_id", "CanonicalWeaponId"),
    ("story_equipment", "story-equipment.csv", "canonical_equipment_id", "CanonicalEquipmentId"),
    ("story_groups", "story-groups.csv", "group_id", "GroupId"),
    ("story_titles", "story-titles.csv", "title_id", "TitleId"),
)
"""Plain ``(story_id, entity_id)`` junctions: table, CSV, entity db column, entity header."""


def _export_story_junctions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    # story_characters carries an extra Fragment column, unlike the plain
    # (story_id, entity_id) junctions in _JUNCTION_EXPORT_SPECS.
    rows = conn.execute(
        "SELECT story_id, character_id, fragment FROM story_characters ORDER BY story_id, character_id"
    ).fetchall()
    _write(
        csv_dir / "story-characters.csv",
        _CMD_JUNCTIONS,
        (("story_id", "StoryId"), ("character_id", "CharacterId"), ("fragment", "Fragment")),
        rows,
    )

    for table, csv_name, db_col, header in _JUNCTION_EXPORT_SPECS:
        rows = conn.execute(f"SELECT story_id, {db_col} FROM {table} ORDER BY story_id, {db_col}").fetchall()
        _write(csv_dir / csv_name, _CMD_JUNCTIONS, (("story_id", "StoryId"), (db_col, header)), rows)


# ---------------------------------------------------------------------------
# JSON dump
# ---------------------------------------------------------------------------

_ALL_TABLES = [
    "stories",
    "narrated_videos",
    "regions",
    "locations",
    "characters",
    "character_heroes",
    "monsters",
    "fauna",
    "flora",
    "food_and_drink",
    "heroes_canonical",
    "heroes_game",
    "heroes_printings",
    "weapons_canonical",
    "weapons_game",
    "weapons_printings",
    "equipment_canonical",
    "equipment_game",
    "equipment_printings",
    "classes",
    "talents",
    "sets",
    "set_types",
    "story_characters",
    "story_locations",
    "story_regions",
    "story_monsters",
    "story_fauna",
    "story_flora",
    "story_food_drink",
    "story_weapons",
    "story_equipment",
    "groups",
    "group_characters",
    "story_groups",
    "titles",
    "title_holders",
    "story_titles",
    "character_kin",
    "character_epithets",
    "location_aliases",
    "group_aliases",
    "kinds",
    "character_kinds",
    "kind_aliases",
    "professions",
    "character_professions",
]


def dump_to_json(conn: sqlite3.Connection, out_dir: Path) -> None:
    """Write one ``<table>.json`` file per table into ``out_dir``.

    Each file contains a JSON array of objects keyed by column name.
    ``out_dir`` is created if it does not exist.

    Args:
        conn: Open database connection.
        out_dir: Directory to write JSON files into.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for table in _ALL_TABLES:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        data = [dict(r) for r in rows]
        (out_dir / f"{table}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
