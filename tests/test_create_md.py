"""Tests for :mod:`create_md` (optional pandas / py-markdown-table)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))


def test_create_md_characters_md_from_characters_csv(tmp_path: Path) -> None:
    """npcs.csv can be rendered to npcs.md via output_md."""
    pytest.importorskip("pandas")
    pytest.importorskip("py_markdown_table")

    import create_md

    data = tmp_path / "data"
    data.mkdir(parents=True)
    characters = data / "characters.csv"
    characters.write_text(
        "# comment\nCharacterId|Name|Species|Status\n" "LCbbbbbbbbbb|Zed|Human|Alive\n" "LCaaaaaaaaaa|Amy|Elf|Dead\n",
        encoding="utf-8",
    )
    out = data / "characters.md"
    create_md.create_md_file(characters, "Name", output_md=out)
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
        "LocationId|Name|RegionId|Notes\n" "LObbbbbbbbbb|Zed Town|RGaaaaaaaaaa|Near water\n",
        encoding="utf-8",
    )
    out = data / "locations.md"
    create_md.create_md_file(data / "locations.csv", "Name", output_md=out)
    text = out.read_text(encoding="utf-8")
    assert "LocationId" not in text and "RegionId" not in text
    assert "LObbbbbbbbbb" not in text and "RGaaaaaaaaaa" not in text
    assert "Test Region" in text and "Zed Town" in text


def test_the_sync_hook_triggers_on_files_that_actually_exist() -> None:
    """Every path in the ensure-create-md-sync trigger must be a real file.

    Migration 12 renamed `npcs.csv` to `characters.csv` and `npcs.md` to
    `characters.md`, updated `MD_FILES` in the script, and left this regex
    naming the old paths. The hook then stopped firing for the largest registry
    in the repo — a rename cannot break a mirror check loudly, so it broke it
    silently, and the mirror could drift exactly as the hand-written
    character-groups page once did.
    """
    import re

    root = Path(__file__).resolve().parent.parent
    config = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    hook = config[config.index("id: ensure-create-md-sync") :]
    line = next(x for x in hook.splitlines() if x.strip().startswith("files:"))
    pattern = line.split("files:", 1)[1].strip()

    # Pull the alternations back out of the anchored regex and rebuild the paths.
    stems = re.findall(r"\(([a-z0-9|+-]+)\)\\\.(csv|md)", pattern)
    missing = []
    for group, ext in stems:
        folder = "csv" if ext == "csv" else "md"
        for stem in group.split("|"):
            if not (root / "src" / "data" / folder / f"{stem}.{ext}").is_file():
                missing.append(f"src/data/{folder}/{stem}.{ext}")
    assert not missing, f"ensure-create-md-sync triggers on files that do not exist: {missing}"
