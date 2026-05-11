"""Deterministic primary keys for lore registry CSVs (pipe-delimited).

Uses :func:`npc_lore.normalize_name` for stable folding consistent with ``npcs.csv``
and other name-keyed ids (``LC``, ``MO``, ``FA``, etc.).
"""

from __future__ import annotations

import hashlib

from npc_lore import normalize_name


def story_id(story_key: str) -> str:
    """Compute ``StoryId`` for ``stories.csv``.

    Junction tables (``story-npcs.csv``, etc.) store this value, not ``StoryKey``.

    Args:
        story_key: Path relative to ``src/``, POSIX-style.

    Returns:
        ``ST`` plus the first 10 hex digits of SHA-256 over UTF-8 ``story_key``.
    """
    digest = hashlib.sha256(story_key.encode("utf-8")).hexdigest()[:10]
    return f"ST{digest}"


def canonical_id(canonical_slug: str) -> str:
    """Compute ``CanonicalId`` from slug (matches ``create_heroes_csv`` hashing).

    Args:
        canonical_slug: Lowercase slug such as ``boltyn``.

    Returns:
        ``CN`` plus the first 10 hex digits of SHA-1 over UTF-8 slug.
    """
    digest = hashlib.sha1(canonical_slug.strip().encode("utf-8")).hexdigest()[:10]
    return f"CN{digest}"


def _sha256_id(prefix: str, label: str) -> str:
    """Return ``prefix`` + 10 hex chars of SHA-256 over :func:`normalize_name` of ``label``."""
    digest = hashlib.sha256(normalize_name(label).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}{digest}"


def lore_character_id(name: str) -> str:
    """Return deterministic ``LC`` + 10 hex chars from SHA-256 of :func:`normalize_name`.

    Args:
        name: Character display name as stored in ``npcs.csv``.

    Returns:
        Primary key string ``LC`` + digest, stable for a given spelling.
    """
    return _sha256_id("LC", name.strip())


def monster_id(name: str) -> str:
    """Return ``MonsterId`` for a monster display name.

    Args:
        name: Monster name as stored in ``monsters.csv``.

    Returns:
        ``MO`` + digest id.
    """
    return _sha256_id("MO", name.strip())


def fauna_id_from_name(name: str) -> str:
    """Return ``FaunaId`` from plain display ``name``.

    Args:
        name: Fauna name text.

    Returns:
        ``FA`` + digest id.
    """
    return _sha256_id("FA", name.strip())


def flora_id(name: str) -> str:
    """Return ``FloraId`` for a plant name.

    Args:
        name: Flora display name.

    Returns:
        ``FR`` + digest id.
    """
    return _sha256_id("FR", name.strip())


def food_drink_id(name: str, kind: str) -> str:
    """Return ``FoodDrinkId`` from name and type/kind.

    Args:
        name: Item display name.
        kind: ``Type`` column value.

    Returns:
        ``FD`` + digest of ``name|kind``.
    """
    composite = f"{name.strip()}|{kind.strip()}"
    return _sha256_id("FD", composite)


def region_row_id(region_name: str) -> str:
    """Return deterministic ``RegionId`` for a region display name.

    Matches existing ``regions.csv`` rows (``RG`` + SHA-256 of
    :func:`normalize_name` of ``region_name``).

    Args:
        region_name: Human-readable region name (e.g. ``Aria``).

    Returns:
        ``RG`` + 10 hex characters.
    """
    return _sha256_id("RG", region_name.strip())


def location_id(name: str, region_id: str) -> str:
    """Return ``LocationId`` from place name and ``RegionId``.

    Args:
        name: Location display name.
        region_id: Foreign key string into ``regions.csv``; may be empty when
            the location's region is unknown.

    Returns:
        ``LO`` + digest of ``name|region_id``.
    """
    composite = f"{name.strip()}|{region_id.strip()}"
    return _sha256_id("LO", composite)
