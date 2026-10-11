"""Tests for ``mdbook_story_meta`` mdBook preprocessor helpers."""

from __future__ import annotations

from mdbook_story_meta import (
    _NO_WORDCOUNT_TYPES,
    GRAPH_SLOT,
    _arc_of,
    _arc_positions,
    _build_context_html,
    _build_meta_html,
    _order_heroes_by_mentions,
    _build_share_html,
    _inject_after_heading,
    _process_chapter,
)


# ---------------------------------------------------------------------------
# _build_share_html
# ---------------------------------------------------------------------------


def test_share_html_contains_all_platforms() -> None:
    html = _build_share_html()
    assert "story-share-facebook" in html
    assert "story-share-twitter" in html
    assert "story-share-bluesky" in html
    assert "story-share-whatsapp" in html
    assert "story-share-copy" in html


def test_share_html_no_story_type_omits_attribute() -> None:
    html = _build_share_html()
    assert "data-story-type" not in html


def test_share_html_story_type_attribute() -> None:
    html = _build_share_html("main-story")
    assert 'data-story-type="main-story"' in html


def test_share_html_story_type_escaped() -> None:
    html = _build_share_html("<script>")
    # The attribute value must be HTML-escaped; check it appears correctly in the div tag
    assert 'data-story-type="&lt;script&gt;"' in html


def test_share_html_contains_clipboard_script() -> None:
    html = _build_share_html()
    assert "navigator.clipboard" in html


# ---------------------------------------------------------------------------
# _build_meta_html — word count suppression
# ---------------------------------------------------------------------------


def test_no_wordcount_types_contains_expected() -> None:
    assert "world-of-rathe" in _NO_WORDCOUNT_TYPES
    assert "heroes-of-rathe" in _NO_WORDCOUNT_TYPES


def test_meta_html_includes_word_count_by_default() -> None:
    html = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=500,
    )
    assert "500" in html
    assert "far fa-clock" in html


def test_meta_html_suppresses_word_count_when_flag_false() -> None:
    html = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=500,
        show_word_count=False,
    )
    # far fa-clock is the word-count icon; its absence confirms suppression
    # (avoid asserting on "500" directly — that digit appears in the BlueSky SVG path)
    assert "far fa-clock" not in html
    assert "words" not in html


def test_meta_html_share_always_present() -> None:
    # Even with no metadata fields, share buttons are injected
    html = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=0,
    )
    assert "story-share" in html


def test_meta_html_no_story_meta_div_when_no_items() -> None:
    html = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=0,
    )
    assert 'class="story-meta"' not in html


def test_meta_html_story_type_passed_to_share() -> None:
    html = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="",
        word_count=0,
        story_type="main-story",
    )
    assert 'data-story-type="main-story"' in html


def test_meta_html_authors_rendered() -> None:
    html = _build_meta_html(
        authors="Jane Doe",
        artists="",
        publication_date="",
        source_link="",
        word_count=0,
    )
    assert "Jane Doe" in html
    assert "fa-pencil" in html


def test_meta_html_authors_escaped() -> None:
    html = _build_meta_html(
        authors="<b>Bad</b>",
        artists="",
        publication_date="",
        source_link="",
        word_count=0,
    )
    assert "<b>" not in html
    assert "&lt;b&gt;" in html


# ---------------------------------------------------------------------------
# _process_chapter — world-of-rathe / heroes-of-rathe skip word count
# ---------------------------------------------------------------------------


def _make_row(story_type: str, **kwargs: str) -> dict[str, str]:
    base = {
        "StoryId": "ST123",
        "StoryKey": "test/page.md",
        "StoryType": story_type,
        "Title": "Test",
        "Authors": "",
        "Artists": "",
        "SourceLink": "",
        "PublicationDate": "",
        "ThumbnailImageLink": "",
    }
    return {**base, **kwargs}


def test_process_chapter_world_of_rathe_no_word_count() -> None:
    content = "# Hub\n\nSome text " * 30  # enough words to normally show count
    row = _make_row("world-of-rathe")
    out = _process_chapter(content, row)
    assert "fa-clock" not in out


def test_process_chapter_heroes_of_rathe_no_word_count() -> None:
    content = "# Hero\n\nSome text " * 30
    row = _make_row("heroes-of-rathe")
    out = _process_chapter(content, row)
    assert "fa-clock" not in out


