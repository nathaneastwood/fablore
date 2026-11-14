"""``mdbook_common.arc_of`` and what each of its callers makes of a page's arc.

Six preprocessors used to work out "which arc is this page in" from the path
themselves, with rules that had drifted apart. They now share
:func:`mdbook_common.arc_of` and keep their differences as explicit filters.

The caller table below was taken from the pre-``arc_of`` code over every chapter
path in ``SUMMARY.md`` (one row per path shape found there), plus synthetic
shapes the book does not contain yet (deeper folders, a flat short story) so
the filters that only bite on those stay pinned too. A row changing here means
a page's set card, hub listing, story card, breadcrumb or graph cluster moved.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

import pytest

import mdbook_breadcrumb
import mdbook_graph
import mdbook_set_index
import mdbook_set_meta
import mdbook_sets_hub
import mdbook_story_meta
from mdbook_common import SECTION_BY_KEY, arc_of

SRC = Path(__file__).resolve().parent.parent / "src"


# ---------------------------------------------------------------------------
# arc_of itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        # Folder-per-arc sections: the arc is the folder one level down, at any depth.
        ("main-story/monarch/sworn-to-protect.md", ("main-story", "monarch")),
        ("short-stories/outsiders/aiming-high.md", ("short-stories", "outsiders")),
        ("digital-tiles/monarch/monarch.md", ("digital-tiles", "monarch")),
        ("main-story/monarch/deeper/page.md", ("main-story", "monarch")),
        # An arc folder's own landing page is still in that arc, in either spelling.
        ("short-stories/roll-of-honour/index.md", ("short-stories", "roll-of-honour")),
        ("short-stories/roll-of-honour/README.md", ("short-stories", "roll-of-honour")),
        # Flavour: the arc is the filename, so only direct children count.
        ("flavour/monarch.md", ("flavour", "monarch")),
        ("flavour/intro.md", ("flavour", "intro")),
        ("flavour/sub/page.md", None),
        # A page directly under a folder-per-arc section is in no arc.
        ("main-story/the-land-of-rathe.md", None),
        ("short-stories/index.md", None),
        ("short-stories/kassais-diary.md", None),
        ("digital-tiles/index.md", None),
        # Sections without arcs, and things that are not section pages.
        ("summaries/war-of-the-monarch-pt-1.md", None),
        ("world-of-rathe/rathe.md", None),
        ("heroes-of-rathe/azalea-about.md", None),
        ("archive/world-of-rathe/aria/aria.md", None),
        ("browse.md", None),
        ("", None),
    ],
)
def test_arc_of(path: str, expected: tuple[str, str] | None) -> None:
    assert arc_of(path) == expected


def test_arc_of_names_a_real_arc_for_every_chapter_in_the_book() -> None:
    """Every arc ``arc_of`` reports for a chapter is a folder (or flavour page) that exists."""
    paths = set(re.findall(r"\]\(([^)]+\.md)\)", (SRC / "SUMMARY.md").read_text(encoding="utf-8")))
    seen = 0
    for path in paths:
        arc = arc_of(path)
        if arc is None:
            continue
        seen += 1
        section, slug = arc
        assert SECTION_BY_KEY[section].has_arcs
        if SECTION_BY_KEY[section].arcs_in_filenames:
            assert (SRC / section / f"{slug}.md").is_file(), path
        else:
            assert (SRC / section / slug).is_dir(), path
    assert seen > 100


# ---------------------------------------------------------------------------
# Each caller's answer, pinned
# ---------------------------------------------------------------------------


def _book(path: str) -> list[dict]:
    return [{"Chapter": {"name": "Page", "path": path, "content": "# Page\n", "sub_items": []}}]


def _graph(path: str) -> str | None:
    return mdbook_graph.arc_slug_for_story(path) or None


class _AnyArc(dict):
    """A set-metadata map that knows every arc, so the walk shows which slug it looked up."""

    def __contains__(self, slug: object) -> bool:
        return True

    def __missing__(self, slug: str) -> dict:
        return {"slug": slug}


def _set_meta(path: str, monkeypatch: pytest.MonkeyPatch) -> str | None:
    monkeypatch.setattr(mdbook_set_meta, "_build_set_meta_html", lambda meta: f"<SLUG {meta['slug']}>")
    items = _book(path)
    mdbook_set_meta._walk_sections(items, _AnyArc())
    m = re.search(r"<SLUG ([^>]*)>", items[0]["Chapter"]["content"])
    return m.group(1) if m else None


def _set_index(path: str) -> tuple[str, str] | None:
    content = {k: OrderedDict() for k in mdbook_set_index._SECTION_ORDER}
    mdbook_set_index._collect(_book(path), content)
    found = [(section, slug) for section, by_arc in content.items() for slug in by_arc]
    assert len(found) <= 1
    return found[0] if found else None


def _sets_hub(path: str) -> tuple[str, str] | None:
    flavour: list = []
    story_arcs = {k: OrderedDict() for k in ("main-story", "short-stories", "digital-tiles")}
    mdbook_sets_hub._collect(_book(path), flavour, story_arcs)
    found = [(section, slug) for section, by_arc in story_arcs.items() for slug in by_arc]
    # The flavour hub lists pages, not arcs: each card's slug is read off its path later.
    found += [("flavour", "*")] * len(flavour)
    assert len(found) <= 1
    return found[0] if found else None


def _story_meta(path: str) -> str | None:
    return mdbook_story_meta._arc_of(path)


def _breadcrumb(path: str) -> str | None:
    """The arc crumb's label (``Section › Arc › Page``), or ``None`` for a trail without one."""
    ch = _book(path)[0]["Chapter"]
    mdbook_breadcrumb._process_chapter(ch, {}, {})
    crumbs = re.findall(r"<li>(?:<a [^>]*>|<span[^>]*>)([^<]*)<", ch["content"])
    return crumbs[1] if len(crumbs) == 3 else None


