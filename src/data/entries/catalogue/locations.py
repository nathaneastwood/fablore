"""Canonical location definitions — the one place each place is described.

``location_id`` is a hash of ``name`` *and* ``region_id``
(``_domain._location_id``), so the region is part of the identity: the same place
written once with a region and once without is two rows in the database, silently.
``The Shadow Crypts`` and ``Legendarium`` each became two rows that way. ``Deathmatch
Arena`` and ``The Moat`` were caught before they did: some pages named a region and
some did not, so the fork was latent in the declarations rather than in the data.
Define each location once, here, with its region.

``notes`` is deliberately absent: location lore text belongs to ``descriptions.py``,
which owns that column. Story modules reference these as ``loc.NAME``.
"""

from __future__ import annotations

from db import LocationEntry


# -------------------------------------------------------------------------
# Aria
# -------------------------------------------------------------------------

ALDENGROVE = LocationEntry("Aldengrove", region="Aria")
ALDEVYR = LocationEntry("Aldevyr", region="Aria")
CANDLEHOLD = LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold")
ENION = LocationEntry("Enion", region="Aria", lore_fragment="enion")
FRACTAL_SCAR = LocationEntry("Fractal Scar", region="Aria")
ISENLOFT = LocationEntry("Isenloft", region="Aria")
ISEN_RANGES = LocationEntry("Isen Ranges", region="Aria")
LEGENDARIUM = LocationEntry("Legendarium", region="Aria", lore_fragment="the-everfest-carnival")
MILESIAN_RANGES = LocationEntry("Milesian Ranges", region="Aria")
MOUNT_HEROIC = LocationEntry("Mount Heroic", region="Aria")
MT_ISEN = LocationEntry("Mt. Isen", region="Aria", lore_fragment="mount-isen")
ROTWOOD = LocationEntry("Rotwood", region="Aria")
SHYLDVERK = LocationEntry("Shyldverk", region="Aria", lore_fragment="shyldverk")
THE_EVERFEST_CARNIVAL = LocationEntry("The Everfest Carnival", region="Aria", lore_fragment="the-everfest-carnival")
THE_FLOW = LocationEntry("The Flow", region="Aria", lore_fragment="the-flow")
THE_GOLDEN_GNOME = LocationEntry("The Golden Gnome", region="Aria")
THE_MAELA = LocationEntry("The Maela", region="Aria")
THE_VALDUR = LocationEntry("The Valdur", region="Aria")
VALAHAI = LocationEntry("Valahai", region="Aria", lore_fragment="valahai")
VOLTHAVEN = LocationEntry("Volthaven", region="Aria", lore_fragment="enion")

# -------------------------------------------------------------------------
# Demonastery
# -------------------------------------------------------------------------

BLASMOPHET_S_DOMAIN = LocationEntry("Blasmophet's Domain", region="Demonastery")
DEMONASTERY = LocationEntry("Demonastery", region="Demonastery")
DIMENXXIONAL_GATEWAY = LocationEntry("Dimenxxional Gateway", region="Demonastery")
NECROPOLIS = LocationEntry("Necropolis", region="Demonastery")
THE_SHADOW_CRYPTS = LocationEntry("The Shadow Crypts", region="Demonastery", lore_fragment="the-shadow-crypts")

# -------------------------------------------------------------------------
# High Seas
# -------------------------------------------------------------------------

DREADFALL_REACH = LocationEntry("Dreadfall Reach", region="High Seas", lore_fragment="dreadfall-reach")
FIDDLER_S_GREEN = LocationEntry("Fiddler's Green", region="High Seas")
PIPER_S_PIER = LocationEntry("Piper's Pier", region="High Seas", lore_fragment="pipers-pier")

# -------------------------------------------------------------------------
# Metrix
# -------------------------------------------------------------------------

COGWERX_CONGLOMERATE = LocationEntry("Cogwerx Conglomerate", region="Metrix", lore_fragment="cogwerx-conglomerate")
EIDOLON = LocationEntry("Eidolon", region="Metrix")
IRON_ASSEMBLY = LocationEntry("Iron Assembly", region="Metrix", lore_fragment="iron-assembly")
LOWLAKE = LocationEntry("Lowlake", region="Metrix")
TEKLO_INDUSTRIES = LocationEntry("Teklo Industries", region="Metrix", lore_fragment="teklo-industries")

# -------------------------------------------------------------------------
# Misteria
# -------------------------------------------------------------------------

AUI_S_SCALES_STRONGHOLDS = LocationEntry("Aui's Scales Strongholds", region="Misteria")
IKARU = LocationEntry("Ikaru", region="Misteria", lore_fragment="ikaru")
KIROHIME_GATE = LocationEntry("Kirohime Gate", region="Misteria")
MISTCLOAK_GULLY = LocationEntry("Mistcloak Gully", region="Misteria", lore_fragment="mistcloak-gully")
MUGENSHI_ANCESTRAL_SHRINE = LocationEntry("Mugenshi Ancestral Shrine", region="Misteria")
MUGENSHI_GORGE = LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge")
MUGENSHI_VILLAGE = LocationEntry("Mugenshi Village", region="Misteria")
SKYLARK_PEAK = LocationEntry("Skylark Peak", region="Misteria")

