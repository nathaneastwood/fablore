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
    fauna,
    flora,
    food_drink as food,
    groups as grp,
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
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    heroes=["aurora", "lexi"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.ASTREA_QUAZOR,
        npc.AURIC_SEERESS,
        npc.LORD_SUTCLIFFE,
        npc.RUPIUS_AURIC_SCROLLMASTER,
        npc.YVOR,
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        npc.DARYAS_NIMBUS,
        npc.FREYA_ELDINGSTURM,
        npc.MAELA_ISULFV,
        npc.MAELA_SHARENA,
        npc.REZNYR_ELDINGSTURM,
        npc.SKYNDA_FEYSCOUT,
        npc.VYHARA_CLOUDBURST,
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
    heroes=["prism"],
    hero_fragments={"prism": "celestial-cataclysm---mon062"},
    npcs=[
        npc.AMIRA_SURANA,
        npc.ASTRA_MORENA,
        npc.AUREA_CHAMPION_OF_THE_DAWN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.CHANCELLOR_HELENA_PRIMAVERA,
        npc.CHANCELLOR_HYPATIA,
        npc.CHIARA_SUNCREST,
        npc.DANU_ASHENGUARD,
        npc.ERSEBET,
        npc.GRAND_MAGISTER_THE_RADIANT,
        npc.HARLAND,
        npc.HAROLD_HONEYSETT,
        npc.JACKDAW,
        npc.KIRIGAMI,
        npc.MERLEN_RIVERA,
        npc.NESTUS,
        npc.SANNI,
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        npc.VIDYA_WILLOWMERE,
    ],
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
    # to `heroes` rather than to a registry (2026-08-21).
    #
    # `heroes=` is new on this call and deletes nothing — the page had no hero
    # links. The slug is `squizzyfloof`, not the display name.
    heroes=["squizzyfloof", "yorick"],
    npcs=[
        npc.AEGIS_THE_SHIELD_OF_LIGHT,
        npc.AVALON_MESSENGER_OF_THE_DAWN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.THEMIS_KEEPER_OF_THE_SCALES,
        npc.YVOR,
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
    heroes=["kayo", "lyath", "pleiades", "tuffnut", "victor-goldmane"],
    npcs=[
        # Already curated — named here only to link them to this page. The DB holds
        # the fightmasters under their bare names, not the "Fightmaster X" form the
        # cards use.
        npc.BATBITER,
        npc.EMEVIERE,
        npc.FIGHTMASTER_KOX,
        npc.FIGHTMASTER_RUSTY,
        npc.LUCA_ARENA_CICERONE,
        npc.MOLOCA,
        npc.SLAPSTICK_SAL,
        npc.SPEAKEASY,
        # New with this set. Species is unattested in the flavour text.
        npc.FOREMAN_PEBB,
        npc.FUGGER_GRIMES,
        npc.HELX,
        npc.SALVADOR_STALLION,
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
    heroes=["fai", "valda"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        # MPG029 prints "Archangel Aegis"; that is a new epithet for the Herald of
        # Protection already registered under her Monarch title, not a new character.
        npc.AEGIS_THE_SHIELD_OF_LIGHT,
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        npc.MAELA_ONE_EYE,
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
    npcs=[
        # Already curated — named here only to link them to this page.
        # MPW048 prints "Lieutenant Farris"; Pride of the Ironsongs introduces the
        # same Solanian lieutenant on the same Savage Lands frontier.
        npc.FARRIS,
        npc.FIGHTMASTER_KOX,
        npc.FIGHTMASTER_RUSTY,
        npc.LIEUTENANT_TIMAEUS,
        # New with this set. Species is unattested in the flavour text.
        npc.CAPTAIN_SHEVEZ,
        npc.INQUISITOR_ARICIA,
        npc.LUCILLA_THE_SETTING_SUN,
        npc.TASHA_OF_DESHVAHAN,
        npc.THE_BASTION,
        npc.VANIK_SILVERTOOTH,
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
    heroes=["malice", "chane", "levia", "vynnset", "viserai"],
    npcs=[
        npc.BLASMOPHET,
        npc.SOL,
        npc.ARBITER_MAGISTER_OF_JUSTICE,
        npc.WHISPERS_OF_XERYS,
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
    heroes=["arakni-huntsman"],
    # Preserved, not re-derived. An omitted hero_fragments= CLEARS the stored
    # anchors rather than leaving them alone, which the dry run caught.
    hero_fragments={"arakni-huntsman": "back-stab---out015016017"},
    npcs=[
        npc.ACHLYS_HAG_OF_MOJIRE,
        npc.AKUO,
        npc.DR_KREST_MORTIMER_THE_FIXER,
        npc.LENA_BELLE,
        npc.OTMAR,
        npc.SURAJ_THE_ORACLE,
    ],
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
    heroes=["azalea", "dash", "kano"],
    hero_fragments={"azalea": "three-of-a-kind---arc044", "kano": "blazing-aether---arc118"},
    npcs=[
        npc.ATEIA,
        npc.DR_KREST_MORTIMER_THE_FIXER,
        npc.ELDON_LOST_KNIGHT,
        npc.ELIAS_EDGECOMBE,
        npc.GRAHAM_THE_GALLANT,
        npc.JEEVES,
        npc.LIEUTENANT_YAMADA,
        npc.MAXWELL,
        npc.VERA,
        npc.XAINE_RUNESCRIBE,
    ],
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
    heroes=["hala", "jarl", "kano", "teklovossen"],
    hero_fragments={
        "hala": "unified-decree---cru083",
        "kano": "aetherize---cru164",
        "teklovossen": "teklovossens-workshop---cru115116117",
    },
    npcs=[
        npc.BUTCHER_JEK,
        npc.GREENBIRD,
        npc.JACKDAW,
        npc.JULES_TEKLOVOSSEN,
        npc.LINNEA_MISTRESS_OF_MALADY,
        npc.SEPTUS,
        npc.SPOKES,
        npc.THUK,
        npc.TOGARK_THE_WRANGLER,
    ],
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
    heroes=["enigma", "nuu", "zen"],
    hero_fragments={"enigma": "deep-blue-sea---mst084"},
    npcs=[
        npc.ANHE_KOTORI_WAVEBENDER,
        npc.DAN_LU_KOTORI_GALEWARDEN,
        npc.GUDO_MISTWARD_PILGRIM,
        npc.HIREI,
        npc.KOUKI,
        npc.MASTER_MORITA_ART_OF_THE_HAND,
        npc.MIKU,
        npc.NING_KOTORI_MOONSEEKER,
        npc.REINA_SPIRIT_CALLER,
        npc.SHIO,
        npc.SOREN,
        npc.SUMIRE,
        npc.TOHIRO_ETERNAL_SCRIBE,
    ],
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
# closes npc.KARALYN, the last npcs.csv row with no catalogue constant.
db.upsert_story(
    path="src/flavour/compendium-of-rathe.md",
    story_type="flavour",
    title="Compendium of Rathe",
    heroes=["enigma", "florian", "hala", "maxx", "uzuri"],
    npcs=[
        npc.ANARCH_ZEIR,
        npc.APOSTATE,
        npc.BATBITER,
        npc.DAVNIR,
        npc.DR_KREST_MORTIMER_THE_FIXER,
        # X06: Kox is a hero and this page writes "Fightmaster Kox". The NPC row
        # is what the other nine pages link, so this one joins them rather than
        # starting a tenth spelling of the same person. Stage 6 re-points all ten.
        npc.FIGHTMASTER_KOX,
        npc.GALCIA,
        npc.KARALYN,
        npc.MAELA_FAIRMIND,
        npc.SOL,
        npc.THEMIS_KEEPER_OF_THE_SCALES,
        npc.YVOR,
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
        # identical summary; `species` is not a declaration parameter, so the
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
    #     person, not the order. If it evidences anything it evidences an NPC.
    #   MUGENSHI_CLAN — the page gives only "- Mugenshi proverb". A proverb's
    #     attribution names a culture; the row is kind="clan" with no notes.
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
# data, and `sp.DRAGON` held only Miragai.
#
# **The dragons are named by the card titles, not the flavour text** — "Invoke
# Azvolai" over "The dragon of choice, said to guard the crossroads of Sandikai."
# Every one of the twelve is like that. Counting a card title as attestation is the
# user's call (2026-08-21) and it is what makes this registration worth doing; read
# without it, the page names no dragon at all. The same reading is what admits
# npc.FYENDAL, from "Fyendal's Fighting Spirit" (UPR194).
#
# Deliberately left out under that same reading, because neither has a row anywhere
# and neither is described by its own flavour line: `Vipox` (UPR188, a Spider quote
# about something else) and the `ice nymph` of UPR144 — lower-case, generic, and in
# the body rather than a title. Both the user's call.
db.upsert_story(
    path="src/flavour/uprising.md",
    story_type="flavour",
    title="Uprising",
    heroes=["dromai", "fai", "victor-goldmane"],
    # Not decoration. All three were already stored, and the first dry run of this
    # declaration reported them as "-> cleared": hero fragments are replace-semantic,
    # so omitting them is a deletion. Each is the card section that quotes its hero —
    # "Burn Away" for Dromai, "Lava Vein Loyalty" for Fai, "That All You Got?" for
    # Victor Goldmane. They were seeded rather than declared, so this is the first
    # time upsert_story has validated them against the real headings.
    hero_fragments={
        "dromai": "burn-away---upr094",
        # Corrected 2026-08-21. The seeded value was `lava-vein-loyalty---upr069`,
        # which is not a heading on the page — the card prints three numbers, so the
        # real id is the full run. The third stale fragment found this way; stage 3
        # found two, and nothing validates them except upsert_story on write, so the
        # 195 declarations that have never been written may hide more.
        "fai": "lava-vein-loyalty---upr069070071",
        "victor-goldmane": "that-all-you-got---upr189",
    },
    npcs=[
        # "The dragon of devastation, said to serve only the Aesir of Flames"
        # (UPR006). This row is Infernai under his epithet; the rename is stage 7.
        npc.AESIR_OF_FLAMES,
        npc.AZVOLAI,
        npc.CROMAI,
        npc.DOMINIA,
        npc.DRACONA_OPTIMAI,
        npc.FYENDAL,
        npc.KYLORIA,
        npc.MIRAGAI,
        npc.NEKRIA,
        npc.OUVIA,
        npc.THEMAI,
        npc.TOMELTAI,
        npc.VYNSERAKAI,
        npc.YENDURAI,
        # "The sun is setting on this Dynasty. Tomorrow we rise up, my son."
        npc.YUNKAI,
    ],
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
