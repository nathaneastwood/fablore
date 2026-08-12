"""Main story registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

# Every section module imports the whole entry set, so extending a declaration
# with a new entity type never also means editing the import. Unused names are
# deliberate.
from db import (  # noqa: F401
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    MonsterEntry,
    NarratedVideoEntry,
)

# NPCs, locations and regions are referenced, never constructed. Their ids are
# hashes of the fields written at the call site, so a second literal for the same
# entity competes with the first row instead of reusing it — that is how
# "The Shadow Crypts" became two rows. The canonical definition of each lives
# in entries/catalogue/; the three names are deliberately not imported above, so
# writing LocationEntry(...) here is a NameError rather than a silent new row.
from entries.catalogue import locations as loc, npcs as npc, regions as reg  # noqa: F401
from entries._runner import db

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
    locations=[loc.IKARU],
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
        npc.MAGNUS_THE_VIGILANT,
        npc.GAWAIN,
        npc.MORGAN,
        npc.MARBLES,
        npc.MIKAEL,
    ],
    locations=[
        loc.THE_FLOW,
        loc.THE_EVERFEST_CARNIVAL,
        loc.LEGENDARIUM,
        loc.THE_MAELA,
        loc.THE_VALDUR,
        loc.ALDEVYR,
        loc.FRACTAL_SCAR,
        # Named only here, by Mikael on his return to the Everfest — an Arian range.
        loc.MILESIAN_RANGES,
    ],
    regions=[reg.ARIA],
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
        npc.MINERVA_THEMIS,
        # TODO: Does fragment link to world lore? If so, how?
        npc.GRAND_MAGISTER_THE_STEADFAST,
        npc.SOL,
        npc.VALERIA,
        npc.FELIX,
        npc.CHARIS,
        npc.FARRIS,
        npc.VITUS,
        npc.PALLAS,
        npc.DARIUS,
        npc.MARCUS,
    ],
    locations=[
        loc.HAND_OF_SOL,
        loc.GOLDEN_CHARIOT,
        loc.IRONSONG_FORGE,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.AMPHITHEATRE,
        loc.SOLSTICE_OF_LAURELS,
        loc.THE_AWAKENING_CEREMONY,
        loc.THE_LIGHT_OF_SOL,
        loc.SILVARIUM,
        loc.THE_GOLDEN_FIELDS,
        loc.FORWARD_CAMPS,
        loc.THE_GRAND_COUNCIL,
        loc.THE_SAVAGE_WILDS,
        loc.CEREMONIAL_CHAMBER,
    ],
    regions=[reg.SOLANA, reg.THE_SAVAGE_LANDS],
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
        loc.THE_GOLDEN_FIELDS,
        loc.RHINAR_S_TERRITORY,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
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
        npc.MASTER_TAKUMI,
        npc.MASTER_SAORI,
    ],
    locations=[
        loc.MUGENSHI_GORGE,
        loc.MUGENSHI_ANCESTRAL_SHRINE,
        loc.MUGENSHI_VILLAGE,
        loc.MISTCLOAK_GULLY,
        loc.AUI_S_SCALES_STRONGHOLDS,
    ],
    regions=[reg.MISTERIA],
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
    locations=[loc.BLACKJACK_S_TAVERN],
    regions=[reg.THE_PITS, reg.METRIX],
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
        npc.MORAY,
        npc.GREENBIRD,
    ],  # TODO: fragment to the tavern?
    locations=[
        loc.THE_MAW,
        loc.BLACKJACK_S_TAVERN,
    ],
    regions=[reg.THE_PITS, reg.METRIX],
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
        npc.LENA_BELLE,
        npc.GREENBIRD,  # TODO: fragment to the tavern?
        npc.BARTON,
        npc.THE_HARVESTER,
        npc.HOG,
        npc.MORAY,
        npc.JACKDAW,
        npc.COBBS,
    ],
    locations=[
        loc.BLACKJACK_S_TAVERN,
        loc.THE_MAW,
        loc.BARTON_S_HOUSE,
    ],
    regions=[reg.THE_PITS, reg.METRIX],
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
        loc.ENION,
        loc.THE_FLOW,
        loc.VOLTHAVEN,
        loc.AURIC_KEEP,
        loc.VALAHAI,
        loc.VOLTARIS_GEM,
        loc.SHYLDVERK,
        loc.ASTRAL_BRIDGE,
        loc.I_ARATHAEL,
        loc.THE_NORTHERN_REALMS,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
        reg.MISTERIA,
        reg.METRIX,
        reg.SOLANA,
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
        npc.WENDRYN,
        npc.ASTREA_QUAZOR,
        npc.AURIC_SEERESS,
        npc.WYNVARIN,
        npc.YVOR,
        npc.DAVNIR,
        npc.GALCIA,
    ],
    locations=[
        loc.VALAHAI,
        loc.SHYLDVERK,
        loc.ENION,
        loc.ISENLOFT,
        loc.ALDENGROVE,
        loc.ISEN_RANGES,
        loc.AURIC_KEEP,
        loc.ASTRAL_BRIDGE,
        loc.ARCANE_HALL,
        loc.VOLTARIS_GEM,
        loc.ANVILHEIM,
        loc.DAWNHAVEN,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
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
        npc.KIEN,
        npc.URSUR,
    ],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_SHADOW_CRYPTS,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
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
        npc.NASRETH,
        npc.BLASMOPHET,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.EIRINA,
        npc.SOL,
    ],
    locations=[
        loc.HAND_OF_SOL,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.SOLANA,
        reg.DEMONASTERY,
    ],
    weapons=["flail-of-agony", "raydn-duskbane"],
    dry_run=True,
)
