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
    """Regenerate every database-backed CSV file in ``data_dir/csv/``.

    Four CSVs in that directory have no table behind them and are never written
    here: ``story-arcs.csv`` and ``reviewed-name-pairs.csv`` are hand-maintained,
    and ``heroes-ll.csv`` / ``hero-card-name-aliases.csv`` are inputs to
    ``create_heroes_csv.py``. Everything else is exported.

    Superset of :func:`export_stories`, :func:`export_registry_tables` and
    :func:`export_story_junctions`. It skipped the eight registry tables only
    ``export_registry_tables`` wrote until the docstring was made true, which
    let an export run clean and leave groups, aliases, species, titles, kin and
    professions stale. ``tests/test_db_export.py`` compares the file sets, so a
    new exporter added to one of the narrower functions cannot be forgotten here.

    Args:
        conn: Open database connection.
        data_dir: Repository ``src/data/`` directory.
    """
    csv_dir = data_dir / "csv"
    _export_stories(conn, csv_dir)
    _export_story_narrated_videos(conn, csv_dir)
    _export_regions(conn, csv_dir)
    _export_locations(conn, csv_dir)
    _export_characters(conn, csv_dir)
    _export_monsters(conn, csv_dir)
    _export_fauna(conn, csv_dir)
    _export_flora(conn, csv_dir)
    _export_food_drink(conn, csv_dir)
    _export_groups(conn, csv_dir)
    _export_group_members(conn, csv_dir)
    _export_alternate_names(conn, csv_dir)
    _export_species(conn, csv_dir)
    _export_titles(conn, csv_dir)
    _export_title_holders(conn, csv_dir)
    _export_character_kin(conn, csv_dir)
    _export_professions(conn, csv_dir)
    _export_heroes_canonical(conn, csv_dir)
    _export_character_heroes(conn, csv_dir)
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
    _export_characters(conn, csv_dir)
    _export_character_heroes(conn, csv_dir)
    _export_monsters(conn, csv_dir)
    _export_fauna(conn, csv_dir)
    _export_flora(conn, csv_dir)
    _export_food_drink(conn, csv_dir)
    _export_groups(conn, csv_dir)
    _export_group_members(conn, csv_dir)
    _export_alternate_names(conn, csv_dir)
    _export_species(conn, csv_dir)
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
        [
            "StoryId",
            "StoryKey",
            "StoryType",
            "Title",
            "Authors",
            "Artists",
            "SourceLink",
            "PublicationDate",
            "ThumbnailImageLink",
        ],
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
            "ParentLocationId": r["parent_location_id"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "locations.csv",
        _CMD_REGISTRY,
        ["LocationId", "Name", "RegionId", "Notes", "LoreFragment", "ParentLocationId"],
        data,
    )


