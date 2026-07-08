"""Low-level parameterised SQL operations for all fablore database tables.

All raw SQL lives in this module. Functions accept a ``sqlite3.Connection``
as their first argument and perform no domain logic — callers are responsible
for transaction management and ID computation.

Upsert functions use ``INSERT ... ON CONFLICT DO UPDATE`` (SQLite ≥ 3.24).
"""

from __future__ import annotations

import logging
import sqlite3

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------


def upsert_story(
    conn: sqlite3.Connection,
    *,
    story_id: str,
    story_key: str,
    story_type: str,
    title: str,
    authors: str = "",
    artists: str = "",
    source_link: str = "",
    publication_date: str = "",
    thumbnail_image_link: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO stories
            (story_id, story_key, story_type, title, authors, artists,
             source_link, publication_date, thumbnail_image_link)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(story_id) DO UPDATE SET
            story_key            = excluded.story_key,
            story_type           = excluded.story_type,
            title                = excluded.title,
            authors              = excluded.authors,
            artists              = excluded.artists,
            source_link          = excluded.source_link,
            publication_date     = excluded.publication_date,
            thumbnail_image_link = excluded.thumbnail_image_link
        """,
        (
            story_id,
            story_key,
            story_type,
            title,
            authors,
            artists,
            source_link,
            publication_date,
            thumbnail_image_link,
        ),
    )


def select_story_by_key(conn: sqlite3.Connection, story_key: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM stories WHERE story_key = ?", [story_key]
    ).fetchone()


def select_story_by_id(conn: sqlite3.Connection, story_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM stories WHERE story_id = ?", [story_id]
    ).fetchone()


def delete_story(conn: sqlite3.Connection, story_id: str) -> int:
    """Delete story and all junction rows (cascade). Returns rows deleted from stories."""
    cur = conn.execute("DELETE FROM stories WHERE story_id = ?", [story_id])
    return cur.rowcount


def select_all_stories(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM stories ORDER BY story_key").fetchall()


# ---------------------------------------------------------------------------
# Narrated videos
# ---------------------------------------------------------------------------


def set_narrated_videos(
    conn: sqlite3.Connection,
    story_id: str,
    videos: list[tuple[str, str, str]],
) -> None:
    """Replace all narrated video rows for ``story_id`` with ``videos``.

    Args:
        videos: List of ``(author, source_link, channel_link)`` tuples
            in display order. ``channel_link`` may be an empty string.
    """
    conn.execute("DELETE FROM narrated_videos WHERE story_id = ?", [story_id])
    if videos:
        conn.executemany(
            "INSERT INTO narrated_videos "
            "(story_id, author, source_link, channel_link) "
            "VALUES (?,?,?,?)",
            [(story_id, author, url, channel) for author, url, channel in videos],
        )


def select_narrated_videos(
    conn: sqlite3.Connection, story_id: str
) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT author, source_link, channel_link "
        "FROM narrated_videos WHERE story_id = ? "
        "ORDER BY narrated_video_id",
        [story_id],
    ).fetchall()


# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------


def upsert_region(
    conn: sqlite3.Connection,
    *,
    region_id: str,
    region_name: str,
    world_of_rathe_story_key: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO regions (region_id, region_name, world_of_rathe_story_key)
        VALUES (?,?,?)
        ON CONFLICT(region_id) DO UPDATE SET
            region_name              = excluded.region_name,
            world_of_rathe_story_key = CASE
                WHEN excluded.world_of_rathe_story_key != '' THEN excluded.world_of_rathe_story_key
                ELSE regions.world_of_rathe_story_key
            END
        """,
        (region_id, region_name, world_of_rathe_story_key),
    )


def select_region_by_id(conn: sqlite3.Connection, region_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM regions WHERE region_id = ?", [region_id]
    ).fetchone()


def select_all_regions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM regions ORDER BY region_name").fetchall()


def region_id_exists(conn: sqlite3.Connection, region_id: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM regions WHERE region_id = ?", [region_id]
        ).fetchone()
        is not None
    )


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------


