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

It is the default, not the only option. A member may instead be written as an
``(npc, story_key)`` pair when that one membership is attested somewhere else.
Eleven of the twelve rosters here were read off a single page and use the plain
form; ``THE_MAELA`` is the exception that needed the pair, its five seers named
across four flavour pages with no page listing them together.

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
HAND_OF_SOL = GroupEntry(
    "Hand of Sol",
    kind="order of knights",
    lore_story_key="world-of-rathe/solana.md",
    lore_fragment="the-hand-of-sol",
)
"""Was a locations row with 9 story links. An order of knights is not a place, so
the row is dropped; ``lore_story_key`` is what keeps its link to solana.md alive,
which is the only reason it was ever a location."""
HOUSE_ASHWOOD = GroupEntry("House Ashwood", kind="house", hero_members=("pleiades",))
HOUSE_GOLDMANE = GroupEntry(
    "House Goldmane",
    kind="house",
    npc_members=(npc.BLOODWORTH_GOLDMANE,),
    hero_members=("lyath", "victor-goldmane"),
    member_source="heroes-of-rathe/lyath-about.md",
)

SISTERS_OF_OCTOTHESIA = GroupEntry("Sisters of Octothesia", kind="order")
THE_LIGHT_OF_SOL = GroupEntry(
    "The Light of Sol",
    kind="order of scholars",
    lore_story_key="world-of-rathe/solana.md",
    lore_fragment="the-light-of-sol",
)
"""Was a locations row. The Hand of Sol's matched pair — knights and scholars —
and treated the same way."""


# ---------------------------------------------------------------------------
# Demonastery / Shadow
# ---------------------------------------------------------------------------

CHURCH_OF_PAIN = GroupEntry("Church of Pain", kind="institution")
"""The institution; the Disciples are its followers. Two rows, not one: the
supplement described both and they are not the same thing (2026-08-20)."""
DISCIPLES_OF_PAIN = GroupEntry("Disciples of Pain", kind="faction", parent=CHURCH_OF_PAIN)
GLOOMBLADES = GroupEntry("Gloomblades", kind="faction", hero_members=("viserai",))


# ---------------------------------------------------------------------------
# Volcor
# ---------------------------------------------------------------------------

ALSHONI = GroupEntry("Alshoni", kind="faction")
CHILDREN_OF_THE_DRAGON = GroupEntry("Children of the Dragon", kind="order", hero_members=("fang",))
CINTARI = GroupEntry(
    "Cintari",
    kind="clan",
    npc_members=(npc.ALIF, npc.FAYYAD, npc.SADA),
    hero_members=("kassai",),
    member_source="main-story/heavy-hitters/thirst-for-revenge.md",
)
"""A clan, not a people: kassai-about.md:11 has them *induct* Kassai into their
ranks, a hero trait reads "Leader of the Cintari", and fires-of-rebellion.md:79
has rebels wearing "Cintari disguises". None of that is true of a species, which
is what separates this call from ``Chanek`` (2026-08-20)."""
DRACAI = GroupEntry("Dracai", kind="people")
"""The other half of the Volcoran split, and typed like ``Volcai`` because it is
the same kind of fact: volcor.md draws the line at dragon's blood, not at office.
Was ``title`` (2026-08-20) — the named offices are the titles, "Fang, Dracai of
Blades", "Taipanis, Dracai of Judgement", and those hang off this row in stage 7.

Not a species row, although a caste reads like one: every named Dracai is a
**hero**, and ``heroes_canonical`` has three columns and no species, so a species
row could hold nobody. See ``catalogue/species.py``."""
EZU = GroupEntry("Ezu", kind="faction")
SAYASHI = GroupEntry("Sayashi", kind="special force")
VOLCAI = GroupEntry(
    "Volcai",
    kind="people",
    lore_story_key="world-of-rathe/volcor.md",
    lore_fragment="the-volcai",
)
"""``Volcai``, not ``The Volcai``: volcor.md heads the section with the article but
its prose writes "the Volcai" lowercase, so the article is not part of the name —
rule N3, the same call that named ``Registry``. Named on thirty-odd pages; only
the ones registered so far link it."""


# ---------------------------------------------------------------------------
# Metrix / The Pits
# ---------------------------------------------------------------------------

