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
        _seed_kinds(conn, data_dir)
        _seed_characters(conn, data_dir)
        _seed_character_kinds(conn, data_dir)
        _seed_monsters(conn, data_dir)
        _seed_fauna(conn, data_dir)
        _seed_flora(conn, data_dir)
        _seed_food_drink(conn, data_dir)
        _seed_heroes_canonical(conn, data_dir)
        _seed_character_heroes(conn, data_dir)
        _self_heal_character_heroes(conn)
        _seed_heroes_game(conn, data_dir)
        _seed_heroes_printings(conn, data_dir)
        _seed_heroes_ll(conn, data_dir)
        _seed_weapons_canonical(conn, data_dir)
        _seed_weapons_game(conn, data_dir)
        _seed_weapons_printings(conn, data_dir)
        _seed_equipment_canonical(conn, data_dir)
        _seed_equipment_game(conn, data_dir)
        _seed_equipment_printings(conn, data_dir)
        _seed_groups(conn, data_dir)
        _seed_group_members(conn, data_dir)
        _seed_alternate_names(conn, data_dir)
        _seed_titles(conn, data_dir)
        _seed_title_holders(conn, data_dir)
        _seed_character_kin(conn, data_dir)
        _seed_professions(conn, data_dir)
        _seed_character_professions(conn, data_dir)
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
        q.upsert_talent(conn, talent_id=_s(row, "TalentId"), talent_name=_s(row, "TalentName"))


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


