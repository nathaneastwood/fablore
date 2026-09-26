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
    titles as ttl,
)

# NarratedVideoEntry is the one exception: a narrated reading belongs to one
# story, has no registry table and no id of its own, so it is per-declaration
# data rather than a shared entity.
from db import NarratedVideoEntry  # noqa: F401
from entries._runner import db

# PARTIAL BY DECISION, NOT BY OMISSION (the user's call, 2026-08-21).
#
# This page is 4471 words across 29 sections and names a great many locations,
# regions and characters. This call declares none of them. Only the entities stage 5
# needed are here: the two gods, the two groups this page already documents by
# lore_story_key, and Dhani Deities — three groups, not the two this said until
# 2026-08-21. See the note on grp.DHANI_DEITIES below for why the third is here.
#
# The page is not link-free, though: five location links (Cogwerx Conglomerate,
# Dagger Docks, Griefers Reef, Kraken's Barrel, Trōpal-Dhani) were seeded onto it
# and survive because `locations=` is omitted rather than emptied. Omission
# preserves; an empty list would delete them.
#
# Anyone extending this call should treat the absences as unexamined rather than
# as decided — the opposite of every other declaration in entries/, where an
# entity left out was looked at and rejected. A full extraction of this page is
# its own gated pass.
#
# Absolon is the reason the module exists. He is named as a god here at :125 —
# "an ancient Dhani cult that worshipped Absolon, god of the great deep" — and
# nowhere else. The eight mentions on the already-declared
# main-story/high-seas/captain-bones-and-the-city-of-gold.md are every one of
# them the Kuraghan flagship "Absolon's Dream", never the deity.
#
# Nocetes did not need the module: captain-bones names the god outright. He is
# declared here anyway because :143 is where this page names him, and because the
# two gods share one roster.
db.upsert_story(
    path="src/world-of-rathe/high-seas.md",
    story_type="world-of-rathe",
    title="High Seas",
    # Not decoration. The story row already held this, and the first dry run of
    # this declaration reported "Cleared: - Source" — omitting it is a deletion,
    # because story metadata is replace-semantic like every junction. The eleven
    # world-of-rathe rows were seeded by create_stories_index.py and carry source
    # links that no declaration has ever had to preserve before, this module
    # being the first that can touch them.
    source_link="https://fabtcg.com/world-of-rathe/high-seas/",
    characters=[
        people.ABSOLON,
        people.NOCETES,
    ],
    groups=[
        # Both already carry lore_story_key pointing at this page, so the page
        # documented them while nothing linked them to it.
        grp.KURAGHAN,
        grp.THE_DHANI_EMPIRE,
        # The page describes the Dhani pantheon rather than naming it — the same
        # footing as "Speakeasy's Guilds", where the group name is the page's own
        # phrasing rather than an in-world proper noun. This link is also what
        # writes the roster and, through the parent walk, the Deities row itself:
        # reachability runs group -> members, never member -> group, so without a
        # declaration naming it the pantheon would exist only in the catalogue.
        grp.DHANI_DEITIES,
    ],
    dry_run=True,
)


