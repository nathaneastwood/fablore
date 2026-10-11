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
    holders=(
        (people.GRAND_MAGISTER_THE_DEVOUT, 1, "world-of-rathe/solana.md"),
        (people.GRAND_MAGISTER_THE_ADAMANT, 2, "world-of-rathe/solana.md"),
        (people.GRAND_MAGISTER_THE_RADIANT, 3, "world-of-rathe/solana.md"),
        (people.GRAND_MAGISTER_THE_BELOVED, 4, "world-of-rathe/solana.md"),
        (people.GRAND_MAGISTER_THE_STEADFAST, 5, "world-of-rathe/solana.md"),
    ),
)

MAGISTER = TitleEntry(
    "Magister",
    holders=((people.THE_LIBRARIAN, 0, "other-characters/the-librarian.md"),),
)
