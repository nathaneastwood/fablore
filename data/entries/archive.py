"""Archive page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.

**Scaffolding only, added 2026-08-22, stage 12.** ``archive`` was already a
valid ``story_type`` — ``db/_domain.py`` lists it in ``upsert_story``'s own
docstring — and ``create_stories_index.py`` has always scanned ``src/archive/``
as one of its content roots. What was missing was somewhere to declare its 78
pages, so this module exists purely so the SECTIONS row has somewhere to point.
It carries **no declarations**. Writing the 63 extractions this root already
has seeded links for is deferred data entry, out of scope here.

**A caveat for whoever writes the first declaration in this module.**
``src/archive/`` holds retired, superseded content — pages the live site has
moved past. A declaration here asserts that an *archived* page links to an
entity, and that assertion can outlive the reason the page was archived. It can
also collide with what a live page says: ``archive/.../graystone-penitentiary.md:19``
and ``world-of-rathe/high-seas.md:125`` already carry the same Absolon sentence,
one with a curly apostrophe and one straight. Before declaring an archive page,
check whether a live page says the same thing, and whether the two should agree.
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
