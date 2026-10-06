"""World of Rathe page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.

**Added 2026-08-21, stage 5 (the user's call).** ``world-of-rathe`` was already a
valid ``story_type`` — ``db/_domain.py`` lists it in ``upsert_story``'s own
docstring, and ``create_stories_index.py`` has always put all eleven pages in
``stories``. What was missing was somewhere to declare them, so the eleven rows
sat in the spine with nothing able to link an entity to them. That was not a
schema limit; it was a hole in this package.

This module was the **eighth** of the eleven ``SECTIONS`` rows, added because
Absolon needed it and nothing else was in scope at the time. ``archive`` (78
stories), ``equipment`` (19) and ``weapons`` (16) stayed undeclarable until
stage 12 (2026-08-22) gave each one a module of its own, so ``entries/`` now
covers **11 of the 11 story types** the index produces.

Those three modules are scaffolding and carry no declarations. The 63 of their
113 pages that already hold seeded entity links remain undeclared, and that is
not a bug to fix in passing: each is its own decision about whether an archived
or reference page should assert a relationship at all.

This module starts with **one declaration of eleven pages**, and that is
deliberate rather than unfinished. ``high-seas.md`` is declared for the entities
stage 5 needed and no others (the user's call) — see the call for what that
leaves out.
"""

from __future__ import annotations

from entries._runner import db
from entries.catalogue import (
    characters as people,
)
from entries.catalogue import (
    fauna,
    flora,
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
    monsters as mon,
)
from entries.catalogue import (
    regions as reg,
)
from entries.catalogue import (
    titles as ttl,
)

db.upsert_story(
    path="src/world-of-rathe/high-seas.md",
    story_type="world-of-rathe",
    title="High Seas",
    source_link="https://fabtcg.com/world-of-rathe/high-seas/",
    characters=[
        people.ABSOLON,
        people.NOCETES,
    ],
    groups=[
        grp.KURAGHAN,
        grp.THE_DHANI_EMPIRE,
        grp.DHANI_DEITIES,
    ],
    dry_run=True,
)


