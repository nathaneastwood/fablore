"""World of Rathe page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.

**Added 2026-08-21, stage 5 (the user's call).** ``world-of-rathe`` was already a
valid ``story_type`` — ``db/_domain.py`` lists it in ``upsert_story``'s own
docstring, and ``create_stories_index.py`` has always put all eleven pages in
``stories``. What was missing was somewhere to declare them, so the eleven rows
sat in the spine with nothing able to link an entity to them. That was not a
schema limit; it was a hole in this package.

This module was the **eighth** of the eleven ``SECTIONS`` rows, added because
Absolon needed it and nothing else was in scope at the time. ``archive`` (78
stories), ``equipment`` (19) and ``weapons`` (16) stayed undeclarable until
stage 12 (2026-08-22) gave each one a module of its own, so ``entries/`` now
covers **11 of the 11 story types** the index produces.

Those three modules are scaffolding and carry no declarations. The 63 of their
113 pages that already hold seeded entity links remain undeclared, and that is
not a bug to fix in passing: each is its own decision about whether an archived
or reference page should assert a relationship at all.

This module starts with **one declaration of eleven pages**, and that is
deliberate rather than unfinished. ``high-seas.md`` is declared for the entities
stage 5 needed and no others (the user's call) — see the call for what that
leaves out.
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

# PARTIAL BY DECISION, NOT BY OMISSION (the user's call, 2026-08-21).
#
# This page is 4471 words across 29 sections and names a great many locations,
# regions and characters. This call declares none of them. Only the entities stage 5
# needed are here: the two gods, the two groups this page already documents by
# lore_story_key, and Dhani Deities — three groups, not the two this said until
# 2026-08-21. See the note on grp.DHANI_DEITIES below for why the third is here.
#
# The page is not link-free, though: five location links (Cogwerx Conglomerate,
# Dagger Docks, Griefers Reef, Kraken's Barrel, Trōpal-Dhani) were seeded onto it
# and survive because `locations=` is omitted rather than emptied. Omission
# preserves; an empty list would delete them.
#
# Anyone extending this call should treat the absences as unexamined rather than
# as decided — the opposite of every other declaration in entries/, where an
# entity left out was looked at and rejected. A full extraction of this page is
# its own gated pass.
#
# Absolon is the reason the module exists. He is named as a god here at :125 —
# "an ancient Dhani cult that worshipped Absolon, god of the great deep" — and
# nowhere else. The eight mentions on the already-declared
# main-story/high-seas/captain-bones-and-the-city-of-gold.md are every one of
# them the Kuraghan flagship "Absolon's Dream", never the deity.
#
# Nocetes did not need the module: captain-bones names the god outright. He is
# declared here anyway because :143 is where this page names him, and because the
# two gods share one roster.
db.upsert_story(
    path="src/world-of-rathe/high-seas.md",
    story_type="world-of-rathe",
    title="High Seas",
    # Not decoration. The story row already held this, and the first dry run of
    # this declaration reported "Cleared: - Source" — omitting it is a deletion,
    # because story metadata is replace-semantic like every junction. The eleven
    # world-of-rathe rows were seeded by create_stories_index.py and carry source
    # links that no declaration has ever had to preserve before, this module
    # being the first that can touch them.
    source_link="https://fabtcg.com/world-of-rathe/high-seas/",
    characters=[
        people.ABSOLON,
        people.NOCETES,
    ],
    groups=[
        # Both already carry lore_story_key pointing at this page, so the page
        # documented them while nothing linked them to it.
        grp.KURAGHAN,
        grp.THE_DHANI_EMPIRE,
        # The page describes the Dhani pantheon rather than naming it — the same
        # footing as "Speakeasy's Guilds", where the group name is the page's own
        # phrasing rather than an in-world proper noun. This link is also what
        # writes the roster and, through the parent walk, the Deities row itself:
        # reachability runs group -> members, never member -> group, so without a
        # declaration naming it the pantheon would exist only in the catalogue.
        grp.DHANI_DEITIES,
    ],
    dry_run=True,
)
