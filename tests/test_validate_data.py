"""Integration checks for :mod:`validate_data`."""

from __future__ import annotations

import json
from pathlib import Path

import validate_data


def test_collect_alerts_empty_when_repository_consistent() -> None:
    """Committed CSVs under ``src/data`` satisfy validation rules."""
    assert validate_data.collect_alerts() == []


def test_check_location_lore_fragments_rejects_unsafe_ids(tmp_path: Path) -> None:
    """``LoreFragment`` must look like an HTML ``id`` fragment."""
    loc = tmp_path / "locations.csv"
    loc.write_text(
        "# banner\n" "LocationId|Name|RegionId|Notes|LoreFragment\n" "LO1|X|RG1||bad frag\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_lore_fragments(loc)
    assert len(alerts) == 1
    assert "bad frag" in alerts[0]


def test_collect_warnings_does_not_raise_or_block() -> None:
    """``collect_warnings`` is informational only; must always return a list."""
    warnings = validate_data.collect_warnings()
    assert isinstance(warnings, list)


def test_check_id_hash_drift_flags_stale_id(tmp_path: Path) -> None:
    from registry_ids import monster_id

    path = tmp_path / "monsters.csv"
    path.write_text(
        "# banner\nMonsterId|Name|Description\nMOdeadbeef01|Test Beast|\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_id_hash_drift(path, "MonsterId", "Name", monster_id, "monsters.csv")
    assert len(alerts) == 1
    assert "Test Beast" in alerts[0]


def test_check_id_hash_drift_clean_when_id_matches(tmp_path: Path) -> None:
    from registry_ids import monster_id

    computed = monster_id("Test Beast")
    path = tmp_path / "monsters.csv"
    path.write_text(
        f"# banner\nMonsterId|Name|Description\n{computed}|Test Beast|\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_id_hash_drift(path, "MonsterId", "Name", monster_id, "monsters.csv")
    assert alerts == []


def test_check_location_id_hash_drift_flags_stale_id(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\nLocationId|Name|RegionId|Notes|LoreFragment\nLOdeadbeef01|Test Place|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_id_hash_drift(path)
    assert len(alerts) == 1
    assert "Test Place" in alerts[0]


def test_check_location_id_hash_drift_clean_when_id_matches(tmp_path: Path) -> None:
    from registry_ids import location_id

    computed = location_id("Test Place", "RG1")
    path = tmp_path / "locations.csv"
    path.write_text(
        f"# banner\nLocationId|Name|RegionId|Notes|LoreFragment\n{computed}|Test Place|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_id_hash_drift(path)
    assert alerts == []


def test_check_near_duplicate_names_flags_typo(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|Amphitheatre|RG1||\n"
        "LO2|Ampitheatre|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert len(alerts) == 1
    assert "Amphitheatre" in alerts[0] and "Ampitheatre" in alerts[0]


def test_check_near_duplicate_names_ignores_unrelated_names(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n" "LocationId|Name|RegionId|Notes|LoreFragment\n" "LO1|The Maela|RG1||\n" "LO2|The Valdur|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert alerts == []


def test_check_near_duplicate_names_respects_group_column(tmp_path: Path) -> None:
    """Same near-duplicate name pair in *different* regions should not be flagged
    when grouped by region — they may legitimately be distinct places."""
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|Ampitheatre|RG1||\n"
        "LO2|Amphitheatre|RG2||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert alerts == []


# ---------------------------------------------------------------------------
# hints_supplement.json entity types
# ---------------------------------------------------------------------------


def _supplement(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "hints_supplement.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_check_supplement_types_accepts_known_types(tmp_path: Path) -> None:
    path = _supplement(tmp_path, {"Chanek": {"type": "species", "summary": "Rathenfolk of the far west."}})
    assert validate_data._check_supplement_types(path) == []


def test_check_supplement_types_flags_a_typo(tmp_path: Path) -> None:
    """The reason this check exists.

    theme/hints.js prints `type` verbatim as the tooltip label, so a misspelling
    ships as a visible label rather than failing anything downstream.
    """
    path = _supplement(tmp_path, {"Rosetta": {"type": "factoin", "summary": "An Order of spell weavers."}})
    alerts = validate_data._check_supplement_types(path)
    assert len(alerts) == 1
    assert "'factoin'" in alerts[0]


def test_check_supplement_types_skips_override_only_entries(tmp_path: Path) -> None:
    """25 entries carry only match/url/exclude_pages and take their type from the DB."""
    path = _supplement(tmp_path, {"Isenloft": {"url": "/world-of-rathe/aria.html#isenloft"}})
    assert validate_data._check_supplement_types(path) == []


def test_check_supplement_types_skips_plain_string_entries(tmp_path: Path) -> None:
    """The seven Solanian weekdays are stored as bare summary strings."""
    path = _supplement(tmp_path, {"Lunedes": "Solanian Monday"})
    assert validate_data._check_supplement_types(path) == []


def test_species_is_a_known_type() -> None:
    """Added 2026-08-20 so Chanek could be retyped off `faction`; it is a species."""
    assert "species" in validate_data._SUPPLEMENT_TYPES


def test_real_supplement_has_no_unknown_types() -> None:
    assert validate_data._check_supplement_types(validate_data.SRC / "hints_supplement.json") == []


# ---------------------------------------------------------------------------
# Group lore fragments
# ---------------------------------------------------------------------------


def _group_fragment_fixture(tmp_path: Path, lore_story_key: str, lore_fragment: str) -> tuple[Path, Path, Path]:
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "solana.md").write_text("# Solana\n\n### The Hand of Sol\n\ntext\n", encoding="utf-8")
    groups = tmp_path / "groups.csv"
    groups.write_text(
        "# banner\n"
        "GroupId|Name|Kind|Notes|ParentGroupId|LocationId|LoreStoryKey|LoreFragment\n"
        f"GR1|Hand of Sol|order|||| {lore_story_key}|{lore_fragment}\n".replace("| ", "|"),
        encoding="utf-8",
    )
    stories = tmp_path / "stories.csv"
    stories.write_text(
        "# banner\nStoryId|StoryKey|StoryType|Title\nST1|world-of-rathe/solana.md|world-of-rathe|Solana\n",
        encoding="utf-8",
    )
    return groups, stories, src


def test_check_group_lore_fragments_accepts_a_real_heading(tmp_path: Path) -> None:
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/solana.md", "the-hand-of-sol")
    assert validate_data._check_group_lore_fragments(groups, stories, src) == []


def test_check_group_lore_fragments_rejects_a_missing_heading(tmp_path: Path) -> None:
    """Catches a heading renamed in the markdown, which nothing else would see."""
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/solana.md", "the-hand-of-sun")
    alerts = validate_data._check_group_lore_fragments(groups, stories, src)
    assert len(alerts) == 1
    assert "the-hand-of-sun" in alerts[0]


def test_check_group_lore_fragments_rejects_an_unknown_page(tmp_path: Path) -> None:
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/nowhere.md", "the-hand-of-sol")
    alerts = validate_data._check_group_lore_fragments(groups, stories, src)
    assert len(alerts) == 1
    assert "not a StoryKey" in alerts[0]


def test_check_group_lore_fragments_ignores_groups_with_no_link(tmp_path: Path) -> None:
    """Most groups carry no documentation page, and that is not an error."""
    groups, stories, src = _group_fragment_fixture(tmp_path, "", "")
    assert validate_data._check_group_lore_fragments(groups, stories, src) == []


# ---------------------------------------------------------------------------
# Membership and alternate-name FK checks
# ---------------------------------------------------------------------------


def test_epithet_kind_must_be_in_the_closed_list(tmp_path: Path) -> None:
    from validate_data import _check_epithet_kinds

    path = tmp_path / "npc-epithets.csv"
    path.write_text("# x\nCharacterId|Name|Kind\nLC1|the Fixer|nickname\n")
    alerts = _check_epithet_kinds(path)
    assert len(alerts) == 1
    assert "nickname" in alerts[0]


def test_epithet_kind_accepts_both_valid_kinds(tmp_path: Path) -> None:
    from validate_data import _check_epithet_kinds

    path = tmp_path / "npc-epithets.csv"
    path.write_text("# x\nCharacterId|Name|Kind\nLC1|the Fixer|epithet\nLC1|Mortimer|short-name\n")
    assert _check_epithet_kinds(path) == []
