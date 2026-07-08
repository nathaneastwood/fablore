"""Extra tests for db/_domain.py — covers list_*/print_* helpers, StoryRecord.display/remove,
display_story, and _print_table."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "data"))

import db._queries as q
from db import Database, NPCEntry, RegionEntry, LocationEntry


# ---------------------------------------------------------------------------
# Helpers (mirrors test_database.py)
# ---------------------------------------------------------------------------


def _seed_weapon(database: Database, slug: str, name: str) -> str:
    from registry_ids import make_hash_id

    wid = make_hash_id("CW", slug)
    q.upsert_weapon_canonical(database.conn, canonical_weapon_id=wid, canonical_slug=slug, canonical_weapon=name)
    return wid


def _seed_equipment(database: Database, slug: str, name: str) -> str:
    from registry_ids import make_hash_id

    eid = make_hash_id("CE", slug)
    q.upsert_equipment_canonical(
        database.conn, canonical_equipment_id=eid, canonical_slug=slug, canonical_equipment=name
    )
    return eid


# ---------------------------------------------------------------------------
# list_weapons / list_equipment
# ---------------------------------------------------------------------------


def test_list_weapons_empty(db: Database) -> None:
    assert db.list_weapons() == []


def test_list_weapons_with_data(db: Database) -> None:
    _seed_weapon(db, "iron-axe", "Iron Axe")
    weapons = db.list_weapons()
    assert len(weapons) == 1
    assert weapons[0]["slug"] == "iron-axe"
    assert weapons[0]["name"] == "Iron Axe"


def test_list_equipment_empty(db: Database) -> None:
    assert db.list_equipment() == []


def test_list_equipment_with_data(db: Database) -> None:
    _seed_equipment(db, "iron-boots", "Iron Boots")
    equipment = db.list_equipment()
    assert len(equipment) == 1
    assert equipment[0]["slug"] == "iron-boots"
    assert equipment[0]["name"] == "Iron Boots"


# ---------------------------------------------------------------------------
# list_regions / list_npcs / list_locations
# ---------------------------------------------------------------------------


def test_list_regions_empty(db: Database) -> None:
    assert db.list_regions() == []


def test_list_regions_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/r.md",
        story_type="main-story",
        title="R",
        regions=[RegionEntry("Solana", world_of_rathe_story_key="world-of-rathe/solana.md")],
    )
    regions = db.list_regions()
    assert any(r["region_name"] == "Solana" for r in regions)


def test_list_npcs_empty(db: Database) -> None:
    assert db.list_npcs() == []


def test_list_npcs_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/n.md",
        story_type="main-story",
        title="N",
        npcs=[NPCEntry("Guard Captain", species="Human", status="Alive")],
    )
    npcs = db.list_npcs()
    assert any(n["name"] == "Guard Captain" for n in npcs)
    assert all("name" in n and "species" in n and "status" in n for n in npcs)


def test_list_locations_empty(db: Database) -> None:
    assert db.list_locations() == []


def test_list_locations_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/l.md",
        story_type="main-story",
        title="L",
        locations=[LocationEntry("Grand Bazaar", notes="A busy market")],
    )
    locations = db.list_locations()
    assert any(loc["name"] == "Grand Bazaar" for loc in locations)
    assert all("name" in loc and "region" in loc for loc in locations)


# ---------------------------------------------------------------------------
# print_heroes / print_weapons / print_equipment / print_regions / print_npcs / print_locations
# ---------------------------------------------------------------------------


def test_print_heroes_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_heroes(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_weapons_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_weapons(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_weapons_with_data(db: Database) -> None:
    _seed_weapon(db, "ember-blade", "Ember Blade")
    buf = io.StringIO()
    db.print_weapons(file=buf)
    out = buf.getvalue()
    assert "ember-blade" in out
    assert "Ember Blade" in out


def test_print_equipment_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_equipment(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_equipment_with_data(db: Database) -> None:
    _seed_equipment(db, "silver-helm", "Silver Helm")
    buf = io.StringIO()
    db.print_equipment(file=buf)
    out = buf.getvalue()
    assert "silver-helm" in out
    assert "Silver Helm" in out


def test_print_regions_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_regions(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_regions_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/r2.md",
        story_type="main-story",
        title="R2",
        regions=[RegionEntry("Aria")],
    )
    buf = io.StringIO()
    db.print_regions(file=buf)
    assert "Aria" in buf.getvalue()


def test_print_npcs_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_npcs(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_npcs_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/n2.md",
        story_type="main-story",
        title="N2",
        npcs=[NPCEntry("Ranger", species="Elf", status="Unknown")],
    )
    buf = io.StringIO()
    db.print_npcs(file=buf)
    assert "Ranger" in buf.getvalue()


def test_print_locations_empty(db: Database) -> None:
    buf = io.StringIO()
    db.print_locations(file=buf)
    assert "(none)" in buf.getvalue()


def test_print_locations_with_data(db: Database) -> None:
    db.upsert_story(
        "src/main-story/l2.md",
        story_type="main-story",
        title="L2",
        locations=[LocationEntry("Dark Tower")],
    )
    buf = io.StringIO()
    db.print_locations(file=buf)
    assert "Dark Tower" in buf.getvalue()


# ---------------------------------------------------------------------------
# _print_table — exercises stdout path (no file= argument)
# ---------------------------------------------------------------------------


def test_print_heroes_stdout(db: Database, capsys) -> None:
    db.print_heroes()
    out = capsys.readouterr().out
    assert isinstance(out, str)


def test_print_regions_stdout(db: Database, capsys) -> None:
    db.print_regions()
    capsys.readouterr()  # Should not raise


# ---------------------------------------------------------------------------
# stories table — direct query (list_stories / print_stories don't exist)
# ---------------------------------------------------------------------------


def test_stories_table_empty_at_start(db: Database) -> None:
    count = db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
    assert count == 0


def test_stories_table_has_entry_after_upsert(db: Database) -> None:
    db.upsert_story("src/main-story/foo.md", story_type="main-story", title="Foo")
    row = db.conn.execute("SELECT title, story_type FROM stories").fetchone()
    assert row["title"] == "Foo"
    assert row["story_type"] == "main-story"


def test_stories_table_multiple_entries(db: Database) -> None:
    db.upsert_story("src/main-story/a.md", story_type="main-story", title="Alpha")
    db.upsert_story("src/main-story/b.md", story_type="main-story", title="Beta")
    count = db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
    assert count == 2


# ---------------------------------------------------------------------------
# StoryRecord.display / StoryRecord.remove
# ---------------------------------------------------------------------------


def test_story_record_display(db: Database, monkeypatch, capsys) -> None:
    import db._domain as _dom

    r = db.upsert_story("src/main-story/foo.md", story_type="main-story", title="Foo")
    # StoryRecord.display() passes the short story_key back through _story_key_from_path,
    # which can't resolve bare keys without the src/ prefix. Patch it to pass through.
    monkeypatch.setattr(_dom, "_story_key_from_path", lambda p: str(p))
    r.display()
    out = capsys.readouterr().out
    assert "Foo" in out


def test_story_record_display_to_buffer(db: Database, monkeypatch) -> None:
    import db._domain as _dom

    r = db.upsert_story("src/main-story/foo.md", story_type="main-story", title="Bar Display")
    monkeypatch.setattr(_dom, "_story_key_from_path", lambda p: str(p))
    buf = io.StringIO()
    r.display(file=buf)
    assert "Bar Display" in buf.getvalue()


def test_story_record_remove(db: Database, monkeypatch, capsys) -> None:
    import db._domain as _dom

    r = db.upsert_story("src/main-story/foo.md", story_type="main-story", title="Foo")
    # StoryRecord.remove() passes story_key (short form) back through _story_key_from_path;
    # patch it to pass through so the story is found by key directly.
    monkeypatch.setattr(_dom, "_story_key_from_path", lambda p: str(p))
    result = r.remove(dry_run=False)
    capsys.readouterr()  # discard printed output
    assert "story_key" in result
    assert result["story_deleted"] is True


def test_story_record_remove_dry_run(db: Database, monkeypatch, capsys) -> None:
    import db._domain as _dom

    r = db.upsert_story("src/main-story/foo.md", story_type="main-story", title="Foo")
    monkeypatch.setattr(_dom, "_story_key_from_path", lambda p: str(p))
    result = r.remove(dry_run=True)
    capsys.readouterr()  # discard printed output
    assert result["dry_run"] is True
    assert result["story_deleted"] is False
    # Restore path fn and verify story still exists
    monkeypatch.undo()
    assert db.get_story("src/main-story/foo.md") is not None


# ---------------------------------------------------------------------------
# display_story
# ---------------------------------------------------------------------------


def test_display_story_not_found(db: Database) -> None:
    buf = io.StringIO()
    db.display_story("src/main-story/nonexistent.md", file=buf)
    assert "not found" in buf.getvalue().lower()


def test_display_story_basic(db: Database) -> None:
    db.upsert_story(
        "src/main-story/foo.md",
        story_type="main-story",
        title="Foo",
        authors="Alice",
        artists="Bob",
        source_link="https://example.com",
        publication_date="2025-01-01",
    )
    buf = io.StringIO()
    db.display_story("src/main-story/foo.md", file=buf)
    out = buf.getvalue()
    assert "Foo" in out
    assert "Alice" in out
    assert "Bob" in out
    assert "2025-01-01" in out
    assert "https://example.com" in out


def test_display_story_with_junctions(db: Database) -> None:
    db.upsert_story(
        "src/main-story/foo.md",
        story_type="main-story",
        title="Junction Story",
        npcs=[NPCEntry("Mystic", species="Unknown", status="Unknown")],
    )
    buf = io.StringIO()
    db.display_story("src/main-story/foo.md", file=buf)
    out = buf.getvalue()
    assert "Mystic" in out
    assert "NPCs" in out
