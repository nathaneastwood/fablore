"""Tests for :mod:`mdbook_hints` auto-detection preprocessor."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_hints import (  # noqa: E402
    _AUTO_DETECT_TYPES,
    extract_section_heading_texts,
    find_protected_regions,
    get_match_strings,
    page_slug_from_path,
    process_chapter,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

# DB-backed types (auto-detected):
#   Southmaw   — location
#   Siren      — fauna with list match
#   Brawnhide  — fauna
#   Meep       — fauna
#   MeepColony — fauna with match override (longer match test)
#
# Non-DB types (NOT auto-detected, manual markup only):
#   Sol        — aesir
#   HandOfSol  — faction with match override
#   Raven      — aesir

HINTS = {
    "Southmaw": {"type": "location", "summary": "An asylum in the Pits."},
    "Siren": {"match": ["Siren", "Sirens"], "type": "fauna", "summary": "Enchanting merfolk."},
    "Brawnhide": {"type": "fauna", "summary": "A giant furred beast."},
    "Meep": {"type": "fauna", "summary": "Tiny mischievous creatures."},
    "MeepColony": {"match": "Meep Colony", "type": "fauna", "summary": "A group of Meeps."},
    # Non-DB — must NOT be auto-detected
    "Sol": {"type": "aesir", "summary": "Aesir of Light"},
    "HandOfSol": {"match": "Hand of Sol", "type": "faction"},
    "Raven": {"type": "aesir"},
}

# ---------------------------------------------------------------------------
# _AUTO_DETECT_TYPES
# ---------------------------------------------------------------------------


def test_auto_detect_types_contains_db_types():
    assert _AUTO_DETECT_TYPES == {"location", "monster", "fauna", "flora"}


# ---------------------------------------------------------------------------
# get_match_strings
# ---------------------------------------------------------------------------


def test_get_match_strings_plain_string():
    assert get_match_strings("Sol", "Aesir of Light") == ["Sol"]


def test_get_match_strings_dict_no_match():
    assert get_match_strings("Southmaw", {"type": "location", "summary": "..."}) == ["Southmaw"]


def test_get_match_strings_dict_string_match():
    assert get_match_strings("HandOfSol", {"match": "Hand of Sol", "type": "faction"}) == [
        "Hand of Sol"
    ]


def test_get_match_strings_dict_list_match():
    result = get_match_strings("Siren", {"match": ["Siren", "Sirens"]})
    assert result == ["Siren", "Sirens"]


def test_get_match_strings_dict_no_match_field_uses_key():
    assert get_match_strings("Raven", {"type": "aesir", "summary": "..."}) == ["Raven"]


# ---------------------------------------------------------------------------
# page_slug_from_path
# ---------------------------------------------------------------------------


def test_page_slug_from_path_simple():
    assert page_slug_from_path("Solana/guide.md") == "Solana/guide"


def test_page_slug_from_path_none():
    assert page_slug_from_path(None) == ""


def test_page_slug_from_path_nested():
    assert page_slug_from_path("main-story/uprising/betrayal.md") == "main-story/uprising/betrayal"


# ---------------------------------------------------------------------------
# extract_section_heading_texts
# ---------------------------------------------------------------------------


def test_extract_section_headings_basic():
    content = "# Title\n\n## Section One\n\n### Sub\n\nBody text.\n"
    headings = extract_section_heading_texts(content)
    assert "Section One" in headings
    assert "Sub" in headings
    assert "Title" not in headings  # H1 excluded


def test_extract_section_headings_none():
    assert extract_section_heading_texts("Just some text.\n") == []


# ---------------------------------------------------------------------------
# process_chapter — type filter
# ---------------------------------------------------------------------------


def test_db_type_auto_detected():
    content = "A Brawnhide emerged from the trees.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Brawnhide"' in result


def test_non_db_type_not_auto_detected():
    # "Sol" is type "aesir" — must not be auto-linked
    content = "Sol shines over Solana.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Sol"' not in result


def test_non_db_type_via_old_markup_still_works():
    # Manual [Text](~Key) should work for any type
    content = "[Sol](~Sol) shines over Solana.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Sol"' in result


def test_faction_not_auto_detected():
    content = "The Hand of Sol marched forth.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="HandOfSol"' not in result


def test_plain_string_entry_not_auto_detected():
    hints = {"Aedes": "Solanian Tuesday"}
    content = "It was Aedes morning.\n"
    result = process_chapter(content, hints)
    assert 'hint="Aedes"' not in result


# ---------------------------------------------------------------------------
# process_chapter — basic injection
# ---------------------------------------------------------------------------


def test_basic_injection():
    content = "A Brawnhide prowled the edge of the forest.\n"
    result = process_chapter(content, HINTS)
    assert '<span class="hint" hint="Brawnhide">Brawnhide</span>' in result


def test_first_occurrence_only():
    content = "A Brawnhide appeared. The Brawnhide growled.\n"
    result = process_chapter(content, HINTS)
    assert result.count('hint="Brawnhide"') == 1


def test_no_match_in_content():
    content = "Nothing relevant here.\n"
    result = process_chapter(content, HINTS)
    assert "hint=" not in result


def test_list_match_first_variant():
    content = "A Siren sang from the rocks.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Siren"' in result


def test_list_match_second_variant():
    content = "Three Sirens lured sailors to their doom.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Siren"' in result


def test_word_boundary_no_partial():
    # "Meep" must not match inside a made-up longer word
    content = "The Meeplings scurried away.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Meep"' not in result


def test_match_string_override_for_db_type():
    # MeepColony has match="Meep Colony" — verify the override fires
    content = "The Meep Colony gathered near the stream.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="MeepColony"' in result


# ---------------------------------------------------------------------------
# process_chapter — protected regions
# ---------------------------------------------------------------------------


def test_code_span_protected():
    content = "Use `Brawnhide` in code.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Brawnhide"' not in result


def test_fenced_code_protected():
    content = "```\nA Brawnhide appeared.\n```\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Brawnhide"' not in result


def test_link_text_protected():
    content = "See [Brawnhide](https://example.com) for details.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Brawnhide"' not in result


def test_heading_text_not_injected():
    # Even though H1 doesn't suppress (Option A), injection into the heading is blocked
    content = "# Brawnhide\n\nThe Brawnhide is a large beast.\n"
    result = process_chapter(content, HINTS)
    assert "# Brawnhide\n" in result  # heading itself unchanged


# ---------------------------------------------------------------------------
# process_chapter — heading suppression (Option A)
# ---------------------------------------------------------------------------


def test_option_a_h2_suppresses():
    content = "## Southmaw\n\nSouthmaw is an asylum.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Southmaw"' not in result


def test_option_a_h3_suppresses():
    content = "### Southmaw\n\nSouthmaw is an asylum.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Southmaw"' not in result


def test_option_a_h1_does_not_suppress():
    # H1 headings do NOT trigger Option A; body occurrence should be injected
    content = "# Southmaw\n\nSouthmaw is an asylum in the Pits.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Southmaw"' in result


def test_option_a_unrelated_heading():
    content = "## The Northern Realms\n\nA Brawnhide prowled here.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="Brawnhide"' in result


# ---------------------------------------------------------------------------
# process_chapter — exclude_pages (Option C)
# ---------------------------------------------------------------------------


def test_option_c_excluded():
    hints = {
        "Brawnhide": {"type": "fauna", "summary": "A beast.", "exclude_pages": ["lore/brawnhide"]},
    }
    content = "A Brawnhide prowled.\n"
    result = process_chapter(content, hints, page_slug="lore/brawnhide")
    assert 'hint="Brawnhide"' not in result


def test_option_c_not_excluded():
    hints = {
        "Brawnhide": {"type": "fauna", "summary": "A beast.", "exclude_pages": ["lore/brawnhide"]},
    }
    content = "A Brawnhide prowled.\n"
    result = process_chapter(content, hints, page_slug="other/page")
    assert 'hint="Brawnhide"' in result


# ---------------------------------------------------------------------------
# process_chapter — backward-compat old markup
# ---------------------------------------------------------------------------


def test_old_markup_converted():
    content = "The [Hand of Sol](~HandOfSol) patrol.\n"
    result = process_chapter(content, HINTS)
    assert '<span class="hint" hint="HandOfSol">Hand of Sol</span>' in result


def test_old_markup_key_not_double_injected():
    # Key processed via old markup must not also be auto-detected
    content = "[Brawnhide](~Brawnhide) and another Brawnhide.\n"
    result = process_chapter(content, HINTS)
    assert result.count('hint="Brawnhide"') == 1


# ---------------------------------------------------------------------------
# process_chapter — longest match wins
# ---------------------------------------------------------------------------


def test_longer_match_preferred():
    # "Meep Colony" (longer) should match before "Meep" (shorter) gets a chance
    content = "The Meep Colony sheltered many a Meep.\n"
    result = process_chapter(content, HINTS)
    assert 'hint="MeepColony"' in result
    assert 'hint="Meep"' in result
    # Verify the Colony match came first (appears earlier in the string)
    assert result.index('hint="MeepColony"') < result.index('hint="Meep"')


# ---------------------------------------------------------------------------
# find_protected_regions — spot checks
# ---------------------------------------------------------------------------


def test_protected_fenced_code():
    content = "```\nSome code\n```\n"
    regions = find_protected_regions(content)
    assert any(s == 0 for s, _ in regions)


def test_protected_inline_code():
    content = "Use `foo` here."
    regions = find_protected_regions(content)
    start = content.index("`foo`")
    assert any(s == start for s, _ in regions)


def test_protected_link():
    content = "See [text](https://example.com)."
    regions = find_protected_regions(content)
    start = content.index("[text]")
    assert any(s == start for s, _ in regions)
