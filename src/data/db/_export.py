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

import csv
import json
import sqlite3
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import auto_gen_banner  # noqa: E402
import db._queries as q  # noqa: E402

# Regenerate hint strings (mirrored from the old pipe_csv_io constants)
_CMD_STORIES = "python3 src/data/create_stories_index.py"
_CMD_HEROES = "python3 src/data/create_heroes_csv.py"
_CMD_WEAPONS = "python3 src/data/create_weapons_csv.py"
_CMD_EQUIPMENT = "python3 src/data/create_equipment_csv.py"
_CMD_SETS = "python3 src/data/create_sets_csv.py"
_CMD_CLASSES = "python3 src/data/create_classes_talents_csv.py"
_CMD_REGISTRY = "Use the Database class in src/data/db/ (db.upsert_story)."
_CMD_JUNCTIONS = "Use the Database class in src/data/db/ (db.upsert_story / db.remove_story)."


def _write_pipe_csv(
    path: Path,
    banner_cmd: str,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(auto_gen_banner(banner_cmd))
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="|",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _export_story_narrated_videos(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = conn.execute(
        """
        SELECT nv.story_id, nv.author, nv.source_link, nv.channel_link
        FROM narrated_videos nv
        INNER JOIN stories s ON s.story_id = nv.story_id
        ORDER BY s.story_key, nv.narrated_video_id
        """
    ).fetchall()
    data = [
        {
            "StoryId": r["story_id"],
            "Author": r["author"],
            "SourceLink": r["source_link"],
            "ChannelLink": r["channel_link"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "story-narrated-videos.csv",
        _CMD_STORIES,
        ["StoryId", "Author", "SourceLink", "ChannelLink"],
        data,
    )


def export_all(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Regenerate every CSV file in ``data_dir/csv/`` from the database.

    Args:
        conn: Open database connection.
        data_dir: Repository ``src/data/`` directory.
    """
    csv_dir = data_dir / "csv"
    _export_stories(conn, csv_dir)
    _export_story_narrated_videos(conn, csv_dir)
    _export_regions(conn, csv_dir)
    _export_locations(conn, csv_dir)
    _export_npcs(conn, csv_dir)
    _export_monsters(conn, csv_dir)
    _export_fauna(conn, csv_dir)
    _export_flora(conn, csv_dir)
    _export_food_drink(conn, csv_dir)
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
    _export_story_junctions(conn, csv_dir)


def export_stories(conn: sqlite3.Connection, data_dir: Path) -> None:
    _export_stories(conn, data_dir / "csv")


def export_registry_tables(conn: sqlite3.Connection, data_dir: Path) -> None:
    csv_dir = data_dir / "csv"
    _export_regions(conn, csv_dir)
    _export_locations(conn, csv_dir)
    _export_npcs(conn, csv_dir)
    _export_monsters(conn, csv_dir)
    _export_fauna(conn, csv_dir)
    _export_flora(conn, csv_dir)
    _export_food_drink(conn, csv_dir)


def export_story_junctions(conn: sqlite3.Connection, data_dir: Path) -> None:
    _export_story_junctions(conn, data_dir / "csv")


# ---------------------------------------------------------------------------
# Per-table exporters
# ---------------------------------------------------------------------------

def _export_stories(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_stories(conn)
    data = [
        {
            "StoryId": r["story_id"],
            "StoryKey": r["story_key"],
            "StoryType": r["story_type"],
            "Title": r["title"],
            "Authors": r["authors"],
            "Artists": r["artists"],
            "SourceLink": r["source_link"],
            "PublicationDate": r["publication_date"],
            "ThumbnailImageLink": r["thumbnail_image_link"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "stories.csv",
        _CMD_STORIES,
        ["StoryId", "StoryKey", "StoryType", "Title", "Authors", "Artists",
         "SourceLink", "PublicationDate", "ThumbnailImageLink"],
        data,
    )


def _export_regions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_regions(conn)
    data = [
        {
            "RegionId": r["region_id"],
            "RegionName": r["region_name"],
            "WorldOfRatheStoryKey": r["world_of_rathe_story_key"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "regions.csv",
        _CMD_REGISTRY,
        ["RegionId", "RegionName", "WorldOfRatheStoryKey"],
        data,
    )


def _export_locations(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_locations(conn)
    data = [
        {
            "LocationId": r["location_id"],
            "Name": r["name"],
            "RegionId": r["region_id"],
            "Notes": r["notes"],
            "LoreFragment": r["lore_fragment"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "locations.csv",
        _CMD_REGISTRY,
        ["LocationId", "Name", "RegionId", "Notes", "LoreFragment"],
        data,
    )


def _export_npcs(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_npcs(conn)
    data = [
        {
            "CharacterId": r["character_id"],
            "Name": r["name"],
            "Species": r["species"],
            "Status": r["status"],
            "OtherCharactersStoryKey": r["other_characters_story_key"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "npcs.csv",
        _CMD_REGISTRY,
        ["CharacterId", "Name", "Species", "Status", "OtherCharactersStoryKey"],
        data,
    )


def _export_monsters(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_monsters(conn)
    data = [
        {"MonsterId": r["monster_id"], "Name": r["name"], "Description": r["description"]}
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "monsters.csv", _CMD_REGISTRY,
        ["MonsterId", "Name", "Description"], data,
    )


def _export_fauna(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_fauna(conn)
    data = [
        {"FaunaId": r["fauna_id"], "Name": r["name"], "Description": r["description"]}
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "fauna.csv", _CMD_REGISTRY,
        ["FaunaId", "Name", "Description"], data,
    )


def _export_flora(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_flora(conn)
    data = [
        {"FloraId": r["flora_id"], "Name": r["name"], "Description": r["description"]}
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "flora.csv", _CMD_REGISTRY,
        ["FloraId", "Name", "Description"], data,
    )


def _export_food_drink(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_food_drink(conn)
    data = [
        {"FoodDrinkId": r["food_drink_id"], "Name": r["name"], "Type": r["type"]}
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "food-and-drink.csv", _CMD_REGISTRY,
        ["FoodDrinkId", "Name", "Type"], data,
    )


def _export_heroes_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_heroes_canonical(conn)
    data = [
        {
            "CanonicalId": r["canonical_id"],
            "CanonicalSlug": r["canonical_slug"],
            "CanonicalHero": r["canonical_hero"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "heroes-canonical.csv", _CMD_HEROES,
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"], data,
    )


def _export_heroes_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_heroes_game(conn)
    data = [
        {
            "HeroGameId": r["hero_game_id"],
            "CardName": r["card_name"],
            "CanonicalId": r["canonical_id"],
            "ClassIds": r["class_ids"],
            "TalentIds": r["talent_ids"],
            "Health": r["health"],
            "Intellect": r["intellect"],
            "AbilityText": r["ability_text"],
            "YoungHero": r["young_hero"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "heroes-game.csv", _CMD_HEROES,
        ["HeroGameId", "CardName", "CanonicalId", "ClassIds", "TalentIds",
         "Health", "Intellect", "AbilityText", "YoungHero"],
        data,
    )


def _export_heroes_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_heroes_printings(conn)
    data = [
        {
            "HeroGameId": r["hero_game_id"],
            "SetId": r["set_id"],
            "CardId": r["card_id"],
            "Rarity": r["rarity"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "heroes-printings.csv", _CMD_HEROES,
        ["HeroGameId", "SetId", "CardId", "Rarity"], data,
    )


def _export_weapons_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_weapons_canonical(conn)
    data = [
        {
            "CanonicalWeaponId": r["canonical_weapon_id"],
            "CanonicalSlug": r["canonical_slug"],
            "CanonicalWeapon": r["canonical_weapon"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "weapons-canonical.csv", _CMD_WEAPONS,
        ["CanonicalWeaponId", "CanonicalSlug", "CanonicalWeapon"], data,
    )


def _export_weapons_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_weapons_game(conn)
    data = [
        {
            "WeaponGameId": r["weapon_game_id"],
            "CardName": r["card_name"],
            "CanonicalWeaponId": r["canonical_weapon_id"],
            "ClassIds": r["class_ids"],
            "TalentIds": r["talent_ids"],
            "Cost": r["cost"],
            "Power": r["power"],
            "AbilityText": r["ability_text"],
            "Types": r["types"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "weapons-game.csv", _CMD_WEAPONS,
        ["WeaponGameId", "CardName", "CanonicalWeaponId", "ClassIds", "TalentIds",
         "Cost", "Power", "AbilityText", "Types"],
        data,
    )


def _export_weapons_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_weapons_printings(conn)
    data = [
        {
            "WeaponGameId": r["weapon_game_id"],
            "SetId": r["set_id"],
            "CardId": r["card_id"],
            "Rarity": r["rarity"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "weapons-printings.csv", _CMD_WEAPONS,
        ["WeaponGameId", "SetId", "CardId", "Rarity"], data,
    )


def _export_equipment_canonical(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_equipment_canonical(conn)
    data = [
        {
            "CanonicalEquipmentId": r["canonical_equipment_id"],
            "CanonicalSlug": r["canonical_slug"],
            "CanonicalEquipment": r["canonical_equipment"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "equipment-canonical.csv", _CMD_EQUIPMENT,
        ["CanonicalEquipmentId", "CanonicalSlug", "CanonicalEquipment"], data,
    )


def _export_equipment_game(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_equipment_game(conn)
    data = [
        {
            "EquipmentGameId": r["equipment_game_id"],
            "CardName": r["card_name"],
            "CanonicalEquipmentId": r["canonical_equipment_id"],
            "ClassIds": r["class_ids"],
            "TalentIds": r["talent_ids"],
            "Cost": r["cost"],
            "Defense": r["defense"],
            "AbilityText": r["ability_text"],
            "Types": r["types"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "equipment-game.csv", _CMD_EQUIPMENT,
        ["EquipmentGameId", "CardName", "CanonicalEquipmentId", "ClassIds", "TalentIds",
         "Cost", "Defense", "AbilityText", "Types"],
        data,
    )


def _export_equipment_printings(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_equipment_printings(conn)
    data = [
        {
            "EquipmentGameId": r["equipment_game_id"],
            "SetId": r["set_id"],
            "CardId": r["card_id"],
            "Rarity": r["rarity"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "equipment-printings.csv", _CMD_EQUIPMENT,
        ["EquipmentGameId", "SetId", "CardId", "Rarity"], data,
    )


def _export_classes(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_classes(conn)
    data = [{"ClassId": r["class_id"], "ClassName": r["class_name"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "classes.csv", _CMD_CLASSES, ["ClassId", "ClassName"], data
    )


def _export_talents(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_talents(conn)
    data = [{"TalentId": r["talent_id"], "TalentName": r["talent_name"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "talents.csv", _CMD_CLASSES, ["TalentId", "TalentName"], data
    )


def _export_sets(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_sets(conn)
    data = [
        {
            "SetId": r["set_id"],
            "SetTypeId": r["set_type_id"],
            "SetName": r["set_name"],
            "InitialReleaseDate": r["initial_release_date"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "sets.csv", _CMD_SETS,
        ["SetId", "SetTypeId", "SetName", "InitialReleaseDate"], data,
    )


def _export_set_types(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_set_types(conn)
    data = [
        {
            "SetTypeId": r["set_type_id"],
            "SetType": r["set_type"],
            "SetTypeLayer": r["set_type_layer"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "set-types.csv", _CMD_SETS,
        ["SetTypeId", "SetType", "SetTypeLayer"], data,
    )


_JUNCTION_EXPORT_SPECS: tuple[tuple[str, str, str, str, str], ...] = (
    ("story_locations", "story-locations.csv", "location_id", "StoryId", "LocationId"),
    ("story_regions", "story-regions.csv", "region_id", "StoryId", "RegionId"),
    ("story_monsters", "story-monsters.csv", "monster_id", "StoryId", "MonsterId"),
    ("story_fauna", "story-fauna.csv", "fauna_id", "StoryId", "FaunaId"),
    ("story_flora", "story-flora.csv", "flora_id", "StoryId", "FloraId"),
    (
        "story_food_drink", "story-food-drink.csv",
        "food_drink_id", "StoryId", "FoodDrinkId",
    ),
    (
        "story_weapons", "story-weapons.csv",
        "canonical_weapon_id", "StoryId", "CanonicalWeaponId",
    ),
    (
        "story_equipment", "story-equipment.csv",
        "canonical_equipment_id", "StoryId", "CanonicalEquipmentId",
    ),
)


def _export_story_junctions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    # story_heroes and story_npcs carry an extra Fragment column.
    for table, csv_name, db_col, csv_id_col in (
        ("story_heroes", "story-heroes.csv", "canonical_id", "CanonicalId"),
        ("story_npcs", "story-npcs.csv", "character_id", "CharacterId"),
    ):
        rows = conn.execute(
            f"SELECT story_id, {db_col}, fragment"
            f" FROM {table} ORDER BY story_id, {db_col}"
        ).fetchall()
        data = [
            {"StoryId": r["story_id"], csv_id_col: r[db_col], "Fragment": r["fragment"]}
            for r in rows
        ]
        _write_pipe_csv(
            csv_dir / csv_name,
            _CMD_JUNCTIONS,
            ["StoryId", csv_id_col, "Fragment"],
            data,
        )

    for table, csv_name, db_col, csv_sid, csv_eid in _JUNCTION_EXPORT_SPECS:
        rows = conn.execute(
            f"SELECT story_id, {db_col} FROM {table} ORDER BY story_id, {db_col}"
        ).fetchall()
        data = [{csv_sid: r["story_id"], csv_eid: r[db_col]} for r in rows]
        _write_pipe_csv(
            csv_dir / csv_name, _CMD_JUNCTIONS, [csv_sid, csv_eid], data
        )


# ---------------------------------------------------------------------------
# JSON dump
# ---------------------------------------------------------------------------

_ALL_TABLES = [
    "stories", "narrated_videos", "regions", "locations", "npcs",
    "monsters", "fauna", "flora", "food_and_drink",
    "heroes_canonical", "heroes_game", "heroes_printings",
    "weapons_canonical", "weapons_game", "weapons_printings",
    "equipment_canonical", "equipment_game", "equipment_printings",
    "classes", "talents", "sets", "set_types",
    "story_npcs", "story_heroes", "story_locations", "story_regions",
    "story_monsters", "story_fauna", "story_flora", "story_food_drink",
    "story_weapons", "story_equipment",
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
