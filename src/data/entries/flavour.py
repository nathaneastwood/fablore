"""Flavour page registrations — one ``db.upsert_story`` call per page.

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
    path="src/flavour/omens-of-the-third-age.md",
    story_type="flavour",
    title="Omens of the Third Age",
    heroes=["aurora", "lexi"],
    npcs=[
        # Already curated — named here only to link them to this page. Species and
        # status are left empty so the existing curated values are preserved.
        npc.ASTREA_QUAZOR,
        npc.AURIC_SEERESS,
        npc.LORD_SUTCLIFFE,
        npc.RUPIUS_AURIC_SCROLLMASTER,
        npc.YVOR,
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        npc.DARYAS_NIMBUS,
        npc.FREYA_ELDINGSTURM,
        npc.MAELA_ISULFV,
        npc.MAELA_SHARENA,
        npc.REZNYR_ELDINGSTURM,
        npc.SKYNDA_FEYSCOUT,
        npc.VYHARA_CLOUDBURST,
    ],
    locations=[
        loc.ENION,
        loc.VALAHAI,
        loc.VOLTHAVEN,
        loc.I_ARATHAEL,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
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
        npc.AMIRA_SURANA,
        npc.ASTRA_MORENA,
        npc.AUREA_CHAMPION_OF_THE_DAWN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.CHANCELLOR_HELENA_PRIMAVERA,
        npc.CHANCELLOR_HYPATIA,
        npc.CHIARA_SUNCREST,
        npc.DANU_ASHENGUARD,
        npc.ERSEBET,
        npc.GRAND_MAGISTER_THE_RADIANT,
        npc.HARLAND,
        npc.HAROLD_HONEYSETT,
        npc.JACKDAW,
        npc.KIRIGAMI,
        npc.MERLEN_RIVERA,
        npc.NESTUS,
        npc.SANNI,
        npc.SURAYA_ARCHANGEL_OF_KNOWLEDGE,
        npc.VIDYA_WILLOWMERE,
    ],
    regions=[
        reg.SOLANA,
    ],
    dry_run=True,
)

db.upsert_story(
    path="src/flavour/non-set-cards.md",
    story_type="flavour",
    title="Non-Set Cards",
    npcs=[
        npc.AEGIS_THE_SHIELD_OF_LIGHT,
        npc.AVALON_MESSENGER_OF_THE_DAWN,
        npc.BELLONA_THE_WARTUNE_HERALD,
        npc.THEMIS_KEEPER_OF_THE_SCALES,
        npc.YVOR,
    ],
    locations=[
        loc.AURIC_KEEP,
        loc.ENION,
        loc.VOLTHAVEN,
    ],
    regions=[
        reg.ARIA,
        reg.NEBULUS_RIFT,
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
        npc.BATBITER,
        npc.EMEVIERE,
        npc.FIGHTMASTER_KOX,
        npc.FIGHTMASTER_RUSTY,
        npc.LUCA_ARENA_CICERONE,
        npc.MOLOCA,
        npc.SLAPSTICK_SAL,
        npc.SPEAKEASY,
        # New with this set. Species is unattested in the flavour text.
        npc.FOREMAN_PEBB,
        npc.FUGGER_GRIMES,
        npc.HELX,
        npc.SALVADOR_STALLION,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.DEN_OF_BEASTS,
        loc.GRINNING_BOAR_CANTINA,
        # A Deathmatch venue, distinct from "The Maw" in the Pits. Region is left
        # blank to match its siblings (The Undercroft, The Moat, Arena Barracks).
        loc.INFERNAL_MAW,
        loc.THE_MOAT,
        loc.THE_UNDERCROFT,
    ],
    regions=[
        reg.THE_SAVAGE_LANDS,
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
        npc.AEGIS_THE_SHIELD_OF_LIGHT,
        # New with this set. Species is unattested in the flavour text, so it is
        # left to default to "Unknown" rather than being guessed.
        npc.MAELA_ONE_EYE,
    ],
    locations=[
        loc.ANVILHEIM,
        loc.THE_EVERFEST_CARNIVAL,
    ],
    regions=[
        reg.ARIA,
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
        npc.FARRIS,
        npc.FIGHTMASTER_KOX,
        npc.FIGHTMASTER_RUSTY,
        npc.LIEUTENANT_TIMAEUS,
        # New with this set. Species is unattested in the flavour text.
        npc.CAPTAIN_SHEVEZ,
        npc.INQUISITOR_ARICIA,
        npc.LUCILLA_THE_SETTING_SUN,
        npc.TASHA_OF_DESHVAHAN,
        npc.THE_BASTION,
        npc.VANIK_SILVERTOOTH,
    ],
    locations=[
        loc.DAWNHAVEN,
        loc.DESHVAHAN,
        loc.FIDDLER_S_GREEN,
        loc.NEELASHA,
        loc.OCTOMILITIA,
        loc.THE_SOLARIUM,
        loc.VALAHAI,
    ],
    regions=[
        reg.DEMONASTERY,
        reg.SOLANA,
        reg.THE_SAVAGE_LANDS,
        reg.VOLCOR,
    ],
    dry_run=True,
)
