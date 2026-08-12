"""Canonical entity definitions, referenced by the story declarations.

Three files own three different things, and keeping them apart is what stops the
database growing duplicate rows for one in-world thing:

* **``entries/catalogue/``** (here) — *what an entity is*. One constant per NPC,
  location and region, carrying the fields that make up its identity.
* **``entries/*.py``** — *which page links to what*. Relationships only; the
  declarations reference the constants here and never construct their own.
* **``descriptions.py``** — *the lore text* (location ``notes``, monster/fauna/
  flora ``description``). It writes the same rows and must stay the only writer.

Why references rather than literals: every registry id is a hash of the fields
written at the call site — an NPC *is* its name, a location *is* its name and its
region. A second literal for the same entity therefore does not reuse the first
row, it mints a second one, and nothing raises. Referencing a shared constant
makes that impossible, and turns a typo into an ``AttributeError`` on import —
the same protection ``heroes=``/``weapons=``/``equipment=`` already get from
raising on an unknown canonical slug.

``tests/test_data_entry.py`` enforces both halves: no section module may
construct one of these types, and no two constants here may hash to the same id.
"""
