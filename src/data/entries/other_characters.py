"""Other-character page registrations — one ``db.upsert_story`` call per page.

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
    characters as people,
    fauna,
    flora,
    food_drink as food,
    groups as grp,
    locations as loc,
    monsters as mon,
    regions as reg,
    titles as ttl,
)

# NarratedVideoEntry is the one exception: a narrated reading belongs to one
# story, has no registry table and no id of its own, so it is per-declaration
# data rather than a shared entity.
from db import NarratedVideoEntry  # noqa: F401
from entries._runner import db


# Registered 2026-08-20 to unstrand Achlys' and Raven's epithets (R4, stage 3).
# Additive: the three hero links and both entry-named links already existed.
db.upsert_story(
    path="src/other-characters/krest-mortimer.md",
    story_type="other-characters",
    title="Dr. Krest Mortimer, 'The Fixer'",
    characters=[
        "arakni-huntsman",
        "arakni-solitary-confinement",
        "arakni-web-of-deceit",
        people.ACHLYS_HAG_OF_MOJIRE,
        people.GAVIN,
        people.LENA_BELLE,
        people.RAVEN,
    ],
    locations=[
        loc.MOJIRE,
        loc.SOUTHMAW,
    ],
    regions=[reg.DEMONASTERY, reg.METRIX, reg.THE_PITS],
    groups=[grp.L_APOCALYPTA],
    # TODO: needs review — Tanner's (too vague to mint a location),
    # Bloodrot Pox / Frailty / Inertia (concepts).
    dry_run=True,
)


# Registered 2026-08-25 (the user's call) alongside the Grand Magister, to
# record that the Librarian holds one of Solana's eight Magister seats — a
# different office, not a lesser grade of the same one. See catalogue/titles.py.
#
# Titles only: the stored Prism link and Solana region link are left alone by
# omitting their kwargs, which preserves. This page is undeclared for the same
# reason solana.md is.
db.upsert_story(
    path="src/other-characters/the-librarian.md",
    story_type="other-characters",
    title="The Librarian",
    # Restated for the same reason as solana.md: these do not preserve on
    # omission, and dropping them would be a silent deletion.
    authors="Nicola Price, Tarryn Thomas",
    artists="Federico Musetti",
    source_link="https://fabtcg.com/articles/librarian/",
    publication_date="2021-05-24",
    titles=[ttl.MAGISTER],
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/minerva-themis.md",
    story_type="other-characters",
    title="Minerva Themis",
    # Restated exactly as the DB row holds them (no footer byline on this page).
    authors="Nicola Price, Tarryn Thomas",
    artists="Mihail Spil-Haufter",
    source_link="https://fabtcg.com/articles/minerva-themis/",
    publication_date="2021-05-17",
    characters=[
        people.MERCURIUS,  # twin brother, named directly (l.3, l.5, l.11)
    ],
    locations=[
        loc.GOLDEN_CHARIOT,  # "the Golden Chariot" (l.9), Minerva's inn — not seeded, adding
        loc.THE_GOLDEN_FIELDS,  # "beyond the Golden Fields" (l.3) — not seeded, adding
    ],
    regions=[reg.METRIX, reg.SOLANA, reg.VOLCOR],  # all three named, restating seeded set unchanged
    groups=[grp.GEMINI],  # "the Gemini" (l.3), "a fellow Gemini" (l.11) — not seeded, adding
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/lord-sutcliffe.md",
    story_type="other-characters",
    title="Lord Sutcliffe",
    authors="Nicola Price, Tarryn Thomas",
    artists="bimawithpencil",
    source_link="https://fabtcg.com/articles/lord-sutcliffe/",
    publication_date="2021-05-10",
    characters=["viserai", people.LORD_SUTCLIFFE],
    regions=[reg.DEMONASTERY],
    groups=[grp.DISCIPLES_OF_PAIN],
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/README.md",
    story_type="other-characters",
    title="Readme",
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/lady-barthimont.md",
    story_type="other-characters",
    title="Lady Barthimont",
    authors="Nicola Price, Tarryn Thomas",
    artists="Carlos Cruchaga",
    source_link="https://fabtcg.com/articles/lady-barthimont/",
    publication_date="2021-05-03",
    characters=[people.LADY_BARTHIMONT, people.LORD_BARTHIMONT],
    locations=[loc.THE_NORTHERN_REALMS],
    regions=[reg.SOLANA],
    dry_run=True,
)
