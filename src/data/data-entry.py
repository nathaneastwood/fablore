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
    dry_run=True
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
    dry_run=True
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
    dry_run=True
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
    dry_run=True
)

db.upsert_story(
    path="src/main-story/crucible-of-war/edge-of-autumn.md",
    story_type="main-story",
    title="Edge of Autumn",
    source_link="https://fabtcg.com/hero/ira-3/story/edge-of-autumn/",
    weapons=["edge-of-autumn"],
    locations=[LocationEntry("Ikaru", region="Misteria", lore_fragment="ikaru")],
    dry_run=True
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/a-rising-star.md",
    story_type="main-story",
    title="A Rising Star",
    authors="Nicola Price",
    artists="MJ Fetesio, Sindy Wo",
    source_link="https://fabtcg.com/hero/bravo-4/story/bravo-showtopper-story/",
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=E6JoDmEbTgU', channel_link='https://www.youtube.com/@St_Havock')
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
      LocationEntry("The Everfest Carnival", region="Aria", lore_fragment="the-everfest-carnival"),
      LocationEntry("Legendarium", region="Aria", lore_fragment="the-everfest-carnival"),
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
      FaunaEntry("Vitr'eo")
    ],
    food_drink=[FoodDrinkEntry(name="Alder Cider", kind="Drink")],
    weapons=["anothos"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/pride-of-the-ironsongs.md",
    story_type="main-story",
    title='Pride of the Ironsongs',
    authors='Nicola Price',
    artists='MJ Fetesio, Sindy Wo',
    source_link='https://fabtcg.com/hero/dorinthea/story/story/',
    publication_date='',
    thumbnail_image_link='',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=AuOKr_eoDLY', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["dorinthea", "hala"],
    npcs=[
      NPCEntry(name="Minerva Themis", species="Human", other_characters_story_key="other-characters/minerva-themis.md"),
      NPCEntry(name="Grand Magister, The Steadfast", species="Human"), # TODO: Does fragment link to world lore? If so, how?
      NPCEntry(name="Sol"),
      NPCEntry(name="Valeria", species="Human"),
      NPCEntry(name="Felix", species="Human"),
      NPCEntry(name="Charis", species="Human"),
      NPCEntry(name="Farris", species="Human"),
      NPCEntry(name="Vitus", species="Human"),
      NPCEntry(name="Pallas", species="Human"),
      NPCEntry(name="Darius", species="Human"),
      NPCEntry(name="Marcus", species="Human")
    ],
    locations=[
      LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol"),
      LocationEntry("Golden Chariot", region="Solana"),
      LocationEntry("Ironsong Forge", region="Solana"),
      LocationEntry("Library of Illumination", region="Solana"),
      LocationEntry("Amphitheatre", region="Solana"),
      LocationEntry("Solstice of Laurels", region="Solana", lore_fragment="solstice-of-laurels"),
      LocationEntry("The Awakening Ceremony", region="Solana", lore_fragment="the-awakening-ceremony"),
      LocationEntry("The Light of Sol", region="Solana", lore_fragment="the-light-of-sol"),
      LocationEntry("Silvarium", region="Solana"),
      LocationEntry("The Golden Fields", region="Solana"),
      LocationEntry("Forward Camps", region="The Savage Lands"),
      LocationEntry("The Grand Council", region="Solana", lore_fragment="the-grand-council"),
      LocationEntry("The Savage Wilds", region="The Savage Lands"),
      LocationEntry("Ceremonial Chamber", region="Solana")
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
    title='Kill or be Killed',
    authors='Nicola Price',
    artists='MJ Fetesio',
    source_link='https://fabtcg.com/hero/rhinar/story/rhinar-story/',
    publication_date='',
    thumbnail_image_link='',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=lROh5AG3DoI', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["rhinar"],
    npcs=[],
    locations=[
      LocationEntry("The Golden Fields", region="Solana"),
      LocationEntry("Rhinar's Territory", region="The Savage Lands")
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
      FaunaEntry("Rek'vas")
    ],
    flora=[FloraEntry("Rashari")],
    food_drink=[],
    weapons=[],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/welcome-to-rathe/wanderings-in-the-mists.md",
    story_type="main-story",
    title='Wanderings in the Mists',
    authors='Nicola Price',
    artists='MJ Fetesio, Sindy Wo',
    source_link='https://fabtcg.com/hero/katsu-the-wanderer/story/katsu-story/',
    publication_date='',
    thumbnail_image_link='',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=zgk-_YeeqxQ', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["katsu"],
    npcs=[
      NPCEntry("Master Takumi", species="Human"),
      NPCEntry("Master Saori", species="Human")
    ],
    locations=[
      LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge"),
      LocationEntry("Mugenshi Ancestral Shrine", region="Misteria"),
      LocationEntry("Mugenshi Village", region="Misteria"),
      LocationEntry("Mistcloak Gully", region="Misteria"),
      LocationEntry("Aui's Scales Strongholds", region="Misteria")
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
    title='Slings and Arrows',
    source_link='https://fabtcg.com/hero/azalea/story/slings-and-arrows/',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=BAhPVnQePQE', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["azalea"],
    locations=[
      LocationEntry("Blackjack's Tavern", region="The Pits", lore_fragment="blackjacks-mercenary-company")
    ],
    regions=[RegionEntry("The Pits"), RegionEntry("Metrix")],
    monsters=[MonsterEntry("Dregs")],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/cards-on-the-table.md",
    story_type="main-story",
    title='Cards on the Table',
    source_link='https://fabtcg.com/hero/azalea/story/cards-on-the-table/',
    publication_date='',
    thumbnail_image_link='',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=BAhPVnQePQE&t=267s', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["azalea"],
    npcs=[
      NPCEntry("Moray", species="Human"),
      NPCEntry("Greenbird", species="Human") # TODO: fragment to the tavern?
    ],
    locations=[
      LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw"),
      LocationEntry("Blackjack's Tavern", region="The Pits", lore_fragment="blackjacks-mercenary-company")
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
    title='A Bird in the Hand',
    source_link='https://fabtcg.com/hero/azalea/story/a-bird-in-the-hand/',
    publication_date='',
    thumbnail_image_link='',
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=BAhPVnQePQE&t=1030s', channel_link='https://www.youtube.com/@St_Havock')
    ],
    heroes=["azalea"],
    npcs=[
      NPCEntry("Lena Belle", species="Human"),
      NPCEntry("Greenbird", species="Human"), # TODO: fragment to the tavern?
      NPCEntry("Barton", species="Human"),
      NPCEntry("The Harvester", species="Human"),
      NPCEntry("Hog", species="Human"),
      NPCEntry("Moray", species="Human"),
      NPCEntry("Jackdaw", species="Human"),
      NPCEntry("Cobbs", species="Human")
    ],
    locations=[
      LocationEntry("Blackjack's Tavern", region="The Pits", lore_fragment="blackjacks-mercenary-company"),
      LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw"),
      LocationEntry("Barton's House", region="The Pits")
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
    title='Omens in the Sky',
    source_link="https://fabtcg.com/articles/omens-in-the-sky/",
    publication_date="2026-05-08",
    narrated_videos=[
      NarratedVideoEntry(author='St_Havock', source_link='https://www.youtube.com/watch?v=z42BCa8L3hs', channel_link='https://www.youtube.com/@St_Havock')
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
    dry_run=True
)
