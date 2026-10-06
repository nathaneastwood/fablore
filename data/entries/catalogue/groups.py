"""Canonical group definitions — houses, clans, guilds, orders and troupes.

``group_id`` hashes the name alone, so a second spelling mints a second row.
This file is the only place a group name is written; the story declarations
reference ``grp.NAME``.
"""

from __future__ import annotations

from db import GroupEntry

from . import characters as people
from . import locations as loc

# ---------------------------------------------------------------------------
# Deathmatch Super Slam guilds
# ---------------------------------------------------------------------------

SUPER_SLAM_GUILDS = GroupEntry("Super Slam Guilds", category="federation")

SPEAKEASYS_GUILDS = GroupEntry(
    "Speakeasy's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.SPEAKEASY,),
    member_source="main-story/super-slam/feudmasters.md",
)

BATBITERS_GUILDS = GroupEntry(
    "Batbiter's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.BATBITER,),
    member_source="main-story/super-slam/feudmasters.md",
)

MOLOCAS_GUILDS = GroupEntry(
    "Moloca's Guilds",
    category="stable",
    parent=SUPER_SLAM_GUILDS,
    members=(people.MOLOCA,),
    member_source="main-story/super-slam/feudmasters.md",
)

BALEFUL_HORDE = GroupEntry(
    "Baleful Horde",
    category="guild",
    parent=BATBITERS_GUILDS,
    members=(people.FUGGER_GRIMES,),
    member_source="flavour/super-slam.md",
)
BIG_BOPPERS = GroupEntry("Big Boppers", category="guild", parent=BATBITERS_GUILDS)
BOULDERS = GroupEntry("Boulders", category="guild", parent=SPEAKEASYS_GUILDS)
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
JUNGLE_SLAYERS = GroupEntry(
    "Jungle Slayers",
    category="guild",
    parent=BATBITERS_GUILDS,
    aliases=("Chanek Jungle Slayers",),
    members=(people.HELX,),
    member_source="flavour/super-slam.md",
)
MYTHMAKERS = GroupEntry("Mythmakers", category="guild", parent=SPEAKEASYS_GUILDS)
PROWLERS = GroupEntry("Prowlers", category="guild", parent=BATBITERS_GUILDS, members=("kayo",))
WILD_WONDERS = GroupEntry("Wild Wonders", category="guild", parent=SPEAKEASYS_GUILDS)


# ---------------------------------------------------------------------------
# Solana
# ---------------------------------------------------------------------------

CHILDREN_OF_THE_LIGHT = GroupEntry("Children of the Light", category="people")
GEMINI = GroupEntry("Gemini", category="order")
HAND_OF_SOL = GroupEntry(
    "Hand of Sol",
    category="order of knights",
    lore_story_key="world-of-rathe/solana.md",
    lore_fragment="the-hand-of-sol",
)
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


# ---------------------------------------------------------------------------
# Demonastery / Shadow
# ---------------------------------------------------------------------------

CHURCH_OF_PAIN = GroupEntry("Church of Pain", category="institution")
DISCIPLES_OF_PAIN = GroupEntry("Disciples of Pain", category="faction", parent=CHURCH_OF_PAIN)
GLOOMBLADES = GroupEntry("Gloomblades", category="faction", members=("viserai",))


# ---------------------------------------------------------------------------
# Volcor
# ---------------------------------------------------------------------------

ALSHONI = GroupEntry("Alshoni", category="faction")
CHILDREN_OF_CHAOS = GroupEntry("Children of Chaos", category="cult")
CHILDREN_OF_THE_DRAGON = GroupEntry("Children of the Dragon", category="order", members=("fang",))
DUST_RUNNERS = GroupEntry(
    "Dust Runners",
    category="gang",
    members=(people.KAYAT,),
    member_source="main-story/the-hunted/mark-of-a-traitor.md",
)
ROYAL_GUARD = GroupEntry(
    "Royal Guard",
    category="corps",
    members=("fang",),
    member_source="main-story/the-hunted/mark-of-a-traitor.md",
)
CINTARI = GroupEntry(
    "Cintari",
    category="clan",
    members=("kassai", people.ALIF, people.FAYYAD, people.SADA),
    member_source="main-story/heavy-hitters/thirst-for-revenge.md",
)
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
DRACAI = GroupEntry("Dracai", category="people")
SANDFOLK = GroupEntry("Sandfolk", category="people")
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
VOLCAI = GroupEntry(
    "Volcai",
    category="people",
    lore_story_key="world-of-rathe/volcor.md",
    lore_fragment="the-volcai",
)


