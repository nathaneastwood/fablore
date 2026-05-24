"""Tests for ``mdbook_story_meta`` mdBook preprocessor helpers."""

from __future__ import annotations

from mdbook_story_meta import (
    _NO_WORDCOUNT_TYPES,
    _build_meta_html,
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
    html = _build_share_html('<script>')
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
        authors="", artists="", publication_date="", source_link="",
        word_count=500,
    )
    assert "500" in html
    assert "fa-clock-o" in html


def test_meta_html_suppresses_word_count_when_flag_false() -> None:
    html = _build_meta_html(
        authors="", artists="", publication_date="", source_link="",
        word_count=500, show_word_count=False,
    )
    # fa-clock-o is the word-count icon; its absence confirms suppression
    # (avoid asserting on "500" directly — that digit appears in the BlueSky SVG path)
    assert "fa-clock-o" not in html
    assert "words" not in html


def test_meta_html_share_always_present() -> None:
    # Even with no metadata fields, share buttons are injected
    html = _build_meta_html(
        authors="", artists="", publication_date="", source_link="",
        word_count=0,
    )
    assert "story-share" in html


def test_meta_html_no_story_meta_div_when_no_items() -> None:
    html = _build_meta_html(
        authors="", artists="", publication_date="", source_link="",
        word_count=0,
    )
    assert 'class="story-meta"' not in html


def test_meta_html_story_type_passed_to_share() -> None:
    html = _build_meta_html(
        authors="", artists="", publication_date="", source_link="",
        word_count=0, story_type="main-story",
    )
    assert 'data-story-type="main-story"' in html


def test_meta_html_authors_rendered() -> None:
    html = _build_meta_html(
        authors="Jane Doe", artists="", publication_date="", source_link="",
        word_count=0,
    )
    assert "Jane Doe" in html
    assert "fa-pencil" in html


def test_meta_html_authors_escaped() -> None:
    html = _build_meta_html(
        authors="<b>Bad</b>", artists="", publication_date="", source_link="",
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
    assert "fa-clock-o" not in out


def test_process_chapter_heroes_of_rathe_no_word_count() -> None:
    content = "# Hero\n\nSome text " * 30
    row = _make_row("heroes-of-rathe")
    out = _process_chapter(content, row)
    assert "fa-clock-o" not in out


def test_process_chapter_main_story_has_word_count() -> None:
    content = "# Story\n\nSome text " * 30
    row = _make_row("main-story")
    out = _process_chapter(content, row)
    assert "fa-clock-o" in out


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
        "# Title\n\n"
        "<!-- fablore-story-meta:start -->\n<p>OLD</p>\n<!-- fablore-story-meta:end -->\n\n"
        "Body."
    )
    out = _inject_after_heading(existing, "<p>NEW</p>")
    assert "OLD" not in out
    assert "<p>NEW</p>" in out
    assert "Body." in out


def test_inject_after_heading_no_heading_prepends() -> None:
    out = _inject_after_heading("Just a paragraph.", "<p>meta</p>")
    assert out.startswith("<!-- fablore-story-meta:start -->")
