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


DREGS = MonsterEntry("Dregs")
GLUTGORR = MonsterEntry("Glutgorr")
NECROPHAGE = MonsterEntry("Necrophage")
PUPPETEER = MonsterEntry("Puppeteer")
RAVENIR = MonsterEntry("Ravenir")
SHADOWREALM_WALKER = MonsterEntry("Shadowrealm Walker")
