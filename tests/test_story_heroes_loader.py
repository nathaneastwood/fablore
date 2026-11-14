"""The one story→hero join (migration 17) and the callers that read it.

``mdbook_common.load_story_heroes`` is the single home of the
``story-characters.csv`` → ``character-heroes.csv`` → ``heroes-canonical.csv``
join. The story_meta test pins what that preprocessor produced before it moved
onto the shared loader.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook_common import entity_names, load_story_heroes
from mdbook_story_meta import _load_story_heroes


def _write_csvs(src_root: Path, files: dict[str, str]) -> Path:
    csv_dir = src_root / "data" / "csv"
    csv_dir.mkdir(parents=True)
    for name, body in files.items():
        (csv_dir / name).write_text("# AUTO-GENERATED\n" + body, encoding="utf-8")
    return src_root / "data"


_CLEAN = {
    "heroes-canonical.csv": "CanonicalId|CanonicalSlug|CanonicalHero\nCN1|azalea|Azalea\nCN2|kano|Kano\nCN3|dash|Dash\n",
    "character-heroes.csv": "CanonicalId|CharacterId\nCN1|LC1\nCN2|LC2\nCN3|LC3\n",
    # ST1: Kano, an ordinary character, Azalea, Kano again. ST2: Azalea only.
    "story-characters.csv": (
        "StoryId|CharacterId|Fragment\n" "ST1|LC2|\n" "ST1|LC9|\n" "ST1|LC1|azalea\n" "ST1|LC2|\n" "ST2|LC1|\n"
    ),
}


@pytest.fixture
def clean_src(tmp_path: Path) -> Path:
    _write_csvs(tmp_path, _CLEAN)
    hero_dir = tmp_path / "heroes-of-rathe"
    hero_dir.mkdir()
    (hero_dir / "azalea-about.md").write_text("# Azalea\n", encoding="utf-8")
    return tmp_path


def test_story_meta_heroes_in_junction_order_once_each(clean_src: Path) -> None:
    """Heroes in junction row order, deduplicated; ordinary characters dropped; no page -> None."""
    assert _load_story_heroes(clean_src / "data", clean_src) == {
        "ST1": [("Kano", None), ("Azalea", "heroes-of-rathe/azalea-about.md")],
        "ST2": [("Azalea", "heroes-of-rathe/azalea-about.md")],
    }


def test_story_meta_heroes_empty_without_the_junction(tmp_path: Path) -> None:
    files = dict(_CLEAN)
    del files["story-characters.csv"]
    data_dir = _write_csvs(tmp_path, files)
    assert _load_story_heroes(data_dir, tmp_path) == {}


def test_load_story_heroes_joins_story_character_canonical(tmp_path: Path) -> None:
    data_dir = _write_csvs(tmp_path, _CLEAN)
    sh = load_story_heroes(data_dir)
    assert sh.character_to_canonical == {"LC1": "CN1", "LC2": "CN2", "LC3": "CN3"}
    assert sh.canonical_to_character == {"CN1": "LC1", "CN2": "LC2", "CN3": "LC3"}
    assert sh.story_heroes == {"ST1": ("CN2", "CN1"), "ST2": ("CN1",)}
    assert sh.hero_stories == {"CN1": frozenset({"ST1", "ST2"}), "CN2": frozenset({"ST1"})}
    assert sh.story_characters == {"ST1": frozenset({"LC1", "LC2", "LC9"}), "ST2": frozenset({"LC1"})}
    assert sh.character_stories == {
        "LC1": frozenset({"ST1", "ST2"}),
        "LC2": frozenset({"ST1"}),
        "LC9": frozenset({"ST1"}),
    }
    assert sh.fragments == {("ST1", "LC1"): "azalea"}


def test_load_story_heroes_strips_and_skips_blank_ids(tmp_path: Path) -> None:
    data_dir = _write_csvs(
        tmp_path,
        {
            "character-heroes.csv": "CanonicalId|CharacterId\n CN1 | LC1 \nCN2|\n|LC2\n",
            "story-characters.csv": "StoryId|CharacterId|Fragment\n ST1 | LC1 |\nST1||\n|LC1|\n",
        },
    )
    sh = load_story_heroes(data_dir)
    assert sh.character_to_canonical == {"LC1": "CN1"}
    assert sh.story_heroes == {"ST1": ("CN1",)}
    assert sh.story_characters == {"ST1": frozenset({"LC1"})}


def test_load_story_heroes_empty_when_csvs_absent(tmp_path: Path) -> None:
    sh = load_story_heroes(tmp_path)
    assert sh.character_to_canonical == {} and sh.story_heroes == {} and sh.hero_stories == {}


def test_entity_names_strips_and_skips_blank_id_or_name(tmp_path: Path) -> None:
    data_dir = _write_csvs(tmp_path, {"regions.csv": "RegionId|RegionName\n R1 | Aria \nR2|\n|Misteria\n"})
    assert entity_names(data_dir / "csv" / "regions.csv", "RegionId", "RegionName") == {"R1": "Aria"}
