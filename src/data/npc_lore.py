"""Shared helpers for NPC roster rows and hero-name classification.

``npcs.csv`` is the curated in-repo roster for non-playable characters
(``CharacterId``, ``Name``, ``Species``, ``Status``). Story appearances are
recorded in ``story-npcs.csv`` (``StoryId``, ``CharacterId``).

Playable heroes are defined by ``heroes-canonical.csv`` (``CanonicalHero``).
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import REGENERATE_STORY_REGISTRY, read_pipe_csv, write_pipe_csv_autogen

ROOT = Path(__file__).resolve().parents[2]
HEROES_CANONICAL_CSV_PATH = ROOT / "src/data/heroes-canonical.csv"
NPCS_CSV_PATH = ROOT / "src/data/npcs.csv"

# Map Icelandic (and similar) letters before folding so CSV spellings match canonical.
_LATIN1_BRIDGES = str.maketrans({"ð": "d", "þ": "th", "Þ": "TH", "Ð": "D"})


def ascii_fold(value: str) -> str:
    """Remove combining marks after NFKD normalization for ASCII-ish folding.

    Args:
        value: Arbitrary Unicode display string.

    Returns:
        NFKD base characters without combining diacritics.
    """
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(value: str) -> str:
    """Lowercase alphanumeric-only fold for lore name keys and id hashing.

    Args:
        value: Display name from CSV or markdown.

    Returns:
        Folded, lowercased key suitable for hashing and set membership.
    """
    folded = ascii_fold(value.translate(_LATIN1_BRIDGES))
    return re.sub(r"[^a-z0-9]+", "", folded.lower())


def load_canonical_hero_names(path: Path) -> list[str]:
    """Load unique ``CanonicalHero`` labels from ``heroes-canonical.csv``.

    Args:
        path: Pipe-delimited heroes canonical CSV.

    Returns:
        First-seen order of non-empty ``CanonicalHero`` strings (case-fold deduped).
    """
    names: list[str] = []
    seen: set[str] = set()
    _, rows = read_pipe_csv(path)
    for row in rows:
        raw = (row.get("CanonicalHero") or "").strip()
        if not raw:
            continue
        key = raw.casefold()
        if key not in seen:
            seen.add(key)
            names.append(raw)
    return names


def build_hero_match_keys(hero_names: list[str]) -> set[str]:
    """Build lookup keys so a display ``Name`` can be classified as a playable hero.

    Args:
        hero_names: Display names from :func:`load_canonical_hero_names`.

    Returns:
        Set of strings to test with :func:`row_name_matches_hero`.
    """
    keys: set[str] = set()
    for hero in hero_names:
        stripped = hero.strip()
        keys.add(stripped.casefold())
        keys.add(normalize_name(stripped))
        parts = stripped.split()
        if len(parts) > 1:
            keys.add(parts[0].casefold())
            keys.add(normalize_name(parts[0]))
    return keys


def row_name_matches_hero(name: str, hero_keys: set[str]) -> bool:
    """Return whether ``name`` refers to a playable hero (must not be stored as an NPC).

    Args:
        name: Proposed ``Name`` for an NPC row.
        hero_keys: Output of :func:`build_hero_match_keys`.

    Returns:
        ``True`` if the name should be refused for NPC tooling.
    """
    n = name.strip()
    if n.casefold() in hero_keys:
        return True
    nn = normalize_name(n)
    if nn in hero_keys:
        return True
    return False


def read_npc_rows(path: Path | None = None) -> list[dict[str, str]]:
    """Load ``npcs.csv`` rows with stripped string fields.

    Args:
        path: CSV path; defaults to :data:`NPCS_CSV_PATH`.

    Returns:
        Row dicts with keys ``CharacterId``, ``Name``, ``Species``, ``Status``.
    """
    p = path or NPCS_CSV_PATH
    out: list[dict[str, str]] = []
    _, rows = read_pipe_csv(p)
    for row in rows:
        out.append(
            {
                "CharacterId": (row.get("CharacterId") or "").strip(),
                "Name": (row.get("Name") or "").strip(),
                "Species": (row.get("Species") or "").strip(),
                "Status": (row.get("Status") or "").strip(),
            }
        )
    return out


def write_npc_rows(rows: list[dict[str, str]], path: Path | None = None) -> None:
    """Write ``npcs.csv`` sorted by normalized name for stable diffs.

    Emits the same ``# AUTO-GENERATED FILE`` banner as other lore registries written
    by ``story.py`` (``pipe_csv_io.REGENERATE_STORY_REGISTRY``).

    Args:
        rows: Row dicts with keys ``CharacterId``, ``Name``, ``Species``, ``Status``.
        path: Destination path; defaults to :data:`NPCS_CSV_PATH`.
    """
    p = path or NPCS_CSV_PATH
    fieldnames = ["CharacterId", "Name", "Species", "Status"]
    sorted_rows = sorted(rows, key=lambda r: normalize_name(r["Name"]))
    write_pipe_csv_autogen(
        p,
        fieldnames,
        sorted_rows,
        regenerate_command=REGENERATE_STORY_REGISTRY,
    )
