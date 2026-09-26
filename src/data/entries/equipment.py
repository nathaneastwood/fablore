"""Equipment page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.

**Scaffolding only, added 2026-08-22, stage 12.** ``equipment`` was already a
valid ``story_type`` — ``db/_domain.py`` lists it in ``upsert_story``'s own
docstring — and ``create_stories_index.py`` has always scanned
``src/equipment/`` as one of its content roots. What was missing was somewhere
to declare its 19 pages, so this module exists purely so the SECTIONS row has
somewhere to point. It carries **no declarations**. Writing the extractions
this root's pages already have seeded links for is deferred data entry, out of
scope here.
"""

from __future__ import annotations

# Entities are referenced, never constructed. Every registry id is a hash of the
# fields written at the call site, so a second literal for the same entity
# competes with the first row instead of reusing it — that is how "The Shadow
# Crypts" became two rows. The canonical definition of each lives in
# entries/catalogue/; none of the entry classes are imported here, so writing
# LocationEntry(...) is a NameError rather than a silent new row.
from entries.catalogue import (  # noqa: F401
    characters as people,
    fauna,
    flora,
    food_drink as food,
    groups as grp,
    locations as loc,
    monsters as mon,
    regions as reg,
)

# NarratedVideoEntry is the one exception: a narrated reading belongs to one
# story, has no registry table and no id of its own, so it is per-declaration
# data rather than a shared entity.
from db import NarratedVideoEntry  # noqa: F401
from entries._runner import db  # noqa: F401

db.upsert_story(
    path="src/equipment/skullhorn.md",
    story_type="equipment",
    title="Skullhorn",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    # authors/artists/thumbnail_image_link omitted — DB row holds them empty
    # and the page carries no footer byline.
    equipment=["skullhorn"],  # the item this page is about; slug exists in db.list_equipment()
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/amethyst-tiara.md",
    story_type="equipment",
    title="Amethyst Tiara",
    characters=["emperor"],
    regions=[reg.VOLCOR],
    locations=[loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    groups=[grp.DRACAI],  # "our courageous Dracai" (:5)
    equipment=["amethyst-tiara"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/blazen-yoroi.md",
    story_type="equipment",
    title="Blazen Yoroi",
    characters=["emperor"],
    regions=[reg.VOLCOR],
    locations=[loc.FOREST_OF_FLAMES, loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    equipment=["blazen-yoroi"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/bloodsheath-skeleta.md",
    story_type="equipment",
    title="Bloodsheath Skeleta",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    equipment=["bloodsheath-skeleta"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/bolt-n-boots.md",
    story_type="equipment",
    title="Bolt'N' Boots",
    regions=[reg.THE_PITS],
    locations=[loc.BLACKJACK_S_TAVERN],  # "wandered into Blackjack's" — read as the tavern; unconfirmed
    equipment=["boltn-boots"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/crater-fist.md",
    story_type="equipment",
    title="Crater Fist",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    equipment=["crater-fist"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/grimoire-of-fellingsong.md",
    story_type="equipment",
    title="Grimoire Of Fellingsong",
    characters=["vynnset", people.NASRETH],
    regions=[reg.DEMONASTERY],
    equipment=["grimoire-of-fellingsong"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/in-the-fires-of-the-forge.md",
    story_type="equipment",
    title="In the Fires of the Forge",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/metacarpus-node.md",
    story_type="equipment",
    title="Metacarpus Node",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    equipment=["metacarpus-node"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/viziertronic-model-i.md",
    story_type="equipment",
    title="Viziertronic Model I",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    equipment=["viziertronic-model-i"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/wind-cutter.md",
    story_type="equipment",
    title="Wind Cutter",
    regions=[reg.MISTERIA],
    equipment=["wind-cutter"],
    groups=[grp.HOUSE_MIHARU],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/breeze-rider-boots.md",
    story_type="equipment",
    title="Breeze Rider Boots",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    equipment=["breeze-rider-boots"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/celestial-kimono.md",
    story_type="equipment",
    title="Celestial Kimono",
    characters=["emperor"],
    locations=[loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    regions=[reg.VOLCOR, reg.MISTERIA],
    groups=[grp.OKARI_CLAN],
    equipment=["celestial-kimono"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/comeback-kicks.md",
    story_type="equipment",
    title="Comeback Kicks",
    characters=[people.GRANNIE_SANDLAR],
    locations=[loc.THE_MOAT, loc.DEATHMATCH_ARENA],
    groups=[grp.SANDLARS],
    equipment=["comeback-kicks"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/courage-of-bladehold.md",
    story_type="equipment",
    title="Courage Of Bladehold",
    source_link="https://fabtcg.com/articles/fires-forge/",
    publication_date="2020-08-18",
    # "the amphitheatre" (:3) is lowercase and unplaced — not linked to Solana's.
    equipment=["courage-of-bladehold"],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/myrkhellir-helm.md",
    story_type="equipment",
    title="Myrkhellir Helm",
    equipment=["myrkhellir-helm"],
    locations=[loc.MYRKHELLIR],
    # "the Old Ones" is still held for the user: it recurs unmodelled.
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/seasoned-saviour.md",
    story_type="equipment",
    title="Seasoned Saviour",
    equipment=["seasoned-saviour"],
    characters=["emperor", people.GENERAL_UMADESU],
    regions=[reg.VOLCOR],
    locations=[loc.DRAGON_FESTIVAL, loc.IMPERIAL_PALACE],
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/synapse-sparkcap.md",
    story_type="equipment",
    title="Synapse Sparkcap",
    equipment=["synapse-sparkcap"],
    characters=["teklovossen"],
    regions=[reg.METRIX],
    locations=[loc.COGMIRE_S_SALVAGE_EMPORIUM_AND_WORKSHOPPE],  # the page uses the short form
    dry_run=True,
)

db.upsert_story(
    path="src/equipment/trench-of-watery-depths.md",
    story_type="equipment",
    title="Trench Of Watery Depths",
    equipment=["trench-of-watery-depths"],
    characters=[people.CAPTAIN_RUE],
    regions=[reg.HIGH_SEAS],
    groups=[grp.THE_DHANI_EMPIRE],
    dry_run=True,
)
