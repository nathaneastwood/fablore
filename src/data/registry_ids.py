"""Deterministic primary keys for lore and game registry CSVs (pipe-delimited).

Lore-side ids (``LC``, ``MO``, ``FA``, ``FR``, ``FD``, ``RG``, ``LO``, ``ST``) use
SHA-256 over :func:`text_utils.normalize_name` of the source string. Game-side ids
(``CN``, ``HG``, ``WG``, ``EG``, ``CW``, ``CE``, ``CL``, ``TL``, ``TY``) use
:func:`make_hash_id` (SHA-1) over a caller-supplied stable key (slug, name, or
composite). Two algorithms remain for backwards compatibility with the original
generator output; both are deterministic.
"""

from __future__ import annotations

import hashlib

from text_utils import normalize_name


def assert_unique_ids(items: list[tuple[str, str]], id_kind: str) -> None:
    """Raise ``ValueError`` naming the colliding source strings on hash collision.

    Args:
        items: ``(generated_id, source_string)`` pairs. Empty ids are skipped so
            partially-built id lists (e.g. canonical rows that haven't been hashed
            yet) don't trigger false positives.
        id_kind: Human-readable label (e.g. ``"canonical hero"``) used in the error.

    Raises:
        ValueError: When two distinct source strings produced the same id.
    """
    seen: dict[str, str] = {}
    for new_id, source in items:
        if not new_id:
            continue
        if new_id in seen and seen[new_id] != source:
            raise ValueError(
                f"{id_kind} ID hash collision detected: "
                f"{seen[new_id]!r} and {source!r} both hash to {new_id!r}"
            )
        seen[new_id] = source


def make_hash_id(prefix: str, unique_value: str, digest_len: int = 10) -> str:
    """Return ``prefix`` + truncated SHA-1 hex digest of ``unique_value``.

    Used for game-side registries (heroes, weapons, equipment, classes, talents,
    sets, set types). Callers pre-normalize when needed: canonical-slug ids pass
    the slug as-is; class/talent/set-type ids pass :func:`normalize_name` output.

    Args:
        prefix: Two-letter uppercase id family (``HG``, ``CN``, ``CL``, ``TY`` …).
        unique_value: Stable UTF-8 string to hash.
        digest_len: Hex characters to keep (default ``10``).

    Returns:
        Deterministic identifier.
    """
    digest = hashlib.sha1(unique_value.encode("utf-8")).hexdigest()[:digest_len]
    return f"{prefix}{digest}"


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
    return make_hash_id("CN", canonical_slug.strip())


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
