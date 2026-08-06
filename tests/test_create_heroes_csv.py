"""Tests for helpers in :mod:`create_heroes_csv`."""

from __future__ import annotations

from create_heroes_csv import apply_lore_canonical_override, split_name_variant
from registry_ids import make_hash_id
from text_utils import normalize_name


def test_normalize_name_folds_to_alnum() -> None:
    """Non-alphanumeric characters are removed for matching keys."""
    assert normalize_name("Ser Boltyn") == "serboltyn"


def test_split_name_variant() -> None:
    """Printed titles split on the first comma."""
    name, sub = split_name_variant("Ira, Crimson Haze")
    assert name == "Ira"
    assert sub == "Crimson Haze"


def test_make_hash_id_deterministic() -> None:
    """Same input yields the same id prefix and length."""
    a = make_hash_id("HG", "stable-key")
    b = make_hash_id("HG", "stable-key")
    assert a == b
    assert a.startswith("HG")
    assert len(a) == len("HG") + 10


def test_lore_canonical_override_splits_arakni_forms() -> None:
    """Arakni's forms are distinct characters and must not collapse to one slug.

    The override table is keyed by the base hero name, but the caller passes a
    ``base_slug`` that has already been resolved through the roster's name index
    — for Arakni that is ``arakni-huntsman``, not ``arakni``. Looking up only the
    resolved slug silently routed every Arakni card to the Huntsman.
    """
    cases = {
        "Arakni, Marionette": "arakni-web-of-deceit",
        "Arakni, Web of Deceit": "arakni-web-of-deceit",
        "Arakni, Solitary Confinement": "arakni-solitary-confinement",
        "Arakni, 5L!p3d 7hRu 7h3 cR4X": "arakni-solitary-confinement",
        "Arakni, Huntsman": "arakni-huntsman",
        "Arakni": "arakni-huntsman",
    }
    for card_name, expected in cases.items():
        name, variant = split_name_variant(card_name)
        assert apply_lore_canonical_override("arakni-huntsman", name, variant) == expected, card_name


def test_lore_canonical_override_passes_through_unknown_heroes() -> None:
    """A hero with no override table keeps the slug it was resolved to."""
    assert apply_lore_canonical_override("bravo", "Bravo", "Showstopper") == "bravo"
