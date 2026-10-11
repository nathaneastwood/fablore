"""Slug helpers for canonical weapon and equipment rows derived from ``Name``."""

from __future__ import annotations

import re


def slugify_card_name_stem(printed_name: str) -> str:
    """Return a stable hyphen slug from the full printed card ``Name``.

    Uses the entire ``Name`` field (including text after commas). Apostrophes are
    removed before punctuation is folded to hyphens so possessives like
    ``Kraken's`` become ``krakens``, not ``kraken-s``.

    Args:
        printed_name: Raw ``Name`` from ``card.csv`` (weapon/equipment rows).

    Returns:
        Lowercase hyphenated slug, or ``"unknown"`` when the fold is empty.
    """
    s = printed_name.strip().lower()
    # ASCII and typographic apostrophe — drop before replacing other punctuation
    s = s.replace("\u2019", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"
