"""Short story registrations — one ``db.upsert_story`` call per page.

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
    groups as grp,
)
from entries.catalogue import (
    locations as loc,
)
from entries.catalogue import (
    regions as reg,
)

db.upsert_story(
    path="src/short-stories/usurp-the-shadow-throne/open-the-gates.md",
    title="Open the Gates",
    publication_date="2026-07-16",
    characters=[
        "viserai",
        "levia",
        "malice",
        people.BLASMOPHET,
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
    groups=[grp.GLOOMBLADES],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-pleiades/pleiades.md",
    title="Build The Arena Atmosphere Like A Superstar!",
    characters=["pleiades"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/wings-of-wisdom.md",
    title="Wings of Wisdom",
    source_link="https://fabtcg.com/articles/wings-of-wisdom/",
    characters=[
        "prism",
        people.SEKEM_ARCHANGEL_OF_RAVAGES,
    ],
    regions=[reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kassais-diary.md",
    title="Kassai's Diary",
    characters=[
        "betsy",
        "kassai",
        "kayo",
        "olympia",
        "rhinar",
        "victor-goldmane",
        people.FIGHTMASTER_KOX,
        people.GENERAL_CHUL,
        people.SADA,
        people.ALIF,
        people.FAYYAD,
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
    title="Surging to Success",
    source_link="https://fabtcg.com/articles/surging-success/",
    characters=["katsu"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/ira-crimson-haze.md",
    title="Roll of Honor: Ira, Crimson Haze",
    characters=["ira"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/kassai-cintari-sellsword.md",
    title="Roll of Honor: Kassai, Cintari Sellsword",
    characters=["kassai"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/oscilio-constella-intelligence.md",
    title="Oscilio, Constella Intelligence",
    characters=[
        "aurora",
        "oscilio",
        people.QUEEN_OF_CANDLEHOLD,
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
    title="Rise From The Depths And Terrorize The High Seas",
    characters=["gravy"],
    locations=[loc.DREADFALL_REACH],
    regions=[reg.HIGH_SEAS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-rhinar/rhinar.md",
    title="Reclaim Your Territory! Rip Your Foes Apart!",
    characters=["rhinar"],
    locations=[loc.DEATHMATCH_ARENA],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/living-on-a-prayer.md",
    title="Living on a Prayer",
    source_link="https://fabtcg.com/articles/living-on-a-prayer/",
    characters=[
        "boltyn",
        people.GALAPHOR,
    ],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    weapons=["raydn-duskbane"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/dusk-till-dawn/no-pain-no-gain.md",
    title="No Pain No Gain",
    source_link="https://fabtcg.com/articles/no-pain-no-gain/",
    characters=[
        "vynnset",
        people.DARIAN,
        people.DAXIUS,
        people.DHERIC,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/victor.md",
    title="Victor",
    characters=[
        "victor-goldmane",
        people.HOG,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/bait-and-switch.md",
    title="Bait and Switch",
    source_link="https://fabtcg.com/articles/bait-and-switch/",
    characters=["uzuri"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/cornering-your-prey.md",
    title="Cornering Your Prey",
    source_link="https://fabtcg.com/articles/cornering-your-prey/",
    characters=["arakni-huntsman"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/chane.md",
    title="Roll of Honor: Chane",
    characters=["chane"],
    regions=[reg.DEMONASTERY, reg.SOLANA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/lexi-livewire.md",
    title="Roll of Honor: Lexi, Livewire",
    characters=["briar", "lexi", "yorick"],
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
    title="Roll of Honor: Rhinar",
    characters=[
        people.LUCA_ARENA_CICERONE,
        people.TOGARK_THE_WRANGLER,
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
    title="Aurora, Shooting Star",
    characters=["aurora"],
    locations=[loc.ENION],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/verdance-thorn-of-the-rose.md",
    title="Verdance, Thorn of the Rose",
    characters=["florian", "verdance"],
    locations=[loc.CANDLEHOLD],
    regions=[reg.ARIA],
    groups=[grp.ROSETTA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/round-the-table/brevant-civic-protector.md",
    title="Brevant, Civic Protector",
    characters=[
        "brevant",
        people.THEBASTO_MAGISTER_OF_DEFENSE,
    ],
    locations=[
        loc.CHARRED_RANGE,
    ],
    regions=[reg.SOLANA, reg.VOLCOR],
    groups=[grp.HAND_OF_SOL],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-arakni/arakni-5l!p3d-7hru-7h3-cr4x.md",
    title="5l!p 7hru 7h3 Cr4x 4nd Unh!ng3 Your V!c7!m",
    characters=["arakni-solitary-confinement"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-deck-hala/hala.md",
    title="Armory Deck Origins: Hala",
    characters=["hala"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/maxx-imum-hype.md",
    title="Maxx-imum Hype",
    characters=["maxx"],
    weapons=["banksy"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kassai.md",
    title="Kassai",
    characters=["kassai"],
    locations=[loc.THE_MOAT],
    weapons=["cintari-saber"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/kayo.md",
    title="Kayo",
    characters=["kayo"],
    regions=[reg.THE_SAVAGE_LANDS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/aiming-high.md",
    title="Aiming High",
    source_link="https://fabtcg.com/articles/aiming-high/",
    characters=[
        "azalea",
        people.BAZZ,
        people.PINWHEEL,
    ],
    locations=[loc.BLOCKHEAD_TERRITORY],
    regions=[reg.THE_PITS],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/briar-warden-of-thorns.md",
    title="Roll of Honor: Briar, Warden of Thorns",
    characters=["briar"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/dash.md",
    title="Roll of Honor: Dash",
    characters=[
        "dash",
        people.DR_WYVERSTONE,
        people.RICKY_ROYCE,
        people.THIROUX,
    ],
    locations=[
        loc.TEKLO_INDUSTRIES,
        loc.ZINNIA_PARK,
        loc.TERRACETTE_PATH_ACADEMY,
        loc.GIGADRILL_ELEVATOR,
    ],
    regions=[reg.METRIX],
    groups=[grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/iyslander-stormbind.md",
    title="Roll of Honor: Iyslander, Stormbind",
    characters=["iyslander"],
    regions=[reg.VOLCOR],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/kano.md",
    title="Roll of Honor: Kano",
    characters=["kano"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/oldhim-grandfather-of-eternity.md",
    title="Roll of Honor: Oldhim, Grandfather of Eternity",
    source_link="https://fabtcg.com/articles/roll-of-honor-oldhim-grandfather-of-eternity/",
    characters=["oldhim"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/oldhim.md",
    title="Roll of Honor: Oldhim",
    source_link="https://fabtcg.com/articles/roll-honor-oldhim/",
    characters=["oldhim"],
    locations=[loc.ISENLOFT],
    regions=[reg.ARIA],
    weapons=["winters-wail"],
    equipment=["stalagmite-bastion-of-isenloft"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/victor-goldmane.md",
    title="Roll of Honor: Victor Goldmane",
    characters=[
        "victor-goldmane",
        people.AURELIUS,
        people.DUKE_DREXEN,
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
    title="Dash Through Data",
    characters=["dash", "data-doll-mkii"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/more-than-human.md",
    title="More Than Human",
    characters=["teklovossen"],
    locations=[loc.EAST_RISE],
    regions=[reg.METRIX],
    equipment=["evo-face-breaker"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/compendium-of-rathe/seasonal-guide.md",
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
    title="Betsy",
    characters=["betsy"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/olympia.md",
    title="Olympia",
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/rhinar.md",
    title="Rhinar",
    characters=[people.FIGHTMASTER_KOX],
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
    title="A Thousand Cuts",
    source_link="https://fabtcg.com/articles/thousand-cuts/",
    characters=["benji"],
    regions=[reg.THE_PITS],
    weapons=["zephyr-needle"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/outsiders/its-a-trap.md",
    title="It's a Trap!",
    source_link="https://fabtcg.com/articles/its-trap/",
    characters=[
        "riptide",
        people.SQUIDGE,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/briar.md",
    title="Roll of Honor: Briar",
    characters=[
        "briar",
        people.DAVNIR,
        people.YVOR,
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
    title="Roll of Honor: Iyslander",
    source_link="https://fabtcg.com/articles/roll-honor-iyslander/",
    characters=["iyslander"],
    locations=[loc.BLEAK_EXPANSE],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/roll-of-honour/zen.md",
    title="Roll of Honor: Zen",
    characters=[
        "zen",
        people.MASTER_MORITA_ART_OF_THE_HAND,
    ],
    regions=[reg.MISTERIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/rosetta/florian-rotwood-harbinger.md",
    title="Florian, Rotwood Harbinger",
    characters=["florian"],
    locations=[
        loc.CANDLEHOLD,
        loc.ROTWOOD,
    ],
    regions=[reg.ARIA],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/round-the-table/melody-sing-along.md",
    title="Melody, Sing-along",
    characters=["melody"],
    locations=[
        loc.ASKRAWELD,
        loc.FENSALIR,
        loc.THE_FLOW,
    ],
    regions=[reg.ARIA, reg.METRIX, reg.MISTERIA],
    fauna=[fauna.CESARI],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/bright-lights/bright-lights.md",
    title="Bright Lights",
    locations=[
        loc.IRON_ASSEMBLY,
        loc.TEKLO_INDUSTRIES,
    ],
    groups=[
        grp.IRON_ASSEMBLY,
        grp.MENDACITY_MEDIA,
        grp.TEKLO_INDUSTRIES,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/armory-decks/armory-decks.md",
    title="Armory Decks",
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/heavy-hitters/march-armoury-kit.md",
    title="March 2024 Armory Kit",
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/part-the-mistveil/set-announcement.md",
    title="Part the Mistveil",
    characters=["enigma", "nuu", "zen"],
    dry_run=True,
)

db.upsert_story(
    path="src/short-stories/part-the-mistveil/set-spoilers.md",
    title="Part the Mistveil Spoilers",
    characters=["enigma", "nuu", "zen"],
    dry_run=True,
)
