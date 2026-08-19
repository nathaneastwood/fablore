"""Main story registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

# Entities are referenced, never constructed. Every registry id is a hash of the
# fields written at the call site, so a second literal for the same entity
# competes with the first row instead of reusing it — that is how "The Shadow
# Crypts" became two rows. The canonical definition of each lives in
# entries/catalogue/; none of the entry classes are imported here, so writing
# LocationEntry(...) is a NameError rather than a silent new row.
from entries.catalogue import (  # noqa: F401
    fauna,
    flora,
    food_drink as food,
    locations as loc,
    monsters as mon,
    npcs as npc,
    regions as reg,
)

# NarratedVideoEntry is the one exception: a narrated reading belongs to one
# story, has no registry table and no id of its own, so it is per-declaration
# data rather than a shared entity.
from db import NarratedVideoEntry  # noqa: F401
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
    heroes=["ira"],
    npcs=[
        npc.JING,
        npc.XILIN,
    ],
    locations=[loc.IKARU],
    regions=[reg.MISTERIA],
    weapons=["edge-of-autumn"],
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
    monsters=[mon.DREGS],
    fauna=[
        fauna.CESARI,
        fauna.MEEP,
        fauna.KAIE_O,
        fauna.FIANNA,
        fauna.VITR_EO,
    ],
    food_drink=[food.ALDER_CIDER],
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
        fauna.JACARA,
        fauna.STRIX,
        fauna.SKERA,
        fauna.PELUDA,
        fauna.ANK_IS,
        fauna.BRAWNHIDE,
        fauna.REK_VAS,
    ],
    flora=[flora.RASHARI, flora.HALDOR],
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
    npcs=[npc.JACKDAW],
    locations=[loc.BLACKJACK_S_TAVERN],
    regions=[reg.THE_PITS, reg.METRIX],
    monsters=[mon.DREGS],
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
    food_drink=[food.BLACKJACK_S_WHISKEY],
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
    food_drink=[food.BLACKJACK_S_WHISKEY],
    weapons=[],
    # TODO: group — Arms Dealers (the gang Azalea is contracted against)
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
        mon.RAVENIR,
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
        mon.SHADOWREALM_WALKER,
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

db.upsert_story(
    path="src/main-story/crucible-of-war/no-smoke-without-fire.md",
    story_type="main-story",
    title="No Smoke Without Fire",
    artists="Nikolay Moskvin, Bramasta Aji",
    publication_date="2020-08-14",
    source_link="https://fabtcg.com/articles/no-smoke-without-fire/",
    heroes=["dorinthea", "kassai"],
    npcs=[npc.TAKA],
    locations=[
        loc.THE_SOLARIUM,
        loc.MT_VOLCOR,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/crucible-of-war/sutcliffes-research-notes.md",
    story_type="main-story",
    title="Sutcliffe's Research Notes",
    heroes=["viserai"],
    npcs=[
        npc.LORD_SUTCLIFFE,
        npc.LEONA,
    ],
    regions=[reg.SOLANA, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/super-slam/feudmasters.md",
    story_type="main-story",
    title="Feudmasters",
    heroes=["betsy"],
    npcs=[
        npc.BATBITER,
        npc.EMEVIERE,
        npc.FIGHTMASTER_RUSTY,
        npc.MOLOCA,
        npc.MORGA_GRINNING_BOAR_CANTINA_BARMAID,
        npc.SLAPSTICK_SAL,
        npc.SPEAKEASY,
        npc.FUGGER_GRIMES,
    ],
    locations=[
        loc.GRINNING_BOAR_CANTINA,
        loc.THE_MOAT,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    # TODO: group — Mythmakers (Speakeasy's guild)
    # TODO: group — Glorytown Gladiators (Speakeasy's guild)
    # TODO: group — Fury Fists (Speakeasy's guild)
    # TODO: group — Boulders (Speakeasy's guild)
    # TODO: group — Heavy Metals (affiliation ambiguous, see Ambiguous)
    # TODO: group — Wild Wonders (Speakeasy's guild)
    # TODO: group — Champions of Chivalry (Speakeasy's guild)
    # TODO: group — Big Boppers (Batbiter's guild)
    # TODO: group — Baleful Horde (Batbiter's guild)
    # TODO: group — Gorelords (Batbiter's guild)
    # TODO: group — Prowlers (Batbiter's guild)
    # TODO: group — Chanek Jungle Slayers (Batbiter's guild)
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/tales-of-aria/amongst-the-brambles.md",
    story_type="main-story",
    title="Amongst the Brambles",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/hero/briar/story/briar-story/",
    heroes=["briar"],
    npcs=[
        npc.DAVNIR,
        npc.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[loc.CANDLEHOLD, loc.THE_FLOW],
    regions=[reg.ARIA],
    fauna=[fauna.CESARI],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/tales-of-aria/the-broken-covenant.md",
    story_type="main-story",
    title="The Broken Covenant",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/oldhim-2/story/oldhim/",
    heroes=["oldhim"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/tales-of-aria/wonders-of-the-wayfarer.md",
    story_type="main-story",
    title="Wonders of the Wayfarer",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/lexi/story/lexi-story/",
    heroes=["lexi"],
    npcs=[
        npc.YVOR,
    ],
    # TODO: needs catalogue constant — Lake Frigid (loc)
    locations=[loc.ENION, loc.VOLTHAVEN, loc.THE_KORSHEM],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dynasty/ember-in-the-ash.md",
    story_type="main-story",
    title="Ember in the Ash",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    publication_date="2022-10-27",
    source_link="https://fabtcg.com/articles/ember-ash/",
    heroes=["dromai", "emperor", "fai"],
    npcs=[
        npc.GENERAL_RIKU,
        npc.LORD_MERCHANT_SAVAI,
        npc.LORD_WIZARD_CHIYO,
        # TODO: needs catalogue constant — Chancellor Yama (npc)
        # TODO: needs catalogue constant — Spymaster Xathari (npc)
    ],
    locations=[
        loc.ASHVAHAN,
        loc.DESHVAHAN,
        loc.RED_DESERT,
        loc.IMPERIAL_PALACE,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.THE_PITS,
        reg.VOLCOR,
    ],
    fauna=[fauna.VUURLIN],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dynasty/emperor-the-one-emperor.md",
    story_type="main-story",
    title="The One Emperor",
    source_link="https://fabtcg.com/hero/emperor/story/emperor-story/",
    heroes=["emperor", "yoji"],
    npcs=[
        # TODO: needs catalogue constant — Chancellor Yama (npc)
        # TODO: needs catalogue constant — Spymaster Xathari (npc)
    ],
    locations=[loc.MT_VOLCOR],
    regions=[reg.VOLCOR],
    fauna=[fauna.APOPHIS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dynasty/the-blood-stained-web.md",
    story_type="main-story",
    title="The Blood Stained Web",
    source_link="https://fabtcg.com/articles/story/the-bloodstained-web/",
    heroes=["emperor"],
    locations=[
        loc.IMPERIAL_PALACE,
        loc.THE_GOLDEN_ORCHARD_ESTATE,
    ],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dynasty/vow-of-vigilence.md",
    story_type="main-story",
    title="Vow of Vigilence",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/yoji/story/yoji-story/",
    heroes=["emperor", "yoji"],
    npcs=[
        # TODO: needs catalogue constant — Chancellor Yama (npc)
    ],
    locations=[
        loc.BLACKROCK_QUARRIES,
        loc.DRAGON_S_PEAK,
        loc.THE_OBSIDIAN_COAST,
        # TODO: needs catalogue constant — Tchankem Castle (location)
        # TODO: needs catalogue constant — Serpent's Crescent (location)
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dusk-till-dawn/anointed-in-shadow.md",
    story_type="main-story",
    title="Anointed in Shadow",
    authors="Edwin McRae, Rachel Rees",
    artists="Henrique Lindner",
    source_link="https://fabtcg.com/hero/vynnset/story/anointed-in-shadow/",
    heroes=["vynnset"],
    npcs=[
        npc.NASRETH,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_SAVAGE_LANDS],
    dry_run=True,
)
# TODO: group — Sisters of Octothesia (faction, no catalogue location match)

db.upsert_story(
    path="src/main-story/dusk-till-dawn/falling-in-darkness.md",
    story_type="main-story",
    title="Falling In Darkness",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/falling-in-darkness/",
    publication_date="2023-07-01",
    heroes=["boltyn", "bravo", "briar", "dorinthea", "levia", "lexi", "oldhim", "prism", "shiyana"],
    npcs=[
        npc.APOSTATE,
        npc.CAYLIN,
        npc.CAYLIN_S_MOTHER,
        npc.MINERVA_THEMIS,
        npc.THEBASTO_MAGISTER_OF_DEFENSE,
        npc.NASRETH,
        npc.BLASMOPHET,
    ],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.OCTOGRIA,
        loc.THE_GOLDEN_FIELDS,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.THE_SOLARIUM,
        loc.MORLOCK_HILL,
        loc.I_ARATHAEL,
    ],
    regions=[reg.ARIA, reg.DEMONASTERY, reg.SOLANA],
    weapons=["anothos"],
    dry_run=True,
)
# TODO: needs catalogue constant — Scholars Assembly (loc, region likely Solana)

db.upsert_story(
    path="src/main-story/dusk-till-dawn/prism-awakener-of-sol.md",
    story_type="main-story",
    title="Prism, Awakener of Sol",
    heroes=["boltyn", "dorinthea", "levia", "prism", "shiyana", "vynnset"],
    locations=[loc.DIMENXXIONAL_GATEWAY, loc.I_ARATHAEL],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dusk-till-dawn/unity-in-light.md",
    story_type="main-story",
    title="Unity In Light",
    authors="Edwin McRae, Rachel Rees",
    artists="Jessketchin",
    source_link="https://fabtcg.com/articles/unity-in-light/",
    publication_date="2023-06-30",
    heroes=[
        "boltyn",
        "bravo",
        "briar",
        "dorinthea",
        "lexi",
        "oldhim",
        "prism",
        "shiyana",
        "yorick",
    ],
    npcs=[
        npc.ONE_EYE,
    ],
    locations=[
        loc.THE_KORSHEM,
        loc.THE_FLOW,
        loc.FRACTAL_SCAR,
        loc.THE_MAELA,
        loc.THE_EVERFEST_CARNIVAL,
        loc.I_ARATHAEL,
        loc.LIBRARY_OF_ILLUMINATION,
    ],
    regions=[reg.ARIA, reg.DEMONASTERY, reg.SOLANA],
    weapons=["anothos"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/another-day-another-title.md",
    story_type="main-story",
    title="Another Day, Another Title",
    publication_date="2023-12-22",
    source_link="https://fabtcg.com/hero/olympia/story/olympia/",
    heroes=["olympia"],
    npcs=[
        npc.DEMETRIOS,
    ],
    locations=[
        loc.ARENA_BARRACKS,
        loc.BUTCHER_S_BIN,
        loc.CHAMPION_S_QUARTERS,
        loc.CHAMPIONS_REST,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/arena-announcements.md",
    story_type="main-story",
    title="Arena Announcements",
    heroes=["betsy", "kassai", "kayo", "oldhim", "rhinar", "victor-goldmane"],
    regions=[reg.SOLANA, reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/bloodied-sands.md",
    story_type="main-story",
    title="Bloodied Sands",
    publication_date="2024-08-16",
    source_link="https://fabtcg.com/articles/bloodied-sands/",
    heroes=["betsy", "kassai", "kayo", "olympia", "rhinar", "victor-goldmane"],
    npcs=[
        npc.ALIF,
        npc.AMIR,
        npc.FAYYAD,
        npc.FIGHTMASTER_KOX,
        npc.GENERAL_CHUL,
        npc.SADA,
    ],
    locations=[loc.THE_UNDERCROFT],
    regions=[reg.THE_SAVAGE_LANDS, reg.VOLCOR],
    weapons=["cintari-saber", "mandible-claw"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/deathmatch-wrecking-ball.md",
    story_type="main-story",
    title="Deathmatch Wrecking Ball",
    publication_date="2023-12-20",
    source_link="https://fabtcg.com/hero/betsy/story/46529-2/",
    heroes=["betsy"],
    npcs=[
        npc.EBBA,
        npc.HANK,
        npc.MARCUS_MAULER_MONROE,
    ],
    locations=[
        loc.FORWARD_CAMPS,
        loc.GRINNING_BOAR_CANTINA,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/the-golden-son.md",
    story_type="main-story",
    title="The Golden Son",
    source_link="https://fabtcg.com/hero/victor/story/victor/",
    heroes=["victor-goldmane"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/thirst-for-revenge.md",
    story_type="main-story",
    title="Thirst For Revenge",
    publication_date="2024-01-24",
    source_link="https://fabtcg.com/hero/kassai-3/story/thirst-for-revenge/",
    heroes=["kassai"],
    npcs=[
        npc.ALIF,
        npc.FAYYAD,
        npc.FIGHTMASTER_KOX,
        npc.SADA,
    ],
    weapons=["cintari-saber"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/untamed-and-unbroken.md",
    story_type="main-story",
    title="Untamed and Unbroken",
    publication_date="2023-12-27",
    source_link="https://fabtcg.com/hero/kayo-br/story/kayo-story/",
    heroes=["kayo"],
    npcs=[
        npc.DERVIN_MASTER_OF_BEASTS,
        npc.FIGHTMASTER_KOX,
        npc.YARIN,
    ],
    locations=[
        loc.THE_BADLANDS,
        loc.THE_UNDERCROFT,
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-1-the-tiger-in-the-mist.md",
    story_type="main-story",
    title="Part 1: The Tiger in the Mist",
    source_link="https://fabtcg.com/hero/zen-tamer-of-purpose/story/part-1-the-tiger-in-the-mist/",
    heroes=["nuu", "zen"],
    npcs=[
        npc.SATSUKI,
        npc.SETO_OF_MIHARU,
        npc.TOROJA_OF_ISHIGAKI,
    ],
    locations=[
        loc.MISTCLOAK_LAKE,
        loc.NASU_KA_TEAHOUSE,
        loc.IKARU,
        # Kept pending curator ruling: agent recommends DROPPING this — the page
        # only says "the maw of a yawning lizard", a common noun, not the place.
        loc.THE_MAW,
    ],
    regions=[reg.MISTERIA],
    fauna=[fauna.RACIKI, fauna.ROWBUG],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-2-the-tapestry-unfolds.md",
    story_type="main-story",
    title="Part 2: The Tapestry Unfolds",
    source_link="https://fabtcg.com/hero/zen-tamer-of-purpose/story/part-2-the-tapestry-unfolds/",
    heroes=["enigma"],
    npcs=[
        npc.KOUKI,
    ],
    locations=[loc.LUNAR_TEMPLE, loc.MISTCLOAK_LAKE, loc.MISTCLOAK_GULLY, loc.NASU_KA_TEAHOUSE],
    regions=[reg.MISTERIA],
    # TODO: needs catalogue constant — Gentua (fauna); also called "Imps" per src/faq.md
    # TODO: needs catalogue constant — Three-Legged Crow (fauna); see Ambiguous
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-3-the-serpents-strike.md",
    story_type="main-story",
    title="Part 3: The Serpent's Strike",
    source_link="https://fabtcg.com/hero/zen-tamer-of-purpose/story/part-3-the-serpents-strike/",
    heroes=["nuu", "zen"],
    npcs=[
        npc.BOJANI,
        npc.SATSUKI,
        npc.SETO_OF_MIHARU,
        npc.TOROJA_OF_ISHIGAKI,
    ],
    locations=[loc.NASU_KA_TEAHOUSE, loc.MISTCLOAK_GULLY],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-4-the-hare-and-the-snake.md",
    story_type="main-story",
    title="Part 4: The Hare and the Snake",
    heroes=["enigma", "nuu", "zen"],
    npcs=[
        npc.KOUKI,
    ],
    locations=[loc.LUNAR_TEMPLE, loc.MISTCLOAK_GULLY],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/birth-of-the-arknight.md",
    story_type="main-story",
    title="Birth of the Arknight",
    authors="Nicola Price",
    artists="MJ Fetesio",
    source_link="https://fabtcg.com/hero/viserai/story/viserai-story/",
    heroes=["viserai"],
    npcs=[npc.LORD_SUTCLIFFE],
    locations=[
        loc.DEMONASTERY,
        loc.ENTRANCE_HALL,
    ],
    regions=[reg.DEMONASTERY],
    # TODO: needs catalogue constant — Corva (npc), Whisper (npc), Mani (npc),
    # Scriptorium (location), Vidus (monster), Pallas (fauna). See the table below.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/from-the-ashes.md",
    story_type="main-story",
    title="From the Ashes",
    source_link="https://fabtcg.com/hero/kano/story/from-the-ashes/",
    heroes=["kano", "emperor"],
    npcs=[npc.LORD_WIZARD_CHIYO],
    locations=[
        loc.CHAMBER_OF_THE_DRAGON,
        loc.IMPERIAL_PALACE,
    ],
    regions=[reg.VOLCOR],
    fauna=[fauna.RYOKI, fauna.VUURLIN],
    weapons=["crucible-of-aetherweave"],
    # TODO: needs catalogue constant — Lord Wizard Akihiko (npc), Lord Chancellor Yama (npc),
    # Daijo (npc), the Empress (npc). See the table below.
    # TODO: group — the Alshoni faction, the Ezu faction
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/full-steam-ahead.md",
    story_type="main-story",
    title="Full Steam Ahead",
    source_link="https://fabtcg.com/hero/dash/story/full-steam-ahead/",
    heroes=["dash"],
    npcs=[
        npc.RICKY_ROYCE,
        npc.THIROUX,
    ],
    locations=[
        loc.COPPERTOWN,
        loc.EAST_RISE,
        loc.GIGADRILL_ELEVATOR,
        loc.MIDTOWN_MARKETS,
        loc.OLD_METRIX,
        loc.THE_NEEDLE,
        loc.ZINNIA_PARK,
        loc.LOWLAKE,
        loc.COGWERX_CONGLOMERATE,
        loc.TEKLO_INDUSTRIES,
        loc.CENTENNIAL_CONSUMABLES,
    ],
    regions=[reg.METRIX],
    weapons=["teklo-plasma-pistol"],
    # TODO: needs catalogue constant — The Sprawl (loc), The Expanse (loc), Pit 3 (loc),
    # Goode's (loc), Mo (npc). See the table below.
    # TODO: no equipment slug for the D.R.E.S.S. — flagged, not guessed.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/needle-in-a-haystack.md",
    story_type="main-story",
    title="Needle in a Haystack",
    source_link="https://fabtcg.com/hero/dash/story/needle-in-a-haystack/",
    heroes=["dash"],
    npcs=[npc.RICKY_ROYCE],
    locations=[
        loc.BEACON,
        loc.COPPERTOWN,
        loc.GIGADRILL_ELEVATOR,
        loc.MIDTOWN_MARKETS,
        loc.THE_REGISTRY,
        loc.ZESCA_S,
        loc.ZINNIA_PARK,
        loc.COGWERX_CONGLOMERATE,
        loc.TEKLO_INDUSTRIES,
        loc.CENTENNIAL_CONSUMABLES,
    ],
    regions=[reg.METRIX],
    # TODO: needs catalogue constant — The Sprawl (loc), Natalya's (loc), Beak (npc),
    # Mite (npc). See the table below.
    # TODO: group — Mendacity Media, referred to here by its former name "Voxx"
    # TODO: no equipment slug for the D.R.E.S.S. — flagged, not guessed.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/playing-with-fire.md",
    story_type="main-story",
    title="Playing with Fire",
    source_link="https://fabtcg.com/hero/kano/story/playing-with-fire/",
    heroes=["emperor", "kano"],
    locations=[
        loc.CHAMBER_OF_THE_DRAGON,
        loc.IMPERIAL_PALACE,
        loc.MT_VOLCOR,
    ],
    regions=[reg.VOLCOR],
    fauna=[fauna.APOPHIS, fauna.VUURLIN],
    # TODO: needs catalogue constant — Ryo (npc), Lord Wizard Akihiko (npc),
    # Lord Chancellor Yama (npc). See the table below.
    # TODO: group — the Hideshi
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/return-of-the-shadow.md",
    story_type="main-story",
    title="Return of the Shadow",
    artists="Nikolay Moskvin",
    publication_date="2020-08-12",
    source_link="https://fabtcg.com/articles/return-shadow/",
    heroes=["viserai"],
    locations=[
        loc.DEMONASTERY,
        loc.ENTRANCE_HALL,
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY],
    weapons=["nebula-blade"],
    # TODO: needs catalogue constant — Whisper (npc). Requested from
    # birth-of-the-arknight.md; one addition serves both pages.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/smoke-and-mirrors.md",
    story_type="main-story",
    title="Smoke and Mirrors",
    source_link="https://fabtcg.com/hero/kano/story/smoke-and-mirrors/",
    heroes=["kano"],
    npcs=[npc.LORD_WIZARD_CHIYO],
    locations=[
        loc.CHAMBER_OF_THE_DRAGON,
        loc.IMPERIAL_PALACE,
        loc.MT_VOLCOR,
    ],
    regions=[reg.VOLCOR],
    # TODO: needs catalogue constant — Lord Wizard Akihiko (npc), Minako (npc).
    # Akihiko is also requested from playing-with-fire.md and from-the-ashes.md.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/stroke-of-genius.md",
    story_type="main-story",
    title="Stroke of Genius",
    source_link="https://fabtcg.com/hero/dash/story/stroke-of-genius/",
    heroes=["dash"],
    npcs=[
        npc.DR_WYVERSTONE,
        npc.THIROUX,
    ],
    locations=[
        loc.CENTENNIAL_CONSUMABLES,
        loc.COGWERX_CONGLOMERATE,
        loc.GIGADRILL_ELEVATOR,
        loc.MIDTOWN_MARKETS,
        loc.TEKLO_INDUSTRIES,
        loc.THE_NEEDLE,
        loc.WEST_RISE,
    ],
    regions=[reg.METRIX],
    # TODO: needs catalogue constant — Clara (npc). See the table below.
    # TODO: group — the Iron Council (see the near-duplicate note in Ambiguous)
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/destroy-and-consume.md",
    story_type="main-story",
    title="Destroy and Consume",
    authors="Nicola Price, Tarryn Thomas",
    artists="Iain Miki",
    source_link="https://fabtcg.com/hero/levia/story/levia-story-destroy-and-consume/",
    heroes=["levia"],
    npcs=[
        npc.LADY_BARTHIMONT,
        npc.LORD_SUTCLIFFE,
    ],
    locations=[
        loc.BARTHIMONT_MANOR,
        loc.BLASMOPHET_S_DOMAIN,
        loc.COURTYARD,
        loc.DEATH_S_KNELL,
        loc.THE_NORTHERN_REALMS,
        loc.THE_VENARIUM,
    ],
    regions=[reg.SOLANA],
    # TODO: needs catalogue constant — Lord Barthimont (npc). See the table below.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/emissary-of-the-void.md",
    story_type="main-story",
    title="Emissary of the Void",
    authors="Nicola Price, Tarryn Thomas",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/hero/chane/story/chane-story/",
    heroes=["chane"],
    npcs=[npc.URSUR],
    locations=[
        loc.DEMONASTERY,
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    # TODO: needs catalogue constant — Scriptorium (loc). Also requested from
    # birth-of-the-arknight.md; one addition serves both pages.
    # TODO: group — the Disciples of Pain
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/stories-of-illumination.md",
    story_type="main-story",
    title="Stories of Illumination",
    authors="Nicola Price, Tarryn Thomas",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/prism-soa/story/prism-story-stories-of-illumination/",
    heroes=["prism"],
    npcs=[
        npc.AEGIS_THE_SHIELD_OF_LIGHT,
        npc.AVALON_MESSENGER_OF_THE_DAWN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.METIS_ARCHANGEL_OF_TENACITY,
        npc.SEKEM_ARCHANGEL_OF_RAVAGES,
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        npc.THEMIS_KEEPER_OF_THE_SCALES,
        npc.VICTORIA_ARCHANGEL_OF_TRIUMPH,
    ],
    locations=[
        loc.LIBRARY_OF_ILLUMINATION,
        loc.SILVARIUM,
        loc.THE_GOLDEN_FIELDS,
    ],
    regions=[reg.SOLANA],
    # TODO: needs catalogue constant — Signarus (loc). See the table below.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/sworn-to-protect.md",
    story_type="main-story",
    title="Sworn to Protect",
    authors="Nicola Price, Tarryn Thomas",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/hero/boltyn-3/story/ser-story/",
    heroes=["boltyn"],
    npcs=[
        npc.AIOS,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.EIRINA,
        npc.MINERVA_THEMIS,
    ],
    locations=[
        loc.GOLDEN_CHARIOT,
        loc.HAND_OF_SOL,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_NORTHERN_REALMS,
        loc.THE_SOLARIUM,
    ],
    regions=[reg.SOLANA],
    # TODO: group — the Gemini
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/step-into-the-light.md",
    story_type="main-story",
    title="Step Into The Light",
    authors="Nicola Price, Tarryn Thomas",
    artists="Sam Yang",
    publication_date="2021-04-20",
    source_link="https://fabtcg.com/articles/step-into-light/",
    heroes=["boltyn", "prism"],
    npcs=[
        npc.AIOS,
        npc.APOSTATE,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        npc.THE_LIBRARIAN,
    ],
    locations=[
        loc.AMPHITHEATRE,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_NORTHERN_REALMS,
        loc.THE_SOLARIUM,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    # TODO: needs catalogue constant — Leander (npc), Viator (npc). See the table below.
    # TODO: group — the Glory of Sol
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/harbinger-of-the-abyss.md",
    story_type="main-story",
    title="Harbinger of the Abyss",
    authors="Nicola Price, Tarryn Thomas",
    artists="Nikolay Moskvin",
    publication_date="2021-04-15",
    source_link="https://fabtcg.com/articles/harbinger-abyss/",
    heroes=["chane", "levia"],
    npcs=[
        npc.BLASMOPHET,
        npc.LADY_BARTHIMONT,
        npc.LORD_SUTCLIFFE,
    ],
    locations=[
        loc.BARTHIMONT_MANOR,
        loc.BLASMOPHET_S_DOMAIN,
        loc.COURTYARD,
        loc.DEATH_S_KNELL,
        loc.DEMONASTERY,
        loc.ENTRANCE_HALL,
        loc.THE_VENARIUM,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    # TODO: needs catalogue constant — Graves (npc), Devoratum (mon), Blasphema (loc).
    # See the table below.
    dry_run=True,
)
