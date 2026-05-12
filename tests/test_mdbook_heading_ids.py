"""Tests for :mod:`mdbook_heading_ids` (mdBook 0.4 heading id compatibility)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_heading_ids import (  # noqa: E402
    collect_heading_anchor_ids,
    collect_heading_anchor_ids_from_path,
    id_from_content,
    normalize_id,
    require_valid_lore_fragment,
    unique_id_from_content,
)


def test_normalize_id_rust_examples() -> None:
    assert (
        normalize_id("`--passes`: add more rustdoc passes")
        == "--passes-add-more-rustdoc-passes"
    )
    assert normalize_id("_-_12345") == "_-_12345"
    assert normalize_id("12345") == "12345"


def test_id_from_content_strips_hashes() -> None:
    assert id_from_content("### Enion") == "enion"
    assert id_from_content("Enion") == "enion"


def test_unique_id_duplicate_headings() -> None:
    ctr: dict[str, int] = {}
    assert unique_id_from_content("#### Wayfarers", ctr) == "wayfarers"
    assert unique_id_from_content("#### Wayfarers", ctr) == "wayfarers-1"


def test_collect_heading_ids_includes_enion_on_real_aria() -> None:
    aria = ROOT / "src/world-of-rathe/aria.md"
    ids = collect_heading_anchor_ids_from_path(aria)
    assert "enion" in ids
    assert "wayfarers" in ids and "wayfarers-1" in ids


def test_require_valid_lore_fragment_ok(tmp_path: Path) -> None:
    src = tmp_path / "src"
    data = tmp_path / "src" / "data"
    data.mkdir(parents=True)
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text(
        "## Aria\n### Enion\nBody.\n", encoding="utf-8"
    )
    regions = data / "regions.csv"
    regions.write_text(
        "# h\nRegionId|RegionName|WorldOfRatheStoryKey\n"
        "RG1|Aria|world-of-rathe/aria.md\n",
        encoding="utf-8",
    )
    require_valid_lore_fragment(
        src_root=src,
        regions_csv=regions,
        region_id="RG1",
        lore_fragment="enion",
    )


def test_require_valid_lore_fragment_lists_options(tmp_path: Path) -> None:
    src = tmp_path / "src"
    data = tmp_path / "src" / "data"
    data.mkdir(parents=True)
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text("## Aria\n### Enion\n", encoding="utf-8")
    regions = data / "regions.csv"
    regions.write_text(
        "# h\nRegionId|RegionName|WorldOfRatheStoryKey\n"
        "RG1|Aria|world-of-rathe/aria.md\n",
        encoding="utf-8",
    )
    try:
        require_valid_lore_fragment(
            src_root=src,
            regions_csv=regions,
            region_id="RG1",
            lore_fragment="nosuch",
        )
    except ValueError as exc:
        msg = str(exc)
        assert "nosuch" in msg
        assert "aria" in msg.lower() or "enion" in msg
    else:
        raise AssertionError("expected ValueError")


def test_collect_heading_anchor_ids_skips_non_atx() -> None:
    md = "Para\n\n## One\n\nUnderlined\n--------\n"
    assert collect_heading_anchor_ids(md) == ["one"]
