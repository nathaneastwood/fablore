"""Tests for :meth:`Database.move_location_region`.

``LocationId`` hashes ``name|region_id``, so a location that changes region gets
a new id. Re-declaring it in the catalogue mints a second row with the same name
and strands the first, and ``delete_entity("location", name)`` cannot clean up:
it removes every row of that name, and refuses while any of them is linked. The
move does the whole migration in one place.
"""

from __future__ import annotations

import pytest

import db._queries as q
from db import Database, GroupEntry, LocationEntry
from registry_ids import location_id, region_row_id

ARENA = "Deathmatch Arena"
SAVAGE = "The Savage Lands"
OLD_ID = location_id(ARENA, region_row_id(SAVAGE))
NEW_ID = location_id(ARENA, "")


def _story(database: Database, path: str, **kw):
    return database.upsert_story(path=path, title=path, **kw)


def _linked_location_ids(database: Database, path: str) -> set[str]:
    story = database.get_story(path)
    assert story is not None
    rows = database.conn.execute(
        "SELECT location_id FROM story_locations WHERE story_id = ?", [story.story_id]
    ).fetchall()
    return {r[0] for r in rows}


def _seed_arena(database: Database) -> None:
    arena = LocationEntry(ARENA, region=SAVAGE, notes="Where heroes fight.", lore_fragment="the-boneyard")
    _story(database, "src/main-story/a.md", locations=[arena])
    _story(database, "src/main-story/b.md", locations=[arena])
    database.conn.execute(
        "INSERT INTO location_aliases (location_id, alias, era, sort_order) VALUES (?, 'The Pit', '', 0)",
        [OLD_ID],
    )


def test_move_rekeys_the_row_and_keeps_its_fields(db: Database) -> None:
    _seed_arena(db)

    db.move_location_region(ARENA, from_region=SAVAGE, to_region="")

    assert q.select_location_by_id(db.conn, OLD_ID) is None
    row = q.select_location_by_id(db.conn, NEW_ID)
    assert row is not None
    assert (row["name"], row["region_id"], row["notes"], row["lore_fragment"]) == (
        ARENA,
        "",
        "Where heroes fight.",
        "the-boneyard",
    )


def test_move_repoints_every_story_link(db: Database) -> None:
    _seed_arena(db)

    db.move_location_region(ARENA, from_region=SAVAGE, to_region="")

    assert _linked_location_ids(db, "src/main-story/a.md") == {NEW_ID}
    assert _linked_location_ids(db, "src/main-story/b.md") == {NEW_ID}


def test_move_carries_aliases_children_and_groups(db: Database) -> None:
    _seed_arena(db)
    db.conn.execute(
        "INSERT INTO locations (location_id, name, parent_location_id) VALUES ('LOchild', 'Undercroft', ?)",
        [OLD_ID],
    )
    _story(db, "src/main-story/c.md", groups=[GroupEntry("Arena Staff", category="guild")])
    db.conn.execute("UPDATE groups SET location_id = ? WHERE name = 'Arena Staff'", [OLD_ID])

    db.move_location_region(ARENA, from_region=SAVAGE, to_region="")

    aliases = db.conn.execute("SELECT location_id, alias FROM location_aliases").fetchall()
    assert [tuple(r) for r in aliases] == [(NEW_ID, "The Pit")]
    child = q.select_location_by_id(db.conn, "LOchild")
    assert child["parent_location_id"] == NEW_ID
    group = db.conn.execute("SELECT location_id FROM groups WHERE name = 'Arena Staff'").fetchone()
    assert group[0] == NEW_ID


def test_move_refuses_when_the_source_row_is_missing(db: Database) -> None:
    with pytest.raises(ValueError, match="not found"):
        db.move_location_region(ARENA, from_region=SAVAGE, to_region="")


def test_move_refuses_when_the_target_row_already_exists(db: Database) -> None:
    """Two rows to merge is a different job; the move must not silently pick one."""
    _seed_arena(db)
    _story(db, "src/main-story/d.md", locations=[LocationEntry(ARENA)])

    with pytest.raises(ValueError, match="already exists"):
        db.move_location_region(ARENA, from_region=SAVAGE, to_region="")
    assert q.select_location_by_id(db.conn, OLD_ID) is not None


def test_move_exports_the_changed_csvs(db: Database, tmp_path) -> None:
    _seed_arena(db)

    db.move_location_region(ARENA, from_region=SAVAGE, to_region="")

    locations_csv = (tmp_path / "csv" / "locations.csv").read_text(encoding="utf-8")
    story_locations_csv = (tmp_path / "csv" / "story-locations.csv").read_text(encoding="utf-8")
    assert NEW_ID in locations_csv and OLD_ID not in locations_csv
    assert NEW_ID in story_locations_csv and OLD_ID not in story_locations_csv
