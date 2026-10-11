"""Summary page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

from entries._runner import db
from entries.catalogue import (
    characters as people,
)
from entries.catalogue import (
    groups as grp,
)
from entries.catalogue import (
    locations as loc,
)
from entries.catalogue import (
    regions as reg,
)

db.upsert_story(
    path="src/summaries/war-of-the-monarch-pt-1.md",
    story_type="summaries",
    title="War of the Monarch, Part 1",
    characters=[
        "viserai",
        "chane",
        "levia",
        "vynnset",
        "prism",
        "boltyn",
        "dorinthea",
        "shiyana",
        people.GRAND_MAGISTER_THE_DEVOUT,
        people.APOSTATE,
        people.LORD_SUTCLIFFE,
        people.LADY_BARTHIMONT,
        people.URSUR,
        people.BLASMOPHET,
        people.NASRETH,
        people.SOL,
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.MINERVA_THEMIS,
    ],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.VOLCOR,
    ],
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/summaries/war-of-the-monarch-pt-2.md",
    story_type="summaries",
    title="War of the Monarch, Part 2",
    authors="Rachel Rees, Kasharn Rao, Aidan Kwasneski, Edwin McRae",
    source_link="https://fabtcg.com/usurp-the-shadow-throne-lore-recap/",
    publication_date="2026-07-17",
    characters=[
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
        people.APOSTATE,
        people.LORD_SUTCLIFFE,
        people.URSUR,
        people.BLASMOPHET,
        people.SOL,
    ],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
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
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/summaries/README.md",
    story_type="summaries",
    title="Main Story Summaries",
    dry_run=True,
)
