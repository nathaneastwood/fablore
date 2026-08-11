"""Summary page registrations — one ``db.upsert_story`` call per page.

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
    path="src/summaries/war-of-the-monarch-pt-1.md",
    story_type="summaries",
    title="War of the Monarch, Part 1",
    heroes=[
        "viserai",
        "chane",
        "levia",
        "vynnset",
        "prism",
        "boltyn",
        "dorinthea",
        "shiyana",
    ],
    npcs=[
        NPCEntry(name="Grand Magister, the Devout", species="Human", status="Assumed Dead"),
        NPCEntry(name="Apostate", species="Human"),
        NPCEntry(name="Lord Sutcliffe", species="Human", status="Just a head"),
        NPCEntry(name="Lady Bartimont"),
        NPCEntry(name="Ursur", species="Embra"),
        NPCEntry(name="Blasmophet", species="Embra"),
        NPCEntry(name="Nasreth", species="Embra"),
        NPCEntry(name="Sol", species="Aesir"),
        NPCEntry(name="Suraya, Archangel of Knowledge", species="Herald"),
        NPCEntry(name="Bellona, the Wartune Herald", species="Herald"),
        NPCEntry(name="Minerva Themis", species="Human", status="Deceased"),
    ],
    locations=[
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("Library of Illumination", region="Solana"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
        RegionEntry("Volcor"),
    ],
    dry_run=True,
)
# TODO: metadata — authors / source_link / publication_date unknown for this recap

db.upsert_story(
    path="src/summaries/war-of-the-monarch-pt-2.md",
    story_type="summaries",
    title="War of the Monarch, Part 2",
    authors="Rachel Rees, Kasharn Rao, Aidan Kwasneski, Edwin McRae",
    source_link="https://fabtcg.com/usurp-the-shadow-throne-lore-recap/",
    publication_date="2026-07-17",
    heroes=[
        "viserai",
        "chane",
        "levia",
        "vynnset",
        "prism",
        "bravo",
        "oldhim",
        "lexi",
        "briar",
        "dorinthea",
        "boltyn",
        "hala",
    ],
    npcs=[
        NPCEntry(name="Apostate", species="Human"),
        NPCEntry(name="Lord Sutcliffe", species="Human", status="Just a head"),
        NPCEntry(name="Ursur", species="Embra"),
        NPCEntry(name="Blasmophet", species="Embra"),
        NPCEntry(name="Sol", species="Aesir"),
    ],
    locations=[
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry(
            "The Northern Realms",
            region="Solana",
            lore_fragment="the-northern-realms",
        ),
        LocationEntry("The Solarium", region="Solana"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Nebulus Rift"),
        RegionEntry("Solana"),
    ],
    dry_run=True,
)
