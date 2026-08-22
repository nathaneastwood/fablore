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
    return conn.execute("SELECT * FROM stories WHERE story_key = ?", [story_key]).fetchone()


def select_story_by_id(conn: sqlite3.Connection, story_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM stories WHERE story_id = ?", [story_id]).fetchone()


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
            "INSERT INTO narrated_videos " "(story_id, author, source_link, channel_link) " "VALUES (?,?,?,?)",
            [(story_id, author, url, channel) for author, url, channel in videos],
        )


def select_narrated_videos(conn: sqlite3.Connection, story_id: str) -> list[sqlite3.Row]:
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
    return conn.execute("SELECT * FROM regions WHERE region_id = ?", [region_id]).fetchone()


def select_all_regions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM regions ORDER BY region_name").fetchall()


def region_id_exists(conn: sqlite3.Connection, region_id: str) -> bool:
    return conn.execute("SELECT 1 FROM regions WHERE region_id = ?", [region_id]).fetchone() is not None


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
    parent_location_id: str = "",
) -> None:
    if not notes:
        row = conn.execute("SELECT notes FROM locations WHERE location_id = ?", [location_id]).fetchone()
        if row and row[0]:
            _log.warning(
                "Skipping notes overwrite for location %r — existing notes preserved"
                " (pass non-empty notes to update them)",
                location_id,
            )
    conn.execute(
        """
        INSERT INTO locations
            (location_id, name, region_id, notes, lore_fragment, parent_location_id)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(location_id) DO UPDATE SET
            name               = excluded.name,
            region_id          = excluded.region_id,
            notes              = CASE WHEN excluded.notes != ''
                                 THEN excluded.notes
                                 ELSE locations.notes END,
            lore_fragment      = CASE WHEN excluded.lore_fragment != ''
                                 THEN excluded.lore_fragment
                                 ELSE locations.lore_fragment END,
            parent_location_id = CASE WHEN excluded.parent_location_id != ''
                                 THEN excluded.parent_location_id
                                 ELSE locations.parent_location_id END
        """,
        (location_id, name, region_id, notes, lore_fragment, parent_location_id),
    )


