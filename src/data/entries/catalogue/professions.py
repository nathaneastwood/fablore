"""Canonical profession definitions — a trade many hold independently (R9).

``profession_id`` is a hash of the name (``registry_ids.profession_id``), so a
second ``ProfessionEntry`` literal for the same trade reuses this row rather
than minting a second one. The real trap is a *changed* name — that mints a
new row and strands the old one, the same as every other registry id.

``catalogue/npcs.py`` will reference these as ``prof.NAME`` once the first
profession lands; nothing else should import this module. See
``entries/catalogue/species.py`` for the same one-way shape.

The **notes** live in ``descriptions.py``, like every other registry's lore
text.

**Scaffolding only.** This module carries no constants yet — Braumeister and
the other fourteen names identified while designing this table (see
``plans/character-groups-schema-options.md`` §3B and R9) are deferred data
entry, out of scope for the schema-and-declaration-surface stage that created
this file. ``hints_supplement.json`` still holds a hand-written ``Braumeister``
entry under ``organisation``; migrating it is part of that later pass, not
this one.
"""

from __future__ import annotations
