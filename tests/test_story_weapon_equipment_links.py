"""Tests for :meth:`Story.link_weapon` and :meth:`Story.link_equipment`."""

from __future__ import annotations

from pathlib import Path

import pytest

import story


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
    monkeypatch.setattr(story, "WEAPONS_CANONICAL_CSV_PATH", data / "weapons-canonical.csv")
    monkeypatch.setattr(story, "EQUIPMENT_CANONICAL_CSV_PATH", data / "equipment-canonical.csv")
    return src, data


def test_link_weapon_writes_canonical_id_junction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """link_weapon resolves slug from weapons-canonical and merges story-weapons row."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "main-story" / "x.md"
    md.parent.mkdir(parents=True)
    md.write_text("# X\n", encoding="utf-8")

    (data / "weapons-canonical.csv").write_text(
        "# banner\n"
        "CanonicalWeaponId|CanonicalSlug|CanonicalWeapon\n"
        "CWtest111111|test-blade|Test Blade\n",
        encoding="utf-8",
    )

    s = story.Story(md, "main-story", "X")
    wid = s.link_weapon(canonical_slug="test-blade")
    assert wid == "CWtest111111"

    _, rows = story.read_pipe_csv(data / "story-weapons.csv")
    assert len(rows) == 1
    assert (rows[0].get("StoryId") or "").strip() == s.story_id
    assert (rows[0].get("CanonicalWeaponId") or "").strip() == "CWtest111111"


def test_link_weapon_unknown_slug_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown CanonicalSlug raises ValueError."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "flavour" / "y.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Y\n", encoding="utf-8")

    (data / "weapons-canonical.csv").write_text(
        "CanonicalWeaponId|CanonicalSlug|CanonicalWeapon\n"
        "CWaaaaaaaaaa|other|Other\n",
        encoding="utf-8",
    )

    s = story.Story(md, "flavour", "Y")
    with pytest.raises(ValueError, match="Unknown weapon CanonicalSlug"):
        s.link_weapon(canonical_slug="missing-blade")


def test_link_equipment_writes_canonical_id_junction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """link_equipment resolves slug from equipment-canonical."""
    src, data = _patch_story_paths(tmp_path, monkeypatch)
    md = src / "short-stories" / "z.md"
    md.parent.mkdir(parents=True)
    md.write_text("# Z\n", encoding="utf-8")

    (data / "equipment-canonical.csv").write_text(
        "CanonicalEquipmentId|CanonicalSlug|CanonicalEquipment\n"
        "CEtest222222|iron-boots|Iron Boots\n",
        encoding="utf-8",
    )

    s = story.Story(md, "short-stories", "Z")
    eid = s.link_equipment(canonical_slug="iron-boots")
    assert eid == "CEtest222222"

    _, rows = story.read_pipe_csv(data / "story-equipment.csv")
    assert len(rows) == 1
    assert (rows[0].get("CanonicalEquipmentId") or "").strip() == "CEtest222222"
