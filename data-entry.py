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

# TODO: Fauna / Flora link to lore fragments?
#       Location rename? e.g. The Flow is not a location
