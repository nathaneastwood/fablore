"""Tests for db/_export.py — CSV and JSON export functions.

Covers the public API (export_all, export_stories, export_registry_tables,
export_story_junctions, dump_to_json) and the private
_export_story_narrated_videos helper (exercised via export_all).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import db._export as _export
import db._queries as q
from db import Database


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _csv_lines(path: Path) -> list[str]:
    """Return non-empty lines from a CSV file."""
    return [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _csv_header(path: Path) -> str:
    """Return the pipe-delimited header line (second line — first is the banner)."""
    lines = _csv_lines(path)
    # First line is the auto_gen_banner comment; second is headers.
    return lines[1]


def _csv_data_lines(path: Path) -> list[str]:
    """Return all data lines (everything after the banner and header)."""
    lines = _csv_lines(path)
    return lines[2:]


# ---------------------------------------------------------------------------
# export_stories
# ---------------------------------------------------------------------------


def test_export_stories_creates_file(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo Story",
    )
    _export.export_stories(db.conn, tmp_path)

    csv_path = tmp_path / "csv" / "stories.csv"
    assert csv_path.exists()


def test_export_stories_header_columns(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo Story",
    )
    _export.export_stories(db.conn, tmp_path)

    header = _csv_header(tmp_path / "csv" / "stories.csv")
    for col in ("StoryId", "StoryKey", "StoryType", "Title"):
        assert col in header


def test_export_stories_data_row_present(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo Story",
        authors="Jane Author",
    )
    _export.export_stories(db.conn, tmp_path)

    content = (tmp_path / "csv" / "stories.csv").read_text(encoding="utf-8")
    assert "Foo Story" in content
    assert "Jane Author" in content


def test_export_stories_banner_present(db: Database, tmp_path: Path) -> None:
    _export.export_stories(db.conn, tmp_path)
    first_line = _csv_lines(tmp_path / "csv" / "stories.csv")[0]
    assert first_line.startswith("#")


# ---------------------------------------------------------------------------
# export_registry_tables
# ---------------------------------------------------------------------------


def test_export_registry_tables_creates_all_files(db: Database, tmp_path: Path) -> None:
    _export.export_registry_tables(db.conn, tmp_path)

    csv_dir = tmp_path / "csv"
    for fname in (
        "regions.csv",
        "locations.csv",
        "npcs.csv",
        "monsters.csv",
        "fauna.csv",
        "flora.csv",
        "food-and-drink.csv",
    ):
        assert (csv_dir / fname).exists(), f"Missing {fname}"


def test_export_registry_tables_regions(db: Database, tmp_path: Path) -> None:
    q.upsert_region(db.conn, region_id="R1", region_name="Solana")
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "regions.csv").read_text(encoding="utf-8")
    assert "Solana" in content
    assert "RegionId" in content
    assert "RegionName" in content


def test_export_registry_tables_locations(db: Database, tmp_path: Path) -> None:
    q.upsert_region(db.conn, region_id="R1", region_name="Solana")
    q.upsert_location(
        db.conn,
        location_id="L1",
        name="Grand Bazaar",
        region_id="R1",
        notes="A marketplace.",
        lore_fragment="grand-bazaar",
    )
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "locations.csv").read_text(encoding="utf-8")
    assert "Grand Bazaar" in content
    assert "LocationId" in content


def test_export_registry_tables_npcs(db: Database, tmp_path: Path) -> None:
    q.upsert_npc(
        db.conn,
        character_id="C1",
        name="Ira",
        species="Draconic",
        status="Alive",
    )
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "npcs.csv").read_text(encoding="utf-8")
    assert "Ira" in content
    assert "CharacterId" in content


def test_export_registry_tables_monsters(db: Database, tmp_path: Path) -> None:
    q.upsert_monster(
        db.conn, monster_id="M1", name="Brute", description="Big and mean."
    )
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "monsters.csv").read_text(encoding="utf-8")
    assert "Brute" in content
    assert "MonsterId" in content


def test_export_registry_tables_fauna(db: Database, tmp_path: Path) -> None:
    q.upsert_fauna(db.conn, fauna_id="FA1", name="Brawnhide", description="A lizard.")
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "fauna.csv").read_text(encoding="utf-8")
    assert "Brawnhide" in content
    assert "FaunaId" in content


def test_export_registry_tables_flora(db: Database, tmp_path: Path) -> None:
    q.upsert_flora(db.conn, flora_id="FL1", name="Starbloom", description="A flower.")
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "flora.csv").read_text(encoding="utf-8")
    assert "Starbloom" in content
    assert "FloraId" in content


def test_export_registry_tables_food_drink(db: Database, tmp_path: Path) -> None:
    q.upsert_food_drink(db.conn, food_drink_id="FD1", name="Arcane Brew", type_="Drink")
    _export.export_registry_tables(db.conn, tmp_path)

    content = (tmp_path / "csv" / "food-and-drink.csv").read_text(encoding="utf-8")
    assert "Arcane Brew" in content
    assert "FoodDrinkId" in content


# ---------------------------------------------------------------------------
# export_story_junctions
# ---------------------------------------------------------------------------


def test_export_story_junctions_heroes(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo",
    )
    q.upsert_hero_canonical(
        db.conn,
        canonical_id="CN1",
        canonical_slug="boltyn",
        canonical_hero="Boltyn",
    )
    q.set_story_heroes(db.conn, "S1", [("CN1", "")])
    _export.export_story_junctions(db.conn, tmp_path)

    content = (tmp_path / "csv" / "story-heroes.csv").read_text(encoding="utf-8")
    assert "S1" in content
    assert "CN1" in content
    assert "StoryId" in content
    assert "CanonicalId" in content


def test_export_story_junctions_npcs(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo",
    )
    q.upsert_npc(db.conn, character_id="C1", name="Guard")
    q.set_story_npcs(db.conn, "S1", [("C1", "intro")])
    _export.export_story_junctions(db.conn, tmp_path)

    content = (tmp_path / "csv" / "story-npcs.csv").read_text(encoding="utf-8")
    assert "S1" in content
    assert "C1" in content
    assert "CharacterId" in content
    assert "Fragment" in content


def test_export_story_junctions_locations(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/foo.md",
        story_type="main-story",
        title="Foo",
    )
    q.upsert_location(db.conn, location_id="L1", name="Grand Bazaar")
    q.set_story_junction(db.conn, "S1", "story_locations", "location_id", ["L1"])
    _export.export_story_junctions(db.conn, tmp_path)

    content = (tmp_path / "csv" / "story-locations.csv").read_text(encoding="utf-8")
    assert "S1" in content
    assert "L1" in content
    assert "LocationId" in content


def test_export_story_junctions_creates_all_files(db: Database, tmp_path: Path) -> None:
    _export.export_story_junctions(db.conn, tmp_path)

    csv_dir = tmp_path / "csv"
    for fname in (
        "story-heroes.csv",
        "story-npcs.csv",
        "story-locations.csv",
        "story-regions.csv",
        "story-monsters.csv",
        "story-fauna.csv",
        "story-flora.csv",
        "story-food-drink.csv",
        "story-weapons.csv",
        "story-equipment.csv",
    ):
        assert (csv_dir / fname).exists(), f"Missing {fname}"


# ---------------------------------------------------------------------------
# _export_story_narrated_videos (via export_all)
# ---------------------------------------------------------------------------


def test_export_all_creates_narrated_videos_csv(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/vid.md",
        story_type="main-story",
        title="Video Story",
    )
    q.set_narrated_videos(
        db.conn,
        "S1",
        [("Alice", "https://example.com/vid", "https://yt.com/c/alice")],
    )
    _export.export_all(db.conn, tmp_path)

    csv_path = tmp_path / "csv" / "story-narrated-videos.csv"
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "Alice" in content
    assert "StoryId" in content
    assert "Author" in content
    assert "SourceLink" in content


def test_export_all_narrated_videos_empty(db: Database, tmp_path: Path) -> None:
    _export.export_all(db.conn, tmp_path)

    csv_path = tmp_path / "csv" / "story-narrated-videos.csv"
    assert csv_path.exists()
    # Only banner + header, no data rows
    data_lines = _csv_data_lines(csv_path)
    assert data_lines == []


# ---------------------------------------------------------------------------
# export_all
# ---------------------------------------------------------------------------


def test_export_all_creates_stories_and_registry_files(
    db: Database, tmp_path: Path
) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/all.md",
        story_type="main-story",
        title="All Story",
    )
    q.upsert_region(db.conn, region_id="R1", region_name="Solana")
    q.upsert_location(db.conn, location_id="L1", name="The Cathedral", region_id="R1")
    q.upsert_npc(db.conn, character_id="C1", name="The High Lord")

    _export.export_all(db.conn, tmp_path)

    csv_dir = tmp_path / "csv"
    assert (csv_dir / "stories.csv").exists()
    assert (csv_dir / "regions.csv").exists()
    assert (csv_dir / "locations.csv").exists()
    assert (csv_dir / "npcs.csv").exists()
    assert "All Story" in (csv_dir / "stories.csv").read_text(encoding="utf-8")
    assert "Solana" in (csv_dir / "regions.csv").read_text(encoding="utf-8")
    assert "The Cathedral" in (csv_dir / "locations.csv").read_text(encoding="utf-8")
    assert "The High Lord" in (csv_dir / "npcs.csv").read_text(encoding="utf-8")


def test_export_all_creates_heroes_and_weapons_files(
    db: Database, tmp_path: Path
) -> None:
    _export.export_all(db.conn, tmp_path)

    csv_dir = tmp_path / "csv"
    for fname in (
        "heroes-canonical.csv",
        "heroes-game.csv",
        "heroes-printings.csv",
        "weapons-canonical.csv",
        "weapons-game.csv",
        "weapons-printings.csv",
        "equipment-canonical.csv",
        "equipment-game.csv",
        "equipment-printings.csv",
        "classes.csv",
        "talents.csv",
        "sets.csv",
        "set-types.csv",
    ):
        assert (csv_dir / fname).exists(), f"Missing {fname}"


# ---------------------------------------------------------------------------
# dump_to_json
# ---------------------------------------------------------------------------


def test_dump_to_json_creates_json_files(db: Database, tmp_path: Path) -> None:
    json_dir = tmp_path / "json"
    _export.dump_to_json(db.conn, json_dir)

    assert json_dir.exists()
    for table in ("stories", "regions", "npcs", "monsters", "fauna", "flora"):
        assert (json_dir / f"{table}.json").exists(), f"Missing {table}.json"


def test_dump_to_json_stories_content(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/json-test.md",
        story_type="main-story",
        title="JSON Test Story",
        authors="Some Author",
    )
    json_dir = tmp_path / "json"
    _export.dump_to_json(db.conn, json_dir)

    data = json.loads((json_dir / "stories.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["story_id"] == "S1"
    assert data[0]["title"] == "JSON Test Story"
    assert data[0]["authors"] == "Some Author"


def test_dump_to_json_regions_content(db: Database, tmp_path: Path) -> None:
    q.upsert_region(db.conn, region_id="R1", region_name="Solana")
    json_dir = tmp_path / "json"
    _export.dump_to_json(db.conn, json_dir)

    data = json.loads((json_dir / "regions.json").read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["region_id"] == "R1"
    assert data[0]["region_name"] == "Solana"


def test_dump_to_json_narrated_videos(db: Database, tmp_path: Path) -> None:
    q.upsert_story(
        db.conn,
        story_id="S1",
        story_key="main-story/vid.md",
        story_type="main-story",
        title="Video",
    )
    q.set_narrated_videos(
        db.conn,
        "S1",
        [("Narrator One", "https://vid.example.com", "https://yt.com/c/one")],
    )
    json_dir = tmp_path / "json"
    _export.dump_to_json(db.conn, json_dir)

    data = json.loads((json_dir / "narrated_videos.json").read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["story_id"] == "S1"
    assert data[0]["author"] == "Narrator One"


def test_dump_to_json_empty_tables_are_valid_json(db: Database, tmp_path: Path) -> None:
    json_dir = tmp_path / "json"
    _export.dump_to_json(db.conn, json_dir)

    for table in ("stories", "npcs", "monsters", "story_heroes", "story_npcs"):
        path = json_dir / f"{table}.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == []


def test_dump_to_json_creates_output_dir(db: Database, tmp_path: Path) -> None:
    json_dir = tmp_path / "nested" / "json" / "output"
    assert not json_dir.exists()
    _export.dump_to_json(db.conn, json_dir)
    assert json_dir.exists()
    assert (json_dir / "stories.json").exists()
