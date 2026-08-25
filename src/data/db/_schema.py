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
 10 — npc_epithets, location_aliases, group_aliases (the names that are not the name)
 11 — species, npc_species, species_aliases; npcs.species free text retired
 12 — npcs renamed to characters (character_id unchanged); character_heroes
      links a canonical hero to its character row; every hero gets a
      character row, self-healing at seed time; status becomes a closed
      five-value vocabulary
 13 — titles, title_holders, story_titles: offices (Grand Magister, Dracai of
      Aether) with ordered or concurrent holders, resolved through
      character_heroes so a hero and an ordinary character can share one title_holders row
 14 — character_kin: kinship facts (father, mother, parent, sibling, spouse,
      child), one row per stated fact; the inverse is derived at read time,
      never stored
 15 — professions, character_professions: a trade many hold independently
      (Braumeister, shieldbearer) — unbounded and unsourceable, unlike a
      group's roster, so there is no ``member_source`` and no citation column.
      Resolved through ``character_heroes`` exactly as ``title_holders`` is, so
      a profession reaches a hero with no ``CharacterEntry`` of its own.
 16 — characters.summary: the tooltip text for a person. Until this column
      existed generate_hints_json.py emitted nothing for people at all and
      hints_supplement.json was the sole writer of every one, which also left
      the npc_epithets rows stage 3 created rendering nowhere.
 17 — story_npcs + story_heroes merge into story_characters: after migration
      12's identity spine a hero and an ordinary character are rows of the same `characters`
      table, so one junction (keyed on character_id, still carrying
      fragment) reaches both, exactly as title_holders (13) and
      character_professions (15) already read through character_heroes for
      the same reason. A person declared through both paths for one story
      collapses to one row; see the migration block for the fragment
      tie-break.
 18 — group_npcs + group_heroes merge into group_characters: the roster half
      of the same move 17 made for story links. GroupEntry loses character_members
      and hero_members for one `members` tuple that takes a CharacterEntry or a
      canonical hero slug, which also gives a hero member the
      (member, story_key) citation pair only a ``CharacterEntry`` member could carry.
 19 — species -> kinds, npc_species -> character_kinds, species_aliases ->
      kind_aliases, npc_epithets -> character_epithets; species_id -> kind_id.
      The declaration surface followed in the same sprint: SpeciesEntry became
      KindEntry and CharacterEntry(species=) became CharacterEntry(kinds=).
