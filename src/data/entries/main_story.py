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
    # TODO: needs catalogue constant — Gentua (fauna); also called "Imps" per src/faq.md
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
    ],
    locations=[
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
    characters=["viserai"],
    locations=[
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
        # is linked to no other story; reopened with the species values in stage 4.
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
        "fai",
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
