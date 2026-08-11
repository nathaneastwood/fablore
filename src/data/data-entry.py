# Registers each story and the entities it links to (heroes, npcs, locations,
# regions, monsters, fauna, flora, food/drink, weapons, equipment). This file
# only declares *relationships* — it does not set lore text.
#
# Lore text (location notes; monster/fauna/flora descriptions) belongs in
# descriptions.py, not here. See descriptions.py for why.

import sys

sys.path.insert(0, "src/data")
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
)

db = Database("src/data/fablore.db")

# -------------------------------------------------------------------------------------------------------------------- #
# Heroes
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/heroes-of-rathe/aurora-about.md",
    story_type="heroes-of-rathe",
    title="Aurora",
    heroes=["aurora"],
    locations=[
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Volthaven", region="Aria", lore_fragment="enion"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
    ],
    weapons=["star-fall", "scorpio-comet-tail"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/oscilio-about.md",
    story_type="heroes-of-rathe",
    title="Oscilio",
    heroes=["oscilio"],
    locations=[
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
    ],
    regions=[RegionEntry("Aria")],
    weapons=["volzar-the-lightning-rod"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zyggy-about.md",
    story_type="heroes-of-rathe",
    title="Zyggy Starlight",
    heroes=["zyggy", "oscilio"],
    regions=[RegionEntry("Nebulus Rift")],
    locations=[
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
    ],
    weapons=["aphrodias"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/blaze-about.md",
    story_type="heroes-of-rathe",
    title="Blaze",
    heroes=["blaze"],
    regions=[RegionEntry("Volcor")],
    locations=[
        LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court"),
    ],
    fauna=[FaunaEntry("Flare Deer")],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dorinthea-about.md",
    story_type="heroes-of-rathe",
    title="Dorinthea",
    heroes=["dorinthea", "hala"],
    locations=[
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("The Golden Fields", region="Solana"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
    ],
    weapons=["dawnblade", "dawnblade-resplendent"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/baalghor-about.md",
    story_type="heroes-of-rathe",
    title="Baalghor",
    source_link="https://fabtcg.com/hero/baalghor/",
    heroes=["baalghor"],
    locations=[
        LocationEntry("i'Arathael"),
        LocationEntry("Shadowrealm"),
        LocationEntry("The Abyss"),
    ],
    regions=[RegionEntry("Demonastery")],
    dry_run=True,
)

# -------------------------------------------------------------------------------------------------------------------- #
# Main Story
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/main-story/the-land-of-rathe.md",
    story_type="main-story",
    title="The Land of Rathe",
    authors="Nicola Price",
    source_link="https://fabtcg.com/articles/land-of-rathe/",
    publication_date="2019-08-29",
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/crucible-of-war/edge-of-autumn.md",
    story_type="main-story",
    title="Edge of Autumn",
    source_link="https://fabtcg.com/hero/ira-3/story/edge-of-autumn/",
    weapons=["edge-of-autumn"],
    locations=[LocationEntry("Ikaru", region="Misteria", lore_fragment="ikaru")],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/a-rising-star.md",
    story_type="main-story",
    title="A Rising Star",
    authors="Nicola Price",
    artists="MJ Fetesio, Sindy Wo",
    source_link="https://fabtcg.com/hero/bravo-4/story/bravo-showtopper-story/",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=E6JoDmEbTgU",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["bravo"],
    npcs=[
        NPCEntry(name="Magnus the Vigilant", species="Human"),
        NPCEntry(name="Gawain", species="Human"),
        NPCEntry(name="Morgan", species="Human"),
        NPCEntry(name="Marbles", species="Meep"),
        NPCEntry(name="Mikael", species="Human"),
    ],
    locations=[
        LocationEntry("The Flow", region="Aria", lore_fragment="the-flow"),
        LocationEntry(
            "The Everfest Carnival",
            region="Aria",
            lore_fragment="the-everfest-carnival",
        ),
        LocationEntry("Legendarium", region="Aria", lore_fragment="the-everfest-carnival"),
        LocationEntry("The Maela", region="Aria"),
        LocationEntry("The Valdur", region="Aria"),
        LocationEntry("Aldevyr", region="Aria"),
        LocationEntry("Fractal Scar", region="Aria"),
        # Named only here, by Mikael on his return to the Everfest — an Arian range.
        LocationEntry("Milesian Ranges", region="Aria"),
    ],
    regions=[RegionEntry("Aria")],
    monsters=[MonsterEntry("Dregs")],
    fauna=[
        FaunaEntry("Cesari"),
        FaunaEntry("Meep"),
        FaunaEntry("Kaie'o"),
        FaunaEntry("Fianna"),
        FaunaEntry("Vitr'eo"),
    ],
    food_drink=[FoodDrinkEntry(name="Alder Cider", kind="Drink")],
    weapons=["anothos"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/pride-of-the-ironsongs.md",
    story_type="main-story",
    title="Pride of the Ironsongs",
    authors="Nicola Price",
    artists="MJ Fetesio, Sindy Wo",
    source_link="https://fabtcg.com/hero/dorinthea/story/story/",
    publication_date="",
    thumbnail_image_link="",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=AuOKr_eoDLY",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["dorinthea", "hala"],
    npcs=[
        NPCEntry(
            name="Minerva Themis",
            species="Human",
            other_characters_story_key="other-characters/minerva-themis.md",
        ),
        # TODO: Does fragment link to world lore? If so, how?
        NPCEntry(name="Grand Magister, The Steadfast", species="Human"),
        NPCEntry(name="Sol"),
        NPCEntry(name="Valeria", species="Human"),
        NPCEntry(name="Felix", species="Human"),
        NPCEntry(name="Charis", species="Human"),
        NPCEntry(name="Farris", species="Human"),
        NPCEntry(name="Vitus", species="Human"),
        NPCEntry(name="Pallas", species="Human"),
        NPCEntry(name="Darius", species="Human"),
        NPCEntry(name="Marcus", species="Human"),
    ],
    locations=[
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("Golden Chariot", region="Solana"),
        LocationEntry("Ironsong Forge", region="Solana"),
        LocationEntry("Library of Illumination", region="Solana"),
        LocationEntry("Amphitheatre", region="Solana"),
        LocationEntry("Solstice of Laurels", region="Solana", lore_fragment="solstice-of-laurels"),
        LocationEntry(
            "The Awakening Ceremony",
            region="Solana",
            lore_fragment="the-awakening-ceremony",
        ),
        LocationEntry("The Light of Sol", region="Solana", lore_fragment="the-light-of-sol"),
        LocationEntry("Silvarium", region="Solana"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("Forward Camps", region="The Savage Lands"),
        LocationEntry("The Grand Council", region="Solana", lore_fragment="the-grand-council"),
        LocationEntry("The Savage Wilds", region="The Savage Lands"),
        LocationEntry("Ceremonial Chamber", region="Solana"),
    ],
    regions=[RegionEntry("Solana"), RegionEntry("The Savage Lands")],
    monsters=[],
    fauna=[],
    food_drink=[],
    weapons=["dawnblade"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/kill-or-be-killed.md",
    story_type="main-story",
    title="Kill or be Killed",
    authors="Nicola Price",
    artists="MJ Fetesio",
    source_link="https://fabtcg.com/hero/rhinar/story/rhinar-story/",
    publication_date="",
    thumbnail_image_link="",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=lROh5AG3DoI",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["rhinar"],
    npcs=[],
    locations=[
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("Rhinar's Territory", region="The Savage Lands"),
    ],
    regions=[RegionEntry("The Savage Lands")],
    monsters=[],
    fauna=[
        FaunaEntry("Jacara"),
        FaunaEntry("Strix"),
        FaunaEntry("Skera"),
        FaunaEntry("Peluda"),
        FaunaEntry("Ank'is"),
        FaunaEntry("Brawnhide"),
        FaunaEntry("Rek'vas"),
    ],
    flora=[FloraEntry("Rashari"), FloraEntry("Haldor")],
    food_drink=[],
    weapons=[],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/wanderings-in-the-mists.md",
    story_type="main-story",
    title="Wanderings in the Mists",
    authors="Nicola Price",
    artists="MJ Fetesio, Sindy Wo",
    source_link="https://fabtcg.com/hero/katsu-the-wanderer/story/katsu-story/",
    publication_date="",
    thumbnail_image_link="",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=zgk-_YeeqxQ",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["katsu"],
    npcs=[
        NPCEntry("Master Takumi", species="Human", status="Alive"),
        NPCEntry("Master Saori", species="Human", status="Alive"),
    ],
    locations=[
        LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge"),
        LocationEntry("Mugenshi Ancestral Shrine", region="Misteria"),
        LocationEntry("Mugenshi Village", region="Misteria"),
        LocationEntry("Mistcloak Gully", region="Misteria", lore_fragment="mistcloak-gully"),
        LocationEntry("Aui's Scales Strongholds", region="Misteria"),
    ],
    regions=[RegionEntry("Misteria")],
    monsters=[],
    fauna=[],
    flora=[],
    food_drink=[],
    weapons=["harmonized-kodachi"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/slings-and-arrows.md",
    story_type="main-story",
    title="Slings and Arrows",
    source_link="https://fabtcg.com/hero/azalea/story/slings-and-arrows/",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=BAhPVnQePQE",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["azalea"],
    locations=[
        LocationEntry(
            "Blackjack's Tavern",
            region="The Pits",
            lore_fragment="blackjacks-mercenary-company",
        )
    ],
    regions=[RegionEntry("The Pits"), RegionEntry("Metrix")],
    monsters=[MonsterEntry("Dregs")],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/cards-on-the-table.md",
    story_type="main-story",
    title="Cards on the Table",
    source_link="https://fabtcg.com/hero/azalea/story/cards-on-the-table/",
    publication_date="",
    thumbnail_image_link="",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=BAhPVnQePQE&t=267s",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["azalea"],
    npcs=[
        NPCEntry("Moray", species="Human"),
        NPCEntry("Greenbird", species="Human"),
    ],  # TODO: fragment to the tavern?
    locations=[
        LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw"),
        LocationEntry(
            "Blackjack's Tavern",
            region="The Pits",
            lore_fragment="blackjacks-mercenary-company",
        ),
    ],
    regions=[RegionEntry("The Pits"), RegionEntry("Metrix")],
    monsters=[],
    fauna=[],
    flora=[],
    food_drink=[FoodDrinkEntry("Blackjack's Whiskey", kind="Drink")],
    weapons=[],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/a-bird-in-the-hand.md",
    story_type="main-story",
    title="A Bird in the Hand",
    source_link="https://fabtcg.com/hero/azalea/story/a-bird-in-the-hand/",
    publication_date="",
    thumbnail_image_link="",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=BAhPVnQePQE&t=1030s",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["azalea"],
    npcs=[
        NPCEntry("Lena Belle", species="Human"),
        NPCEntry("Greenbird", species="Human"),  # TODO: fragment to the tavern?
        NPCEntry("Barton", species="Human"),
        NPCEntry("The Harvester", species="Human"),
        NPCEntry("Hog", species="Human"),
        NPCEntry("Moray", species="Human"),
        NPCEntry("Jackdaw", species="Human"),
        NPCEntry("Cobbs", species="Human"),
    ],
    locations=[
        LocationEntry(
            "Blackjack's Tavern",
            region="The Pits",
            lore_fragment="blackjacks-mercenary-company",
        ),
        LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw"),
        LocationEntry("Barton's House", region="The Pits"),
    ],
    regions=[RegionEntry("The Pits"), RegionEntry("Metrix")],
    monsters=[],
    fauna=[],
    flora=[],
    food_drink=[FoodDrinkEntry("Blackjack's Whiskey", kind="Drink")],
    weapons=[],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/omens-of-the-third-age/omens-in-the-sky.md",
    story_type="main-story",
    title="Omens in the Sky",
    source_link="https://fabtcg.com/articles/omens-in-the-sky/",
    publication_date="2026-05-08",
    narrated_videos=[
        NarratedVideoEntry(
            author="St_Havock",
            source_link="https://www.youtube.com/watch?v=z42BCa8L3hs",
            channel_link="https://www.youtube.com/@St_Havock",
        )
    ],
    heroes=["oscilio", "zyggy", "aurora"],
    locations=[
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("The Flow", region="Aria", lore_fragment="the-flow"),
        LocationEntry("Volthaven", region="Aria", lore_fragment="enion"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("Voltaris Gem", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("Shyldverk", region="Aria", lore_fragment="shyldverk"),
        LocationEntry("Astral Bridge", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("i'Arathael"),
        LocationEntry("The Northern Realms", region="Solana", lore_fragment="the-northern-realms"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
        RegionEntry("Misteria"),
        RegionEntry("Metrix"),
        RegionEntry("Solana"),
    ],
    weapons=["star-fall", "scorpio-comet-tail"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/omens-of-the-third-age/fall-of-valahai.md",
    story_type="main-story",
    title="Fall of Valahai",
    authors="Corey J. White, Becca Barnes, Rachel Rees, Aidan Kwasneski, Edwin McRae",
    artists="Narendra B Adi, Federico Musetti, Olga Tereshenko, Simon Wong, Carlos Cruchaga",
    source_link="https://fabtcg.com/articles/fall-of-valahai/",
    publication_date="2026-06-09",
    heroes=["zyggy", "oscilio"],
    npcs=[
        NPCEntry(name="Wendryn", species="Human", status="Deceased"),
        NPCEntry(name="Astrea Quazor", species="Human", status="Alive"),
        NPCEntry(name="Auric Seeress", species="Human", status="Deceased"),
        NPCEntry(name="Wynvarin", species="Human"),
        NPCEntry(name="Yvor", species="Ancient", status="Deceased"),
        NPCEntry(name="Davnir", species="Ancient", status="Deceased"),
        NPCEntry(name="Galcia", species="Ancient", status="Deceased"),
    ],
    locations=[
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("Shyldverk", region="Aria", lore_fragment="shyldverk"),
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Isenloft", region="Aria"),
        LocationEntry("Aldengrove", region="Aria"),
        LocationEntry("Isen Ranges", region="Aria"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
        LocationEntry("Astral Bridge", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("Arcane Hall", region="Nebulus Rift", lore_fragment="auric-keep"),
        LocationEntry("Voltaris Gem", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("Anvilheim"),
        LocationEntry("Dawnhaven"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    monsters=[
        MonsterEntry("Ravenir"),
    ],
    weapons=["aphrodias"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/usurp-the-shadow-throne/letters-from-the-beyond.md",
    story_type="main-story",
    title="Letters from the Beyond",
    authors="Corey J White, Becca Barnes, Rachel Rees, Aidan Kwasneski, Kasharn Rao, Edwin McRae",
    artists="Sebastian Giacobino",
    source_link="https://fabtcg.com/articles/letters-from-the-beyond/",
    publication_date="2026-07-07",
    heroes=["baalghor", "chane", "vynnset"],
    npcs=[
        NPCEntry(name="Kien", species="Human", status="Deceased"),
        NPCEntry(name="Ursur", species="Embra"),
    ],
    locations=[
        LocationEntry("i'Arathael"),
        LocationEntry("Shadowrealm"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry(
            "The Shadow Crypts",
            region="Demonastery",
            lore_fragment="the-shadow-crypts",
        ),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
    ],
    monsters=[
        MonsterEntry("Shadowrealm Walker"),
    ],
    weapons=["galaxxi-black"],
    dry_run=True,
)
# TODO: group — Disciples of Pain
# TODO: group — Runeblades

db.upsert_story(
    path="src/main-story/usurp-the-shadow-throne/agony-in-light.md",
    story_type="main-story",
    title="Agony in Light",
    authors="Corey J. White, Rachel Rees, Aidan Kwasneski, Kasharn Rao, Edwin McRae",
    artists="Olga Tereshenko, Dominik Mayer, Simon Dominic, Isuardi Therianto",
    source_link="https://fabtcg.com/articles/agony-in-light/",
    publication_date="2026-07-31",
    heroes=["vynnset", "boltyn", "dorinthea", "levia"],
    npcs=[
        NPCEntry(name="Nasreth", species="Embra"),
        NPCEntry(name="Blasmophet", species="Embra"),
        NPCEntry(name="Bellona, the Wartune Herald", species="Herald"),
        NPCEntry(name="Eirina", species="Human Cleric", status="Dead"),
        NPCEntry(name="Sol"),
    ],
    locations=[
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Solana"),
        RegionEntry("Demonastery"),
    ],
    weapons=["flail-of-agony", "raydn-duskbane"],
    dry_run=True,
)

# -------------------------------------------------------------------------------------------------------------------- #
# Short Stories
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/short-stories/usurp-the-shadow-throne/open-the-gates.md",
    story_type="short-stories",
    title="Open the Gates",
    publication_date="2026-07-16",
    heroes=["viserai", "levia", "malice"],
    npcs=[
        NPCEntry(name="Blasmophet", species="Embra"),
    ],
    locations=[
        LocationEntry("The Abyss"),
        LocationEntry("Neverest"),
        LocationEntry("Shadowrealm"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
    ],
    dry_run=True,
)
# TODO: group — Gloomblades

# -------------------------------------------------------------------------------------------------------------------- #
# Summaries
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/summaries/war-of-the-monarch-pt-1.md",
    story_type="summaries",
    title="War of the Monarch, Part 1",
    heroes=[
        "viserai",
        "chane",
        "levia",
        "vynnset",
        "prism",
        "boltyn",
        "dorinthea",
        "shiyana",
    ],
    npcs=[
        NPCEntry(name="Grand Magister, the Devout", species="Human", status="Assumed Dead"),
        NPCEntry(name="Apostate", species="Human"),
        NPCEntry(name="Lord Sutcliffe", species="Human", status="Just a head"),
        NPCEntry(name="Lady Bartimont"),
        NPCEntry(name="Ursur", species="Embra"),
        NPCEntry(name="Blasmophet", species="Embra"),
        NPCEntry(name="Nasreth", species="Embra"),
        NPCEntry(name="Sol", species="Aesir"),
        NPCEntry(name="Suraya, Archangel of Knowledge", species="Herald"),
        NPCEntry(name="Bellona, the Wartune Herald", species="Herald"),
        NPCEntry(name="Minerva Themis", species="Human", status="Deceased"),
    ],
    locations=[
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry("Library of Illumination", region="Solana"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
        RegionEntry("Volcor"),
    ],
    dry_run=True,
)
# TODO: metadata — authors / source_link / publication_date unknown for this recap

db.upsert_story(
    path="src/summaries/war-of-the-monarch-pt-2.md",
    story_type="summaries",
    title="War of the Monarch, Part 2",
    authors="Rachel Rees, Kasharn Rao, Aidan Kwasneski, Edwin McRae",
    source_link="https://fabtcg.com/usurp-the-shadow-throne-lore-recap/",
    publication_date="2026-07-17",
    heroes=[
        "viserai",
        "chane",
        "levia",
        "vynnset",
        "prism",
        "bravo",
        "oldhim",
        "lexi",
        "briar",
        "dorinthea",
        "boltyn",
        "hala",
    ],
    npcs=[
        NPCEntry(name="Apostate", species="Human"),
        NPCEntry(name="Lord Sutcliffe", species="Human", status="Just a head"),
        NPCEntry(name="Ursur", species="Embra"),
        NPCEntry(name="Blasmophet", species="Embra"),
        NPCEntry(name="Sol", species="Aesir"),
    ],
    locations=[
        LocationEntry("Dimenxxional Gateway", region="Demonastery"),
        LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
        LocationEntry(
            "The Northern Realms",
            region="Solana",
            lore_fragment="the-northern-realms",
        ),
        LocationEntry("The Solarium", region="Solana"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Nebulus Rift"),
        RegionEntry("Solana"),
    ],
    dry_run=True,
)

# -------------------------------------------------------------------------------------------------------------------- #
# Flavour
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    heroes=["aurora", "lexi"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Astrea Quazor"),
        NPCEntry(name="Auric Seeress"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Rupius, Auric Scrollmaster"),
        NPCEntry(name="Yvor"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Daryas Nimbus"),
        NPCEntry(name="Freya Eldingsturm"),
        NPCEntry(name="Maela Isulfv"),
        NPCEntry(name="Maela Sharena"),
        NPCEntry(name="Reznyr Eldingsturm"),
        NPCEntry(name="Skynda Feyscout"),
        NPCEntry(name="Vyhara Cloudburst"),
    ],
    locations=[
        LocationEntry("Enion", region="Aria"),
        LocationEntry("Valahai", region="Aria"),
        LocationEntry("Volthaven", region="Aria"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    dry_run=True,
)

# Monarch's four Heralds are printed without flavour text; the lines the page used
# to carry belong to the promo printings and now live on non-set-cards.md. This
# declaration exists to repoint Themis, Aegis and Avalon off this page — Bellona
# stays, still named by Chiara Suncrest's line on MON081.
db.upsert_story(
    path="src/flavour/monarch.md",
    story_type="flavour",
    title="Monarch",
    heroes=["prism"],
    hero_fragments={"prism": "celestial-cataclysm---mon062"},
    npcs=[
        NPCEntry(name="Amira Surana"),
        NPCEntry(name="Astra Morena"),
        NPCEntry(name="Aurea, Champion of the Dawn"),
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Chancellor Helena Primavera"),
        NPCEntry(name="Chancellor Hypatia"),
        NPCEntry(name="Chiara Suncrest"),
        NPCEntry(name="Danu Ashenguard"),
        NPCEntry(name="Ersebet"),
        NPCEntry(name="Grand Magister, the Radiant"),
        NPCEntry(name="Harland"),
        NPCEntry(name="Harold Honeysett"),
        NPCEntry(name="Jackdaw"),
        NPCEntry(name="Kirigami"),
        NPCEntry(name="Merlen Rivera"),
        NPCEntry(name="Nestus"),
        NPCEntry(name="Sanni"),
        NPCEntry(name="Suraya, Archangel of Knowledge"),
        NPCEntry(name="Vidya Willowmere"),
    ],
    regions=[
        RegionEntry("Solana"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/non-set-cards.md",
    story_type="flavour",
    title="Non-Set Cards",
    npcs=[
        NPCEntry(name="Aegis, the Shield of Light"),
        NPCEntry(name="Avalon, Messenger of the Dawn"),
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Themis, Keeper of the Scales"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Auric Keep", region="Nebulus Rift"),
        LocationEntry("Enion", region="Aria"),
        LocationEntry("Volthaven", region="Aria"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/super-slam.md",
    story_type="flavour",
    title="Super Slam",
    heroes=["kayo", "lyath", "pleiades", "tuffnut", "victor-goldmane"],
    npcs=[
        # Already curated — named here only to link them to this page. The DB holds
        # the fightmasters under their bare names, not the "Fightmaster X" form the
        # cards use.
        NPCEntry(name="Batbiter"),
        NPCEntry(name="Emeviere"),
        NPCEntry(name="Fightmaster Kox"),
        NPCEntry(name="Fightmaster Rusty"),
        NPCEntry(name="Luca, Arena Cicerone"),
        NPCEntry(name="Moloca"),
        NPCEntry(name="Slapstick Sal"),
        NPCEntry(name="Speakeasy"),
        # New with this set. Species is unattested in the flavour text.
        NPCEntry(name="Foreman Pebb"),
        NPCEntry(name="Fugger Grimes"),
        NPCEntry(name="Helx"),
        NPCEntry(name="Salvador Stallion"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Den of Beasts"),
        LocationEntry("Grinning Boar Cantina"),
        # A Deathmatch venue, distinct from "The Maw" in the Pits. Region is left
        # blank to match its siblings (The Undercroft, The Moat, Arena Barracks).
        LocationEntry("Infernal Maw"),
        LocationEntry("The Moat"),
        LocationEntry("The Undercroft"),
    ],
    regions=[
        RegionEntry("The Savage Lands"),
    ],
    dry_run=True,
)
# TODO: group — Baleful Horde, Boulder Clan, Champions of Chivalry, Fury Fists,
# Glorytown Gladiators, Jungle Slayers, Mythmakers, Prowlers, Wild Wonders

db.upsert_story(
    path="src/flavour/mastery-pack-guardian.md",
    story_type="flavour",
    title="Mastery Pack Guardian",
    heroes=["fai", "valda"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        # MPG029 prints "Archangel Aegis"; that is a new epithet for the Herald of
        # Protection already registered under her Monarch title, not a new character.
        NPCEntry(name="Aegis, the Shield of Light"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Maela One-eye"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("The Everfest Carnival", region="Aria"),
    ],
    regions=[
        RegionEntry("Aria"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/mastery-pack-warrior.md",
    story_type="flavour",
    title="Mastery Pack Warrior",
    npcs=[
        # Already curated — named here only to link them to this page.
        # MPW048 prints "Lieutenant Farris"; Pride of the Ironsongs introduces the
        # same Solanian lieutenant on the same Savage Lands frontier.
        NPCEntry(name="Farris"),
        NPCEntry(name="Fightmaster Kox"),
        NPCEntry(name="Fightmaster Rusty"),
        NPCEntry(name="Lieutenant Timaeus"),
        # New with this set. Species is unattested in the flavour text.
        NPCEntry(name="Captain Shevez"),
        NPCEntry(name="Inquisitor Aricia"),
        NPCEntry(name="Lucilla the Setting Sun"),
        NPCEntry(name="Tasha of Deshvahan"),
        NPCEntry(name="The Bastion"),
        NPCEntry(name="Vanik Silvertooth"),
    ],
    locations=[
        LocationEntry("Dawnhaven"),
        LocationEntry("Deshvahan", region="Volcor"),
        LocationEntry("Fiddler's Green", region="High Seas"),
        LocationEntry("Neelasha"),
        LocationEntry("Octomilitia", region="Solana"),
        LocationEntry("Solarium", region="Solana"),
        LocationEntry("Valahai", region="Aria"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
    ],
    dry_run=True,
)

# -------------------------------------------------------------------------------------------------------------------- #
# Digital Tiles
# -------------------------------------------------------------------------------------------------------------------- #

db.upsert_story(
    path="src/digital-tiles/omens-of-the-third-age/omens-of-the-third-age.md",
    story_type="digital-tiles",
    title="Omens of the Third Age",
    heroes=["aurora", "oscilio", "zyggy"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Maela Isulfv"),
        NPCEntry(name="Yvor"),
        # New with this set.
        NPCEntry(name="Karl"),
    ],
    locations=[
        LocationEntry("Astral Bridge", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/bright-lights/bright-lights.md",
    story_type="digital-tiles",
    title="Bright Lights",
    # The Fabricate tile is signed "Jules Teklovossen" — that is the hero
    # Teklovossen under his full name, not the separate NPC row of that name.
    heroes=["dash", "teklovossen"],
    hero_fragments={"dash": "dash-io", "teklovossen": "fabricate"},
    locations=[
        LocationEntry("Cogwerx Conglomerate", region="Metrix", lore_fragment="cogwerx-conglomerate"),
        # New with this set. The realm of data made manifest, reached through Teklo's
        # Data Link — named on the main-story and flavour pages for this set too.
        LocationEntry("Eidolon", region="Metrix"),
        LocationEntry("Iron Assembly", region="Metrix", lore_fragment="iron-assembly"),
        LocationEntry("Lowlake", region="Metrix"),
        LocationEntry("Teklo Industries", region="Metrix", lore_fragment="teklo-industries"),
    ],
    regions=[
        RegionEntry("Metrix"),
    ],
    equipment=["cogwerx-base-head", "evo-command-center", "evo-data-mine"],
    dry_run=True,
)
# TODO: group — Steelstreet Enforcers

db.upsert_story(
    path="src/digital-tiles/compendium-of-rathe/compendium-of-rathe.md",
    story_type="digital-tiles",
    title="Compendium of Rathe",
    heroes=["dorinthea", "jarl"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Sol"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Boo"),
        # A dragon, not a person — there is no dragons table, so it is carried
        # as an NPC row and relabelled to "creature" in hints_supplement.json.
        NPCEntry(name="Miragai", species="Dragon"),
    ],
    locations=[
        LocationEntry("Demonastery", region="Demonastery"),
        # New with this set. The Demonastery's mortuary quarter.
        LocationEntry("Necropolis", region="Demonastery"),
        LocationEntry("The Awakening Ceremony", region="Solana", lore_fragment="the-awakening-ceremony"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("High Seas"),
        RegionEntry("Misteria"),
        RegionEntry("Solana"),
        RegionEntry("Volcor"),
    ],
    weapons=["dawnblade"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/crucible-of-war/crucible-of-war.md",
    story_type="digital-tiles",
    title="Crucible of War",
    heroes=["azalea", "dorinthea", "emperor", "kassai", "teklovossen"],
    hero_fragments={
        "dorinthea": "courage-of-bladehold",
        "emperor": "cindering-foresight",
        "kassai": "cintari-saber",
        "teklovossen": "teklovossens-workshop",
    },
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="General Ekoda"),
        NPCEntry(name="Lord Sabuto"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Magnus the Vigilant"),
        NPCEntry(name="Sol"),
        NPCEntry(name="Theodore Hamilton Scarborough"),
        NPCEntry(name="Írunaméabh"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court"),
        LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge"),
        LocationEntry("The Badlands", region="Volcor"),
        LocationEntry("The Broken Chariot Tavern"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("Zancaro", region="Volcor"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Metrix"),
        RegionEntry("Misteria"),
        RegionEntry("Solana"),
        RegionEntry("The Pits"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
    ],
    fauna=[
        FaunaEntry(name="Azeri"),
        FaunaEntry(name="Rek'vas"),
    ],
    weapons=[
        "cintari-saber",
        "mandible-claw",
        "plasma-barrel-shot",
        "red-liner",
        "sledge-of-anvilheim",
        "talishar-the-lost-prince",
        "zephyr-needle",
    ],
    equipment=[
        "bloodsheath-skeleta",
        "breeze-rider-boots",
        "courage-of-bladehold",
        "crater-fist",
        "gamblers-gloves",
        "metacarpus-node",
        "skullhorn",
        "viziertronic-model-i",
    ],
    dry_run=True,
)
# TODO: group — Lost Clans, Mugenshi

db.upsert_story(
    path="src/digital-tiles/everfest/everfest.md",
    story_type="digital-tiles",
    title="Everfest",
    heroes=["boltyn"],
    hero_fragments={"boltyn": "swarming-gloomveil"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Jezabelle, Everfest Healer and Allsorts"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Sol"),
    ],
    locations=[
        LocationEntry("Demonastery", region="Demonastery"),
        LocationEntry("Isenloft", region="Aria"),
        LocationEntry("Skylark Peak", region="Misteria"),
        LocationEntry("The Badlands", region="Volcor"),
        LocationEntry("The Everfest Carnival", region="Aria", lore_fragment="the-everfest-carnival"),
        LocationEntry("The Golden Gnome", region="Aria"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Metrix"),
        RegionEntry("Misteria"),
        RegionEntry("The Pits"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
    ],
    fauna=[
        FaunaEntry(name="Kaie'o"),
        FaunaEntry(name="Kraken"),
        FaunaEntry(name="Meep"),
        # New with this set, all three named only as tavern-tale creatures.
        FaunaEntry(name="Ebon Serpent"),
        FaunaEntry(name="Kumiho"),
        FaunaEntry(name="Mireoa"),
    ],
    weapons=["dreadbore", "krakens-aethervein"],
    equipment=[
        "arcane-lantern",
        "crown-of-reflection",
        "earthlore-bounty",
        "helm-of-sharp-eye",
        "mask-of-the-pouncing-lynx",
        "stalagmite-bastion-of-isenloft",
        "vexing-quillhand",
    ],
    dry_run=True,
)
# TODO: group — Shieldbearers, The Grey

db.upsert_story(
    path="src/digital-tiles/heavy-hitters/heavy-hitters.md",
    story_type="digital-tiles",
    title="Heavy Hitters",
    # Hood of Red Sand names "The Terror of the Golden Sands" — that is Kassai.
    heroes=["kassai", "olympia", "rhinar", "victor-goldmane"],
    hero_fragments={"rhinar": "show-no-mercy", "victor-goldmane": "aurum-aegis"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Demetrios"),
    ],
    locations=[
        # New, though it is named on eleven other pages already. Region is left
        # blank to match its siblings (The Moat, The Undercroft, Arena Barracks).
        LocationEntry("Deathmatch Arena"),
    ],
    equipment=["aurum-aegis", "gauntlets-of-iron-will", "hood-of-red-sand"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/high-seas/high-seas.md",
    story_type="digital-tiles",
    title="High Seas",
    heroes=["gravy"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Kelpie"),
        NPCEntry(name="Moray Le Fay"),
        NPCEntry(name="Scooba"),
        NPCEntry(name="Swabbie"),
        # New with this set.
        NPCEntry(name="Captain Bludge"),
        NPCEntry(name="Chowder", species="Zombie"),
        # "Dhani death-mage" — Dhani is the culture, not a species, so species is
        # left to default to "Unknown".
        NPCEntry(name="Thanuella"),
    ],
    locations=[
        LocationEntry("Dreadfall Reach", region="High Seas"),
        LocationEntry("Piper's Pier", region="High Seas"),
    ],
    regions=[
        RegionEntry("High Seas"),
    ],
    monsters=[
        MonsterEntry(name="Necrophage"),
    ],
    fauna=[
        FaunaEntry(name="Kraken"),
        FaunaEntry(name="Sawmaw"),
        # New with this set, named only as an ingredient on Chowder's menu.
        FaunaEntry(name="Kulpie"),
    ],
    equipment=["dead-threads"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/monarch/monarch.md",
    story_type="digital-tiles",
    title="Monarch",
    heroes=["boltyn"],
    hero_fragments={"boltyn": "seek-enlightenment"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Blasmophet"),
        NPCEntry(name="Sol"),
        NPCEntry(name="Ursur"),
    ],
    locations=[
        LocationEntry("Blasmophet's Domain", region="Demonastery"),
        LocationEntry("Solana", region="Solana"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("The Northern Realms", region="Solana", lore_fragment="the-northern-realms"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
    ],
    weapons=["galaxxi-black"],
    equipment=["aether-ironweave"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/part-the-mistveil/part-the-mistveil.md",
    story_type="digital-tiles",
    title="Part the Mistveil",
    heroes=["enigma", "nuu"],
    hero_fragments={"enigma": "10000-year-reunion"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Dan Lu, Kotori Galewarden"),
        NPCEntry(name="Kazuo"),
        NPCEntry(name="Kouki"),
        NPCEntry(name="Master Udo"),
        NPCEntry(name="Shio"),
        NPCEntry(name="Xin"),
    ],
    locations=[
        # Spelled to match the live row that Wanderings in the Mists registers.
        # "Aui's Scale Strongholds" is an unlinked duplicate awaiting deletion.
        LocationEntry("Aui's Scales Strongholds", region="Misteria"),
        LocationEntry("Kirohime Gate", region="Misteria"),
        LocationEntry("Mistcloak Gully", region="Misteria", lore_fragment="mistcloak-gully"),
        # Murky Water's "Butcher" is the hero Riptide; deliberately not linked, as
        # the tile never names him and the DB holds two unrelated Butcher NPCs.
        LocationEntry("Seethe", region="The Pits"),
    ],
    regions=[
        RegionEntry("Misteria"),
        RegionEntry("The Pits"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/rosetta/rosetta.md",
    story_type="digital-tiles",
    title="Rosetta",
    heroes=["aurora", "florian", "melody", "oscilio", "verdance"],
    hero_fragments={"aurora": "aurora-shooting-star", "melody": "sanctuary-of-aria"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Davnir"),
        NPCEntry(name="Queen of Candlehold"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold"),
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Rotwood", region="Aria"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
    ],
    regions=[
        RegionEntry("Aria"),
    ],
    weapons=[
        "rotwood-reaper",
        "staff-of-verdant-shoots",
        "star-fall",
        "volzar-the-lightning-rod",
    ],
    equipment=["aether-bindings-of-the-third-age"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/tales-of-aria/tales-of-aria.md",
    story_type="digital-tiles",
    title="Tales of Aria",
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Davnir"),
        NPCEntry(name="Queen of Candlehold"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold"),
        LocationEntry("Isenloft", region="Aria"),
        LocationEntry("Mount Heroic", region="Aria"),
        LocationEntry("Mt. Isen", region="Aria", lore_fragment="mount-isen"),
        LocationEntry("Volthaven", region="Aria", lore_fragment="enion"),
    ],
    regions=[
        RegionEntry("Aria"),
    ],
    dry_run=True,
)
# TODO: group — Wardens

db.upsert_story(
    path="src/digital-tiles/the-hunted/the-hunted.md",
    story_type="digital-tiles",
    title="The Hunted",
    heroes=["arakni-huntsman", "cindra", "emperor", "taipanis"],
    hero_fragments={"cindra": "wrath-of-retribution"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Dr. Krest Mortimer, 'The Fixer'"),
    ],
    locations=[
        LocationEntry("Ashvahan", region="Volcor"),
        LocationEntry("Deshvahan", region="Volcor", lore_fragment="deshvahan"),
        LocationEntry("Skein", region="The Pits"),
    ],
    regions=[
        RegionEntry("The Pits"),
        RegionEntry("Volcor"),
    ],
    weapons=["graphene-chelicera", "mark-of-the-huntsman"],
    equipment=[
        "dragonscaler-flight-path",
        "kabuto-of-imperial-authority",
        "mask-of-deceit",
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/uprising/uprising.md",
    story_type="digital-tiles",
    title="Uprising",
    heroes=["dromai", "emperor", "fai"],
    locations=[
        LocationEntry("Zancaro", region="Volcor"),
    ],
    regions=[
        RegionEntry("Volcor"),
    ],
    weapons=["storm-of-sandikai"],
    dry_run=True,
)