def select_all_locations(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM locations ORDER BY name").fetchall()


def set_parent(
    conn: sqlite3.Connection, table: str, id_col: str, parent_col: str, entity_id: str, parent_id: str
) -> None:
    """Set a self-referencing parent column after every row exists.

    Seeding cannot set these inline: the CSV is ordered by name, so a child is
    routinely read before its parent, and foreign keys are enforced. Both
    seeders therefore insert every row first and set parents in a second pass.
    """
    if not parent_id:
        return
    conn.execute(f"UPDATE {table} SET {parent_col} = ? WHERE {id_col} = ?", (parent_id, entity_id))


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


def upsert_group(
    conn: sqlite3.Connection,
    *,
    group_id: str,
    name: str,
    kind: str = "",
    notes: str = "",
    parent_group_id: str = "",
    location_id: str = "",
    lore_story_key: str = "",
    lore_fragment: str = "",
) -> None:
    """Insert or update a group, preserving curated fields the caller omits.

    ``notes`` follows the same rule as location notes and monster descriptions:
    an empty value never clears a curated one, because ``descriptions.py`` is the
    only writer that should be setting it.
    """
    if not notes:
        row = conn.execute("SELECT notes FROM groups WHERE group_id = ?", [group_id]).fetchone()
        if row and row[0]:
            _log.warning(
                "Skipping notes overwrite for group %r — existing notes preserved"
                " (pass non-empty notes to update them)",
                group_id,
            )
    conn.execute(
        """
        INSERT INTO groups
            (group_id, name, kind, notes, parent_group_id, location_id,
             lore_story_key, lore_fragment)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(group_id) DO UPDATE SET
            name            = excluded.name,
            kind            = CASE WHEN excluded.kind != ''
                              THEN excluded.kind
                              ELSE groups.kind END,
            notes           = CASE WHEN excluded.notes != ''
                              THEN excluded.notes
                              ELSE groups.notes END,
            parent_group_id = CASE WHEN excluded.parent_group_id != ''
                              THEN excluded.parent_group_id
                              ELSE groups.parent_group_id END,
            location_id     = CASE WHEN excluded.location_id != ''
                              THEN excluded.location_id
                              ELSE groups.location_id END,
            lore_story_key  = CASE WHEN excluded.lore_story_key != ''
                              THEN excluded.lore_story_key
                              ELSE groups.lore_story_key END,
            lore_fragment   = CASE WHEN excluded.lore_fragment != ''
                              THEN excluded.lore_fragment
                              ELSE groups.lore_fragment END
        """,
        (group_id, name, kind, notes, parent_group_id, location_id, lore_story_key, lore_fragment),
    )


def select_all_groups(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM groups ORDER BY name").fetchall()


def update_group_notes(conn: sqlite3.Connection, group_id: str, notes: str) -> int:
    """Update the notes (tooltip summary) for a single group. Returns rows affected.

    Groups keep their summary in ``notes``, the same column name locations use,
    rather than the ``description`` column monsters/fauna/flora use — which is why
    this cannot go through :func:`update_entity_description`.
    """
    cur = conn.execute("UPDATE groups SET notes = ? WHERE group_id = ?", (notes, group_id))
    return cur.rowcount


def set_group_members(
    conn: sqlite3.Connection,
    group_id: str,
    table: str,
    id_col: str,
    members: list[tuple[str, str]],
) -> None:
    """Replace all membership rows for ``group_id`` with ``members``.

    Args:
        members: ``(entity_id, story_key)`` pairs. ``story_key`` is the optional
            evidence citation (D2) and may be empty.
    """
    conn.execute(f"DELETE FROM {table} WHERE group_id = ?", [group_id])
    if members:
        conn.executemany(
            f"INSERT OR IGNORE INTO {table} (group_id, {id_col}, story_key) VALUES (?,?,?)",
            [(group_id, eid, key) for eid, key in members],
        )


def select_group_members(conn: sqlite3.Connection, group_id: str, table: str, id_col: str) -> list[tuple[str, str]]:
    """Return ``(entity_id, story_key)`` membership rows for ``group_id``, sorted."""
    rows = conn.execute(
        f"SELECT {id_col}, story_key FROM {table} WHERE group_id = ? ORDER BY {id_col}",
        [group_id],
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


# ---------------------------------------------------------------------------
# Titles (R3)
# ---------------------------------------------------------------------------


def upsert_title(
    conn: sqlite3.Connection,
    *,
    title_id: str,
    name: str,
    group_id: str = "",
    notes: str = "",
) -> None:
    """Insert or update a title, preserving curated fields the caller omits.

    ``group_id`` follows the same preserve-on-empty rule as
    ``groups.parent_group_id``: an empty incoming value never clears a stored
    link. ``notes`` follows the same rule as group notes — ``descriptions.py``
    is the only writer that should be setting it.
    """
    if not notes:
        row = conn.execute("SELECT notes FROM titles WHERE title_id = ?", [title_id]).fetchone()
        if row and row[0]:
            _log.warning(
                "Skipping notes overwrite for title %r — existing notes preserved"
                " (pass non-empty notes to update them)",
                title_id,
            )
    conn.execute(
        """
        INSERT INTO titles (title_id, name, group_id, notes)
        VALUES (?,?,?,?)
        ON CONFLICT(title_id) DO UPDATE SET
            name     = excluded.name,
            group_id = CASE WHEN excluded.group_id != ''
                       THEN excluded.group_id
                       ELSE titles.group_id END,
            notes    = CASE WHEN excluded.notes != ''
                       THEN excluded.notes
                       ELSE titles.notes END
        """,
        (title_id, name, group_id, notes),
    )


def select_all_titles(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM titles ORDER BY name").fetchall()


def update_title_notes(conn: sqlite3.Connection, title_id: str, notes: str) -> int:
    """Update the notes (tooltip summary) for a single title. Returns rows affected."""
    cur = conn.execute("UPDATE titles SET notes = ? WHERE title_id = ?", (notes, title_id))
    return cur.rowcount


def set_title_holders(
    conn: sqlite3.Connection,
    title_id: str,
    holders: list[tuple[str, int, str]],
) -> None:
    """Replace all holder rows for ``title_id`` with ``(character_id, ordinal, story_key)`` triples."""
    conn.execute("DELETE FROM title_holders WHERE title_id = ?", [title_id])
    if holders:
        conn.executemany(
            "INSERT OR IGNORE INTO title_holders (title_id, character_id, ordinal, story_key) VALUES (?,?,?,?)",
            [(title_id, cid, ordinal, story_key) for cid, ordinal, story_key in holders],
        )


def select_title_holders(conn: sqlite3.Connection, title_id: str) -> list[tuple[str, int, str]]:
    """Return ``(character_id, ordinal, story_key)`` holder rows for ``title_id``, sorted."""
    rows = conn.execute(
        "SELECT character_id, ordinal, story_key FROM title_holders WHERE title_id = ? ORDER BY ordinal, character_id",
        [title_id],
    ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


# ---------------------------------------------------------------------------
# Kinship (R8)
# ---------------------------------------------------------------------------

KIN_INVERSE = {
    "father": "child",
    "mother": "child",
    "parent": "child",
    "child": "parent",
    "sibling": "sibling",
    "spouse": "spouse",
}
"""How a stored relation reads from the *other* end.

``character_kin`` stores one row per stated fact — "Lyath's father is
Bloodworth" — and never the inverse. A fact stored twice could disagree with
itself and nothing would say which half was right, so the second half is
derived here instead, at read time. ``father``/``mother``/``parent`` all
invert to ``child``; ``child`` inverts to ``parent`` rather than a gender,
because a row that only says "parent" does not know which one. ``sibling``
and ``spouse`` invert to themselves.
"""


def set_character_kin(conn: sqlite3.Connection, character_id: str, kin: list[tuple[str, str, str]]) -> None:
    """Replace every kin row stated *by* ``character_id``.

    Args:
        kin: ``(relative_id, relation, story_key)`` triples. Replace-semantic,
            like the group rosters and ``npc_species``: this is the complete
            set of kin facts this declaration states, so an omitted fact is a
            deletion, not a preserved value.
    """
    conn.execute("DELETE FROM character_kin WHERE character_id = ?", [character_id])
    if kin:
        conn.executemany(
            "INSERT OR IGNORE INTO character_kin (character_id, relative_id, relation, story_key) VALUES (?,?,?,?)",
            [(character_id, rid, relation, story_key) for rid, relation, story_key in kin],
        )


def select_character_kin(conn: sqlite3.Connection, character_id: str) -> list[tuple[str, str, str]]:
    """Return ``(relative_id, relation, story_key)`` rows stated *by* ``character_id``, sorted.

    Only the stored direction — the same half :func:`set_character_kin` writes.
    Use :func:`select_character_kin_both_directions` to also see facts stated
    *about* this character by someone else.
    """
    rows = conn.execute(
        "SELECT relative_id, relation, story_key FROM character_kin WHERE character_id = ? ORDER BY relative_id, relation",
        [character_id],
    ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


def select_character_kin_both_directions(conn: sqlite3.Connection, character_id: str) -> list[tuple[str, str, str]]:
    """Return this character's kin in both directions, relation as seen from ``character_id``.

    ``character_kin`` stores one row per stated fact and never its inverse (see
    :data:`KIN_INVERSE`), so "who are Bloodworth's children" has no row to
    select directly. This derives it: rows ``character_id`` stated directly,
    plus rows stated *about* ``character_id`` by someone else, inverted through
    :data:`KIN_INVERSE` so every relation reads correctly from this character's
    own perspective.

    Returns:
        ``(relative_id, relation, story_key)`` triples, unsorted union of both halves.
    """
    direct = conn.execute(
        "SELECT relative_id, relation, story_key FROM character_kin WHERE character_id = ? ORDER BY relative_id, relation",
        [character_id],
    ).fetchall()
    inverse = conn.execute(
        "SELECT character_id, relation, story_key FROM character_kin WHERE relative_id = ? ORDER BY character_id, relation",
        [character_id],
    ).fetchall()
    result = [(r[0], r[1], r[2]) for r in direct]
    result.extend((r[0], KIN_INVERSE[r[1]], r[2]) for r in inverse)
    return result


# ---------------------------------------------------------------------------
# Alternate names (R4 epithets, R6 aliases)
# ---------------------------------------------------------------------------
#
# One shape, three tables. Each owns a different registry, so the id column and
# the extra columns differ, but all three are replace-semantic on their owner —
# the same rule membership follows, for the same reason: a declaration states the
# complete set, so a name dropped from it is a name the lore no longer supports.


def set_npc_epithets(conn: sqlite3.Connection, character_id: str, entries: list[tuple[str, str]]) -> None:
    """Replace every alternate name for ``character_id``.

    Args:
        entries: ``(name, kind)`` pairs in display order. ``kind`` is ``'epithet'``
            or ``'short-name'``; ``sort_order`` follows the list order.
    """
    conn.execute("DELETE FROM npc_epithets WHERE character_id = ?", [character_id])
    if entries:
        conn.executemany(
            "INSERT OR IGNORE INTO npc_epithets (character_id, name, kind, sort_order) VALUES (?,?,?,?)",
            [(character_id, name, kind, i) for i, (name, kind) in enumerate(entries)],
        )


def select_npc_epithets(conn: sqlite3.Connection, character_id: str) -> list[tuple[str, str]]:
    """Return ``(name, kind)`` rows for ``character_id`` in declared order."""
    rows = conn.execute(
        "SELECT name, kind FROM npc_epithets WHERE character_id = ? ORDER BY sort_order, name",
        [character_id],
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def set_location_aliases(conn: sqlite3.Connection, location_id: str, entries: list[tuple[str, str]]) -> None:
    """Replace every alias for ``location_id``.

    Args:
        entries: ``(alias, era)`` pairs in display order. ``era`` may be empty
            where the lore does not date the name.
    """
    conn.execute("DELETE FROM location_aliases WHERE location_id = ?", [location_id])
    if entries:
        conn.executemany(
            "INSERT OR IGNORE INTO location_aliases (location_id, alias, era, sort_order) VALUES (?,?,?,?)",
            [(location_id, alias, era, i) for i, (alias, era) in enumerate(entries)],
        )


def select_location_aliases(conn: sqlite3.Connection, location_id: str) -> list[tuple[str, str]]:
    """Return ``(alias, era)`` rows for ``location_id`` in declared order."""
    rows = conn.execute(
        "SELECT alias, era FROM location_aliases WHERE location_id = ? ORDER BY sort_order, alias",
        [location_id],
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def set_group_aliases(conn: sqlite3.Connection, group_id: str, aliases: list[str]) -> None:
    """Replace every alias for ``group_id``, in the order given."""
    conn.execute("DELETE FROM group_aliases WHERE group_id = ?", [group_id])
    if aliases:
        conn.executemany(
            "INSERT OR IGNORE INTO group_aliases (group_id, alias, sort_order) VALUES (?,?,?)",
            [(group_id, alias, i) for i, alias in enumerate(aliases)],
        )


def select_group_aliases(conn: sqlite3.Connection, group_id: str) -> list[str]:
    """Return the aliases for ``group_id`` in declared order."""
    rows = conn.execute(
        "SELECT alias FROM group_aliases WHERE group_id = ? ORDER BY sort_order, alias",
        [group_id],
    ).fetchall()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Species (R2)
# ---------------------------------------------------------------------------
#
# Three functions for what used to be one column. ``species`` is a registry like
# any other; ``npc_species`` is a junction, replace-semantic on the character the
# way a roster is on its group; ``species_aliases`` is the fourth alias table and
# behaves exactly like the other three.


def upsert_species(conn: sqlite3.Connection, *, species_id: str, name: str, notes: str = "") -> None:
    """Insert or update a species row, preserving ``notes`` the caller omits.

    ``notes`` follows the preserve-on-empty contract the other registries use:
    a declaration names a species, ``descriptions.py`` writes what it is.
    """
    conn.execute(
        """
        INSERT INTO species (species_id, name, notes)
        VALUES (?,?,?)
        ON CONFLICT(species_id) DO UPDATE SET
            name  = excluded.name,
            notes = CASE WHEN excluded.notes != '' THEN excluded.notes ELSE species.notes END
        """,
        (species_id, name, notes),
    )


def select_all_species(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM species ORDER BY name").fetchall()


def update_species_notes(conn: sqlite3.Connection, species_id: str, notes: str) -> int:
    cur = conn.execute("UPDATE species SET notes = ? WHERE species_id = ?", [notes, species_id])
    return cur.rowcount


def set_npc_species(conn: sqlite3.Connection, character_id: str, species_ids: list[str]) -> None:
    """Replace every species linked to ``character_id``, in the order given."""
    conn.execute("DELETE FROM npc_species WHERE character_id = ?", [character_id])
    if species_ids:
        conn.executemany(
            "INSERT OR IGNORE INTO npc_species (character_id, species_id, sort_order) VALUES (?,?,?)",
            [(character_id, sid, i) for i, sid in enumerate(species_ids)],
        )


def select_npc_species(conn: sqlite3.Connection, character_id: str) -> list[str]:
    """Return the species ids linked to ``character_id`` in declared order."""
    rows = conn.execute(
        "SELECT species_id FROM npc_species WHERE character_id = ? ORDER BY sort_order, species_id",
        [character_id],
    ).fetchall()
    return [r[0] for r in rows]


def set_species_aliases(conn: sqlite3.Connection, species_id: str, aliases: list[str]) -> None:
    """Replace every alias for ``species_id``, in the order given."""
    conn.execute("DELETE FROM species_aliases WHERE species_id = ?", [species_id])
    if aliases:
        conn.executemany(
            "INSERT OR IGNORE INTO species_aliases (species_id, alias, sort_order) VALUES (?,?,?)",
            [(species_id, alias, i) for i, alias in enumerate(aliases)],
        )


def select_species_aliases(conn: sqlite3.Connection, species_id: str) -> list[str]:
    """Return the aliases for ``species_id`` in declared order."""
    rows = conn.execute(
        "SELECT alias FROM species_aliases WHERE species_id = ? ORDER BY sort_order, alias",
        [species_id],
    ).fetchall()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Professions (R9)
# ---------------------------------------------------------------------------
#
# A trade many hold independently, not a roster: "who is a Braumeister" is
# unbounded and unsourceable, which is exactly what a group's member_source
# exists to prevent, so there is no source column here and no alias table —
# unlike species, no plural or supplement entry has needed one yet.


def upsert_profession(conn: sqlite3.Connection, *, profession_id: str, name: str, notes: str = "") -> None:
    """Insert or update a profession row, preserving ``notes`` the caller omits.

    ``notes`` follows the preserve-on-empty contract the other registries use:
    a declaration names a profession, ``descriptions.py`` writes what it is.
    """
    conn.execute(
        """
        INSERT INTO professions (profession_id, name, notes)
        VALUES (?,?,?)
        ON CONFLICT(profession_id) DO UPDATE SET
            name  = excluded.name,
            notes = CASE WHEN excluded.notes != '' THEN excluded.notes ELSE professions.notes END
        """,
        (profession_id, name, notes),
    )


def select_all_professions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM professions ORDER BY name").fetchall()


def update_profession_notes(conn: sqlite3.Connection, profession_id: str, notes: str) -> int:
    cur = conn.execute("UPDATE professions SET notes = ? WHERE profession_id = ?", [notes, profession_id])
    return cur.rowcount


def set_character_professions(conn: sqlite3.Connection, character_id: str, profession_ids: list[str]) -> None:
    """Replace every profession linked to ``character_id``, in the order given."""
    conn.execute("DELETE FROM character_professions WHERE character_id = ?", [character_id])
    if profession_ids:
        conn.executemany(
            "INSERT OR IGNORE INTO character_professions (character_id, profession_id, sort_order) VALUES (?,?,?)",
            [(character_id, pid, i) for i, pid in enumerate(profession_ids)],
        )


def select_character_professions(conn: sqlite3.Connection, character_id: str) -> list[str]:
    """Return the profession ids linked to ``character_id`` in declared order."""
    rows = conn.execute(
        "SELECT profession_id FROM character_professions WHERE character_id = ? ORDER BY sort_order, profession_id",
        [character_id],
    ).fetchall()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# NPCs
# ---------------------------------------------------------------------------


def upsert_npc(
    conn: sqlite3.Connection,
    *,
    character_id: str,
    name: str,
    status: str = "",
    other_characters_story_key: str = "",
) -> None:
    """Insert or update an NPC, preserving curated fields the caller omits.

    ``status`` follows the same preserve-on-empty contract as
    :func:`upsert_location`'s ``notes``: an empty string means "leave whatever is
    already there", not "set it to Unknown". This matters because most callers are
    story registrations that know a character's name but not their curated lore
    status — passing a sentinel would silently replace values such as
    ``"Just a head"`` or ``"Assumed Dead"`` with ``"Unknown"``.

    A brand-new NPC still lands as ``"Unknown"`` for an omitted ``status``.

    Species does **not** live here any more and does not follow that contract.
    It is a junction (:func:`set_npc_species`), replace-semantic like the group
    rosters, because one column could not hold `Zombie` and `Dog` at once.
    """
    row = conn.execute(
        "SELECT status FROM characters WHERE character_id = ?",
        [character_id],
    ).fetchone()
    if row is None:
        # New row — an omitted field has nothing to preserve, so seed the sentinel.
        status = status or "Unknown"
    else:
        existing = row["status"]
        if not status and existing and existing != "Unknown":
            _log.warning(
                "Skipping status overwrite for npc %r — existing value %r preserved"
                " (pass a non-empty status to update it)",
                character_id,
                existing,
            )
    conn.execute(
        """
        INSERT INTO characters (character_id, name, status, other_characters_story_key)
        VALUES (?,?,?,?)
        ON CONFLICT(character_id) DO UPDATE SET
            name    = excluded.name,
            status  = CASE WHEN excluded.status != ''
                      THEN excluded.status
                      ELSE characters.status END,
            other_characters_story_key = CASE
                WHEN excluded.other_characters_story_key != ''
                    THEN excluded.other_characters_story_key
                ELSE characters.other_characters_story_key
            END
        """,
        (character_id, name, status, other_characters_story_key),
    )


def update_character_summary(conn: sqlite3.Connection, character_id: str, summary: str) -> int:
    """Set a character's tooltip summary. Returns the number of rows updated.

    Called only by ``descriptions.py`` through ``Database.update_description``,
    which owns every registry's lore text. ``entries/catalogue/`` deliberately
    has no way to reach this: two writers for one summary is the hazard the
    faction and species entries had to be migrated out of.
    """
    cur = conn.execute(
        "UPDATE characters SET summary = ? WHERE character_id = ?",
        [summary, character_id],
    )
    return cur.rowcount


def select_all_npcs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM characters ORDER BY name").fetchall()


# ---------------------------------------------------------------------------
# character_heroes — the identity spine (R... migration 12)
# ---------------------------------------------------------------------------


def set_character_hero(conn: sqlite3.Connection, canonical_id: str, character_id: str) -> None:
    """Insert or update the character_heroes row for ``canonical_id``.

    ``canonical_id`` is the primary key — a hero is exactly one person — so this
    upserts by hero, overwriting a stale ``character_id`` the way every other
    upsert in this module overwrites a stale scalar.
    """
    conn.execute(
        """
        INSERT INTO character_heroes (canonical_id, character_id)
        VALUES (?,?)
        ON CONFLICT(canonical_id) DO UPDATE SET
            character_id = excluded.character_id
        """,
        (canonical_id, character_id),
    )


def select_character_id_for_hero(conn: sqlite3.Connection, canonical_id: str) -> str | None:
    row = conn.execute(
        "SELECT character_id FROM character_heroes WHERE canonical_id = ?",
        [canonical_id],
    ).fetchone()
    return row[0] if row else None


def select_all_character_heroes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM character_heroes ORDER BY canonical_id").fetchall()


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
        row = conn.execute(f"SELECT description FROM {table} WHERE {id_col} = ?", [entity_id]).fetchone()
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


def upsert_monster(conn: sqlite3.Connection, *, monster_id: str, name: str, description: str = "") -> None:
    _upsert_named_entity(conn, "monsters", "monster_id", monster_id, name, description)


def upsert_fauna(conn: sqlite3.Connection, *, fauna_id: str, name: str, description: str = "") -> None:
    _upsert_named_entity(conn, "fauna", "fauna_id", fauna_id, name, description)


def upsert_flora(conn: sqlite3.Connection, *, flora_id: str, name: str, description: str = "") -> None:
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


def select_location_by_id(conn: sqlite3.Connection, location_id: str) -> sqlite3.Row | None:
    """Return a location row by id, or ``None``."""
    return conn.execute("SELECT * FROM locations WHERE location_id = ?", [location_id]).fetchone()


def select_location_ids_by_name(conn: sqlite3.Connection, name: str) -> list[str]:
    """Return every ``LocationId`` stored under ``name`` (may be >1 for duplicate rows)."""
    rows = conn.execute("SELECT location_id FROM locations WHERE name = ?", [name]).fetchall()
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


def upsert_food_drink(conn: sqlite3.Connection, *, food_drink_id: str, name: str, type_: str) -> None:
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


def upsert_talent(conn: sqlite3.Connection, *, talent_id: str, talent_name: str) -> None:
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
    return conn.execute("SELECT * FROM heroes_canonical WHERE canonical_slug = ?", [slug]).fetchone()


def select_all_heroes_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM heroes_canonical ORDER BY canonical_slug").fetchall()


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
    return conn.execute("SELECT * FROM heroes_printings ORDER BY hero_game_id, set_id, card_id").fetchall()


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
    return conn.execute("SELECT * FROM weapons_canonical WHERE canonical_slug = ?", [slug]).fetchone()


def select_all_weapons_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM weapons_canonical ORDER BY canonical_slug").fetchall()


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
    image_url: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO weapons_printings (weapon_game_id, set_id, card_id, rarity, image_url)
        VALUES (?,?,?,?,?)
        ON CONFLICT(weapon_game_id, set_id, card_id, image_url) DO UPDATE SET
            rarity = excluded.rarity
        """,
        (weapon_game_id, set_id, card_id, rarity, image_url),
    )


def select_all_weapons_printings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM weapons_printings ORDER BY weapon_game_id, set_id, card_id, image_url"
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
    return conn.execute("SELECT * FROM equipment_canonical WHERE canonical_slug = ?", [slug]).fetchone()


def select_all_equipment_canonical(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM equipment_canonical ORDER BY canonical_slug").fetchall()


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
    image_url: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO equipment_printings (equipment_game_id, set_id, card_id, rarity, image_url)
        VALUES (?,?,?,?,?)
        ON CONFLICT(equipment_game_id, set_id, card_id, image_url) DO UPDATE SET
            rarity = excluded.rarity
        """,
        (equipment_game_id, set_id, card_id, rarity, image_url),
    )


def select_all_equipment_printings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM equipment_printings ORDER BY equipment_game_id, set_id, card_id, image_url"
    ).fetchall()


# ---------------------------------------------------------------------------
# Story junction helpers
# ---------------------------------------------------------------------------


def select_story_hero_fragments(conn: sqlite3.Connection, story_id: str) -> dict[str, str]:
    """Return ``{canonical_id: fragment}`` for a story's hero links.

    Fragments live in the ``story_heroes`` junction rather than on a registry
    row, so :func:`select_story_junction` cannot see them. The dry-run preview
    needs them to report an anchor that a declaration is about to clear.
    """
    rows = conn.execute(
        "SELECT canonical_id, fragment FROM story_heroes WHERE story_id = ?",
        [story_id],
    ).fetchall()
    return {r["canonical_id"]: (r["fragment"] or "") for r in rows}


def set_story_heroes(
    conn: sqlite3.Connection,
    story_id: str,
    entries: list[tuple[str, str]],
) -> None:
    """Replace all story_heroes rows for ``story_id`` with ``(canonical_id, fragment)`` pairs."""
    conn.execute("DELETE FROM story_heroes WHERE story_id = ?", [story_id])
    if entries:
        conn.executemany(
            "INSERT OR IGNORE INTO story_heroes (story_id, canonical_id, fragment)" " VALUES (?,?,?)",
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
            "INSERT OR IGNORE INTO story_npcs (story_id, character_id, fragment)" " VALUES (?,?,?)",
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


def select_story_junction(conn: sqlite3.Connection, story_id: str, table: str, id_col: str) -> list[str]:
    """Return entity ids linked to ``story_id`` in ``table``, sorted."""
    rows = conn.execute(
        f"SELECT {id_col} FROM {table} WHERE story_id = ? ORDER BY {id_col}",
        [story_id],
    ).fetchall()
    return [r[0] for r in rows]


def delete_all_story_junctions(conn: sqlite3.Connection, story_id: str) -> dict[str, int]:
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
        ("story_groups", "group_id"),
    ]
    counts: dict[str, int] = {}
    for table, _ in junctions:
        cur = conn.execute(f"DELETE FROM {table} WHERE story_id = ?", [story_id])
        counts[table] = cur.rowcount
    return counts


def count_entity_story_links(conn: sqlite3.Connection, junction_table: str, id_column: str, entity_id: str) -> int:
    """Return how many story junction rows reference ``entity_id``.

    Used to guard :func:`delete_entity_row` against silently orphaning story
    links — callers should refuse to delete (or repoint links first) when
    this is non-zero.
    """
    return conn.execute(f"SELECT COUNT(*) FROM {junction_table} WHERE {id_column} = ?", [entity_id]).fetchone()[0]


def delete_entity_row(conn: sqlite3.Connection, table: str, id_column: str, entity_id: str) -> int:
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
        "story_groups",
    ]
    return {
        t: conn.execute(f"SELECT COUNT(*) FROM {t} WHERE story_id = ?", [story_id]).fetchone()[0] for t in junctions
    }