ARMS_DEALERS = GroupEntry("Arms Dealers", kind="gang")
COGWERX = GroupEntry("Cogwerx", kind="corporation")
IRON_ASSEMBLY = GroupEntry("Iron Assembly", kind="organisation")
"""Absorbs ``Iron Council``, shouted once in stroke-of-genius.md (Q2)."""
TRANSCENDENTS = GroupEntry("Transcendents", kind="order", location=loc.SKYLARK_PEAK)
"""Named once, on flavour/outsiders.md: "Grand masters of old reside atop Skylark
peak. Amongst these Transcendents..." The location is where they are; no page
describes them well enough for a summary."""
L_APOCALYPTA = GroupEntry(
    "L'Apocalypta",
    kind="cult",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="lapocalypta",
)
"""Straight apostrophe, not the curly one pits.md heads its section with.
``generate_hints_json.py`` emits both glyphs from the name, so the DB holds one
spelling and the prose still resolves either way — the same rule ``Aui's Scales``
follows."""
MENDACITY_MEDIA = GroupEntry("Mendacity Media", kind="corporation", aliases=("Mendacity",))
"""The prose says "Mendacity" far more often than the full name — metrix.md writes
it bare six times. Migrating the supplement entry to a group renamed the tooltip
key to the full name and took the short form's tooltip with it; the alias is what
gives it back."""
"""Absorbs ``Mendacity``, ``Voxx`` and the ``Voxx Press`` location row (Q5)."""
REGISTRY = GroupEntry(
    "Registry",
    kind="corporation",
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="registry",
)
"""No "The" in the name: metrix.md's heading is "Registry" and the prose writes
"the Registry" with a lowercase article, so the article is not part of the name.
Rule N3 — follow the lore name by name. Contrast "The Foundry", whose own heading
keeps its article."""
STEELSTREET_ENFORCERS = GroupEntry("Steelstreet Enforcers", kind="law enforcement")
THE_FOUNDRY = GroupEntry(
    "The Foundry",
    kind="organisation",
    location=loc.THE_FOUNDRY,
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="the-foundry",
)
"""A station and a place, so it keeps its locations row and links to it, the same
shape as Teklo Industries."""
TEKLO_INDUSTRIES = GroupEntry("Teklo Industries", kind="corporation", location=loc.TEKLO_INDUSTRIES)
"""The one group that is genuinely also a place: a company and a works, with 14
story links to the location, which is why the location row stays (G05)."""


# ---------------------------------------------------------------------------
# Misteria
# ---------------------------------------------------------------------------

AUIS_SCALES = GroupEntry("Aui's Scales", kind="organisation")
"""Keeps an override-only supplement stub: its ``exclude_pages`` suppression on
wanderings-in-the-mists and its two ``match`` spellings (straight and curly
apostrophe) are display facts no column models."""
CRIMSON_HAZE = GroupEntry("Crimson Haze", kind="rebels")
"""At odds with Aui's Scales for centuries. The opposition between them is a
relation with no column; it stays prose in the notes. Keeps a stub for
``exclude_pages``."""
CLAN_NASU_KA = GroupEntry("Clan Nasu-ka", kind="clan", location=loc.NASU_KA_TEAHOUSE)
"""The clan and the house it keeps, linked like Ikaru Clan to Ikaru.
part-1-the-tiger-in-the-mist.md calls the teahouse itself "Nasu-ka", so the two
names are close enough that keeping both rows joined is what stops them drifting."""
HIDESHI = GroupEntry("Hideshi", kind="house")
KAIGOMO = GroupEntry("Kaigomo", kind="order")
"""One mention in the whole book, on flavour/part-the-mistveil.md — enough to
know they field ronin across Misteria, not enough for a documentation page."""
REKVAS_BLOODBOARS = GroupEntry("Rek'vas Bloodboars", kind="warband")
"""Named once, on flavour/crucible-of-war.md — they hear word of war and want in,
which is what marks them as people rather than the beasts the name suggests."""
KOTORI = GroupEntry(
    "Kotori",
    kind="emissaries",
    npc_members=(
        npc.ANHE_KOTORI_WAVEBENDER,
        npc.DAN_LU_KOTORI_GALEWARDEN,
        npc.NING_KOTORI_MOONSEEKER,
    ),
    member_source="flavour/part-the-mistveil.md",
)
"""No page describes the Kotori as a body; the group is inferred from three NPC
names that all carry it — Wavebender, Galewarden, Moonseeker. Those three roles
are ranks and wait for R3. No notes, because nothing in the lore describes them."""
IKARU_CLAN = GroupEntry(
    "Ikaru Clan",
    kind="house",
    hero_members=("ira",),
    location=loc.IKARU,
    member_source="heroes-of-rathe/ira-about.md",
)
"""Absorbs ``House of Blossoms``. The location row stays as the place Ikaru (Q6)."""
MUGENSHI_CLAN = GroupEntry("Mugenshi Clan", kind="clan", hero_members=("benji",))


# ---------------------------------------------------------------------------
# Aria / Everfest
# ---------------------------------------------------------------------------