# ---------------------------------------------------------------------------
# Metrix / The Pits
# ---------------------------------------------------------------------------

ARMS_DEALERS = GroupEntry("Arms Dealers", category="gang")
BLACKJACK_S_MINING_INCORPORATED = GroupEntry(
    "Blackjack's Mining Incorporated",
    category="corporation",
    aliases=("Blackjack's Mining",),
)
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
CIRCUIT_BREAKER = GroupEntry("Circuit Breaker", category="band")
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
IRON_ASSEMBLY = GroupEntry("Iron Assembly", category="organisation")
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
L_APOCALYPTA = GroupEntry(
    "L'Apocalypta",
    category="cult",
    members=(people.ANARCH_ZEIR,),
    member_source="flavour/compendium-of-rathe.md",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="lapocalypta",
)
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
RUNNING_TIGERS = GroupEntry(
    "Running Tigers",
    category="gang",
    members=(people.NJERI, people.HISATO, people.JEMJANG),
    member_source="main-story/outsiders/its-just-business.md",
)
REGISTRY = GroupEntry(
    "Registry",
    category="corporation",
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="registry",
)
SOUTHMAW_ASYLUM = GroupEntry(
    "Southmaw Asylum",
    category="institution",
    lore_story_key="world-of-rathe/pits.md",
    lore_fragment="southmaw-asylum",
)
STEELSTREET_ENFORCERS = GroupEntry("Steelstreet Enforcers", category="law enforcement")
THE_FOUNDRY = GroupEntry(
    "The Foundry",
    category="organisation",
    location=loc.THE_FOUNDRY,
    lore_story_key="world-of-rathe/metrix.md",
    lore_fragment="the-foundry",
)
TEKLO_INDUSTRIES = GroupEntry("Teklo Industries", category="corporation", location=loc.TEKLO_INDUSTRIES)


# ---------------------------------------------------------------------------
# Misteria
# ---------------------------------------------------------------------------

AUIS_SCALES = GroupEntry("Aui's Scales", category="organisation")
CRIMSON_HAZE = GroupEntry("Crimson Haze", category="rebels")
CLAN_NASU_KA = GroupEntry("Clan Nasu-ka", category="clan", location=loc.NASU_KA_TEAHOUSE)
HIDESHI = GroupEntry("Hideshi", category="house")
KAIGOMO = GroupEntry("Kaigomo", category="order")
REKVAS_BLOODBOARS = GroupEntry("Rek'vas Bloodboars", category="warband")
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
OKARI_CLAN = GroupEntry("Okari Clan", category="clan")
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
THE_VALDUR = GroupEntry(
    "The Valdur",
    category="troupe",
    location=loc.THE_EVERFEST_CARNIVAL,
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="the-everfest-carnival",
)
WARDENS = GroupEntry("Wardens", category="order")
WAYFARERS = GroupEntry(
    "Wayfarers",
    category="order",
    lore_story_key="world-of-rathe/aria.md",
    lore_fragment="wayfarers-1",
)


# ---------------------------------------------------------------------------
# Unplaced
# ---------------------------------------------------------------------------

SANDLARS = GroupEntry(
    "Sandlars",
    category="clan",
    members=(people.GRANNIE_SANDLAR,),
    member_source="equipment/comeback-kicks.md",
)

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
DEITIES = GroupEntry("Deities", category="pantheon")

DHANI_DEITIES = GroupEntry(
    "Dhani Deities",
    category="pantheon",
    parent=DEITIES,
    members=(people.ABSOLON, people.NOCETES),
    member_source="world-of-rathe/high-seas.md",
)

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
VIPRESSA = GroupEntry("Vipressa", category="faction")
