"""Tests for ``src/flavour/get_flavour.py``, the flavour page generator.

Every test runs against a miniature repo built in ``tmp_path``: a ``sets.csv``,
a ``story-arcs.csv``, a flavour directory and a ``card-flattened.json`` in the
upstream shape. The module's path constants are monkeypatched to point at it,
so nothing under ``src/`` is read or written.

The fixture sets are dated OLD (2020) < NEW (2022) < LAT (2024), and the page
under test is NEW's, ``new-set.md``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import get_flavour

SETS_CSV = """\
# AUTO-GENERATED FILE — do not edit by hand.
SetId|SetTypeId|SetName|InitialReleaseDate
OLD|TY1|Old Set|2020-01-01T00:00:00.000Z
NEW|TY1|New Set|2022-06-01T00:00:00.000Z
LAT|TY1|Later Set|2024-01-01T00:00:00.000Z
"""

STORY_ARCS_CSV = """\
# Hand-maintained mapping from arc folder/file slug → set metadata.
Slug|SetId|DisplayName|ImageLink|SortDate
old-set|OLD|||
new-set|NEW|||
later-set|LAT|||
interlude||Interlude||2021-03-01
"""

PAGES = {
    "old-set.md": "# Old Set\n\n#### Ancient - (OLD001)\nReprinted line.\n",
    "later-set.md": "# Later Set\n\n#### Future - (LAT001)\nLater line.\n",
    "interlude.md": "# Interlude\n\n#### Pause - (INT001)\nInterlude line.\n",
    # No story-arcs row, so it cannot be dated and must suppress nothing.
    "mystery.md": "# Mystery\n\n#### Riddle - (MYS001)\nMystery line.\n",
    # Its worked example looks like a block but is not published flavour text.
    "README.md": "# Flavour\n\n```\n#### Card Name - (XXX000)\nReadme line.\n```\n",
    # The page being regenerated: two protected blocks, one already-published line.
    "new-set.md": (
        "# New Set\n\n"
        "#### Astral - (NEW060)\n"
        '<!-- keep: card prints "Quazor" -->\n'
        "Quazor speaks.\n\n"
        "#### Cycle Strike - (NEW010/011/012)\n"
        "Strike thrice.\n\n"
        "#### Lost Card - (NEW070)\n"
        "<!-- keep: upstream has no flavour -->\n"
        "Only on the card.\n"
    ),
}

CARDS = [
    {"set_id": "NEW", "id": "NEW001", "name": "Zephyr", "flavor_text": "“Wind,” she said…"},
    # A pitch cycle sharing one line, listed out of order, one with stray whitespace.
    {"set_id": "NEW", "id": "NEW012", "name": "Cycle Strike", "flavor_text": "Strike thrice."},
    {"set_id": "NEW", "id": "NEW010", "name": "Cycle Strike", "flavor_text": "Strike thrice."},
    {"set_id": "NEW", "id": "NEW011", "name": "Cycle Strike", "flavor_text": "Strike  thrice."},
    # One quote split across a cycle: separate entries.
    {"set_id": "NEW", "id": "NEW021", "name": "Wax On", "flavor_text": "Wax off."},
    {"set_id": "NEW", "id": "NEW020", "name": "Wax On", "flavor_text": "Wax on."},
    {"set_id": "NEW", "id": "NEW030", "name": "Old Echo", "flavor_text": "Reprinted line."},
    {"set_id": "NEW", "id": "NEW040", "name": "Forward Echo", "flavor_text": "Later line."},
    {"set_id": "NEW", "id": "NEW050", "name": "Blank", "flavor_text": ""},
    {"set_id": "NEW", "id": "NEW051", "name": "Null", "flavor_text": None},
    {"set_id": "NEW", "id": "NEW060", "name": "Astral", "flavor_text": "Quazar speaks."},
    {"set_id": "NEW", "id": "NEW080", "name": "Interlude Echo", "flavor_text": "Interlude line."},
    {"set_id": "NEW", "id": "NEW090", "name": "Mystery Echo", "flavor_text": "Mystery line."},
    {"set_id": "NEWER", "id": "NEWER01", "name": "Wrong Set", "flavor_text": "Not this set."},
    {"set_id": "OLD", "id": "OLD001", "name": "Ancient", "flavor_text": "Reprinted line."},
]

EXPECTED_PAGE = """\
# New Set