db.upsert_story(
    path="src/world-of-rathe/solana.md",
    story_type="world-of-rathe",
    title="Solana",
    source_link="https://fabtcg.com/world-of-rathe/solana/",
    titles=[ttl.GRAND_MAGISTER],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/nebulus-rift.md",
    story_type="world-of-rathe",
    title="Nebulus Rift",
    source_link="https://fabtcg.com/world-of-rathe/nebulus-rift/",
    characters=[
        "aurora",
        "oscilio",
        "zyggy",
        people.RUPIUS_AURIC_SCROLLMASTER,
    ],
    locations=[
        loc.AURIC_KEEP,
        loc.ASTRAL_BRIDGE,
        loc.SHYLDVERK,
        loc.VOLTARIS_GEM,
        loc.ENION,
        loc.I_ARATHAEL,
    ],
    regions=[reg.ARIA],
    groups=[grp.AETHERSCRIBES],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/rathe.md",
    story_type="world-of-rathe",
    title="World of Rathe",
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/demonastery.md",
    story_type="world-of-rathe",
    title="Demonastery",
    source_link="https://fabtcg.com/world-of-rathe/demonastery/",
    characters=[
        "viserai",
        people.SOL,
        people.GRAND_MAGISTER_THE_DEVOUT,
        people.ELDON_LOST_KNIGHT,
        people.HARLAND,
        people.SEPTUS,
        people.XAINE_RUNESCRIBE,
        people.LORD_SUTCLIFFE,
        people.CAOIMHE,
        people.CORVA,
        people.JEROVE,
        people.NIALL,
        people.WHISPER,
    ],
    locations=[
        loc.VALAHAI,
        loc.THE_SHADOW_CRYPTS,
        loc.ENION,
        loc.I_ARATHAEL,
        loc.THE_GOLDEN_FIELDS,
        loc.EBON_MAW,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_SAVAGE_LANDS],
    groups=[grp.HAND_OF_SOL],
    monsters=[
        mon.DIAPHENES,
        mon.BEREDOS,
        mon.LYSAGENES,
        mon.MANI,
        mon.SCAPHUS,
    ],
    equipment=["grimoire-of-the-haunt"],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/aria.md",
    story_type="world-of-rathe",
    title="Aria",
    source_link="https://fabtcg.com/world-of-rathe/aria/",
    characters=[
        people.YVOR,
        people.DAVNIR,
        people.GALCIA,
        people.ISEN,
        people.ALOSYN,
        people.NARAKIR,
        people.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.THE_FLOW,
        loc.THE_KORSHEM,
        loc.MT_ISEN,
        loc.ISEN_RANGES,
        loc.LARINKMORTH,
        loc.BLEAK_EXPANSE,
        loc.THUNDER_STEPPE,
        loc.ENION,
        loc.BOULDERHEAD_ISLAND,
        loc.VOLTHAVEN,
        loc.CANDLEHOLD,
        loc.THRONE_GLADE,
        loc.HIGHLOFT_INN,
        loc.SKYBREAKER,
        loc.THE_EVERFEST_CARNIVAL,
        loc.LEGENDARIUM,
        loc.VALAHAI,
        loc.ALDENGROVE,
        loc.ISENLOFT,
        loc.ANVILHEIM,
        loc.AURIC_KEEP,
        loc.SHYLDVERK,
    ],
    regions=[reg.ARIA],
    fauna=[
        fauna.CESARI,
        fauna.WELKIN,
        fauna.VITR_EO,
        fauna.KAIE_O,
        fauna.NA_SHARI,
        fauna.MEEP,
        fauna.FIANNA,
        fauna.SHOCK_STRIKER,
    ],
    monsters=[mon.RAVENIR],
    groups=[
        grp.WAYFARERS,
        grp.OLLIN,
        grp.AETHERSCRIBES,
        grp.ROSETTA,
        grp.THE_MAELA,
        grp.THE_VALDUR,
    ],
    food_drink=[
        food.ISENRI_SAKE,
        food.BREAKERNUT_ALE,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/misteria.md",
    story_type="world-of-rathe",
    title="Misteria",
    source_link="https://fabtcg.com/world-of-rathe/misteria/",
    characters=[people.KOUKI, people.JIRO_HENSHU, people.MISTRESS_IKARU],
    locations=[loc.MISTCLOAK_GULLY, loc.MUGENSHI_GORGE, loc.LUNAR_TEMPLE],
    regions=[reg.MISTERIA],
    groups=[
        grp.AUIS_SCALES,
        grp.IKARU_CLAN,
        grp.MUGENSHI_CLAN,
        grp.HOUSE_SANJING,
        grp.HOUSE_MIHARU,
        grp.HOUSE_YIJUN,
        grp.HOUSE_ISHIGAKI,
        grp.KEEPERS_OF_THE_SEVEN_ARTS,
    ],
    monsters=[mon.GENTUA],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/metrix.md",
    story_type="world-of-rathe",
    title="A Towering Metropolis",
    source_link="https://fabtcg.com/world-of-rathe/metrix/",
    characters=[
        "teklovossen",
        people.REX_BIGGUN,
        people.PROSPECTOR_COGMIRE,
        people.CHARLOTTE,
        people.SYNTHEA_TEKLO,
        people.RICKY_ROYCE,
        people.AUDACITY,
        people.MEAZE_BANZE,
        people.FRANCESCA_ZINNIA,
    ],
    locations=[
        loc.COGWERX_CONGLOMERATE,
        loc.THE_REGISTRY,
        loc.TEKLO_INDUSTRIES,
        loc.COPPERTOWN,
        loc.WEST_RISE,
        loc.EAST_RISE,
        loc.THE_EXPANSE,
        loc.ASCENSION_TERMINAL,
        loc.ZENITH,
        loc.MENDACITY_CYBER_THEATERS,
        loc.THE_SPRAWL,
        loc.COGMIRE_S_SALVAGE_EMPORIUM_AND_WORKSHOPPE,
        loc.MIDTOWN_MARKETS,
        loc.GIGADRILL_ELEVATOR,
        loc.PIT_3,
        loc.THE_NEEDLE,
        loc.TERRACETTE_PATH_ACADEMY,
        loc.ZINNIA_PARK,
        loc.IRON_ASSEMBLY,
        loc.IRON_HALL,
        loc.ENERGIZE_THE_ERA,
        loc.THE_NORTHERN_REALMS,
        loc.THE_FOUNDRY,
    ],
    regions=[reg.METRIX, reg.THE_PITS, reg.THE_SAVAGE_LANDS, reg.ARIA],
    groups=[
        grp.COGWERX,
        grp.TEKLO_INDUSTRIES,
        grp.IRON_ASSEMBLY,
        grp.THE_FOUNDRY,
        grp.REGISTRY,
        grp.MENDACITY_MEDIA,
        grp.BLACKJACK_S_MINING_INCORPORATED,
        grp.THE_SPIDER,
        grp.THE_MOB,
    ],
    food_drink=[food.OIL_COIL],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/pits.md",
    story_type="world-of-rathe",
    title="Pits",
    source_link="https://fabtcg.com/world-of-rathe/pits/",
    characters=[
        "kavdaen",
        people.WHITETAIL,
        people.ALKA_BIGGUNS,
        people.JEMJANG,
        people.BARON_DRIP,
        people.ACHLYS_HAG_OF_MOJIRE,
        people.BARTON_MOLE,
        people.ANARCH_ZEIR,
        people.GREENBIRD,
    ],
    locations=[
        loc.THE_MAW,
        loc.PIT_2,
        loc.COPPERTOWN,
        loc.ANKOMEIDO,
        loc.GIGADRILL_ELEVATOR,
        loc.PIT_3,
        loc.THE_LEAF_HOUSE,
        loc.THE_NORTHERN_REALMS,
        loc.SEETHE,
        loc.MINERS_REEF,
        loc.SKEIN,
        loc.RATTLEBONE,
        loc.GUTPURSE,
        loc.IRON_ASSEMBLY,
        loc.SOUTHMAW,
        loc.THE_SLICK,
        loc.BONEYARD,
        loc.MOJIRE,
        loc.BLACKJACK_S_TAVERN,
    ],
    regions=[reg.THE_PITS, reg.METRIX, reg.MISTERIA, reg.VOLCOR, reg.THE_SAVAGE_LANDS],
    groups=[
        grp.THE_MOB,
        grp.RUNNING_TIGERS,
        grp.COGWERX,
        grp.TEKLO_INDUSTRIES,
        grp.BLOCKHEADS,
        grp.TORCHED,
        grp.NUMBSKULLS,
        grp.JAWBREAKERS,
        grp.PIRANHAS,
        grp.FREAKSHOW,
        grp.BLACKJACK_S_MERCENARY_COMPANY,
        grp.BLACKJACK_S_MINING_INCORPORATED,
        grp.SOUTHMAW_ASYLUM,
        grp.THE_SPIDER,
        grp.L_APOCALYPTA,
    ],
    monsters=[mon.DREGS],
    fauna=[fauna.EEL_WOLVES, fauna.CRIMSON_JELLIES],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/savage-lands.md",
    story_type="world-of-rathe",
    title="Savage Lands",
    source_link="https://fabtcg.com/world-of-rathe/savage-lands/",
    characters=[
        people.THEODORE_HAMILTON_SCARBOROUGH,
        people.CAREM_DUNFIRTH,
        people.QUENTON,
        people.RUK_UTAN,
    ],
    locations=[loc.THE_BONEYARD],
    regions=[reg.THE_SAVAGE_LANDS],
    fauna=[fauna.ANK_IS, fauna.BRAWNHIDE, fauna.PELUDA, fauna.REK_VAS, fauna.SKERA, fauna.STRIX],
    flora=[
        flora.BLACKLACE,
        flora.BLOODROOT_MOSS,
        flora.DRUDEN,
        flora.HALDOR,
        flora.KINDLEWEED,
        flora.PATA,
        flora.SNAPJAW,
        flora.STONEBERRY_TREE,
        flora.THIEVES_LADDER,
        flora.VIOLET_LANCE,
        flora.VISURA,
        flora.WINTERGOLD,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/volcor.md",
    story_type="world-of-rathe",
    title="Volcor",
    source_link="https://fabtcg.com/world-of-rathe/volcor/",
    characters=["emperor", "iyslander", people.MIN_OF_THE_FOREST_OF_FLAMES, people.INFERNAI],
    locations=[
        loc.ASHVAHAN,
        loc.IMPERIAL_PALACE,
        loc.CHAMBER_OF_THE_DRAGON,
        loc.DRAGON_FESTIVAL,
        loc.FOREST_OF_FLAMES,
        loc.TAOKING,
        loc.BLACKROCK_QUARRIES,
        loc.DRAGON_S_PEAK,
        loc.THE_OBSIDIAN_COAST,
        loc.RED_DESERT,
        loc.DESHVAHAN,
        loc.MT_VOLCOR,
        loc.DRAGON_S_TEETH,
        loc.THE_MOLTEN_TIDE,
    ],
    regions=[reg.VOLCOR, reg.SOLANA],
    groups=[
        grp.EZU,
        grp.ALSHONI,
        grp.SAYASHI,
        grp.DRACAI,
        grp.VOLCAI,
        grp.CINTARI,
        grp.DUST_RUNNERS,
    ],
    fauna=[
        fauna.VUURLIN,
        fauna.LONGMA,
        fauna.RYOKI,
        fauna.MORROWS,
        fauna.APOPHIS,
        fauna.GIANT_DRIFT_STINGERS,
    ],
    dry_run=True,
)
