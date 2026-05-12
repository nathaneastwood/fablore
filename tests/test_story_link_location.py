"""Tests for :meth:`Story.link_location` and ``regions.csv`` upserts."""

from __future__ import annotations

from pathlib import Path

import pytest

import story
from registry_ids import location_id, region_row_id


def _patch_story_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Point ``story`` module data dirs at ``tmp_path``."""
    root = tmp_path
    src = root / "src"
    data = src / "data"
    data.mkdir(parents=True)
    monkeypatch.setattr(story, "ROOT", root)
    monkeypatch.setattr(story, "SRC", src)
    monkeypatch.setattr(story, "DATA", data)
    monkeypatch.setattr(story, "STORIES_PATH", data / "stories.csv")
    return src, data


def test_link_location_unknown_region_no_regions_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Omitting region leaves empty RegionId; regions.csv need not exist."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "main-story" / "place.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Place\n", encoding="utf-8")

    s = story.Story(md, "main-story", "Place")
    lid = s.link_location("Lost Isle", location_notes="somewhere")

    assert lid == location_id("Lost Isle", "")
    assert not (data / "regions.csv").is_file()

    _, loc_rows = story.read_pipe_csv(data / "locations.csv")
    assert len(loc_rows) == 1
    assert (loc_rows[0].get("RegionId") or "").strip() == ""


def test_link_location_region_name_upserts_regions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """region_name= creates regions.csv and sets LocationId from resolved region."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "flavour" / "town.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Town\n", encoding="utf-8")

    s = story.Story(md, "flavour", "Town")
    rg = region_row_id("Testaria")
    lid = s.link_location(
        "Testville",
        region_name="Testaria",
        world_of_rathe_story_key="world-of-rathe/testaria.md",
    )

    assert lid == location_id("Testville", rg)
    _, reg_rows = story.read_pipe_csv(data / "regions.csv")
    assert len(reg_rows) == 1
    assert (reg_rows[0].get("RegionId") or "").strip() == rg
    assert (reg_rows[0].get("RegionName") or "").strip() == "Testaria"
    assert (reg_rows[0].get("WorldOfRatheStoryKey") or "").strip() == (
        "world-of-rathe/testaria.md"
    )


def test_link_location_region_id_requires_existing_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """region_id alone must exist in regions.csv."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "flavour" / "x.md"
    md.parent.mkdir(parents=True)
    md.write_text("# X\n", encoding="utf-8")

    (data / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n"
        "RGaaaaaaaaaa|Old|world-of-rathe/old.md\n",
        encoding="utf-8",
    )

    s = story.Story(md, "flavour", "X")
    with pytest.raises(ValueError, match="not in regions"):
        s.link_location("Y", region_id="RGbbbbbbbbbb")


def test_link_location_region_id_and_name_must_agree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Conflicting region_id and region_name raises ValueError."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "flavour" / "z.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Z\n", encoding="utf-8")

    s = story.Story(md, "flavour", "Z")
    with pytest.raises(ValueError, match="does not match region_name"):
        s.link_location(
            "Zed",
            region_id="RGaaaaaaaaaa",
            region_name="Other",
        )


def test_link_location_sets_lore_fragment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``lore_fragment=`` persists ``LoreFragment`` on ``locations.csv``."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text(
        "## Aria\n### Enion\n", encoding="utf-8"
    )
    md = src / "flavour" / "anyon.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Anyon\n", encoding="utf-8")

    s = story.Story(md, "flavour", "Anyon")
    s.link_location(
        "Enion",
        region_name="Aria",
        world_of_rathe_story_key="world-of-rathe/aria.md",
        lore_fragment="enion",
    )
    _, loc_rows = story.read_pipe_csv(data / "locations.csv")
    assert len(loc_rows) == 1
    assert (loc_rows[0].get("LoreFragment") or "").strip() == "enion"


def test_link_location_rejects_unknown_lore_fragment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid ``lore_fragment`` raises ``ValueError`` with valid heading ids."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text(
        "## Aria\n### Enion\n", encoding="utf-8"
    )
    md = src / "flavour" / "b.md"
    md.parent.mkdir(parents=True)
    md.write_text("# B\n", encoding="utf-8")

    s = story.Story(md, "flavour", "B")
    with pytest.raises(ValueError, match="not a heading id"):
        s.link_location(
            "Nowhere",
            region_name="Aria",
            world_of_rathe_story_key="world-of-rathe/aria.md",
            lore_fragment="nosuchsection",
        )
