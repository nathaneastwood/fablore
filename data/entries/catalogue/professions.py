"""Canonical profession definitions — a trade many hold independently (R9).

``profession_id`` is a hash of the name (``registry_ids.profession_id``), so a
second ``ProfessionEntry`` literal for the same trade reuses this row rather
than minting a second one. The real trap is a *changed* name — that mints a
new row and strands the old one, the same as every other registry id.
"""

from __future__ import annotations
