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
        people.RAVEN_AESIR_OF_CHAOS,
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
