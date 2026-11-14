"""The site-section registry in ``mdbook_common`` and the views each caller derives from it.

The registry replaced about ten hand-kept tables. The characterisation tests
below pin each caller's view to the literal table it used to hold (README/index
pairs collapsed to the ``index.md`` form ``chapter_path`` returns), so a registry
edit that would change a page shows up here before it shows up in the build.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from mdbook_common import SECTIONS, SECTION_BY_KEY, Section, chapter_path, normalise_page_path

SRC = Path(__file__).resolve().parent.parent / "src"
DATA = SRC / "data"


# ---------------------------------------------------------------------------
# The registry itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("section", SECTIONS, ids=lambda s: s.key)
def test_every_section_is_a_directory_under_src(section: Section) -> None:
    assert (SRC / section.key).is_dir()


@pytest.mark.parametrize("section", [s for s in SECTIONS if s.hub], ids=lambda s: s.key)
def test_every_hub_page_exists(section: Section) -> None:
    assert (SRC / section.hub).is_file()
    assert section.hub.startswith(section.prefix)


def test_keys_are_unique_and_indexed() -> None:
    assert len({s.key for s in SECTIONS}) == len(SECTIONS)
    assert all(SECTION_BY_KEY[s.key] is s for s in SECTIONS)


def test_sections_are_frozen() -> None:
    with pytest.raises(AttributeError):
        SECTIONS[0].key = "x"  # type: ignore[misc]


def test_only_arc_sections_put_arcs_in_filenames() -> None:
    assert all(s.has_arcs for s in SECTIONS if s.arcs_in_filenames)
    assert [s.key for s in SECTIONS if s.arcs_in_filenames] == ["flavour"]


def test_entries_modules_match_the_package() -> None:
    on_disk = {p.stem for p in (DATA / "entries").glob("*.py") if not p.stem.startswith("_")}
    assert {s.entries_module for s in SECTIONS if s.entries_module} == on_disk


# ---------------------------------------------------------------------------
# chapter_path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("short-stories/README.md", "short-stories/index.md"),
        ("short-stories/index.md", "short-stories/index.md"),
        ("  main-story/monarch/x.md ", "main-story/monarch/x.md"),
        ("README.md", "index.md"),
        ("flavour/intro.md", "flavour/intro.md"),
        ("", ""),
        (None, ""),
    ],
)
def test_chapter_path_normalises_readme_once(raw: str | None, expected: str) -> None:
    assert chapter_path({"path": raw}) == expected


def test_chapter_path_without_a_path_key() -> None:
    assert chapter_path({}) == ""


def test_normalise_page_path_leaves_other_readme_like_names() -> None:
    assert normalise_page_path("a/NOT-README.md") == "a/NOT-README.md"


# ---------------------------------------------------------------------------
# Each caller keeps its old answers
# ---------------------------------------------------------------------------


def test_breadcrumb_trails_match_the_old_table() -> None:
    from mdbook_breadcrumb import _TRAILS

    assert {t[0]: t[1:] for t in _TRAILS} == {
        "main-story/": (
            "Main Story",
            "main-story/the-land-of-rathe.md",
            True,
            frozenset({"main-story/the-land-of-rathe.md", "main-story/index.md"}),
        ),
        "short-stories/": ("Short Stories", "short-stories/index.md", True, frozenset({"short-stories/index.md"})),
        "flavour/": ("Flavour Text", "flavour/intro.md", False, frozenset({"flavour/intro.md"})),
        "heroes-of-rathe/": (
            "Heroes of Rathe",
            "heroes-of-rathe/heroes-of-rathe.md",
            False,
            frozenset(
                {
                    "heroes-of-rathe/heroes-of-rathe.md",
                    "heroes-of-rathe/professions-of-rathe.md",
                    "heroes-of-rathe/other.md",
                    "heroes-of-rathe/*-about.md",
                }
            ),
        ),
        "world-of-rathe/": ("World of Rathe", "world-of-rathe/rathe.md", False, frozenset({"world-of-rathe/rathe.md"})),
        "weapons/": ("Weapons", "weapons/armed-to-the-teeth.md", False, frozenset({"weapons/armed-to-the-teeth.md"})),
        "equipment/": (
            "Equipment",
            "equipment/in-the-fires-of-the-forge.md",
            False,
            frozenset({"equipment/in-the-fires-of-the-forge.md"}),
        ),
        "languages/": ("Languages", "languages/intro.md", False, frozenset({"languages/intro.md"})),
        "other-characters/": (
            "Other Characters",
            "other-characters/index.md",
            False,
            frozenset({"other-characters/index.md"}),
        ),
        "summaries/": ("Main Story Summaries", "summaries/index.md", False, frozenset({"summaries/index.md"})),
        "digital-tiles/": ("Digital Tiles", "digital-tiles/index.md", True, frozenset({"digital-tiles/index.md"})),
    }


def test_sets_hub_pages_match_the_old_table() -> None:
    from mdbook_sets_hub import _HUB_PAGES

    assert _HUB_PAGES == {
        "flavour/intro.md": "flavour",
        "short-stories/index.md": "short-stories",
        "main-story/the-land-of-rathe.md": "main-story",
        "digital-tiles/index.md": "digital-tiles",
    }


def test_child_hub_pages_match_the_old_table() -> None:
    from mdbook_child_hub import _HUB_PAGES

    assert _HUB_PAGES == {
        "weapons/armed-to-the-teeth.md": "weapons",
        "equipment/in-the-fires-of-the-forge.md": "equipment",
        "languages/intro.md": "languages",
        "other-characters/index.md": "plain",
        "data/data.md": "plain",
    }


def test_set_index_tables_match_the_old_ones() -> None:
    from mdbook_set_index import _HUB_SKIP, _INDEX_PAGE, _SECTION_LABELS

    assert _INDEX_PAGE == "sets/index.md"
    assert _HUB_SKIP == frozenset(
        {
            "sets/index.md",
            "flavour/intro.md",
            "short-stories/index.md",
            "main-story/the-land-of-rathe.md",
            "digital-tiles/index.md",
        }
    )
    assert _SECTION_LABELS == {
        "main-story": "Main Story",
        "flavour": "Flavour Text",
        "short-stories": "Short Stories",
        "digital-tiles": "Digital Tiles",
    }


_CARD_LABELS = [
    ("main-story", "Main Story"),
    ("short-stories", "Short Story"),
    ("summaries", "Summary"),
    ("world-of-rathe", "World of Rathe"),
    ("flavour", "Flavour Text"),
    ("digital-tiles", "Digital Tile"),
]
_NOT_NARRATIVE = frozenset({"archive", "heroes-of-rathe", "other-characters", "weapons", "equipment"})


def test_browse_tables_match_the_old_ones() -> None:
    from mdbook_browse import _SKIP_TYPES, _TYPE_LABELS

    assert list(_TYPE_LABELS.items()) == _CARD_LABELS
    assert _SKIP_TYPES == _NOT_NARRATIVE


def test_related_tables_match_the_old_ones() -> None:
    from mdbook_related import _STORY_TYPE_LABELS, _STORY_TYPES_SKIP

    assert list(_STORY_TYPE_LABELS.items()) == _CARD_LABELS
    assert _STORY_TYPES_SKIP == _NOT_NARRATIVE


def test_graph_tables_match_the_old_ones() -> None:
    from mdbook_graph import _SKIP_STORY_TYPES, _STORY_TYPE_LABELS

    assert list(_STORY_TYPE_LABELS.items()) == _CARD_LABELS + [
        ("spoilers", "Spoiler"),
        ("languages", "Language"),
        ("sets", "Set"),
    ]
    assert _SKIP_STORY_TYPES == _NOT_NARRATIVE
    # The graph's arc-folder table now lives in arc_of (tests/test_arc_of.py pins each
    # caller's answers); the registry flags it reads still give the old split.
    assert {s.key for s in SECTIONS if s.has_arcs and not s.arcs_in_filenames} == {
        "main-story",
        "short-stories",
        "digital-tiles",
    }
    assert [s.key for s in SECTIONS if s.arcs_in_filenames] == ["flavour"]


def test_story_meta_tables_match_the_old_ones() -> None:
    from mdbook_story_meta import _ARC_SECTIONS, _NO_WORDCOUNT_TYPES

    assert _ARC_SECTIONS == frozenset({"main-story", "short-stories"})
    assert _NO_WORDCOUNT_TYPES == frozenset({"world-of-rathe", "heroes-of-rathe"})


def test_story_roots_match_the_old_table() -> None:
    from create_stories_index import STORY_ROOTS

    assert sorted(STORY_ROOTS) == [
        "archive",
        "digital-tiles",
        "equipment",
        "flavour",
        "heroes-of-rathe",
        "main-story",
        "other-characters",
        "short-stories",
        "summaries",
        "weapons",
        "world-of-rathe",
    ]


def test_entries_sections_match_the_old_table() -> None:
    from entries import SECTIONS as ENTRY_SECTIONS

    assert ENTRY_SECTIONS == {
        "heroes": "heroes-of-rathe",
        "main_story": "main-story",
        "short_stories": "short-stories",
        "other_characters": "other-characters",
        "summaries": "summaries",
        "flavour": "flavour",
        "digital_tiles": "digital-tiles",
        "world_of_rathe": "world-of-rathe",
        "archive": "archive",
        "equipment": "equipment",
        "weapons": "weapons",
    }


# ---------------------------------------------------------------------------
# Import hygiene
# ---------------------------------------------------------------------------


def _top_level_imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def test_mdbook_common_is_stdlib_only() -> None:
    local = {p.stem for p in DATA.glob("*.py")}
    third_party = _top_level_imports(DATA / "mdbook_common.py") - local - set(sys.stdlib_module_names)
    assert third_party == set()