def upsert_location(
    conn: sqlite3.Connection,
    *,
    location_id: str,
    name: str,
    region_id: str = "",
    notes: str = "",
    lore_fragment: str = "",
) -> None:
    if not notes:
        row = conn.execute(
            "SELECT notes FROM locations WHERE location_id = ?", [location_id]
        ).fetchone()
        if row and row[0]:
            _log.warning(
                "Skipping notes overwrite for location %r — existing notes preserved"
                " (pass non-empty notes to update them)",
                location_id,
            )
    conn.execute(
        """
        INSERT INTO locations (location_id, name, region_id, notes, lore_fragment)
        VALUES (?,?,?,?,?)
        ON CONFLICT(location_id) DO UPDATE SET
            name          = excluded.name,
            region_id     = excluded.region_id,
            notes         = CASE WHEN excluded.notes != ''
                            THEN excluded.notes
                            ELSE locations.notes END,
            lore_fragment = CASE WHEN excluded.lore_fragment != ''
                            THEN excluded.lore_fragment
                            ELSE locations.lore_fragment END
        """,
        (location_id, name, region_id, notes, lore_fragment),
    )


def select_all_locations(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM locations ORDER BY name").fetchall()


# ---------------------------------------------------------------------------
# NPCs
# ---------------------------------------------------------------------------


def upsert_npc(
    conn: sqlite3.Connection,
    *,
    character_id: str,
    name: str,
    species: str = "Unknown",
    status: str = "Unknown",
    other_characters_story_key: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO npcs (character_id, name, species, status, other_characters_story_key)
        VALUES (?,?,?,?,?)
        ON CONFLICT(character_id) DO UPDATE SET
            name    = excluded.name,
            species = excluded.species,
            status  = excluded.status,
            other_characters_story_key = CASE
                WHEN excluded.other_characters_story_key != ''
                    THEN excluded.other_characters_story_key
                ELSE npcs.other_characters_story_key
            END
        """,
        (character_id, name, species, status, other_characters_story_key),
    )


def select_all_npcs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM npcs ORDER BY name").fetchall()


# ---------------------------------------------------------------------------
# Monsters / Fauna / Flora  (identical structure)
# ---------------------------------------------------------------------------


def _upsert_named_entity(
    conn: sqlite3.Connection,
    table: str,
    id_col: str,
    entity_id: str,
    name: str,
    description: str = "",
) -> None:
    if not description:
        row = conn.execute(
            f"SELECT description FROM {table} WHERE {id_col} = ?", [entity_id]
        ).fetchone()
        if row and row[0]:
            _log.warning(
                "Skipping description overwrite for %s %r — existing description preserved"
                " (pass a non-empty description to update it)",
                table,
                entity_id,
            )
    conn.execute(
        f"""
        INSERT INTO {table} ({id_col}, name, description)
        VALUES (?,?,?)
        ON CONFLICT({id_col}) DO UPDATE SET
            name        = excluded.name,
            description = CASE WHEN excluded.description != ''
                          THEN excluded.description
                          ELSE {table}.description END
        """,
        (entity_id, name, description),
    )


def upsert_monster(
    conn: sqlite3.Connection, *, monster_id: str, name: str, description: str = ""
) -> None:
    _upsert_named_entity(conn, "monsters", "monster_id", monster_id, name, description)


def upsert_fauna(
    conn: sqlite3.Connection, *, fauna_id: str, name: str, description: str = ""
) -> None:
    _upsert_named_entity(conn, "fauna", "fauna_id", fauna_id, name, description)


def upsert_flora(
    conn: sqlite3.Connection, *, flora_id: str, name: str, description: str = ""
) -> None:
    _upsert_named_entity(conn, "flora", "flora_id", flora_id, name, description)


def update_entity_description(
    conn: sqlite3.Connection,
    table: str,
    id_col: str,
    entity_id: str,
    description: str,
) -> int:
    """Update the description for a single entity. Returns rows affected."""
    cur = conn.execute(
        f"UPDATE {table} SET description = ? WHERE {id_col} = ?",
        (description, entity_id),
    )
    return cur.rowcount


def update_location_notes(
    conn: sqlite3.Connection,
    name: str,
    notes: str,
) -> int:
    """Update notes for all locations matching name. Returns rows affected."""
    cur = conn.execute(
        "UPDATE locations SET notes = ? WHERE name = ?",
        (notes, name),
    )
    return cur.rowcount


def select_location_ids_by_name(conn: sqlite3.Connection, name: str) -> list[str]:
    """Return every ``LocationId`` stored under ``name`` (may be >1 for duplicate rows)."""
    rows = conn.execute(
        "SELECT location_id FROM locations WHERE name = ?", [name]
    ).fetchall()
    return [r[0] for r in rows]


def select_all_monsters(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM monsters ORDER BY name").fetchall()


def select_all_fauna(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM fauna ORDER BY name").fetchall()


def select_all_flora(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM flora ORDER BY name").fetchall()


# ---------------------------------------------------------------------------
# Food and drink
# ---------------------------------------------------------------------------


def upsert_food_drink(
    conn: sqlite3.Connection, *, food_drink_id: str, name: str, type_: str
) -> None:
    conn.execute(
        """
        INSERT INTO food_and_drink (food_drink_id, name, type)
        VALUES (?,?,?)
        ON CONFLICT(food_drink_id) DO UPDATE SET
            name = excluded.name,
            type = excluded.type
        """,
        (food_drink_id, name, type_),
    )


def select_all_food_drink(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM food_and_drink ORDER BY name").fetchall()


# ---------------------------------------------------------------------------
# Set types and sets
# ---------------------------------------------------------------------------


def upsert_set_type(
    conn: sqlite3.Connection,
    *,
    set_type_id: str,
    set_type: str,
    set_type_layer: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO set_types (set_type_id, set_type, set_type_layer)
        VALUES (?,?,?)
        ON CONFLICT(set_type_id) DO UPDATE SET
            set_type       = excluded.set_type,
            set_type_layer = excluded.set_type_layer
        """,
        (set_type_id, set_type, set_type_layer),
    )


def upsert_set(
    conn: sqlite3.Connection,
    *,
    set_id: str,
    set_type_id: str,
    set_name: str,
    initial_release_date: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO sets (set_id, set_type_id, set_name, initial_release_date)
        VALUES (?,?,?,?)
        ON CONFLICT(set_id) DO UPDATE SET
            set_type_id          = excluded.set_type_id,
            set_name             = excluded.set_name,
            initial_release_date = excluded.initial_release_date
        """,
        (set_id, set_type_id, set_name, initial_release_date),
    )


def select_all_set_types(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM set_types ORDER BY set_type").fetchall()


def select_all_sets(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM sets ORDER BY set_id").fetchall()


# ---------------------------------------------------------------------------
# Classes and talents
# ---------------------------------------------------------------------------


def upsert_class(conn: sqlite3.Connection, *, class_id: str, class_name: str) -> None:
    conn.execute(
        """
        INSERT INTO classes (class_id, class_name) VALUES (?,?)
        ON CONFLICT(class_id) DO UPDATE SET class_name = excluded.class_name
        """,
        (class_id, class_name),
    )


def upsert_talent(
    conn: sqlite3.Connection, *, talent_id: str, talent_name: str
) -> None:
    conn.execute(
        """
        INSERT INTO talents (talent_id, talent_name) VALUES (?,?)
        ON CONFLICT(talent_id) DO UPDATE SET talent_name = excluded.talent_name
        """,
        (talent_id, talent_name),
    )


def select_all_classes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM classes ORDER BY class_name").fetchall()


def select_all_talents(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM talents ORDER BY talent_name").fetchall()


# ---------------------------------------------------------------------------
# Heroes canonical / game / printings
# ---------------------------------------------------------------------------


def upsert_hero_canonical(
    conn: sqlite3.Connection,
    *,
    canonical_id: str,
    canonical_slug: str,
    canonical_hero: str,
) -> None:
    conn.execute(
        """
        INSERT INTO heroes_canonical (canonical_id, canonical_slug, canonical_hero)
        VALUES (?,?,?)
        ON CONFLICT(canonical_id) DO UPDATE SET
            canonical_slug = excluded.canonical_slug,
            canonical_hero = excluded.canonical_hero
        """,
        (canonical_id, canonical_slug, canonical_hero),
    )


def select_hero_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM heroes_canonical WHERE canonical_slug = ?", [slug]
    ).fetchone()


def select_all_heroes_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM heroes_canonical ORDER BY canonical_slug"
    ).fetchall()


def upsert_hero_game(
    conn: sqlite3.Connection,
    *,
    hero_game_id: str,
    card_name: str,
    canonical_id: str,
    class_ids: str = "",
    talent_ids: str = "",
    health: str = "",
    intellect: str = "",
    ability_text: str = "",
    young_hero: str = "false",
) -> None:
    conn.execute(
        """
        INSERT INTO heroes_game
            (hero_game_id, card_name, canonical_id, class_ids, talent_ids,
             health, intellect, ability_text, young_hero)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(hero_game_id) DO UPDATE SET
            card_name    = excluded.card_name,
            canonical_id = excluded.canonical_id,
            class_ids    = excluded.class_ids,
            talent_ids   = excluded.talent_ids,
            health       = excluded.health,
            intellect    = excluded.intellect,
            ability_text = excluded.ability_text,
            young_hero   = excluded.young_hero
        """,
        (
            hero_game_id,
            card_name,
            canonical_id,
            class_ids,
            talent_ids,
            health,
            intellect,
            ability_text,
            young_hero,
        ),
    )


def select_all_heroes_game(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM heroes_game ORDER BY card_name").fetchall()


def upsert_hero_printing(
    conn: sqlite3.Connection,
    *,
    hero_game_id: str,
    set_id: str,
    card_id: str,
    rarity: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO heroes_printings (hero_game_id, set_id, card_id, rarity)
        VALUES (?,?,?,?)
        ON CONFLICT(hero_game_id, set_id, card_id) DO UPDATE SET
            rarity = excluded.rarity
        """,
        (hero_game_id, set_id, card_id, rarity),
    )


def select_all_heroes_printings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM heroes_printings ORDER BY hero_game_id, set_id, card_id"
    ).fetchall()


