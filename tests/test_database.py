"""Tests for the Database domain API (db package).

Replaces the four legacy CSV-based story test files:
  test_story_metadata.py, test_story_remove.py,
  test_story_link_location.py, test_story_weapon_equipment_links.py
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

import db._queries as q
from db import (
    Database,
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    RegionEntry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_hero(database: Database, slug: str, name: str) -> str:
    from registry_ids import canonical_id

    cid = canonical_id(slug)
    q.upsert_hero_canonical(
        database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name
    )
    return cid


def _seed_weapon(database: Database, slug: str, name: str) -> str:
    from registry_ids import make_hash_id

    wid = make_hash_id("CW", slug)
    q.upsert_weapon_canonical(
        database.conn,
        canonical_weapon_id=wid,
        canonical_slug=slug,
        canonical_weapon=name,
    )
    return wid


def _seed_equipment(database: Database, slug: str, name: str) -> str:
    from registry_ids import make_hash_id

    eid = make_hash_id("CE", slug)
    q.upsert_equipment_canonical(
        database.conn,
        canonical_equipment_id=eid,
        canonical_slug=slug,
        canonical_equipment=name,
    )
    return eid


# ---------------------------------------------------------------------------
# Story metadata persistence
# ---------------------------------------------------------------------------


def test_upsert_story_persists_metadata(db: Database) -> None:
    """Metadata fields are stored in the stories table."""
    db.upsert_story(
        "src/main-story/meta.md",
        story_type="main-story",
        title="Meta Story",
        authors="Author A, Author B",
        artists="Illustrator A",
        source_link="https://example.com/story",
        publication_date="2026-05-13",
        thumbnail_image_link="https://example.com/thumb.jpg",
    )
    row = db.conn.execute("SELECT * FROM stories").fetchone()
    assert row["title"] == "Meta Story"
    assert row["authors"] == "Author A, Author B"
    assert row["artists"] == "Illustrator A"
    assert row["source_link"] == "https://example.com/story"
    assert row["publication_date"] == "2026-05-13"
    assert row["thumbnail_image_link"] == "https://example.com/thumb.jpg"


def test_upsert_story_returns_story_record(db: Database) -> None:
    """upsert_story returns a StoryRecord with correct fields."""
    rec = db.upsert_story(
        "src/main-story/a.md",
        story_type="main-story",
        title="Alpha",
        authors="Writer",
    )
    assert rec.title == "Alpha"
    assert rec.story_key == "main-story/a.md"
    assert rec.story_type == "main-story"
    assert rec.authors == "Writer"
    assert rec.story_id.startswith("ST")


def test_upsert_story_narrated_videos_stored(db: Database) -> None:
    """Narrated videos are stored in the narrated_videos table."""
    db.upsert_story(
        "src/main-story/vid.md",
        story_type="main-story",
        title="Video Story",
        narrated_videos=[
            NarratedVideoEntry("Narrator One", "https://video.example.com/1"),
            NarratedVideoEntry("Narrator Two", "https://video.example.com/2"),
        ],
    )
    story_id = db.conn.execute("SELECT story_id FROM stories").fetchone()["story_id"]
    vids = db.conn.execute(
        "SELECT author, source_link FROM narrated_videos WHERE story_id = ?",
        [story_id],
    ).fetchall()
    assert len(vids) == 2
    assert {v["author"] for v in vids} == {"Narrator One", "Narrator Two"}


def test_upsert_story_replaces_narrated_videos(db: Database) -> None:
    """Passing new narrated_videos replaces the previous list."""
    db.upsert_story(
        "src/main-story/vid.md",
        story_type="main-story",
        title="T",
        narrated_videos=[NarratedVideoEntry("Old", "https://old.com")],
    )
    db.upsert_story(
        "src/main-story/vid.md",
        story_type="main-story",
        title="T",
        narrated_videos=[NarratedVideoEntry("New", "https://new.com")],
    )
    story_id = db.conn.execute("SELECT story_id FROM stories").fetchone()["story_id"]
    vids = db.conn.execute(
        "SELECT author FROM narrated_videos WHERE story_id = ?", [story_id]
    ).fetchall()
    assert len(vids) == 1
    assert vids[0]["author"] == "New"


# ---------------------------------------------------------------------------
# get_story
# ---------------------------------------------------------------------------


def test_get_story_returns_record(db: Database) -> None:
    """get_story returns a StoryRecord for a registered path."""
    db.upsert_story("src/main-story/a.md", story_type="main-story", title="Alpha")
    rec = db.get_story("src/main-story/a.md")
    assert rec is not None
    assert rec.title == "Alpha"
    assert rec.story_key == "main-story/a.md"


def test_get_story_returns_none_for_unknown(db: Database) -> None:
    """get_story returns None when the path has not been registered."""
    assert db.get_story("src/main-story/nope.md") is None


# ---------------------------------------------------------------------------
# NPC links
# ---------------------------------------------------------------------------


def test_upsert_story_links_npcs(db: Database) -> None:
    """NPCEntry creates an npc row and a story_npcs junction."""
    db.upsert_story(
        "src/main-story/npc.md",
        story_type="main-story",
        title="NPC Story",
        npcs=[NPCEntry("Guard Captain", species="Human", status="Alive")],
    )
    npc = db.conn.execute("SELECT * FROM npcs").fetchone()
    assert npc["name"] == "Guard Captain"
    assert npc["species"] == "Human"
    assert db.conn.execute("SELECT COUNT(*) FROM story_npcs").fetchone()[0] == 1


def test_upsert_story_npc_replace_semantics(db: Database) -> None:
    """Passing npcs=[] removes all existing NPC links."""
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        npcs=[NPCEntry("Soldier")],
    )
    db.upsert_story("src/main-story/x.md", story_type="main-story", title="X", npcs=[])
    assert db.conn.execute("SELECT COUNT(*) FROM story_npcs").fetchone()[0] == 0


def test_upsert_story_npc_none_leaves_existing(db: Database) -> None:
    """Passing npcs=None leaves existing NPC links unchanged."""
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        npcs=[NPCEntry("Soldier")],
    )
    db.upsert_story(
        "src/main-story/x.md", story_type="main-story", title="X", npcs=None
    )
    assert db.conn.execute("SELECT COUNT(*) FROM story_npcs").fetchone()[0] == 1


# ---------------------------------------------------------------------------
# Hero links
# ---------------------------------------------------------------------------


def test_upsert_story_links_heroes(db: Database) -> None:
    """Hero canonical slugs are resolved and stored in story_heroes."""
    _seed_hero(db, "boltyn", "Boltyn")
    db.upsert_story(
        "src/main-story/hero.md",
        story_type="main-story",
        title="Hero",
        heroes=["boltyn"],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM story_heroes").fetchone()[0] == 1


def test_upsert_story_unknown_hero_raises(db: Database) -> None:
    """Unknown hero slug raises ValueError before any write."""
    with pytest.raises(ValueError, match="Unknown hero canonical slug"):
        db.upsert_story(
            "src/main-story/hero.md",
            story_type="main-story",
            title="H",
            heroes=["nonexistent-slug"],
        )
    assert db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Weapon links
# ---------------------------------------------------------------------------


def test_upsert_story_links_weapon(db: Database) -> None:
    """Weapon slug is resolved and stored in story_weapons."""
    _seed_weapon(db, "test-blade", "Test Blade")
    db.upsert_story(
        "src/main-story/w.md",
        story_type="main-story",
        title="W",
        weapons=["test-blade"],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM story_weapons").fetchone()[0] == 1


def test_upsert_story_unknown_weapon_raises(db: Database) -> None:
    """Unknown weapon slug raises ValueError."""
    with pytest.raises(ValueError, match="Unknown weapon canonical slug"):
        db.upsert_story(
            "src/main-story/w.md",
            story_type="main-story",
            title="W",
            weapons=["missing-blade"],
        )


# ---------------------------------------------------------------------------
# Equipment links
# ---------------------------------------------------------------------------


def test_upsert_story_links_equipment(db: Database) -> None:
    """Equipment slug is resolved and stored in story_equipment."""
    _seed_equipment(db, "iron-boots", "Iron Boots")
    db.upsert_story(
        "src/main-story/e.md",
        story_type="main-story",
        title="E",
        equipment=["iron-boots"],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM story_equipment").fetchone()[0] == 1


def test_upsert_story_unknown_equipment_raises(db: Database) -> None:
    """Unknown equipment slug raises ValueError."""
    with pytest.raises(ValueError, match="Unknown equipment canonical slug"):
        db.upsert_story(
            "src/main-story/e.md",
            story_type="main-story",
            title="E",
            equipment=["missing-gear"],
        )


# ---------------------------------------------------------------------------
# Location links
# ---------------------------------------------------------------------------


def test_upsert_story_location_without_region(db: Database) -> None:
    """LocationEntry without region stores an empty region_id on the locations row."""
    db.upsert_story(
        "src/main-story/loc.md",
        story_type="main-story",
        title="L",
        locations=[LocationEntry("Lost Isle", notes="somewhere")],
    )
    loc = db.conn.execute("SELECT * FROM locations").fetchone()
    assert loc["name"] == "Lost Isle"
    assert (loc["region_id"] or "") == ""
    assert db.conn.execute("SELECT COUNT(*) FROM story_locations").fetchone()[0] == 1


def test_upsert_story_location_with_region(db: Database) -> None:
    """LocationEntry with region= upserts the region and links the location."""
    db.upsert_story(
        "src/main-story/loc.md",
        story_type="main-story",
        title="L",
        locations=[
            LocationEntry(
                "Testville",
                region="Testaria",
                world_of_rathe_story_key="world-of-rathe/testaria.md",
            )
        ],
    )
    reg = db.conn.execute("SELECT * FROM regions").fetchone()
    assert reg["region_name"] == "Testaria"
    assert reg["world_of_rathe_story_key"] == "world-of-rathe/testaria.md"
    loc = db.conn.execute("SELECT * FROM locations").fetchone()
    assert loc["name"] == "Testville"
    assert loc["region_id"] == reg["region_id"]


def test_upsert_story_location_lore_fragment_valid(
    db: Database, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A lore_fragment matching a heading on the world lore page is accepted."""
    world_dir = tmp_path / "src" / "world-of-rathe"
    world_dir.mkdir(parents=True)
    (world_dir / "aria.md").write_text("# Aria\n### Enion\n", encoding="utf-8")
    import db._domain as _dom

    monkeypatch.setattr(_dom, "SRC", tmp_path / "src")

    db.upsert_story(
        tmp_path / "src" / "flavour" / "a.md",
        story_type="flavour",
        title="A",
        locations=[
            LocationEntry(
                "Enion",
                region="Aria",
                world_of_rathe_story_key="world-of-rathe/aria.md",
                lore_fragment="enion",
            )
        ],
    )
    loc = db.conn.execute("SELECT lore_fragment FROM locations").fetchone()
    assert loc["lore_fragment"] == "enion"


