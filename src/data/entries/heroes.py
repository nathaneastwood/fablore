"""Hero page registrations — one ``db.upsert_story`` call per page.

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
    path="src/heroes-of-rathe/aurora-about.md",
    story_type="heroes-of-rathe",
    title="Aurora",
    heroes=["aurora"],
    locations=[
        loc.ENION,
        loc.VOLTHAVEN,
        loc.VALAHAI,
    ],
    weapons=["star-fall", "scorpio-comet-tail"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/oscilio-about.md",
    story_type="heroes-of-rathe",
    title="Oscilio",
    heroes=["oscilio"],
    locations=[
        loc.ENION,
    ],
    regions=[reg.ARIA],
    weapons=["volzar-the-lightning-rod"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zyggy-about.md",
    story_type="heroes-of-rathe",
    title="Zyggy Starlight",
    heroes=["zyggy", "oscilio"],
    regions=[reg.NEBULUS_RIFT],
    locations=[
        loc.VALAHAI,
        loc.AURIC_KEEP,
    ],
    weapons=["aphrodias"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/blaze-about.md",
    story_type="heroes-of-rathe",
    title="Blaze",
    heroes=["blaze"],
    regions=[reg.VOLCOR],
    locations=[
        loc.IMPERIAL_PALACE,
    ],
    fauna=[FaunaEntry("Flare Deer")],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dorinthea-about.md",
    story_type="heroes-of-rathe",
    title="Dorinthea",
    heroes=["dorinthea", "hala"],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.HAND_OF_SOL,
        loc.THE_GOLDEN_FIELDS,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    weapons=["dawnblade", "dawnblade-resplendent"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/baalghor-about.md",
    story_type="heroes-of-rathe",
    title="Baalghor",
    source_link="https://fabtcg.com/hero/baalghor/",
    heroes=["baalghor"],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
        loc.THE_ABYSS,
    ],
    regions=[reg.DEMONASTERY],
    dry_run=True,
)
