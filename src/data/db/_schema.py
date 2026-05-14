"""DDL and forward-only schema migrations for the fablore SQLite database.

Version history:
  1 — initial schema (all 32 tables)
"""

from __future__ import annotations

import sqlite3

CURRENT_VERSION = 1

_V1_DDL = """
CREATE TABLE IF NOT EXISTS stories (
    story_id             TEXT PRIMARY KEY,
    story_key            TEXT UNIQUE NOT NULL,
    story_type           TEXT NOT NULL,
    title                TEXT NOT NULL,
    authors              TEXT NOT NULL DEFAULT '',
    artists              TEXT NOT NULL DEFAULT '',
    source_link          TEXT NOT NULL DEFAULT '',
    publication_date     TEXT NOT NULL DEFAULT '',
    thumbnail_image_link TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS narrated_videos (
    narrated_video_id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id          TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    author            TEXT NOT NULL,
    source_link       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
    region_id                TEXT PRIMARY KEY,
    region_name              TEXT NOT NULL,
    world_of_rathe_story_key TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS locations (
    location_id   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    region_id     TEXT NOT NULL DEFAULT '',
    notes         TEXT NOT NULL DEFAULT '',
    lore_fragment TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS npcs (
    character_id TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    species      TEXT NOT NULL DEFAULT 'Unknown',
    status       TEXT NOT NULL DEFAULT 'Unknown'
);

CREATE TABLE IF NOT EXISTS monsters (
    monster_id  TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS fauna (
    fauna_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS flora (
    flora_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS food_and_drink (
    food_drink_id TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    type          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS set_types (
    set_type_id  TEXT PRIMARY KEY,
    set_type     TEXT NOT NULL,
    set_type_layer TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sets (
    set_id               TEXT PRIMARY KEY,
    set_type_id          TEXT NOT NULL REFERENCES set_types(set_type_id),
    set_name             TEXT NOT NULL,
    initial_release_date TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS classes (
    class_id   TEXT PRIMARY KEY,
    class_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS talents (
    talent_id   TEXT PRIMARY KEY,
    talent_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS heroes_canonical (
    canonical_id   TEXT PRIMARY KEY,
    canonical_slug TEXT UNIQUE NOT NULL,
    canonical_hero TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS heroes_game (
    hero_game_id TEXT PRIMARY KEY,
    card_name    TEXT NOT NULL,
    canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
    class_ids    TEXT NOT NULL DEFAULT '',
    talent_ids   TEXT NOT NULL DEFAULT '',
    health       TEXT NOT NULL DEFAULT '',
    intellect    TEXT NOT NULL DEFAULT '',
    ability_text TEXT NOT NULL DEFAULT '',
    young_hero   TEXT NOT NULL DEFAULT 'false'
);

CREATE TABLE IF NOT EXISTS heroes_printings (
    hero_game_id TEXT NOT NULL REFERENCES heroes_game(hero_game_id) ON DELETE CASCADE,
    set_id       TEXT NOT NULL,
    card_id      TEXT NOT NULL,
    rarity       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (hero_game_id, set_id, card_id)
);

CREATE TABLE IF NOT EXISTS weapons_canonical (
    canonical_weapon_id TEXT PRIMARY KEY,
    canonical_slug      TEXT UNIQUE NOT NULL,
    canonical_weapon    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weapons_game (
    weapon_game_id      TEXT PRIMARY KEY,
    card_name           TEXT NOT NULL,
    canonical_weapon_id TEXT NOT NULL REFERENCES weapons_canonical(canonical_weapon_id),
    class_ids           TEXT NOT NULL DEFAULT '',
    talent_ids          TEXT NOT NULL DEFAULT '',
    cost                TEXT NOT NULL DEFAULT '',
    power               TEXT NOT NULL DEFAULT '',
    ability_text        TEXT NOT NULL DEFAULT '',
    types               TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS weapons_printings (
    weapon_game_id TEXT NOT NULL REFERENCES weapons_game(weapon_game_id) ON DELETE CASCADE,
    set_id         TEXT NOT NULL,
    card_id        TEXT NOT NULL,
    rarity         TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (weapon_game_id, set_id, card_id)
);

CREATE TABLE IF NOT EXISTS equipment_canonical (
    canonical_equipment_id TEXT PRIMARY KEY,
    canonical_slug         TEXT UNIQUE NOT NULL,
    canonical_equipment    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS equipment_game (
    equipment_game_id      TEXT PRIMARY KEY,
    card_name              TEXT NOT NULL,
    canonical_equipment_id TEXT NOT NULL REFERENCES equipment_canonical(canonical_equipment_id),
    class_ids              TEXT NOT NULL DEFAULT '',
    talent_ids             TEXT NOT NULL DEFAULT '',
    cost                   TEXT NOT NULL DEFAULT '',
    defense                TEXT NOT NULL DEFAULT '',
    ability_text           TEXT NOT NULL DEFAULT '',
    types                  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS equipment_printings (
    equipment_game_id TEXT NOT NULL REFERENCES equipment_game(equipment_game_id) ON DELETE CASCADE,
    set_id            TEXT NOT NULL,
    card_id           TEXT NOT NULL,
    rarity            TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (equipment_game_id, set_id, card_id)
);

-- Story junction tables (all cascade-delete when a story is removed)
CREATE TABLE IF NOT EXISTS story_npcs (
    story_id     TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES npcs(character_id),
    PRIMARY KEY (story_id, character_id)
);

CREATE TABLE IF NOT EXISTS story_heroes (
    story_id     TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
    PRIMARY KEY (story_id, canonical_id)
);

CREATE TABLE IF NOT EXISTS story_locations (
    story_id    TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    location_id TEXT NOT NULL REFERENCES locations(location_id),
    PRIMARY KEY (story_id, location_id)
);

CREATE TABLE IF NOT EXISTS story_regions (
    story_id  TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    PRIMARY KEY (story_id, region_id)
);

CREATE TABLE IF NOT EXISTS story_monsters (
    story_id   TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    monster_id TEXT NOT NULL REFERENCES monsters(monster_id),
    PRIMARY KEY (story_id, monster_id)
);

CREATE TABLE IF NOT EXISTS story_fauna (
    story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    fauna_id TEXT NOT NULL REFERENCES fauna(fauna_id),
    PRIMARY KEY (story_id, fauna_id)
);

CREATE TABLE IF NOT EXISTS story_flora (
    story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    flora_id TEXT NOT NULL REFERENCES flora(flora_id),
    PRIMARY KEY (story_id, flora_id)
);

CREATE TABLE IF NOT EXISTS story_food_drink (
    story_id      TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    food_drink_id TEXT NOT NULL REFERENCES food_and_drink(food_drink_id),
    PRIMARY KEY (story_id, food_drink_id)
);

CREATE TABLE IF NOT EXISTS story_weapons (
    story_id            TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    canonical_weapon_id TEXT NOT NULL REFERENCES weapons_canonical(canonical_weapon_id),
    PRIMARY KEY (story_id, canonical_weapon_id)
);

CREATE TABLE IF NOT EXISTS story_equipment (
    story_id               TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    canonical_equipment_id TEXT NOT NULL REFERENCES equipment_canonical(canonical_equipment_id),
    PRIMARY KEY (story_id, canonical_equipment_id)
);
"""


def apply_schema(conn: sqlite3.Connection) -> None:
    """Create all tables from scratch (called for version 0 → 1 migration)."""
    conn.executescript(_V1_DDL)


def migrate(conn: sqlite3.Connection) -> None:
    """Apply all pending forward-only migrations based on PRAGMA user_version."""
    version: int = conn.execute("PRAGMA user_version").fetchone()[0]
    if version < 1:
        apply_schema(conn)
        conn.execute(f"PRAGMA user_version = {CURRENT_VERSION}")
        conn.commit()
