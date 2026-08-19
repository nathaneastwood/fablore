"""Short story registrations — one ``db.upsert_story`` call per page.

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
    path="src/short-stories/usurp-the-shadow-throne/open-the-gates.md",
    story_type="short-stories",
    title="Open the Gates",
    publication_date="2026-07-16",
    heroes=["viserai", "levia", "malice"],
    npcs=[
        npc.BLASMOPHET,
    ],
    locations=[
        loc.THE_ABYSS,
        loc.NEVEREST,
        loc.SHADOWREALM,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    dry_run=True,
)
# TODO: group — Gloomblades

db.upsert_story(
    path="src/short-stories/armory-deck-pleiades/pleiades.md",
    story_type="short-stories",
    title="Build The Arena Atmosphere Like A Superstar!",
    heroes=["pleiades"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/wings-of-wisdom.md",
    story_type="short-stories",
    title="Wings of Wisdom",
    source_link="https://fabtcg.com/articles/wings-of-wisdom/",
    heroes=["prism"],
    npcs=[
        npc.SEKEM_ARCHANGEL_OF_RAVAGES,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kassais-diary.md",
    story_type="short-stories",
    title="Kassai's Diary",
    heroes=["betsy", "kassai", "kayo", "olympia", "rhinar", "victor-goldmane"],
    npcs=[
        npc.FIGHTMASTER_KOX,
        npc.GENERAL_CHUL,
        npc.SADA,
        npc.ALIF,
        npc.FAYYAD,
    ],
    locations=[
        loc.DESHVAHAN,
        loc.URJIYSA,
        loc.ASHVAHAN,
        loc.RED_DESERT,
        loc.GOUGEMOOR,
        loc.THE_MOAT,
        loc.DEATHMATCH_ARENA,
    ],
    regions=[reg.THE_SAVAGE_LANDS, reg.VOLCOR],
    fauna=[fauna.GIANT_DRIFT_STINGERS, fauna.BRAWNHIDE],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/surging-to-success.md",
    story_type="short-stories",
    title="Surging to Success",
    source_link="https://fabtcg.com/articles/surging-success/",
    heroes=["katsu"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/ira-crimson-haze.md",
    story_type="short-stories",
    title="Roll of Honor: Ira, Crimson Haze",
    heroes=["ira"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/kassai-cintari-sellsword.md",
    story_type="short-stories",
    title="Roll of Honor: Kassai, Cintari Sellsword",
    heroes=["kassai"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/oscilio-constella-intelligence.md",
    story_type="short-stories",
    title="Oscilio, Constella Intelligence",
    heroes=["aurora", "oscilio"],
    npcs=[
        npc.QUEEN_OF_CANDLEHOLD,
    ],
    locations=[
        loc.ARCTUROS,
        loc.CANDLEHOLD,
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-gravy-bones/gravy-bones.md",
    story_type="short-stories",
    title="Rise From The Depths And Terrorize The High Seas",
    heroes=["gravy"],
    locations=[loc.DREADFALL_REACH],
    regions=[reg.HIGH_SEAS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-rhinar/rhinar.md",
    story_type="short-stories",
    title="Reclaim Your Territory! Rip Your Foes Apart!",
    heroes=["rhinar"],
    locations=[loc.DEATHMATCH_ARENA],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/living-on-a-prayer.md",
    story_type="short-stories",
    title="Living on a Prayer",
    source_link="https://fabtcg.com/articles/living-on-a-prayer/",
    heroes=["boltyn"],
    npcs=[npc.GALAPHOR],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    weapons=["raydn-duskbane"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/no-pain-no-gain.md",
    story_type="short-stories",
    title="No Pain No Gain",
    source_link="https://fabtcg.com/articles/no-pain-no-gain/",
    heroes=["vynnset"],
    npcs=[
        npc.DARIAN,
        npc.DAXIUS,
        npc.DHERIC,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/victor.md",
    story_type="short-stories",
    title="Victor",
    heroes=["victor-goldmane"],
    npcs=[npc.HOG],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/bait-and-switch.md",
    story_type="short-stories",
    title="Bait and Switch",
    source_link="https://fabtcg.com/articles/bait-and-switch/",
    heroes=["uzuri"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/cornering-your-prey.md",
    story_type="short-stories",
    title="Cornering Your Prey",
    source_link="https://fabtcg.com/articles/cornering-your-prey/",
    heroes=["arakni-huntsman"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/chane.md",
    story_type="short-stories",
    title="Roll of Honor: Chane",
    heroes=["chane"],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/lexi-livewire.md",
    story_type="short-stories",
    title="Roll of Honor: Lexi, Livewire",
    heroes=["briar", "lexi", "yorick"],
    locations=[
        loc.CANDLEHOLD,
        loc.ENION,
    ],
    regions=[reg.ARIA],
    weapons=["voltaire-strike-twice"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/rhinar.md",
    story_type="short-stories",
    title="Roll of Honor: Rhinar",
    npcs=[
        npc.LUCA_ARENA_CICERONE,
        npc.TOGARK_THE_WRANGLER,
    ],
    locations=[
        loc.GOUGEMOOR,
        loc.TARNISH_HILL,
        loc.THE_MOAT,
        loc.DEATHMATCH_ARENA,
    ],
    fauna=[fauna.SCARBIT, fauna.BRAWNHIDE],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/aurora-shooting-star.md",
    story_type="short-stories",
    title="Aurora, Shooting Star",
    heroes=["aurora"],
    locations=[loc.ENION],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/verdance-thorn-of-the-rose.md",
    story_type="short-stories",
    title="Verdance, Thorn of the Rose",
    heroes=["florian", "verdance"],
    locations=[loc.CANDLEHOLD],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/round-the-table/brevant-civic-protector.md",
    story_type="short-stories",
    title="Brevant, Civic Protector",
    heroes=["brevant"],
    npcs=[npc.THEBASTO_MAGISTER_OF_DEFENSE],
    locations=[
        loc.CHARRED_RANGE,
        loc.HAND_OF_SOL,
    ],
    regions=[reg.SOLANA, reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-arakni/arakni-5l!p3d-7hru-7h3-cr4x.md",
    story_type="short-stories",
    title="5l!p 7hru 7h3 Cr4x 4nd Unh!ng3 Your V!c7!m",
    heroes=["arakni-solitary-confinement"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-hala/hala.md",
    story_type="short-stories",
    title="Armory Deck Origins: Hala",
    heroes=["hala"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/maxx-imum-hype.md",
    story_type="short-stories",
    title="Maxx-imum Hype",
    heroes=["maxx"],
    weapons=["banksy"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kassai.md",
    story_type="short-stories",
    title="Kassai",
    heroes=["kassai"],
    locations=[loc.THE_MOAT],
    weapons=["cintari-saber"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kayo.md",
    story_type="short-stories",
    title="Kayo",
    heroes=["kayo"],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/aiming-high.md",
    story_type="short-stories",
    title="Aiming High",
    source_link="https://fabtcg.com/articles/aiming-high/",
    heroes=["azalea"],
    npcs=[
        npc.BAZZ,
        npc.PINWHEEL,
    ],
    locations=[loc.BLOCKHEAD_TERRITORY],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/briar-warden-of-thorns.md",
    story_type="short-stories",
    title="Roll of Honor: Briar, Warden of Thorns",
    heroes=["briar"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/dash.md",
    story_type="short-stories",
    title="Roll of Honor: Dash",
    heroes=["dash"],
    npcs=[
        npc.DR_WYVERSTONE,
        npc.RICKY_ROYCE,
        npc.THIROUX,
    ],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.ZINNIA_PARK,
        loc.TERRACETTE_PATH_ACADEMY,
        loc.GIGADRILL_ELEVATOR,
    ],
    regions=[reg.METRIX],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/iyslander-stormbind.md",
    story_type="short-stories",
    title="Roll of Honor: Iyslander, Stormbind",
    heroes=["iyslander"],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/kano.md",
    story_type="short-stories",
    title="Roll of Honor: Kano",
    heroes=["kano"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/oldhim-grandfather-of-eternity.md",
    story_type="short-stories",
    title="Roll of Honor: Oldhim, Grandfather of Eternity",
    source_link="https://fabtcg.com/articles/roll-of-honor-oldhim-grandfather-of-eternity/",
    heroes=["oldhim"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/oldhim.md",
    story_type="short-stories",
    title="Roll of Honor: Oldhim",
    source_link="https://fabtcg.com/articles/roll-honor-oldhim/",
    heroes=["oldhim"],
    locations=[loc.ISENLOFT],
    regions=[reg.ARIA],
    weapons=["winters-wail"],
    equipment=["stalagmite-bastion-of-isenloft"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/victor-goldmane.md",
    story_type="short-stories",
    title="Roll of Honor: Victor Goldmane",
    heroes=["victor-goldmane"],
    npcs=[
        npc.AURELIUS,
        npc.DUKE_DREXEN,
    ],
    locations=[
        loc.CLIFFHOLD,
        loc.THE_NORTHERN_REALMS,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/dash-through-data.md",
    story_type="short-stories",
    title="Dash Through Data",
    heroes=["dash", "data-doll-mkii"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/more-than-human.md",
    story_type="short-stories",
    title="More Than Human",
    heroes=["teklovossen"],
    locations=[loc.EAST_RISE],
    regions=[reg.METRIX],
    equipment=["evo-face-breaker"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/compendium-of-rathe/seasonal-guide.md",
    story_type="short-stories",
    title="Seasonal Guide",
    regions=[
        reg.ARIA,
        reg.METRIX,
        reg.SOLANA,
        reg.THE_SAVAGE_LANDS,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/betsy.md",
    story_type="short-stories",
    title="Betsy",
    heroes=["betsy"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/olympia.md",
    story_type="short-stories",
    title="Olympia",
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/rhinar.md",
    story_type="short-stories",
    title="Rhinar",
    npcs=[npc.FIGHTMASTER_KOX],
    locations=[
        loc.TARNISH_HILL,
        loc.THISTLEFOLD,
        loc.WEST_RANGES,
    ],
    regions=[reg.SOLANA, reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/a-thousand-cuts.md",
    story_type="short-stories",
    title="A Thousand Cuts",
    source_link="https://fabtcg.com/articles/thousand-cuts/",
    heroes=["benji"],
    regions=[reg.THE_PITS],
    weapons=["zephyr-needle"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/its-a-trap.md",
    story_type="short-stories",
    title="It's a Trap!",
    source_link="https://fabtcg.com/articles/its-trap/",
    heroes=["riptide"],
    npcs=[npc.SQUIDGE],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/briar.md",
    story_type="short-stories",
    title="Roll of Honor: Briar",
    heroes=["briar"],
    npcs=[
        npc.DAVNIR,
        npc.YVOR,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA],
    weapons=["rosetta-thorn"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/iyslander.md",
    story_type="short-stories",
    title="Roll of Honor: Iyslander",
    source_link="https://fabtcg.com/articles/roll-honor-iyslander/",
    heroes=["iyslander"],
    locations=[loc.BLEAK_EXPANSE],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/zen.md",
    story_type="short-stories",
    title="Roll of Honor: Zen",
    heroes=["zen"],
    npcs=[npc.MASTER_MORITA_ART_OF_THE_HAND],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/florian-rotwood-harbinger.md",
    story_type="short-stories",
    title="Florian, Rotwood Harbinger",
    heroes=["florian"],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/round-the-table/melody-sing-along.md",
    story_type="short-stories",
    title="Melody, Sing-along",
    heroes=["melody"],
    locations=[
        loc.ASKRAWELD,
        loc.FENSALIR,
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA, reg.METRIX, reg.MISTERIA],
    fauna=[fauna.CESARI],
    dry_run=True,
)
