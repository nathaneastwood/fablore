"""Canonical kind definitions — what a character *is* (R2).

One flat list. Herald, Aesir, Ancient, Embra and Dragon sit beside Human and
Dwarf, and beside Dog and Parrot, with no sub-column separating an order of
being from a people or an animal — that line is a reading of the lore rather
than a fact the data can check, and a column nothing can validate is a column
that drifts.

``kind_id`` is a hash of the name, so a second ``KindEntry`` literal for
``Human`` reuses this row rather than minting a second one. The real trap is a
*changed* name — that mints a new row and strands the old one, the same as
every other registry id. ``catalogue/characters.py`` references these as ``kind.NAME``;
nothing else does, so no section module needs the import.

The **notes** live in ``descriptions.py``, like every other registry's lore text.
A kind with no notes emits no tooltip, which is the honest state for the
fourteen nobody has written a sentence about.

What is *not* here:

* **Occupations.** ``Wizard``, ``Witch``, ``Sorceress``, ``Illusionist`` and
  ``Diviner`` were kind values on seven characters and are professions. They
  wait for R9 with the seven comma-tails.
* **Memberships.** ``Rosetta`` was a kind value *and* a group; it turned out
  to be both, and both rows exist. ``Maela Soothsayer`` was only ever a
  membership, and Kaysin is on The Maela's roster instead.
* **Volcai and Dracai.** Volcoran castes, and every named Volcoran is a hero
  rather than a character — ``heroes_canonical`` has three columns and no kind, so
  a kind row could hold nobody. They stay group rows.
* **Rathenfolk.** A generic term for the peoples of Rathe, so it sits above
  these rather than beside them. Still a ``concept`` in ``hints_supplement.json``.
"""

from __future__ import annotations

from db import KindEntry


# ---------------------------------------------------------------------------
# Kind proper
# ---------------------------------------------------------------------------

BRUTE = KindEntry("Brute")
CHANEK = KindEntry("Chanek")
DOG = KindEntry("Dog")
DWARF = KindEntry("Dwarf")
GOBLIN = KindEntry("Goblin")
HECKLER = KindEntry("Heckler")
HORSE = KindEntry("Horse")
HUMAN = KindEntry("Human")
MEEP = KindEntry("Meep")
OCTOPUS = KindEntry("Octopus")
PARROT = KindEntry("Parrot")
ROBOT = KindEntry("Robot")
ROSETTA = KindEntry("Rosetta")
WELKIN = KindEntry("Welkin")
ZOMBIE = KindEntry("Zombie")


# ---------------------------------------------------------------------------
# Cosmological — same list, no separate column
# ---------------------------------------------------------------------------

AESIR = KindEntry("Aesir", aliases=("Aesirs",))
ANCIENT = KindEntry("Ancient", aliases=("Ancients",))
DRAGON = KindEntry("Dragon")
EMBRA = KindEntry("Embra", aliases=("Embras",))
HERALD = KindEntry("Herald", aliases=("Angel",))
