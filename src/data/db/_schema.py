"""DDL and forward-only schema migrations for the fablore SQLite database.

Version history:
  1 — initial schema (all 32 tables)
  2 — narrated_videos: add channel_link, duration columns
  3 — npcs: add other_characters_story_key column
  4 — story_heroes, story_npcs: add fragment column
  5 — heroes_ll: new table for living-legend status per hero variant
  6 — narrated_videos: drop duration column
  7 — weapons_printings, equipment_printings: image_url in the primary key
  8 — groups, group_npcs, group_heroes, story_groups; locations.parent_location_id
  9 — groups: lore_story_key, lore_fragment (the page a group is documented on)
"""

from __future__ import annotations

import sqlite3

CURRENT_VERSION = 10

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
    location_id        TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    region_id          TEXT NOT NULL DEFAULT '',
    notes              TEXT NOT NULL DEFAULT '',
    lore_fragment      TEXT NOT NULL DEFAULT '',
    -- Containment only: X is *inside* Y. Proximity ("area next to Candlehold")
    -- stays prose in notes, because the two read identically in the data and a
    -- mechanical migration would assert containments the lore denies. The split
    -- was reviewed row by row; see plans/location-containment-review.csv.
    -- No SQL REFERENCES: the column defaults to '' for the ~180 locations with no
    -- parent, and '' can never satisfy a foreign key. This is the same shape as
    -- region_id above, which is likewise validated in validate_data.py rather
    -- than by SQLite.
    parent_location_id TEXT NOT NULL DEFAULT ''
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
    image_url      TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (weapon_game_id, set_id, card_id, image_url)
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
    image_url         TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (equipment_game_id, set_id, card_id, image_url)
);

CREATE TABLE IF NOT EXISTS groups (
    group_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    kind            TEXT NOT NULL DEFAULT '',
    notes           TEXT NOT NULL DEFAULT '',
    -- A group inside a group: Boulders inside a clan, a guild inside a carnival.
    -- Both id columns default to '' and so carry no SQL REFERENCES; see the note
    -- on locations.parent_location_id. validate_data.py checks them.
    parent_group_id TEXT NOT NULL DEFAULT '',
    -- Only for a group that is *also* a physical place, e.g. Teklo Industries,
    -- which is a company and a works with 14 story links to the location. Most
    -- groups leave this empty; a group is not a place.
    location_id     TEXT NOT NULL DEFAULT '',
    -- Where the group is *documented*, not where it lives. A location reaches its
    -- page by walking region_id -> regions.world_of_rathe_story_key; a group has
    -- no region to walk, because a group is not tied to one place — so it carries
    -- the page itself. Both halves have precedent (the fragment on locations, the
    -- story key on regions); a single row holding both is new to groups.
    lore_story_key  TEXT NOT NULL DEFAULT '',
    lore_fragment   TEXT NOT NULL DEFAULT ''
);

-- Membership (R1). Declared on the group in entries/catalogue/groups.py, not on
-- the story: "Tara VanGeld is a VanGeld" is a world fact, not a page fact. See
-- D1 in plans/character-groups-schema-options.md. story_key is the optional
-- evidence column from D2 — an uncited membership is unsourced lore.
CREATE TABLE IF NOT EXISTS group_npcs (
    group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES npcs(character_id),
    story_key    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (group_id, character_id)
);

