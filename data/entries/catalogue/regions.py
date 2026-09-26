"""Canonical region definitions — the ten regions of Rathe.

``region_id`` is a hash of the name, so a misspelling here mints an eleventh
region rather than failing. ``world_of_rathe_story_key`` is left to
``_auto_world_key()``, which resolves each of these to its
``src/world-of-rathe/<slug>.md`` page.

Story modules reference these as ``reg.NAME``.
"""

from __future__ import annotations

from db import RegionEntry


ARIA = RegionEntry("Aria")
DEMONASTERY = RegionEntry("Demonastery")
HIGH_SEAS = RegionEntry("High Seas")
METRIX = RegionEntry("Metrix")
MISTERIA = RegionEntry("Misteria")
NEBULUS_RIFT = RegionEntry("Nebulus Rift")
SOLANA = RegionEntry("Solana")
THE_PITS = RegionEntry("The Pits")
THE_SAVAGE_LANDS = RegionEntry("The Savage Lands")
VOLCOR = RegionEntry("Volcor")
