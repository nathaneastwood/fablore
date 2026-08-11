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
        LocationEntry("Milesian Ranges"),
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
