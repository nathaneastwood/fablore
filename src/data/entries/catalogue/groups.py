"""Canonical group definitions — houses, clans, guilds, orders and troupes.

``group_id`` hashes the name alone, so a second spelling mints a second row.
This file is the only place a group name is written; the story declarations
reference ``grp.NAME``. The 42 names parked across the ``# TODO: group —``
backlog were folded down to the 39 rows below, and five of those 42 turned out
not to be groups at all — ``Runeblades`` is a game class, ``The Grey`` a person,
``Shieldbearers`` a rank, ``Glory of Sol`` an ideal, ``Lost Clans`` a phrase.
The reasoning for every name, and the variant spellings each one absorbed, is in
``plans/group-canonical-names.md``.

**Membership is declared here, not on the story.** That is a deliberate
departure from the rule that the catalogue holds identity only: "Tara VanGeld is
a VanGeld" is a world fact with no page to hang it from, so no ``upsert_story``
call could assert it. Mentions still belong to the story, via
``upsert_story(groups=[...])``. Both exist and answer different questions — the
roster answers "who belongs", the mention answers "which pages name this group".
See D1 in ``plans/character-groups-schema-options.md``.

``member_source`` cites the page the roster was read off (D2). A roster with no
citation is unsourced lore, so an uncited membership is left out rather than
guessed: most groups below carry no members yet, and that is the honest state,
not an oversight.

Import direction is one-way — this module imports ``npcs.py`` and names hero
slugs as strings, and nothing imports this module back — so no cycle is possible.
"""

from __future__ import annotations

from db import GroupEntry

from . import locations as loc
from . import npcs as npc


# ---------------------------------------------------------------------------
# Deathmatch Super Slam guilds
# ---------------------------------------------------------------------------
# Guild-to-fightmaster affiliation (Speakeasy's, Batbiter's, Moloca's) is a
# group-to-person relation, not a parent group, so it is not modelled here.

BALEFUL_HORDE = GroupEntry(
    "Baleful Horde",
    kind="guild",
    npc_members=(npc.FUGGER_GRIMES,),
    member_source="flavour/super-slam.md",
)
BIG_BOPPERS = GroupEntry("Big Boppers", kind="guild")
BOULDERS = GroupEntry("Boulders", kind="guild")
"""Absorbs ``Boulder Clan``; one guild, not a guild plus a dwarven clan (Q3)."""
CHAMPIONS_OF_CHIVALRY = GroupEntry(
    "Champions of Chivalry",
    kind="guild",
    npc_members=(npc.EMEVIERE,),
    member_source="flavour/super-slam.md",
)
FURY_FISTS = GroupEntry("Fury Fists", kind="guild")
GLORYTOWN_GLADIATORS = GroupEntry(
    "Glorytown Gladiators",
    kind="guild",
    npc_members=(npc.SALVADOR_STALLION,),
    member_source="flavour/super-slam.md",
)
GORELORDS = GroupEntry("Gorelords", kind="guild")
HEAVY_METALS = GroupEntry("Heavy Metals", kind="guild")
JUNGLE_SLAYERS = GroupEntry(
    "Jungle Slayers",
    kind="guild",
    npc_members=(npc.HELX,),
    member_source="flavour/super-slam.md",
)
"""Absorbs ``Chanek Jungle Slayers``. Chanek is a species, not part of the name (Q4)."""
MYTHMAKERS = GroupEntry("Mythmakers", kind="guild")
PROWLERS = GroupEntry("Prowlers", kind="guild", hero_members=("kayo",))
WILD_WONDERS = GroupEntry("Wild Wonders", kind="guild")


# ---------------------------------------------------------------------------
# Solana
# ---------------------------------------------------------------------------

CHILDREN_OF_THE_LIGHT = GroupEntry("Children of the Light", kind="people")
"""Every citizen inside the walls (solana.md:21). Deliberately rosterless: the
membership is unbounded, so this row exists for mentions only (Q11)."""
GEMINI = GroupEntry("Gemini", kind="order")
HAND_OF_SOL = GroupEntry("Hand of Sol", kind="order")
HOUSE_ASHWOOD = GroupEntry("House Ashwood", kind="house", hero_members=("pleiades",))
HOUSE_GOLDMANE = GroupEntry(
    "House Goldmane",
    kind="house",
    npc_members=(npc.BLOODWORTH_GOLDMANE,),
    hero_members=("lyath", "victor-goldmane"),
    member_source="heroes-of-rathe/lyath-about.md",
)
SISTERS_OF_OCTOTHESIA = GroupEntry("Sisters of Octothesia", kind="order")
THE_LIGHT_OF_SOL = GroupEntry("The Light of Sol", kind="order")


