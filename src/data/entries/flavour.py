"""Flavour page registrations — one ``db.upsert_story`` call per page.

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
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    characters=[
        "aurora",
        "lexi",
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.ASTREA_QUAZOR,
        people.AURIC_SEERESS,
        people.LORD_SUTCLIFFE,
        people.RUPIUS_AURIC_SCROLLMASTER,
        people.YVOR,
        # New with this set. Kind is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
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

# Monarch's four Heralds are printed without flavour text; the lines the page used
# to carry belong to the promo printings and now live on non-set-cards.md. This
# declaration exists to repoint Themis, Aegis and Avalon off this page — Bellona
# stays, still named by Chiara Suncrest's line on MON081.
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
        # :83 — "Tremor of i'Arathael" (MON254/255/256). The name appears in the
        # card title and nowhere else on the page, so this link exists only under
        # the card-title-as-attestation reading flavour/uprising.md established
        # (2026-08-21). It is the one already-registered flavour page that reading
        # changes; Anvilheim and Siren are named in flavour *text* elsewhere and
        # were plain missed links, not consequences of the precedent.
        #
        # `locations=` is new on this call. It deletes nothing: monarch.md carried
        # no location links at all. i'Arathael's row has an empty region and the
        # constant names none, so the id does not fork.
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
    # Both are card titles and nothing else: :3 — "Yorick, Weaver of Tales"
    # (LSS004) and :57 — "Squizzy & Floof" (HER100), each printed with no flavour
    # text under it. Both are hero rows, so this is the card-title reading applied
    # to a hero slug rather than to a registry (2026-08-21).
    #
    # The hero slugs are new on this call and delete nothing — the page had no
    # hero links. The slug is `squizzyfloof`, not the display name.
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
        # Already curated — named here only to link them to this page. The DB holds
        # the fightmasters under their bare names, not the "Fightmaster X" form the
        # cards use.
        people.BATBITER,
        people.EMEVIERE,
        people.FIGHTMASTER_KOX,
        people.FIGHTMASTER_RUSTY,
        people.LUCA_ARENA_CICERONE,
        people.MOLOCA,
        people.SLAPSTICK_SAL,
        people.SPEAKEASY,
        # New with this set. Kind is unattested in the flavour text.
        people.FOREMAN_PEBB,
        people.FUGGER_GRIMES,
        people.HELX,
        people.SALVADOR_STALLION,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.DEN_OF_BEASTS,
        loc.GRINNING_BOAR_CANTINA,
        # A Deathmatch venue, distinct from "The Maw" in the Pits. Region is left
        # blank to match its siblings (The Undercroft, The Moat, Arena Barracks).
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
# Glorytown Gladiators, Jungle Slayers, Mythmakers, Prowlers, Wild Wonders

db.upsert_story(
    path="src/flavour/mastery-pack-guardian.md",
    story_type="flavour",
    title="Mastery Pack Guardian",
    characters=[
        "fai",
        "valda",
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        # MPG029 prints "Archangel Aegis"; that is a new epithet for the Herald of
        # Protection already registered under her Monarch title, not a new character.
        people.AEGIS_THE_SHIELD_OF_LIGHT,
        # New with this set. Kind is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
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
        # Already curated — named here only to link them to this page.
        # MPW048 prints "Lieutenant Farris"; Pride of the Ironsongs introduces the
        # same Solanian lieutenant on the same Savage Lands frontier.
        people.FARRIS,
        people.FIGHTMASTER_KOX,
        people.FIGHTMASTER_RUSTY,
        people.LIEUTENANT_TIMAEUS,
        # New with this set. Kind is unattested in the flavour text.
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
        # Was loc.FIDDLER_S_GREEN — folded into Coralysi as an alias (R6).
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
        people.WHISPERS_OF_XERYS,
    ],
    locations=[
        loc.SHADOWREALM,
    ],
    regions=[
        reg.SOLANA,
    ],
    dry_run=True,
)

# ---------------------------------------------------------------------------
# Registered 2026-08-20 to unstrand five NPC epithets (R4, stage 3).
#
# All four pages already carried links, created as a side effect of other
# upserts rather than by any declaration, so these registrations are additive
# over what was there: every existing link is named again, because a *present*
# kwarg replaces the junction wholesale and an omitted entity would read as a
# deletion. Entities the pages name that have no catalogue constant are listed
# per page and left for their own review rather than minted here.
# ---------------------------------------------------------------------------

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
    # Preserved, not re-derived. An omitted fragments= CLEARS the stored
    # anchors rather than leaving them alone, which the dry run caught.
    fragments={"arakni-huntsman": "back-stab---out015016017"},
    locations=[
        loc.FLOATING_DOJO,
        loc.MOJIRE,
        loc.SKYLARK_PEAK,
    ],
    regions=[reg.THE_PITS],
    # Akuo is styled "Spider Operative" on OUT143.
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
    # TODO: needs review — Eye of Ophidia, Arknight, Velocitator 60-T.
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
    # CRU024 writes "Isen's Peak", which is Mt. Isen's alias (R6) — the first
    # link the alias table has earned rather than merely recorded.
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
    # TODO: needs review — Wakuro (one mention, too thin to type).
    dry_run=True,
)

# Registered 2026-08-20 to give Maela Fairmind's membership its own citation. It
# was the page THE_MAELA's member_source had always named, and the only page that
# names her — but nothing declared it, so she had no story link at all and the
# citation pointed at a page the graph did not connect her to. Registering it also
# closes people.KARALYN, the last npcs.csv row with no catalogue constant.
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
        # X06: Kox is a hero and this page writes "Fightmaster Kox". The character row
        # is what the other nine pages link, so this one joins them rather than
        # starting a tenth spelling of the same person. Stage 6 re-points all ten.
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
        # "those Rosetta willing to embrace it" (PEN219) is the *people*, and the
        # link is to the *order*. Both rows exist and carry a word-for-word
        # identical summary; `kind` is not a declaration parameter, so the
        # group is the only reachable one. Forced, not chosen. Stage 6/7.
        grp.ROSETTA,
        # Thin, and kept: "These Teklo monsters" (PEN075) is adjectival and names
        # the brand rather than the company as an actor, but "Teklo" denotes only
        # this company.
        grp.TEKLO_INDUSTRIES,
        grp.THE_SPIDER,
    ],
    # Dropped 2026-08-21 by review, both too thin to stand (the user's call):
    #   DISCIPLES_OF_PAIN — PEN195 reads "The Disciple of Pain sought dominion,
    #     but in desperance *he* languished". Singular, and "he": that is one
    #     person, not the order. If it evidences anything it evidences an ordinary character.
    #   MUGENSHI_CLAN — the page gives only "- Mugenshi proverb". A proverb's
    #     attribution names a culture; the row is category="clan" with no notes.
    # Not dropped, but noted: the same sentence that gives "our Gemini" also gives
    # "our Inquisitors", and that got no link because no Inquisitors row exists.
    # What a page links is shaped by what the registry already holds.
    # Orihon of Mystic Tenets is quoted twice (PEN269, PEN273). It matches no row
    # in any registry because it is a *card name*, not a character name:
    # flavour/part-the-mistveil.md:41 lists it as MST080, and the digital-tiles
    # page has it as a heading. The character behind it would be "Orihon"; the
    # subtitle is the card's. Deliberately left out (the user's call, 2026-08-20).
    # Recorded in the plan as well as here, because a comment is deletable and
    # this decision has already been re-litigated once.
    dry_run=True,
)

# Registered 2026-08-21, stage 5. This is the page that gives eleven of the twelve
# dragons a database row: they existed in character-groups.md and nowhere in the
# data, and `kind.DRAGON` held only Miragai.
#
# **The dragons are named by the card titles, not the flavour text** — "Invoke
# Azvolai" over "The dragon of choice, said to guard the crossroads of Sandikai."
# Every one of the twelve is like that. Counting a card title as attestation is the
# user's call (2026-08-21) and it is what makes this registration worth doing; read
# without it, the page names no dragon at all. The same reading is what admits
# people.FYENDAL, from "Fyendal's Fighting Spirit" (UPR194).
#
# Deliberately left out under that same reading, because neither has a row anywhere
# and neither is described by its own flavour line: `Vipox` (UPR188, a Spider quote
# about something else) and the `ice nymph` of UPR144 — lower-case, generic, and in
# the body rather than a title. Both the user's call.
db.upsert_story(
    path="src/flavour/uprising.md",
    story_type="flavour",
    title="Uprising",
    characters=[
        "dromai",
        "fai",
        "victor-goldmane",
        # "The dragon of devastation, said to serve only the Aesir of Flames"
        # (UPR006). The card names the epithet; the row is Infernai, renamed
        # 2026-08-26 with "Aesir of Flames" kept as the epithet it always was.
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
        # "The sun is setting on this Dynasty. Tomorrow we rise up, my son."
        people.YUNKAI,
    ],
    # Not decoration. All three were already stored, and the first dry run of this
    # declaration reported them as "-> cleared": hero fragments are replace-semantic,
    # so omitting them is a deletion. Each is the card section that quotes its hero —
    # "Burn Away" for Dromai, "Lava Vein Loyalty" for Fai, "That All You Got?" for
    # Victor Goldmane. They were seeded rather than declared, so this is the first
    # time upsert_story has validated them against the real headings.
    fragments={
        "dromai": "burn-away---upr094",
        # Corrected 2026-08-21. The seeded value was `lava-vein-loyalty---upr069`,
        # which is not a heading on the page — the card prints three numbers, so the
        # real id is the full run. The third stale fragment found this way; stage 3
        # found two, and nothing validates them except upsert_story on write, so the
        # 195 declarations that have never been written may hide more.
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
        # Not named in a single line of this page. Included because the page is the
        # Volcai uprising against the Dracai and three of the seven locations above
        # sit in Volcor — the one region here carried by implication rather than by
        # name, and flagged so a later reader can disagree with it.
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
        # New link — DYN212 "Invoke Suraya" is spoken by Prism but Prism was not
        # previously linked to this page at all.
        "prism",
        # New link. Named only in the DYN066 card title "Spirit of Eirina"; the
        # quote itself ("Her spirit inside me, always." - Boltyn) is about her.
        people.EIRINA,
        people.GENERAL_NAKAMI,
        people.GRANDMASTER_LI,
        people.JACKDAW,
        people.JULES_TEKLOVOSSEN,
        # New link. Named only in the DYN212 card title "Invoke Suraya"; the
        # flavour text ("Enlightened one, illuminate our path with your
        # knowledge...") addresses her by her existing epithet.
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
        # New link. "Mt. Volcor" (DYN085/086/087, "Visit the Imperial Forge") —
        # exact-name match to the existing catalogue constant, region Volcor.
        loc.MT_VOLCOR,
        # New link. "The Red Desert of Volcor" (DYN003) — exact-name match to
        # the existing catalogue constant, region Volcor.
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
        # seeded value was 'outland-skirmish---evr066' (truncated); real heading covers EVR066/067/068
        "kassai": "outland-skirmish---evr066067068",
        # seeded value was 'steadfast---evr033' (truncated); real heading covers EVR033/034/035
        "oldhim": "steadfast---evr033034035",
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/heavy-hitters.md",
    story_type="flavour",
    title="Heavy Hitters",
    characters=[
        "bolfar",  # named on page ("Wage Might" speaker) but not seeded; bare slug — matches hero list exactly
        "olympia",  # "Draw Swords" speaker; matches hero list exactly (no qualifying title on this page)
        "victor-goldmane",  # "The Golden Son" speaker; matches hero list exactly (no qualifying title on this page)
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
        "olympia": "draw-swords---hvy121122123",  # seeded id 'draw-swords---hvy121' was stale (truncated); real heading id has full HVY121/122/123 range
        "victor-goldmane": "the-golden-son---hvy059",
    },
    locations=[loc.GRINNING_BOAR_CANTINA],  # named inside Morga's title
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/rosetta.md",
    story_type="flavour",
    title="Rosetta",
    characters=[
        "verdance",
        "oldhim",
        "florian",  # heroes: bare slugs
        people.OZRIM,
        people.SERAPHINA,
        people.KAYSIN,
        people.DAVNIR,
        people.YVOR,  # named in passing: "Davnir's lessons"/"Kin of Davnir" (Blossoming Decay, Earth Form), "great Yvor's fall"/"energy of Yvor" (Heaven's Claws, Lightning Form)
        people.QUEEN_OF_CANDLEHOLD,  # speaker "Queen of the Rosetta" — see Ambiguities
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,  # named in Autumn's Touch, Cadaverous Tilling, Harvest Season
        loc.VOLTHAVEN,  # "Volthaven was born" (Heaven's Claws)
    ],
    regions=[reg.ARIA],
    groups=[grp.OLLIN],  # "The mighty Ollin once fought alongside the Kin of Davnir" (Earth Form)
    fragments={
        "oldhim": "earth-form---ros036037038",  # seeded id 'earth-form---ros036' is stale; corrected to match the real heading id
        "florian": "autumns-touch---ros046047048",  # seeded id 'autumns-touch---ros046' is stale; corrected to match the real heading id
    },
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/the-hunted.md",
    story_type="flavour",
    title="The Hunted",
    characters=[
        "taipanis",  # not seeded, but named twice as speaker (Imperial Intent, Pledge Fealty); is a hero slug
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
        grp.CHILDREN_OF_THE_DRAGON,  # :59 "Pledge Fealty" — an existing group, not a poetic name
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
        "puffin",  # named speaker (Cogwerx Workshop), matches hero slug — not seeded
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
        loc.ANVILHEIM,  # named (Nimby), not seeded
        loc.AZURO_KEYS,  # new
        loc.HORIZON_S_MANTLE,  # new
        loc.LOST_LAGOON,  # new
    ],
    regions=[reg.HIGH_SEAS],
    groups=[
        grp.THE_DHANI_EMPIRE
    ],  # "Dhani Empire" named directly (Portside Exchange, Saltwater Swell, Sunken Treasure)
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
        people.SOL,  # not seeded; named directly ("blessing of Sol", Warrior's Valor) — existing constant
        people.FYENDAL,  # card titles "Heart of Fyendal"/"Tome of Fyendal" — card-title-as-attestation, as on monarch.md
    ],
    regions=[reg.SOLANA, reg.MISTERIA, reg.THE_SAVAGE_LANDS],
    groups=[grp.HAND_OF_SOL],  # named directly ("A warrior of the Hand of Sol...", Steelblade Shunt)
    fragments={
        "ira": "flic-flak---wtr092093094",  # seeded id 'flic-flak---wtr092' is stale; real heading id verified against built HTML
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
        "data-doll-mkii",  # hero slug; page's byline reads "Data Doll MKI" — see Ambiguities
        "vynnset",  # hero slug
        people.REX_BIGGUN,
        people.HUXLEY,
        people.SYNTHEA_TEKLO,
        people.KYLE,
        people.TASKMASTER_PYRION,
        people.EXECUTIVE_SMYTE,
        people.SANDY_SHOO,
        people.PROFESSOR_MIN,
        people.PROSPECTOR_COGMIRE,
        people.FIGHTMASTER_KOX,  # page reads "Kox, Deathmatch Fightmaster" — see Ambiguities
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
        "vynnset": "slay---evo248",  # seeded key was display name 'Vynnset'; rekeyed to match characters= slug
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
    # :44 "the Einion" — possibly the people of Enion; held for the user. grp.GUARDIANS also held.
    groups=[grp.OLLIN, grp.ROSETTA],
    dry_run=True,
)
