"""fablore database package — public API.

Import :class:`Database` and the entity dataclasses from here::

    from db import (
        Database,
        FaunaEntry,
        FloraEntry,
        FoodDrinkEntry,
        LocationEntry,
        MonsterEntry,
        NarratedVideoEntry,
        NPCEntry,
        RegionEntry,
        StoryRecord,
    )
"""

from db._domain import (  # noqa: F401
    Database,
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    RegionEntry,
    StoryRecord,
)
