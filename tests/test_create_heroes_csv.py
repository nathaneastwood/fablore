"""Tests for helpers in :mod:`create_heroes_csv`."""

from __future__ import annotations

from create_heroes_csv import make_hash_id, normalize_name, split_name_variant


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
