"""Tests for :mod:`mdbook_graph_link` — the per-page backlink into the Lore Graph."""

from __future__ import annotations

import pytest

from mdbook_graph_link import (
    MARK_END,
    MARK_START,
    STORY_META_END,
    build_link_html,
    inject_into_content,
    relative_graph_href,
    walk_and_process,
)


# ---------------------------------------------------------------------------
# relative_graph_href
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("chapter", "expected"),
    [
        ("graph.md", "graph.html#aria-region"),
        ("browse.md", "graph.html#aria-region"),
        ("world-of-rathe/aria.md", "../graph.html#aria-region"),
        ("main-story/monarch/sworn-to-protect.md", "../../graph.html#aria-region"),
    ],
)
def test_backlink_climbs_to_the_book_root(chapter: str, expected: str) -> None:
    """mdBook renders each chapter at its own depth, so the href cannot be flat."""
    assert relative_graph_href(chapter, "aria-region") == expected


# ---------------------------------------------------------------------------
# build_link_html
# ---------------------------------------------------------------------------


def test_link_names_the_node_it_points_at() -> None:
    html = build_link_html("world-of-rathe/aria.md", {"n": "Aria", "sl": "aria-region"})
    assert 'href="../graph.html#aria-region"' in html
    assert "See Aria in the Lore Graph" in html
    assert "lore-graph-backlink" in html


def test_node_names_are_escaped() -> None:
    """Names come from the lore CSVs and go straight into markup."""
    html = build_link_html("intro.md", {"n": 'Rhinar "The <Beast>"', "sl": "rhinar"})
    assert "<Beast>" not in html
    assert "&lt;Beast&gt;" in html
    assert "&quot;" in html


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------


def test_link_lands_directly_under_the_share_sheet() -> None:
    """The share sheet sits just below the H1, and the backlink belongs with it."""
    content = f"# Aria\n\n{STORY_META_END}\n\nBody text.\n\nMore body.\n"
    out = inject_into_content(content, "<p>link</p>")
    assert out.index(STORY_META_END) < out.index("<p>link</p>") < out.index("Body text.")


def test_link_falls_back_to_the_end_when_there_is_no_share_sheet() -> None:
    content = "# Plain Page\n\nBody text.\n"
    out = inject_into_content(content, "<p>link</p>")
    assert out.index("Body text.") < out.index("<p>link</p>")


def test_a_stale_link_lower_down_is_moved_not_duplicated() -> None:
    """Guards the upgrade path from the first placement, above Related Lore."""
    content = f"# Aria\n\n{STORY_META_END}\n\nBody.\n\n" f"{MARK_START}\n<p>old</p>\n{MARK_END}\n\nRelated.\n"
    out = inject_into_content(content, "<p>new</p>")
    assert out.count(MARK_START) == 1
    assert "<p>old</p>" not in out
    assert out.index("<p>new</p>") < out.index("Body.")
    assert "Related." in out


def test_share_sheet_placement_is_idempotent() -> None:
    content = f"# Aria\n\n{STORY_META_END}\n\nBody.\n"
    once = inject_into_content(content, "<p>link</p>")
    twice = inject_into_content(once, "<p>link</p>")
    assert once == twice


def test_inject_replaces_a_stale_block() -> None:
    content = f"# Aria\n\nBody.\n\n{MARK_START}\nold link\n{MARK_END}\n"
    out = inject_into_content(content, "<p>fresh</p>")
    assert "old link" not in out
    assert "<p>fresh</p>" in out
    assert out.count(MARK_START) == 1


def test_inject_appends_when_absent() -> None:
    out = inject_into_content("# Aria\n\nBody.\n", "<p>fresh</p>")
    assert out.startswith("# Aria")
    assert "Body." in out
    assert MARK_START in out and MARK_END in out


def test_repeated_injection_is_idempotent() -> None:
    """Every build re-runs the preprocessor; links must not stack up."""
    once = inject_into_content("# Aria\n", "<p>a</p>")
    twice = inject_into_content(once, "<p>a</p>")
    assert once == twice
    assert twice.count(MARK_START) == 1


# ---------------------------------------------------------------------------
# walk_and_process
# ---------------------------------------------------------------------------


def _book() -> dict:
    return {
        "items": [
            {"Chapter": {"path": "graph.md", "content": "# Lore Graph\n", "sub_items": []}},
            {"Chapter": {"path": "browse.md", "content": "# Browse\n", "sub_items": []}},
            {
                "Chapter": {
                    "path": "world-of-rathe/aria.md",
                    "content": "# Aria\n",
                    "sub_items": [
                        {
                            "Chapter": {
                                "path": "heroes-of-rathe/dorinthea-about.md",
                                "content": "# Dorinthea\n",
                                "sub_items": [],
                            }
                        }
                    ],
                }
            },
        ]
    }


TARGETS = {
    "graph.md": {"n": "Lore Graph", "sl": "lore-graph"},
    "world-of-rathe/aria.md": {"n": "Aria", "sl": "aria-region"},
    "heroes-of-rathe/dorinthea-about.md": {"n": "Dorinthea", "sl": "dorinthea"},
}


def test_only_pages_with_a_node_get_a_backlink() -> None:
    book = _book()
    walk_and_process(book["items"], TARGETS)
    assert MARK_START not in book["items"][1]["Chapter"]["content"], "browse.md has no node"
    assert "aria-region" in book["items"][2]["Chapter"]["content"]


def test_the_graph_page_never_links_to_itself() -> None:
    book = _book()
    walk_and_process(book["items"], TARGETS)
    assert MARK_START not in book["items"][0]["Chapter"]["content"]


def test_nested_chapters_are_reached() -> None:
    book = _book()
    walk_and_process(book["items"], TARGETS)
    nested = book["items"][2]["Chapter"]["sub_items"][0]["Chapter"]["content"]
    assert "../graph.html#dorinthea" in nested


def test_an_empty_target_map_changes_nothing() -> None:
    book = _book()
    before = [i["Chapter"]["content"] for i in book["items"]]
    walk_and_process(book["items"], {})
    assert [i["Chapter"]["content"] for i in book["items"]] == before
