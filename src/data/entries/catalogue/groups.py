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
``(character, story_key)`` pair when that one membership is attested somewhere else.
Eleven of the twelve rosters here were read off a single page and use the plain
form; ``THE_MAELA`` is the exception that needed the pair, its five seers named
across four flavour pages with no page listing them together.

Import direction is one-way — this module imports ``characters.py`` and names hero
slugs as strings, and nothing imports this module back — so no cycle is possible.
"""

from __future__ import annotations

from db import GroupEntry

from . import characters as people
from . import locations as loc


# ---------------------------------------------------------------------------
# Deathmatch Super Slam guilds
# ---------------------------------------------------------------------------
# This section used to carry the note: "Guild-to-fightmaster affiliation
# (Speakeasy's, Batbiter's, Moloca's) is a group-to-person relation, not a parent
# group, so it is not modelled here." **That was wrong on both halves** and is
# replaced 2026-08-21 (the user's call).
#
# It is not a group-to-person relation. main-story/super-slam/feudmasters.md is a
# panel at which each patron is handed the floor and introduces their own guilds
# in turn, so the page states a guild-to-stable relation and the stable-to-patron
# relation separately. And it *is* a parent group: three stables inside one
# federation, twelve guilds inside the three stables, which `parent_group_id`
# already models. Verified before writing that the chain holds at three levels —
# parents are written first and only a cycle raises, there is no depth cap.
#
# The relation was never unmodellable. It was unmodelled because the reading came
# from src/data/md/character-groups.md, which hedges ("mentioned in rivalry, but
# tied to her side", "unnamed, but implied") and is **wrong twice** — see
# HEAVY_METALS and MOLOCAS_GUILDS below. feudmasters.md, already declared at
# entries/main_story.py:503, says it plainly.

SUPER_SLAM_GUILDS = GroupEntry("Super Slam Guilds", category="federation")
"""The competition every stable below fights in, and the row that makes the three
stables siblings rather than three unrelated groups. It holds no members of its
own: a fighter belongs to a guild, and the federation is what the guilds enter."""

SPEAKEASYS_GUILDS = GroupEntry(
    "Speakeasy's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.SPEAKEASY,),
    member_source="main-story/super-slam/feudmasters.md",
)
"""Rusty names this stable outright — the Wild Wonders are "among **Speakeasy's**
guilds" — which is why the group is named for her rather than given an in-world
name no page supplies.

The patron sits in ``members``, and that **strains the relation**: Speakeasy
fronts the stable, she does not fight in it, and ``group_characters`` means membership
everywhere else in this file. It is used here because it is the only person-to-
group relation that exists, and because the alternative — letting the group's
*name* carry the patron — makes a rename silently drop the link. The user's call,
2026-08-21. Recorded in stage 11."""

BATBITERS_GUILDS = GroupEntry(
    "Batbiter's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.BATBITER,),
    member_source="main-story/super-slam/feudmasters.md",
)
"""See ``SPEAKEASYS_GUILDS`` on the patron membership. Speakeasy names this stable
for him too — "a pack of **your** Chanek Jungle Slayers"."""

MOLOCAS_GUILDS = GroupEntry(
    "Moloca's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.MOLOCA,),
    member_source="main-story/super-slam/feudmasters.md",
)
"""**Deliberately empty, and that is the finding.** character-groups.md gives
Moloca a guild — "Savage Land beasts (unnamed, but implied as a competing force
in the arena)" — and feudmasters.md gives her none. Rusty asks her outright why
she is even on the panel and she answers "For my beasts. To find out what sort of
meat they can look forward to consuming over the coming weeks." She fronts
nothing.

