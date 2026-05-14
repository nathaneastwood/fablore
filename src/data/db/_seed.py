"""Seed the fablore database from committed pipe-delimited CSV files.

Reads every CSV under ``data_dir/csv/`` using :func:`pipe_csv_io.read_pipe_csv`
and performs ``INSERT OR IGNORE`` so reseeding is always safe (existing rows
are never overwritten).  The legacy ``NarratedVideos`` JSON blob from
``stories.csv`` is decoded and inserted into the ``narrated_videos`` table when
present; :file:`story-narrated-videos.csv` then replaces rows for each listed
``StoryId`` (see :func:`_seed_narrated_videos_from_csv`).

Call :func:`seed_from_csvs` after schema migration; call order respects FK
dependencies so FK enforcement (``PRAGMA foreign_keys = ON``) stays clean
throughout.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402
import db._queries as q  # noqa: E402


def _csv(data_dir: Path, name: str) -> tuple[list[str], list[dict[str, str]]]:
    """Read a pipe CSV from ``data_dir/csv/<name>``; tolerate missing files."""
    return read_pipe_csv(data_dir / "csv" / name)


def _s(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def seed_from_csvs(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Bulk-load all committed CSVs into the database.

    Uses ``INSERT OR IGNORE`` so existing rows are not overwritten. Safe to
    call multiple times. Inserts in FK-dependency order.

    Args:
        conn: Open database connection (FK enforcement already applied).
        data_dir: Repository ``src/data/`` directory containing the ``csv/`` subfolder.
    """
    with conn:
        _seed_set_types(conn, data_dir)
        _seed_sets(conn, data_dir)
        _seed_classes(conn, data_dir)
        _seed_talents(conn, data_dir)
        _seed_regions(conn, data_dir)
        _seed_locations(conn, data_dir)
        _seed_npcs(conn, data_dir)
        _seed_monsters(conn, data_dir)
        _seed_fauna(conn, data_dir)
        _seed_flora(conn, data_dir)
        _seed_food_drink(conn, data_dir)
        _seed_heroes_canonical(conn, data_dir)
        _seed_heroes_game(conn, data_dir)
        _seed_heroes_printings(conn, data_dir)
        _seed_weapons_canonical(conn, data_dir)
        _seed_weapons_game(conn, data_dir)
        _seed_weapons_printings(conn, data_dir)
        _seed_equipment_canonical(conn, data_dir)
        _seed_equipment_game(conn, data_dir)
        _seed_equipment_printings(conn, data_dir)
        _seed_stories(conn, data_dir)
        _seed_narrated_videos_from_csv(conn, data_dir)
        _seed_story_junctions(conn, data_dir)


# ---------------------------------------------------------------------------
# Game data tables
# ---------------------------------------------------------------------------

def _seed_set_types(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "set-types.csv")
    for row in rows:
        q.upsert_set_type(
            conn,
            set_type_id=_s(row, "SetTypeId"),
            set_type=_s(row, "SetType"),
            set_type_layer=_s(row, "SetTypeLayer"),
        )


def _seed_sets(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "sets.csv")
    for row in rows:
        q.upsert_set(
            conn,
            set_id=_s(row, "SetId"),
            set_type_id=_s(row, "SetTypeId"),
            set_name=_s(row, "SetName"),
            initial_release_date=_s(row, "InitialReleaseDate"),
        )


def _seed_classes(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "classes.csv")
    for row in rows:
        q.upsert_class(conn, class_id=_s(row, "ClassId"), class_name=_s(row, "ClassName"))


def _seed_talents(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "talents.csv")
    for row in rows:
        q.upsert_talent(
            conn, talent_id=_s(row, "TalentId"), talent_name=_s(row, "TalentName")
        )


def _seed_heroes_canonical(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "heroes-canonical.csv")
    for row in rows:
        q.upsert_hero_canonical(
            conn,
            canonical_id=_s(row, "CanonicalId"),
            canonical_slug=_s(row, "CanonicalSlug"),
            canonical_hero=_s(row, "CanonicalHero"),
        )


def _seed_heroes_game(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "heroes-game.csv")
    for row in rows:
        q.upsert_hero_game(
            conn,
            hero_game_id=_s(row, "HeroGameId"),
            card_name=_s(row, "CardName"),
            canonical_id=_s(row, "CanonicalId"),
            class_ids=_s(row, "ClassIds"),
            talent_ids=_s(row, "TalentIds"),
            health=_s(row, "Health"),
            intellect=_s(row, "Intellect"),
            ability_text=_s(row, "AbilityText"),
            young_hero=_s(row, "YoungHero") or "false",
        )


