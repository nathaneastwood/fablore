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
"""feudmasters.md:31 pairs them with the Chanek — "a team made up of Chanek and
our more amiable Brutes" — two peoples staffing one guild, which is what marks
this a kind rather than a build (the user's call, 2026-08-20)."""
CHANEK = KindEntry("Chanek")
"""The green-skinned, pointed-eared Rathenfolk of the far west. No character row
carries it yet; the kind is attested and the characters are not."""
DOG = KindEntry("Dog")
DWARF = KindEntry("Dwarf")
GOBLIN = KindEntry("Goblin")
HECKLER = KindEntry("Heckler")
"""savage-lands.md:77-91 — "ruthless, feral and violent", nomadic, raiding in small
groups; no named leader or roster, which is what marks this a people rather than a
group, on the ``BRUTE`` precedent. faq.md:11 lists them among the "races of Rathe"
alongside Brutes. No character row carries it yet; the kind is attested and the
characters are not, same as ``CHANEK``."""
HORSE = KindEntry("Horse")
HUMAN = KindEntry("Human")
MEEP = KindEntry("Meep")
OCTOPUS = KindEntry("Octopus")
PARROT = KindEntry("Parrot")
ROBOT = KindEntry("Robot")
ROSETTA = KindEntry("Rosetta")
"""A people as well as an order (the user's call, 2026-08-20). essence-of-decay.md:9
gives Ozrim "a groan of protesting Oakwood" and a voice that "oozed as sluggishly
as sap"; the-land-of-legends.md:35 seats the Queen of Candlehold on "a throne of
elderwood" and calls them "her people". The ``Rosetta`` group row stays and both
carry a word-for-word identical summary, so it does not matter which wins the
tooltip — the same move ``Registry`` made."""
WELKIN = KindEntry("Welkin")
ZOMBIE = KindEntry("Zombie")


# ---------------------------------------------------------------------------
# Cosmological — same list, no separate column
# ---------------------------------------------------------------------------

AESIR = KindEntry("Aesir", aliases=("Aesirs",))
"""Absorbs the ``Aesir`` supplement entry, whose hand-written match array carried
the plural. The three "Aesir of —" epithets are titles and wait for stage 7."""
ANCIENT = KindEntry("Ancient", aliases=("Ancients",))
"""Absorbs the ``Ancients`` supplement entry. The kind value on the character rows is
singular and the prose is plural, so the alias is what joins them."""
DRAGON = KindEntry("Dragon")
EMBRA = KindEntry("Embra", aliases=("Embras",))
"""Absorbs the ``Embra`` supplement entry and its plural."""
HERALD = KindEntry("Herald", aliases=("Angel",))
"""Eight characters, every one of them carrying at least one Archangel epithet —
four wear it as their display name and four carry it as an epithet row, so the
rank is uniform across the order rather than dividing it.

A kind and not a title (the user's call, 2026-08-25). Nobody *becomes* a Herald:
prism-about.md:9 calls them "Sol's golden emissaries" and
stories-of-illumination.md:23 "emissaries of Sol, bastions of the Light", and
prism-about.md:11 calls them "these legendary beings" whose forms Prism learns to
conjure. That is an order of being, like Aesir. `Angel` is an alias rather than
the name because the lore says Herald throughout; the game's "Angel Ally" is the
other name it answers to, which is exactly what an alias is for.

No supplement entry ever existed, so this row has no notes and no tooltip yet."""
