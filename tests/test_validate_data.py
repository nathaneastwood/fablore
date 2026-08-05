"""Integration checks for :mod:`validate_data`."""

from __future__ import annotations

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