def test_upsert_story_location_lore_fragment_invalid(
    db: Database, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A lore_fragment not present on the world lore page raises ValueError."""
    world_dir = tmp_path / "src" / "world-of-rathe"
    world_dir.mkdir(parents=True)
    (world_dir / "aria.md").write_text("# Aria\n### Enion\n", encoding="utf-8")
    import db._domain as _dom

    monkeypatch.setattr(_dom, "SRC", tmp_path / "src")

    with pytest.raises(ValueError, match="not found in"):
        db.upsert_story(
            tmp_path / "src" / "flavour" / "b.md",
            story_type="flavour",
            title="B",
            locations=[
                LocationEntry(
                    "Nowhere",
                    region="Aria",
                    world_of_rathe_story_key="world-of-rathe/aria.md",
                    lore_fragment="nosuchsection",
                )
            ],
        )


# ---------------------------------------------------------------------------
# Region links
# ---------------------------------------------------------------------------


def test_upsert_story_regions(db: Database) -> None:
    """RegionEntry creates a regions row and story_regions junction."""
    db.upsert_story(
        "src/main-story/r.md",
        story_type="main-story",
        title="R",
        regions=[
            RegionEntry(
                "Testaria", world_of_rathe_story_key="world-of-rathe/testaria.md"
            )
        ],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == 1
    assert db.conn.execute("SELECT COUNT(*) FROM story_regions").fetchone()[0] == 1


# ---------------------------------------------------------------------------
# Other lore entities
# ---------------------------------------------------------------------------


def test_upsert_story_monsters(db: Database) -> None:
    """MonsterEntry creates a monster row and story_monsters junction."""
    db.upsert_story(
        "src/main-story/m.md",
        story_type="main-story",
        title="M",
        monsters=[MonsterEntry("Cave Troll", description="Big.")],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0] == 1
    assert db.conn.execute("SELECT COUNT(*) FROM story_monsters").fetchone()[0] == 1


def test_upsert_story_fauna(db: Database) -> None:
    """FaunaEntry creates a fauna row and story_fauna junction."""
    db.upsert_story(
        "src/main-story/f.md",
        story_type="main-story",
        title="F",
        fauna=[FaunaEntry("River Eel")],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM fauna").fetchone()[0] == 1
    assert db.conn.execute("SELECT COUNT(*) FROM story_fauna").fetchone()[0] == 1


def test_upsert_story_flora(db: Database) -> None:
    """FloraEntry creates a flora row and story_flora junction."""
    db.upsert_story(
        "src/main-story/fl.md",
        story_type="main-story",
        title="Fl",
        flora=[FloraEntry("Moon Lily")],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM flora").fetchone()[0] == 1


def test_upsert_story_food_drink(db: Database) -> None:
    """FoodDrinkEntry creates a food_and_drink row and story_food_drink junction."""
    db.upsert_story(
        "src/main-story/fd.md",
        story_type="main-story",
        title="Fd",
        food_drink=[FoodDrinkEntry("Ember Ale", kind="Drink")],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM food_and_drink").fetchone()[0] == 1


# ---------------------------------------------------------------------------
# remove_story
# ---------------------------------------------------------------------------


def test_remove_story_dry_run(db: Database) -> None:
    """Dry run reports junction counts and 'DRY RUN' without deleting anything."""
    db.upsert_story(
        "src/archive/sample.md",
        story_type="archive",
        title="Sample",
        npcs=[NPCEntry("Guard")],
    )
    buf = io.StringIO()
    report = db.remove_story("src/archive/sample.md", dry_run=True, file=buf)

    assert report["dry_run"] is True
    assert "sample.md" in report["story_key"]
    assert report["story_deleted"] is False
    assert report["junctions"]["story_npcs"] == 1
    assert "DRY RUN" in buf.getvalue()
    assert db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 1


def test_remove_story_actual(db: Database) -> None:
    """Non-dry-run removes the story row and all junction rows."""
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        npcs=[NPCEntry("Soldier")],
    )
    report = db.remove_story("src/main-story/x.md", file=io.StringIO())

    assert report["dry_run"] is False
    assert report["story_deleted"] is True
    assert db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 0
    assert db.conn.execute("SELECT COUNT(*) FROM story_npcs").fetchone()[0] == 0


def test_remove_story_second_pass_is_no_op(db: Database) -> None:
    """Removing an already-absent story is handled gracefully."""
    db.upsert_story(
        "src/flavour/twice.md",
        story_type="flavour",
        title="Twice",
        npcs=[NPCEntry("Guard")],
    )
    db.remove_story("src/flavour/twice.md", file=io.StringIO())
    report = db.remove_story("src/flavour/twice.md", file=io.StringIO())

    assert report["story_id"] is None
    assert report["story_deleted"] is False


# ---------------------------------------------------------------------------
# dry_run for upsert_story
# ---------------------------------------------------------------------------


def test_upsert_story_dry_run_does_not_write(db: Database, capsys) -> None:
    """dry_run=True returns a StoryRecord without persisting any data."""
    rec = db.upsert_story(
        "src/main-story/draft.md",
        story_type="main-story",
        title="Draft",
        dry_run=True,
    )
    assert rec.title == "Draft"
    assert rec.story_key == "main-story/draft.md"
    assert db.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0] == 0


def test_upsert_story_dry_run_prints_summary(db: Database, capsys) -> None:
    """dry_run prints 'DRY RUN' to stdout."""
    db.upsert_story(
        "src/main-story/d.md", story_type="main-story", title="D", dry_run=True
    )
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