def test_process_chapter_main_story_has_word_count() -> None:
    content = "# Story\n\nSome text " * 30
    row = _make_row("main-story")
    out = _process_chapter(content, row)
    assert "far fa-clock" in out


def test_process_chapter_injects_after_heading() -> None:
    content = "# My Story\n\nParagraph one.\n"
    row = _make_row("main-story")
    out = _process_chapter(content, row)
    # Meta block must appear before the paragraph
    assert out.index("story-share") < out.index("Paragraph one")


def test_process_chapter_idempotent() -> None:
    content = "# My Story\n\nParagraph.\n"
    row = _make_row("main-story")
    once = _process_chapter(content, row)
    twice = _process_chapter(once, row)
    # Running twice should not duplicate the block
    assert twice.count("story-share-facebook") == once.count("story-share-facebook")


# ---------------------------------------------------------------------------
# _inject_after_heading
# ---------------------------------------------------------------------------


def test_inject_after_heading_inserts_after_h1() -> None:
    out = _inject_after_heading("# Title\n\nBody.", "<p>meta</p>")
    assert out.index("# Title") < out.index("<p>meta</p>") < out.index("Body.")


def test_inject_after_heading_replaces_existing_block() -> None:
    existing = (
        "# Title\n\n" "<!-- fablore-story-meta:start -->\n<p>OLD</p>\n<!-- fablore-story-meta:end -->\n\n" "Body."
    )
    out = _inject_after_heading(existing, "<p>NEW</p>")
    assert "OLD" not in out
    assert "<p>NEW</p>" in out
    assert "Body." in out


def test_inject_after_heading_no_heading_prepends() -> None:
    out = _inject_after_heading("Just a paragraph.", "<p>meta</p>")
    assert out.startswith("<!-- fablore-story-meta:start -->")


# ---------------------------------------------------------------------------
# FA6 icon prefix — prevents mdBook build warnings
#
# mdBook 0.5.3 converts <i class="..."> elements to inline SVG. Using the
# bare "fa" class (FA4 syntax) defaults to FA6 "regular" and warns for icons
# that only exist in "solid" or "brands". All icons must carry an explicit
# FA6 prefix: fas (solid), fab (brands), or far (regular).
# ---------------------------------------------------------------------------


def test_share_html_uses_fa6_brands_prefix_for_facebook() -> None:
    html = _build_share_html()
    assert 'class="fab fa-facebook"' in html
    assert 'class="fa fa-facebook"' not in html


def test_share_html_uses_fa6_brands_prefix_for_whatsapp() -> None:
    html = _build_share_html()
    assert 'class="fab fa-whatsapp"' in html
    assert 'class="fa fa-whatsapp"' not in html


def test_share_html_uses_fa6_solid_prefix_for_link() -> None:
    html = _build_share_html()
    assert 'class="fas fa-link"' in html
    assert 'class="fa fa-link"' not in html


def test_meta_html_no_bare_fa_prefix() -> None:
    """No icon in story-meta output should use the bare 'fa' FA4 class prefix."""
    html = _build_meta_html(
        authors="Author",
        artists="Artist",
        publication_date="2024-01-01",
        source_link="https://example.com",
        word_count=1000,
        show_word_count=True,
        story_type="main-story",
    )
    import re

    bare_fa = re.findall(r'class="fa fa-', html)
    assert bare_fa == [], f"Found bare FA4 'fa' prefix: {bare_fa}"


# ---------------------------------------------------------------------------
# Story card: context row, links row
# ---------------------------------------------------------------------------


def _chapter(path: str, sub_items: list | None = None) -> dict:
    return {"Chapter": {"path": path, "content": "", "sub_items": sub_items or []}}


def test_arc_of_only_matches_story_chapters_in_arc_folders() -> None:
    assert _arc_of("main-story/arcane-rising/cards-on-the-table.md") == "arcane-rising"
    assert _arc_of("short-stories/outsiders/aiming-high.md") == "outsiders"
    assert _arc_of("short-stories/index.md") is None
    assert _arc_of("short-stories/roll-of-honour/index.md") is None
    assert _arc_of("heroes-of-rathe/azalea-about.md") is None