# -------------------------------------------------------------------------
# Nebulus Rift
# -------------------------------------------------------------------------

ARCANE_HALL = LocationEntry("Arcane Hall", region="Nebulus Rift", lore_fragment="auric-keep")
ASTRAL_BRIDGE = LocationEntry("Astral Bridge", region="Nebulus Rift", lore_fragment="astral-bridge")
AURIC_KEEP = LocationEntry("Auric Keep", region="Nebulus Rift", lore_fragment="auric-keep")
VOLTARIS_GEM = LocationEntry("Voltaris Gem", region="Nebulus Rift", lore_fragment="astral-bridge")

# -------------------------------------------------------------------------
# Solana
# -------------------------------------------------------------------------

AMPHITHEATRE = LocationEntry("Amphitheatre", region="Solana")
CEREMONIAL_CHAMBER = LocationEntry("Ceremonial Chamber", region="Solana")
GOLDEN_CHARIOT = LocationEntry("Golden Chariot", region="Solana")
HAND_OF_SOL = LocationEntry("Hand of Sol", region="Solana", lore_fragment="the-hand-of-sol")
IRONSONG_FORGE = LocationEntry("Ironsong Forge", region="Solana")
LIBRARY_OF_ILLUMINATION = LocationEntry("Library of Illumination", region="Solana")
OCTOMILITIA = LocationEntry("Octomilitia", region="Solana")
SILVARIUM = LocationEntry("Silvarium", region="Solana")
SOLANA = LocationEntry("Solana", region="Solana")
SOLARIUM = LocationEntry("Solarium", region="Solana")
SOLSTICE_OF_LAURELS = LocationEntry("Solstice of Laurels", region="Solana", lore_fragment="solstice-of-laurels")
THE_AWAKENING_CEREMONY = LocationEntry(
    "The Awakening Ceremony", region="Solana", lore_fragment="the-awakening-ceremony"
)
THE_GOLDEN_FIELDS = LocationEntry("The Golden Fields", region="Solana")
THE_GRAND_COUNCIL = LocationEntry("The Grand Council", region="Solana", lore_fragment="the-grand-council")
THE_LIGHT_OF_SOL = LocationEntry("The Light of Sol", region="Solana", lore_fragment="the-light-of-sol")
THE_NORTHERN_REALMS = LocationEntry("The Northern Realms", region="Solana", lore_fragment="the-northern-realms")
THE_SOLARIUM = LocationEntry("The Solarium", region="Solana")

# -------------------------------------------------------------------------
# The Pits
# -------------------------------------------------------------------------

BARTON_S_HOUSE = LocationEntry("Barton's House", region="The Pits")
BLACKJACK_S_TAVERN = LocationEntry(
    "Blackjack's Tavern", region="The Pits", lore_fragment="blackjacks-mercenary-company"
)
SEETHE = LocationEntry("Seethe", region="The Pits")
SKEIN = LocationEntry("Skein", region="The Pits")
THE_MAW = LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw")

# -------------------------------------------------------------------------
# The Savage Lands
# -------------------------------------------------------------------------

DEATHMATCH_ARENA = LocationEntry("Deathmatch Arena", region="The Savage Lands")
FORWARD_CAMPS = LocationEntry("Forward Camps", region="The Savage Lands")
RHINAR_S_TERRITORY = LocationEntry("Rhinar's Territory", region="The Savage Lands")
THE_MOAT = LocationEntry("The Moat", region="The Savage Lands")
THE_SAVAGE_WILDS = LocationEntry("The Savage Wilds", region="The Savage Lands")

# -------------------------------------------------------------------------
# Volcor
# -------------------------------------------------------------------------

ASHVAHAN = LocationEntry("Ashvahan", region="Volcor", lore_fragment="ashvahan")
DESHVAHAN = LocationEntry("Deshvahan", region="Volcor", lore_fragment="deshvahan")
IMPERIAL_PALACE = LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court")
THE_BADLANDS = LocationEntry("The Badlands", region="Volcor")
ZANCARO = LocationEntry("Zancaro", region="Volcor")

# -------------------------------------------------------------------------
# No region recorded
# -------------------------------------------------------------------------

ANVILHEIM = LocationEntry("Anvilheim")
DAWNHAVEN = LocationEntry("Dawnhaven")
DEN_OF_BEASTS = LocationEntry("Den of Beasts")
GRINNING_BOAR_CANTINA = LocationEntry("Grinning Boar Cantina")
INFERNAL_MAW = LocationEntry("Infernal Maw")
I_ARATHAEL = LocationEntry("i'Arathael")
NEELASHA = LocationEntry("Neelasha")
NEVEREST = LocationEntry("Neverest")
SHADOWREALM = LocationEntry("Shadowrealm")
THE_ABYSS = LocationEntry("The Abyss")
THE_BROKEN_CHARIOT_TAVERN = LocationEntry("The Broken Chariot Tavern")
THE_UNDERCROFT = LocationEntry("The Undercroft")
