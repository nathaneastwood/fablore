"""Summary page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

# Entities are referenced, never constructed. Every registry id is a hash of the
# fields written at the call site, so a second literal for the same entity
# competes with the first row instead of reusing it — that is how "The Shadow
# Crypts" became two rows. The canonical definition of each lives in
# entries/catalogue/; none of the entry classes are imported here, so writing
# LocationEntry(...) is a NameError rather than a silent new row.
from entries.catalogue import (  # noqa: F401
    fauna,
    flora,
    food_drink as food,
    locations as loc,
    monsters as mon,
    npcs as npc,
    regions as reg,
)

# NarratedVideoEntry is the one exception: a narrated reading belongs to one
# story, has no registry table and no id of its own, so it is per-declaration
# data rather than a shared entity.
from db import NarratedVideoEntry  # noqa: F401
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
        npc.GRAND_MAGISTER_THE_DEVOUT,
        npc.APOSTATE,
        npc.LORD_SUTCLIFFE,
        npc.LADY_BARTHIMONT,
        npc.URSUR,
        npc.BLASMOPHET,
        npc.NASRETH,
        npc.SOL,
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.MINERVA_THEMIS,
    ],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.HAND_OF_SOL,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.VOLCOR,
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
        npc.APOSTATE,
        npc.LORD_SUTCLIFFE,
        npc.URSUR,
        npc.BLASMOPHET,
        npc.SOL,
    ],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.HAND_OF_SOL,
        loc.THE_NORTHERN_REALMS,
        loc.THE_SOLARIUM,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.DEMONASTERY,
        reg.NEBULUS_RIFT,
        reg.SOLANA,
    ],
    dry_run=True,
)
