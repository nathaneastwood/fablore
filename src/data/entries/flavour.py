"""Flavour page registrations — one ``db.upsert_story`` call per page.

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
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    heroes=["aurora", "lexi"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        NPCEntry(name="Astrea Quazor"),
        NPCEntry(name="Auric Seeress"),
        NPCEntry(name="Lord Sutcliffe"),
        NPCEntry(name="Rupius, Auric Scrollmaster"),
        NPCEntry(name="Yvor"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Daryas Nimbus"),
        NPCEntry(name="Freya Eldingsturm"),
        NPCEntry(name="Maela Isulfv"),
        NPCEntry(name="Maela Sharena"),
        NPCEntry(name="Reznyr Eldingsturm"),
        NPCEntry(name="Skynda Feyscout"),
        NPCEntry(name="Vyhara Cloudburst"),
    ],
    locations=[
        LocationEntry("Enion", region="Aria"),
        LocationEntry("Valahai", region="Aria"),
        LocationEntry("Volthaven", region="Aria"),
        LocationEntry("i'Arathael"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    dry_run=True,
)

# Monarch's four Heralds are printed without flavour text; the lines the page used
# to carry belong to the promo printings and now live on non-set-cards.md. This
# declaration exists to repoint Themis, Aegis and Avalon off this page — Bellona
# stays, still named by Chiara Suncrest's line on MON081.
db.upsert_story(
    path="src/flavour/monarch.md",
    story_type="flavour",
    title="Monarch",
    heroes=["prism"],
    hero_fragments={"prism": "celestial-cataclysm---mon062"},
    npcs=[
        NPCEntry(name="Amira Surana"),
        NPCEntry(name="Astra Morena"),
        NPCEntry(name="Aurea, Champion of the Dawn"),
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Chancellor Helena Primavera"),
        NPCEntry(name="Chancellor Hypatia"),
        NPCEntry(name="Chiara Suncrest"),
        NPCEntry(name="Danu Ashenguard"),
        NPCEntry(name="Ersebet"),
        NPCEntry(name="Grand Magister, the Radiant"),
        NPCEntry(name="Harland"),
        NPCEntry(name="Harold Honeysett"),
        NPCEntry(name="Jackdaw"),
        NPCEntry(name="Kirigami"),
        NPCEntry(name="Merlen Rivera"),
        NPCEntry(name="Nestus"),
        NPCEntry(name="Sanni"),
        NPCEntry(name="Suraya, Archangel of Knowledge"),
        NPCEntry(name="Vidya Willowmere"),
    ],
    regions=[
        RegionEntry("Solana"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/non-set-cards.md",
    story_type="flavour",
    title="Non-Set Cards",
    npcs=[
        NPCEntry(name="Aegis, the Shield of Light"),
        NPCEntry(name="Avalon, Messenger of the Dawn"),
        NPCEntry(name="Bellona, the Wartune Herald"),
        NPCEntry(name="Themis, Keeper of the Scales"),
        NPCEntry(name="Yvor"),
    ],
    locations=[
        LocationEntry("Auric Keep", region="Nebulus Rift"),
        LocationEntry("Enion", region="Aria"),
        LocationEntry("Volthaven", region="Aria"),
    ],
    regions=[
        RegionEntry("Aria"),
        RegionEntry("Nebulus Rift"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/super-slam.md",
    story_type="flavour",
    title="Super Slam",
    heroes=["kayo", "lyath", "pleiades", "tuffnut", "victor-goldmane"],
    npcs=[
        # Already curated — named here only to link them to this page. The DB holds
        # the fightmasters under their bare names, not the "Fightmaster X" form the
        # cards use.
        NPCEntry(name="Batbiter"),
        NPCEntry(name="Emeviere"),
        NPCEntry(name="Fightmaster Kox"),
        NPCEntry(name="Fightmaster Rusty"),
        NPCEntry(name="Luca, Arena Cicerone"),
        NPCEntry(name="Moloca"),
        NPCEntry(name="Slapstick Sal"),
        NPCEntry(name="Speakeasy"),
        # New with this set. Species is unattested in the flavour text.
        NPCEntry(name="Foreman Pebb"),
        NPCEntry(name="Fugger Grimes"),
        NPCEntry(name="Helx"),
        NPCEntry(name="Salvador Stallion"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("Den of Beasts"),
        LocationEntry("Grinning Boar Cantina"),
        # A Deathmatch venue, distinct from "The Maw" in the Pits. Region is left
        # blank to match its siblings (The Undercroft, The Moat, Arena Barracks).
        LocationEntry("Infernal Maw"),
        LocationEntry("The Moat"),
        LocationEntry("The Undercroft"),
    ],
    regions=[
        RegionEntry("The Savage Lands"),
    ],
    dry_run=True,
)
# TODO: group — Baleful Horde, Boulder Clan, Champions of Chivalry, Fury Fists,
# Glorytown Gladiators, Jungle Slayers, Mythmakers, Prowlers, Wild Wonders

db.upsert_story(
    path="src/flavour/mastery-pack-guardian.md",
    story_type="flavour",
    title="Mastery Pack Guardian",
    heroes=["fai", "valda"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        # MPG029 prints "Archangel Aegis"; that is a new epithet for the Herald of
        # Protection already registered under her Monarch title, not a new character.
        NPCEntry(name="Aegis, the Shield of Light"),
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        NPCEntry(name="Maela One-eye"),
    ],
    locations=[
        LocationEntry("Anvilheim"),
        LocationEntry("The Everfest Carnival", region="Aria"),
    ],
    regions=[
        RegionEntry("Aria"),
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/mastery-pack-warrior.md",
    story_type="flavour",
    title="Mastery Pack Warrior",
    npcs=[
        # Already curated — named here only to link them to this page.
        # MPW048 prints "Lieutenant Farris"; Pride of the Ironsongs introduces the
        # same Solanian lieutenant on the same Savage Lands frontier.
        NPCEntry(name="Farris"),
        NPCEntry(name="Fightmaster Kox"),
        NPCEntry(name="Fightmaster Rusty"),
        NPCEntry(name="Lieutenant Timaeus"),
        # New with this set. Species is unattested in the flavour text.
        NPCEntry(name="Captain Shevez"),
        NPCEntry(name="Inquisitor Aricia"),
        NPCEntry(name="Lucilla the Setting Sun"),
        NPCEntry(name="Tasha of Deshvahan"),
        NPCEntry(name="The Bastion"),
        NPCEntry(name="Vanik Silvertooth"),
    ],
    locations=[
        LocationEntry("Dawnhaven"),
        LocationEntry("Deshvahan", region="Volcor"),
        LocationEntry("Fiddler's Green", region="High Seas"),
        LocationEntry("Neelasha"),
        LocationEntry("Octomilitia", region="Solana"),
        LocationEntry("Solarium", region="Solana"),
        LocationEntry("Valahai", region="Aria"),
    ],
    regions=[
        RegionEntry("Demonastery"),
        RegionEntry("Solana"),
        RegionEntry("The Savage Lands"),
        RegionEntry("Volcor"),
    ],
    dry_run=True,
)