#### Astral - (NEW060)
<!-- keep: card prints "Quazor" -->
Quazor speaks.

#### Cycle Strike - (NEW010/011/012)
Strike thrice.

#### Forward Echo - (NEW040)
Later line.

#### Lost Card - (NEW070)
<!-- keep: upstream has no flavour -->
Only on the card.

#### Mystery Echo - (NEW090)
Mystery line.

#### Wax On - (NEW020)
Wax on.

#### Wax On - (NEW021)
Wax off.

#### Zephyr - (NEW001)
"Wind," she said...
"""


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build the miniature repo and point ``get_flavour`` at it."""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    (csv_dir / "sets.csv").write_text(SETS_CSV, encoding="utf-8")
    (csv_dir / "story-arcs.csv").write_text(STORY_ARCS_CSV, encoding="utf-8")
    flavour = tmp_path / "flavour"
    flavour.mkdir()
    for name, text in PAGES.items():
        (flavour / name).write_text(text, encoding="utf-8")
    (tmp_path / "card-flattened.json").write_text(json.dumps(CARDS), encoding="utf-8")

    monkeypatch.setattr(get_flavour, "_FLAVOUR_DIR", flavour)
    monkeypatch.setattr(get_flavour, "_SETS_CSV", csv_dir / "sets.csv")
    monkeypatch.setattr(get_flavour, "_STORY_ARCS_CSV", csv_dir / "story-arcs.csv")
    return tmp_path


def _generate(repo: Path, **kwargs):
    out = repo / "flavour" / "new-set.md"
    result = get_flavour.create_flavour_md("NEW", str(repo / "card-flattened.json"), str(out), **kwargs)
    return out.read_text(encoding="utf-8"), result


# --- create_flavour_md: the written page -------------------------------------


def test_page_is_written_in_repo_format(repo: Path) -> None:
    page, _ = _generate(repo)
    assert page == EXPECTED_PAGE


def test_regenerating_a_page_is_idempotent(repo: Path) -> None:
    first, _ = _generate(repo)
    second, _ = _generate(repo)
    assert second == first


def test_title_overrides_the_set_name(repo: Path) -> None:
    page, _ = _generate(repo, title="Custom Heading")
    assert page.startswith("# Custom Heading\n\n#### Astral - (NEW060)\n")


def test_drop_reprints_false_keeps_earlier_published_lines(repo: Path) -> None:
    page, _ = _generate(repo, drop_reprints=False)
    assert "#### Old Echo - (NEW030)\nReprinted line.\n" in page
    assert "#### Interlude Echo - (NEW080)\nInterlude line.\n" in page


def test_a_scratch_copy_with_the_page_name_excludes_the_published_page(repo: Path) -> None:
    scratch = repo / "scratch"
    scratch.mkdir()
    out = scratch / "new-set.md"
    out.write_text(PAGES["new-set.md"], encoding="utf-8")
    get_flavour.create_flavour_md("NEW", str(repo / "card-flattened.json"), str(out))
    assert out.read_text(encoding="utf-8") == EXPECTED_PAGE


# --- set_name / release_date ---------------------------------------------------


def test_set_name_reads_sets_csv(repo: Path) -> None:
    assert get_flavour.set_name("LAT") == "Later Set"


def test_set_name_raises_for_an_unknown_set(repo: Path) -> None:
    with pytest.raises(KeyError, match="create_sets_csv.py"):
        get_flavour.set_name("XYZ")


def test_release_date_is_the_iso_day(repo: Path) -> None:
    assert get_flavour.release_date("NEW") == "2022-06-01"


def test_release_date_of_an_unknown_set_sorts_last(repo: Path) -> None:
    assert get_flavour.release_date("XYZ") == "9999-99-99"


