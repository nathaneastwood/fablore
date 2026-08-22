"""fablore database package — public API.

Import :class:`Database` and the entity dataclasses from here::

    from db import (
        Database,
        FaunaEntry,
        FloraEntry,
        FoodDrinkEntry,
        GroupEntry,
        LocationEntry,
        MonsterEntry,
        NarratedVideoEntry,
        NPCEntry,
        ProfessionEntry,
        RegionEntry,
        SpeciesEntry,
        StoryRecord,
        TitleEntry,
    )
"""

from db._domain import (  # noqa: F401
    Database,
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    GroupEntry,
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    ProfessionEntry,
    RegionEntry,
    SpeciesEntry,
    StoryRecord,
    TitleEntry,
)