_MS = ("main-story", "monarch")

# path, graph, set_meta, set_index, sets_hub, story_meta, breadcrumb arc crumb
_CALLERS = [
    # A story in an arc folder: every caller but set_meta agrees.
    ("main-story/monarch/sworn-to-protect.md", "monarch", None, _MS, _MS, "monarch", "Monarch"),
    (
        "short-stories/outsiders/aiming-high.md",
        "outsiders",
        None,
        ("short-stories", "outsiders"),
        ("short-stories", "outsiders"),
        "outsiders",
        "Outsiders",
    ),
    # Digital tiles: story_meta gives them no arc (no "Part n of m" row).
    (
        "digital-tiles/monarch/monarch.md",
        "monarch",
        "monarch",
        ("digital-tiles", "monarch"),
        ("digital-tiles", "monarch"),
        None,
        "Monarch",
    ),
    # Flavour: story_meta gives no arc; the breadcrumb has no arc crumb (the page is the arc).
    ("flavour/monarch.md", "monarch", "monarch", ("flavour", "monarch"), ("flavour", "*"), None, None),
    # The flavour hub: only the graph treats it as an arc ("intro", which maps to no set).
    ("flavour/intro.md", "intro", None, None, None, None, None),
    # An arc folder's landing page: story_meta alone leaves it out.
    (
        "short-stories/roll-of-honour/index.md",
        "roll-of-honour",
        None,
        ("short-stories", "roll-of-honour"),
        ("short-stories", "roll-of-honour"),
        None,
        "Roll Of Honour",
    ),
    (
        "short-stories/roll-of-honour/README.md",
        "roll-of-honour",
        None,
        ("short-stories", "roll-of-honour"),
        ("short-stories", "roll-of-honour"),
        None,
        "Roll Of Honour",
    ),
    # Deeper than one arc folder: set_meta (digital tiles) and story_meta stop at depth 3.
    ("main-story/monarch/deeper/page.md", "monarch", None, _MS, _MS, None, "Monarch"),
    (
        "digital-tiles/monarch/deeper/page.md",
        "monarch",
        None,
        ("digital-tiles", "monarch"),
        ("digital-tiles", "monarch"),
        None,
        "Monarch",
    ),
    ("flavour/sub/page.md", None, None, None, None, None, None),
    # A flat short story: sets_hub alone makes it its own pseudo-arc.
    ("short-stories/kassais-diary.md", None, None, None, ("short-stories", "kassais-diary"), None, None),
    # Section hubs and pages outside the arc sections: no arc anywhere.
    ("main-story/the-land-of-rathe.md", None, None, None, None, None, None),
    ("short-stories/index.md", None, None, None, None, None, None),
    ("digital-tiles/index.md", None, None, None, None, None, None),
    ("summaries/war-of-the-monarch-pt-1.md", None, None, None, None, None, None),
    ("world-of-rathe/rathe.md", None, None, None, None, None, None),
    ("heroes-of-rathe/azalea-about.md", None, None, None, None, None, None),
    ("archive/world-of-rathe/aria/aria.md", None, None, None, None, None, None),
]


@pytest.mark.parametrize(
    ("path", "graph", "set_meta", "set_index", "sets_hub", "story_meta", "breadcrumb"),
    _CALLERS,
    ids=[row[0] for row in _CALLERS],
)
def test_each_caller_keeps_its_answer(
    path: str,
    graph: str | None,
    set_meta: str | None,
    set_index: tuple[str, str] | None,
    sets_hub: tuple[str, str] | None,
    story_meta: str | None,
    breadcrumb: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert {
        "graph": _graph(path),
        "set_meta": _set_meta(path, monkeypatch),
        "set_index": _set_index(path),
        "sets_hub": _sets_hub(path),
        "story_meta": _story_meta(path),
        "breadcrumb": _breadcrumb(path),
    } == {
        "graph": graph,
        "set_meta": set_meta,
        "set_index": set_index,
        "sets_hub": sets_hub,
        "story_meta": story_meta,
        "breadcrumb": breadcrumb,
    }
