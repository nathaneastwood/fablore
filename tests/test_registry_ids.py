"""Tests for :mod:`registry_ids`."""

from __future__ import annotations

from create_heroes_csv import make_hash_id
from registry_ids import canonical_id, lore_character_id, story_id


def test_canonical_id_matches_create_heroes_hashing() -> None:
    """Canonical slug hashing matches ``make_hash_id(\"CN\", ...)``."""
    slug = "boltyn"
    assert canonical_id(slug) == make_hash_id("CN", slug)


def test_story_id_prefix_and_length() -> None:
    """Story ids use the ``ST`` prefix and fixed digest length."""
    sid = story_id("main-story/example.md")
    assert sid.startswith("ST")
    assert len(sid) == len("ST") + 10


def test_lore_character_id_stable() -> None:
    """Same name yields the same ``LC`` id."""
    a = lore_character_id("Merchant Jane")
    b = lore_character_id("Merchant Jane")
    assert a == b
    assert a.startswith("LC")