def _seed_heroes_printings(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "heroes-printings.csv")
    for row in rows:
        q.upsert_hero_printing(
            conn,
            hero_game_id=_s(row, "HeroGameId"),
            set_id=_s(row, "SetId"),
            card_id=_s(row, "CardId"),
            rarity=_s(row, "Rarity"),
        )


def _seed_weapons_canonical(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "weapons-canonical.csv")
    for row in rows:
        q.upsert_weapon_canonical(
            conn,
            canonical_weapon_id=_s(row, "CanonicalWeaponId"),
            canonical_slug=_s(row, "CanonicalSlug"),
            canonical_weapon=_s(row, "CanonicalWeapon"),
        )


def _seed_weapons_game(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "weapons-game.csv")
    for row in rows:
        q.upsert_weapon_game(
            conn,
            weapon_game_id=_s(row, "WeaponGameId"),
            card_name=_s(row, "CardName"),
            canonical_weapon_id=_s(row, "CanonicalWeaponId"),
            class_ids=_s(row, "ClassIds"),
            talent_ids=_s(row, "TalentIds"),
            cost=_s(row, "Cost"),
            power=_s(row, "Power"),
            ability_text=_s(row, "AbilityText"),
            types=_s(row, "Types"),
        )


def _seed_weapons_printings(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "weapons-printings.csv")
    for row in rows:
        q.upsert_weapon_printing(
            conn,
            weapon_game_id=_s(row, "WeaponGameId"),
            set_id=_s(row, "SetId"),
            card_id=_s(row, "CardId"),
            rarity=_s(row, "Rarity"),
        )


def _seed_equipment_canonical(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "equipment-canonical.csv")
    for row in rows:
        q.upsert_equipment_canonical(
            conn,
            canonical_equipment_id=_s(row, "CanonicalEquipmentId"),
            canonical_slug=_s(row, "CanonicalSlug"),
            canonical_equipment=_s(row, "CanonicalEquipment"),
        )


def _seed_equipment_game(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "equipment-game.csv")
    for row in rows:
        q.upsert_equipment_game(
            conn,
            equipment_game_id=_s(row, "EquipmentGameId"),
            card_name=_s(row, "CardName"),
            canonical_equipment_id=_s(row, "CanonicalEquipmentId"),
            class_ids=_s(row, "ClassIds"),
            talent_ids=_s(row, "TalentIds"),
            cost=_s(row, "Cost"),
            defense=_s(row, "Defense"),
            ability_text=_s(row, "AbilityText"),
            types=_s(row, "Types"),
        )


def _seed_equipment_printings(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "equipment-printings.csv")
    for row in rows:
        q.upsert_equipment_printing(
            conn,
            equipment_game_id=_s(row, "EquipmentGameId"),
            set_id=_s(row, "SetId"),
            card_id=_s(row, "CardId"),
            rarity=_s(row, "Rarity"),
        )


# ---------------------------------------------------------------------------
# Lore registry tables
# ---------------------------------------------------------------------------

def _seed_regions(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "regions.csv")
    for row in rows:
        q.upsert_region(
            conn,
            region_id=_s(row, "RegionId"),
            region_name=_s(row, "RegionName"),
            world_of_rathe_story_key=_s(row, "WorldOfRatheStoryKey"),
        )


def _seed_locations(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "locations.csv")
    for row in rows:
        q.upsert_location(
            conn,
            location_id=_s(row, "LocationId"),
            name=_s(row, "Name"),
            region_id=_s(row, "RegionId"),
            notes=_s(row, "Notes"),
            lore_fragment=_s(row, "LoreFragment"),
        )


def _seed_npcs(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "npcs.csv")
    for row in rows:
        q.upsert_npc(
            conn,
            character_id=_s(row, "CharacterId"),
            name=_s(row, "Name"),
            species=_s(row, "Species") or "Unknown",
            status=_s(row, "Status") or "Unknown",
            other_characters_story_key=_s(row, "OtherCharactersStoryKey"),
        )


def _seed_monsters(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "monsters.csv")
    for row in rows:
        q.upsert_monster(
            conn,
            monster_id=_s(row, "MonsterId"),
            name=_s(row, "Name"),
            description=_s(row, "Description"),
        )


