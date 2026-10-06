"""Flavour page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

from entries._runner import db
from entries.catalogue import (
    characters as people,
)
from entries.catalogue import (
    groups as grp,
)
from entries.catalogue import (
    locations as loc,
)
from entries.catalogue import (
    regions as reg,
)

db.upsert_story(
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    characters=[
        "aurora",
        "lexi",
        people.ASTREA_QUAZOR,
        people.AURIC_SEERESS,
        people.LORD_SUTCLIFFE,
        people.RUPIUS_AURIC_SCROLLMASTER,
        people.YVOR,
        people.DARYAS_NIMBUS,
        people.FREYA_ELDINGSTURM,
        people.MAELA_ISULFV,
        people.MAELA_SHARENA,
        people.REZNYR_ELDINGSTURM,
        people.SKYNDA_FEYSCOUT,
        people.VYHARA_CLOUDBURST,
    ],
    locations=[
        loc.ENION,
        loc.VALAHAI,
        loc.VOLTHAVEN,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/monarch.md",
    story_type="flavour",
    title="Monarch",
    characters=[
        "prism",
        people.AMIRA_SURANA,
        people.ASTRA_MORENA,
        people.AUREA_CHAMPION_OF_THE_DAWN,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.CHANCELLOR_HELENA_PRIMAVERA,
        people.CHANCELLOR_HYPATIA,
        people.CHIARA_SUNCREST,
        people.DANU_ASHENGUARD,
        people.ERSEBET,
        people.GRAND_MAGISTER_THE_RADIANT,
        people.HARLAND,
        people.HAROLD_HONEYSETT,
        people.JACKDAW,
        people.KIRIGAMI,
        people.MERLEN_RIVERA,
        people.NESTUS,
        people.SANNI,
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        people.VIDYA_WILLOWMERE,
    ],
    fragments={"prism": "celestial-cataclysm---mon062"},
    locations=[
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.SOLANA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/non-set-cards.md",
    story_type="flavour",
    title="Non-Set Cards",
    characters=[
        "squizzyfloof",
        "yorick",
        people.AEGIS_THE_SHIELD_OF_LIGHT,
        people.AVALON_MESSENGER_OF_THE_DAWN,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.THEMIS_KEEPER_OF_THE_SCALES,
        people.YVOR,
    ],
    locations=[
        loc.AURIC_KEEP,
        loc.ENION,
        loc.VOLTHAVEN,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/super-slam.md",
    story_type="flavour",
    title="Super Slam",
    characters=[
        "kayo",
        "lyath",
        "pleiades",
        "tuffnut",
        "victor-goldmane",
        people.BATBITER,
        people.EMEVIERE,
        people.FIGHTMASTER_KOX,
        people.FIGHTMASTER_RUSTY,
        people.LUCA_ARENA_CICERONE,
        people.MOLOCA,
        people.SLAPSTICK_SAL,
        people.SPEAKEASY,
        people.FOREMAN_PEBB,
        people.FUGGER_GRIMES,
        people.HELX,
        people.SALVADOR_STALLION,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.DEN_OF_BEASTS,
        loc.GRINNING_BOAR_CANTINA,
        loc.INFERNAL_MAW,
        loc.THE_MOAT,
        loc.THE_UNDERCROFT,
    ],
    regions=[
        reg.THE_SAVAGE_LANDS,
    ],
    groups=[
        grp.BALEFUL_HORDE,
        grp.BOULDERS,
        grp.CHAMPIONS_OF_CHIVALRY,
        grp.FURY_FISTS,
        grp.GLORYTOWN_GLADIATORS,
        grp.JUNGLE_SLAYERS,
        grp.MYTHMAKERS,
        grp.PROWLERS,
        grp.WILD_WONDERS,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/mastery-pack-guardian.md",
    story_type="flavour",
    title="Mastery Pack Guardian",
    characters=[
        "fai",
        "valda",
        people.AEGIS_THE_SHIELD_OF_LIGHT,
        people.MAELA_ONE_EYE,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[
        reg.ARIA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/mastery-pack-warrior.md",
    story_type="flavour",
    title="Mastery Pack Warrior",
    characters=[
        people.FARRIS,
        people.FIGHTMASTER_KOX,
        people.FIGHTMASTER_RUSTY,
        people.LIEUTENANT_TIMAEUS,
        people.CAPTAIN_SHEVEZ,
        people.INQUISITOR_ARICIA,
        people.LUCILLA_THE_SETTING_SUN,
        people.TASHA_OF_DESHVAHAN,
        people.THEBASTO_MAGISTER_OF_DEFENSE,
        people.VANIK_SILVERTOOTH,
    ],
    locations=[
        loc.DAWNHAVEN,
        loc.DESHVAHAN,
        loc.CORALYSI,
        loc.NEELASHA,
        loc.OCTOMILITIA,
        loc.THE_SOLARIUM,
        loc.VALAHAI,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/usurp-the-shadow-throne.md",
    story_type="flavour",
    title="Usurp the Shadow Throne",
    characters=[
        "malice",
        "chane",
        "levia",
        "vynnset",
        "viserai",
        people.BLASMOPHET,
        people.SOL,
        people.ARBITER_MAGISTER_OF_JUSTICE,
        people.XERYS,
    ],
    locations=[
        loc.SHADOWREALM,
    ],
    regions=[
        reg.SOLANA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/outsiders.md",
    story_type="flavour",
    title="Outsiders",
    characters=[
        "arakni-huntsman",
        people.ACHLYS_HAG_OF_MOJIRE,
        people.AKUO,
        people.DR_KREST_MORTIMER_THE_FIXER,
        people.LENA_BELLE,
        people.OTMAR,
        people.SURAJ_THE_ORACLE,
    ],
    fragments={"arakni-huntsman": "back-stab---out015016017"},
    locations=[
        loc.FLOATING_DOJO,
        loc.MOJIRE,
        loc.SKYLARK_PEAK,
    ],
    regions=[reg.THE_PITS],
    groups=[grp.L_APOCALYPTA, grp.THE_SPIDER, grp.TRANSCENDENTS],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/arcane-rising.md",
    story_type="flavour",
    title="Arcane Rising",
    characters=[
        "azalea",
        "dash",
        "kano",
        people.ATEIA,
        people.DR_KREST_MORTIMER_THE_FIXER,
        people.ELDON_LOST_KNIGHT,
        people.ELIAS_EDGECOMBE,
        people.GRAHAM_THE_GALLANT,
        people.JEEVES,
        people.LIEUTENANT_YAMADA,
        people.MAXWELL,
        people.VERA,
        people.XAINE_RUNESCRIBE,
    ],
    fragments={"azalea": "three-of-a-kind---arc044", "kano": "blazing-aether---arc118"},
    locations=[loc.DEATH_S_KNELL],
    regions=[reg.THE_PITS],
    groups=[grp.DRACAI],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/crucible-of-war.md",
    story_type="flavour",
    title="Crucible of War",
    characters=[
        "hala",
        "jarl",
        "kano",
        people.BUTCHER_JEK,
        people.GREENBIRD,
        people.JACKDAW,
        people.JULES_TEKLOVOSSEN,
        people.LINNEA_MISTRESS_OF_MALADY,
        people.SEPTUS,
        people.SPOKES,
        people.THUK,
        people.TOGARK_THE_WRANGLER,
    ],
    fragments={
        "hala": "unified-decree---cru083",
        "kano": "aetherize---cru164",
        "Jules Teklovossen": "teklovossens-workshop---cru115116117",
    },
    locations=[loc.MT_ISEN],
    regions=[reg.ARIA, reg.THE_PITS],
    groups=[grp.REKVAS_BLOODBOARS],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/part-the-mistveil.md",
    story_type="flavour",
    title="Part the Mistveil",
    characters=[
        "enigma",
        "nuu",
        "zen",
        people.ANHE_KOTORI_WAVEBENDER,
        people.DAN_LU_KOTORI_GALEWARDEN,
        people.GUDO_MISTWARD_PILGRIM,
        people.HIREI,
        people.KOUKI,
        people.MASTER_MORITA_ART_OF_THE_HAND,
        people.MIKU,
        people.NING_KOTORI_MOONSEEKER,
        people.REINA_SPIRIT_CALLER,
        people.SHIO,
        people.SOREN,
        people.SUMIRE,
        people.TOHIRO_ETERNAL_SCRIBE,
    ],
    fragments={"enigma": "deep-blue-sea---mst084"},
    locations=[loc.RYOSOZAN_PEAKS],
    regions=[reg.MISTERIA],
    groups=[grp.CLAN_NASU_KA, grp.KAIGOMO, grp.KOTORI, grp.VIPRESSA, grp.VOLCAI],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/compendium-of-rathe.md",
    story_type="flavour",
    title="Compendium of Rathe",
    characters=[
        "enigma",
        "florian",
        "hala",
        "maxx",
        "uzuri",
        people.ANARCH_ZEIR,
        people.APOSTATE,
        people.BATBITER,
        people.DAVNIR,
        people.DR_KREST_MORTIMER_THE_FIXER,
        people.FIGHTMASTER_KOX,
        people.GALCIA,
        people.KARALYN,
        people.MAELA_FAIRMIND,
        people.SOL,
        people.THEMIS_KEEPER_OF_THE_SCALES,
        people.YVOR,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.CORALYSI,
        loc.ENION,
        loc.I_ARATHAEL,
        loc.MOUNT_HEROIC,
        loc.THE_FLOW,
        loc.VALAHAI,
    ],
    regions=[reg.ARIA],
    groups=[
        grp.GEMINI,
        grp.L_APOCALYPTA,
        grp.PROWLERS,
        grp.ROSETTA,
        grp.TEKLO_INDUSTRIES,
        grp.THE_SPIDER,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/uprising.md",
    story_type="flavour",
    title="Uprising",
    characters=[
        "dromai",
        "fai",
        "victor-goldmane",
        people.INFERNAI,
        people.AZVOLAI,
        people.CROMAI,
        people.DOMINIA,
        people.DRACONA_OPTIMAI,
        people.FYENDAL,
        people.KYLORIA,
        people.MIRAGAI,
        people.NEKRIA,
        people.OUVIA,
        people.THEMAI,
        people.TOMELTAI,
        people.VYNSERAKAI,
        people.YENDURAI,
        people.YUNKAI,
    ],
    fragments={
        "dromai": "burn-away---upr094",
        "fai": "lava-vein-loyalty---upr069070071",
        "victor-goldmane": "that-all-you-got---upr189",
    },
    locations=[
        loc.BLEAK_EXPANSE,
        loc.IMPERIAL_FURNACE,
        loc.KYLORIA_S_LAIR,
        loc.RED_DESERT,
        loc.RUST_BELT,
        loc.SANDIKAI,
        loc.THE_ASH_PLAINS,
    ],
    regions=[
        reg.ARIA,
        reg.DEMONASTERY,
        reg.METRIX,
        reg.MISTERIA,
        reg.SOLANA,
        reg.THE_PITS,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
    ],
    groups=[
        grp.DRACAI,
        grp.THE_SPIDER,
        grp.VOLCAI,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/dynasty.md",
    story_type="flavour",
    title="Dynasty",
    characters=[
        "boltyn",
        "emperor",
        "hala",
        "prism",
        people.EIRINA,
        people.GENERAL_NAKAMI,
        people.GRANDMASTER_LI,
        people.JACKDAW,
        people.JULES_TEKLOVOSSEN,
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
    ],
    fragments={
        "boltyn": "spirit-of-eirina---dyn066",
        "emperor": "crown-of-dominion---dyn234",
        "hala": "blessing-of-steel---dyn073074075",
        "prism": "invoke-suraya---dyn212",
        "Eirina": "spirit-of-eirina---dyn066",
        "General Nakami": "blessing-of-patience---dyn033034035",
        "Grandmaster Li": "mindstate-of-tiger---dyn048",
        "Jackdaw": "pay-day---dyn123",
        "Jules Teklovossen": "blessing-of-ingenuity---dyn098099100",
        "Suraya, Archangel of Knowledge": "invoke-suraya---dyn212",
    },
    locations=[
        loc.MT_VOLCOR,
        loc.RED_DESERT,
        loc.THE_SHADOW_CRYPTS,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/everfest.md",
    story_type="flavour",
    title="Everfest",
    characters=[
        "viserai",
        people.ASTIER,
        "lexi",
        people.MASTER_MORITA_ART_OF_THE_HAND,
        "kassai",
        "oldhim",
        people.JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS,
        people.EFARIS_BRITTLEBONE,
    ],
    locations=[loc.TEKLO_INDUSTRIES, loc.THE_EVERFEST_CARNIVAL],
    regions=[reg.ARIA, reg.THE_SAVAGE_LANDS],
    groups=[grp.DRACAI, grp.VOLCAI, grp.OLLIN],
    fragments={
        "viserai": "runic-reclamation---evr104",
        "lexi": "this-rounds-on-me---evr160",
        "kassai": "outland-skirmish---evr066067068",
        "oldhim": "steadfast---evr033034035",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/heavy-hitters.md",
    story_type="flavour",
    title="Heavy Hitters",
    characters=[
        "bolfar",
        "olympia",
        "victor-goldmane",
        people.FIGHTMASTER_KOX,
        people.GIANTSLAYER_CRIX,
        people.LUCA_ARENA_CICERONE,
        people.BREWMEISTER_MARV,
        people.MORGA_GRINNING_BOAR_CANTINA_BARMAID,
        people.BEEZY_THE_BRASH,
        people.DUNRIC_VARGAS,
        people.COUNTESS_CAMILLA,
        people.BRUTUS_SUMMA_RUDIS,
        people.MISS_Q,
    ],
    fragments={
        "olympia": "draw-swords---hvy121122123",
        "victor-goldmane": "the-golden-son---hvy059",
    },
    locations=[loc.GRINNING_BOAR_CANTINA],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/rosetta.md",
    story_type="flavour",
    title="Rosetta",
    characters=[
        "verdance",
        "oldhim",
        "florian",
        people.OZRIM,
        people.SERAPHINA,
        people.KAYSIN,
        people.DAVNIR,
        people.YVOR,
        people.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
        loc.VOLTHAVEN,
    ],
    regions=[reg.ARIA],
    groups=[grp.OLLIN],
    fragments={
        "oldhim": "earth-form---ros036037038",
        "florian": "autumns-touch---ros046047048",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/the-hunted.md",
    story_type="flavour",
    title="The Hunted",
    characters=[
        "taipanis",
        "cindra",
        "dromai",
        "emperor",
        "fang",
        "yoji",
        people.CAPTAIN_JUKA,
        people.GENERAL_NAKAMI,
        people.LIEUTENANT_YAMADA,
        people.MAGISTRATE_CHEN,
        people.SAYASHI_CARA,
        people.TETZUO,
        people.VAIL_THE_VAGRANT,
    ],
    locations=[loc.DESHVAHAN, loc.THE_OBSIDIAN_COAST],
    regions=[reg.VOLCOR, reg.THE_PITS],
    groups=[
        grp.ALSHONI,
        grp.CHILDREN_OF_THE_DRAGON,
        grp.DRACAI,
        grp.DUST_RUNNERS,
        grp.EZU,
        grp.SAYASHI,
        grp.VOLCAI,
    ],
    fragments={
        "dromai": "proclaim-vengeance---hnt165",
        "yoji": "hunted-or-hunter---hnt052",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/dusk-till-dawn.md",
    story_type="flavour",
    title="Dusk till Dawn",
    characters=[
        "boltyn",
        people.XAINE_RUNESCRIBE,
        people.TEMPLAR_TIMAERUS,
        people.SOL,
        people.AMIRA_SURANA,
        people.BARUS_BOLDSTRIDE,
        "dorinthea",
        people.BAM_BAM,
        people.LADY_BARTHIMONT,
        people.LORD_SUTCLIFFE,
        people.BLASMOPHET,
        "prism",
    ],
    fragments={"dorinthea": "morlock-hill---dtd209"},
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/high-seas.md",
    story_type="flavour",
    title="High Seas",
    characters=[
        "puffin",
        people.CAPTAIN_GRIT_JABIR,
        people.CAPTAIN_RUE,
        people.CAPTAIN_COODER_OF_THE_SWIFTWATER_WARDEN_COODER,
        people.MUTINOUS_MAGGIE,
        people.SWILLER_SALTBEARD,
        people.CAPTAIN_KLOW,
        people.PEARL_SANDHRI,
        people.CAPTAIN_VANEGULL,
        people.RAY_STINGEYE,
        people.NAILBIT_NARI,
    ],
    locations=[
        loc.DREADFALL_REACH,
        loc.KRAKEN_S_BARREL,
        loc.SELLSHORE_COAST,
        loc.PORT_CONNIVER,
        loc.GOLDEN_PORT,
        loc.PIPER_S_PIER,
        loc.CORALYSI,
        loc.TROPAL_DHANI,
        loc.DAGGER_DOCKS,
        loc.BLACKWATER_STRAIT,
        loc.TERAMUNDR_S_TRIANGLE,
        loc.ANVILHEIM,
        loc.AZURO_KEYS,
        loc.HORIZON_S_MANTLE,
        loc.LOST_LAGOON,
    ],
    regions=[reg.HIGH_SEAS],
    groups=[grp.THE_DHANI_EMPIRE],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/welcome-to-rathe.md",
    story_type="flavour",
    title="Welcome to Rathe",
    characters=[
        "ira",
        "valda",
        people.BARTRAND_THE_BLOODY,
        people.FLANNIGAN,
        people.LENA_BELLE,
        people.LIEUTENANT_TIMAEUS,
        people.MABON,
        people.RAGNAR_FROSTHELM,
        people.SOL,
        people.FYENDAL,
    ],
    regions=[reg.SOLANA, reg.MISTERIA, reg.THE_SAVAGE_LANDS],
    groups=[grp.HAND_OF_SOL],
    fragments={
        "ira": "flic-flak---wtr092093094",
        "valda": "cranial-crush---wtr045",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/xx-non-set-cards.md",
    story_type="flavour",
    title="Non-Set Cards",
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/bright-lights.md",
    story_type="flavour",
    title="Bright Lights",
    characters=[
        "data-doll-mkii",
        "vynnset",
        people.REX_BIGGUN,
        people.HUXLEY,
        people.SYNTHEA_TEKLO,
        people.KYLE,
        people.TASKMASTER_PYRION,
        people.EXECUTIVE_SMYTE,
        people.SANDY_SHOO,
        people.PROFESSOR_MIN,
        people.PROSPECTOR_COGMIRE,
        people.FIGHTMASTER_KOX,
        people.MASTER_MORITA_ART_OF_THE_HAND,
        people.ENFORCER_EESHA,
    ],
    locations=[
        loc.IRON_ASSEMBLY,
        loc.COPPERTOWN,
        loc.CHROME_CAVERNS,
        loc.EIDOLON,
        loc.THE_SPRAWL,
        loc.CENTENNIAL_CONSUMABLES,
    ],
    regions=[reg.METRIX],
    groups=[grp.MENDACITY_MEDIA, grp.COGWERX],
    fragments={
        "vynnset": "slay---evo248",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/README.md",
    story_type="flavour",
    title="Flavour Text",
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/intro.md",
    story_type="flavour",
    title="Flavour Text",
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/tales-of-aria.md",
    story_type="flavour",
    title="Tales of Aria",
    characters=[people.VALGARD_HOARFROST, people.LISHU_CRIMSON_HAZE_VIGILANTE],
    locations=[loc.CANDLEHOLD, loc.BLEAK_EXPANSE, loc.ISENLOFT, loc.VOLTHAVEN, loc.MT_ISEN, loc.THE_FLOW],
    regions=[reg.ARIA],
    groups=[grp.OLLIN, grp.ROSETTA],
    dry_run=True,
)
