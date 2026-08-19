"""Shared text-normalization helpers used for registry id hashing and name matching.

Single source of truth for the lowercase alphanumeric fold used across all
``src/data/`` registries. For ASCII inputs the fold is equivalent to the simpler
``re.sub(r"[^a-z0-9]+", "", value.lower())`` previously duplicated in several
generators; for inputs containing diacritics it folds them via NFKD before
stripping non-alphanumerics so spellings like ``Éva`` and ``Eva`` hash the same.
"""

from __future__ import annotations

import re
import unicodedata

_LATIN1_BRIDGES = str.maketrans({"ð": "d", "þ": "th", "Þ": "TH", "Ð": "D"})


def ascii_fold(value: str) -> str:
    """Remove combining marks after NFKD normalization for ASCII-ish folding."""
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(value: str) -> str:
    """Lowercase alphanumeric-only fold for registry name keys and id hashing."""
    folded = ascii_fold(value.translate(_LATIN1_BRIDGES))
    return re.sub(r"[^a-z0-9]+", "", folded.lower())