"""

from __future__ import annotations

import sqlite3

CURRENT_VERSION = 19

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

-- No species column. What a character *is* lives in character_kinds, because one
-- free-text column held three different facts — species, cosmological tier and
-- occupation — and could hold only one of them at a time. Scooba is a Zombie Dog.
--
-- Renamed from npcs in migration 12. character_id is unchanged: it is still
-- LC + SHA-256 of normalize_name(name), the same lore_character_id() every
-- caller already used, so no row's id moved. Like every registry id in this
-- file, it is a hash of the name at the call site — editing a stored name here
-- does not update the row, it mints a second one and strands the first.
CREATE TABLE IF NOT EXISTS characters (
    character_id TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'Unknown',
    -- Tooltip text (migration 16). Owned by descriptions.py like every other
    -- registry's lore text, never by entries/catalogue/ — two writers for one
    -- summary is the hazard the faction and species entries were migrated out
    -- of. Preserve-on-empty, like status and locations.notes.
    summary      TEXT NOT NULL DEFAULT ''
);

-- Identity spine (migration 12). heroes_canonical and characters are two
-- registries for one person — a hero is exactly one character, so
-- canonical_id is the primary key here, not character_id. A person may be
-- several heroes in principle (character_id is not unique), though nothing
-- exercises that yet.
--
-- Populated two ways: CharacterEntry(hero_slug=...) declares "this character row is that
-- hero", and seed time self-heals every hero this table does not yet cover by
-- minting a character row (status 'Unknown') and linking it — so a hero added
-- later by create_heroes_csv.py can never end up without an identity. An
-- existing row here always wins over the self-heal.
CREATE TABLE IF NOT EXISTS character_heroes (
    canonical_id TEXT PRIMARY KEY REFERENCES heroes_canonical(canonical_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_character_heroes_character_id ON character_heroes(character_id);

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
--
-- Merges group_npcs and group_heroes (migration 18), the roster half of the
-- move migration 17 made for story links: a hero and an ordinary character are rows of the
-- same `characters` table, so one junction keyed on character_id holds a
-- whole roster. GroupEntry.members takes a CharacterEntry or a canonical hero slug
-- and both land here. story_key stays the per-membership evidence column.
CREATE TABLE IF NOT EXISTS group_characters (
    group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES characters(character_id),
    story_key    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (group_id, character_id)
);

-- Story junction tables (all cascade-delete when a story is removed)
--
-- Merges story_npcs and story_heroes (migration 17). A hero and an ordinary character are
-- rows of the same `characters` table since migration 12, so every entry in
-- upsert_story()'s characters= list — a hero slug or a CharacterEntry — resolves
-- to a character_id and writes here, one row per (story, person). fragment
-- carries the mdBook heading anchor either kind of entry can give it; see
-- Database.upsert_story's fragments= docstring for how a declaration names
-- one.
CREATE TABLE IF NOT EXISTS story_characters (
    story_id     TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES characters(character_id),
    fragment     TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (story_id, character_id)
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

-- Mentions (R5): this page names the Prowlers. Separate from group_characters, which
-- is membership. Both are needed and they answer different questions.
CREATE TABLE IF NOT EXISTS story_groups (
    story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    group_id TEXT NOT NULL REFERENCES groups(group_id),
    PRIMARY KEY (story_id, group_id)
);

-- An office: Grand Magister, Dracai of Aether, Soothsayer. A person may hold
-- several titles and a title may have several holders at once — the Dracai are
-- distinct offices held concurrently, the five Grand Magisters are one office
-- held in succession.
CREATE TABLE IF NOT EXISTS titles (
    title_id   TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    -- The body this office belongs to, if any: Dracai of Aether hangs off the
    -- Dracai, Soothsayer hangs off nothing. Defaults to '' and carries no SQL
    -- REFERENCES, the same shape as groups.parent_group_id and
    -- locations.parent_location_id: '' can never satisfy a foreign key, so
    -- validate_data.py checks it instead.
    group_id   TEXT NOT NULL DEFAULT '',
    notes      TEXT NOT NULL DEFAULT ''
);

-- Holders (R3). character_id is what migration 12's identity spine makes
-- possible: a hero and an ordinary character can be the same row of this column, with no
-- second table the way group_npcs/group_heroes needed one before migration 18 — Kano the hero and
-- the five Grand Magister characters share one junction.
CREATE TABLE IF NOT EXISTS title_holders (
    title_id     TEXT NOT NULL REFERENCES titles(title_id) ON DELETE CASCADE,
    character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    -- Records a succession where the lore gives one (Grand Magister 1-5) and is
    -- 0 where it does not. Not unique: several holders may share an ordinal
    -- (the Dracai, held concurrently) or all carry 0.
    ordinal      INTEGER NOT NULL DEFAULT 0,
    story_key    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (title_id, character_id)
);

-- Mentions (R5), mirroring story_groups: this page names the Grand Magisters.
-- Separate from title_holders, which is who held the office. Both are needed
-- and they answer different questions.
CREATE TABLE IF NOT EXISTS story_titles (
    story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
    title_id TEXT NOT NULL REFERENCES titles(title_id),
    PRIMARY KEY (story_id, title_id)
);

-- Kinship (R8). "Lyath's father is Bloodworth Goldmane" is one row, not two.
-- Storing the inverse too ("Bloodworth's child is Lyath") would let the two
-- halves disagree with each other with nothing to say which is right, so only
-- the stated direction is ever written; db._queries.select_character_kin_both_directions
-- derives "who are Bloodworth's children" at read time instead, via
-- db._queries.KIN_INVERSE. No kin_id: this is a junction, not a registry, the
-- same shape as group_characters.
--
-- relation is a closed vocabulary, checked in validate_data.py rather than by
-- SQLite (the same split status and npc_epithets.kind follow):
-- 'father'/'mother'/'parent' invert to 'child'; 'child' inverts to 'parent',
-- not a gender, because the data does not know which parent; 'sibling' and
-- 'spouse' are their own inverse.
CREATE TABLE IF NOT EXISTS character_kin (
    character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    relative_id  TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    relation     TEXT NOT NULL,
    story_key    TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (character_id, relative_id, relation)
);

-- Names that are not the name (R4 epithets, R6 aliases). Three tables rather
-- than one keyed by entity_type, matching the group_npcs / group_heroes split that
-- migration 18 has since closed:
-- each keeps a real REFERENCES to its own registry, which SQLite can enforce
-- and a shared entity_type column cannot.
--
-- Display names stay untouched. Nothing here renames anything; these rows are
-- the *other* names a thing answers to, which is what the tooltip matcher and
-- the Lore Graph need in order to stop drawing one thing as several.
CREATE TABLE IF NOT EXISTS character_epithets (
    character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
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

-- What a character *is* (R2). One flat list: Herald sits beside Human and beside
-- Parrot, because the line between a people, an order of being and an animal is
-- a reading of the lore rather than a fact the data can check, and a column
-- nobody can validate is a column that drifts.
--
-- Called `species` until migration 19, which was the wrong word for most of what
-- it held: Dragon, Herald, Aesir, Ancient and Embra are orders of being, Zombie
-- is an acquired condition that stacks, and Robot is manufactured. "Kind" is the
-- only word true of all of them at once. `kind_id` keeps the `SP` prefix its
-- hash was minted with — the prefix is stored data, so renaming it would move
-- every id and every foreign key with it.
CREATE TABLE IF NOT EXISTS kinds (
    kind_id TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    notes   TEXT NOT NULL DEFAULT ''
);

-- Many-to-many, unlike the column it replaces. `Zombie Dog` and `Human Cleric`
-- were single values gluing two facts together; splitting them needs somewhere
-- for both halves to go, so Scooba holds Zombie and Dog at once.
CREATE TABLE IF NOT EXISTS character_kinds (
    character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    kind_id      TEXT NOT NULL REFERENCES kinds(kind_id) ON DELETE CASCADE,
    sort_order   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, kind_id)
);

-- The fourth alias table (R6). The prose writes "Aesirs" and "Embras", and the
-- supplement entries these replace carried those plurals by hand. English
-- plurals are not mechanical enough to generate — `Aesir` takes an s, `Human`
-- would too but nothing writes it, and `Chanek` does not.
CREATE TABLE IF NOT EXISTS kind_aliases (
    kind_id    TEXT NOT NULL REFERENCES kinds(kind_id) ON DELETE CASCADE,
    alias      TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (kind_id, alias)
);

-- A trade many hold independently (R9): Braumeister, shieldbearer. Unlike a
-- group's roster there is no member_source column here — "who is a
-- Braumeister" is unbounded and unsourceable, which is exactly what a group's
-- member_source exists to prevent, so a profession never gets one.
CREATE TABLE IF NOT EXISTS professions (
    profession_id TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    notes         TEXT NOT NULL DEFAULT ''
);

-- Many-to-many against `characters`, not `npcs` — after migration 12's identity
-- spine, a hero and an ordinary character are rows of the same table, so one junction reaches
-- both. Kano is a hero with no ``CharacterEntry``; his profession still lands here.
CREATE TABLE IF NOT EXISTS character_professions (
    character_id  TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
    profession_id TEXT NOT NULL REFERENCES professions(profession_id) ON DELETE CASCADE,
    sort_order    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, profession_id)
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
        # Targets "characters", the migration-12 name, so a from-scratch build
        # (which creates "characters" directly via _V1_DDL) can run this block
        # too — this step never touches the real npcs-named table on disk,
        # because that database is already past version 3.
        conn.execute("ALTER TABLE characters" " ADD COLUMN other_characters_story_key TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 3")
        conn.commit()
    if version < 4:
        # Guarded by existence (migration 17): a from-scratch build no longer
        # creates story_heroes/story_npcs at all — _V1_DDL creates
        # story_characters directly, with fragment already on it — so this
        # step has nothing to ALTER on that path. A real database still
        # sitting below version 4 has both tables and gets the column added,
        # same as before.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "story_heroes" in tables:
            conn.execute("ALTER TABLE story_heroes ADD COLUMN fragment TEXT NOT NULL DEFAULT ''")
        if "story_npcs" in tables:
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
        # Names that are not the name. 36 character names glue an epithet on after a
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
    if version < 11:
        # What a character *is* (R2). One free-text column held three different
        # facts and could hold only one at a time: species proper (Human, Dwarf,
        # Welkin), cosmological tier (Herald, Aesir, Ancient, Embra, Dragon),
        # and occupation (Wizard, Witch, Diviner) — plus two memberships that had
        # nowhere else to go, and `Unkown` next to `Unknown` ×50.
        #
        # No data is carried across. The database is seeded from the CSVs, and
        # this migration empties a fact the CSVs alone can restore, so `species`
        # joins the tables `db._seed.needs_seed` watches — the same move
        # migration 7 made for the printings tables.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS species (
                species_id TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                notes      TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS npc_species (
                character_id TEXT NOT NULL REFERENCES npcs(character_id) ON DELETE CASCADE,
                species_id   TEXT NOT NULL REFERENCES species(species_id) ON DELETE CASCADE,
                sort_order   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (character_id, species_id)
            );
            CREATE TABLE IF NOT EXISTS species_aliases (
                species_id TEXT NOT NULL REFERENCES species(species_id) ON DELETE CASCADE,
                alias      TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (species_id, alias)
            );
            """
        )
        # Resolve the table by whichever name it currently has. A from-scratch
        # build already created it as "characters" via _V1_DDL; a database
        # sitting at version 10 still calls it "npcs", because the rename is
        # migration 12 and has not run yet. Naming only one of the two would
        # make PRAGMA table_info report zero rows for the other and skip the
        # DROP silently — which would carry the retired free-text species
        # column through the rename and undo stage 4 on exactly the databases
        # that had not caught up yet.
        _t = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        _npc_table = "characters" if "characters" in _t else "npcs"
        if any(r[1] == "species" for r in conn.execute(f"PRAGMA table_info({_npc_table})")):
            conn.execute(f"ALTER TABLE {_npc_table} DROP COLUMN species")
        conn.execute("PRAGMA user_version = 11")
        conn.commit()
    if version < 12:
        # Identity spine. heroes_canonical (78 rows) and npcs (334 rows) were
        # two registries for one thing: a person. The split ran through four
        # places — group_npcs/group_heroes and story_npcs/story_heroes are
        # matched pairs, while npc_epithets and npc_species had no hero half
        # at all, which is why a species row could never be created for
        # Volcai or Dracai: every named Volcoran is a hero, and
        # heroes_canonical has three columns and no species.
        #
        # npcs is renamed to characters — same character_id, same
        # lore_character_id() hashing, no id changes — and character_heroes
        # links a canonical hero to its character row. Guarded so this is
        # safe to run against either starting point: an existing database
        # still has the table under its old name, while a from-scratch build
        # already created "characters" directly via _V1_DDL.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "npcs" in tables and "characters" not in tables:
            conn.execute("ALTER TABLE npcs RENAME TO characters")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS character_heroes (
                canonical_id TEXT PRIMARY KEY REFERENCES heroes_canonical(canonical_id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_character_heroes_character_id ON character_heroes(character_id);
            """
        )
        conn.execute("PRAGMA user_version = 12")
        conn.commit()
    if version < 13:
        # Titles and their holders (Option D, stage 7). A person may hold
        # several titles and a title may have several holders at once — the
        # Dracai are distinct offices held concurrently, the Grand Magisters
        # are one office held in succession.
        #
        # No table-name ambiguity to guard here, unlike migration 11's
        # npcs/characters rename: these are three brand-new tables, and
        # CREATE TABLE IF NOT EXISTS is correct whether this runs against a
        # database that just applied migration 12 or a from-scratch build
        # that already created them via _V1_DDL.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS titles (
                title_id   TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                group_id   TEXT NOT NULL DEFAULT '',
                notes      TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS title_holders (
                title_id     TEXT NOT NULL REFERENCES titles(title_id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
                ordinal      INTEGER NOT NULL DEFAULT 0,
                story_key    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (title_id, character_id)
            );
            CREATE TABLE IF NOT EXISTS story_titles (
                story_id TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
                title_id TEXT NOT NULL REFERENCES titles(title_id),
                PRIMARY KEY (story_id, title_id)
            );
            """
        )
        conn.execute("PRAGMA user_version = 13")
        conn.commit()
    if version < 14:
        # Kinship (R8). One row per stated fact; the inverse is derived at read
        # time by db._queries.select_character_kin_both_directions, never
        # stored, so "Lyath's father is Bloodworth" and "Bloodworth's child is
        # Lyath" cannot come to disagree with each other.
        #
        # No table-name ambiguity to guard here, unlike migration 11's
        # npcs/characters rename: this is one brand-new table, and
        # CREATE TABLE IF NOT EXISTS is correct whether this runs against a
        # database that just applied migration 13 or a from-scratch build
        # that already created it via _V1_DDL.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS character_kin (
                character_id TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
                relative_id  TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
                relation     TEXT NOT NULL,
                story_key    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (character_id, relative_id, relation)
            );
            """
        )
        conn.execute("PRAGMA user_version = 14")
        conn.commit()
    if version < 15:
        # Professions (R9): a trade many hold independently, unbounded and
        # unsourceable — Braumeister is "the elite of their trade", not a named
        # roster, which is why there is no member_source here the way groups.py
        # has one. character_professions references `characters`, matching
        # title_holders and character_kin (both post-date migration 12's
        # rename), rather than the legacy `npc_species` shape that still says
        # "npc" in its own name for a table that has referenced `characters`
        # since migration 12.
        #
        # No table-name ambiguity to guard here, unlike migration 11's
        # npcs/characters rename: these are two brand-new tables, and
        # CREATE TABLE IF NOT EXISTS is correct whether this runs against a
        # database sitting at any earlier version or a from-scratch build that
        # already created them via _V1_DDL.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS professions (
                profession_id TEXT PRIMARY KEY,
                name          TEXT NOT NULL,
                notes         TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS character_professions (
                character_id  TEXT NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
                profession_id TEXT NOT NULL REFERENCES professions(profession_id) ON DELETE CASCADE,
                sort_order    INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (character_id, profession_id)
            );
            """
        )
        conn.execute("PRAGMA user_version = 15")
        conn.commit()
    if version < 16:
        # The tooltip text for a person. generate_hints_json.py emitted entries
        # for locations, monsters, fauna, flora, groups and species, and nothing
        # at all for people, because there was nowhere to put the sentence — so
        # hints_supplement.json hand-wrote all 39 ordinary-character and 65 hero tooltips, and
        # the 25 npc_epithets rows stage 3 created were correct data that
        # rendered nowhere.
        #
        # Guarded by name like migration 12's ALTER, and resolved against
        # whichever name the table currently has, for the reason migration 11
        # had to be corrected: a database that has not reached the rename yet
        # still calls this table `npcs`, and naming only one of the two would
        # skip the column silently on exactly the databases that were behind.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        target = "characters" if "characters" in tables else "npcs"
        if target in tables:
            cols = {r[1] for r in conn.execute(f"PRAGMA table_info({target})")}
            if "summary" not in cols:
                conn.execute(f"ALTER TABLE {target} ADD COLUMN summary TEXT NOT NULL DEFAULT ''")
        conn.execute("PRAGMA user_version = 16")
        conn.commit()
    if version < 17:
        # story_npcs (character_id) and story_heroes (canonical_id) both carry a
        # fragment column and both key a story to a person. After migration 12's
        # identity spine a hero and an ordinary character are rows of the same `characters`
        # table, so one junction — keyed on character_id — reaches both, the
        # same move title_holders (13) and character_professions (15) already
        # made for a different relationship.
        #
        # THE TRAP: character_heroes is populated by a *seed-time* self-heal
        # (_self_heal_character_heroes in db/_seed.py), not by migration 12
        # itself. Database.__init__ runs every pending migration back-to-back
        # before it ever checks whether a seed is needed (see open_db), so a
        # database sitting below version 12 that opens after this migration
        # exists runs migrations 12..17 in one call with character_heroes
        # completely empty throughout. Resolving story_heroes.canonical_id
        # through character_heroes and skipping what does not match would
        # silently drop every hero story link. Instead this mints the missing
        # link itself, exactly as Database._upsert_one_title does for a hero
        # holder at write time: look up heroes_canonical.canonical_hero, hash
        # it with lore_character_id, insert the characters row if absent, and
        # insert the character_heroes link — INSERT OR IGNORE throughout, so an
        # existing link (or an existing character row) always wins.
        #
        # Resolved by whichever name the character table currently has, like
        # migrations 11/12/16: by the time this block runs, migration 12 has
        # already executed earlier in the same migrate() call for any database
        # starting below version 12, so the table is "characters" in every
        # reachable case — this still checks rather than assumes it, matching
        # every other migration's guard style in this file.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        char_table = "characters" if "characters" in tables else "npcs"

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS story_characters (
                story_id     TEXT NOT NULL REFERENCES stories(story_id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES {char_table}(character_id),
                fragment     TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (story_id, character_id)
            )
            """
        )

        if "story_heroes" in tables or "story_npcs" in tables:
            # Local, function-scoped import: _schema.py carries no sys.path
            # bootstrap of its own (unlike _domain.py / _seed.py), and
            # db/_seed.py's own self-heal takes the same local-import shape
            # for the same reason — this module can be imported before
            # src/data is on sys.path, so the bootstrap has to happen here,
            # right before the one place that needs registry_ids.
            import sys as _sys
            from pathlib import Path as _Path

            _script_dir = _Path(__file__).resolve().parents[1]
            if str(_script_dir) not in _sys.path:
                _sys.path.insert(0, str(_script_dir))
            from registry_ids import lore_character_id  # noqa: PLC0415

            hero_character_id: dict[str, str] = {}
            if "character_heroes" in tables:
                hero_character_id = {
                    row[0]: row[1] for row in conn.execute("SELECT canonical_id, character_id FROM character_heroes")
                }

            def _character_id_for_hero(canonical_id: str) -> str:
                cid = hero_character_id.get(canonical_id)
                if cid:
                    return cid
                row = conn.execute(
                    "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
                    [canonical_id],
                ).fetchone()
                hero_name = row[0] if row else ""
                new_cid = lore_character_id(hero_name)
                conn.execute(
                    f"INSERT OR IGNORE INTO {char_table} (character_id, name, status) VALUES (?,?,'Unknown')",
                    (new_cid, hero_name),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO character_heroes (canonical_id, character_id) VALUES (?,?)",
                    (canonical_id, new_cid),
                )
                hero_character_id[canonical_id] = new_cid
                return new_cid

            # (story_id, character_id) -> fragment. A non-empty fragment
            # always beats an empty one whichever side carries it, and where
            # both sides carry a real anchor story_heroes wins — see the
            # docstring on Database.upsert_story's fragments= for why the
            # *write* path raises on that contradiction and this historical
            # migration does not: story-npcs.csv carries zero non-empty
            # fragments (verified against the committed file), so a genuine
            # disagreement is not a case the CSVs contain. The empty-beats-
            # nothing rule is here so that a database whose story_npcs rows
            # did not come from those CSVs cannot lose an anchor silently.
            merged: dict[tuple[str, str], str] = {}
            if "story_heroes" in tables:
                for story_id, canonical_id, fragment in conn.execute(
                    "SELECT story_id, canonical_id, fragment FROM story_heroes"
                ):
                    character_id = _character_id_for_hero(canonical_id)
                    merged[(story_id, character_id)] = fragment or ""
            if "story_npcs" in tables:
                for story_id, character_id, fragment in conn.execute(
                    "SELECT story_id, character_id, fragment FROM story_npcs"
                ):
                    key = (story_id, character_id)
                    if not merged.get(key):
                        merged[key] = fragment or ""

            if merged:
                conn.executemany(
                    "INSERT OR IGNORE INTO story_characters (story_id, character_id, fragment) VALUES (?,?,?)",
                    [(sid, cid, frag) for (sid, cid), frag in merged.items()],
                )

            conn.executescript("DROP TABLE IF EXISTS story_heroes; DROP TABLE IF EXISTS story_npcs;")

        conn.execute("PRAGMA user_version = 17")
        conn.commit()
    if version < 18:
        # The roster half of migration 17. group_npcs (character_id) and
        # group_heroes (canonical_id) both key a group to a person and both
        # carry the same story_key evidence column, so after migration 12's
        # identity spine they are one junction keyed on character_id.
        #
        # THE SAME TRAP AS 17, and it is not solved by 17 having run first.
        # character_heroes is filled by a seed-time self-heal, not by migration
        # 12, and migrate() runs every pending block before Database.__init__
        # ever checks whether a seed is needed. Migration 17 mints a link for
        # every hero that had a *story* row; a hero with a group row and no
        # story row still has none, so this block must mint its own too rather
        # than lean on its predecessor. Same INSERT OR IGNORE contract: an
        # existing link, or an existing characters row, always wins.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        char_table = "characters" if "characters" in tables else "npcs"

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS group_characters (
                group_id     TEXT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
                character_id TEXT NOT NULL REFERENCES {char_table}(character_id),
                story_key    TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (group_id, character_id)
            )
            """
        )

        if "group_heroes" in tables or "group_npcs" in tables:
            # Function-scoped import for the reason migration 17 gives: this
            # module carries no sys.path bootstrap of its own.
            import sys as _sys
            from pathlib import Path as _Path

            _script_dir = _Path(__file__).resolve().parents[1]
            if str(_script_dir) not in _sys.path:
                _sys.path.insert(0, str(_script_dir))
            from registry_ids import lore_character_id  # noqa: PLC0415

            hero_character_id: dict[str, str] = {}
            if "character_heroes" in tables:
                hero_character_id = {
                    row[0]: row[1] for row in conn.execute("SELECT canonical_id, character_id FROM character_heroes")
                }

            def _group_character_id_for_hero(canonical_id: str) -> str:
                cid = hero_character_id.get(canonical_id)
                if cid:
                    return cid
                row = conn.execute(
                    "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
                    [canonical_id],
                ).fetchone()
                hero_name = row[0] if row else ""
                new_cid = lore_character_id(hero_name)
                conn.execute(
                    f"INSERT OR IGNORE INTO {char_table} (character_id, name, status) VALUES (?,?,'Unknown')",
                    (new_cid, hero_name),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO character_heroes (canonical_id, character_id) VALUES (?,?)",
                    (canonical_id, new_cid),
                )
                hero_character_id[canonical_id] = new_cid
                return new_cid

            # (group_id, character_id) -> story_key. A cited membership beats an
            # uncited one whichever side carries it, and where both cite a page
            # group_npcs wins. Unlike the write path, which raises when one
            # roster names a person twice, a historical migration takes the row
            # it is given: the committed CSVs contain no group named on both
            # sides, so a genuine disagreement is not a case that reaches here.
            merged: dict[tuple[str, str], str] = {}
            if "group_npcs" in tables:
                for group_id, character_id, story_key in conn.execute(
                    "SELECT group_id, character_id, story_key FROM group_npcs"
                ):
                    merged[(group_id, character_id)] = story_key or ""
            if "group_heroes" in tables:
                for group_id, canonical_id, story_key in conn.execute(
                    "SELECT group_id, canonical_id, story_key FROM group_heroes"
                ):
                    key = (group_id, _group_character_id_for_hero(canonical_id))
                    if not merged.get(key):
                        merged[key] = story_key or ""

            if merged:
                conn.executemany(
                    "INSERT OR IGNORE INTO group_characters (group_id, character_id, story_key) VALUES (?,?,?)",
                    [(gid, cid, key) for (gid, cid), key in merged.items()],
                )

            conn.executescript("DROP TABLE IF EXISTS group_npcs; DROP TABLE IF EXISTS group_heroes;")

        conn.execute("PRAGMA user_version = 18")
        conn.commit()

    if version < 19:
        # "Species" was the wrong word for most of what the table held. Twenty
        # rows covered five incompatible kinds of fact: peoples (Human, Dwarf,
        # Welkin), animals (Dog, Horse, Parrot), orders of being (Dragon,
        # Herald, Aesir, Ancient, Embra), an acquired condition (Zombie, which
        # stacks — Scooba is a Zombie and a Dog) and one manufactured being
        # (Robot). "Race" would have been worse: it fits the animals and the
        # tiers no better and buys no precision anywhere. "Kind" is true of all
        # of them, and matches `groups.kind` already in the schema.
        #
        # npc_epithets comes along because it was the last table still carrying
        # the retired NPC vocabulary, and because the Teklovossen merge just
        # before this put its first row on a hero. Heroes have epithets and
        # kinds; the foreign keys never said otherwise.
        #
        # Blocks 10 and 11 still create these under their original names,
        # because that is what they did and an old database migrating forward
        # needs the shape it actually had. So a from-scratch build arrives here
        # with BOTH sets: the new names from _V1_DDL and the old ones re-made
        # empty by 10 and 11. Renaming onto an existing table fails, so where
        # both exist the legacy table is folded in and dropped. Migration 4's
        # crash was this same from-scratch/legacy split.
        # The legacy tables blocks 10 and 11 create still carry
        # `REFERENCES npcs(...)`, and migration 12 renamed `npcs` away. SQLite
        # refuses to DROP a table whose foreign-key parent is missing, so
        # enforcement goes off for the fold and back on after. The pragma is a
        # no-op inside a transaction, hence the commit either side.
        conn.commit()
        conn.execute("PRAGMA foreign_keys = OFF")

        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for old_name, new_name in (
            ("npc_epithets", "character_epithets"),
            ("species", "kinds"),
            ("npc_species", "character_kinds"),
            ("species_aliases", "kind_aliases"),
        ):
            if old_name not in tables:
                continue
            if new_name in tables:
                if conn.execute(f"SELECT COUNT(*) FROM {old_name}").fetchone()[0]:
                    cols = ", ".join(r[1] for r in conn.execute(f"PRAGMA table_info({old_name})"))
                    conn.execute(f"INSERT OR IGNORE INTO {new_name} SELECT {cols} FROM {old_name}")
                conn.execute(f"DROP TABLE {old_name}")
            else:
                conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")

        # The id prefix stays `SP`: it is part of every stored kind_id, so
        # renaming it would move every id and every foreign key with it.
        for table in ("kinds", "character_kinds", "kind_aliases"):
            if "species_id" in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}:
                conn.execute(f"ALTER TABLE {table} RENAME COLUMN species_id TO kind_id")

        conn.execute("PRAGMA user_version = 19")
        conn.commit()