def test_arc_positions_count_in_book_order_across_nesting() -> None:
    items = [
        _chapter(
            "main-story/the-land-of-rathe.md",
            [
                _chapter("main-story/arc-a/one.md"),
                _chapter("main-story/arc-b/other.md"),
                _chapter("main-story/arc-a/two.md"),
            ],
        )
    ]
    positions = _arc_positions(items)
    assert positions["main-story/arc-a/one.md"] == (1, 2)
    assert positions["main-story/arc-a/two.md"] == (2, 2)
    assert positions["main-story/arc-b/other.md"] == (1, 1)
    assert "main-story/the-land-of-rathe.md" not in positions


def test_arc_positions_count_each_section_folder_separately() -> None:
    """main-story/outsiders and short-stories/outsiders share an arc slug only."""
    items = [
        _chapter("main-story/outsiders/one.md"),
        _chapter("main-story/outsiders/two.md"),
        _chapter("short-stories/outsiders/a.md"),
    ]
    positions = _arc_positions(items)
    assert positions["main-story/outsiders/two.md"] == (2, 2)
    assert positions["short-stories/outsiders/a.md"] == (1, 1)


def test_heroes_ordered_by_mentions_then_first_appearance() -> None:
    heroes = [("Azalea", None), ("Kano", None), ("Dash", None)]
    text = "Kano spoke. Dash ran. Azalea aimed. Azalea fired. Dash fell. Azalea won."
    assert [n for n, _ in _order_heroes_by_mentions(heroes, text)] == ["Azalea", "Dash", "Kano"]


def test_context_row_names_arc_part_and_linked_hero() -> None:
    out = _build_context_html(
        "main-story/arcane-rising/cards-on-the-table.md",
        arc_name="Arcane Rising",
        position=(3, 11),
        heroes=[("Azalea", "heroes-of-rathe/azalea-about.md")],
    )
    assert "Arcane Rising" in out
    assert "Part 3 of 11" in out
    assert '<a href="../../heroes-of-rathe/azalea-about.html">Azalea</a>' in out


def test_context_row_omits_part_for_a_single_story_arc() -> None:
    out = _build_context_html("main-story/interlude/x.md", arc_name="Interlude", position=(1, 1), heroes=[])
    assert "Part" not in out


def test_context_row_caps_heroes_and_counts_the_rest() -> None:
    heroes = [(n, None) for n in ("A", "B", "C", "D", "E")]
    out = _build_context_html("main-story/arc/x.md", arc_name="", position=None, heroes=heroes)
    assert "A, B, C" in out
    assert "+2 more" in out
    assert 'title="D, E"' in out


def test_context_row_names_a_fourth_hero_rather_than_plus_one() -> None:
    heroes = [(n, None) for n in ("A", "B", "C", "D")]
    out = _build_context_html("main-story/arc/x.md", arc_name="", position=None, heroes=heroes)
    assert "A, B, C, D" in out
    assert "more" not in out


def test_card_links_row_holds_source_and_graph_slot() -> None:
    out = _build_meta_html(
        authors="",
        artists="",
        publication_date="",
        source_link="https://example.com/story",
        word_count=0,
    )
    assert '<p class="story-card-links"><a class="story-card-source" href="https://example.com/story"' in out
    assert f"Original article</a>{GRAPH_SLOT}</p>" in out


def test_card_has_no_blank_lines_inside() -> None:
    """Markdown ends an HTML block at a blank line; the card must stay one block."""
    out = _build_meta_html(
        authors="A",
        artists="B",
        publication_date="2024-01-01",
        source_link="https://example.com",
        word_count=500,
        context_html="<span>Arc</span>",
    )
    card = out[out.index('<div class="story-card">') : out.index("</div>\n\n") + 6]
    assert "\n\n" not in card


def test_process_chapter_reference_pages_get_no_context_row() -> None:
    out = _process_chapter("# Hero\n\nText.\n", _make_row("heroes-of-rathe"))
    assert "story-card-context" not in out


def test_heroes_tied_on_mentions_keep_first_appearance() -> None:
    heroes = [("Azalea", None), ("Dash", None)]
    text = "Dash ran. Azalea aimed. Azalea fired. Dash fell."
    assert [n for n, _ in _order_heroes_by_mentions(heroes, text)] == ["Dash", "Azalea"]
