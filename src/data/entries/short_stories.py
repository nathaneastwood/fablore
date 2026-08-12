"""Short story registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

# Every section module imports the whole entry set, so extending a declaration
# with a new entity type never also means editing the import. Unused names are
# deliberate.
from db import (  # noqa: F401
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    MonsterEntry,
    NarratedVideoEntry,
)

# NPCs, locations and regions are referenced, never constructed. Their ids are
# hashes of the fields written at the call site, so a second literal for the same
# entity competes with the first row instead of reusing it — that is how
# "The Shadow Crypts" became two rows. The canonical definition of each lives
# in entries/catalogue/; the three names are deliberately not imported above, so
# writing LocationEntry(...) here is a NameError rather than a silent new row.
from entries.catalogue import locations as loc, npcs as npc, regions as reg  # noqa: F401
from entries._runner import db

db.upsert_story(
    path="src/short-stories/usurp-the-shadow-throne/open-the-gates.md",
    story_type="short-stories",
    title="Open the Gates",
    publication_date="2026-07-16",
    heroes=["viserai", "levia", "malice"],
    npcs=[
        npc.BLASMOPHET,
    ],
    locations=[
        loc.THE_ABYSS,
        loc.NEVEREST,
        loc.SHADOWREALM,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    dry_run=True,
)
# TODO: group — Gloomblades
