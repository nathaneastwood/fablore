"""Tests for :mod:`card_types_extract`."""

from __future__ import annotations

from card_types_extract import (
    VALID_TALENT_TOKENS,
    extract_card_classes_and_talents,
    extract_equipment_classes_and_talents,
    extract_weapon_classes_and_talents,
    is_non_weapon_equipment_card,
    parse_tokens,
    types_include_equipment,
    types_include_weapon,
)


def test_valid_talent_token_count() -> None:
    """Affinity vocabulary matches the twelve FAB talent names."""
    assert len(VALID_TALENT_TOKENS) == 12


def test_parse_tokens_splits_commas() -> None:
    """Comma-separated ``Types`` tokens are trimmed."""
    assert parse_tokens(" A , B , ") == ["A", "B"]


def test_types_include_weapon_detects_token() -> None:
    """Word-boundary match finds weapon layout tokens."""
    assert types_include_weapon("Warrior, Weapon, Sword, 1h") is True
    assert types_include_weapon("Mechanologist, Equipment, Legs") is False


def test_types_include_equipment_detects_token() -> None:
    """Equipment keyword is detected inside a type token."""
    assert types_include_equipment("Wizard, Equipment, Chest") is True


def test_extract_card_classes_and_talents() -> None:
    """Classes use ``BASE_CLASSES``; talents use affinity tokens only."""
    classes, talents = extract_card_classes_and_talents("Ninja, Hero, Young")
    assert classes == ["Ninja"]
    assert talents == []

    c2, t2 = extract_card_classes_and_talents("Light, Warrior, Hero, Young")
    assert c2 == ["Warrior"]
    assert t2 == ["Light"]


def test_extract_weapon_only_affinity_talents() -> None:
    """Weapon layout tokens are not talents; affinity tokens are."""
    classes, talents = extract_weapon_classes_and_talents(
        "Shadow, Assassin, Weapon, Dagger, 1h"
    )
    assert "Assassin" in classes
    assert talents == ["Shadow"]


def test_is_non_weapon_equipment_card() -> None:
    """Hybrids with both weapon and equipment are not pure equipment rows."""
    assert is_non_weapon_equipment_card("Mechanologist, Equipment, Legs") is True
    assert is_non_weapon_equipment_card("Warrior, Weapon, Equipment, Sword") is False


def test_extract_equipment_strips_equipment_label() -> None:
    """Equipment layout token is removed from derived talents."""
    _, talents = extract_equipment_classes_and_talents("Wizard, Equipment, Chest")
    assert talents == []
