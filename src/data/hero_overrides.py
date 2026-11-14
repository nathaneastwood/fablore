"""Shared hero-specific overrides used by the heroes generator and mdBook preprocessor.

Some heroes (notably Arakni) have multiple distinct in-fiction identities sharing
a base card name. Keeping the maps that route those variants — lore file paths
and the card-name alias loader — in one module avoids the two-source-of-truth
problem the earlier setup had (one map in ``create_heroes_csv.py``, another in
``mdbook_related.py``).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

HERO_CARD_NAME_ALIASES_PATH = Path(__file__).resolve().parent / "csv" / "hero-card-name-aliases.csv"

# Canonical slug → ``src``-relative lore markdown path for slugs whose lore page
# does not follow the default ``heroes-of-rathe/{slug}-about.md`` rule.
HERO_SLUG_LORE_FILE_OVERRIDES: dict[str, str] = {
    "arakni-huntsman": "heroes-of-rathe/arakni-about.md",
    "arakni-solitary-confinement": "heroes-of-rathe/arakni-5l!p3d-7hru-7h3-cr4x-about.md",
    "arakni-web-of-deceit": "heroes-of-rathe/arakni-marionette-about.md",
}


def load_canonical_hero_card_name_aliases() -> dict[str, str]:
    """Return ``NormalizedCardName -> CanonicalSlug`` from the aliases CSV.

    A key is ``normalize_name`` of either a full printed card title or the
    part before its first comma; :func:`create_heroes_csv.resolve_card_canonical_slug`
    tries the full title first.

    Editable as a data file so non-Python contributors can add hero card-name
    routing without touching the generator. Loaded each call; the file is tiny.
    """
    _, rows = read_pipe_csv(HERO_CARD_NAME_ALIASES_PATH)
    out: dict[str, str] = {}
    for row in rows:
        key = (row.get("NormalizedCardName") or "").strip()
        slug = (row.get("CanonicalSlug") or "").strip()
        if key and slug:
            out[key] = slug
    return out
