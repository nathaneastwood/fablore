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
      LocationEntry("Aldevyr", region="Aria", notes="A village in Aria"),
      LocationEntry("Fractal Scar", region="Aria"),
      LocationEntry("Milesian Ranges"),
    ],
    regions=[RegionEntry("Aria")],
    monsters=[
      MonsterEntry(
        name="Dregs",
        description="Humanoid figures with bloated, rotting bodies; their faces a mass of melted, discoloured skin, dripping the length of their bony, twisted limbs."
      )
    ],
    fauna=[
      FaunaEntry("Cesari"),
      FaunaEntry("Meep"),
      FaunaEntry("Kaie'o"),
      FaunaEntry("Fianna"),
      FaunaEntry("Vitr'eo")
    ],
    food_drink=[FoodDrinkEntry(name="Alder Cider", kind="Drink")],
    weapons=["anothos"],
    dry_run = True,
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
    dry_run = True,
)