The row exists because she is still a patron and the user chose to keep her as
one (2026-08-21). An empty stable is the only shape that can say so: a junction
keyed ``(group, character)`` would have had no row to put her on, and she would
have disappeared from the data entirely. That is what ruled the junction out."""

BALEFUL_HORDE = GroupEntry(
    "Baleful Horde",
    category="guild",
    parent=BATBITERS_GUILDS,
    members=(people.FUGGER_GRIMES,),
    member_source="flavour/super-slam.md",
)
BIG_BOPPERS = GroupEntry("Big Boppers", category="guild", parent=BATBITERS_GUILDS)
BOULDERS = GroupEntry("Boulders", category="guild", parent=SPEAKEASYS_GUILDS)
"""Absorbs ``Boulder Clan``; one guild, not a guild plus a dwarven clan (Q3)."""
CHAMPIONS_OF_CHIVALRY = GroupEntry(
    "Champions of Chivalry",
    category="guild",
    parent=SPEAKEASYS_GUILDS,
    members=(people.EMEVIERE,),
    member_source="flavour/super-slam.md",
)
FURY_FISTS = GroupEntry("Fury Fists", category="guild", parent=SPEAKEASYS_GUILDS)
GLORYTOWN_GLADIATORS = GroupEntry(
    "Glorytown Gladiators",
    category="guild",
    parent=SPEAKEASYS_GUILDS,
    members=(people.SALVADOR_STALLION,),
    member_source="flavour/super-slam.md",
)
GORELORDS = GroupEntry("Gorelords", category="guild", parent=BATBITERS_GUILDS)
HEAVY_METALS = GroupEntry("Heavy Metals", category="guild", parent=BATBITERS_GUILDS)
"""**character-groups.md puts this guild on the wrong side**, under Speakeasy with
the hedge "(mentioned in rivalry, but tied to her side)". It is Batbiter's (the
user's call, 2026-08-21). Speakeasy is arguing that *her* guilds fight with honor
and cites this one against him — "Isn't it true, **Batbiter**, the last time the
Heavy Metals fought, they exploded part of the stadium, then ripped their opponent
apart with maces" — and he answers by defending them: "An accident caused the
stand to collapse, and the dwarves were cunning enough to take advantage."
Nobody defends a rival's guild. Being *named by* Speakeasy is what the hand-
written file mistook for being *hers*."""
JUNGLE_SLAYERS = GroupEntry(
    "Jungle Slayers",
    category="guild",
    parent=BATBITERS_GUILDS,
    aliases=("Chanek Jungle Slayers",),
    members=(people.HELX,),
    member_source="flavour/super-slam.md",
)
"""Absorbs ``Chanek Jungle Slayers``. Chanek is a kind, not part of the name
(Q4) — so the short form stays canonical, and the long form is an **alias** as of
2026-08-21 (the user's call) rather than being dropped. Both feudmasters.md and
character-groups.md write the long form, so without the alias the tooltip matched
neither of the two places the guild is actually named. The drift was already
logged in ``.claude/rules/data-pipeline.md``."""
MYTHMAKERS = GroupEntry("Mythmakers", category="guild", parent=SPEAKEASYS_GUILDS)
PROWLERS = GroupEntry("Prowlers", category="guild", parent=BATBITERS_GUILDS, members=("kayo",))
WILD_WONDERS = GroupEntry("Wild Wonders", category="guild", parent=SPEAKEASYS_GUILDS)


# ---------------------------------------------------------------------------
# Solana
# ---------------------------------------------------------------------------

CHILDREN_OF_THE_LIGHT = GroupEntry("Children of the Light", category="people")
"""Every citizen inside the walls (solana.md:21). Deliberately rosterless: the
membership is unbounded, so this row exists for mentions only (Q11)."""
GEMINI = GroupEntry("Gemini", category="order")
HAND_OF_SOL = GroupEntry(
    "Hand of Sol",
    category="order of knights",
    lore_story_key="world-of-rathe/solana.md",
    lore_fragment="the-hand-of-sol",
)
"""Was a locations row with 9 story links. An order of knights is not a place, so
the row is dropped; ``lore_story_key`` is what keeps its link to solana.md alive,
which is the only reason it was ever a location."""
HOUSE_ASHWOOD = GroupEntry("House Ashwood", category="house", members=("pleiades",))
HOUSE_GOLDMANE = GroupEntry(
    "House Goldmane",
    category="house",
    members=("lyath", "victor-goldmane", people.BLOODWORTH_GOLDMANE),
    member_source="heroes-of-rathe/lyath-about.md",
)

SISTERS_OF_OCTOTHESIA = GroupEntry("Sisters of Octothesia", category="order")
THE_LIGHT_OF_SOL = GroupEntry(
    "The Light of Sol",
    category="order of scholars",
    lore_story_key="world-of-rathe/solana.md",
    lore_fragment="the-light-of-sol",
)
"""Was a locations row. The Hand of Sol's matched pair — knights and scholars —
and treated the same way."""


# ---------------------------------------------------------------------------
# Demonastery / Shadow
# ---------------------------------------------------------------------------

CHURCH_OF_PAIN = GroupEntry("Church of Pain", category="institution")
"""The institution; the Disciples are its followers. Two rows, not one: the
supplement described both and they are not the same thing (2026-08-20)."""
DISCIPLES_OF_PAIN = GroupEntry("Disciples of Pain", category="faction", parent=CHURCH_OF_PAIN)
GLOOMBLADES = GroupEntry("Gloomblades", category="faction", members=("viserai",))


# ---------------------------------------------------------------------------
# Volcor
# ---------------------------------------------------------------------------

ALSHONI = GroupEntry("Alshoni", category="faction")
CHILDREN_OF_CHAOS = GroupEntry("Children of Chaos", category="cult")
"""main-story/the-hunted/children-of-chaos.md:171 — "the Children of the Dragon facing
the Children of Chaos". The page gives no category; "cult" is by analogy with KURAGHAN."""
CHILDREN_OF_THE_DRAGON = GroupEntry("Children of the Dragon", category="order", members=("fang",))
DUST_RUNNERS = GroupEntry(
    "Dust Runners",
    category="gang",
    members=(people.KAYAT,),
    member_source="main-story/the-hunted/mark-of-a-traitor.md",
)
"""Smugglers run out of a Deshvahan glassworks; "gang" is the catalogue's word,
the page says "smugglers"."""
ROYAL_GUARD = GroupEntry(
    "Royal Guard",
    category="corps",
    members=("fang",),
    member_source="main-story/the-hunted/mark-of-a-traitor.md",
)
"""mark-of-a-traitor.md:59, :153 — its captains kneel before the generals of the
Children of the Dragon: confirmed as a corps nested within that order, distinct
from it rather than an alias."""
CINTARI = GroupEntry(
    "Cintari",
    category="clan",
    members=("kassai", people.ALIF, people.FAYYAD, people.SADA),
    member_source="main-story/heavy-hitters/thirst-for-revenge.md",
)
"""A clan, not a people: kassai-about.md:11 has them *induct* Kassai into their
ranks, a hero trait reads "Leader of the Cintari", and fires-of-rebellion.md:79
has rebels wearing "Cintari disguises". None of that is true of a kind, which
is what separates this call from ``Chanek`` (2026-08-20)."""
LORD_WIZARDS_OF_THE_COURT = GroupEntry(
    "Lord Wizards of the Court",
    category="council",
    members=(
        "kano",
        (people.LORD_WIZARD_AKIHIKO, "main-story/arcane-rising/playing-with-fire.md"),
        (people.LORD_WIZARD_CHIYO, "main-story/arcane-rising/from-the-ashes.md"),
    ),
    member_source="heroes-of-rathe/kano-about.md",
)
"""The body at Court, **not** the rank. The two were split deliberately and only
this half is a group (the user's call, 2026-08-21).

The name is the one phrase that names the body: ``kano-about.md:7``, "the other
Lord Wizards **of the Court**" — which is also what puts Kano on the roster, since
"the other" makes him one of them. He is the only hero here; the other two are
characters, and each cites the page that names them in office rather than the page that
names the body, so the roster carries pairs the way ``THE_MAELA`` does.

**What forced the split.** ``ember-in-the-ash.md:3`` has a territory petition
"**our** Lord Wizard for aid", so the office is held per-territory by many people
at once. ``from-the-ashes.md:137`` writes "several of the **lord wizards**" and
"the **lord wizards** have continued to monitor the court" — lowercase, twice,
which is the N3 signal that named ``Volcai`` rather than ``The Volcai``. And
``cindra-about.md:11`` lists "Dracai Lord Wizard" beside "Volcai farmer",
"dust-born merchant" and "war-mongering general", which is an occupation among
occupations. A rank many hold independently is R9 and waits for stage 9; a named
body at Court is this row.

No ``lore_story_key``. ``volcor.md:31`` heads a section "The Royal Court", but
``IMPERIAL_PALACE`` already claims ``the-royal-court`` as its fragment and stage 11
records that the institution/building split is unresolved — a second row pointing
at the same anchor would deepen it rather than use it.

``category`` is the one guess in this row: no page gives the body a collective
noun, and "council" is chosen for "monitor the court" (``from-the-ashes.md:137``)."""
DRACAI = GroupEntry("Dracai", category="people")
"""The other half of the Volcoran split, and typed like ``Volcai`` because it is
the same kind of fact: volcor.md draws the line at dragon's blood, not at office.
Was ``title`` (2026-08-20) — the named offices are the titles, "Fang, Dracai of
Blades", "Taipanis, Dracai of Judgement", and those hang off this row in stage 7.

Not a kind row, although a caste reads like one: every named Dracai is a
**hero**, and ``heroes_canonical`` has three columns and no kind, so a kind
row could hold nobody. See ``catalogue/kind.py``."""
SANDFOLK = GroupEntry("Sandfolk", category="people")
"""A people, not a kind — the same call Volcai and Dracai took in stage 3, so the
three sit in one table rather than split across two (the user's call, 2026-08-21).

Dromai's mother's people: "Sani of the Sandfolk"
(``main-story/uprising/dragons-of-empire.md``), whose illusionists hold the great
sandstone wall against her dragons, and whose "fury continues to fester, as Xathari
hoped it would" (``main-story/dynasty/ember-in-the-ash.md:59``). Dromai is called a
"half-blood" for being of them and of the Dracai both."""
EZU = GroupEntry("Ezu", category="faction")
SAYASHI = GroupEntry("Sayashi", category="special force")
THE_TWELVE_DRAGONS = GroupEntry(
    "The Twelve Dragons",
    category="pantheon",
    members=(
        people.AZVOLAI,
        people.CROMAI,
        people.DOMINIA,
        people.DRACONA_OPTIMAI,
        people.KYLORIA,
        people.MIRAGAI,
        people.NEKRIA,
        people.OUVIA,
        people.THEMAI,
        people.TOMELTAI,
        people.VYNSERAKAI,
        people.YENDURAI,
    ),
    member_source="flavour/uprising.md",
    lore_story_key="main-story/uprising/dragons-of-empire.md",
)
"""The collective the twelve dragon rows belong to (the user's call, 2026-08-21).

**Named once in the whole repository**, and capitalised there:
``main-story/uprising/dragons-of-empire.md:67`` has Dromai "pore over the tomes of
The Twelve Dragons". That is the only line that treats the twelve as one named
thing rather than as a count, so ``lore_story_key`` points at it while the roster
cites the page that actually names the members.

``member_source`` is ``flavour/uprising.md`` because that is where all twelve are
attested — one ``Invoke <name>`` card title each, UPR006-UPR017, and nothing else
on the page names a dragon at all. dragons-of-empire.md names only four of them
(Azvolai, Nekria, Tomeltai, Vynserakai), so declaring the roster from the page that
names the group would have lost two thirds of it. The count matching the name
exactly — twelve titles, twelve rows, no thirteenth ``kind.DRAGON`` character anywhere — is
what carries the inference that these twelve are those twelve.

``pantheon``, the same category ``Deities`` and ``Dhani Deities`` took: the tomes are
studied, and dromai-about.md calls Dracona Optimai, Tomeltai and Dominia "servants
of the Draconic Aesir". Whether that is worship or taxonomy is stage 11's problem,
not this row's."""
VOLCAI = GroupEntry(
    "Volcai",
    category="people",
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

ARMS_DEALERS = GroupEntry("Arms Dealers", category="gang")
BLACKJACK_S_MINING_INCORPORATED = GroupEntry(
    "Blackjack's Mining Incorporated",
    category="corporation",
    aliases=("Blackjack's Mining",),
)
"""main-story/outsiders/its-just-business.md — the full name once, the short form
twice. Confirmed as the same Blackjack as loc.BLACKJACK_S_TAVERN: this is the
parent corporation, BLACKJACK_S_MERCENARY_COMPANY its militant offshoot, and the
Tavern is the Mercenary Company's HQ — world-of-rathe/pits.md:157-163 and
main-story/outsiders/its-just-business.md."""
BLOCKHEADS = GroupEntry(
    "Blockheads",
    category="gang",
    members=(people.SLAB,),
    member_source="main-story/outsiders/the-spiders-trap.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="blockheads",
)
BLACKJACK_S_MERCENARY_COMPANY = GroupEntry(
    "Blackjack's Mercenary Company",
    category="mercenary company",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="blackjacks-mercenary-company",
)
"""The militant offshoot of Blackjack's Mining Incorporated — world-of-rathe/pits.md."""
CIRCUIT_BREAKER = GroupEntry("Circuit Breaker", category="band")
"""A sour-synth band from the Sprawl — main-story/bright-lights/synthetic-futures.md.
No member is named, so no roster."""
COGWERX = GroupEntry("Cogwerx", category="corporation")
FREAKSHOW = GroupEntry(
    "Freakshow",
    category="gang",
    members=(people.CAGER,),
    member_source="main-story/outsiders/the-spiders-trap.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="freakshow",
)
GIMLET_MINING = GroupEntry("Gimlet Mining", category="corporation")
"""Named once on main-story/outsiders/its-just-business.md — the rival that
contracts the hit on Overseer Crichton."""
IRON_ASSEMBLY = GroupEntry("Iron Assembly", category="organisation")
"""Absorbs ``Iron Council``, shouted once in stroke-of-genius.md (Q2)."""
JAWBREAKERS = GroupEntry(
    "Jawbreakers",
    category="gang",
    members=(people.MADAME_FUSE,),
    member_source="main-story/outsiders/the-spiders-trap.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="jawbreakers",
)
TORCHED = GroupEntry(
    "Torched",
    category="gang",
    members=(people.MELTEN_WICK,),
    member_source="main-story/outsiders/the-spiders-trap.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="torched",
)
THE_MOB = GroupEntry(
    "The Mob",
    category="gang",
    members=(people.REX_BIGGUN,),
    member_source="world-of-rathe/metrix.md",
)
TRANSCENDENTS = GroupEntry("Transcendents", category="order", location=loc.SKYLARK_PEAK)
"""Named once, on flavour/outsiders.md: "Grand masters of old reside atop Skylark
peak. Amongst these Transcendents..." The location is where they are; no page
describes them well enough for a summary."""
L_APOCALYPTA = GroupEntry(
    "L'Apocalypta",
    category="cult",
    members=(people.ANARCH_ZEIR,),
    member_source="flavour/compendium-of-rathe.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="lapocalypta",
)
"""Straight apostrophe, not the curly one pits.md heads its section with.
``generate_hints_json.py`` emits both glyphs from the name, so the DB holds one
spelling and the prose still resolves either way — the same rule ``Aui's Scales``
follows."""
MENDACITY_MEDIA = GroupEntry("Mendacity Media", category="corporation", aliases=("Mendacity",))
NUMBSKULLS = GroupEntry(
    "Numbskulls",
    category="gang",
    members=(people.MARROW,),
    member_source="main-story/outsiders/the-spiders-trap.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="numbskulls",
)
PIRANHAS = GroupEntry(
    "Piranhas",
    category="gang",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="piranhas",
)
"""A Pits gang with a heading of its own on pits.md (:117). Named on
main-story/outsiders/catch-of-the-day.md, which names no individual member."""
"""The prose says "Mendacity" far more often than the full name — metrix.md writes
it bare six times. Migrating the supplement entry to a group renamed the tooltip
key to the full name and took the short form's tooltip with it; the alias is what
gives it back."""
"""Absorbs ``Mendacity``, ``Voxx`` and the ``Voxx Press`` location row (Q5)."""
RUNNING_TIGERS = GroupEntry(
    "Running Tigers",
    category="gang",
    members=(people.NJERI, people.HISATO, people.JEMJANG),
    member_source="main-story/outsiders/its-just-business.md",
)
"""Uzuri's parents' smuggling ring: "Njeri handled Metrix, Hisato looked after
Misteria, and Jemjang kept the thoroughfares open between them"."""
REGISTRY = GroupEntry(
    "Registry",
    category="corporation",
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="registry",
)
"""No "The" in the name: metrix.md's heading is "Registry" and the prose writes
"the Registry" with a lowercase article, so the article is not part of the name.
Rule N3 — follow the lore name by name. Contrast "The Foundry", whose own heading
keeps its article."""
SOUTHMAW_ASYLUM = GroupEntry(
    "Southmaw Asylum",
    category="institution",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="southmaw-asylum",
)
"""An institution inside the Southmaw district (loc.SOUTHMAW), not the district."""
STEELSTREET_ENFORCERS = GroupEntry("Steelstreet Enforcers", category="law enforcement")
THE_FOUNDRY = GroupEntry(
    "The Foundry",
    category="organisation",
    location=loc.THE_FOUNDRY,
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="the-foundry",
)
"""A station and a place, so it keeps its locations row and links to it, the same
shape as Teklo Industries."""
TEKLO_INDUSTRIES = GroupEntry("Teklo Industries", category="corporation", location=loc.TEKLO_INDUSTRIES)
"""The one group that is genuinely also a place: a company and a works, with 14
story links to the location, which is why the location row stays (G05)."""


# ---------------------------------------------------------------------------
# Misteria
# ---------------------------------------------------------------------------

AUIS_SCALES = GroupEntry("Aui's Scales", category="organisation")
"""Keeps an override-only supplement stub: its ``exclude_pages`` suppression on
wanderings-in-the-mists and its two ``match`` spellings (straight and curly
apostrophe) are display facts no column models."""
CRIMSON_HAZE = GroupEntry("Crimson Haze", category="rebels")
"""At odds with Aui's Scales for centuries. The opposition between them is a
relation with no column; it stays prose in the notes. Keeps a stub for
``exclude_pages``."""
CLAN_NASU_KA = GroupEntry("Clan Nasu-ka", category="clan", location=loc.NASU_KA_TEAHOUSE)
"""The clan and the house it keeps, linked like Ikaru Clan to Ikaru.
part-1-the-tiger-in-the-mist.md calls the teahouse itself "Nasu-ka", so the two
names are close enough that keeping both rows joined is what stops them drifting."""
HIDESHI = GroupEntry("Hideshi", category="house")
KAIGOMO = GroupEntry("Kaigomo", category="order")
"""One mention in the whole book, on flavour/part-the-mistveil.md — enough to
know they field ronin across Misteria, not enough for a documentation page."""
REKVAS_BLOODBOARS = GroupEntry("Rek'vas Bloodboars", category="warband")
"""Named once, on flavour/crucible-of-war.md — they hear word of war and want in,
which is what marks them as people rather than the beasts the name suggests."""
KOTORI = GroupEntry(
    "Kotori",
    category="emissaries",
    members=(
        people.ANHE_KOTORI_WAVEBENDER,
        people.DAN_LU_KOTORI_GALEWARDEN,
        people.NING_KOTORI_MOONSEEKER,
    ),
    member_source="flavour/part-the-mistveil.md",
)
"""No page describes the Kotori as a body; the group is inferred from three character
names that all carry it — Wavebender, Galewarden, Moonseeker. Those three roles
are ranks and wait for R3. No notes, because nothing in the lore describes them."""
HOUSE_ISHIGAKI = GroupEntry(
    "House Ishigaki",
    category="house",
    lore_story_key="world-of-rathe/misteria.md",
    lore_fragment="ishigaki",
)
HOUSE_MIHARU = GroupEntry(
    "House Miharu",
    category="house",
    lore_story_key="world-of-rathe/misteria.md",
    lore_fragment="miharu",
)
HOUSE_SANJING = GroupEntry(
    "House Sanjing",
    category="house",
    lore_story_key="world-of-rathe/misteria.md",
    lore_fragment="sanjing",
    members=(people.JIRO_HENSHU,),
    member_source="world-of-rathe/misteria.md",
)
HOUSE_YIJUN = GroupEntry(
    "House Yijun",
    category="house",
    lore_story_key="world-of-rathe/misteria.md",
    lore_fragment="yijun",
)
IKARU_CLAN = GroupEntry(
    "Ikaru Clan",
    category="house",
    members=("ira",),
    location=loc.IKARU,
    member_source="heroes-of-rathe/ira-about.md",
)
"""Absorbs ``House of Blossoms``. The location row stays as the place Ikaru (Q6)."""
OKARI_CLAN = GroupEntry("Okari Clan", category="clan")
"""equipment/celestial-kimono.md — "the inscrutable Okari Clan of Misteria", gift-givers
to the Emperor. Named nowhere else."""
KEEPERS_OF_THE_SEVEN_ARTS = GroupEntry(
    "The Keepers of the Seven Arts",
    category="council",
    lore_story_key="world-of-rathe/misteria.md",
    lore_fragment="the-keepers-of-the-seven-arts",
)
MUGENSHI_CLAN = GroupEntry("Mugenshi Clan", category="clan", members=("benji",))


# ---------------------------------------------------------------------------
# Aria / Everfest
# ---------------------------------------------------------------------------

AETHERSCRIBES = GroupEntry(
    "Aetherscribes",
    category="collective",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="aetherscribes",
)
GUARDIANS = GroupEntry("Guardians", category="order")
OLLIN = GroupEntry(
    "Ollin",
    category="order",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="ollin",
)
ROSETTA = GroupEntry(
    "Rosetta",
    category="order",
    members=(people.OZRIM, people.QUEEN_OF_CANDLEHOLD),
    member_source="short-stories/rosetta/verdance-thorn-of-the-rose.md",
)
"""``Rosetta`` is also the ``Kind`` value on both of these characters, which is the
kind column holding a membership — the mix-up stage 4 exists to unpick. The
group is the truth; the kind values are wrong (2026-08-20)."""
SEERS = GroupEntry("Seers", category="order")
THE_MAELA = GroupEntry(
    "The Maela",
    category="troupe",
    members=(
        (people.MAELA_FAIRMIND, "flavour/compendium-of-rathe.md"),
        (people.MAELA_ISULFV, "flavour/omens-of-the-third-age.md"),
        (people.MAELA_ONE_EYE, "flavour/mastery-pack-guardian.md"),
        (people.MAELA_SHARENA, "flavour/omens-of-the-third-age.md"),
        (people.KAYSIN, "flavour/rosetta.md"),
    ),
    location=loc.THE_EVERFEST_CARNIVAL,
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="the-everfest-carnival",
)
"""Was a locations row (G01). The Carnival link is a ``location``, not a
``parent`` — the Everfest Carnival is a place, and no group row exists for it.

No ``member_source``. aria.md:93 describes the Maela and names nobody, and no
other page lists them as a roster, so there is no single page to cite — this is
the group the per-member ``(character, story_key)`` pair was added for. ``lore_story_key``
carries the page that documents the group; each membership carries its own.

**The name is the attestation.** Four of the five are written ``Maela <name>`` in
the flavour credits. Kaysin is written "Kaysin, Maela Soothsayer"
(``flavour/rosetta.md:16``) — the same construction with the rank last, and the
exact string the retired ``Kind`` column held for her. An earlier note here
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
outright and that page is what ``group_characters`` cites. It is the fallback if the
credit line is ever disputed, and it is recorded nowhere else.

Isulfv, One-eye and Sharena joined at the same time, on the same reading of the
prefix that gave ``KOTORI`` its roster (the user's call, 2026-08-20).
``Soothsayer`` is a rank and waits for stage 7."""
THE_VALDUR = GroupEntry(
    "The Valdur",
    category="troupe",
    location=loc.THE_EVERFEST_CARNIVAL,
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="the-everfest-carnival",
)
"""Was a locations row (G02). See THE_MAELA on the Carnival link, and on the
fragment: both troupes are described in the same aria.md section and neither has
a heading of its own, so both point at ``the-everfest-carnival``."""
WARDENS = GroupEntry("Wardens", category="order")
WAYFARERS = GroupEntry(
    "Wayfarers",
    category="order",
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

SANDLARS = GroupEntry(
    "Sandlars",
    category="clan",
    members=(people.GRANNIE_SANDLAR,),
    member_source="equipment/comeback-kicks.md",
)
"""Craftsfolk of the Moat — equipment/comeback-kicks.md. Possibly a clan of the
Sandfolk; unconfirmed."""

# ---------------------------------------------------------------------------
# High Seas
# ---------------------------------------------------------------------------

THE_DHANI_EMPIRE = GroupEntry(
    "The Dhani Empire",
    category="empire",
    aliases=("Dhani Empire",),
    lore_story_key="world-of-rathe/high-seas.md",
    lore_fragment="the-dhani-empire",
)
"""The polity, not the people. "Dhani" also runs through the archive as a folk with
their own gods, language and dress — that sense is a kind and belongs to stage 4;
this row is the empire they built (2026-08-20).

The alias restores the bare form. Stage 2 replaced a supplement entry matching
``Dhani Empire`` with this row, whose name carries the article, so the matcher
stopped finding "a long-dead Dhani Empire" — the same loss ``Mendacity`` took, and
one the clash warning cannot report, because a missing bare form is not a clash."""
DEITIES = GroupEntry("Deities", category="pantheon")
"""**Gods are a group, not a kind** (the user's call, 2026-08-21). A deity is a
role a culture assigns, not a kind of being, so Absolon and Nocetes do not join
``kind.AESIR``/``kind.ANCIENT``/``kind.EMBRA``/``kind.HERALD``/``kind.DRAGON`` in the kind
table the way the other cosmological tiers did in stage 4.

This is also what gives the ``Gods`` section of ``character-groups.md`` its
``Culture`` column without a new column anywhere: the culture is the **parent
group**, so ``Dhani Deities`` inside ``Deities`` says "Dhani" and "god" in one
chain. The same shape as ``SUPER_SLAM_GUILDS``, chosen for the same reason.

Holds no members itself. Every deity belongs to a culture's pantheon, and this row
is what makes those pantheons siblings."""

DHANI_DEITIES = GroupEntry(
    "Dhani Deities",
    category="pantheon",
    parent=DEITIES,
    members=(people.ABSOLON, people.NOCETES),
    member_source="world-of-rathe/high-seas.md",
)
"""Both gods are named on one page — ``world-of-rathe/high-seas.md``, Absolon at
:125 and Nocetes at :143 — so the roster takes the plain ``member_source`` form
rather than the per-member pair ``THE_MAELA`` needed.

Distinct from ``THE_DHANI_EMPIRE``, which is the polity. That row's docstring
already notes that "Dhani" also runs through the archive as a folk with their own
**gods**, language and dress; this is that sense's pantheon."""

KURAGHAN = GroupEntry(
    "Kuraghan",
    category="cult",
    lore_story_key="world-of-rathe/high-seas.md",
    lore_fragment="the-kuraghan",
)
THE_SPIDER = GroupEntry(
    "The Spider",
    category="organisation",
    members=("uzuri", "arakni-solitary-confinement"),
    member_source="heroes-of-rathe/uzuri-about.md",
)
VANGELD = GroupEntry(
    "VanGeld",
    category="clan",
    members=(people.TARA_VANGELD,),
    member_source="heroes-of-rathe/lyath-about.md",
)
"""No "clan" in the name: lyath-about.md writes it as a common noun, and
``category`` holds it. Sits beside ``Mugenshi Clan``, which keeps its category
word because the lore always writes it that way — rule N3, follow the lore
name by name (Q13)."""
VIPRESSA = GroupEntry("Vipressa", category="faction")
