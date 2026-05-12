"""Integration checks for :mod:`validate_data`."""

from __future__ import annotations

import validate_data


def test_collect_alerts_empty_when_repository_consistent() -> None:
    """Committed CSVs under ``src/data`` satisfy validation rules."""
    assert validate_data.collect_alerts() == []


def test_check_location_lore_fragments_rejects_unsafe_ids(tmp_path: Path) -> None:
    """``LoreFragment`` must look like an HTML ``id`` fragment."""
    loc = tmp_path / "locations.csv"
    loc.write_text(
        "# banner\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|X|RG1||bad frag\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_lore_fragments(loc)
    assert len(alerts) == 1
    assert "bad frag" in alerts[0]
