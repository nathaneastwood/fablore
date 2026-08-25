"""Digital tiles page registrations — one ``db.upsert_story`` call per page.

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
    path="src/digital-tiles/omens-of-the-third-age/omens-of-the-third-age.md",
    story_type="digital-tiles",
    title="Omens of the Third Age",
    characters=[
        "aurora",
        "oscilio",
        "zyggy",
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.MAELA_ISULFV,
        people.YVOR,
        # New with this set.
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
    # The Fabricate tile is signed "Jules Teklovossen" — that is the hero
    # Teklovossen under his full name, not the separate character row of that name.
    characters=["dash", "teklovossen"],
    fragments={"dash": "dash-io", "teklovossen": "fabricate"},
    locations=[
        loc.COGWERX_CONGLOMERATE,
        # New with this set. The realm of data made manifest, reached through Teklo's
        # Data Link — named on the main-story and flavour pages for this set too.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.BELLONA_THE_WARTUNE_HERALD,
        people.SOL,
        # New with this set. Kind is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        people.BOO,
        # A dragon, not a person — there is no dragons table, so it is carried
        # as a character row and relabelled to "creature" in hints_supplement.json.
        people.MIRAGAI,
    ],
    locations=[
        # New with this set. The Demonastery's mortuary quarter.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
        # New with this set, all three named only as tavern-tale creatures.
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
    # Hood of Red Sand names "The Terror of the Golden Sands" — that is Kassai.
    characters=[
        "kassai",
        "olympia",
        "rhinar",
        "victor-goldmane",
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.DEMETRIOS,
    ],
    fragments={"rhinar": "show-no-mercy", "victor-goldmane": "aurum-aegis"},
    locations=[
        # New, though it is named on eleven other pages already. Region is left
        # blank to match its siblings (The Moat, The Undercroft, Arena Barracks).
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.KELPIE,
        people.MORAY_LE_FAY,
        people.SCOOBA,
        people.SWABBIE,
        # New with this set.
        people.CAPTAIN_BLUDGE,
        people.CHOWDER,
        # "Dhani death-mage" — Dhani is the culture, not a kind, so kind is
        # left to default to "Unknown".
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
        # New with this set, named only as an ingredient on Chowder's menu.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
        people.DAN_LU_KOTORI_GALEWARDEN,
        people.KAZUO,
        people.KOUKI,
        people.MASTER_UDO,
        people.SHIO,
        people.XIN,
    ],
    fragments={"enigma": "10000-year-reunion"},
    locations=[
        # Spelled to match the live row that Wanderings in the Mists registers.
        # "Aui's Scale Strongholds" is an unlinked duplicate awaiting deletion.
        loc.AUI_S_SCALES_STRONGHOLDS,
        loc.KIROHIME_GATE,
        loc.MISTCLOAK_GULLY,
        # Murky Water's "Butcher" is the hero Riptide; deliberately not linked, as
        # the tile never names him and the DB holds two unrelated Butcher character rows.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
        # Already curated — named here only to link them to this page. Kind and
        # status are left empty so the existing curated values are preserved.
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
