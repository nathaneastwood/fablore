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
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    RegionEntry,
)
from entries._runner import db

db.upsert_story(
    path="src/heroes-of-rathe/aurora-about.md",
    story_type="heroes-of-rathe",
    title="Aurora",
    heroes=["aurora"],
    locations=[
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Volthaven", region="Aria", lore_fragment="enion"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
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
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
    ],
    regions=[RegionEntry("Aria")],
    weapons=["volzar-the-lightning-rod"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zyggy-about.md",
    story_type="heroes-of-rathe",
    title="Zyggy Starlight",
    heroes=["zyggy", "oscilio"],
    regions=[RegionEntry("Nebulus Rift")],
    locations=[
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
    ],
    weapons=["aphrodias"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/blaze-about.md",
    story_type="heroes-of-rathe",
    title="Blaze",
    heroes=["blaze"],
    regions=[RegionEntry("Volcor")],
    locations=[
        LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court"),
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
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("The Golden Fields", region="Solana"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
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
        LocationEntry("i'Arathael"),
        LocationEntry("Shadowrealm"),
        LocationEntry("The Abyss"),
    ],
    regions=[RegionEntry("Demonastery")],
    dry_run=True,
)
