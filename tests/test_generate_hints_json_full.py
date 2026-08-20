"""Tests for the DB-interaction functions in generate_hints_json.

Covers: _key, _entry_with_match, _region_map, and generate().
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from generate_hints_json import _entry_with_match, _key, _region_map  # noqa: E402


# ---------------------------------------------------------------------------
# _key
# ---------------------------------------------------------------------------


def test_key_no_apostrophe():
    assert _key("Hello") == "Hello"


def test_key_strips_apostrophe():
    assert _key("Kae'io") == "Kaeio"


def test_key_multiple_apostrophes():
    assert _key("O'Dar'el") == "ODarel"


# ---------------------------------------------------------------------------
# _entry_with_match
# ---------------------------------------------------------------------------


def test_entry_with_match_no_match_field_when_key_equals_name():
    result = _entry_with_match("normal", {"type": "fauna"})
    assert result == {"type": "fauna"}
    assert "match" not in result


def test_entry_with_match_adds_match_field_when_key_differs():
    result = _entry_with_match("Kae'io", {"type": "fauna"})
    assert result == {"match": "Kae'io", "type": "fauna"}


def test_entry_with_match_does_not_mutate_base():
    base = {"type": "fauna"}
    _entry_with_match("Kae'io", base)
    assert "match" not in base


# ---------------------------------------------------------------------------
# _region_map
# ---------------------------------------------------------------------------


def test_region_map_returns_dict():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE regions (region_id TEXT, region_name TEXT)")
    conn.execute("INSERT INTO regions VALUES ('R1', 'Solana')")
    conn.execute("INSERT INTO regions VALUES ('R2', 'Aria')")
    conn.commit()

    result = _region_map(conn)
    conn.close()

    assert result == {"R1": "Solana", "R2": "Aria"}


def test_region_map_empty_table():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE regions (region_id TEXT, region_name TEXT)")
    conn.commit()

    result = _region_map(conn)
    conn.close()

    assert result == {}


# ---------------------------------------------------------------------------
# generate() helpers
# ---------------------------------------------------------------------------


def _make_db(path: Path) -> None:
    """Create a minimal fablore DB at *path*."""
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE regions (region_id TEXT, region_name TEXT)")
    conn.execute("CREATE TABLE locations (name TEXT, notes TEXT, region_id TEXT, location_id TEXT DEFAULT '')")
    conn.execute("CREATE TABLE monsters (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE fauna (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE flora (name TEXT, description TEXT)")
    conn.execute(
        "CREATE TABLE groups (name TEXT, kind TEXT, notes TEXT, location_id TEXT DEFAULT '',"
        " lore_story_key TEXT DEFAULT '', lore_fragment TEXT DEFAULT '')"
    )
    conn.execute("INSERT INTO regions VALUES ('R1', 'Solana')")
    conn.execute("INSERT INTO locations (name, notes, region_id) VALUES ('Grand Bazaar', 'A marketplace.', 'R1')")
    conn.execute("INSERT INTO locations (name, notes, region_id) VALUES ('Empty Place', '', 'R1')")
    conn.execute("INSERT INTO monsters VALUES ('Brute', 'A nasty beast.')")
    conn.execute("INSERT INTO fauna VALUES (\"Kae'io\", 'A bird.')")
    conn.execute("INSERT INTO flora VALUES ('Starbloom', '')")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# generate()
# ---------------------------------------------------------------------------


def test_generate_writes_output(tmp_path, monkeypatch):
    import generate_hints_json as ghj

    db_path = tmp_path / "fablore.db"
    _make_db(db_path)

    output_path = tmp_path / "hints.json"
    monkeypatch.setattr(ghj, "DB_PATH", db_path)
    monkeypatch.setattr(ghj, "SUPPLEMENT_PATH", tmp_path / "nonexistent.json")
    monkeypatch.setattr(ghj, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(ghj, "ROOT", tmp_path)

    ghj.generate()

    hints = json.loads(output_path.read_text(encoding="utf-8"))

    # Location with notes is included with region
    assert "Grand Bazaar" in hints
    assert hints["Grand Bazaar"]["type"] == "location"
    assert hints["Grand Bazaar"]["summary"] == "A marketplace."
    assert hints["Grand Bazaar"]["region"] == "Solana"

    # Location with empty notes is skipped
    assert "Empty Place" not in hints

    # Monster included
    assert "Brute" in hints
    assert hints["Brute"]["type"] == "monster"
    assert hints["Brute"]["summary"] == "A nasty beast."

    # Fauna with apostrophe: key has apostrophe stripped, match field added
    assert "Kaeio" in hints
    assert hints["Kaeio"]["type"] == "fauna"
    assert hints["Kaeio"]["match"] == "Kae'io"

    # Flora with empty description is skipped
    assert "Starbloom" not in hints


def test_generate_no_region_for_unknown_region_id(tmp_path, monkeypatch):
    import generate_hints_json as ghj

    db_path = tmp_path / "fablore.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE regions (region_id TEXT, region_name TEXT)")
    conn.execute("CREATE TABLE locations (name TEXT, notes TEXT, region_id TEXT, location_id TEXT DEFAULT '')")
    conn.execute("CREATE TABLE monsters (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE fauna (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE flora (name TEXT, description TEXT)")
    conn.execute(
        "CREATE TABLE groups (name TEXT, kind TEXT, notes TEXT, location_id TEXT DEFAULT '',"
        " lore_story_key TEXT DEFAULT '', lore_fragment TEXT DEFAULT '')"
    )
    # Location references a region_id not in the regions table
    conn.execute("INSERT INTO locations (name, notes, region_id) VALUES ('Lost Shrine', 'Ancient ruins.', 'UNKNOWN')")
    conn.commit()
    conn.close()

    output_path = tmp_path / "hints.json"
    monkeypatch.setattr(ghj, "DB_PATH", db_path)
    monkeypatch.setattr(ghj, "SUPPLEMENT_PATH", tmp_path / "nonexistent.json")
    monkeypatch.setattr(ghj, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(ghj, "ROOT", tmp_path)

    ghj.generate()

    hints = json.loads(output_path.read_text(encoding="utf-8"))
    assert "Lost Shrine" in hints
    assert "region" not in hints["Lost Shrine"]


def test_generate_merges_supplement(tmp_path, monkeypatch):
    import generate_hints_json as ghj

    db_path = tmp_path / "fablore.db"
    _make_db(db_path)

    supplement = {
        "Grand Bazaar": {"exclude_pages": ["main-story/set/story"]},
        "ExtraEntry": {"type": "faction", "summary": "A new group."},
    }
    supplement_path = tmp_path / "supplement.json"
    supplement_path.write_text(json.dumps(supplement), encoding="utf-8")

    output_path = tmp_path / "hints.json"
    monkeypatch.setattr(ghj, "DB_PATH", db_path)
    monkeypatch.setattr(ghj, "SUPPLEMENT_PATH", supplement_path)
    monkeypatch.setattr(ghj, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(ghj, "ROOT", tmp_path)

    ghj.generate()

    hints = json.loads(output_path.read_text(encoding="utf-8"))

    # Supplement field merged into existing DB entry
    assert hints["Grand Bazaar"]["type"] == "location"
    assert hints["Grand Bazaar"]["exclude_pages"] == ["main-story/set/story"]

    # Supplement-only entry appended
    assert "ExtraEntry" in hints
    assert hints["ExtraEntry"]["type"] == "faction"


def test_generate_output_is_valid_json(tmp_path, monkeypatch):
    import generate_hints_json as ghj

    db_path = tmp_path / "fablore.db"
    _make_db(db_path)

    output_path = tmp_path / "hints.json"
    monkeypatch.setattr(ghj, "DB_PATH", db_path)
    monkeypatch.setattr(ghj, "SUPPLEMENT_PATH", tmp_path / "nonexistent.json")
    monkeypatch.setattr(ghj, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(ghj, "ROOT", tmp_path)

    ghj.generate()

    # Must parse without error and be a dict
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Group tooltips — derived region, carried url
# ---------------------------------------------------------------------------


def _make_group_db(path: Path) -> None:
    """A DB holding one group tied to a place and one that is not."""
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE regions (region_id TEXT, region_name TEXT)")
    conn.execute("CREATE TABLE locations (name TEXT, notes TEXT, region_id TEXT, location_id TEXT DEFAULT '')")
    conn.execute("CREATE TABLE monsters (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE fauna (name TEXT, description TEXT)")
    conn.execute("CREATE TABLE flora (name TEXT, description TEXT)")
    conn.execute(
        "CREATE TABLE groups (name TEXT, kind TEXT, notes TEXT, location_id TEXT DEFAULT '',"
        " lore_story_key TEXT DEFAULT '', lore_fragment TEXT DEFAULT '')"
    )
    conn.execute("INSERT INTO regions VALUES ('R1', 'Misteria')")
    conn.execute("INSERT INTO locations (name, notes, region_id, location_id) VALUES ('Ikaru', 'A house.', 'R1', 'L1')")
    conn.execute("INSERT INTO groups VALUES ('Ikaru Clan', 'house', 'One of the houses of Misteria.', 'L1', '', '')")
    conn.execute(
        "INSERT INTO groups VALUES ('Hand of Sol', 'order of knights', \"Solana's knights.\", '',"
        " 'world-of-rathe/solana.md', 'the-hand-of-sol')"
    )
    conn.commit()
    conn.close()


def _generate_from(db_path: Path, tmp_path: Path, monkeypatch) -> dict:
    import generate_hints_json as ghj

    output_path = tmp_path / "hints.json"
    monkeypatch.setattr(ghj, "DB_PATH", db_path)
    monkeypatch.setattr(ghj, "SUPPLEMENT_PATH", tmp_path / "nonexistent.json")
    monkeypatch.setattr(ghj, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(ghj, "ROOT", tmp_path)
    ghj.generate()
    return json.loads(output_path.read_text(encoding="utf-8"))


def test_group_region_is_derived_from_its_location(tmp_path: Path, monkeypatch) -> None:
    """Groups store no region. One tied to a place borrows that place's region."""
    db_path = tmp_path / "fablore.db"
    _make_group_db(db_path)
    hints = _generate_from(db_path, tmp_path, monkeypatch)
    assert hints["Ikaru Clan"]["region"] == "Misteria"


def test_group_with_no_location_has_no_region(tmp_path: Path, monkeypatch) -> None:
    """A group is not an immovable object; most carry no region at all."""
    db_path = tmp_path / "fablore.db"
    _make_group_db(db_path)
    hints = _generate_from(db_path, tmp_path, monkeypatch)
    assert "region" not in hints["Hand of Sol"]


def test_group_url_comes_from_its_own_documentation_page(tmp_path: Path, monkeypatch) -> None:
    """What kept the Hand of Sol's link alive when its locations row was dropped."""
    db_path = tmp_path / "fablore.db"
    _make_group_db(db_path)
    hints = _generate_from(db_path, tmp_path, monkeypatch)
    assert hints["Hand of Sol"]["url"] == "/world-of-rathe/solana.html#the-hand-of-sol"


def test_group_tooltip_type_is_its_kind(tmp_path: Path, monkeypatch) -> None:
    """Decided 2026-08-20: the label carries the kind, not a flat 'group'."""
    db_path = tmp_path / "fablore.db"
    _make_group_db(db_path)
    hints = _generate_from(db_path, tmp_path, monkeypatch)
    assert hints["Hand of Sol"]["type"] == "order of knights"