def upsert_hero_ll(
    conn: sqlite3.Connection,
    *,
    canonical_slug: str,
    card_name: str,
    format: str,
    date_in_effect: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO heroes_ll (canonical_slug, card_name, format, date_in_effect)
        VALUES (?,?,?,?)
        ON CONFLICT(card_name, format) DO UPDATE SET
            canonical_slug = excluded.canonical_slug,
            date_in_effect = excluded.date_in_effect
        """,
        (canonical_slug, card_name, format, date_in_effect),
    )


# ---------------------------------------------------------------------------
# Weapons canonical / game / printings
# ---------------------------------------------------------------------------


def upsert_weapon_canonical(
    conn: sqlite3.Connection,
    *,
    canonical_weapon_id: str,
    canonical_slug: str,
    canonical_weapon: str,
) -> None:
    conn.execute(
        """
        INSERT INTO weapons_canonical (canonical_weapon_id, canonical_slug, canonical_weapon)
        VALUES (?,?,?)
        ON CONFLICT(canonical_weapon_id) DO UPDATE SET
            canonical_slug   = excluded.canonical_slug,
            canonical_weapon = excluded.canonical_weapon
        """,
        (canonical_weapon_id, canonical_slug, canonical_weapon),
    )


def select_weapon_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM weapons_canonical WHERE canonical_slug = ?", [slug]
    ).fetchone()


def select_all_weapons_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM weapons_canonical ORDER BY canonical_slug"
    ).fetchall()


def upsert_weapon_game(
    conn: sqlite3.Connection,
    *,
    weapon_game_id: str,
    card_name: str,
    canonical_weapon_id: str,
    class_ids: str = "",
    talent_ids: str = "",
    cost: str = "",
    power: str = "",
    ability_text: str = "",
    types: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO weapons_game
            (weapon_game_id, card_name, canonical_weapon_id, class_ids, talent_ids,
             cost, power, ability_text, types)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(weapon_game_id) DO UPDATE SET
            card_name           = excluded.card_name,
            canonical_weapon_id = excluded.canonical_weapon_id,
            class_ids           = excluded.class_ids,
            talent_ids          = excluded.talent_ids,
            cost                = excluded.cost,
            power               = excluded.power,
            ability_text        = excluded.ability_text,
            types               = excluded.types
        """,
        (
            weapon_game_id,
            card_name,
            canonical_weapon_id,
            class_ids,
            talent_ids,
            cost,
            power,
            ability_text,
            types,
        ),
    )


