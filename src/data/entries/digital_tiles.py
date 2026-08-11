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
    LocationEntry,
    MonsterEntry,
    NarratedVideoEntry,
    NPCEntry,
    RegionEntry,
)
from entries._runner import db

db.upsert_story(
    path="src/digital-tiles/omens-of-the-third-age/omens-of-the-third-age.md",
    story_type="digital-tiles",
    title="Omens of the Third Age",
    heroes=["aurora", "oscilio", "zyggy"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Maela Isulfv"),
        NPCEntry(name="Yvor"),
        # New with this set.
        NPCEntry(name="Karl"),
    ],
    locations=[
        LocationEntry("Astral Bridge", region="Nebulus Rift", lore_fragment="astral-bridge"),
        LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep"),
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
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
        LocationEntry("Cogwerx Conglomerate", region="Metrix", lore_fragment="cogwerx-conglomerate"),
        # New with this set. The realm of data made manifest, reached through Teklo's
        # Data Link — named on the main-story and flavour pages for this set too.
        LocationEntry("Eidolon", region="Metrix"),
        LocationEntry("Iron Assembly", region="Metrix", lore_fragment="iron-assembly"),
        LocationEntry("Lowlake", region="Metrix"),
        LocationEntry("Teklo Industries", region="Metrix", lore_fragment="teklo-industries"),
    ],
    regions=[
        RegionEntry("Metrix"),
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
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Sol"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Boo"),
        # A dragon, not a person — there is no dragons table, so it is carried
        # as an NPC row and relabelled to "creature" in hints_supplement.json.
        NPCEntry(name="Miragai", species="Dragon"),
    ],
    locations=[
        LocationEntry("Demonastery", region="Demonastery"),
        # New with this set. The Demonastery's mortuary quarter.
        LocationEntry("Necropolis", region="Demonastery"),
        LocationEntry("The Awakening Ceremony", region="Solana", lore_fragment="the-awakening-ceremony"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("High Seas"),
        RegionEntry("Misteria"),
        RegionEntry("Solana"),
        RegionEntry("Volcor"),
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
        NPCEntry(name="General Ekoda"),
        NPCEntry(name="Lord Sabuto"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Magnus the Vigilant"),
        NPCEntry(name="Sol"),
        NPCEntry(name="Theodore Hamilton Scarborough"),
        NPCEntry(name="Írunaméabh"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court"),
        LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge"),
        LocationEntry("The Badlands", region="Volcor"),
        LocationEntry("The Broken Chariot Tavern"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("Zancaro", region="Volcor"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Metrix"),
        RegionEntry("Misteria"),
        RegionEntry("Solana"),
        RegionEntry("The Pits"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
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
        NPCEntry(name="Jezabelle, Everfest Healer and Allsorts"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Sol"),
    ],
    locations=[
        LocationEntry("Demonastery", region="Demonastery"),
        LocationEntry("Isenloft", region="Aria"),
        LocationEntry("Skylark Peak", region="Misteria"),
        LocationEntry("The Badlands", region="Volcor"),
        LocationEntry("The Everfest Carnival", region="Aria", lore_fragment="the-everfest-carnival"),
        LocationEntry("The Golden Gnome", region="Aria"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Demonastery"),
        RegionEntry("Metrix"),
        RegionEntry("Misteria"),
        RegionEntry("The Pits"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
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
        NPCEntry(name="Demetrios"),
    ],
    locations=[
        # New, though it is named on eleven other pages already. Region is left
        # blank to match its siblings (The Moat, The Undercroft, Arena Barracks).
        LocationEntry("Deathmatch Arena"),
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
        NPCEntry(name="Kelpie"),
        NPCEntry(name="Moray Le Fay"),
        NPCEntry(name="Scooba"),
        NPCEntry(name="Swabbie"),
        # New with this set.
        NPCEntry(name="Captain Bludge"),
        NPCEntry(name="Chowder", species="Zombie"),
        # "Dhani death-mage" — Dhani is the culture, not a species, so species is
        # left to default to "Unknown".
        NPCEntry(name="Thanuella"),
    ],
    locations=[
        LocationEntry("Dreadfall Reach", region="High Seas"),
        LocationEntry("Piper's Pier", region="High Seas"),
    ],
    regions=[
        RegionEntry("High Seas"),
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
        NPCEntry(name="Blasmophet"),
        NPCEntry(name="Sol"),
        NPCEntry(name="Ursur"),
    ],
    locations=[
        LocationEntry("Blasmophet's Domain", region="Demonastery"),
        LocationEntry("Solana", region="Solana"),
        LocationEntry("The Golden Fields", region="Solana"),
        LocationEntry("The Northern Realms", region="Solana", lore_fragment="the-northern-realms"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
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
        NPCEntry(name="Dan Lu, Kotori Galewarden"),
        NPCEntry(name="Kazuo"),
        NPCEntry(name="Kouki"),
        NPCEntry(name="Master Udo"),
        NPCEntry(name="Shio"),
        NPCEntry(name="Xin"),
    ],
    locations=[
        # Spelled to match the live row that Wanderings in the Mists registers.
        # "Aui's Scale Strongholds" is an unlinked duplicate awaiting deletion.
        LocationEntry("Aui's Scales Strongholds", region="Misteria"),
        LocationEntry("Kirohime Gate", region="Misteria"),
        LocationEntry("Mistcloak Gully", region="Misteria", lore_fragment="mistcloak-gully"),
        # Murky Water's "Butcher" is the hero Riptide; deliberately not linked, as
        # the tile never names him and the DB holds two unrelated Butcher NPCs.
        LocationEntry("Seethe", region="The Pits"),
    ],
    regions=[
        RegionEntry("Misteria"),
        RegionEntry("The Pits"),
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
        NPCEntry(name="Davnir"),
        NPCEntry(name="Queen of Candlehold"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold"),
        LocationEntry("Enion", region="Aria", lore_fragment="enion"),
        LocationEntry("Rotwood", region="Aria"),
        LocationEntry("Valahai", region="Aria", lore_fragment="valahai"),
    ],
    regions=[
        RegionEntry("Aria"),
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
        NPCEntry(name="Davnir"),
        NPCEntry(name="Queen of Candlehold"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold"),
        LocationEntry("Isenloft", region="Aria"),
        LocationEntry("Mount Heroic", region="Aria"),
        LocationEntry("Mt. Isen", region="Aria", lore_fragment="mount-isen"),
        LocationEntry("Volthaven", region="Aria", lore_fragment="enion"),
    ],
    regions=[
        RegionEntry("Aria"),
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
        NPCEntry(name="Dr. Krest Mortimer, 'The Fixer'"),
    ],
    locations=[
        LocationEntry("Ashvahan", region="Volcor"),
        LocationEntry("Deshvahan", region="Volcor", lore_fragment="deshvahan"),
        LocationEntry("Skein", region="The Pits"),
    ],
    regions=[
        RegionEntry("The Pits"),
        RegionEntry("Volcor"),
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
        LocationEntry("Zancaro", region="Volcor"),
    ],
    regions=[
        RegionEntry("Volcor"),
    ],
    weapons=["storm-of-sandikai"],
    dry_run=True,
)