# Registered 2026-08-25 (the user's call) to give the Grand Magister office a
# title row instead of five character rows with the office in their names.
#
# TITLES ONLY, DELIBERATELY. This page names dozens of entities and declares
# none of them — it is one of the ~184 pages carrying stored links that no
# declaration reproduces. Every other kwarg is omitted rather than guessed,
# and an omitted kwarg preserves: `characters=` is replace-semantic, so a
# partial list here would delete rather than add. Declaring the rest of this
# page is its own lore exercise.
db.upsert_story(
    path="src/world-of-rathe/solana.md",
    story_type="world-of-rathe",
    title="Solana",
    # source_link is restated because it does NOT preserve on omission — the
    # first dry run of this declaration reported "Cleared: - Source", which is
    # how that was caught. Authors, artists, date and thumbnail are empty on
    # this row already, so omitting them costs nothing.
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
        "zyggy",  # new link — named at :37, not previously seeded
        people.RUPIUS_AURIC_SCROLLMASTER,
    ],
    locations=[
        loc.AURIC_KEEP,
        loc.ASTRAL_BRIDGE,
        loc.SHYLDVERK,
        loc.VOLTARIS_GEM,
        loc.ENION,
        loc.I_ARATHAEL,  # epigraph only (:9), no region per catalogue convention
    ],
    regions=[reg.ARIA],
    groups=[grp.AETHERSCRIBES],  # new link — named at :21, :33, :37; not previously seeded
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
        "viserai",  # hero bare slug, not people.VISERAI
        people.SOL,
        people.GRAND_MAGISTER_THE_DEVOUT,
        people.ELDON_LOST_KNIGHT,
        people.HARLAND,
        people.SEPTUS,
        people.XAINE_RUNESCRIBE,
        people.LORD_SUTCLIFFE,
        people.CAOIMHE,  # new
        people.CORVA,  # new
        people.JEROVE,  # new
        people.NIALL,  # new
        people.WHISPER,  # new; reclassified from mon.WHISPER — see catalogue note
    ],
    locations=[
        loc.VALAHAI,
        loc.THE_SHADOW_CRYPTS,
        loc.ENION,
        loc.I_ARATHAEL,
        loc.THE_GOLDEN_FIELDS,
        loc.EBON_MAW,  # new; replaces seeded loc.THE_MAW — see Ambiguities
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA, reg.THE_SAVAGE_LANDS],
    groups=[grp.HAND_OF_SOL],
    monsters=[
        mon.DIAPHENES,  # new
        mon.BEREDOS,  # new
        mon.LYSAGENES,  # new
        mon.MANI,  # new
        mon.SCAPHUS,  # new
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
        # :65 "Queen Celvera" — the existing row for Candlehold's queen. Whether the
        # row should be renamed Celvera is the user's call; a rename mints a new id.
        people.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.THE_FLOW,
        loc.THE_KORSHEM,  # seeded
        loc.MT_ISEN,  # page says "Mount Isen", a recorded alias
        loc.ISEN_RANGES,
        loc.LARINKMORTH,  # seeded
        loc.BLEAK_EXPANSE,
        loc.THUNDER_STEPPE,  # seeded
        loc.ENION,  # seeded
        loc.BOULDERHEAD_ISLAND,  # page says "Boulderhead", shortened form of the same isle
        loc.VOLTHAVEN,
        loc.CANDLEHOLD,  # seeded
        loc.THRONE_GLADE,
        loc.HIGHLOFT_INN,
        loc.SKYBREAKER,  # NEW
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
        grp.ROSETTA,  # Valahai-era order named alongside Wayfarers/Aetherscribes — see Ambiguities
        grp.THE_MAELA,
        grp.THE_VALDUR,
    ],
    food_drink=[
        food.ISENRI_SAKE,  # NEW
        food.BREAKERNUT_ALE,  # NEW
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/misteria.md",
    story_type="world-of-rathe",
    title="Misteria",
    source_link="https://fabtcg.com/world-of-rathe/misteria/",
    characters=[people.KOUKI, people.JIRO_HENSHU, people.MISTRESS_IKARU],
    # "Immortal Lunar Temple" on the page is a near-match to existing loc.LUNAR_TEMPLE — see Ambiguities
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
    monsters=[mon.GENTUA],  # reclassified from fauna.GENTUA — see catalogue note
    dry_run=True,
)

db.upsert_story(
    path="src/world-of-rathe/metrix.md",
    story_type="world-of-rathe",
    title="A Towering Metropolis",
    source_link="https://fabtcg.com/world-of-rathe/metrix/",
    characters=[
        "teklovossen",  # hero slug (Jules Teklovossen is in the hero list), not people.JULES_TEKLOVOSSEN
        people.REX_BIGGUN,
        people.PROSPECTOR_COGMIRE,
        people.CHARLOTTE,
        people.SYNTHEA_TEKLO,
        people.RICKY_ROYCE,
        people.AUDACITY,  # "λud@c!ty", the Foundry's anonymous operator
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
        loc.THE_NORTHERN_REALMS,  # "neighboring Northern Realms" Blackjack's expands into
        loc.THE_FOUNDRY,
    ],
    regions=[reg.METRIX, reg.THE_PITS, reg.THE_SAVAGE_LANDS, reg.ARIA],
    groups=[
        # Cogwerx/Teklo/Iron Assembly/Foundry/Registry/Mendacity/Blackjack's already exist as both
        # loc.X (their Metrix premises, seeded) and grp.X (the organisation) — the page describes
        # all of these at length as organisations, so both are included; see Notes.
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
        "kavdaen",  # hero slug, not people.KAVDAEN — also named "Trader of Skins" but heroes get no epithets
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
        loc.IRON_ASSEMBLY,  # seeded as location; page usage reads as the org — see Ambiguities
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
    # "Hecklers" (:77-91) are now kind.HECKLER — a feral people with no named
    # leader or roster, so no character on this page carries it yet.
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
        loc.BLACKROCK_QUARRIES,  # seeded
        loc.DRAGON_S_PEAK,  # seeded
        loc.THE_OBSIDIAN_COAST,
        loc.RED_DESERT,
        loc.DESHVAHAN,  # seeded
        loc.MT_VOLCOR,  # page says "Mount Volcor" — see Ambiguities
        loc.DRAGON_S_TEETH,  # new
        loc.THE_MOLTEN_TIDE,  # new
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