CREATE TABLE IF NOT EXISTS group_heroes (
    group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
    story_key    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (group_id, canonical_id)
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

-- Mentions (R5): this page names the Prowlers. Separate from group_npcs, which
-- is membership. Both are needed and they answer different questions.
CREATE TABLE IF NOT EXISTS story_groups (
    story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    group_id TEXT NOT NULL REFERENCES groups(group_id),
    PRIMARY KEY (story_id, group_id)
);

-- Names that are not the name (R4 epithets, R6 aliases). Three tables rather
-- than one keyed by entity_type, matching the group_npcs / group_heroes split:
-- each keeps a real REFERENCES to its own registry, which SQLite can enforce
-- and a shared entity_type column cannot.
--
-- Display names stay untouched. Nothing here renames anything; these rows are
-- the *other* names a thing answers to, which is what the tooltip matcher and
-- the Lore Graph need in order to stop drawing one thing as several.
CREATE TABLE IF NOT EXISTS npc_epithets (
    character_id TEXT NOT NULL REFERENCES npcs(character_id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    -- 'epithet' is a style the character is given: "the Wartune Herald".
    -- 'short-name' is the same character in fewer words: "Mortimer" for
    -- "Dr. Krest Mortimer, 'The Fixer'". Both resolve to one row, and both are
    -- match strings; the kind is what lets a tooltip word them differently.
    kind         TEXT NOT NULL DEFAULT 'epithet',
    sort_order   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, name)
);

CREATE TABLE IF NOT EXISTS location_aliases (
    location_id TEXT NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    -- Which era of the world used this name: 'Dhani', 'merfolk', 'pirate cant'.
    -- Empty where the lore does not date it.
    era         TEXT NOT NULL DEFAULT '',
    sort_order  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (location_id, alias)
);

CREATE TABLE IF NOT EXISTS group_aliases (
    group_id   TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    alias      TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (group_id, alias)
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
        conn.execute("PRAGMA user_version = 1")
        conn.commit()
        version = 1
    if version < 2:
        conn.execute("ALTER TABLE narrated_videos ADD COLUMN channel_link TEXT NOT NULL DEFAULT ''")
        conn.execute("ALTER TABLE narrated_videos ADD COLUMN duration TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 2")
        conn.commit()
    if version < 3:
        conn.execute("ALTER TABLE npcs" " ADD COLUMN other_characters_story_key TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 3")
        conn.commit()
    if version < 4:
        conn.execute("ALTER TABLE story_heroes ADD COLUMN fragment TEXT NOT NULL DEFAULT ''")
        conn.execute("ALTER TABLE story_npcs ADD COLUMN fragment TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 4")
        conn.commit()
    if version < 5:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS heroes_ll (
                canonical_slug TEXT NOT NULL,
                card_name      TEXT NOT NULL,
                format         TEXT NOT NULL,
                date_in_effect TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (card_name, format)
            )
            """
        )
        conn.execute("PRAGMA user_version = 5")
        conn.commit()
    if version < 6:
        conn.execute("ALTER TABLE narrated_videos DROP COLUMN duration")
        conn.execute("PRAGMA user_version = 6")
        conn.commit()
    if version < 7:
        # equipment-printings.csv and weapons-printings.csv carry an ImageURL column
        # produced from the game API by create_equipment_csv.py / create_weapons_csv.py.
        # The tables had no place for it, so export_to_csv() silently dropped the column
        # on every row — and because alternate printings differ *only* by image URL
        # (e.g. WTR005 in 2019-WTR and again in 2020-U-WTR), the old three-part primary
        # key collapsed them: 1301 equipment rows became 1166, 409 weapon rows became 347.
        # Any run of create_stories_index.py therefore corrupted both CSVs as a side
        # effect. Adding image_url to the key makes the CSV -> DB -> CSV round trip lossless.
        #
        # SQLite cannot alter a primary key, so each table is rebuilt. These hold derived
        # game data seeded from CSV, so they are left empty and repopulated by the reseed
        # in Database.__init__ rather than migrated row by row — existing rows have no
        # image_url to recover, and keeping them would collide with the reseeded rows.
        conn.executescript(
            """
            DROP TABLE IF EXISTS weapons_printings;
            CREATE TABLE weapons_printings (
                weapon_game_id TEXT NOT NULL REFERENCES weapons_game(weapon_game_id) ON DELETE CASCADE,
                set_id         TEXT NOT NULL,
                card_id        TEXT NOT NULL,
                rarity         TEXT NOT NULL DEFAULT '',
                image_url      TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (weapon_game_id, set_id, card_id, image_url)
            );
            DROP TABLE IF EXISTS equipment_printings;
            CREATE TABLE equipment_printings (
                equipment_game_id TEXT NOT NULL REFERENCES equipment_game(equipment_game_id) ON DELETE CASCADE,
                set_id            TEXT NOT NULL,
                card_id           TEXT NOT NULL,
                rarity            TEXT NOT NULL DEFAULT '',
                image_url         TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (equipment_game_id, set_id, card_id, image_url)
            );
            """
        )
        conn.execute("PRAGMA user_version = 7")
        conn.commit()
    if version < 8:
        # Groups: houses, clans, guilds, orders and troupes. Until now the only
        # home for one was a tooltip in hints_supplement.json, so "which stories
        # mention the Rosetta" was unanswerable and the Lore Graph had no group
        # node. 41 `# TODO: group —` comments were parked in entries/ as a result.
        #
        # locations.parent_location_id lands in the same migration because it is
        # the same column shape as groups.parent_group_id and costs nothing while
        # the migration is already open.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS groups (
                group_id        TEXT PRIMARY KEY,
                name            TEXT NOT NULL,
                kind            TEXT NOT NULL DEFAULT '',
                notes           TEXT NOT NULL DEFAULT '',
                parent_group_id TEXT NOT NULL DEFAULT '',
                location_id     TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS group_npcs (
                group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES npcs(character_id),
                story_key    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (group_id, character_id)
            );
            CREATE TABLE IF NOT EXISTS group_heroes (
                group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
                canonical_id TEXT NOT NULL REFERENCES heroes_canonical(canonical_id),
                story_key    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (group_id, canonical_id)
            );
            CREATE TABLE IF NOT EXISTS story_groups (
                story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
                group_id TEXT NOT NULL REFERENCES groups(group_id),
                PRIMARY KEY (story_id, group_id)
            );
            """
        )
        cols = {r[1] for r in conn.execute("PRAGMA table_info(locations)").fetchall()}
        if "parent_location_id" not in cols:
            conn.execute("ALTER TABLE locations ADD COLUMN parent_location_id TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 8")
        conn.commit()
    if version < 9:
        # Where a group is documented. The Hand of Sol was a locations row purely
        # so its tooltip and graph node could link to solana.md#the-hand-of-sol —
        # but an order of knights is not a place, and dropping that row would have
        # taken the link with it. A group has no region to walk to a page, so it
        # carries the page itself.
        cols = {r[1] for r in conn.execute("PRAGMA table_info(groups)").fetchall()}
        for col in ("lore_story_key", "lore_fragment"):
            if col not in cols:
                conn.execute(f"ALTER TABLE groups ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 9")
        conn.commit()
    if version < 10:
        # Names that are not the name. 36 NPC names glue an epithet on after a
        # comma, so a character can hold exactly one and the Heralds' second and
        # third have nowhere to go. Three locations are three rows for one place
        # (Fedhari / Coralysi / Fiddler's Green), which the Lore Graph draws as
        # three nodes. And hints_supplement.json had begun carrying alternate
        # spellings in `match` arrays — an alias living in the display layer,
        # which is the D3 two-writers shape all over again.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS npc_epithets (
                character_id TEXT NOT NULL REFERENCES npcs(character_id) ON DELETE CASCADE,
                name         TEXT NOT NULL,
                kind         TEXT NOT NULL DEFAULT 'epithet',
                sort_order   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (character_id, name)
            );
            CREATE TABLE IF NOT EXISTS location_aliases (
                location_id TEXT NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE,
                alias       TEXT NOT NULL,
                era         TEXT NOT NULL DEFAULT '',
                sort_order  INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (location_id, alias)
            );
            CREATE TABLE IF NOT EXISTS group_aliases (
                group_id   TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
                alias      TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (group_id, alias)
            );
            """
        )
        conn.execute("PRAGMA user_version = 10")
        conn.commit()
