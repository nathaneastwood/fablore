"""Tests for :mod:`card_name_slug`."""

from __future__ import annotations

from card_name_slug import slugify_card_name_stem


def test_slugify_full_title_with_comma() -> None:
    """Comma-separated titles contribute every segment to the slug."""
    assert slugify_card_name_stem("Jinglewood, Smash Hit") == "jinglewood-smash-hit"


def test_slugify_strips_apostrophe_possessive() -> None:
    """Apostrophes drop out so possessives do not become stray hyphens."""
    assert slugify_card_name_stem("Kraken's Aethervein") == "krakens-aethervein"


def test_slugify_basic() -> None:
    """Hyphen slug folds punctuation and spacing."""
    assert slugify_card_name_stem("Nebula Blade") == "nebula-blade"


def test_slugify_unknown_when_empty() -> None:
    """Non-alphanumeric-only stems yield the sentinel slug."""
    assert slugify_card_name_stem("@@@") == "unknown"
    assert slugify_card_name_stem("") == "unknown"


def test_slugify_collapses_repeated_hyphens() -> None:
    """Repeated separators collapse to a single hyphen."""
    assert slugify_card_name_stem("Foo   Bar") == "foo-bar"