def _export_groups(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_groups(conn)
    data = [
        {
            "GroupId": r["group_id"],
            "Name": r["name"],
            "Kind": r["kind"],
            "Notes": r["notes"],
            "ParentGroupId": r["parent_group_id"],
            "LocationId": r["location_id"],
            "LoreStoryKey": r["lore_story_key"],
            "LoreFragment": r["lore_fragment"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "groups.csv",
        _CMD_REGISTRY,
        ["GroupId", "Name", "Kind", "Notes", "ParentGroupId", "LocationId", "LoreStoryKey", "LoreFragment"],
        data,
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
    data = [{"GroupId": r["group_id"], "CharacterId": r["character_id"], "StoryKey": r["story_key"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "group-characters.csv",
        _CMD_REGISTRY,
        ["GroupId", "CharacterId", "StoryKey"],
        data,
    )


def _export_alternate_names(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write the three alternate-name tables (R4, R6).

    Like the membership tables, these hang off their entity rather than a story,
    so they are not story junctions and do not belong in
    ``_JUNCTION_EXPORT_SPECS``.
    """
    for table, csv_name, cols in (
        ("npc_epithets", "npc-epithets.csv", (("character_id", "CharacterId"), ("name", "Name"), ("kind", "Kind"))),
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
        data = [{header: r[db_col] for db_col, header in cols} for r in rows]
        _write_pipe_csv(csv_dir / csv_name, _CMD_REGISTRY, [h for _, h in cols], data)


def _export_species(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``species.csv``, ``npc-species.csv`` and ``species-aliases.csv`` (R2).

    Three files for what was one column, which is the shape of the fix: a species
    is a registry row, a character's species is a junction, and a plural is an
    alias.
    """
    rows = q.select_all_species(conn)
    _write_pipe_csv(
        csv_dir / "species.csv",
        _CMD_REGISTRY,
        ["SpeciesId", "Name", "Notes"],
        [{"SpeciesId": r["species_id"], "Name": r["name"], "Notes": r["notes"]} for r in rows],
    )
    junction = conn.execute(
        "SELECT character_id, species_id FROM npc_species ORDER BY character_id, sort_order, species_id"
    ).fetchall()
    _write_pipe_csv(
        csv_dir / "npc-species.csv",
        _CMD_REGISTRY,
        ["CharacterId", "SpeciesId"],
        [{"CharacterId": r[0], "SpeciesId": r[1]} for r in junction],
    )
    aliases = conn.execute(
        "SELECT species_id, alias FROM species_aliases ORDER BY species_id, sort_order, alias"
    ).fetchall()
    _write_pipe_csv(
        csv_dir / "species-aliases.csv",
        _CMD_REGISTRY,
        ["SpeciesId", "Alias"],
        [{"SpeciesId": r[0], "Alias": r[1]} for r in aliases],
    )


def _export_titles(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_titles(conn)
    data = [
        {
            "TitleId": r["title_id"],
            "Name": r["name"],
            "GroupId": r["group_id"],
            "Notes": r["notes"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "titles.csv",
        _CMD_REGISTRY,
        ["TitleId", "Name", "GroupId", "Notes"],
        data,
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
    data = [
        {
            "TitleId": r["title_id"],
            "CharacterId": r["character_id"],
            "Ordinal": r["ordinal"],
            "StoryKey": r["story_key"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "title-holders.csv",
        _CMD_REGISTRY,
        ["TitleId", "CharacterId", "Ordinal", "StoryKey"],
        data,
    )


def _export_character_kin(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``character-kin.csv`` (R8).

    Not part of ``_JUNCTION_EXPORT_SPECS``: this hangs off a character, not a
    story, and its ``StoryKey`` is evidence for the kin fact (like
    ``group-npcs.csv``'s), not the link itself. Only the stated direction is
    ever written — the inverse is derived at read time and never stored, so
    this file can never disagree with itself about who is whose parent.
    """
    rows = conn.execute(
        "SELECT character_id, relative_id, relation, story_key FROM character_kin "
        "ORDER BY character_id, relative_id, relation"
    ).fetchall()
    data = [
        {
            "CharacterId": r["character_id"],
            "RelativeId": r["relative_id"],
            "Relation": r["relation"],
            "StoryKey": r["story_key"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "character-kin.csv",
        _CMD_REGISTRY,
        ["CharacterId", "RelativeId", "Relation", "StoryKey"],
        data,
    )


def _export_professions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``professions.csv`` and ``character-professions.csv`` (R9).

    Two files, not three: a profession is a registry row and a character's
    profession is a junction, the same split ``species.csv``/``npc-species.csv``
    make — but there is no third, alias file. See
    ``entries/catalogue/professions.py`` for why.
    """
    rows = q.select_all_professions(conn)
    _write_pipe_csv(
        csv_dir / "professions.csv",
        _CMD_REGISTRY,
        ["ProfessionId", "Name", "Notes"],
        [{"ProfessionId": r["profession_id"], "Name": r["name"], "Notes": r["notes"]} for r in rows],
    )
    junction = conn.execute(
        "SELECT character_id, profession_id, sort_order FROM character_professions "
        "ORDER BY character_id, sort_order, profession_id"
    ).fetchall()
    _write_pipe_csv(
        csv_dir / "character-professions.csv",
        _CMD_REGISTRY,
        ["CharacterId", "ProfessionId", "SortOrder"],
        [{"CharacterId": r[0], "ProfessionId": r[1], "SortOrder": r[2]} for r in junction],
    )


def _export_characters(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_characters(conn)
    data = [
        {
            "CharacterId": r["character_id"],
            "Name": r["name"],
            "Status": r["status"],
            "OtherCharactersStoryKey": r["other_characters_story_key"],
            "Summary": r["summary"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "characters.csv",
        _CMD_REGISTRY,
        ["CharacterId", "Name", "Status", "OtherCharactersStoryKey", "Summary"],
        data,
    )


def _export_character_heroes(conn: sqlite3.Connection, csv_dir: Path) -> None:
    """Write ``character-heroes.csv`` — the identity spine (migration 12)."""
    rows = q.select_all_character_heroes(conn)
    data = [{"CanonicalId": r["canonical_id"], "CharacterId": r["character_id"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "character-heroes.csv",
        _CMD_REGISTRY,
        ["CanonicalId", "CharacterId"],
        data,
    )


def _export_monsters(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_monsters(conn)
    data = [
        {
            "MonsterId": r["monster_id"],
            "Name": r["name"],
            "Description": r["description"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "monsters.csv",
        _CMD_REGISTRY,
        ["MonsterId", "Name", "Description"],
        data,
    )


def _export_fauna(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_fauna(conn)
    data = [{"FaunaId": r["fauna_id"], "Name": r["name"], "Description": r["description"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "fauna.csv",
        _CMD_REGISTRY,
        ["FaunaId", "Name", "Description"],
        data,
    )


def _export_flora(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_flora(conn)
    data = [{"FloraId": r["flora_id"], "Name": r["name"], "Description": r["description"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "flora.csv",
        _CMD_REGISTRY,
        ["FloraId", "Name", "Description"],
        data,
    )


def _export_food_drink(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_food_drink(conn)
    data = [{"FoodDrinkId": r["food_drink_id"], "Name": r["name"], "Type": r["type"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "food-and-drink.csv",
        _CMD_REGISTRY,
        ["FoodDrinkId", "Name", "Type"],
        data,
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
        csv_dir / "heroes-canonical.csv",
        _CMD_HEROES,
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"],
        data,
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
        csv_dir / "heroes-game.csv",
        _CMD_HEROES,
        [
            "HeroGameId",
            "CardName",
            "CanonicalId",
            "ClassIds",
            "TalentIds",
            "Health",
            "Intellect",
            "AbilityText",
            "YoungHero",
        ],
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
        csv_dir / "heroes-printings.csv",
        _CMD_HEROES,
        ["HeroGameId", "SetId", "CardId", "Rarity"],
        data,
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
        csv_dir / "weapons-canonical.csv",
        _CMD_WEAPONS,
        ["CanonicalWeaponId", "CanonicalSlug", "CanonicalWeapon"],
        data,
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
        csv_dir / "weapons-game.csv",
        _CMD_WEAPONS,
        [
            "WeaponGameId",
            "CardName",
            "CanonicalWeaponId",
            "ClassIds",
            "TalentIds",
            "Cost",
            "Power",
            "AbilityText",
            "Types",
        ],
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
            "ImageURL": r["image_url"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "weapons-printings.csv",
        _CMD_WEAPONS,
        ["WeaponGameId", "SetId", "CardId", "Rarity", "ImageURL"],
        data,
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
        csv_dir / "equipment-canonical.csv",
        _CMD_EQUIPMENT,
        ["CanonicalEquipmentId", "CanonicalSlug", "CanonicalEquipment"],
        data,
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
        csv_dir / "equipment-game.csv",
        _CMD_EQUIPMENT,
        [
            "EquipmentGameId",
            "CardName",
            "CanonicalEquipmentId",
            "ClassIds",
            "TalentIds",
            "Cost",
            "Defense",
            "AbilityText",
            "Types",
        ],
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
            "ImageURL": r["image_url"],
        }
        for r in rows
    ]
    _write_pipe_csv(
        csv_dir / "equipment-printings.csv",
        _CMD_EQUIPMENT,
        ["EquipmentGameId", "SetId", "CardId", "Rarity", "ImageURL"],
        data,
    )


def _export_classes(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_classes(conn)
    data = [{"ClassId": r["class_id"], "ClassName": r["class_name"]} for r in rows]
    _write_pipe_csv(csv_dir / "classes.csv", _CMD_CLASSES, ["ClassId", "ClassName"], data)


def _export_talents(conn: sqlite3.Connection, csv_dir: Path) -> None:
    rows = q.select_all_talents(conn)
    data = [{"TalentId": r["talent_id"], "TalentName": r["talent_name"]} for r in rows]
    _write_pipe_csv(csv_dir / "talents.csv", _CMD_CLASSES, ["TalentId", "TalentName"], data)


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
        csv_dir / "sets.csv",
        _CMD_SETS,
        ["SetId", "SetTypeId", "SetName", "InitialReleaseDate"],
        data,
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
        csv_dir / "set-types.csv",
        _CMD_SETS,
        ["SetTypeId", "SetType", "SetTypeLayer"],
        data,
    )


_JUNCTION_EXPORT_SPECS: tuple[tuple[str, str, str, str, str], ...] = (
    ("story_locations", "story-locations.csv", "location_id", "StoryId", "LocationId"),
    ("story_regions", "story-regions.csv", "region_id", "StoryId", "RegionId"),
    ("story_monsters", "story-monsters.csv", "monster_id", "StoryId", "MonsterId"),
    ("story_fauna", "story-fauna.csv", "fauna_id", "StoryId", "FaunaId"),
    ("story_flora", "story-flora.csv", "flora_id", "StoryId", "FloraId"),
    (
        "story_food_drink",
        "story-food-drink.csv",
        "food_drink_id",
        "StoryId",
        "FoodDrinkId",
    ),
    (
        "story_weapons",
        "story-weapons.csv",
        "canonical_weapon_id",
        "StoryId",
        "CanonicalWeaponId",
    ),
    (
        "story_equipment",
        "story-equipment.csv",
        "canonical_equipment_id",
        "StoryId",
        "CanonicalEquipmentId",
    ),
    ("story_groups", "story-groups.csv", "group_id", "StoryId", "GroupId"),
    ("story_titles", "story-titles.csv", "title_id", "StoryId", "TitleId"),
)


def _export_story_junctions(conn: sqlite3.Connection, csv_dir: Path) -> None:
    # story_characters carries an extra Fragment column, unlike the plain
    # (story_id, entity_id) junctions in _JUNCTION_EXPORT_SPECS below.
    rows = conn.execute(
        "SELECT story_id, character_id, fragment FROM story_characters ORDER BY story_id, character_id"
    ).fetchall()
    data = [{"StoryId": r["story_id"], "CharacterId": r["character_id"], "Fragment": r["fragment"]} for r in rows]
    _write_pipe_csv(
        csv_dir / "story-characters.csv",
        _CMD_JUNCTIONS,
        ["StoryId", "CharacterId", "Fragment"],
        data,
    )

    for table, csv_name, db_col, csv_sid, csv_eid in _JUNCTION_EXPORT_SPECS:
        rows = conn.execute(f"SELECT story_id, {db_col} FROM {table} ORDER BY story_id, {db_col}").fetchall()
        data = [{csv_sid: r["story_id"], csv_eid: r[db_col]} for r in rows]
        _write_pipe_csv(csv_dir / csv_name, _CMD_JUNCTIONS, [csv_sid, csv_eid], data)


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
    "npc_epithets",
    "location_aliases",
    "group_aliases",
    "species",
    "npc_species",
    "species_aliases",
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
