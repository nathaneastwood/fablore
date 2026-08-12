"""Digital tiles page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

# Every section module imports the whole entry set, so extending a declaration
# with a new entity type never also means editing the import. Unused names are
# deliberate.
from db import (  # noqa: F401
    FaunaEntry,
    FloraEntry,
    FoodDrinkEntry,
    MonsterEntry,
    NarratedVideoEntry,
)

# NPCs, locations and regions are referenced, never constructed. Their ids are
# hashes of the fields written at the call site, so a second literal for the same
# entity competes with the first row instead of reusing it — that is how
# "The Shadow Crypts" became two rows. The canonical definition of each lives
# in entries/catalogue/; the three names are deliberately not imported above, so
# writing LocationEntry(...) here is a NameError rather than a silent new row.
from entries.catalogue import locations as loc, npcs as npc, regions as reg  # noqa: F401
from entries._runner import db

db.upsert_story(
    path="src/digital-tiles/omens-of-the-third-age/omens-of-the-third-age.md",
    story_type="digital-tiles",
    title="Omens of the Third Age",
    heroes=["aurora", "oscilio", "zyggy"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.MAELA_ISULFV,
        npc.YVOR,
        # New with this set.
        npc.KARL,
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
    # Teklovossen under his full name, not the separate NPC row of that name.
    heroes=["dash", "teklovossen"],
    hero_fragments={"dash": "dash-io", "teklovossen": "fabricate"},
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
    dry_run=True,
)
# TODO: group — Steelstreet Enforcers

db.upsert_story(
    path="src/digital-tiles/compendium-of-rathe/compendium-of-rathe.md",
    story_type="digital-tiles",
    title="Compendium of Rathe",
    heroes=["dorinthea", "jarl"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.SOL,
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        npc.BOO,
        # A dragon, not a person — there is no dragons table, so it is carried
        # as an NPC row and relabelled to "creature" in hints_supplement.json.
        npc.MIRAGAI,
    ],
    locations=[
        loc.DEMONASTERY,
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
    heroes=["azalea", "dorinthea", "emperor", "kassai", "teklovossen"],
    hero_fragments={
        "dorinthea": "courage-of-bladehold",
        "emperor": "cindering-foresight",
        "kassai": "cintari-saber",
        "teklovossen": "teklovossens-workshop",
    },
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.GENERAL_EKODA,
        npc.LORD_SABUTO,
        npc.LORD_SUTCLIFFE,
        npc.MAGNUS_THE_VIGILANT,
        npc.SOL,
        npc.THEODORE_HAMILTON_SCARBOROUGH,
        npc.IRUNAMEABH,
    ],
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
        FaunaEntry(name="Azeri"),
        FaunaEntry(name="Rek'vas"),
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
    dry_run=True,
)
# TODO: group — Lost Clans, Mugenshi

db.upsert_story(
    path="src/digital-tiles/everfest/everfest.md",
    story_type="digital-tiles",
    title="Everfest",
    heroes=["boltyn"],
    hero_fragments={"boltyn": "swarming-gloomveil"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS,
        npc.LORD_SUTCLIFFE,
        npc.SOL,
    ],
    locations=[
        loc.DEMONASTERY,
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
        FaunaEntry(name="Kaie'o"),
        FaunaEntry(name="Kraken"),
        FaunaEntry(name="Meep"),
        # New with this set, all three named only as tavern-tale creatures.
        FaunaEntry(name="Ebon Serpent"),
        FaunaEntry(name="Kumiho"),
        FaunaEntry(name="Mireoa"),
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
# TODO: group — Shieldbearers, The Grey

db.upsert_story(
    path="src/digital-tiles/heavy-hitters/heavy-hitters.md",
    story_type="digital-tiles",
    title="Heavy Hitters",
    # Hood of Red Sand names "The Terror of the Golden Sands" — that is Kassai.
    heroes=["kassai", "olympia", "rhinar", "victor-goldmane"],
    hero_fragments={"rhinar": "show-no-mercy", "victor-goldmane": "aurum-aegis"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.DEMETRIOS,
    ],
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
    heroes=["gravy"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.KELPIE,
        npc.MORAY_LE_FAY,
        npc.SCOOBA,
        npc.SWABBIE,
        # New with this set.
        npc.CAPTAIN_BLUDGE,
        npc.CHOWDER,
        # "Dhani death-mage" — Dhani is the culture, not a species, so species is
        # left to default to "Unknown".
        npc.THANUELLA,
    ],
    locations=[
        loc.DREADFALL_REACH,
        loc.PIPER_S_PIER,
    ],
    regions=[
        reg.HIGH_SEAS,
    ],
    monsters=[
        MonsterEntry(name="Necrophage"),
    ],
    fauna=[
        FaunaEntry(name="Kraken"),
        FaunaEntry(name="Sawmaw"),
        # New with this set, named only as an ingredient on Chowder's menu.
        FaunaEntry(name="Kulpie"),
    ],
    equipment=["dead-threads"],
    dry_run=True,
)

db.upsert_story(
    path="src/digital-tiles/monarch/monarch.md",
    story_type="digital-tiles",
    title="Monarch",
    heroes=["boltyn"],
    hero_fragments={"boltyn": "seek-enlightenment"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.BLASMOPHET,
        npc.SOL,
        npc.URSUR,
    ],
    locations=[
        loc.BLASMOPHET_S_DOMAIN,
        loc.SOLANA,
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
    heroes=["enigma", "nuu"],
    hero_fragments={"enigma": "10000-year-reunion"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.DAN_LU_KOTORI_GALEWARDEN,
        npc.KAZUO,
        npc.KOUKI,
        npc.MASTER_UDO,
        npc.SHIO,
        npc.XIN,
    ],
    locations=[
        # Spelled to match the live row that Wanderings in the Mists registers.
        # "Aui's Scale Strongholds" is an unlinked duplicate awaiting deletion.
        loc.AUI_S_SCALES_STRONGHOLDS,
        loc.KIROHIME_GATE,
        loc.MISTCLOAK_GULLY,
        # Murky Water's "Butcher" is the hero Riptide; deliberately not linked, as
        # the tile never names him and the DB holds two unrelated Butcher NPCs.
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
    heroes=["aurora", "florian", "melody", "oscilio", "verdance"],
    hero_fragments={"aurora": "aurora-shooting-star", "melody": "sanctuary-of-aria"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.DAVNIR,
        npc.QUEEN_OF_CANDLEHOLD,
        npc.YVOR,
    ],
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
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.DAVNIR,
        npc.QUEEN_OF_CANDLEHOLD,
        npc.YVOR,
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
    dry_run=True,
)
# TODO: group — Wardens

db.upsert_story(
    path="src/digital-tiles/the-hunted/the-hunted.md",
    story_type="digital-tiles",
    title="The Hunted",
    heroes=["arakni-huntsman", "cindra", "emperor", "taipanis"],
    hero_fragments={"cindra": "wrath-of-retribution"},
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.DR_KREST_MORTIMER_THE_FIXER,
    ],
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
    heroes=["dromai", "emperor", "fai"],
    locations=[
        loc.ZANCARO,
    ],
    regions=[
        reg.VOLCOR,
    ],
    weapons=["storm-of-sandikai"],
    dry_run=True,
)
