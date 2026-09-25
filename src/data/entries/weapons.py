"""Weapon page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.

**Scaffolding only, added 2026-08-22, stage 12.** ``weapons`` was already a
valid ``story_type`` — ``db/_domain.py`` lists it in ``upsert_story``'s own
docstring — and ``create_stories_index.py`` has always scanned ``src/weapons/``
as one of its content roots. What was missing was somewhere to declare its 16
pages, so this module exists purely so the SECTIONS row has somewhere to point.
It carries **no declarations**. Writing the extractions this root's pages
already have seeded links for is deferred data entry, out of scope here.
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
    path="src/weapons/rok.md",
    story_type="weapons",
    title="Rok",
    weapons=["rok"],  # the page is the lore letter for this weapon
    characters=[
        "emperor",
        people.ADU,
    ],
    locations=[
        loc.IMPERIAL_PALACE,
        loc.DRAGON_FESTIVAL,
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/cintari-saber.md",
    story_type="weapons",
    title="Cintari Saber",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    groups=[grp.CINTARI],
    weapons=["cintari-saber"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/armed-to-the-teeth.md",
    story_type="weapons",
    title="Armed to the Teeth",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    regions=[reg.ARIA, reg.METRIX, reg.MISTERIA, reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/mandible-claw.md",
    story_type="weapons",
    title="Mandible Claw",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    weapons=["mandible-claw"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/hanabi-blaster.md",
    story_type="weapons",
    title="Hanabi Blaster",
    characters=["emperor"],
    # Same letter template as rok.md: the Imperial Palace and the Dragon Festival.
    locations=[loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    regions=[reg.SOLANA, reg.VOLCOR, reg.THE_SAVAGE_LANDS],
    # :5 "the Cogworks conglomerate" — read as Cogwerx; the page also writes
    # "metrics" for Metrix, so its spellings are not evidence of a second entity.
    groups=[grp.COGWERX],
    weapons=["hanabi-blaster"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/nebula-blade.md",
    story_type="weapons",
    title="Nebula Blade",
    characters=[
        "viserai",
        people.AELIUS,
        people.GRAND_MAGISTER_THE_RADIANT,
        people.LADY_VERA_SUTCLIFFE,
        people.LETO,  # :3 — the templar who inherited the Blade of Eridani
        people.LORD_SUTCLIFFE,
    ],
    locations=[loc.THE_GOLDEN_FIELDS],
    regions=[reg.DEMONASTERY, reg.METRIX, reg.SOLANA],
    groups=[grp.HAND_OF_SOL, grp.THE_LIGHT_OF_SOL],
    weapons=["nebula-blade"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/merciless-battleaxe.md",
    story_type="weapons",
    title="Merciless Battleaxe",
    characters=["emperor", people.GENERAL_KODA],
    locations=[loc.SWORYUK_GORGE, loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    regions=[reg.VOLCOR],
    weapons=["merciless-battleaxe"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/plasma-barrel-shot.md",
    story_type="weapons",
    title="Plasma Barrel Shot",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    # "The Teklo Corporation" (:1) — read as Teklo Industries.
    groups=[grp.TEKLO_INDUSTRIES],
    weapons=["plasma-barrel-shot"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/reaping-blade.md",
    story_type="weapons",
    title="Reaping Blade",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    weapons=["reaping-blade"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/red-liner.md",
    story_type="weapons",
    title="Red Liner",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    regions=[reg.THE_PITS],
    weapons=["red-liner"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/sandscour-greatbow.md",
    story_type="weapons",
    title="Sandscour Greatbow",
    characters=["emperor", people.SHAYA_SANDSCOUR],
    locations=[loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    regions=[reg.VOLCOR],
    weapons=["sandscour-greatbow"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/savage-claw.md",
    story_type="weapons",
    title="Savage Claw",
    fauna=[fauna.SKERA, fauna.BRAWNHIDE, fauna.ANK_IS],
    weapons=["savage-claw"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/sledge-of-anvilheim.md",
    story_type="weapons",
    title="Sledge Of Anvilheim",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    weapons=["sledge-of-anvilheim"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/surgent-aethertide.md",
    story_type="weapons",
    title="Surgent Aethertide",
    characters=["emperor"],
    regions=[reg.VOLCOR],
    locations=[loc.IMPERIAL_PALACE, loc.DRAGON_FESTIVAL],
    weapons=["surgent-aethertide"],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/talishar-lost-prince.md",
    story_type="weapons",
    title="Talishar Lost Prince",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    weapons=["talishar-the-lost-prince"],
    fauna=[fauna.REK_VAS],
    dry_run=True,
)

db.upsert_story(
    path="src/weapons/zephyr-needle.md",
    story_type="weapons",
    title="Zephyr Needle",
    source_link="https://fabtcg.com/articles/armed-teeth/",
    publication_date="2020-08-17",
    weapons=["zephyr-needle"],
    dry_run=True,
)
