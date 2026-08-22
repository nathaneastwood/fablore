"""Canonical species definitions — what a character *is* (R2).

One flat list. Herald, Aesir, Ancient, Embra and Dragon sit beside Human and
Dwarf with no ``kind`` column separating cosmological tier from species proper,
because that line is a reading of the lore rather than a fact the data can
check, and a column nothing can validate is a column that drifts.

``species_id`` is a hash of the name, so a second ``SpeciesEntry`` literal for
``Human`` reuses this row rather than minting a second one. The real trap is a
*changed* name — that mints a new row and strands the old one, the same as
every other registry id. ``catalogue/npcs.py`` references these as ``sp.NAME``;
nothing else does, so no section module needs the import.

The **notes** live in ``descriptions.py``, like every other registry's lore text.
A species with no notes emits no tooltip, which is the honest state for the
fourteen nobody has written a sentence about.

What is *not* here:

* **Occupations.** ``Wizard``, ``Witch``, ``Sorceress``, ``Illusionist`` and
  ``Diviner`` were species values on seven characters and are professions. They
  wait for R9 with the seven comma-tails.
* **Memberships.** ``Rosetta`` was a species value *and* a group; it turned out
  to be both, and both rows exist. ``Maela Soothsayer`` was only ever a
  membership, and Kaysin is on The Maela's roster instead.
* **Volcai and Dracai.** Volcoran castes, and every named Volcoran is a hero
  rather than an NPC — ``heroes_canonical`` has three columns and no species, so
  a species row could hold nobody. They stay group rows.
* **Rathenfolk.** A generic term for the peoples of Rathe, so it sits above
  these rather than beside them. Still a ``concept`` in ``hints_supplement.json``.
"""

from __future__ import annotations

from db import SpeciesEntry


# ---------------------------------------------------------------------------
# Species proper
# ---------------------------------------------------------------------------

BRUTE = SpeciesEntry("Brute")
"""feudmasters.md:31 pairs them with the Chanek — "a team made up of Chanek and
our more amiable Brutes" — two peoples staffing one guild, which is what marks
this a species rather than a build (the user's call, 2026-08-20)."""
CHANEK = SpeciesEntry("Chanek")
"""The green-skinned, pointed-eared Rathenfolk of the far west. No NPC row
carries it yet; the species is attested and the characters are not."""
DOG = SpeciesEntry("Dog")
DOGG = SpeciesEntry("Dogg")
"""Not a misspelling of ``Dog``. metrix.md:91 writes it twice — "his trusty (and
rusty) pet junkyard dogg Charlotte", "The dogg is just faster" — against Biski,
whom his own page calls one of Farin the Porter's sled dogs."""
DWARF = SpeciesEntry("Dwarf")
GOBLIN = SpeciesEntry("Goblin")
HORSE = SpeciesEntry("Horse")
HUMAN = SpeciesEntry("Human")
MEEP = SpeciesEntry("Meep")
OCTOPUS = SpeciesEntry("Octopus")
PARROT = SpeciesEntry("Parrot")
ROBOT = SpeciesEntry("Robot")
ROSETTA = SpeciesEntry("Rosetta")
"""A people as well as an order (the user's call, 2026-08-20). essence-of-decay.md:9
gives Ozrim "a groan of protesting Oakwood" and a voice that "oozed as sluggishly
as sap"; the-land-of-legends.md:35 seats the Queen of Candlehold on "a throne of
elderwood" and calls them "her people". The ``Rosetta`` group row stays and both
carry a word-for-word identical summary, so it does not matter which wins the
tooltip — the same move ``Registry`` made."""
WELKIN = SpeciesEntry("Welkin")
ZOMBIE = SpeciesEntry("Zombie")


# ---------------------------------------------------------------------------
# Cosmological — same list, no separate column
# ---------------------------------------------------------------------------

AESIR = SpeciesEntry("Aesir", aliases=("Aesirs",))
"""Absorbs the ``Aesir`` supplement entry, whose hand-written match array carried
the plural. The three "Aesir of —" epithets are titles and wait for stage 7."""
ANCIENT = SpeciesEntry("Ancient", aliases=("Ancients",))
"""Absorbs the ``Ancients`` supplement entry. The species value on the NPC rows is
singular and the prose is plural, so the alias is what joins them."""
DRAGON = SpeciesEntry("Dragon")
EMBRA = SpeciesEntry("Embra", aliases=("Embras",))
"""Absorbs the ``Embra`` supplement entry and its plural."""
HERALD = SpeciesEntry("Herald")
"""Eight NPCs, every one of them carrying at least one Archangel epithet. No
supplement entry ever existed, so this row has no notes and no tooltip yet."""
