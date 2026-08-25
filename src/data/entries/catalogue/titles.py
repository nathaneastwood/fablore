"""Canonical title definitions — offices, with the people who have held them.

``title_id`` hashes the name alone, so a second spelling mints a second row.
This file is the only place a title name is written; the story declarations
reference ``ttl.NAME``.

**Holders are declared here, not on the story**, for the reason ``groups.py``
gives for rosters: "the Steadfast is the fifth Grand Magister" is a world fact
with no single page to hang it from. Mentions still belong to the story, via
``upsert_story(titles=[...])``. The two answer different questions — the holder
list answers "who has held this office", the mention answers "which pages name
it".

An office is not a kind and not a group. ``.claude/rules/data-pipeline.md``
§"Kind, title, group" draws the line: a **kind** is what someone *is* and cannot
be resigned; a **title** is an office *held*, and can end; a **group** is a body
*joined*. Grand Magister is the clearest title in the setting — five people have
held it in succession, and four of them no longer do.

``ordinal`` records that succession where the lore gives one, and is ``0`` where
it does not. ``story_key`` cites the page that attests the holder.

**The office is still glued into four character names.** ``characters.py`` holds
``Grand Magister, the Devout`` and four siblings — one row per holder with the
title baked into the display name, which is the shape this table exists to
replace. Untangling them renames a character, and ``lore_character_id`` hashes
the name, so each rename mints a new id and strands that row's story links: the
same repointing the Teklovossen merge needed. The title rows below are correct
without it, so the rename is a separate decision, not a prerequisite.
"""

from __future__ import annotations

from db import TitleEntry

from . import characters as people

# ---------------------------------------------------------------------------
# Solana — the Order of the Light
# ---------------------------------------------------------------------------

GRAND_MAGISTER = TitleEntry(
    "Grand Magister",
    holders=((people.GRAND_MAGISTER_THE_STEADFAST, 5, "world-of-rathe/solana.md"),),
)
"""The office that leads Solana's Grand Council.

``world-of-rathe/solana.md`` names all five in order — the Devout, the Adamant,
the Radiant, the Beloved and the Steadfast, "the fifth and current" — so the
ordinals are read off the page rather than inferred. Only the Steadfast is
declared here (the user's call); the other four are attested in that same
sentence and are one line each when wanted.

**Holders are replace-semantic.** Adding the earlier four means adding them to
this tuple, not to a second declaration — a shorter list is a deletion, and the
dry run prints a ``REMOVED`` line for exactly that reason."""

MAGISTER = TitleEntry(
    "Magister",
    holders=((people.THE_LIBRARIAN, 0, "other-characters/the-librarian.md"),),
)
"""One of the eight seats beneath the Grand Magister — a different office, not a
lesser grade of the same one.

``other-characters/the-librarian.md`` is explicit that the eight "work alongside
the Grand Magister", and that "one Magister watches over the Library of
Illumination"; ``world-of-rathe/solana.md`` names only five people as Grand
Magisters and the Librarian is not among them. Registering the Librarian under
``GRAND_MAGISTER`` would assert something both pages contradict.

``ordinal`` is ``0``: the eight seats carry no stated succession, which is the
case that field's ``0`` exists for.

The Librarian is a playable hero *and* an ordinary character — one
``characters`` row (``LC158fd93075``), linked to canonical hero
``the-librarian``. ``people.THE_LIBRARIAN`` and the bare slug ``"the-librarian"``
resolve to that same row through ``character_heroes``; the constant is used here
because it is the identity, and the slug is only one of its names. This is the
case migration 12 was built for, and X01 was the defect it closed."""
