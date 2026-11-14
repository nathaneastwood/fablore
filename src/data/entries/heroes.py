"""Hero page registrations — one ``db.upsert_story`` call per page.

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
    fauna,
)
from entries.catalogue import (
    food_drink as food,
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
    path="src/heroes-of-rathe/aurora-about.md",
    title="Aurora",
    source_link="https://fabtcg.com/hero/aurora-3/",
    characters=["aurora"],
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
    title="Oscilio",
    source_link="https://fabtcg.com/hero/oscilio-constella-intelligence/",
    characters=["oscilio"],
    locations=[
        loc.ENION,
    ],
    regions=[reg.ARIA],
    weapons=["volzar-the-lightning-rod"],
    groups=[grp.AETHERSCRIBES],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zyggy-about.md",
    title="Zyggy Starlight",
    source_link="https://fabtcg.com/hero/zyggy-starlight/",
    characters=["zyggy", "oscilio"],
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
    title="Blaze",
    source_link="https://fabtcg.com/hero/blaze/",
    characters=["blaze"],
    regions=[reg.VOLCOR],
    locations=[
        loc.IMPERIAL_PALACE,
    ],
    fauna=[fauna.FLARE_DEER],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dorinthea-about.md",
    title="Dorinthea",
    source_link="https://fabtcg.com/hero/dorinthea/",
    characters=["dorinthea", "hala"],
    locations=[
        loc.DIMENXXIONAL_GATEWAY,
        loc.THE_GOLDEN_FIELDS,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    weapons=["dawnblade", "dawnblade-resplendent"],
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/baalghor-about.md",
    title="Baalghor",
    source_link="https://fabtcg.com/hero/baalghor/",
    characters=["baalghor"],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
        loc.THE_ABYSS,
    ],
    regions=[reg.DEMONASTERY],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/malice-about.md",
    title="Malice",
    source_link="https://fabtcg.com/hero/malice/",
    characters=["malice", "viserai"],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-about.md",
    title="Arakni, Huntsman",
    source_link="https://fabtcg.com/hero/arakni-huntsman/",
    characters=["arakni-huntsman"],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/benji-about.md",
    title="Benji, The Piercing Wind",
    source_link="https://fabtcg.com/hero/benji/",
    characters=["benji"],
    locations=[
        loc.GORGE_OF_A_THOUSAND_WINDS,
        loc.MISTCLOAK_GULLY,
    ],
    regions=[reg.MISTERIA],
    groups=[grp.MUGENSHI_CLAN],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/bravo-about.md",
    title="Bravo, Showstopper",
    source_link="https://fabtcg.com/hero/bravo-4/",
    characters=["bravo"],
    locations=[
        loc.FRACTAL_SCAR,
        loc.LEGENDARIUM,
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[reg.ARIA],
    groups=[grp.GUARDIANS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/briar-about.md",
    title="Briar, Warden of Thorns",
    source_link="https://fabtcg.com/hero/briar/",
    characters=["briar"],
    locations=[loc.CANDLEHOLD],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/cindra-about.md",
    title="Cindra, Dracai of Retribution",
    source_link="https://fabtcg.com/hero/cindra-dracai-of-retribution/",
    characters=["cindra", "emperor"],
    regions=[reg.VOLCOR],
    groups=[grp.SAYASHI],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dromai-about.md",
    title="Dromai, Ash Artist",
    source_link="https://fabtcg.com/hero/dromai/",
    characters=["dromai"],
    locations=[loc.MT_VOLCOR],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/emperor-about.md",
    title="Emperor, Dracai of Aesir",
    source_link="https://fabtcg.com/hero/emperor/",
    characters=["emperor"],
    locations=[loc.MT_VOLCOR],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/enigma-about.md",
    title="Enigma, Ledger of Ancestry",
    source_link="https://fabtcg.com/hero/enigma/",
    characters=["enigma"],
    locations=[loc.LUNAR_TEMPLE],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/fai-about.md",
    title="Fai, Rising Rebellion",
    source_link="https://fabtcg.com/hero/fai/",
    characters=[
        "fai",
        people.EUN,
    ],
    locations=[
        loc.ASHVAHAN,
        loc.RED_DESERT,
    ],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/ira-about.md",
    title="Ira, Scarlet Revenger",
    source_link="https://fabtcg.com/hero/ira-3/",
    characters=["ira"],
    locations=[
        loc.VALLEY_OF_BLOSSOMS,
        loc.IKARU,
    ],
    regions=[reg.MISTERIA],
    groups=[grp.CRIMSON_HAZE, grp.IKARU_CLAN],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/lexi-about.md",
    title="Lexi, Livewire",
    source_link="https://fabtcg.com/hero/lexi/",
    characters=["lexi"],
    locations=[
        loc.ENION,
        loc.VOLTHAVEN,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/viserai-about.md",
    title="Viserai",
    source_link="https://fabtcg.com/hero/viserai-the-forsaken/",
    characters=["chane", "viserai", people.LORD_SUTCLIFFE, people.URSUR],
    locations=[
        loc.I_ARATHAEL,
        loc.SHADOWREALM,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/azalea-about.md",
    title="Azalea",
    source_link="https://fabtcg.com/hero/azalea/",
    characters=["azalea"],
    locations=[
        loc.BLACKJACK_S_TAVERN,
    ],
    regions=[reg.THE_PITS],
    weapons=["death-dealer"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/boltyn-about.md",
    title="Boltyn",
    source_link="https://fabtcg.com/hero/boltyn-3/",
    characters=[
        "boltyn",
        people.EIRINA,
        people.AIOS,
        people.FYANNA_REDMOOR,
        people.BELLONA_THE_WARTUNE_HERALD,
        people.MINERVA_THEMIS,
    ],
    locations=[
        loc.THE_NORTHERN_REALMS,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_SOLARIUM,
        loc.OCTOMILITIA,
    ],
    regions=[reg.SOLANA, reg.DEMONASTERY],
    groups=[grp.SISTERS_OF_OCTOTHESIA, grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/fang-about.md",
    title="Fang",
    source_link="https://fabtcg.com/hero/fang/",
    characters=["fang", "emperor"],
    regions=[reg.VOLCOR],
    groups=[grp.CHILDREN_OF_THE_DRAGON],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/hala-about.md",
    title="Hala",
    source_link="https://fabtcg.com/hero/hala/",
    characters=[
        "hala",
        people.GRAND_MAGISTER_THE_STEADFAST,
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
    groups=[grp.CHILDREN_OF_THE_LIGHT],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/katsu-about.md",
    title="Katsu",
    source_link="https://fabtcg.com/hero/katsu-the-wanderer/",
    characters=["katsu"],
    locations=[
        loc.MUGENSHI_GORGE,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kayo-about.md",
    title="Kayo",
    source_link="https://fabtcg.com/hero/kayo/",
    characters=["kayo", "kassai"],
    locations=[
        loc.DEATHMATCH_ARENA,
        loc.THE_BADLANDS,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    groups=[grp.PROWLERS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/melody-about.md",
    title="Melody",
    source_link="https://fabtcg.com/hero/melody-3/",
    characters=["melody"],
    locations=[
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/oldhim-about.md",
    title="Oldhim",
    source_link="https://fabtcg.com/hero/oldhim-2/",
    characters=["oldhim"],
    locations=[
        loc.ISENLOFT,
    ],
    regions=[reg.ARIA],
    equipment=["stalagmite-bastion-of-isenloft"],
    groups=[grp.OLLIN],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/puffin-about.md",
    title="Puffin",
    source_link="https://fabtcg.com/hero/puffin/",
    characters=[
        "puffin",
        people.POLLY_CRANKA,
        people.CAPTAIN_RUE,
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
    title="Shiyana",
    source_link="https://fabtcg.com/hero/shiyana-diamond-gemini/",
    characters=["shiyana"],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/verdance-about.md",
    title="Verdance",
    source_link="https://fabtcg.com/hero/verdance/",
    characters=[
        "verdance",
        "florian",
        people.DAVNIR,
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
    title="Vynnset",
    source_link="https://fabtcg.com/hero/vynnset/",
    characters=[
        "vynnset",
        people.NASRETH,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-5l!p3d-7hru-7h3-cr4x-about.md",
    title="Arakni, 5l!p3d 7hru 7h3 Cr4x",
    source_link="https://fabtcg.com/hero/arakni-5lp3d-7hru-7h3-cr4x/",
    characters=[
        "arakni-solitary-confinement",
        people.DR_KREST_MORTIMER_THE_FIXER,
    ],
    locations=[
        loc.SOUTHMAW,
    ],
    regions=[reg.THE_PITS],
    groups=[grp.THE_SPIDER],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/betsy-about.md",
    title="Betsy, Skin in the Game",
    source_link="https://fabtcg.com/hero/betsy/",
    characters=["betsy"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/chane-about.md",
    title="Chane, Bound by Shadow",
    source_link="https://fabtcg.com/hero/chane/",
    characters=["chane"],
    locations=[
        loc.I_ARATHAEL,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/genis-about.md",
    title="Genis Wotchuneed",
    source_link="https://fabtcg.com/hero/genis-3/",
    characters=["genis"],
    locations=[
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/iyslander-about.md",
    title="Iyslander, Stormbind",
    source_link="https://fabtcg.com/hero/iyslander-2/",
    characters=["iyslander"],
    locations=[
        loc.BLEAK_EXPANSE,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/jarl-about.md",
    title="Jarl Vetreiði",
    source_link="https://fabtcg.com/hero/jarl/",
    characters=["jarl"],
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
    title="Kano, Dracai of Aether",
    source_link="https://fabtcg.com/hero/kano/",
    characters=["kano"],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/nuu-about.md",
    title="Nuu, Alluring Desire",
    source_link="https://fabtcg.com/hero/nuu-3/",
    characters=["nuu"],
    locations=[
        loc.MISTCLOAK_GULLY,
        loc.MISTCLOAK_TEAHOUSE,
    ],
    regions=[reg.MISTERIA],
    groups=[grp.VIPRESSA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/prism-about.md",
    title="Prism, Sculptor of Arc Light",
    source_link="https://fabtcg.com/hero/prism-soa/",
    characters=[
        "prism",
        "the-librarian",
        people.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
    ],
    locations=[
        loc.LIBRARY_OF_ILLUMINATION,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/terra-about.md",
    title="Terra",
    source_link="https://fabtcg.com/hero/terra/",
    characters=["terra"],
    locations=[
        loc.THE_KORSHEM,
        loc.MOUNT_HEROIC,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/tuffnut-about.md",
    title="Tuffnut, Bumbling Hulkster",
    source_link="https://fabtcg.com/hero/tuffnut/",
    characters=["tuffnut"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/uzuri-about.md",
    title="Uzuri, Switchblade",
    source_link="https://fabtcg.com/hero/uzuri-switchblade/",
    characters=["uzuri"],
    regions=[
        reg.METRIX,
        reg.MISTERIA,
        reg.THE_PITS,
    ],
    groups=[grp.THE_SPIDER],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/arakni-marionette-about.md",
    title="Arakni, Marionette",
    source_link="https://fabtcg.com/hero/arakni-marionette/",
    characters=["arakni-web-of-deceit"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/brevant-about.md",
    title="Brevant, Civic Protector",
    source_link="https://fabtcg.com/hero/brevant/",
    characters=["brevant"],
    locations=[],
    regions=[reg.SOLANA],
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/florian-about.md",
    title="Florian, Rotwood Harbinger",
    source_link="https://fabtcg.com/hero/florian/",
    characters=["florian"],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/frankie-about.md",
    title="Frankie, Make Ends Meat",
    source_link="https://fabtcg.com/hero/frankie/",
    characters=["frankie"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/gravy-about.md",
    title="Gravy Bones, Shipwrecked Looter",
    source_link="https://fabtcg.com/hero/gravy-bones/",
    characters=["gravy"],
    locations=[
        loc.DREADFALL_REACH,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kavdaen-about.md",
    title="Kavdaen, Trader of Skins",
    source_link="https://fabtcg.com/hero/kavdaen/",
    characters=["kavdaen"],
    regions=[reg.THE_PITS],
    locations=[
        loc.THE_MAW,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/levia-about.md",
    title="Levia, Shadowborn Abomination",
    source_link="https://fabtcg.com/hero/levia/",
    characters=[
        "levia",
        people.LADY_BARTHIMONT,
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
    title="Rhinar, Reckless Rampage",
    source_link="https://fabtcg.com/hero/rhinar/",
    characters=["rhinar"],
    regions=[reg.THE_SAVAGE_LANDS],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/scurv-about.md",
    title="Scurv, Stowaway",
    source_link="https://fabtcg.com/hero/scurv/",
    characters=[
        "scurv",
        people.STICKY_FINGERS,
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
    title="Teklovossen, Esteemed Magnate",
    source_link="https://fabtcg.com/hero/teklovossen-esteemed-magnate/",
    characters=["teklovossen"],
    regions=[reg.METRIX],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.PLUMVEX_PIPES_FACTORY,
        loc.COGWERX_CONGLOMERATE,
        loc.IRON_ASSEMBLY,
    ],
    groups=[grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/valda-about.md",
    title="Valda, Seismic Impact",
    source_link="https://fabtcg.com/hero/valda-seismic-impact/",
    characters=[
        "valda",
        people.BRAUMEISTER_BALEN,
    ],
    regions=[reg.ARIA],
    locations=[
        loc.THE_EVERFEST_CARNIVAL,
        loc.MIGHT_N_MEAD,
        loc.THE_FLOW,
        loc.LARINKMORTH,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/yoji-about.md",
    title="Yoji, Royal Protector",
    source_link="https://fabtcg.com/hero/yoji/",
    characters=[
        "yoji",
        people.LORD_WIZARD_CHIYO,
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
    title="Dash, Inventor Extraordinaire",
    source_link="https://fabtcg.com/hero/dash-3/",
    characters=[
        "dash",
        "data-doll-mkii",
        "maxx",
        people.JULES_TEKLOVOSSEN,
    ],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.MIDTOWN_MARKETS,
        loc.IRON_ASSEMBLY,
        loc.ROSARIO_HILLS,
        loc.LOWLAKE,
    ],
    regions=[reg.METRIX],
    groups=[grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/data-doll-mkii-about.md",
    title="Data Doll, MKII",
    source_link="https://fabtcg.com/hero/data-doll/",
    characters=["data-doll-mkii"],
    locations=[
        loc.IRON_ASSEMBLY,
    ],
    regions=[reg.METRIX],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/kassai-about.md",
    title="Kassai, Cintari Sellsword",
    source_link="https://fabtcg.com/hero/kassai-og/",
    characters=["kassai"],
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    regions=[reg.VOLCOR],
    groups=[grp.CINTARI],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/lyath-about.md",
    title="Lyath Goldmane, Vile Savant",
    source_link="https://fabtcg.com/hero/lyath-goldmane/",
    characters=[
        "lyath",
        "victor-goldmane",
        people.BLOODWORTH_GOLDMANE,
        people.TARA_VANGELD,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.THE_NORTHERN_REALMS,
    ],
    regions=[reg.THE_SAVAGE_LANDS],
    groups=[grp.HOUSE_GOLDMANE, grp.VANGELD],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/marlynn-about.md",
    title="Marlynn, Treasure Hunter",
    source_link="https://fabtcg.com/hero/marlynn/",
    characters=[
        "marlynn",
        people.CAPTAIN_COODER_OF_THE_SWIFTWATER_WARDEN_COODER,
    ],
    fauna=[fauna.KRAKEN],
    regions=[reg.HIGH_SEAS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/maxx-about.md",
    title="Maxx 'The Hype' Nitro",
    source_link="https://fabtcg.com/hero/maxx/",
    characters=["maxx"],
    locations=[
        loc.COGWERX_CONGLOMERATE,
    ],
    weapons=["banksy"],
    groups=[grp.COGWERX],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/olympia-about.md",
    title="Olympia, Prized Fighter",
    source_link="https://fabtcg.com/hero/olympia/",
    characters=[
        "olympia",
        people.COX,
    ],
    locations=[
        loc.DEATHMATCH_ARENA,
        loc.THE_MOAT,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/other.md",
    title="Others",
    characters=["ruudi", "taipanis", "taylor", "yorick"],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/pleiades-about.md",
    title="Pleiades, Superstar",
    source_link="https://fabtcg.com/hero/pleiades/",
    characters=["pleiades"],
    locations=[
        loc.THE_NORTHERN_REALMS,
        loc.GOUGEMOOR,
    ],
    groups=[grp.HOUSE_ASHWOOD, grp.HOUSE_GOLDMANE],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/riptide-about.md",
    title="Riptide, Lurker of the Deep",
    source_link="https://fabtcg.com/hero/riptide-lurker-of-the-deep/",
    characters=["riptide"],
    locations=[
        loc.SEETHESIDE_DOCKS,
    ],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/victor-goldmane-about.md",
    title="Victor Goldmane, High and Mighty",
    source_link="https://fabtcg.com/hero/victor/",
    characters=["victor-goldmane"],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zen-about.md",
    title="Zen, Tamer of Purpose",
    source_link="https://fabtcg.com/hero/zen-tamer-of-purpose/",
    characters=["zen"],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/heroes-of-rathe.md",
    title="Heroes of Rathe",
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/professions-of-rathe.md",
    title="Professions",
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/killjoy-about.md",
    title="Killjoy",
    source_link="https://fabtcg.com/hero/killjoy/",
    characters=["killjoy"],
    locations=[loc.DEATHMATCH_ARENA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/zane-about.md",
    title="Zane",
    source_link="https://fabtcg.com/hero/zane/",
    characters=["zane"],
    locations=[loc.DEATHMATCH_ARENA],
    dry_run=True,
)

db.upsert_story(
    path="src/heroes-of-rathe/dr-mortimer-about.md",
    title="Dr. Mortimer",
    source_link="https://fabtcg.com/hero/dr-mortimer/",
    characters=["dr-mortimer"],
    locations=[loc.SOUTHMAW],
    regions=[reg.THE_PITS],
    groups=[grp.L_APOCALYPTA, grp.SOUTHMAW_ASYLUM],
    dry_run=True,
)