def _seed_heroes_ll(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "heroes-ll.csv")
    for row in rows:
        q.upsert_hero_ll(
            conn,
            canonical_slug=_s(row, "CanonicalSlug"),
            card_name=_s(row, "CardName"),
            format=_s(row, "Format"),
            date_in_effect=_s(row, "DateInEffect"),
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
            image_url=_s(row, "ImageURL"),
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
            image_url=_s(row, "ImageURL"),
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
    """Seed locations, then wire parents in a second pass.

    ``parent_location_id`` points at another row in this same table and the CSV
    is ordered by name, so a child is routinely read before its parent. Foreign
    keys are enforced, so setting it inline would fail on that ordering. Every
    row is inserted first and parents are applied afterwards.
    """
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
    for row in rows:
        q.set_parent(
            conn,
            "locations",
            "location_id",
            "parent_location_id",
            _s(row, "LocationId"),
            _s(row, "ParentLocationId"),
        )


def _seed_groups(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed groups, then wire parents — same two-pass reason as locations."""
    _, rows = _csv(data_dir, "groups.csv")
    for row in rows:
        q.upsert_group(
            conn,
            group_id=_s(row, "GroupId"),
            name=_s(row, "Name"),
            kind=_s(row, "Kind"),
            notes=_s(row, "Notes"),
            location_id=_s(row, "LocationId"),
            lore_story_key=_s(row, "LoreStoryKey"),
            lore_fragment=_s(row, "LoreFragment"),
        )
    for row in rows:
        q.set_parent(
            conn,
            "groups",
            "group_id",
            "parent_group_id",
            _s(row, "GroupId"),
            _s(row, "ParentGroupId"),
        )


def _seed_group_members(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed the membership table (R1).

    Kept separate from the story junctions because membership is not a story
    link: it hangs off the group, and its ``story_key`` is evidence (D2), not
    the owner of the row. One table since migration 18 — a hero member and an
    entry-named member are both a ``character_id``.
    """
    _, rows = _csv(data_dir, "group-characters.csv")
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO group_characters (group_id, character_id, story_key) VALUES (?,?,?)",
            (_s(row, "GroupId"), _s(row, "CharacterId"), _s(row, "StoryKey")),
        )


def _seed_alternate_names(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed the three alternate-name tables (R4, R6).

    Kept out of the story junctions for the same reason as membership: these hang
    off the entity, not the page. ``sort_order`` is the file order, so the CSV is
    the record of display order and nothing has to store it twice.
    """
    for filename, table, cols in (
        (
            "character-epithets.csv",
            "character_epithets",
            (("CharacterId", "character_id"), ("Name", "name"), ("Kind", "kind")),
        ),
        (
            "location-aliases.csv",
            "location_aliases",
            (("LocationId", "location_id"), ("Alias", "alias"), ("Era", "era")),
        ),
        ("group-aliases.csv", "group_aliases", (("GroupId", "group_id"), ("Alias", "alias"))),
    ):
        _, rows = _csv(data_dir, filename)
        db_cols = [c for _, c in cols]
        placeholders = ",".join("?" * (len(db_cols) + 1))
        for order, row in enumerate(rows):
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({', '.join(db_cols)}, sort_order) VALUES ({placeholders})",
                (*(_s(row, header) for header, _ in cols), order),
            )


def _seed_characters(conn: sqlite3.Connection, data_dir: Path) -> None:
    _, rows = _csv(data_dir, "characters.csv")
    for row in rows:
        q.upsert_character(
            conn,
            character_id=_s(row, "CharacterId"),
            name=_s(row, "Name"),
            status=_s(row, "Status") or "Unknown",
            other_characters_story_key=_s(row, "OtherCharactersStoryKey"),
        )
        # summary is not an upsert_character parameter: that function is the story
        # registration path, and a registration must never touch lore text.
        summary = _s(row, "Summary")
        if summary:
            q.update_character_summary(conn, _s(row, "CharacterId"), summary)


def _seed_character_heroes(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed the character_heroes junction — the identity spine (migration 12).

    Followed by :func:`_self_heal_character_heroes`, which mints a character
    row for any hero this CSV does not yet cover, so a hero added later by
    ``create_heroes_csv.py`` can never end up without an identity.
    """
    _, rows = _csv(data_dir, "character-heroes.csv")
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO character_heroes (canonical_id, character_id) VALUES (?,?)",
            (_s(row, "CanonicalId"), _s(row, "CharacterId")),
        )


def _self_heal_character_heroes(conn: sqlite3.Connection) -> None:
    """Mint and link a character row for every hero not yet in character_heroes.

    Runs after both ``heroes_canonical`` and ``characters`` are seeded. An
    existing ``character_heroes`` row always wins — this only fills gaps, it
    never overwrites an explicit resolution (such as ``CharacterEntry(hero_slug=...)``
    or a hand-curated CSV row), the same ``INSERT OR IGNORE`` contract every
    other seed step in this module uses.
    """
    from registry_ids import lore_character_id

    linked = {r[0] for r in conn.execute("SELECT canonical_id FROM character_heroes")}
    for row in conn.execute("SELECT canonical_id, canonical_hero FROM heroes_canonical"):
        canonical_id, hero_name = row["canonical_id"], row["canonical_hero"]
        if canonical_id in linked or not hero_name:
            continue
        character_id = lore_character_id(hero_name)
        conn.execute(
            "INSERT OR IGNORE INTO characters (character_id, name, status) VALUES (?,?,'Unknown')",
            (character_id, hero_name),
        )
        conn.execute(
            "INSERT OR IGNORE INTO character_heroes (canonical_id, character_id) VALUES (?,?)",
            (canonical_id, character_id),
        )


def _seed_kinds(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed ``species`` and its aliases (R2, R6).

    Before ``_seed_characters``, because ``character_kinds`` references both registries and
    FK enforcement is on.
    """
    _, rows = _csv(data_dir, "kinds.csv")
    for row in rows:
        q.upsert_kind(
            conn,
            kind_id=_s(row, "KindId"),
            name=_s(row, "Name"),
            notes=_s(row, "Notes"),
        )
    _, alias_rows = _csv(data_dir, "kind-aliases.csv")
    for order, row in enumerate(alias_rows):
        conn.execute(
            "INSERT OR IGNORE INTO kind_aliases (kind_id, alias, sort_order) VALUES (?,?,?)",
            (_s(row, "KindId"), _s(row, "Alias"), order),
        )


def _seed_character_kinds(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed the ``character_kinds`` junction. ``sort_order`` is file order."""
    _, rows = _csv(data_dir, "character-kinds.csv")
    for order, row in enumerate(rows):
        conn.execute(
            "INSERT OR IGNORE INTO character_kinds (character_id, kind_id, sort_order) VALUES (?,?,?)",
            (_s(row, "CharacterId"), _s(row, "KindId"), order),
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


def _seed_titles(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed ``titles`` (R3). Before ``_seed_title_holders``, which references it."""
    _, rows = _csv(data_dir, "titles.csv")
    for row in rows:
        q.upsert_title(
            conn,
            title_id=_s(row, "TitleId"),
            name=_s(row, "Name"),
            group_id=_s(row, "GroupId"),
            notes=_s(row, "Notes"),
        )


def _seed_title_holders(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed ``title_holders``. Kept separate from the story junctions for the same
    reason ``group_characters`` is: this hangs off the title, not a
    page, and its ``StoryKey`` is evidence for the holder, not the link itself."""
    _, rows = _csv(data_dir, "title-holders.csv")
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO title_holders (title_id, character_id, ordinal, story_key) VALUES (?,?,?,?)",
            (
                _s(row, "TitleId"),
                _s(row, "CharacterId"),
                int(_s(row, "Ordinal") or 0),
                _s(row, "StoryKey"),
            ),
        )


# ---------------------------------------------------------------------------
# Stories + narrated videos
# ---------------------------------------------------------------------------


def _seed_character_kin(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed ``character_kin`` (R8). Kept separate from the story junctions for
    the same reason ``group_characters``/``title_holders`` are: this hangs off the
    character, not a page, and its ``StoryKey`` is evidence for the kin fact,
    not the link itself."""
    _, rows = _csv(data_dir, "character-kin.csv")
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO character_kin (character_id, relative_id, relation, story_key) VALUES (?,?,?,?)",
            (_s(row, "CharacterId"), _s(row, "RelativeId"), _s(row, "Relation"), _s(row, "StoryKey")),
        )


def _seed_professions(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed ``professions`` (R9). Before ``_seed_character_professions``, which
    references it, and placed alongside ``_seed_titles``/``_seed_character_kin``
    rather than beside ``_seed_kinds`` — ``character_professions`` can name a
    hero-only self-healed character row (``_upsert_hero_professions``), the same
    hazard ``title_holders`` and ``character_kin`` have and ``character_kinds``
    does not, so it seeds after ``_self_heal_character_heroes`` runs."""
    _, rows = _csv(data_dir, "professions.csv")
    for row in rows:
        q.upsert_profession(
            conn,
            profession_id=_s(row, "ProfessionId"),
            name=_s(row, "Name"),
            notes=_s(row, "Notes"),
        )


def _seed_character_professions(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Seed the ``character_professions`` junction. Unlike ``character-kinds.csv``,
    ``SortOrder`` is an explicit column rather than file order, so a re-export
    that reorders unrelated rows cannot silently reorder someone's professions."""
    _, rows = _csv(data_dir, "character-professions.csv")
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO character_professions (character_id, profession_id, sort_order) VALUES (?,?,?)",
            (_s(row, "CharacterId"), _s(row, "ProfessionId"), int(_s(row, "SortOrder") or 0)),
        )


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
                        (str(v.get("author", "")), str(v.get("url", "")), "")
                        for v in parsed
                        if isinstance(v, dict) and v.get("author") and v.get("url")
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
        grouped.setdefault(sid, []).append((author, link, channel))
    for sid, videos in grouped.items():
        q.set_narrated_videos(conn, sid, videos)


# ---------------------------------------------------------------------------
# Story junction tables
# ---------------------------------------------------------------------------

_JUNCTION_SPECS: tuple[tuple[str, str, str, str], ...] = (
    ("story-locations.csv", "story_locations", "LocationId", "location_id"),
    ("story-regions.csv", "story_regions", "RegionId", "region_id"),
    ("story-monsters.csv", "story_monsters", "MonsterId", "monster_id"),
    ("story-fauna.csv", "story_fauna", "FaunaId", "fauna_id"),
    ("story-flora.csv", "story_flora", "FloraId", "flora_id"),
    ("story-food-drink.csv", "story_food_drink", "FoodDrinkId", "food_drink_id"),
    (
        "story-weapons.csv",
        "story_weapons",
        "CanonicalWeaponId",
        "canonical_weapon_id",
    ),
    (
        "story-equipment.csv",
        "story_equipment",
        "CanonicalEquipmentId",
        "canonical_equipment_id",
    ),
    ("story-groups.csv", "story_groups", "GroupId", "group_id"),
    ("story-titles.csv", "story_titles", "TitleId", "title_id"),
)


def _seed_story_junctions(conn: sqlite3.Connection, data_dir: Path) -> None:
    # story_characters carries an extra Fragment column, unlike the plain
    # (story_id, entity_id) junctions in _JUNCTION_SPECS below.
    _, rows = _csv(data_dir, "story-characters.csv")
    triples = [
        (_s(row, "StoryId"), _s(row, "CharacterId"), _s(row, "Fragment"))
        for row in rows
        if _s(row, "StoryId") and _s(row, "CharacterId")
    ]
    if triples:
        conn.executemany(
            "INSERT OR IGNORE INTO story_characters (story_id, character_id, fragment) VALUES (?,?,?)",
            triples,
        )

    for csv_name, table, csv_col, db_col in _JUNCTION_SPECS:
        _, rows = _csv(data_dir, csv_name)
        pairs = [(_s(row, "StoryId"), _s(row, csv_col)) for row in rows if _s(row, "StoryId") and _s(row, csv_col)]
        if pairs:
            conn.executemany(
                f"INSERT OR IGNORE INTO {table} (story_id, {db_col}) VALUES (?,?)",
                pairs,
            )
