"""Tests for :mod:`create_md` (optional pandas / py-markdown-table)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))


def test_create_md_npcs_md_from_npcs_csv(tmp_path: Path) -> None:
    """npcs.csv can be rendered to npcs.md via output_md."""
    pytest.importorskip("pandas")
    pytest.importorskip("py_markdown_table")

    import create_md

    data = tmp_path / "data"
    data.mkdir(parents=True)
    npcs = data / "npcs.csv"
    npcs.write_text(
        "# comment\nCharacterId|Name|Species|Status\n"
        "LCbbbbbbbbbb|Zed|Human|Alive\n"
        "LCaaaaaaaaaa|Amy|Elf|Dead\n",
        encoding="utf-8",
    )
    out = data / "npcs.md"
    create_md.create_md_file(npcs, "Name", output_md=out)
    text = out.read_text(encoding="utf-8")
    assert "<!-- ### NOTE:" in text
    assert "CharacterId" not in text
    assert "LCbbbbbbbbbb" not in text
    assert "Amy" in text and "Zed" in text
    assert text.index("Amy") < text.index("Zed")


def test_create_md_locations_includes_region_name_not_ids(tmp_path: Path) -> None:
    """locations.md drops LocationId/RegionId and shows RegionName from regions.csv."""
    pytest.importorskip("pandas")
    pytest.importorskip("py_markdown_table")

    import create_md

    data = tmp_path / "data"
    data.mkdir(parents=True)
    (data / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n" "RGaaaaaaaaaa|Test Region|\n",
        encoding="utf-8",
    )
    (data / "locations.csv").write_text(
        "LocationId|Name|RegionId|Notes\n"
        "LObbbbbbbbbb|Zed Town|RGaaaaaaaaaa|Near water\n",
        encoding="utf-8",
    )
    out = data / "locations.md"
    create_md.create_md_file(data / "locations.csv", "Name", output_md=out)
    text = out.read_text(encoding="utf-8")
    assert "LocationId" not in text and "RegionId" not in text
    assert "LObbbbbbbbbb" not in text and "RGaaaaaaaaaa" not in text
    assert "Test Region" in text and "Zed Town" in text
