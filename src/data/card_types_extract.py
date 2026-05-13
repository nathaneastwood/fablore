"""Parse ``Types`` fields into display class and talent names for registry CSVs.

Hero, weapon, and equipment pipelines split ``Types`` into **classes** (base hero
classes from :data:`BASE_CLASSES`) and **talents** — only the affinity / element
tokens listed in :data:`VALID_TALENT_TOKENS` (case-insensitive match on each token).
Structural tokens such as *Hero*, *Young*, *Weapon*, *Equipment*, *Sword*, etc.
are not talents for registry purposes.
"""

from __future__ import annotations

import re

BASE_CLASSES = frozenset(
    {
        "adjudicator",
        "assassin",
        "bard",
        "brute",
        "generic",
        "guardian",
        "illusionist",
        "mechanologist",
        "merchant",
        "necromancer",
        "ninja",
        "pirate",
        "ranger",
        "runeblade",
        "shapeshifter",
        "thief",
        "warrior",
        "wizard",
    }
)

HERO_TYPE_EXCLUSIONS = frozenset({"hero", "young", "adult"})

# Token text (lowercase) allowed in ``talents.csv`` — FAB affinity / element talents only.
VALID_TALENT_TOKENS = frozenset(
    {
        "chaos",
        "draconic",
        "earth",
        "elemental",
        "ice",
        "light",
        "lightning",
        "mystic",
        "revered",
        "reviled",
        "royal",
        "shadow",
    }
)


def parse_tokens(value: str) -> list[str]:
    """Split a comma-separated card field into trimmed non-empty tokens.

    Args:
        value: Raw ``Types`` or similar field.

    Returns:
        List of stripped segment strings.
    """
    return [token.strip() for token in str(value).split(",") if token.strip()]


def dedupe_preserving_order(values: list[str]) -> list[str]:
    """Return ``values`` without duplicates, preserving original order.

    Args:
        values: Ordered iterable of strings.

    Returns:
        First-seen unique strings only.
    """
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def title_case_tokens(value: str) -> str:
    """Title-case each comma-separated token for display class/talent names.

    Args:
        value: Comma-separated type tokens from a card ``Types`` field.

    Returns:
        Comma+space joined title-cased tokens.
    """
    tokens = [token.strip() for token in value.split(",") if token.strip()]
    return ", ".join(token[:1].upper() + token[1:].lower() for token in tokens)


def is_young_hero_card(types_value: str) -> bool:
    """Return True when the card ``Types`` list includes a *Young* hero token.

    Args:
        types_value: Raw ``Types`` column from a card row.

    Returns:
        True if any comma-separated token matches *young* case-insensitively.
    """
    return any(token.lower() == "young" for token in parse_tokens(types_value))


def extract_card_classes_and_talents(types_value: str) -> tuple[list[str], list[str]]:
    """Split ``Types`` into class names and registered affinity talent names.

    Args:
        types_value: Raw ``Types`` column from a card row.

    Returns:
        ``(classes, talents)`` as deduped, order-preserving lists of display strings.
        Talents are only tokens in :data:`VALID_TALENT_TOKENS`.
    """
    tokens = parse_tokens(types_value)
    classes = [title_case_tokens(token) for token in tokens if token.lower() in BASE_CLASSES]
    talents = [
        title_case_tokens(token)
        for token in tokens
        if token.lower() in VALID_TALENT_TOKENS
    ]
    return dedupe_preserving_order(classes), dedupe_preserving_order(talents)


def types_include_weapon(types_value: str) -> bool:
    """Return True if any ``Types`` token contains the word *weapon* as a token."""
    for token in parse_tokens(types_value):
        if re.search(r"\bweapon\b", token, re.IGNORECASE):
            return True
    return False


def extract_weapon_classes_and_talents(types_value: str) -> tuple[list[str], list[str]]:
    """Like hero class/talent split, but drop type tokens that denote *weapon* layout."""
    classes, talents = extract_card_classes_and_talents(types_value)
    talents = [
        t for t in talents if not re.search(r"\bweapon\b", t, re.IGNORECASE)
    ]
    return dedupe_preserving_order(classes), dedupe_preserving_order(talents)


def types_include_equipment(types_value: str) -> bool:
    """Return True if any ``Types`` token contains the word *equipment* as a word."""
    for token in parse_tokens(types_value):
        if re.search(r"\bequipment\b", token, re.IGNORECASE):
            return True
    return False


def extract_equipment_classes_and_talents(types_value: str) -> tuple[list[str], list[str]]:
    """Like weapon split: drop type tokens whose display text is the *equipment* label."""
    classes, talents = extract_card_classes_and_talents(types_value)
    talents = [
        t for t in talents if not re.search(r"\bequipment\b", t, re.IGNORECASE)
    ]
    return dedupe_preserving_order(classes), dedupe_preserving_order(talents)


def is_non_weapon_equipment_card(types_value: str) -> bool:
    """True when this row is equipment gear, excluding hybrid *weapon* equipment cards.

    Rows with both ``Weapon`` and ``Equipment`` in ``Types`` are handled by the
    weapons generator only so each physical card appears in at most one game table.
    """
    return types_include_equipment(types_value) and not types_include_weapon(types_value)
