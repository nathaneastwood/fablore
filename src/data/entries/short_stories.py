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
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    RegionEntry,
)
from entries._runner import db

db.upsert_story(
    path="src/short-stories/usurp-the-shadow-throne/open-the-gates.md",
    story_type="short-stories",
    title="Open the Gates",
    publication_date="2026-07-16",
    heroes=["viserai", "levia", "malice"],
    npcs=[
        NPCEntry(name="Blasmophet", species="Embra"),
    ],
    locations=[
        LocationEntry("The Abyss"),
        LocationEntry("Neverest"),
        LocationEntry("Shadowrealm"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
    ],
    dry_run=True,
)
# TODO: group — Gloomblades