def select_all_weapons_game(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM weapons_game ORDER BY card_name").fetchall()


def upsert_weapon_printing(
    conn: sqlite3.Connection,
    *,
    weapon_game_id: str,
    set_id: str,
    card_id: str,
    rarity: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO weapons_printings (weapon_game_id, set_id, card_id, rarity)
        VALUES (?,?,?,?)
        ON CONFLICT(weapon_game_id, set_id, card_id) DO UPDATE SET
            rarity = excluded.rarity
        """,
        (weapon_game_id, set_id, card_id, rarity),
    )


def select_all_weapons_printings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM weapons_printings ORDER BY weapon_game_id, set_id, card_id"
    ).fetchall()


# ---------------------------------------------------------------------------
# Equipment canonical / game / printings
# ---------------------------------------------------------------------------


def upsert_equipment_canonical(
    conn: sqlite3.Connection,
    *,
    canonical_equipment_id: str,
    canonical_slug: str,
    canonical_equipment: str,
) -> None:
    conn.execute(
        """
        INSERT INTO equipment_canonical
            (canonical_equipment_id, canonical_slug, canonical_equipment)
        VALUES (?,?,?)
        ON CONFLICT(canonical_equipment_id) DO UPDATE SET
            canonical_slug      = excluded.canonical_slug,
            canonical_equipment = excluded.canonical_equipment
        """,
        (canonical_equipment_id, canonical_slug, canonical_equipment),
    )


def select_equipment_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM equipment_canonical WHERE canonical_slug = ?", [slug]
    ).fetchone()


def select_all_equipment_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM equipment_canonical ORDER BY canonical_slug"
    ).fetchall()


def upsert_equipment_game(
    conn: sqlite3.Connection,
    *,
    equipment_game_id: str,
    card_name: str,
    canonical_equipment_id: str,
    class_ids: str = "",
    talent_ids: str = "",
    cost: str = "",
    defense: str = "",
    ability_text: str = "",
    types: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO equipment_game
            (equipment_game_id, card_name, canonical_equipment_id, class_ids, talent_ids,
             cost, defense, ability_text, types)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(equipment_game_id) DO UPDATE SET
            card_name              = excluded.card_name,
            canonical_equipment_id = excluded.canonical_equipment_id,
            class_ids              = excluded.class_ids,
            talent_ids             = excluded.talent_ids,
            cost                   = excluded.cost,
            defense                = excluded.defense,
            ability_text           = excluded.ability_text,
            types                  = excluded.types
        """,
        (
            equipment_game_id,
            card_name,
            canonical_equipment_id,
            class_ids,
            talent_ids,
            cost,
            defense,
            ability_text,
            types,
        ),
    )


def select_all_equipment_game(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM equipment_game ORDER BY card_name").fetchall()


def upsert_equipment_printing(
    conn: sqlite3.Connection,
    *,
    equipment_game_id: str,
    set_id: str,
    card_id: str,
    rarity: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO equipment_printings (equipment_game_id, set_id, card_id, rarity)
        VALUES (?,?,?,?)
        ON CONFLICT(equipment_game_id, set_id, card_id) DO UPDATE SET
            rarity = excluded.rarity
        """,
        (equipment_game_id, set_id, card_id, rarity),
    )


def select_all_equipment_printings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM equipment_printings ORDER BY equipment_game_id, set_id, card_id"
    ).fetchall()


# ---------------------------------------------------------------------------
# Story junction helpers
# ---------------------------------------------------------------------------


def set_story_heroes(
    conn: sqlite3.Connection,
    story_id: str,
    entries: list[tuple[str, str]],
) -> None:
    """Replace all story_heroes rows for ``story_id`` with ``(canonical_id, fragment)`` pairs."""
    conn.execute("DELETE FROM story_heroes WHERE story_id = ?", [story_id])
    if entries:
        conn.executemany(
            "INSERT OR IGNORE INTO story_heroes (story_id, canonical_id, fragment)"
            " VALUES (?,?,?)",
            [(story_id, cid, frag) for cid, frag in entries],
        )


def set_story_npcs(
    conn: sqlite3.Connection,
    story_id: str,
    entries: list[tuple[str, str]],
) -> None:
    """Replace all story_npcs rows for ``story_id`` with ``(character_id, fragment)`` pairs."""
    conn.execute("DELETE FROM story_npcs WHERE story_id = ?", [story_id])
    if entries:
        conn.executemany(
            "INSERT OR IGNORE INTO story_npcs (story_id, character_id, fragment)"
            " VALUES (?,?,?)",
            [(story_id, cid, frag) for cid, frag in entries],
        )


def set_story_junction(
    conn: sqlite3.Connection,
    story_id: str,
    table: str,
    id_col: str,
    ids: list[str],
) -> None:
    """Replace all junction rows for ``story_id`` in ``table`` with ``ids``.

    Deletes existing rows then inserts the new set atomically (caller wraps in
    a transaction). Empty ``ids`` clears all links for this story + type.
    """
    conn.execute(f"DELETE FROM {table} WHERE story_id = ?", [story_id])
    if ids:
        conn.executemany(
            f"INSERT OR IGNORE INTO {table} (story_id, {id_col}) VALUES (?,?)",
            [(story_id, eid) for eid in ids],
        )


def select_story_junction(
    conn: sqlite3.Connection, story_id: str, table: str, id_col: str
) -> list[str]:
    """Return entity ids linked to ``story_id`` in ``table``, sorted."""
    rows = conn.execute(
        f"SELECT {id_col} FROM {table} WHERE story_id = ? ORDER BY {id_col}",
        [story_id],
    ).fetchall()
    return [r[0] for r in rows]


def delete_all_story_junctions(
    conn: sqlite3.Connection, story_id: str
) -> dict[str, int]:
    """Delete all junction rows for ``story_id`` across every junction table.

    Returns a dict of table → rows deleted (for dry-run reporting).
    Note: with ``ON DELETE CASCADE`` this happens automatically when the story
    row is deleted, but this is useful for dry-run inspection.
    """
    junctions = [
        ("story_npcs", "character_id"),
        ("story_heroes", "canonical_id"),
        ("story_locations", "location_id"),
        ("story_regions", "region_id"),
        ("story_monsters", "monster_id"),
        ("story_fauna", "fauna_id"),
        ("story_flora", "flora_id"),
        ("story_food_drink", "food_drink_id"),
        ("story_weapons", "canonical_weapon_id"),
        ("story_equipment", "canonical_equipment_id"),
    ]
    counts: dict[str, int] = {}
    for table, _ in junctions:
        cur = conn.execute(f"DELETE FROM {table} WHERE story_id = ?", [story_id])
        counts[table] = cur.rowcount
    return counts


def count_entity_story_links(
    conn: sqlite3.Connection, junction_table: str, id_column: str, entity_id: str
) -> int:
    """Return how many story junction rows reference ``entity_id``.

    Used to guard :func:`delete_entity_row` against silently orphaning story
    links — callers should refuse to delete (or repoint links first) when
    this is non-zero.
    """
    return conn.execute(
        f"SELECT COUNT(*) FROM {junction_table} WHERE {id_column} = ?", [entity_id]
    ).fetchone()[0]


def delete_entity_row(
    conn: sqlite3.Connection, table: str, id_column: str, entity_id: str
) -> int:
    """Delete one row from a lore registry table by id. Returns rows deleted."""
    cur = conn.execute(f"DELETE FROM {table} WHERE {id_column} = ?", [entity_id])
    return cur.rowcount


def count_story_junctions(conn: sqlite3.Connection, story_id: str) -> dict[str, int]:
    """Return a count of linked entities per junction table (for dry-run output)."""
    junctions = [
        "story_npcs",
        "story_heroes",
        "story_locations",
        "story_regions",
        "story_monsters",
        "story_fauna",
        "story_flora",
        "story_food_drink",
        "story_weapons",
        "story_equipment",
    ]
    return {
        t: conn.execute(
            f"SELECT COUNT(*) FROM {t} WHERE story_id = ?", [story_id]
        ).fetchone()[0]
        for t in junctions
    }