# --- published_flavour_text ----------------------------------------------------


def test_published_flavour_text_maps_each_line_to_its_dated_page(repo: Path) -> None:
    assert get_flavour.published_flavour_text() == {
        "Reprinted line.": ("old-set", "2020-01-01"),
        "Later line.": ("later-set", "2024-01-01"),
        "Interlude line.": ("interlude", "2021-03-01"),
        "Mystery line.": ("mystery", "9999-99-99"),
        "Quazor speaks.": ("new-set", "2022-06-01"),
        "Strike thrice.": ("new-set", "2022-06-01"),
        "Only on the card.": ("new-set", "2022-06-01"),
    }


def test_published_flavour_text_excludes_the_named_page(repo: Path) -> None:
    published = get_flavour.published_flavour_text(exclude="new-set.md")
    assert "Strike thrice." not in published
    assert "Reprinted line." in published


def test_published_flavour_text_keeps_the_earliest_origin(repo: Path) -> None:
    (repo / "flavour" / "later-set.md").write_text(
        "# Later Set\n\n#### Again - (LAT002)\nReprinted line.\n", encoding="utf-8"
    )
    assert get_flavour.published_flavour_text()["Reprinted line."] == ("old-set", "2020-01-01")


# --- create_flavour_md: the returned rows --------------------------------------


def test_returns_kept_rows_as_dicts_in_page_order(repo: Path) -> None:
    _, (kept, _) = _generate(repo)
    assert kept == [
        {"set_id": "NEW", "id": "NEW060", "ids": ["NEW060"], "name": "Astral", "flavor_text": "Quazar speaks."},
        {
            "set_id": "NEW",
            "id": "NEW010/011/012",
            "ids": ["NEW010", "NEW011", "NEW012"],
            "name": "Cycle Strike",
            "flavor_text": "Strike thrice.",
        },
        {"set_id": "NEW", "id": "NEW040", "ids": ["NEW040"], "name": "Forward Echo", "flavor_text": "Later line."},
        {"set_id": "NEW", "id": "NEW090", "ids": ["NEW090"], "name": "Mystery Echo", "flavor_text": "Mystery line."},
        {"set_id": "NEW", "id": "NEW020", "ids": ["NEW020"], "name": "Wax On", "flavor_text": "Wax on."},
        {"set_id": "NEW", "id": "NEW021", "ids": ["NEW021"], "name": "Wax On", "flavor_text": "Wax off."},
        {"set_id": "NEW", "id": "NEW001", "ids": ["NEW001"], "name": "Zephyr", "flavor_text": '"Wind," she said...'},
    ]


def test_returns_dropped_rows_with_the_page_that_published_them_first(repo: Path) -> None:
    _, (_, dropped) = _generate(repo)
    assert dropped == [
        {
            "set_id": "NEW",
            "id": "NEW080",
            "ids": ["NEW080"],
            "name": "Interlude Echo",
            "flavor_text": "Interlude line.",
            "reprint_of": "interlude",
        },
        {
            "set_id": "NEW",
            "id": "NEW030",
            "ids": ["NEW030"],
            "name": "Old Echo",
            "flavor_text": "Reprinted line.",
            "reprint_of": "old-set",
        },
    ]


def test_nothing_is_dropped_when_drop_reprints_is_false(repo: Path) -> None:
    _, (kept, dropped) = _generate(repo, drop_reprints=False)
    assert dropped == []
    assert [row["id"] for row in kept] == [
        "NEW060",
        "NEW010/011/012",
        "NEW040",
        "NEW080",
        "NEW090",
        "NEW030",
        "NEW020",
        "NEW021",
        "NEW001",
    ]


# --- dependencies ----------------------------------------------------------------


def test_module_imports_without_numpy_or_pandas() -> None:
    """The generator is stdlib-only, like every other script in the repo."""
    script = (
        "import sys; sys.modules['numpy'] = None; sys.modules['pandas'] = None; "
        f"sys.path.insert(0, {str(Path(get_flavour.__file__).parent)!r}); import get_flavour"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
