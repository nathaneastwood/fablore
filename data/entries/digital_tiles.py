"""Digital tiles page registrations — one ``db.upsert_story`` call per page.

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
    monsters as mon,
)
from entries.catalogue import (
    regions as reg,
)

db.upsert_story(
    path="src/digital-tiles/omens-of-the-third-age/omens-of-the-third-age.md",
    story_type="digital-tiles",
    title="Omens of the Third Age",
    characters=[
        "aurora",
        "oscilio",
        "zyggy",
        people.MAELA_ISULFV,
        people.YVOR,
        people.KARL,
    ],
    locations=[
        loc.ASTRAL_BRIDGE,
        loc.AURIC_KEEP,
        loc.ENION,
        loc.VALAHAI,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/bright-lights/bright-lights.md",
    story_type="digital-tiles",
    title="Bright Lights",
    characters=["dash", "teklovossen"],
    fragments={"dash": "dash-io", "teklovossen": "fabricate"},
    locations=[
        loc.COGWERX_CONGLOMERATE,
        loc.EIDOLON,
        loc.IRON_ASSEMBLY,
        loc.LOWLAKE,
        loc.TEKLO_INDUSTRIES,
    ],
    regions=[
        reg.METRIX,
    ],
    equipment=["cogwerx-base-head", "evo-command-center", "evo-data-mine"],
    groups=[grp.STEELSTREET_ENFORCERS, grp.TEKLO_INDUSTRIES],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/compendium-of-rathe/compendium-of-rathe.md",
    story_type="digital-tiles",
    title="Compendium of Rathe",
    characters=[
        "dorinthea",
        "jarl",
        people.BELLONA_THE_WARTUNE_HERALD,
        people.SOL,
        people.BOO,
        people.MIRAGAI,
    ],
    locations=[
        loc.NECROPOLIS,
        loc.THE_AWAKENING_CEREMONY,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.HIGH_SEAS,
        reg.MISTERIA,
        reg.SOLANA,
        reg.VOLCOR,
    ],
    weapons=["dawnblade"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/crucible-of-war/crucible-of-war.md",
    story_type="digital-tiles",
    title="Crucible of War",
    characters=[
        "azalea",
        "dorinthea",
        "emperor",
        "kassai",
        "teklovossen",
        people.GENERAL_EKODA,
        people.LORD_SABUTO,
        people.LORD_SUTCLIFFE,
        people.MAGNUS_THE_VIGILANT,
        people.SOL,
        people.THEODORE_HAMILTON_SCARBOROUGH,
        people.IRUNAMEABH,
    ],
    fragments={
        "dorinthea": "courage-of-bladehold",
        "emperor": "cindering-foresight",
        "kassai": "cintari-saber",
        "teklovossen": "teklovossens-workshop",
    },
    locations=[
        loc.ANVILHEIM,
        loc.IMPERIAL_PALACE,
        loc.MUGENSHI_GORGE,
        loc.THE_BADLANDS,
        loc.THE_BROKEN_CHARIOT_TAVERN,
        loc.THE_GOLDEN_FIELDS,
        loc.ZANCARO,
        loc.I_ARATHAEL,
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
    fauna=[
        fauna.AZERI,
        fauna.REK_VAS,
    ],
    weapons=[
        "cintari-saber",
        "mandible-claw",
        "plasma-barrel-shot",
        "red-liner",
        "sledge-of-anvilheim",
        "talishar-the-lost-prince",
        "zephyr-needle",
    ],
    equipment=[
        "bloodsheath-skeleta",
        "breeze-rider-boots",
        "courage-of-bladehold",
        "crater-fist",
        "gamblers-gloves",
        "metacarpus-node",
        "skullhorn",
        "viziertronic-model-i",
    ],
    groups=[grp.MUGENSHI_CLAN],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/everfest/everfest.md",
    story_type="digital-tiles",
    title="Everfest",
    characters=[
        "boltyn",
        people.JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS,
        people.LORD_SUTCLIFFE,
        people.SOL,
    ],
    fragments={"boltyn": "swarming-gloomveil"},
    locations=[
        loc.ISENLOFT,
        loc.SKYLARK_PEAK,
        loc.THE_BADLANDS,
        loc.THE_EVERFEST_CARNIVAL,
        loc.THE_GOLDEN_GNOME,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.DEMONASTERY,
        reg.METRIX,
        reg.MISTERIA,
        reg.THE_PITS,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
    ],
    fauna=[
        fauna.KAIE_O,
        fauna.KRAKEN,
        fauna.MEEP,
        fauna.EBON_SERPENT,
        fauna.KUMIHO,
        fauna.MIREOA,
    ],
    weapons=["dreadbore", "krakens-aethervein"],
    equipment=[
        "arcane-lantern",
        "crown-of-reflection",
        "earthlore-bounty",
        "helm-of-sharp-eye",
        "mask-of-the-pouncing-lynx",
        "stalagmite-bastion-of-isenloft",
        "vexing-quillhand",
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/heavy-hitters/heavy-hitters.md",
    story_type="digital-tiles",
    title="Heavy Hitters",
    characters=[
        "kassai",
        "olympia",
        "rhinar",
        "victor-goldmane",
        people.DEMETRIOS,
    ],
    fragments={"rhinar": "show-no-mercy", "victor-goldmane": "aurum-aegis"},
    locations=[
        loc.DEATHMATCH_ARENA,
    ],
    equipment=["aurum-aegis", "gauntlets-of-iron-will", "hood-of-red-sand"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/high-seas/high-seas.md",
    story_type="digital-tiles",
    title="High Seas",
    characters=[
        "gravy",
        people.KELPIE,
        people.MORAY_LE_FAY,
        people.SCOOBA,
        people.SWABBIE,
        people.CAPTAIN_BLUDGE,
        people.CHOWDER,
        people.THANUELLA,
    ],
    locations=[
        loc.DREADFALL_REACH,
        loc.PIPER_S_PIER,
    ],
    regions=[
        reg.HIGH_SEAS,
    ],
    monsters=[
        mon.NECROPHAGE,
    ],
    fauna=[
        fauna.KRAKEN,
        fauna.SAWMAW,
        fauna.KULPIE,
    ],
    equipment=["dead-threads"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/monarch/monarch.md",
    story_type="digital-tiles",
    title="Monarch",
    characters=[
        "boltyn",
        people.BLASMOPHET,
        people.SOL,
        people.URSUR,
    ],
    fragments={"boltyn": "seek-enlightenment"},
    locations=[
        loc.BLASMOPHET_S_DOMAIN,
        loc.THE_GOLDEN_FIELDS,
        loc.THE_NORTHERN_REALMS,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
    ],
    weapons=["galaxxi-black"],
    equipment=["aether-ironweave"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/part-the-mistveil/part-the-mistveil.md",
    story_type="digital-tiles",
    title="Part the Mistveil",
    characters=[
        "enigma",
        "nuu",
        people.DAN_LU_KOTORI_GALEWARDEN,
        people.KAZUO,
        people.KOUKI,
        people.MASTER_UDO,
        people.SHIO,
        people.XIN,
    ],
    fragments={"enigma": "10000-year-reunion"},
    locations=[
        loc.AUI_S_SCALES_STRONGHOLDS,
        loc.KIROHIME_GATE,
        loc.MISTCLOAK_GULLY,
        loc.SEETHE,
    ],
    regions=[
        reg.MISTERIA,
        reg.THE_PITS,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/rosetta/rosetta.md",
    story_type="digital-tiles",
    title="Rosetta",
    characters=[
        "aurora",
        "florian",
        "melody",
        "oscilio",
        "verdance",
        people.DAVNIR,
        people.QUEEN_OF_CANDLEHOLD,
        people.YVOR,
    ],
    fragments={"aurora": "aurora-shooting-star", "melody": "sanctuary-of-aria"},
    locations=[
        loc.ANVILHEIM,
        loc.CANDLEHOLD,
        loc.ENION,
        loc.ROTWOOD,
        loc.VALAHAI,
    ],
    regions=[
        reg.ARIA,
    ],
    weapons=[
        "rotwood-reaper",
        "staff-of-verdant-shoots",
        "star-fall",
        "volzar-the-lightning-rod",
    ],
    equipment=["aether-bindings-of-the-third-age"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/tales-of-aria/tales-of-aria.md",
    story_type="digital-tiles",
    title="Tales of Aria",
    characters=[
        people.DAVNIR,
        people.QUEEN_OF_CANDLEHOLD,
        people.YVOR,
    ],
    locations=[
        loc.CANDLEHOLD,
        loc.ISENLOFT,
        loc.MOUNT_HEROIC,
        loc.MT_ISEN,
        loc.VOLTHAVEN,
    ],
    regions=[
        reg.ARIA,
    ],
    groups=[grp.WARDENS],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/the-hunted/the-hunted.md",
    story_type="digital-tiles",
    title="The Hunted",
    characters=[
        "arakni-huntsman",
        "cindra",
        "emperor",
        "taipanis",
        people.DR_KREST_MORTIMER_THE_FIXER,
    ],
    fragments={"cindra": "wrath-of-retribution"},
    locations=[
        loc.ASHVAHAN,
        loc.DESHVAHAN,
        loc.SKEIN,
    ],
    regions=[
        reg.THE_PITS,
        reg.VOLCOR,
    ],
    weapons=["graphene-chelicera", "mark-of-the-huntsman"],
    equipment=[
        "dragonscaler-flight-path",
        "kabuto-of-imperial-authority",
        "mask-of-deceit",
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/uprising/uprising.md",
    story_type="digital-tiles",
    title="Uprising",
    characters=["dromai", "emperor", "fai"],
    locations=[
        loc.ZANCARO,
    ],
    regions=[
        reg.VOLCOR,
    ],
    weapons=["storm-of-sandikai"],
    groups=[grp.DRACAI],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/README.md",
    story_type="digital-tiles",
    title="Readme",
    dry_run=True,
)
