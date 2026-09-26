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
    characters as people,
    fauna,
    flora,
    food_drink as food,
    groups as grp,
    locations as loc,
    monsters as mon,
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
    characters=[
        "ira",
        people.JING,
        people.XILIN,
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
    characters=[
        "bravo",
        people.MAGNUS_THE_VIGILANT,
        people.GAWAIN,
        people.MORGAN,
        people.MARBLES,
        people.MIKAEL,
    ],
    locations=[
        loc.THE_FLOW,
        loc.THE_EVERFEST_CARNIVAL,
        loc.LEGENDARIUM,
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
    groups=[grp.THE_MAELA, grp.THE_VALDUR],
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
    characters=[
        "dorinthea",
        "hala",
        people.MINERVA_THEMIS,
        # TODO: Does fragment link to world lore? If so, how?
        people.GRAND_MAGISTER_THE_STEADFAST,
        people.SOL,
        people.VALERIA,
        people.FELIX,
        people.CHARIS,
        people.FARRIS,
        people.VITUS,
        people.PALLAS,
        people.DARIUS,
        people.MARCUS,
    ],
    locations=[
        loc.GOLDEN_CHARIOT,
        loc.IRONSONG_FORGE,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.AMPHITHEATRE,
        loc.SOLSTICE_OF_LAURELS,
        loc.THE_AWAKENING_CEREMONY,
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
    groups=[grp.HAND_OF_SOL, grp.THE_LIGHT_OF_SOL],
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
    characters=[
        "rhinar",
    ],
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
    characters=[
        "katsu",
        people.MASTER_TAKUMI,
        people.MASTER_SAORI,
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
    groups=[grp.AUIS_SCALES],
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
    characters=[
        "azalea",
        people.JACKDAW,
    ],
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
    characters=[
        "azalea",
        people.MORAY,
        people.GREENBIRD,
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
    characters=[
        "azalea",
        people.LENA_BELLE,
        people.GREENBIRD,  # TODO: fragment to the tavern?
        people.BARTON,
        people.THE_HARVESTER,
        people.HOG,
        people.MORAY,
        people.JACKDAW,
        people.COBBS,
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
    groups=[grp.ARMS_DEALERS],
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
    characters=["oscilio", "zyggy", "aurora"],
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
    characters=[
        "zyggy",
        "oscilio",
        people.WENDRYN,
        people.ASTREA_QUAZOR,
        people.AURIC_SEERESS,
        people.WYNVARIN,
        people.YVOR,
        people.DAVNIR,
        people.GALCIA,
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
    characters=[
        "baalghor",
        "chane",
        "vynnset",
        people.KIEN,
        people.URSUR,
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
    groups=[grp.DISCIPLES_OF_PAIN, grp.CHURCH_OF_PAIN],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/usurp-the-shadow-throne/agony-in-light.md",
    story_type="main-story",
    title="Agony in Light",
    authors="Corey J. White, Rachel Rees, Aidan Kwasneski, Kasharn Rao, Edwin McRae",
    artists="Olga Tereshenko, Dominik Mayer, Simon Dominic, Isuardi Therianto",
    source_link="https://fabtcg.com/articles/agony-in-light/",
    publication_date="2026-07-31",
    characters=[
        "vynnset",
        "boltyn",
        "dorinthea",
        "levia",
        people.NASRETH,
        people.BLASMOPHET,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.EIRINA,
        people.SOL,
    ],
    locations=[
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.SOLANA,
        reg.DEMONASTERY,
    ],
    weapons=["flail-of-agony", "raydn-duskbane"],
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/crucible-of-war/no-smoke-without-fire.md",
    story_type="main-story",
    title="No Smoke Without Fire",
    artists="Nikolay Moskvin, Bramasta Aji",
    publication_date="2020-08-14",
    source_link="https://fabtcg.com/articles/no-smoke-without-fire/",
    characters=[
        "dorinthea",
        "kassai",
        people.TAKA,
    ],
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
    characters=[
        "viserai",
        people.LORD_SUTCLIFFE,
        people.LEONA,
    ],
    regions=[reg.SOLANA, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/super-slam/feudmasters.md",
    story_type="main-story",
    title="Feudmasters",
    characters=[
        "betsy",
        people.BATBITER,
        people.EMEVIERE,
        people.FIGHTMASTER_RUSTY,
        people.MOLOCA,
        people.MORGA_GRINNING_BOAR_CANTINA_BARMAID,
        people.SLAPSTICK_SAL,
        people.SPEAKEASY,
        people.FUGGER_GRIMES,
    ],
    locations=[
        loc.GRINNING_BOAR_CANTINA,
        loc.THE_MOAT,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    groups=[
        # The three stables and the federation they sit in. Speakeasy's and
        # Batbiter's are reachable anyway, as the parent of every guild below, but
        # Moloca's has no guild to be reached through — she fronts none — so
        # without this line her row would exist in the catalogue and never be
        # written. Naming all four here is also the honest mention-link: this page
        # is where the panel introduces every one of them.
        grp.SUPER_SLAM_GUILDS,
        grp.SPEAKEASYS_GUILDS,
        grp.BATBITERS_GUILDS,
        grp.MOLOCAS_GUILDS,
        grp.BALEFUL_HORDE,
        grp.BIG_BOPPERS,
        grp.BOULDERS,
        grp.CHAMPIONS_OF_CHIVALRY,
        grp.FURY_FISTS,
        grp.GLORYTOWN_GLADIATORS,
        grp.GORELORDS,
        grp.HEAVY_METALS,
        grp.JUNGLE_SLAYERS,
        grp.MYTHMAKERS,
        grp.PROWLERS,
        grp.WILD_WONDERS,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/tales-of-aria/amongst-the-brambles.md",
    story_type="main-story",
    title="Amongst the Brambles",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/hero/briar/story/briar-story/",
    characters=[
        "briar",
        people.DAVNIR,
        people.QUEEN_OF_CANDLEHOLD,
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
    characters=["oldhim"],
    groups=[grp.SEERS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/tales-of-aria/wonders-of-the-wayfarer.md",
    story_type="main-story",
    title="Wonders of the Wayfarer",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/lexi/story/lexi-story/",
    characters=[
        "lexi",
        people.YVOR,
    ],
    # TODO: needs catalogue constant — Lake Frigid (loc)
    locations=[loc.ENION, loc.VOLTHAVEN, loc.THE_KORSHEM],
    regions=[reg.ARIA],
    groups=[grp.WAYFARERS],
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
    characters=[
        "dromai",
        "emperor",
        "fai",
        people.GENERAL_RIKU,
        people.LORD_MERCHANT_SAVAI,
        people.LORD_WIZARD_CHIYO,
        # "Sandfolk fury continues to fester, as Xathari hoped it would" (:59).
        # The TODO here waited for a constant stage 5 created and did not clear.
        people.XATHARI,
        # TODO: needs catalogue constant — Chancellor Yama (npc)
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
    characters=[
        "emperor",
        "yoji",
        people.XATHARI,
        # TODO: needs catalogue constant — Chancellor Yama (npc)
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
    characters=["emperor"],
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
    characters=[
        "emperor",
        "yoji",
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
    characters=[
        "vynnset",
        people.NASRETH,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_SAVAGE_LANDS],
    groups=[grp.SISTERS_OF_OCTOTHESIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/dusk-till-dawn/falling-in-darkness.md",
    story_type="main-story",
    title="Falling In Darkness",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/falling-in-darkness/",
    publication_date="2023-07-01",
    characters=[
        "boltyn",
        "bravo",
        "briar",
        "dorinthea",
        "levia",
        "lexi",
        "oldhim",
        "prism",
        "shiyana",
        people.APOSTATE,
        people.CAYLIN,
        people.CAYLIN_S_MOTHER,
        people.MINERVA_THEMIS,
        people.THEBASTO_MAGISTER_OF_DEFENSE,
        people.NASRETH,
        people.BLASMOPHET,
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
    characters=["boltyn", "dorinthea", "levia", "prism", "shiyana", "vynnset"],
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
    characters=[
        "boltyn",
        "bravo",
        "briar",
        "dorinthea",
        "lexi",
        "oldhim",
        "prism",
        "shiyana",
        "yorick",
        people.ONE_EYE,
    ],
    locations=[
        loc.THE_KORSHEM,
        loc.THE_FLOW,
        loc.FRACTAL_SCAR,
        loc.THE_EVERFEST_CARNIVAL,
        loc.I_ARATHAEL,
        loc.LIBRARY_OF_ILLUMINATION,
    ],
    regions=[reg.ARIA, reg.DEMONASTERY, reg.SOLANA],
    weapons=["anothos"],
    groups=[grp.THE_MAELA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/another-day-another-title.md",
    story_type="main-story",
    title="Another Day, Another Title",
    publication_date="2023-12-22",
    source_link="https://fabtcg.com/hero/olympia/story/olympia/",
    characters=[
        "olympia",
        people.DEMETRIOS,
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
    characters=["betsy", "kassai", "kayo", "oldhim", "rhinar", "victor-goldmane"],
    regions=[reg.SOLANA, reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/bloodied-sands.md",
    story_type="main-story",
    title="Bloodied Sands",
    publication_date="2024-08-16",
    source_link="https://fabtcg.com/articles/bloodied-sands/",
    characters=[
        "betsy",
        "kassai",
        "kayo",
        "olympia",
        "rhinar",
        "victor-goldmane",
        people.ALIF,
        people.AMIR,
        people.FAYYAD,
        people.FIGHTMASTER_KOX,
        people.GENERAL_CHUL,
        people.SADA,
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
    characters=[
        "betsy",
        people.EBBA,
        people.HANK,
        people.MARCUS_MAULER_MONROE,
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
    characters=["victor-goldmane"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/heavy-hitters/thirst-for-revenge.md",
    story_type="main-story",
    title="Thirst For Revenge",
    publication_date="2024-01-24",
    source_link="https://fabtcg.com/hero/kassai-3/story/thirst-for-revenge/",
    characters=[
        "kassai",
        people.ALIF,
        people.FAYYAD,
        people.FIGHTMASTER_KOX,
        people.SADA,
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
    characters=[
        "kayo",
        people.DERVIN_MASTER_OF_BEASTS,
        people.FIGHTMASTER_KOX,
        people.YARIN,
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
    characters=[
        "nuu",
        "zen",
        people.SATSUKI,
        people.SETO_OF_MIHARU,
        people.TOROJA_OF_ISHIGAKI,
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
    characters=[
        "enigma",
        people.KOUKI,
    ],
    locations=[loc.LUNAR_TEMPLE, loc.MISTCLOAK_LAKE, loc.MISTCLOAK_GULLY, loc.NASU_KA_TEAHOUSE],
    regions=[reg.MISTERIA],
    monsters=[mon.GENTUA],  # new; not yet applied — this page's dry_run stays True
    # TODO: needs catalogue constant — Three-Legged Crow (fauna); see Ambiguous
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-3-the-serpents-strike.md",
    story_type="main-story",
    title="Part 3: The Serpent's Strike",
    source_link="https://fabtcg.com/hero/zen-tamer-of-purpose/story/part-3-the-serpents-strike/",
    characters=[
        "nuu",
        "zen",
        people.BOJANI,
        people.SATSUKI,
        people.SETO_OF_MIHARU,
        people.TOROJA_OF_ISHIGAKI,
    ],
    locations=[loc.NASU_KA_TEAHOUSE, loc.MISTCLOAK_GULLY],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/part-the-mistveil/part-4-the-hare-and-the-snake.md",
    story_type="main-story",
    title="Part 4: The Hare and the Snake",
    characters=[
        "enigma",
        "nuu",
        "zen",
        people.KOUKI,
        people.FUMEI,
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
    characters=[
        "viserai",
        people.LORD_SUTCLIFFE,
        people.WHISPER,  # new; not yet applied — this page's dry_run stays True
    ],
    locations=[
        loc.ENTRANCE_HALL,
    ],
    regions=[reg.DEMONASTERY],
    # TODO: needs catalogue constant — Corva (npc), Mani (npc),
    # Scriptorium (location), Vidus (monster), Pallas (fauna). See the table below.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/from-the-ashes.md",
    story_type="main-story",
    title="From the Ashes",
    source_link="https://fabtcg.com/hero/kano/story/from-the-ashes/",
    characters=[
        "kano",
        "emperor",
        people.LORD_WIZARD_CHIYO,
    ],
    locations=[
        loc.CHAMBER_OF_THE_DRAGON,
        loc.IMPERIAL_PALACE,
    ],
    regions=[reg.VOLCOR],
    fauna=[fauna.RYOKI, fauna.VUURLIN],
    weapons=["crucible-of-aetherweave"],
    # TODO: needs catalogue constant — Lord Wizard Akihiko (npc), Lord Chancellor Yama (npc),
    # Daijo (npc), the Empress (npc). See the table below.
    groups=[grp.ALSHONI, grp.EZU],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/full-steam-ahead.md",
    story_type="main-story",
    title="Full Steam Ahead",
    source_link="https://fabtcg.com/hero/dash/story/full-steam-ahead/",
    characters=[
        "dash",
        people.RICKY_ROYCE,
        people.THIROUX,
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
    characters=[
        "dash",
        people.RICKY_ROYCE,
    ],
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
    # TODO: no equipment slug for the D.R.E.S.S. — flagged, not guessed.
    groups=[grp.MENDACITY_MEDIA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/playing-with-fire.md",
    story_type="main-story",
    title="Playing with Fire",
    source_link="https://fabtcg.com/hero/kano/story/playing-with-fire/",
    characters=["emperor", "kano"],
    locations=[
        loc.CHAMBER_OF_THE_DRAGON,
        loc.IMPERIAL_PALACE,
        loc.MT_VOLCOR,
    ],
    regions=[reg.VOLCOR],
    fauna=[fauna.APOPHIS, fauna.VUURLIN],
    # TODO: needs catalogue constant — Ryo (npc), Lord Wizard Akihiko (npc),
    # Lord Chancellor Yama (npc). See the table below.
    groups=[grp.HIDESHI],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/return-of-the-shadow.md",
    story_type="main-story",
    title="Return of the Shadow",
    artists="Nikolay Moskvin",
    publication_date="2020-08-12",
    source_link="https://fabtcg.com/articles/return-shadow/",
    characters=[
        "viserai",
        people.WHISPER,  # new; not yet applied — this page's dry_run stays True
    ],
    locations=[
        loc.ENTRANCE_HALL,
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY],
    weapons=["nebula-blade"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/arcane-rising/smoke-and-mirrors.md",
    story_type="main-story",
    title="Smoke and Mirrors",
    source_link="https://fabtcg.com/hero/kano/story/smoke-and-mirrors/",
    characters=[
        "kano",
        people.LORD_WIZARD_CHIYO,
    ],
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
    characters=[
        "dash",
        people.DR_WYVERSTONE,
        people.THIROUX,
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
    groups=[grp.IRON_ASSEMBLY, grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/destroy-and-consume.md",
    story_type="main-story",
    title="Destroy and Consume",
    authors="Nicola Price, Tarryn Thomas",
    artists="Iain Miki",
    source_link="https://fabtcg.com/hero/levia/story/levia-story-destroy-and-consume/",
    characters=[
        "levia",
        people.LADY_BARTHIMONT,
        people.LORD_SUTCLIFFE,
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
    characters=[
        "chane",
        people.URSUR,
    ],
    locations=[
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    # TODO: needs catalogue constant — Scriptorium (loc). Also requested from
    # birth-of-the-arknight.md; one addition serves both pages.
    groups=[grp.DISCIPLES_OF_PAIN],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/monarch/stories-of-illumination.md",
    story_type="main-story",
    title="Stories of Illumination",
    authors="Nicola Price, Tarryn Thomas",
    artists="Sam Yang",
    source_link="https://fabtcg.com/hero/prism-soa/story/prism-story-stories-of-illumination/",
    characters=[
        "prism",
        people.AEGIS_THE_SHIELD_OF_LIGHT,
        people.AVALON_MESSENGER_OF_THE_DAWN,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.METIS_ARCHANGEL_OF_TENACITY,
        people.SEKEM_ARCHANGEL_OF_RAVAGES,
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        people.THEMIS_KEEPER_OF_THE_SCALES,
        people.VICTORIA_ARCHANGEL_OF_TRIUMPH,
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
    characters=[
        "boltyn",
        people.AIOS,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.EIRINA,
        people.MINERVA_THEMIS,
    ],
    locations=[
        loc.GOLDEN_CHARIOT,
        loc.LIBRARY_OF_ILLUMINATION,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_NORTHERN_REALMS,
        loc.THE_SOLARIUM,
    ],
    regions=[reg.SOLANA],
    groups=[grp.GEMINI, grp.HAND_OF_SOL],
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
    characters=[
        "boltyn",
        "prism",
        people.AIOS,
        people.APOSTATE,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        people.THE_LIBRARIAN,
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
    # X01: the guard is gone. people.THE_LIBRARIAN now carries hero_slug="the-librarian",
    # so this link is allowed — the hero and the ordinary character are one character row, not two.
    # Held at dry_run=True regardless: the pending Leander/Viator catalogue
    # constants above are the reason this declaration isn't applied yet.
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
    characters=[
        "chane",
        "levia",
        people.BLASMOPHET,
        people.LADY_BARTHIMONT,
        people.LORD_SUTCLIFFE,
    ],
    locations=[
        loc.BARTHIMONT_MANOR,
        loc.BLASMOPHET_S_DOMAIN,
        loc.COURTYARD,
        loc.DEATH_S_KNELL,
        loc.ENTRANCE_HALL,
        loc.THE_VENARIUM,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    # TODO: needs catalogue constant — Graves (npc), Devoratum (mon), Blasphema (loc).
    # See the table below.
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/high-seas/captain-bones-and-the-city-of-gold.md",
    story_type="main-story",
    title="Captain Bones and the City of Gold",
    authors="Robbie Wen, Edwin McRae, Rachel Rees, Alan Baxter",
    source_link="https://fabtcg.com/articles/captain-bones-and-the-city-of-gold/",
    publication_date="2025-06-02",
    characters=[
        "gravy",
        people.CHOWDER,
        people.CHUM,
        people.CUTTY,
        # The story calls her the "Hightarn" shaman and never names her, so this row
        # may be her people rather than her name. It predates this registration and
        # is linked to no other story; reopened with the kind values in stage 4.
        people.HIGHTARN,
        people.KELPIE,
        people.LIMPIT,
        people.MORAY_LE_FAY,
        people.NAILBIT_NARI,
        people.RIGGERMORTIS,
        people.SCOOBA,
        people.SHELLY,
        people.SWABBIE,
        people.WAILER,
    ],
    locations=[
        # "Dreadfall's decaying edifices" and "explorations of Dreadfall" are this
        # place under a shortened name, not a second one. high-seas.md has a single
        # "Dreadfall Reach" heading.
        loc.DREADFALL_REACH,
        loc.GOLDEN_PORT,
        loc.GRAYHOLLOW,
        loc.GRAYSTONE,
        loc.GRAYSTONE_PENITENTIARY,
        loc.PIRATE_S_PERCH,
        loc.PORT_CONNIVER,
        loc.TERAMUNDR_S_TRIANGLE,
        loc.TROPAL_DHANI,
    ],
    regions=[reg.HIGH_SEAS],
    fauna=[fauna.CHIRPWHISK, fauna.HYDRA, fauna.KRAKEN],
    food_drink=[food.SEPULCHRE_RUM],
    # The story calls it only "an eldritch compass"; the card is unmistakably the
    # same object, and the link is the user's call, recorded 2026-08-20.
    equipment=["compass-of-sunken-depths"],
    groups=[grp.KURAGHAN, grp.THE_DHANI_EMPIRE],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/armory-deck-maxx/boom-town-boom.md",
    story_type="main-story",
    title="Boom Town Boom",
    source_link="https://fabtcg.com/articles/boom-town-boom/",
    publication_date="2025-04-17",
    characters=[
        "dash",
        "data-doll-mkii",
        "maxx",
        people.AUDACITY,
        people.FERAL,
        people.JUICE,
        people.REZ,
        people.SYNTHEA_TEKLO,
        people.THIROUX,
    ],
    locations=[
        loc.COPPERTOWN,
        loc.EAST_RISE,
        loc.EAST_RISE_POWER_STATION,
        loc.PIT_2,
        # Teklo Industries and The Foundry are each a group *and* a place, so both
        # keep a locations row and are linked from both sides.
        loc.TEKLO_INDUSTRIES,
        loc.THE_FOUNDRY,
        loc.VOSSEN_THEATER,
    ],
    regions=[reg.METRIX, reg.THE_PITS],
    weapons=["banksy"],
    groups=[
        grp.COGWERX,
        grp.MENDACITY_MEDIA,
        grp.REGISTRY,
        grp.STEELSTREET_ENFORCERS,
        grp.TEKLO_INDUSTRIES,
        grp.THE_FOUNDRY,
    ],
    dry_run=True,
)

# Registered 2026-08-21, stage 5. This is the only page that attests Isen — a
# wayfarer says "I've heard legends of the Ancients, Yvor, Davnir, Isen..." (:197) —
# and giving him a row is why it had to be registered. He was one of the fourteen
# names in character-groups.md with no row of any kind.
#
# people.MAELA_ISULFV is linked from this page's "Isulvf", a letter-transposition of
# the same seer. See that constant: registering the page without noticing would have
# minted a second row for one person.
#
# Deliberately left out, none with a row anywhere and none describable from this
# page: `Strale`, `the Indigo Eye`, `the Covenant`, and the `Showstopper` of the
# Everfest poster. `Braumeister` is a profession and already waits for R9.
db.upsert_story(
    path="src/main-story/everfest/a-grand-adventure.md",
    story_type="main-story",
    title="A Grand Adventure",
    # All four were already on the story row. Story metadata is replace-semantic,
    # so omitting any of them is a deletion, not a silence.
    authors="Kasharn Rao",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/grand-adventure/",
    publication_date="2021-12-25",
    characters=[
        "briar",
        "lexi",
        "oldhim",
        "yorick",
        # Named in Briar's line about the Ancients, not present in the story.
        people.DAVNIR,
        people.ISEN,
        people.MAELA_ISULFV,
        people.MARA,
        people.QUEEN_OF_CANDLEHOLD,
        people.THAWNE,
        # Also the statue at :47, "the mythical Ancient of Thunder and Ice".
        people.YVOR,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ENION,
        loc.ISENLOFT,
        loc.THE_EVERFEST_CARNIVAL,
        loc.THE_KORSHEM,
        loc.VOLTHAVEN,
        loc.YVOR_S_PEAK,
    ],
    regions=[reg.ARIA],
    groups=[
        # "The Rosetta...The Ollin..." and the queen's "the Seers...of old"; Lexi is
        # a Wayfarer and the page calls her one repeatedly.
        grp.OLLIN,
        grp.ROSETTA,
        grp.SEERS,
        grp.WAYFARERS,
    ],
    weapons=["rosetta-thorn", "voltaire-strike-twice"],
    dry_run=True,
)

# Registered 2026-08-21, stage 5. Not needed for the dragons in the end —
# flavour/uprising.md had already given all twelve a row by the time this was
# reached — but registered as planned, and it turned out to carry four people who
# had no row at all. people.XATHARI is the one that matters: the Dracai spymaster is
# named on five pages and had never been recorded.
#
# The opening paragraphs before the "# Dragons of Empire" heading are Dromai's
# hero blurb rather than the story, and the entities in them are treated the same
# as the story's own — Torvai, Sani and Min are named nowhere else on the page.
db.upsert_story(
    path="src/main-story/uprising/dragons-of-empire.md",
    story_type="main-story",
    title="Dragons of Empire",
    # Already on the story row; omitting it would clear it.
    source_link="https://fabtcg.com/hero/dromai/story/dromai-story-dragons-of-empire/",
    # The Emperor never appears — Dromai recalls "the Emperor's rare appearance that
    # day, ten years ago" and waits on "the Emperor's thanks". A hero row exists
    # under the slug `emperor`, so the mention links there rather than minting an
    # ordinary-character spelling of the same person.
    characters=[
        "dromai",
        "emperor",
        people.FAI,
        # The four dragons Dromai invokes. Vynserakai, Azvolai and Nekria are all
        # destroyed at the siege; Tomeltai carries the second half of the story.
        people.AZVOLAI,
        people.GENERAL_RIKU,
        people.MIN_OF_THE_FOREST_OF_FLAMES,
        people.NEKRIA,
        people.SANI,
        people.SILVERHAIR,
        people.TOMELTAI,
        people.TORVAI,
        people.VYNSERAKAI,
        people.XATHARI,
    ],
    locations=[
        loc.ASHVAHAN,
        loc.FOREST_OF_FLAMES,
        loc.MT_VOLCOR,
        loc.THE_GOLDEN_ORCHARD_ESTATE,
    ],
    regions=[reg.VOLCOR],
    groups=[
        grp.DRACAI,
        grp.SANDFOLK,
        # :67 — "she pores over the tomes of The Twelve Dragons". The only line in
        # the repository that names the twelve as one thing (the user's call,
        # 2026-08-21); the roster is cited to flavour/uprising.md, which is where
        # all twelve are attested. See catalogue/groups.py.
        grp.THE_TWELVE_DRAGONS,
        grp.VOLCAI,
    ],
    dry_run=True,
)

# Registered 2026-08-21, stage 5. Not on the stage's own list — reached because
# registering dragons-of-empire.md would have dropped `The Oasis`, whose only story
# link sat on that page and whose text never names it. This is the page that does:
# "Dromai sits in the Oasis, her feet dangling in the cave's simmering lake." The
# link moves to the page that earns it rather than being deleted or asserted falsely.
#
# `The Royal Court` is deliberately not linked. It has a heading of its own on
# world-of-rathe/volcor.md and IMPERIAL_PALACE already carries `the-royal-court` as
# its fragment, so the institution is currently modelled as the building. "The Royal
# Court gave her the mantle of Dracai" is the institution acting, not the place, and
# the two are worth separating properly rather than by a link made in passing.
db.upsert_story(
    path="src/main-story/uprising/betrayal.md",
    story_type="main-story",
    title="Betrayal",
    source_link="https://fabtcg.com/hero/dromai/story/dromai-story-betrayal/",
    # None of the three were linked before, though the story is Dromai's throughout.
    characters=[
        "dromai",
        "emperor",
        "fai",
        people.EUN,
        people.GENERAL_RIKU,
        people.MIN_OF_THE_FOREST_OF_FLAMES,
        # Killed here, off the page: Dromai is working out how to profit from his
        # death. The row was minted for dragons-of-empire.md a moment earlier.
        people.XATHARI,
    ],
    locations=[
        loc.ASHVAHAN,
        # "Fai of the Forest of Flames, Slayer of Dracai."
        loc.FOREST_OF_FLAMES,
        loc.MT_VOLCOR,
        loc.THE_OASIS,
    ],
    regions=[
        # "The water comes from Misteria. The lava comes from Mount Volcor."
        reg.MISTERIA,
        reg.VOLCOR,
    ],
    groups=[
        grp.DRACAI,
        grp.VOLCAI,
    ],
    fauna=[
        fauna.FLAREFISH,
        fauna.LUMINOUS_CARP,
    ],
    dry_run=True,
)

# Registered 2026-08-21. Found by the review of 8f8b7e1c rather than by a page
# sweep: people.XATHARI's docstring enumerated the five pages naming him and left this
# one out, though it names him eight times, gives him dialogue, and is the page he
# dies on. Registering it is what made his status answerable.
#
# narrated_videos is omitted, not emptied. The story row carries St_Havock's
# reading and None leaves it alone where [] would delete it (db/_domain.py:714).
#
# Two things on this page are deliberately not linked, both the user's call:
#
#   the Phoenix     :9 "The many feathers of the Phoenix were burning bright" and
#                   :69 "It is time for the Phoenix to rise". A symbol, not a body
#                   — world-of-rathe/volcor.md:85 says so outright, "The phoenix is
#                   their symbol and their accepted fate", over a rebellion the
#                   same paragraph calls "fractured, united only by suffering".
#                   The other two attestations are both "banner". grp.VOLCAI
#                   already carries the rebellion. See the plan.
#   the great       :51, unnamed here. One of the twelve, but the page never says
#   purple dragon   which, and the roster is cited to flavour/uprising.md.
db.upsert_story(
    path="src/main-story/uprising/the-phoenix-and-the-dragon.md",
    story_type="main-story",
    title="The Phoenix and the Dragon",
    # Already on the story row; omitting it would clear it.
    source_link="https://fabtcg.com/hero/fai/story/fai-story-the-phoenix-and-the-dragon/",
    # Fai is the POV throughout and Dromai is on the page. The Emperor never
    # appears — :65, "The Emperor is blind. His dragons are turning against him."
    characters=[
        "dromai",
        "emperor",
        "fai",
        # Eaten by Dromai's dragon at :51. Her row already read Deceased.
        people.EUN,
        # Named but absent: :25, :27, :35, :61.
        people.MIN_OF_THE_FOREST_OF_FLAMES,
        # Dromai's parents, both named by Eun's confession at :39-:47.
        people.SANI,
        people.TORVAI,
        # Swallowed at :57 — this page is why his row now reads Deceased.
        people.XATHARI,
    ],
    locations=[
        # :7 — "to infiltrate the Imperial Palace".
        loc.IMPERIAL_PALACE,
        # :7 and :9 write the short "Golden Orchard"; the row carries the full
        # name and gained the short one as an alias for exactly this.
        loc.THE_GOLDEN_ORCHARD_ESTATE,
    ],
    regions=[reg.VOLCOR],
    groups=[
        # :7 "tear the Dracai down from within", and :57 calls Xathari "The Dracai".
        grp.DRACAI,
        # :9 — "The Lord Wizards were growing desperate." The body at Court; the
        # rank of the same name is R9 and waits for stage 9.
        grp.LORD_WIZARDS_OF_THE_COURT,
        # :9, :39, :69 — the rebellion this page turns.
        grp.VOLCAI,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/uprising/in-flames.md",
    story_type="main-story",
    title="In Flames",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang, various artists",
    source_link="https://fabtcg.com/articles/flames/",
    publication_date="2022-04-25",
    characters=["emperor"],
    locations=[loc.CHAMBER_OF_THE_DRAGON, loc.MT_VOLCOR],  # "Mount Volcor" in the text is loc.MT_VOLCOR ("Mt. Volcor")
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/high-seas/the-lost-treasure-of-blackwater-strait.md",
    story_type="main-story",
    title="The Lost Treasure of Blackwater Strait",
    authors="Robbie Wen, Edwin McRae, Rachel Rees, Bonnie Harris-Lowe, Joyce Chng, Ryan McIntyre",
    source_link="https://fabtcg.com/articles/the-lost-treasure-of-blackwater-strait/",
    publication_date="2025-06-04",
    characters=[
        "puffin",
        people.BUTTONS,
        people.CAPTAIN_MOODY,
        people.GROTA,
        people.JIGSAW,
        people.KNUCKLES,
        people.MAGPIE,
        people.MELDRICK_SUDDS,
        people.PELORUS,
        people.POLLY_CRANKA,
    ],
    locations=[
        loc.BLACKWATER_STRAIT,
        loc.COPPERTOWN,
        loc.GRAYSTONE_PENITENTIARY,
        loc.PIPER_S_PIER,
        loc.TROPAL_DHANI,
    ],
    regions=[reg.HIGH_SEAS],
    # Hoikers already exist in the catalogue (descriptions.py already carries a
    # description for them) but were not yet linked to this story — the page
    # names them explicitly ("Hoikers! Hhhooooikkers!"; "Hoikers spit acid").
    fauna=[fauna.HOIKERS, fauna.ROCK_TURTLE, fauna.SIREN],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/bright-lights/P̸͍̬̭̭̺͉̣̌̐̾̌͆̚r̴͔͍͐ȯ̴̤̰͠t̵̰̘͑õ̶͍͇c̶̟͒o̶̪̳͋l̶̗̑ ̴̮̓͘A̴̞̗͆ṗ̷̢͕̈́ē̵͍̿ŕ̶̩́ḭ̴̧͐͂o̸͙̖̐͘n̴̞̺͋.md",
    story_type="main-story",
    title="P̸͍̬̭̭̺͉̣̌̐̾̌͆̚r̴͔͍͐ȯ̴̤̰͠t̵̰̘͑õ̶͍͇c̶̟͒o̶̪̳͋l̶̗̑ ̴̮̓͘A̴̞̗͆ṗ̷̢͕̈́ē̵͍̿ŕ̶̩́ḭ̴̧͐͂o̸͙̖̐͘n̴̞̺͋",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/aperion-protocol/",
    publication_date="2023-09-24",
    characters=[
        "teklovossen",  # page only ever says "Teklovossen" (never "Jules") — bare hero
        # slug, matching short-stories/bright-lights/more-than-human.md
        # and heroes-of-rathe/teklovossen-about.md, the two sibling
        # declarations that name him the same way
        people.RIGO,
    ],
    locations=[loc.THE_NEEDLE],
    regions=[reg.METRIX],  # not named in the page text itself, but The Needle's own
    # catalogue entry already carries region="Metrix" — restating
    # an established fact about a location the page does name,
    # not new knowledge
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/interlude/morlock-hill.md",
    story_type="main-story",
    title="Morlock Hill",
    authors="Kasharn Rao, Edwin McRae",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/articles/morlock-hill/",
    publication_date="2022-04-11",
    characters=[
        "boltyn",
        "dorinthea",
        people.MINERVA_THEMIS,
        people.BLASMOPHET,  # named only via "One of Blasmophet's followers..." (line 145)
    ],
    locations=[
        loc.AUDRA,
        loc.FARDREYAS,
        loc.HAZELTOWN,
        loc.MORLOCK_HILL,
        loc.SUNVALE,
        loc.THE_VITIATE_GATEWAY,
        loc.I_ARATHAEL,  # new link: "linking Rathe to i'Arathael" (line 63)
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    weapons=["dawnblade"],  # new link: Dorinthea's sword, named repeatedly (e.g. line 21)
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/high-seas/a-kraken-good-tale.md",
    story_type="main-story",
    title="A Kraken Good Tale",
    authors="Robbie Wen, Edwin McRae, Rachel Rees, Bonnie Harris-Lowe",
    source_link="https://fabtcg.com/articles/a-kraken-good-tale/",
    publication_date="2025-06-05",
    characters=[
        "marlynn",
        "gravy",
        people.GOVERNOR_PRACTISS,
        people.MOLLY_THE_MOP,
        people.PEARL_SANDHRI,
        people.QUARREL,
        people.SLINGER,
        people.WHEELER,
    ],
    locations=[
        loc.GOLDEN_PORT,
        loc.GRAYSTONE_PENITENTIARY,
        loc.KRAKEN_S_BARREL,
        loc.PIPER_S_PIER,
        loc.PORT_CONNIVER,
        loc.TERAMUNDR_S_TRIANGLE,
        loc.TROPAL_DHANI,
    ],
    regions=[reg.HIGH_SEAS],
    fauna=[fauna.CURSED_DHANI_WARRIORS, fauna.CYANATU],
    # Goldkiss Rum (the bottle Pearl produces, l.13) was not previously linked
    # to this page even though the catalogue constant already exists.
    food_drink=[food.GOLDKISS_RUM],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/armory-deck-jarl-vetreidi/battle-of-isenloft.md",
    story_type="main-story",
    title="Battle of Isenloft",
    # Restated exactly as the DB row holds it; no footer byline on the page.
    source_link="https://fabtcg.com/articles/battle-of-isenloft/",
    publication_date="2024-11-21",
    characters=[
        "jarl",
        "oldhim",
        # New — the three Ancients named at :97 ("Yvor. Davnir. They were
        # gone.") and throughout :53-:99 (Galcia). Existing catalogue
        # constants, referenced not restated.
        people.DAVNIR,
        people.GALCIA,
        people.KALSHARPE,
        # New — :25, flanking Oldhim by name. Confirmed against
        # flavour/welcome-to-rathe.md:62 ("Staunch Response" - Ragnar
        # Frosthelm), the only Ragnar in the registry.
        people.RAGNAR_FROSTHELM,
        people.SYBERYS,
        people.SYNVERI,
        # New — :25, flanking Oldhim by name. Confirmed against
        # flavour/tales-of-aria.md:10 ("Biting Gale" - Valgard Hoarfrost),
        # the only Valgard in the registry.
        people.VALGARD_HOARFROST,
        people.YVOR,
    ],
    locations=[
        loc.ALDENGROVE,
        loc.ENION,
        # New to this page's links — the story's own setting (title, :17,
        # :71 "Isenloft's sheer walls", etc.). Existing catalogue constant
        # (region Aria), not currently linked from this page.
        loc.ISENLOFT,
        loc.VALAHAI,
    ],
    regions=[reg.ARIA],
    monsters=[mon.GLUTGORR, mon.RAVENIR],
    groups=[
        # :41, :47, :49, :65 (twice) — "the Ollin", "one Ollin", "Ollin
        # looked to Ollin".
        grp.OLLIN,
        # :19 — "Wayfarers, wizards, Rosetta, and guardians shrank out of
        # his way", capitalised alongside grp.WAYFARERS.
        grp.ROSETTA,
        grp.WAYFARERS,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/compendium-of-rathe/vow-unbroken.md",
    story_type="main-story",
    title="Vow Unbroken",
    authors="Robbie Wen, Edwin McRae, Corey J. White, Rachel Rees, Melissa Ren, Paul Davies",
    source_link="https://fabtcg.com/articles/vow-unbroken/",
    publication_date="2026-04-07",
    characters=[
        "boltyn",
        "briar",
        "hala",
        "levia",
        "lexi",
        people.AUREA_CHAMPION_OF_THE_DAWN,
        people.BLASMOPHET,
        # "Bastion, Magister of Defense" — matches this constant's name and
        # epithet exactly.
        people.THEBASTO_MAGISTER_OF_DEFENSE,
    ],
    locations=[loc.CANDLEHOLD, loc.GOLDENHELM_KEEP, loc.THE_SOLARIUM, loc.VALAHAI],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_SAVAGE_LANDS],
    groups=[grp.HAND_OF_SOL, grp.ROSETTA, grp.WAYFARERS],
    weapons=["zenith-blade"],  # Hala's sword, named repeatedly, matches the canonical slug
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/catch-of-the-day.md",
    story_type="main-story",
    title="Catch of the Day",
    source_link="https://fabtcg.com/hero/riptide-lurker-of-the-deep/story/riptide-story/",
    # authors/artists/publication_date/thumbnail_image_link: all empty in the DB row,
    # no frontmatter and no "Story by / Art by" footer on the page — omitted.
    characters=["riptide", "uzuri"],
    locations=[loc.GRIEFERS_REEF, loc.SEETHE, loc.TEMPEST_STRAITS],
    regions=[reg.HIGH_SEAS, reg.METRIX, reg.THE_PITS],
    # High Seas is never spelled out, but Griefers Reef (region="High Seas" in the
    # catalogue) and Tempest Straits are both named — Metrix and "the Pits" are
    # both named verbatim in the text.
    groups=[grp.PIRANHAS],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/bright-lights/the-dynamic-man.md",
    story_type="main-story",
    title="The Dynamic Man",
    source_link="https://fabtcg.com/articles/the-dynamic-man/",
    publication_date="2023-09-22",
    characters=[
        # Full lore name, not the bare "teklovossen" slug — the catalogue constant
        # already folds the hero row and prose name onto one character_id.
        people.JULES_TEKLOVOSSEN,
        people.RIGO,
    ],
    locations=[
        loc.GIGADRILL_ELEVATOR,
        loc.IRON_ASSEMBLY,
        loc.PIT_3,  # new — see below
        loc.PLUMVEX_PIPES_FACTORY,
        loc.TEKLO_INDUSTRIES,
        loc.THE_NEEDLE,
    ],
    regions=[reg.METRIX],
    groups=[
        grp.COGWERX,
        grp.IRON_ASSEMBLY,  # see Ambiguities — page uses it as an organisation, not a place
        grp.TEKLO_INDUSTRIES,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/bright-lights/system-failure.md",
    story_type="main-story",
    title="System Failure",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/system-failure/",
    publication_date="2023-09-22",
    characters=[
        "dash",
        "maxx",  # narrator; "Phantom Maxx, at your service" (line 31) plus the
        # whole Rosario-orphan backstory matches the seeded "Maxx Nitro"
        people.JULES_TEKLOVOSSEN,  # page names him in full, "Jules Teklovossen"
        # (line 63) — unlike sibling
        # bright-lights/P̸[...]on.md, which names only
        # "Teklovossen" and uses the bare hero slug,
        # this page earns the full CharacterEntry form
        people.LENA_BELLE,
        people.RICKY_ROYCE,
    ],
    locations=[
        loc.COPPERTOWN,
        loc.IRON_ASSEMBLY,
        loc.ROSARIO_HILLS,  # page calls it "Rosario Hills Institute" (line 33);
        # matches the existing row (notes: "Orphanage parent
        # company.")
        loc.ROSARIO_ORPHANAGE,
        loc.TEKLO_INDUSTRIES,
        loc.THE_NEEDLE,  # "Teklo Industries' big, beautiful Needle" (line 63)
        loc.ZINNIA_PARK,
        loc.ROSARIO_CHATEAUX,  # new — see below
    ],
    regions=[reg.METRIX, reg.THE_PITS],
    weapons=["plasma-barrel-shot"],  # linked inline as "Plasma Barrel Shot" (line 57)
    food_drink=[food.NUTRISLUG],  # new — see below
    # Both already carry a locations row; the page also treats them as the
    # organisations behind those places ("the Iron Assembly could afford more
    # space for its 'valued customers'", line 11; "A party ... Teklo Industries
    # hasn't seen before", line 71) — same shape as the sibling
    # short-stories/bright-lights/bright-lights.md declaration.
    groups=[grp.IRON_ASSEMBLY, grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/bright-lights/synthetic-futures.md",
    story_type="main-story",
    title="Synthetic Futures",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/synthetic-futures/",
    publication_date="2023-09-22",
    # thumbnail_image_link omitted — empty in the DB row.
    characters=[
        "dash",
        "maxx",
        "data-doll-mkii",
        people.REZ,
        people.THIROUX,
        people.DR_WYVERSTONE,
        people.SYNTHEA_TEKLO,
        people.JULES_TEKLOVOSSEN,
    ],
    locations=[
        loc.LOWLAKE,  # Maxx's hideout — named twice, missing from the seeded set
        loc.THE_SPRAWL,  # new constant, see below
        loc.COPPERTOWN,
        loc.UNDERDOG_CAFE,
        loc.WEST_RISE,
        loc.EAST_RISE,
        loc.THE_NEEDLE,
        loc.IRON_HALL,
        loc.EIGHTH_PRECINCT,
        loc.IRON_ASSEMBLY,
        loc.TEKLO_INDUSTRIES,
    ],
    regions=[reg.METRIX, reg.THE_PITS],
    groups=[
        grp.COGWERX,  # rival corp, discussed as a market actor throughout
        grp.TEKLO_INDUSTRIES,  # discussed as a corporation, not just the building
        grp.IRON_ASSEMBLY,  # "the Assembly collects the data... watch, listen, and speak"
        grp.CIRCUIT_BREAKER,  # new constant, see below
    ],
    food_drink=[
        food.AMYGDAZZLA,  # new constant — matches an existing unclaimed DB row
        food.TINKER_TEA,  # new constant
    ],
    weapons=["teklo-plasma-pistol"],  # Dash's sidearm; canonical slug confirmed
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/rosetta/roots-of-change.md",
    story_type="main-story",
    title="Roots of Change",
    # No footer byline and no frontmatter author on the page; DB carries no
    # authors value either, so the field is omitted rather than guessed.
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/articles/roots-of-change/",
    publication_date="2024-08-23",
    characters=[
        "florian",
        "verdance",
        people.DAVNIR,
        people.OZRIM,
        people.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
        loc.THRONE_GLADE,
    ],
    regions=[reg.ARIA],
    # Ozrim is named "a member of the Rosetta, Candlehold's ancient council" (:65).
    groups=[grp.ROSETTA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/rosetta/essence-of-decay.md",
    story_type="main-story",
    title="Essence of Decay",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/articles/essence-of-decay/",
    publication_date="2024-08-24",
    characters=[
        # :127 — "a time when the Warden of Thorns had departed Candlehold, the
        # only Rosetta to ever do so." Matches Briar's canonical hero title
        # ("Briar, Warden of Thorns") exactly — no other Rosetta departed.
        "briar",
        "florian",
        "verdance",
        people.DAVNIR,
        people.OZRIM,
        # "our Queen" / "the Queen's chosen rose" / "our departed Queen" (:13,
        # :39, :43, :51, :59) — the ruler of Candlehold, not Davnir.
        people.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.CANDLELIGHT_CLEARING,
        # :7, :111, :117 — new link only, references the existing constant.
        loc.ROTWOOD,
    ],
    regions=[reg.ARIA],
    groups=[grp.ROSETTA],
    weapons=["rotwood-reaper"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/the-iconoclast-trials.md",
    story_type="main-story",
    title="The Iconoclast Trials",
    authors="Edwin McRae, Rachel Rees",
    artists="Henrique Lindner",
    source_link="https://fabtcg.com/hero/arakni-huntsman/story/arakni-story/",
    # No frontmatter and no "Story by / Art by" footer on the page — scalars restated
    # from the existing DB row verbatim (see Notes).
    characters=[
        "arakni-huntsman",  # never named "Arakni" in prose — see Ambiguities
        people.DR_KREST_MORTIMER_THE_FIXER,  # signs the footer, "Director of Southmaw Asylum"
    ],
    locations=[
        loc.SHUNTSWITCH_RAILWAY_STATION,
        loc.SKEIN,
        loc.SOUTHMAW,  # "Southmaw Asylum" / "Southmaw", named repeatedly; not yet linked to this story
        loc.THE_MAW,
    ],
    regions=[reg.THE_PITS],
    monsters=[mon.DREGS],  # "alchemical mutants...colloquially known as dregs" (line 3)
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/mastery-pack-guardian/trouble-in-larinkmorth.md",
    story_type="main-story",
    title="Trouble in Larinkmorth",
    authors="Robbie Wen, Edwin McRae, Ryan McIntyre, Rachel Rees, Michael Coorlim, Melissa Ren",
    source_link="https://fabtcg.com/articles/trouble-in-larinkmorth/",
    publication_date="2025-08-06",
    # artists / thumbnail_image_link omitted — empty in the DB row.
    characters=[
        "valda",
        "bravo",  # "Oldhim named him leader of the new Ollin" (line 43)
        "oldhim",
        "jarl",  # "Jarl Vetreiði." (line 87)
        people.BISKI,
        people.BRAUMEISTER_BALEN,
        people.EINAR,
        people.FARIN_THE_PORTER,
        people.HILDEGUN,
        people.KAYSIN,
        people.KOSSEN,
        people.LILJA,
        people.TIRIL,
        people.TOMASS,
        people.WIDOW_JOHANA,
        people.ORIEN,  # new — see below; possible unannounced hero, see Ambiguities
    ],
    locations=[
        loc.CANDLEHOLD,  # seeded; "the first time they'd crossed paths at Candlehold" (line 127)
        loc.LARINKMORTH,
        loc.THE_EVERFEST_CARNIVAL,  # "Everfest" / "the Carnival" (lines 23, 37, 39, 55-61)
        loc.ISENLOFT,  # "his last stand at Isenloft" (line 127)
        loc.MIGHT_N_MEAD,  # "the Might 'n Mead" (line 57)
        loc.THE_FLOW,  # "the flutter of the Flow in her chest" (lines 139-141)
        loc.ISENRI_SAKE_BREWERY,  # new — see below
    ],
    regions=[reg.ARIA, reg.SOLANA],
    monsters=[mon.RAVENIR],  # "That thing's a ravenir!" (line 129)
    fauna=[fauna.VITR_EO],  # named only as a simile — "antlered like a vitr'eo" (line 83)
    groups=[grp.OLLIN],  # "the new Ollin" (line 43); "I'm no Ollin" (line 181)
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/squeakers-christmas.md",
    story_type="main-story",
    title="Squeakers' Christmas",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/squeakers-christmas/",
    publication_date="2022-12-26",
    characters=[
        "azalea",
        "arakni-huntsman",
        "dash",
        people.LENA_BELLE,
    ],
    locations=[loc.COPPERTOWN, loc.TEKLA_TOY_FACTORY],
    regions=[reg.ARIA, reg.METRIX],
    fauna=[fauna.SNOWFAWN],
    food_drink=[food.FESTIVE_FLARE],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/its-just-business.md",
    story_type="main-story",
    title="It's Just Business",
    authors="Edwin McRae, Rachel Rees",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/hero/uzuri-switchblade/story/uzuri-story/",
    # publication_date / thumbnail_image_link: empty in the DB row — omitted.
    characters=[
        "uzuri",
        people.BARON_THE_BUTCHER,
        people.HISATO,
        people.JEMJANG,
        people.MADAM_ROUGE,
        people.NJERI,
        people.OVERSEER_CRICHTON,
        people.WHITETAIL,
    ],
    locations=[
        loc.ANKOMEIDO,
        loc.OVERSEER_CRICHTON_S_MANSION,
        loc.SEETHE,
        loc.SORI_16,
        loc.THE_DROP,  # "a bar called The Drop" — existing constant, not yet linked to any story
        loc.THE_LEAF_HOUSE,
    ],
    regions=[reg.METRIX, reg.MISTERIA, reg.THE_PITS],
    fauna=[fauna.BLINDSEAL, fauna.BLOATFIN],
    food_drink=[food.SEWER_CHICKEN],  # new — see below
    groups=[
        grp.BLACKJACK_S_MINING_INCORPORATED,  # new
        grp.GIMLET_MINING,  # new
        grp.RUNNING_TIGERS,  # new — Njeri/Hisato/Jemjang's old smuggling outfit
        grp.THE_SPIDER,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/rosetta/seeds-of-renewal.md",
    story_type="main-story",
    title="Seeds of Renewal",
    artists="Nikolay Moskvin",
    source_link="https://fabtcg.com/articles/seeds-of-renewal/",
    publication_date="2024-08-25",
    characters=[
        "aurora",
        "briar",  # named only via her title, "the Warden of Thorns" (:53)
        "florian",
        "melody",
        "oscilio",
        people.DAVNIR,  # "ancient Davnir answered" (:121) — distinct from the queen, see Ambiguities
        people.MAELA_ONE_EYE,
        people.OZRIM,
        people.QUEEN_OF_CANDLEHOLD,  # "The Queen of Candlehold is dead" (:45) — existing constant, distinct from Davnir per a-grand-adventure.md precedent
        "verdance",
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ENION,
        loc.LARINKMORTH,
        loc.MILLENNIUM_TREE,  # new — see catalogue section
        loc.THE_EVERFEST_CARNIVAL,  # "since Everfest" (:7)
        loc.THE_FLOW,  # "surge in the Flow" (:43) and later
        loc.THE_KORSHEM,  # "from Korshem to Larinkmorth" (:45)
    ],
    regions=[reg.ARIA],
    groups=[
        grp.ROSETTA,  # "his fellow Rosetta" (:69), "the other Rosetta" (:91)
        grp.THE_MAELA,  # "Seers of Everfest" (:47); Maela One-eye is present, matches aria.md:93's "a group of seers known as the Maela"
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/rosetta/secret-of-the-aetherscribes.md",
    story_type="main-story",
    title="Secret of the Aetherscribes",
    source_link="https://fabtcg.com/articles/secret-of-the-aetherscribes/",
    publication_date="2024-08-29",
    characters=[
        "aurora",
        "melody",
        "oscilio",
        people.YVOR,  # "Yvor defended Enion against the Old Ones" (:89)
    ],
    locations=[
        loc.ARCTUROS,
        loc.BOULDERHEAD_ISLAND,
        loc.ENION,
        loc.THE_FLOW,  # "an unusual fluctuation in The Flow" (:141)
        loc.VOLTHAVEN,
    ],
    regions=[reg.ARIA],
    monsters=[mon.GOLEM],  # new — see Ambiguities
    fauna=[
        fauna.KAIE_O,
        fauna.NA_SHARI,
        fauna.SHOCK_STRIKER,  # new
    ],
    groups=[
        grp.AETHERSCRIBES,
        grp.OLLIN,  # "like a slumberous Ollin thawing under a new dawn" (:33)
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/the-spiders-trap.md",
    story_type="main-story",
    title="The Spider's Trap",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/spiders-trap/",
    publication_date="2023-03-04",
    # thumbnail_image_link omitted — empty in the DB row.
    # narrated_videos omitted — omission preserves the seeded St_Havock reading.
    characters=[
        "arakni-huntsman",  # seeded slug; page calls Arakni "the Huntsman" (:130, :134)
        "emperor",  # "The Emperor of Volcor" — the (forged) contract's named issuer (:26)
        "riptide",
        "uzuri",
        people.WHITETAIL,  # existing constant; former Spider lieutenant turned traitor
        people.WIDOW,  # a Spider assassin (:86), not Widow Johana of Larinkmorth
        people.SLAB,  # leads the Blockheads (:138)
        people.AMBER,  # new
        people.BLAVE,  # new
        people.CAGER,  # new
        people.CARVA,  # new
        people.FLORENCE,  # new
        people.JAPE,  # new
        people.MADAME_FUSE,  # new
        people.MARROW,  # new — see Ambiguities re: kind
        people.MELTEN_WICK,  # new
        people.SILKA,  # new
    ],
    locations=[loc.THE_DROP],  # seeded; Uzuri's bar, scene of Act 1 (:8)
    regions=[reg.METRIX, reg.THE_PITS, reg.VOLCOR],  # all three named verbatim
    monsters=[mon.DREGS],  # "a brace of slavering dregs" (:136) — existing constant, has a description
    groups=[
        grp.THE_SPIDER,  # existing; "Assassins of the Spider" (:180)
        grp.TORCHED,  # new — Wick's gang (:124, :130, :152)
        grp.FREAKSHOW,  # new — Cager's gang (:136, :142)
        grp.BLOCKHEADS,  # new — Slab's gang (:138)
        grp.NUMBSKULLS,  # new — Marrow's gang (:140)
        grp.JAWBREAKERS,  # new — Madame Fuse's gang (:142)
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/README.md",
    story_type="main-story",
    title="Main Story",
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/the-hunted/splinter-soul.md",
    story_type="main-story",
    title="Splinter Soul",
    source_link="https://fabtcg.com/hero/terra/story/splinter-soul/",
    publication_date="2025-02-27",
    characters=["terra", people.HYRINTH, people.SIDRIZ],
    # The Flow and Mount Heroic are both named in the text; The Korshem was
    # the only one already seeded, so all three are restated (replace-semantic).
    locations=[loc.THE_KORSHEM, loc.THE_FLOW, loc.MOUNT_HEROIC],
    regions=[reg.ARIA],
    # Gossamhares was the only seeded fauna link; Fianna and Meep are also
    # named on the page ("a tall fianna", "squirrels and meeps").
    fauna=[fauna.GOSSAMHARES, fauna.FIANNA, fauna.MEEP],
    flora=[flora.BLISSBERRY_BUSH],  # new catalogue const, see below
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/uprising/journey-into-the-forgotten.md",
    story_type="main-story",
    title="Journey into the Forgotten",
    authors="Edwin McRae, Rachel Rees",
    artists="Sam Yang",
    source_link="https://fabtcg.com/articles/journey-forgotten/",
    publication_date="2022-04-21",
    characters=["iyslander"],
    locations=[
        # :49, :81 — "I remember a name. Volcor." / "I recall a name, Ashvahan."
        loc.ASHVAHAN,
        # :1-121, throughout — Iyslander's frozen homeland.
        loc.BLEAK_EXPANSE,
        # :33 — "its Flow will send me on my way" (Aria's Flow). Not previously linked here.
        loc.THE_FLOW,
        # :33 — "the Great Tree of Korshem".
        loc.THE_KORSHEM,
    ],
    regions=[reg.ARIA, reg.SOLANA, reg.VOLCOR],
    fauna=[
        # :31 — "A kaie'o bounds into the meadow". Not previously linked here.
        fauna.KAIE_O,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/the-hunted/mark-of-a-traitor.md",
    story_type="main-story",
    title="Mark of a Traitor",
    source_link="https://fabtcg.com/articles/mark-of-a-traitor/",
    publication_date="2025-01-14",
    characters=[
        "fang",
        "cindra",
        "emperor",
        "arakni-web-of-deceit",
        people.GENERAL_YAMATOKA,
        people.KAYAT,
        people.LIEUTENANT_LI,
    ],
    locations=[loc.DESHVAHAN, loc.SAND_GLASS_DISTRICT],
    regions=[reg.VOLCOR],
    monsters=[mon.GUCAI],  # new — see New catalogue constants
    groups=[
        grp.CHILDREN_OF_THE_DRAGON,
        grp.SAYASHI,
        grp.DRACAI,
        grp.DUST_RUNNERS,  # new
        grp.ROYAL_GUARD,  # new, ambiguous — see Ambiguities
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/uprising/fires-of-rebellion.md",
    story_type="main-story",
    title="Fires of Rebellion",
    source_link="https://fabtcg.com/hero/fai/story/fai-story-fires-of-rebellion/",
    characters=[
        "fai",
        "dromai",
        "emperor",
        people.GENERAL_RIKU,
        people.EUN,
        people.MIN_OF_THE_FOREST_OF_FLAMES,  # "Min" is Fai's mother; page is set in the Forest of
        # Flames, matching this constant over PROFESSOR_MIN
        people.TORVAI,
        people.PHAELIN,  # new
    ],
    locations=[
        loc.FOREST_OF_FLAMES,
        loc.THE_GOLDEN_ORCHARD_ESTATE,
        loc.ASHVAHAN,
        loc.TAOKING,  # new
    ],
    regions=[reg.VOLCOR],
    groups=[grp.VOLCAI, grp.DRACAI, grp.CINTARI],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/outsiders/tidings-in-the-light.md",
    story_type="main-story",
    title="Tidings in the Light",
    authors="Edwin McRae, Rachel Rees",
    artists="Henrique Lindner",
    source_link="https://fabtcg.com/articles/tidings-light/",
    publication_date="2023-03-04",
    characters=[
        "boltyn",
        "dromai",
        "emperor",
        "shiyana",
        people.AIOS,
        people.EIRINA,
        people.GENERAL_RIKU,
        people.GRAND_MAGISTER_THE_STEADFAST,
        # "The Bastion-Magister of Defense" (line 97) — matches this constant's
        # name+office exactly, same resolution main_story.py already uses for
        # "vow-unbroken.md".
        people.THEBASTO_MAGISTER_OF_DEFENSE,
        people.THE_AMBASSADOR,  # new — "The Ambassador-Magister of Diplomacy" (line 67)
        people.THE_LIBRARIAN,
        people.XATHARI,
    ],
    locations=[loc.AMPHITHEATRE, loc.THE_GRAND_COUNCIL, loc.THE_SOLARIUM],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_PITS, reg.VOLCOR],
    groups=[grp.ALSHONI, grp.CHILDREN_OF_THE_LIGHT, grp.EZU, grp.GEMINI, grp.L_APOCALYPTA],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/the-hunted/cleanse-the-corruption.md",
    story_type="main-story",
    title="Cleanse the Corruption",
    source_link="https://fabtcg.com/articles/cleanse-the-corruption/",
    publication_date="2025-01-15",
    characters=[
        "cindra",
        "fang",
        "taipanis",
        "emperor",  # all four are hero slugs, not people.X
        "arakni-web-of-deceit",
        people.JEMJANG,
        people.LORD_MERCHANT_SAVAI,
        people.LORD_WIZARD_CHIYO,
        people.GENERAL_YAMATOKA,
        people.GENERAL_RIKU,
        people.TETZUO,
        people.KAYAT,
    ],
    locations=[loc.DESHVAHAN],
    regions=[reg.THE_PITS],
    groups=[grp.SAYASHI, grp.CHILDREN_OF_THE_DRAGON, grp.THE_SPIDER, grp.ALSHONI, grp.VOLCAI],
    monsters=[mon.GUCAI],
    fauna=[fauna.RYOKI],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/the-hunted/hunter-and-hunted-both.md",
    story_type="main-story",
    title="Hunter and Hunted Both",
    source_link="https://fabtcg.com/articles/hunter-and-hunted-both/",
    publication_date="2025-01-16",
    characters=[
        "cindra",
        "fang",
        "emperor",  # "For the Emperor. For the blood of the dragon!" (line 161)
        "arakni-web-of-deceit",
        people.LORD_MERCHANT_SAVAI,
        people.LORD_WIZARD_CHIYO,
        people.LIEUTENANT_YAMADA,
    ],
    locations=[loc.DESHVAHAN, loc.THE_OBSIDIAN_COAST, loc.ASHVAHAN],
    regions=[reg.VOLCOR],
    fauna=[fauna.FLARE_DEER, fauna.DESERT_FOX],
    groups=[grp.ALSHONI, grp.CHILDREN_OF_THE_DRAGON, grp.DRACAI],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/rosetta/to-halt-the-dark.md",
    story_type="main-story",
    title="To Halt the Dark",
    source_link="https://fabtcg.com/articles/to-halt-the-dark/",
    publication_date="2024-10-11",
    characters=["ira", people.JING, people.SHIRO, people.XILIN],
    locations=[loc.CHROME_CAVERNS, loc.SKYLARK_PEAK, loc.IKARU],
    regions=[reg.SOLANA, reg.MISTERIA, reg.VOLCOR],
    monsters=[mon.PUPPETEER],
    fauna=[fauna.LONGMA],
    groups=[grp.CRIMSON_HAZE, grp.AUIS_SCALES, grp.IKARU_CLAN],
    weapons=["edge-of-autumn"],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/the-hunted/children-of-chaos.md",
    story_type="main-story",
    title="Children of Chaos",
    source_link="https://fabtcg.com/articles/children-of-chaos/",
    publication_date="2025-01-17",
    characters=[
        "cindra",
        "emperor",
        "fang",
        "arakni-web-of-deceit",
        people.JEMJANG,
        people.KAYAT,
        people.LORD_WIZARD_CHIYO,
        people.GENERAL_RIKU,
        people.LIEUTENANT_YAMADA,
        people.VYNSERAKAI,  # named as "a grand temple of Vynserakai"
    ],
    locations=[loc.DESHVAHAN],
    groups=[
        grp.DRACAI,  # "the southern Dracai"
        grp.CHILDREN_OF_THE_DRAGON,  # "the Children of the Dragon"
        grp.THE_SPIDER,  # "the Spider's sticky web"
        grp.CHILDREN_OF_CHAOS,  # new — "the Children of Chaos"
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/main-story/uprising/calm-before-the-storm.md",
    story_type="main-story",
    title="Calm Before the Storm",
    source_link="https://fabtcg.com/hero/iyslander-2/story/iyslander-story-calm-before-the-storm/",
    characters=["iyslander", people.KOVA, people.DENG],
    locations=[loc.ASHVAHAN, loc.MT_VOLCOR],
    regions=[reg.VOLCOR, reg.SOLANA],
    fauna=[fauna.RYOKI, fauna.MORROWS],
    groups=[grp.DRACAI, grp.VOLCAI],
    dry_run=True,
)
