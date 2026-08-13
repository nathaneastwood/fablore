"""Hero page registrations — one ``db.upsert_story`` call per page.

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
    fauna=[fauna.FLARE_DEER],
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
