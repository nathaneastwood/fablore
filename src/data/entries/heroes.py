"""Hero page registrations — one ``db.upsert_story`` call per page.

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
    path="src/heroes-of-rathe/aurora-about.md",
    story_type="heroes-of-rathe",
    title="Aurora",
    heroes=["aurora"],
    locations=[
        loc.ENION,
        loc.VOLTHAVEN,
        loc.VALAHAI,
    ],
    weapons=["star-fall", "scorpio-comet-tail"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/oscilio-about.md",
    story_type="heroes-of-rathe",
    title="Oscilio",
    heroes=["oscilio"],
    locations=[
        loc.ENION,
    ],
    regions=[reg.ARIA],
    weapons=["volzar-the-lightning-rod"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zyggy-about.md",
    story_type="heroes-of-rathe",
    title="Zyggy Starlight",
    heroes=["zyggy", "oscilio"],
    regions=[reg.NEBULUS_RIFT],
    locations=[
        loc.VALAHAI,
        loc.AURIC_KEEP,
    ],
    weapons=["aphrodias"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/blaze-about.md",
    story_type="heroes-of-rathe",
    title="Blaze",
    heroes=["blaze"],
    regions=[reg.VOLCOR],
    locations=[
        loc.IMPERIAL_PALACE,
    ],
    fauna=[fauna.FLARE_DEER],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dorinthea-about.md",
    story_type="heroes-of-rathe",
    title="Dorinthea",
    heroes=["dorinthea", "hala"],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.HAND_OF_SOL,
        loc.THE_GOLDEN_FIELDS,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    weapons=["dawnblade", "dawnblade-resplendent"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/baalghor-about.md",
    story_type="heroes-of-rathe",
    title="Baalghor",
    source_link="https://fabtcg.com/hero/baalghor/",
    heroes=["baalghor"],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
        loc.THE_ABYSS,
    ],
    regions=[reg.DEMONASTERY],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-about.md",
    story_type="heroes-of-rathe",
    title="Arakni, Huntsman",
    heroes=["arakni-huntsman"],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/benji-about.md",
    story_type="heroes-of-rathe",
    title="Benji, The Piercing Wind",
    heroes=["benji"],
    locations=[
        loc.GORGE_OF_A_THOUSAND_WINDS,
        loc.MISTCLOAK_GULLY,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)
# TODO: group — Mugenshi Clan (see Hints table)

db.upsert_story(
    path="src/heroes-of-rathe/bravo-about.md",
    story_type="heroes-of-rathe",
    title="Bravo, Showstopper",
    heroes=["bravo"],
    locations=[
        loc.FRACTAL_SCAR,
        loc.LEGENDARIUM,
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)
# TODO: group — the Guardians (see Hints table)

db.upsert_story(
    path="src/heroes-of-rathe/briar-about.md",
    story_type="heroes-of-rathe",
    title="Briar, Warden of Thorns",
    heroes=["briar"],
    locations=[loc.CANDLEHOLD],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/cindra-about.md",
    story_type="heroes-of-rathe",
    title="Cindra, Dracai of Retribution",
    heroes=["cindra", "emperor"],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dromai-about.md",
    story_type="heroes-of-rathe",
    title="Dromai, Ash Artist",
    heroes=["dromai"],
    locations=[loc.MT_VOLCOR],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/emperor-about.md",
    story_type="heroes-of-rathe",
    title="Emperor, Dracai of Aesir",
    heroes=["emperor"],
    locations=[loc.MT_VOLCOR],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/enigma-about.md",
    story_type="heroes-of-rathe",
    title="Enigma, Ledger of Ancestry",
    heroes=["enigma"],
    locations=[loc.LUNAR_TEMPLE],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/fai-about.md",
    story_type="heroes-of-rathe",
    title="Fai, Rising Rebellion",
    heroes=["fai"],
    npcs=[npc.EUN],
    locations=[
        loc.ASHVAHAN,
        loc.RED_DESERT,
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/ira-about.md",
    story_type="heroes-of-rathe",
    title="Ira, Crimson Haze",
    heroes=["ira"],
    locations=[
        loc.VALLEY_OF_BLOSSOMS,
        loc.IKARU,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/lexi-about.md",
    story_type="heroes-of-rathe",
    title="Lexi, Livewire",
    heroes=["lexi"],
    locations=[
        loc.ENION,
        loc.VOLTHAVEN,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/viserai-about.md",
    story_type="heroes-of-rathe",
    title="Viserai, Rune Blood",
    heroes=["viserai"],
    npcs=[npc.LORD_SUTCLIFFE],
    regions=[reg.DEMONASTERY, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/azalea-about.md",
    story_type="heroes-of-rathe",
    title="Azalea",
    heroes=["azalea"],
    locations=[
        loc.BLACKJACK_S_TAVERN,
    ],
    regions=[reg.THE_PITS],
    weapons=["death-dealer"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/boltyn-about.md",
    story_type="heroes-of-rathe",
    title="Boltyn",
    heroes=["boltyn"],
    npcs=[
        npc.EIRINA,
        npc.AIOS,
        npc.FYANNA_REDMOOR_BOLTYN_S_COUSIN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.MINERVA_THEMIS,
    ],
    locations=[
        loc.THE_NORTHERN_REALMS,
        loc.HAND_OF_SOL,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_SOLARIUM,
        loc.OCTOMILITIA,
    ],
    regions=[reg.SOLANA, reg.DEMONASTERY],
    dry_run=True,
)
# TODO: group — Sisters of Octothesia

db.upsert_story(
    path="src/heroes-of-rathe/fang-about.md",
    story_type="heroes-of-rathe",
    title="Fang",
    heroes=["fang", "emperor"],
    regions=[reg.VOLCOR],
    dry_run=True,
)
# TODO: group — Children of the Dragon

db.upsert_story(
    path="src/heroes-of-rathe/hala-about.md",
    story_type="heroes-of-rathe",
    title="Hala",
    heroes=["hala"],
    npcs=[
        npc.GRAND_MAGISTER_THE_STEADFAST,
    ],
    locations=[
        loc.OCTOMILITIA,
        loc.OCTOTISTA,
        loc.GOLDENHELM_KEEP,
        loc.AMPHITHEATRE,
        loc.SOLSTICE_OF_LAURELS,
    ],
    regions=[
        reg.SOLANA,
        reg.THE_SAVAGE_LANDS,
        reg.DEMONASTERY,
    ],
    weapons=["zenith-blade"],
    dry_run=True,
)
# TODO: group — Children of the Light

db.upsert_story(
    path="src/heroes-of-rathe/katsu-about.md",
    story_type="heroes-of-rathe",
    title="Katsu",
    heroes=["katsu"],
    locations=[
        loc.MUGENSHI_GORGE,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kayo-about.md",
    story_type="heroes-of-rathe",
    title="Kayo",
    heroes=["kayo", "kassai"],
    locations=[
        loc.DEATHMATCH_ARENA,
        loc.THE_BADLANDS,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)
# TODO: group — Prowlers

db.upsert_story(
    path="src/heroes-of-rathe/melody-about.md",
    story_type="heroes-of-rathe",
    title="Melody",
    heroes=["melody"],
    locations=[
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/oldhim-about.md",
    story_type="heroes-of-rathe",
    title="Oldhim",
    heroes=["oldhim"],
    locations=[
        # Open question: should ISENLOFT carry lore_fragment="mount-isen"? Uncertain
        # match. It is a one-line edit in catalogue/locations.py now, and it would
        # apply to every page linking Isenloft rather than to this one — which is
        # the point. See also loc.MT_ISEN, which may be the same place.
        loc.ISENLOFT,
    ],
    regions=[reg.ARIA],
    equipment=["stalagmite-bastion-of-isenloft"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/puffin-about.md",
    story_type="heroes-of-rathe",
    title="Puffin",
    heroes=["puffin"],
    npcs=[
        npc.POLLY_CRANKA,
        npc.CAPTAIN_RUE,
    ],
    locations=[
        loc.PIPER_S_PIER,
        loc.DREADFALL_REACH,
    ],
    regions=[reg.HIGH_SEAS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/shiyana-about.md",
    story_type="heroes-of-rathe",
    title="Shiyana",
    heroes=["shiyana"],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/verdance-about.md",
    story_type="heroes-of-rathe",
    title="Verdance",
    heroes=["verdance", "florian"],
    npcs=[
        npc.DAVNIR,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/vynnset-about.md",
    story_type="heroes-of-rathe",
    title="Vynnset",
    heroes=["vynnset"],
    npcs=[
        npc.NASRETH,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-5l!p3d-7hru-7h3-cr4x-about.md",
    story_type="heroes-of-rathe",
    title="Arakni, Solitary Confinement",
    heroes=["arakni-solitary-confinement"],
    npcs=[
        npc.DR_KREST_MORTIMER_THE_FIXER,
    ],
    locations=[
        loc.SOUTHMAW,
    ],
    regions=[reg.THE_PITS],
    dry_run=True,
)
# TODO: faction — the Spider (see Hints table)

db.upsert_story(
    path="src/heroes-of-rathe/betsy-about.md",
    story_type="heroes-of-rathe",
    title="Betsy, Skin in the Game",
    heroes=["betsy"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/chane-about.md",
    story_type="heroes-of-rathe",
    title="Chane, Bound by Shadow",
    heroes=["chane"],
    locations=[
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/genis-about.md",
    story_type="heroes-of-rathe",
    title="Genis Wotchuneed",
    heroes=["genis"],
    locations=[
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/iyslander-about.md",
    story_type="heroes-of-rathe",
    title="Iyslander, Stormbind",
    heroes=["iyslander"],
    locations=[
        loc.BLEAK_EXPANSE,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/jarl-about.md",
    story_type="heroes-of-rathe",
    title="Jarl Vetreiði",
    heroes=["jarl"],
    locations=[
        loc.ISENLOFT,
        loc.ISEN_RANGES,
    ],
    regions=[reg.ARIA],
    weapons=["summit-the-unforgiving"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kano-about.md",
    story_type="heroes-of-rathe",
    title="Kano, Dracai of Aether",
    heroes=["kano"],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/nuu-about.md",
    story_type="heroes-of-rathe",
    title="Nuu, Alluring Desire",
    heroes=["nuu"],
    locations=[
        loc.MISTCLOAK_GULLY,
        loc.MISTCLOAK_TEAHOUSE,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)
# TODO: faction — Vipressa (see Hints table)

db.upsert_story(
    path="src/heroes-of-rathe/prism-about.md",
    story_type="heroes-of-rathe",
    title="Prism, Sculptor of Arc Light",
    heroes=["prism", "the-librarian"],
    npcs=[
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
    ],
    locations=[
        loc.LIBRARY_OF_ILLUMINATION,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/terra-about.md",
    story_type="heroes-of-rathe",
    title="Terra",
    heroes=["terra"],
    locations=[
        loc.THE_KORSHEM,
        loc.MOUNT_HEROIC,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/tuffnut-about.md",
    story_type="heroes-of-rathe",
    title="Tuffnut, Bumbling Hulkster",
    heroes=["tuffnut"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/uzuri-about.md",
    story_type="heroes-of-rathe",
    title="Uzuri, Switchblade",
    heroes=["uzuri"],
    regions=[
        reg.METRIX,
        reg.MISTERIA,
        reg.THE_PITS,
    ],
    dry_run=True,
)
# TODO: faction — the Spider (see Hints table on arakni-5l!p3d-7hru-7h3-cr4x-about.md)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-marionette-about.md",
    story_type="heroes-of-rathe",
    title="Arakni, Marionette",
    heroes=["arakni-web-of-deceit"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/brevant-about.md",
    story_type="heroes-of-rathe",
    title="Brevant, Civic Protector",
    heroes=["brevant"],
    regions=[reg.SOLANA],
    locations=[
        loc.HAND_OF_SOL,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/florian-about.md",
    story_type="heroes-of-rathe",
    title="Florian, Rotwood Harbinger",
    heroes=["florian"],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/frankie-about.md",
    story_type="heroes-of-rathe",
    title="Frankie, Make Ends Meat",
    heroes=["frankie"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/gravy-about.md",
    story_type="heroes-of-rathe",
    title="Gravy Bones, Shipwrecked Looter",
    heroes=["gravy"],
    locations=[
        loc.DREADFALL_REACH,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kavdaen-about.md",
    story_type="heroes-of-rathe",
    title="Kavdaen, Trader of Skins",
    heroes=["kavdaen"],
    regions=[reg.THE_PITS],
    locations=[
        loc.THE_MAW,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/levia-about.md",
    story_type="heroes-of-rathe",
    title="Levia, Shadowborn Abomination",
    heroes=["levia"],
    npcs=[
        npc.LADY_BARTHIMONT,
    ],
    regions=[reg.DEMONASTERY],
    locations=[
        loc.I_ARATHAEL,
        loc.BELLOWS_OF_HELL,
        loc.DOOMSDAY_PEAK,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/rhinar-about.md",
    story_type="heroes-of-rathe",
    title="Rhinar, Reckless Rampage",
    heroes=["rhinar"],
    regions=[reg.THE_SAVAGE_LANDS],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/scurv-about.md",
    story_type="heroes-of-rathe",
    title="Scurv, Stowaway",
    heroes=["scurv"],
    npcs=[
        npc.STICKY_FINGERS,
    ],
    locations=[
        loc.GRAYSTONE_PENITENTIARY,
        loc.PIPER_S_PIER,
    ],
    food_drink=[food.GOLDKISS_RUM],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/teklovossen-about.md",
    story_type="heroes-of-rathe",
    title="Teklovossen, Esteemed Magnate",
    heroes=["teklovossen"],
    regions=[reg.METRIX],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.PLUMVEX_PIPES_FACTORY,
        loc.COGWERX_CONGLOMERATE,
        loc.IRON_ASSEMBLY,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/valda-about.md",
    story_type="heroes-of-rathe",
    title="Valda Brightaxe",
    heroes=["valda"],
    npcs=[
        npc.BRAUMEISTER_BALEN,
    ],
    regions=[reg.ARIA],
    locations=[
        loc.THE_EVERFEST_CARNIVAL,
        loc.MIGHT_N_MEAD,
        loc.THE_KORSHEM,
        loc.THE_FLOW,
        loc.LARINKMORTH,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/yoji-about.md",
    story_type="heroes-of-rathe",
    title="Yoji, Royal Protector",
    heroes=["yoji"],
    npcs=[
        npc.LORD_WIZARD_CHIYO,
    ],
    regions=[reg.VOLCOR],
    locations=[
        loc.ASHVAHAN,
        loc.GRAND_ARCHWAY,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dash-about.md",
    story_type="heroes-of-rathe",
    title="Dash, Inventor Extraordinaire",
    heroes=["dash", "data-doll-mkii", "maxx", "teklovossen"],
    npcs=[
        npc.JULES_TEKLOVOSSEN,
    ],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.MIDTOWN_MARKETS,
        loc.IRON_ASSEMBLY,
        loc.ROSARIO_HILLS,
        loc.LOWLAKE,
    ],
    regions=[reg.METRIX],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/data-doll-mkii-about.md",
    story_type="heroes-of-rathe",
    title="Data Doll, MKII",
    heroes=["data-doll-mkii"],
    locations=[
        loc.IRON_ASSEMBLY,
    ],
    regions=[reg.METRIX],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kassai-about.md",
    story_type="heroes-of-rathe",
    title="Kassai, Cintari Sellsword",
    heroes=["kassai"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/lyath-about.md",
    story_type="heroes-of-rathe",
    title="Lyath Goldmane, Vile Savant",
    heroes=["lyath", "victor-goldmane"],
    npcs=[
        npc.BLOODWORTH_GOLDMANE,
        npc.TARA_VANGELD,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.THE_NORTHERN_REALMS,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)
# TODO: group — VanGeld clan

db.upsert_story(
    path="src/heroes-of-rathe/marlynn-about.md",
    story_type="heroes-of-rathe",
    title="Marlynn, Treasure Hunter",
    heroes=["marlynn"],
    npcs=[
        npc.CAPTAIN_COODER_OF_THE_SWIFTWATER_WARDEN_COODER,
    ],
    fauna=[fauna.KRAKEN],
    regions=[reg.HIGH_SEAS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/maxx-about.md",
    story_type="heroes-of-rathe",
    title="Maxx 'The Hype' Nitro",
    heroes=["maxx"],
    locations=[
        loc.COGWERX_CONGLOMERATE,
    ],
    weapons=["banksy"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/olympia-about.md",
    story_type="heroes-of-rathe",
    title="Olympia, Prized Fighter",
    heroes=["olympia"],
    npcs=[
        npc.COX,
    ],
    locations=[
        loc.DEATHMATCH_ARENA,
        loc.THE_MOAT,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/other.md",
    story_type="heroes-of-rathe",
    title="Others",
    heroes=["ruudi", "taipanis", "taylor", "yorick"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/pleiades-about.md",
    story_type="heroes-of-rathe",
    title="Pleiades, Superstar",
    heroes=["pleiades"],
    locations=[
        loc.THE_NORTHERN_REALMS,
        loc.GOUGEMOOR,
    ],
    dry_run=True,
)
# TODO: group — House Ashwood
# TODO: group — House Goldmane

db.upsert_story(
    path="src/heroes-of-rathe/riptide-about.md",
    story_type="heroes-of-rathe",
    title="Riptide, Lurker of the Deep",
    heroes=["riptide"],
    locations=[
        loc.SEETHESIDE_DOCKS,
    ],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/victor-goldmane-about.md",
    story_type="heroes-of-rathe",
    title="Victor Goldmane, High and Mighty",
    heroes=["victor-goldmane"],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zen-about.md",
    story_type="heroes-of-rathe",
    title="Zen, Tamer of Purpose",
    heroes=["zen"],
    regions=[reg.MISTERIA],
    dry_run=True,
)