# ---------------------------------------------------------------------------
# Demonastery / Shadow
# ---------------------------------------------------------------------------

DISCIPLES_OF_PAIN = GroupEntry("Disciples of Pain", kind="faction")
GLOOMBLADES = GroupEntry("Gloomblades", kind="faction", hero_members=("viserai",))


# ---------------------------------------------------------------------------
# Volcor
# ---------------------------------------------------------------------------

ALSHONI = GroupEntry("Alshoni", kind="faction")
CHILDREN_OF_THE_DRAGON = GroupEntry("Children of the Dragon", kind="order", hero_members=("fang",))
EZU = GroupEntry("Ezu", kind="faction")


# ---------------------------------------------------------------------------
# Metrix / The Pits
# ---------------------------------------------------------------------------

ARMS_DEALERS = GroupEntry("Arms Dealers", kind="gang")
IRON_ASSEMBLY = GroupEntry("Iron Assembly", kind="organisation")
"""Absorbs ``Iron Council``, shouted once in stroke-of-genius.md (Q2)."""
MENDACITY_MEDIA = GroupEntry("Mendacity Media", kind="corporation")
"""Absorbs ``Mendacity``, ``Voxx`` and the ``Voxx Press`` location row (Q5)."""
STEELSTREET_ENFORCERS = GroupEntry("Steelstreet Enforcers", kind="law enforcement")
TEKLO_INDUSTRIES = GroupEntry("Teklo Industries", kind="corporation", location=loc.TEKLO_INDUSTRIES)
"""The one group that is genuinely also a place: a company and a works, with 14
story links to the location, which is why the location row stays (G05)."""


# ---------------------------------------------------------------------------
# Misteria
# ---------------------------------------------------------------------------

HIDESHI = GroupEntry("Hideshi", kind="house")
IKARU_CLAN = GroupEntry("Ikaru Clan", kind="house", hero_members=("ira",), location=loc.IKARU)
"""Absorbs ``House of Blossoms``. The location row stays as the place Ikaru (Q6)."""
MUGENSHI_CLAN = GroupEntry("Mugenshi Clan", kind="clan", hero_members=("benji",))


# ---------------------------------------------------------------------------
# Aria / Everfest
# ---------------------------------------------------------------------------

GUARDIANS = GroupEntry("Guardians", kind="order")
THE_MAELA = GroupEntry(
    "The Maela",
    kind="troupe",
    npc_members=(npc.MAELA_FAIRMIND,),
    location=loc.THE_EVERFEST_CARNIVAL,
    member_source="flavour/compendium-of-rathe.md",
)
"""Was a locations row (G01). The Carnival link is a ``location``, not a
``parent`` — the Everfest Carnival is a place, and no group row exists for it."""
THE_VALDUR = GroupEntry("The Valdur", kind="troupe", location=loc.THE_EVERFEST_CARNIVAL)
"""Was a locations row (G02). See THE_MAELA on the Carnival link."""
WARDENS = GroupEntry("Wardens", kind="order")


# ---------------------------------------------------------------------------
# Unplaced
# ---------------------------------------------------------------------------

THE_SPIDER = GroupEntry(
    "The Spider",
    kind="organisation",
    hero_members=("uzuri", "arakni-solitary-confinement"),
    member_source="heroes-of-rathe/uzuri-about.md",
)
VANGELD = GroupEntry(
    "VanGeld",
    kind="clan",
    npc_members=(npc.TARA_VANGELD,),
    member_source="heroes-of-rathe/lyath-about.md",
)
"""No "clan" in the name: lyath-about.md writes it as a common noun, and ``kind``
holds it. Sits beside ``Mugenshi Clan``, which keeps its kind word because the
lore always writes it that way — rule N3, follow the lore name by name (Q13)."""
VIPRESSA = GroupEntry("Vipressa", kind="faction")
