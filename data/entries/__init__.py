"""Story registrations, one module per story type.

Each module in this package is a flat list of ``db.upsert_story(...)`` calls —
one per page — that execute on import. Together they are the reviewable record
of which entities every page links to: the diff of a call is what a page
declares, and the comments around it are why.

**Relationships only.** A call here says a page links to an entity. It never
sets lore text — location ``notes`` and monster/fauna/flora ``description``
values are owned exclusively by ``descriptions.py``, which writes the same
database columns. See that file's header for the reasoning.

**References, not definitions.** Every entity with a registry table — NPCs,
locations, regions, monsters, fauna, flora, food and drink — is defined once in
``entries/catalogue/`` and referenced here as ``npc.NAME``, ``loc.NAME``,
``reg.NAME``, ``mon.NAME``, ``fauna.NAME``, ``flora.NAME`` or ``food.NAME``.
Their ids are hashes of the fields written at the call site, so a literal here
would not reuse the entity's row — it would mint a second one, and nothing would
raise. The entry classes are deliberately absent from the section modules'
imports so that writing one is a ``NameError``. ``NarratedVideoEntry`` is the
exception and stays inline: it has no registry table and no id.

Run them with ``python3 src/data/data-entry.py`` (see that file for the
preview-then-commit workflow). Nothing here imports the section modules, so
importing this package is free of side effects — only the runner executes them.

Adding a story type means adding a module and a ``SECTIONS`` row: the mapping
is one module per ``story_type``, and ``tests/test_data_entry.py`` enforces
that every declaration lives in the module its path implies.
"""

from __future__ import annotations

# module name -> the story_type every declaration in it must carry. Ordered as
# the runner executes them.
SECTIONS: dict[str, str] = {
    "heroes": "heroes-of-rathe",
    "main_story": "main-story",
    "short_stories": "short-stories",
    "other_characters": "other-characters",
    "summaries": "summaries",
    "flavour": "flavour",
    "digital_tiles": "digital-tiles",
}
