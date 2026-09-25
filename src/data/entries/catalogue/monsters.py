"""Canonical monster definitions.

``monster_id`` is a hash of the name alone, so unlike a location these cannot
fork on a second field — but a misspelling still mints a new row, and one list is
how you notice the near-duplicate before it becomes one.

``description`` is deliberately absent: monster lore text belongs to
``descriptions.py``, which owns that column. Story modules reference these as
``mon.NAME``.
"""

from __future__ import annotations

from db import MonsterEntry


BEREDOS = MonsterEntry("Beredos")
DIAPHENES = MonsterEntry("Diaphenes")
DREGS = MonsterEntry("Dregs")
GLUTGORR = MonsterEntry("Glutgorr")
GOLEM = MonsterEntry("Golem")
"""main-story/rosetta/secret-of-the-aetherscribes.md — one stone golem at the Arcturos
vault and Oscilio's winged metal sentries, one entry for both."""
GUCAI = MonsterEntry("Gucai")
"""main-story/the-hunted/mark-of-a-traitor.md:53 — twisted, illusion-born flesh-and-glass
creatures; the term recurs on cleanse-the-corruption.md and hunter-and-hunted-both.md."""
LYSAGENES = MonsterEntry("Lysagenes")
MANI = MonsterEntry("Mani")
NECROPHAGE = MonsterEntry("Necrophage")
PUPPETEER = MonsterEntry("Puppeteer")
RAVENIR = MonsterEntry("Ravenir")
SCAPHUS = MonsterEntry("Scaphus")
SHADOWREALM_WALKER = MonsterEntry("Shadowrealm Walker")
WHISPER = MonsterEntry("Whisper")
"""Diaphenes, Beredos, Lysagenes, Mani, Scaphus and Whisper are the named
"Oddities and Specimens" of world-of-rathe/demonastery.md:103-131 — individuals,
not species. Mani and Whisper may belong in characters instead."""