AETHERSCRIBES = GroupEntry(
    "Aetherscribes",
    kind="collective",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="aetherscribes",
)
GUARDIANS = GroupEntry("Guardians", kind="order")
OLLIN = GroupEntry(
    "Ollin",
    kind="order",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="ollin",
)
ROSETTA = GroupEntry(
    "Rosetta",
    kind="order",
    npc_members=(npc.OZRIM, npc.QUEEN_OF_CANDLEHOLD),
    member_source="short-stories/rosetta/verdance-thorn-of-the-rose.md",
)
"""``Rosetta`` is also the ``Species`` value on both of these NPCs, which is the
species column holding a membership — the mix-up stage 4 exists to unpick. The
group is the truth; the species values are wrong (2026-08-20)."""
SEERS = GroupEntry("Seers", kind="order")
THE_MAELA = GroupEntry(
    "The Maela",
    kind="troupe",
    npc_members=(
        (npc.MAELA_FAIRMIND, "flavour/compendium-of-rathe.md"),
        (npc.MAELA_ISULFV, "flavour/omens-of-the-third-age.md"),
        (npc.MAELA_ONE_EYE, "flavour/mastery-pack-guardian.md"),
        (npc.MAELA_SHARENA, "flavour/omens-of-the-third-age.md"),
        (npc.KAYSIN, "flavour/rosetta.md"),
    ),
    location=loc.THE_EVERFEST_CARNIVAL,
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="the-everfest-carnival",
)
"""Was a locations row (G01). The Carnival link is a ``location``, not a
``parent`` — the Everfest Carnival is a place, and no group row exists for it.

No ``member_source``. aria.md:93 describes the Maela and names nobody, and no
other page lists them as a roster, so there is no single page to cite — this is
the group the per-member ``(npc, story_key)`` pair was added for. ``lore_story_key``
carries the page that documents the group; each membership carries its own.

**The name is the attestation.** Four of the five are written ``Maela <name>`` in
the flavour credits. Kaysin is written "Kaysin, Maela Soothsayer"
(``flavour/rosetta.md:16``) — the same construction with the rank last, and the
exact string the retired ``Species`` column held for her. An earlier note here
said in bold that no page called her a Maela and recorded the membership as the
user's inference. That was wrong: rosetta.md attests it, the page is registered,
and ``story_npcs`` has linked her to it the whole time. Corrected 2026-08-20.

That note also carried a **second, independent trail, and it is true** — restored
2026-08-21 after the review found the correction had thrown it out along with the
false claim beside it. ``main-story/mastery-pack-guardian/trouble-in-larinkmorth.md``
gives "the seer" and "the elderly seer" (:63), a journey from Everfest (:23, :37)
and a reading of tea leaves (:63) — which is aria.md's whole description of the
Maela, "a group of seers … respected for their talent in second-sight", and
nothing more. It is not the membership's citation: ``rosetta.md`` names her rank
outright and that page is what ``group_npcs`` cites. It is the fallback if the
credit line is ever disputed, and it is recorded nowhere else.

Isulfv, One-eye and Sharena joined at the same time, on the same reading of the
prefix that gave ``KOTORI`` its roster (the user's call, 2026-08-20).
``Soothsayer`` is a rank and waits for stage 7."""
THE_VALDUR = GroupEntry(
    "The Valdur",
    kind="troupe",
    location=loc.THE_EVERFEST_CARNIVAL,
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="the-everfest-carnival",
)
"""Was a locations row (G02). See THE_MAELA on the Carnival link, and on the
fragment: both troupes are described in the same aria.md section and neither has
a heading of its own, so both point at ``the-everfest-carnival``."""
WARDENS = GroupEntry("Wardens", kind="order")
WAYFARERS = GroupEntry(
    "Wayfarers",
    kind="order",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="wayfarers-1",
)
"""``wayfarers-1``, not ``wayfarers``. aria.md carries the word twice: once at
line 117 under "skills, crafts and talents" (the craft — R9, not migrated) and
once at line 187 under Valahai (this group). The supplement's url pointed at the
craft section while its summary was written from the Valahai one."""


# ---------------------------------------------------------------------------
# Unplaced
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# High Seas
# ---------------------------------------------------------------------------

THE_DHANI_EMPIRE = GroupEntry(
    "The Dhani Empire",
    kind="empire",
    aliases=("Dhani Empire",),
    lore_story_key="world-of-rathe/high-seas.md",
    lore_fragment="the-dhani-empire",
)
"""The polity, not the people. "Dhani" also runs through the archive as a folk with
their own gods, language and dress — that sense is a species and belongs to stage 4;
this row is the empire they built (2026-08-20).

The alias restores the bare form. Stage 2 replaced a supplement entry matching
``Dhani Empire`` with this row, whose name carries the article, so the matcher
stopped finding "a long-dead Dhani Empire" — the same loss ``Mendacity`` took, and
one the clash warning cannot report, because a missing bare form is not a clash."""
KURAGHAN = GroupEntry(
    "Kuraghan",
    kind="cult",
    lore_story_key="world-of-rathe/high-seas.md",
    lore_fragment="the-kuraghan",
)
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