def _seed_fauna(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "fauna.csv")
    for row in rows:
        q.upsert_fauna(
            conn,
            fauna_id=_s(row, "FaunaId"),
            name=_s(row, "Name"),
            description=_s(row, "Description"),
        )


def _seed_flora(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "flora.csv")
    for row in rows:
        q.upsert_flora(
            conn,
            flora_id=_s(row, "FloraId"),
            name=_s(row, "Name"),
            description=_s(row, "Description"),
        )


def _seed_food_drink(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "food-and-drink.csv")
    for row in rows:
        q.upsert_food_drink(
            conn,
            food_drink_id=_s(row, "FoodDrinkId"),
            name=_s(row, "Name"),
            type_=_s(row, "Type"),
        )


# ---------------------------------------------------------------------------
# Stories + narrated videos
# ---------------------------------------------------------------------------

def _seed_stories(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "stories.csv")
    for row in rows:
        story_id = _s(row, "StoryId")
        if not story_id:
            continue
        q.upsert_story(
            conn,
            story_id=story_id,
            story_key=_s(row, "StoryKey"),
            story_type=_s(row, "StoryType"),
            title=_s(row, "Title"),
            authors=_s(row, "Authors"),
            artists=_s(row, "Artists"),
            source_link=_s(row, "SourceLink"),
            publication_date=_s(row, "PublicationDate"),
            thumbnail_image_link=_s(row, "ThumbnailImageLink"),
        )
        # Decode legacy JSON blob into the narrated_videos table
        raw_videos = _s(row, "NarratedVideos")
        if raw_videos:
            try:
                parsed = json.loads(raw_videos)
                if isinstance(parsed, list):
                    videos = [
                        (str(v.get("author", "")), str(v.get("url", "")), "", "")
                        for v in parsed
                        if isinstance(v, dict)
                        and v.get("author")
                        and v.get("url")
                    ]
                    q.set_narrated_videos(conn, story_id, videos)
            except (json.JSONDecodeError, TypeError):
                pass


def _seed_narrated_videos_from_csv(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Load ``story-narrated-videos.csv`` and replace video rows per ``StoryId``.

    Each story that appears in the CSV gets its narrated video rows replaced
    (same semantics as :func:`db._queries.set_narrated_videos`). Row order within
    a story is preserved. Stories absent from the file are unchanged.
    """
    _, rows = _csv(data_dir, "story-narrated-videos.csv")
    grouped: dict[str, list[tuple[str, str, str, str]]] = {}
    for row in rows:
        sid = _s(row, "StoryId")
        author = _s(row, "Author")
        link = _s(row, "SourceLink")
        if not sid or not author or not link:
            continue
        channel = _s(row, "ChannelLink")
        duration = _s(row, "Duration")
        grouped.setdefault(sid, []).append((author, link, channel, duration))
    for sid, videos in grouped.items():
        q.set_narrated_videos(conn, sid, videos)


# ---------------------------------------------------------------------------
# Story junction tables
# ---------------------------------------------------------------------------

_JUNCTION_SPECS: tuple[tuple[str, str, str, str], ...] = (
    ("story-npcs.csv", "story_npcs", "CharacterId", "character_id"),
    ("story-heroes.csv", "story_heroes", "CanonicalId", "canonical_id"),
    ("story-locations.csv", "story_locations", "LocationId", "location_id"),
    ("story-regions.csv", "story_regions", "RegionId", "region_id"),
    ("story-monsters.csv", "story_monsters", "MonsterId", "monster_id"),
    ("story-fauna.csv", "story_fauna", "FaunaId", "fauna_id"),
    ("story-flora.csv", "story_flora", "FloraId", "flora_id"),
    ("story-food-drink.csv", "story_food_drink", "FoodDrinkId", "food_drink_id"),
    ("story-weapons.csv", "story_weapons", "CanonicalWeaponId", "canonical_weapon_id"),
    ("story-equipment.csv", "story_equipment", "CanonicalEquipmentId", "canonical_equipment_id"),
)


def _seed_story_junctions(conn: sqlite3.Connection, data_dir: Path) -> None:
    for csv_name, table, csv_col, db_col in _JUNCTION_SPECS:
        _, rows = _csv(data_dir, csv_name)
        pairs = [
            (_s(row, "StoryId"), _s(row, csv_col))
            for row in rows
            if _s(row, "StoryId") and _s(row, csv_col)
        ]
        if pairs:
            conn.executemany(
                f"INSERT OR IGNORE INTO {table} (story_id, {db_col}) VALUES (?,?)",
                pairs,
            )
