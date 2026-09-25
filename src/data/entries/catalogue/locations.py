"""Canonical location definitions — the one place each place is described.

``location_id`` is a hash of ``name`` *and* ``region_id``
(``_domain._location_id``), so the region is part of the identity: the same place
written once with a region and once without is two rows in the database, silently.
That is exactly how ``Deathmatch Arena``, ``The Moat``, ``The Shadow Crypts`` and
``Legendarium`` forked. Define each location once, here, with its region.

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
ARCTUROS = LocationEntry("Arcturos", region="Aria")
BLEAK_EXPANSE = LocationEntry("Bleak Expanse", region="Aria", lore_fragment="the-bleak-expanse")
BOULDERHEAD_ISLAND = LocationEntry("Boulderhead Island", region="Aria")
CANDLEHOLD = LocationEntry("Candlehold", region="Aria", lore_fragment="candlehold")
CANDLELIGHT_CLEARING = LocationEntry("Candlelight Clearing", region="Aria")
ENION = LocationEntry("Enion", region="Aria", lore_fragment="enion")
FENSALIR = LocationEntry("Fensalir", region="Aria")
FRACTAL_SCAR = LocationEntry("Fractal Scar", region="Aria")
HIGHLOFT_INN = LocationEntry("Highloft Inn", region="Aria")
"""The row already existed; world-of-rathe/aria.md is the first declaration to name it."""
ISENLOFT = LocationEntry("Isenloft", region="Aria")
ISENRI_SAKE_BREWERY = LocationEntry("Isenri Sake Brewery", region="Aria")
"""A named building in Larinkmorth — main-story/mastery-pack-guardian/trouble-in-larinkmorth.md:19."""
ISEN_RANGES = LocationEntry("Isen Ranges", region="Aria")
LARINKMORTH = LocationEntry("Larinkmorth", region="Aria", lore_fragment="larinkmorth")
LEGENDARIUM = LocationEntry("Legendarium", region="Aria", lore_fragment="the-everfest-carnival")
MIGHT_N_MEAD = LocationEntry("Might n' Mead", region="Aria")
MILLENNIUM_TREE = LocationEntry("The Millennium Tree", region="Aria")
"""main-story/rosetta/seeds-of-renewal.md:113 spells it "Millenium"; the two-n form
matches the equipment slug barkskin-of-the-millennium-tree. Spelling unconfirmed."""
MILESIAN_RANGES = LocationEntry("Milesian Ranges", region="Aria")
MOUNT_HEROIC = LocationEntry("Mount Heroic", region="Aria")
MT_ISEN = LocationEntry(
    "Mt. Isen",
    region="Aria",
    lore_fragment="mount-isen",
    aliases=("Mount Isen", "Isen's Peak"),
)
"""The alias used to live twice over: as prose in the notes ("Also recorded as
Isen's Peak") and as a hand-written match array in hints_supplement.json."""
ROTWOOD = LocationEntry("Rotwood", region="Aria")
SHYLDVERK = LocationEntry("Shyldverk", region="Aria", lore_fragment="shyldverk")
SKYBREAKER = LocationEntry("Skybreaker", region="Aria", lore_fragment="skybreaker")
THE_EVERFEST_CARNIVAL = LocationEntry("The Everfest Carnival", region="Aria", lore_fragment="the-everfest-carnival")
THE_FLOW = LocationEntry("The Flow", region="Aria", lore_fragment="the-flow")
THE_GOLDEN_GNOME = LocationEntry("The Golden Gnome", region="Aria")
THE_KORSHEM = LocationEntry("The Korshem", region="Aria", lore_fragment="the-korshem")
THRONE_GLADE = LocationEntry("Throne Glade", region="Aria")
THUNDER_STEPPE = LocationEntry("Thunder Steppe", region="Aria", lore_fragment="thunder-steppe")
VALAHAI = LocationEntry("Valahai", region="Aria", lore_fragment="valahai")
VOLTHAVEN = LocationEntry("Volthaven", region="Aria", lore_fragment="enion")
YVOR_S_PEAK = LocationEntry("Yvor's Peak", region="Aria")

# -------------------------------------------------------------------------
# Demonastery
# -------------------------------------------------------------------------

BLASMOPHET_S_DOMAIN = LocationEntry("Blasmophet's Domain", region="Demonastery")
COURTYARD = LocationEntry("Courtyard", region="Demonastery")
DIMENXXIONAL_GATEWAY = LocationEntry("Dimenxxional Gateway", region="Demonastery")
EBON_MAW = LocationEntry("Ebon Maw", region="Demonastery", lore_fragment="the-shadow-crypts")
"""world-of-rathe/demonastery.md:55 — the rift at the heart of the Shadow Crypts. Not
THE_MAW of the Pits, which was seeded on that page by name overlap."""
ENTRANCE_HALL = LocationEntry("Entrance Hall", region="Demonastery")
NECROPOLIS = LocationEntry("Necropolis", region="Demonastery")
THE_SHADOW_CRYPTS = LocationEntry("The Shadow Crypts", region="Demonastery", lore_fragment="the-shadow-crypts")
THE_VENARIUM = LocationEntry("The Venarium", region="Demonastery")
THE_VITIATE_GATEWAY = LocationEntry("The Vitiate Gateway", region="Demonastery")

# -------------------------------------------------------------------------
# High Seas
# -------------------------------------------------------------------------

AZURO_KEYS = LocationEntry("Azuro Keys", region="High Seas")
BLACKWATER_STRAIT = LocationEntry("Blackwater Strait", region="High Seas")
CORALYSI = LocationEntry(
    "Coralysi",
    region="High Seas",
    aliases=(("Fedhari", "Dhani"), ("Fiddler's Green", "pirate cant")),
)
"""One place, three names (R6). ``high-seas.md:43`` states the identity outright —
"Before it became Coralysi, home of the merfolk, this place was Fedhari" — and the
pirates' name for it cuts sideways through the timeline rather than sitting at the
end of it. Coralysi is canonical because it is the name the world lore heads its
section with, which is also where a link should land. The Fedhari and Fiddler's
Green rows are retired; the Lore Graph now draws one node where it drew three."""
DAGGER_DOCKS = LocationEntry("Dagger Docks", region="High Seas", lore_fragment="dagger-docks")
DREADFALL_REACH = LocationEntry("Dreadfall Reach", region="High Seas", lore_fragment="dreadfall-reach")
GOLDEN_PORT = LocationEntry("Golden Port", region="High Seas")
GRAYHOLLOW = LocationEntry("Grayhollow", region="High Seas")
GRAYSTONE = LocationEntry("Graystone", region="High Seas")
GRAYSTONE_PENITENTIARY = LocationEntry(
    "Graystone Penitentiary", region="High Seas", lore_fragment="graystone-penitentiary"
)
GRIEFERS_REEF = LocationEntry("Griefers Reef", region="High Seas", lore_fragment="griefers-reef")
HORIZON_S_MANTLE = LocationEntry("Horizon's Mantle", region="High Seas")
KRAKEN_S_BARREL = LocationEntry("Kraken's Barrel", region="High Seas", lore_fragment="krakens-barrel")
LOST_LAGOON = LocationEntry("Lost Lagoon", region="High Seas")
PIPER_S_PIER = LocationEntry("Piper's Pier", region="High Seas", lore_fragment="pipers-pier")
PIRATE_S_PERCH = LocationEntry("Pirate's Perch", region="High Seas")
PORT_CONNIVER = LocationEntry("Port Conniver", region="High Seas")
SELLSHORE_COAST = LocationEntry("Sellshore Coast", region="High Seas")
TERAMUNDR_S_TRIANGLE = LocationEntry("Teramundr's Triangle", region="High Seas")
TROPAL_DHANI = LocationEntry("Trōpal-Dhani", region="High Seas", lore_fragment="trōpal-dhani")

# -------------------------------------------------------------------------
# Metrix
# -------------------------------------------------------------------------

ASCENSION_TERMINAL = LocationEntry("Ascension Terminal", region="Metrix", lore_fragment="the-expanse")
BEACON = LocationEntry("Beacon", region="Metrix")
CENTENNIAL_CONSUMABLES = LocationEntry("Centennial Consumables", region="Metrix")
COGMIRE_S_SALVAGE_EMPORIUM_AND_WORKSHOPPE = LocationEntry(
    "Cogmire's Salvage Emporium and Workshoppe",
    region="Metrix",
    lore_fragment="cogmires-salvage-emporium-and-workshoppe",
)
COGWERX_CONGLOMERATE = LocationEntry("Cogwerx Conglomerate", region="Metrix", lore_fragment="cogwerx-conglomerate")
COPPERTOWN = LocationEntry("Coppertown", region="Metrix", lore_fragment="coppertown")
EAST_RISE = LocationEntry("East Rise", region="Metrix", lore_fragment="east-rise")
EAST_RISE_POWER_STATION = LocationEntry("East Rise Power Station", region="Metrix")
PIT_2 = LocationEntry("Pit 2", region="Metrix")
PIT_3 = LocationEntry("Pit 3", region="Metrix")
EIDOLON = LocationEntry("Eidolon", region="Metrix")
EIGHTH_PRECINCT = LocationEntry("Eighth Precinct", region="Metrix")
ENERGIZE_THE_ERA = LocationEntry("Energize the Era", region="Metrix", lore_fragment="iron-assembly")
"""The Iron Assembly's annual summit, held in Iron Hall — an event modelled as a
location on the DRAGON_FESTIVAL precedent."""
GIGADRILL_ELEVATOR = LocationEntry("Gigadrill Elevator", region="Metrix", lore_fragment="gigadrill-elevator")
IRON_ASSEMBLY = LocationEntry("Iron Assembly", region="Metrix", lore_fragment="iron-assembly")
IRON_HALL = LocationEntry("Iron Hall", region="Metrix")
LOWLAKE = LocationEntry("Lowlake", region="Metrix")
MENDACITY_CYBER_THEATERS = LocationEntry("Mendacity Cyber Theaters", region="Metrix", lore_fragment="east-rise")
MIDTOWN_MARKETS = LocationEntry("Midtown Markets", region="Metrix", lore_fragment="midtown-markets")
OLD_METRIX = LocationEntry("Old Metrix", region="Metrix")
PLUMVEX_PIPES_FACTORY = LocationEntry("Plumvex Pipes factory", region="Metrix")
ROSARIO_CHATEAUX = LocationEntry("Rosario Chateaux", region="Metrix")
"""main-story/bright-lights/system-failure.md:33 — the private housing Rosario Hills
gives the children it singles out; named apart from the institute and the orphanage."""
ROSARIO_HILLS = LocationEntry("Rosario Hills", region="Metrix")
ROSARIO_ORPHANAGE = LocationEntry("Rosario Orphanage", region="Metrix")
RUST_BELT = LocationEntry("Rust Belt", region="Metrix")
"""See ``IMPERIAL_FURNACE``. Cromai "soar[s] over the Metrix rust belt" (UPR010),
lower-case; the stored row capitalises it."""
TEKLA_TOY_FACTORY = LocationEntry("Tekla Toy Factory", region="Metrix")
"""main-story/outsiders/squeakers-christmas.md — a toy factory, not Teklo Industries.
The page never states its region; Coppertown and a Metrix cop share the scene."""
TEKLO_INDUSTRIES = LocationEntry("Teklo Industries", region="Metrix", lore_fragment="teklo-industries")
TERRACETTE_PATH_ACADEMY = LocationEntry(
    "Terracette Path Academy", region="Metrix", lore_fragment="terracette-path-academy"
)
THE_EXPANSE = LocationEntry("The Expanse", region="Metrix", lore_fragment="the-expanse")
THE_FOUNDRY = LocationEntry("The Foundry", region="Metrix", lore_fragment="the-foundry")
THE_NEEDLE = LocationEntry("The Needle", region="Metrix", lore_fragment="the-needle")
THE_REGISTRY = LocationEntry("The Registry", region="Metrix")
THE_SPRAWL = LocationEntry("The Sprawl", region="Metrix")
"""Metrix's industrial districts, a proper noun on metrix.md and on
main-story/bright-lights/synthetic-futures.md. The row already existed; this is
the first constant to name it."""
UNDERDOG_CAFE = LocationEntry("Underdog Cafe", region="Metrix")
VOSSEN_THEATER = LocationEntry("Vossen Theater", region="Metrix")
WEST_RISE = LocationEntry("West Rise", region="Metrix", lore_fragment="west-rise")
ZENITH = LocationEntry("Zenith", region="Metrix", lore_fragment="east-rise")
ZESCA_S = LocationEntry("Zesca's", region="Metrix")
ZINNIA_PARK = LocationEntry("Zinnia Park", region="Metrix", lore_fragment="zinnia-park")

# -------------------------------------------------------------------------
# Misteria
# -------------------------------------------------------------------------

AUI_S_SCALES_STRONGHOLDS = LocationEntry("Aui's Scales Strongholds", region="Misteria")
GORGE_OF_A_THOUSAND_WINDS = LocationEntry("Gorge of a Thousand Winds", region="Misteria")
IKARU = LocationEntry("Ikaru", region="Misteria", lore_fragment="ikaru")
KIROHIME_GATE = LocationEntry("Kirohime Gate", region="Misteria")
LUNAR_TEMPLE = LocationEntry("Lunar Temple", region="Misteria", lore_fragment="immortal-lunar-temple")
MISTCLOAK_GULLY = LocationEntry("Mistcloak Gully", region="Misteria", lore_fragment="mistcloak-gully")
MISTCLOAK_LAKE = LocationEntry("Mistcloak Lake", region="Misteria")
MISTCLOAK_TEAHOUSE = LocationEntry("Mistcloak Teahouse", region="Misteria")
MUGENSHI_ANCESTRAL_SHRINE = LocationEntry("Mugenshi Ancestral Shrine", region="Misteria")
MUGENSHI_GORGE = LocationEntry("Mugenshi Gorge", region="Misteria", lore_fragment="mugenshi-gorge")
MUGENSHI_VILLAGE = LocationEntry("Mugenshi Village", region="Misteria")
NASU_KA_TEAHOUSE = LocationEntry("Nasu-ka Teahouse", region="Misteria")
RYOSOZAN_PEAKS = LocationEntry("Ryōsōzan Peaks", region="Misteria")
SKYLARK_PEAK = LocationEntry("Skylark Peak", region="Misteria")
FLOATING_DOJO = LocationEntry("Floating Dojo", region="Misteria", parent=SKYLARK_PEAK)
"""Named only by the card title "Visit the Floating Dojo" (OUT055), whose text puts
the grand masters atop Skylark Peak — hence the containment."""
VALLEY_OF_BLOSSOMS = LocationEntry("Valley of Blossoms", region="Misteria")

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
AUDRA = LocationEntry("Audra", region="Solana")
BARTHIMONT_MANOR = LocationEntry("Barthimont Manor", region="Solana")
CEREMONIAL_CHAMBER = LocationEntry("Ceremonial Chamber", region="Solana")
CLIFFHOLD = LocationEntry("Cliffhold", region="Solana")
FARDREYAS = LocationEntry("Fardreyas", region="Solana")
GOLDENHELM_KEEP = LocationEntry("Goldenhelm Keep", region="Solana")
GOLDEN_CHARIOT = LocationEntry("Golden Chariot", region="Solana")
HAZELTOWN = LocationEntry("Hazeltown", region="Solana")
IRONSONG_FORGE = LocationEntry("Ironsong Forge", region="Solana")
LIBRARY_OF_ILLUMINATION = LocationEntry("Library of Illumination", region="Solana")
MORLOCK_HILL = LocationEntry("Morlock Hill", region="Solana")
OCTOGRIA = LocationEntry("Octogria", region="Solana")
OCTOMILITIA = LocationEntry("Octomilitia", region="Solana")
OCTOTISTA = LocationEntry("Octotista", region="Solana")
SILVARIUM = LocationEntry("Silvarium", region="Solana")
SOLSTICE_OF_LAURELS = LocationEntry("Solstice of Laurels", region="Solana", lore_fragment="solstice-of-laurels")
SUNVALE = LocationEntry("Sunvale", region="Solana")
THE_AWAKENING_CEREMONY = LocationEntry(
    "The Awakening Ceremony", region="Solana", lore_fragment="the-awakening-ceremony"
)
THE_GOLDEN_FIELDS = LocationEntry("The Golden Fields", region="Solana")
THE_GRAND_COUNCIL = LocationEntry("The Grand Council", region="Solana", lore_fragment="the-grand-council")
THE_NORTHERN_REALMS = LocationEntry("The Northern Realms", region="Solana", lore_fragment="the-northern-realms")
THE_SOLARIUM = LocationEntry("The Solarium", region="Solana")

# -------------------------------------------------------------------------
# The Pits
# -------------------------------------------------------------------------

ANKOMEIDO = LocationEntry("Ankomeido", region="The Pits", lore_fragment="ankomeido")
BARTON_S_HOUSE = LocationEntry("Barton's House", region="The Pits")
BLACKJACK_S_TAVERN = LocationEntry(
    "Blackjack's Tavern", region="The Pits", lore_fragment="blackjacks-mercenary-company"
)
BLOCKHEAD_TERRITORY = LocationEntry("Blockhead Territory", region="The Pits")
BONEYARD = LocationEntry("Boneyard", region="The Pits", lore_fragment="numbskulls")
GUTPURSE = LocationEntry("Gutpurse", region="The Pits", lore_fragment="the-skein")
KYLORIA_S_LAIR = LocationEntry("Kyloria's Lair", region="The Pits")
"""See ``IMPERIAL_FURNACE``. Kyloria "dwell[s] in her lair deep beneath the Pits"
(UPR011), and the row's own note already reads: Deep beneath the Pits."""
MINERS_REEF = LocationEntry("Miners Reef", region="The Pits", lore_fragment="the-seethe")
OVERSEER_CRICHTON_S_MANSION = LocationEntry("Overseer Crichton's Mansion", region="The Pits")
RATTLEBONE = LocationEntry("Rattlebone", region="The Pits", lore_fragment="the-skein")
SEETHE = LocationEntry("Seethe", region="The Pits")
SEETHESIDE_DOCKS = LocationEntry("Seetheside Docks", region="The Pits")
SHUNTSWITCH_RAILWAY_STATION = LocationEntry("Shuntswitch Railway Station", region="The Pits")
SKEIN = LocationEntry("Skein", region="The Pits")
SORI_16 = LocationEntry("Sori 16", region="The Pits")
SOUTHMAW = LocationEntry("Southmaw", region="The Pits")
THE_DROP = LocationEntry("The Drop", region="The Pits")
THE_LEAF_HOUSE = LocationEntry("The Leaf House", region="The Pits")
THE_MAW = LocationEntry("The Maw", region="The Pits", lore_fragment="the-maw")

# -------------------------------------------------------------------------
# The Savage Lands
# -------------------------------------------------------------------------

DEATHMATCH_ARENA = LocationEntry("Deathmatch Arena", region="The Savage Lands")
FORWARD_CAMPS = LocationEntry("Forward Camps", region="The Savage Lands")
GOUGEMOOR = LocationEntry("Gougemoor", region="The Savage Lands")
RHINAR_S_TERRITORY = LocationEntry("Rhinar's Territory", region="The Savage Lands")
THE_BONEYARD = LocationEntry("The Boneyard", region="The Savage Lands", lore_fragment="the-boneyard")
"""The Brute Carrion Rite ground. Not BONEYARD, the Numbskulls' turf in the Pits."""
THE_MOAT = LocationEntry("The Moat", region="The Savage Lands")
THE_SAVAGE_WILDS = LocationEntry("The Savage Wilds", region="The Savage Lands")

# -------------------------------------------------------------------------
# Volcor
# -------------------------------------------------------------------------

ASHVAHAN = LocationEntry("Ashvahan", region="Volcor", lore_fragment="ashvahan")
BLACKROCK_QUARRIES = LocationEntry("Blackrock Quarries", region="Volcor", lore_fragment="blackrock-quarries")
CHAMBER_OF_THE_DRAGON = LocationEntry("Chamber of the Dragon", region="Volcor")
DESHVAHAN = LocationEntry("Deshvahan", region="Volcor", lore_fragment="deshvahan")
DRAGON_FESTIVAL = LocationEntry("Dragon Festival", region="Volcor", lore_fragment="dragon-festival")
"""An event with a heading of its own on ``world-of-rathe/volcor.md:27``, modelled as
a location on the precedent of ``THE_EVERFEST_CARNIVAL``. Named on ``weapons/rok.md``."""
DRAGON_S_PEAK = LocationEntry("Dragon's Peak", region="Volcor", lore_fragment="dragons-peak")
DRAGON_S_TEETH = LocationEntry("Dragon's Teeth", region="Volcor", lore_fragment="dragons-peak")
"""The spires below Dragon's Peak — world-of-rathe/volcor.md, under that heading."""
FOREST_OF_FLAMES = LocationEntry("Forest of Flames", region="Volcor", lore_fragment="forest-of-flames")
"""``world-of-rathe/volcor.md:99`` gives it a heading of its own and describes it as
"a dense, vibrant woodland thriving within a volcanic landscape". Named on four
pages before it had a row: volcor.md, ``dragons-of-empire.md``, ``betrayal.md`` and
``fires-of-rebellion.md``. It is also half of two character names already in the
registry — ``Min of the Forest of Flames``, and "Fai of the Forest of Flames" as
this page writes him."""
GRAND_ARCHWAY = LocationEntry("Grand Archway", region="Volcor")
IMPERIAL_FURNACE = LocationEntry("Imperial Furnace", region="Volcor")
"""Already a ``locations`` row before this constant existed (2026-08-21). Name and
region are copied from the stored row rather than read off the page, because
``location_id`` hashes both — a constant spelled from the prose would have minted a
second row and stranded the first. Tomeltai "power[s] the Imperial Furnace"
(``flavour/uprising.md``, UPR007)."""
IMPERIAL_PALACE = LocationEntry("Imperial Palace", region="Volcor", lore_fragment="the-royal-court")
MT_VOLCOR = LocationEntry("Mt. Volcor", region="Volcor")
RED_DESERT = LocationEntry("Red Desert", region="Volcor", lore_fragment="the-red-desert")
SAND_GLASS_DISTRICT = LocationEntry("Sand Glass District", region="Volcor")
SANDIKAI = LocationEntry("Sandikai", region="Volcor")
"""New 2026-08-21. Azvolai "guard[s] the crossroads of Sandikai"
(``flavour/uprising.md``, UPR009), and ``digital-tiles/uprising`` carries a "Storm
of Sandikai" tile.

**The region is the user's call, not the page's** — no text places it. Volcor was
chosen because the set is Volcor's uprising and the two dragon haunts named beside
it, the Red Desert and the Imperial Furnace, are both Volcor. This is not a
correctable guess: ``location_id`` hashes the region, so moving it later mints a
second row rather than editing this one."""
SWORYUK_GORGE = LocationEntry("Sworyuk Gorge", region="Volcor")
TAOKING = LocationEntry("Taoking", region="Volcor")
"""Fai's home village in the Forest of Flames — main-story/uprising/fires-of-rebellion.md."""
THE_ASH_PLAINS = LocationEntry("The Ash Plains", region="Volcor")
"""See ``IMPERIAL_FURNACE`` — another row that predated its constant. The stored
name carries the article; the page writes "the illusionists of the Ash Plains"
(UPR030), which is why the constant is spelled from the row and not the prose."""
THE_BADLANDS = LocationEntry("The Badlands", region="Volcor")
THE_GOLDEN_ORCHARD_ESTATE = LocationEntry(
    "The Golden Orchard Estate",
    region="Volcor",
    aliases=("Golden Orchard",),
)
"""The alias is the form the prose actually uses (the user's call, 2026-08-21).
``the-phoenix-and-the-dragon.md`` writes the short "Golden Orchard" twice, at :7
and :9, where only ``dragons-of-empire.md:87`` uses the full name. Without the
alias the massacre both pages turn on matches nothing."""
THE_MOLTEN_TIDE = LocationEntry("The Molten Tide", region="Volcor", lore_fragment="the-molten-tide")
THE_OASIS = LocationEntry("The Oasis", region="Volcor")
THE_OBSIDIAN_COAST = LocationEntry("The Obsidian Coast", region="Volcor")
THE_SLICK = LocationEntry("The Slick", region="The Pits", lore_fragment="torched")
URJIYSA = LocationEntry("Urjiysa", region="Volcor")
ZANCARO = LocationEntry("Zancaro", region="Volcor")

# -------------------------------------------------------------------------
# No region recorded
# -------------------------------------------------------------------------

ANVILHEIM = LocationEntry("Anvilheim")
ARENA_BARRACKS = LocationEntry("Arena Barracks")
ASKRAWELD = LocationEntry("Askraweld")
BELLOWS_OF_HELL = LocationEntry("Bellows of Hell")
BUTCHER_S_BIN = LocationEntry("Butcher's Bin")
CHAMPIONS_REST = LocationEntry("Champions Rest")
CHAMPION_S_QUARTERS = LocationEntry("Champion's Quarters")
CHARRED_RANGE = LocationEntry("Charred Range")
CHROME_CAVERNS = LocationEntry("Chrome Caverns")
DAWNHAVEN = LocationEntry("Dawnhaven")
DEATH_S_KNELL = LocationEntry("Death's Knell")
DEN_OF_BEASTS = LocationEntry("Den of Beasts")
DOOMSDAY_PEAK = LocationEntry("Doomsday Peak")
GRINNING_BOAR_CANTINA = LocationEntry("Grinning Boar Cantina")
INFERNAL_MAW = LocationEntry("Infernal Maw")
I_ARATHAEL = LocationEntry("i'Arathael")
MOJIRE = LocationEntry("Mojire")
NEELASHA = LocationEntry("Neelasha")
NEVEREST = LocationEntry("Neverest")
SHADOWREALM = LocationEntry("Shadowrealm")
TARNISH_HILL = LocationEntry("Tarnish Hill")
TEMPEST_STRAITS = LocationEntry("Tempest Straits")
THE_ABYSS = LocationEntry("The Abyss")
THE_BROKEN_CHARIOT_TAVERN = LocationEntry("The Broken Chariot Tavern")
THE_UNDERCROFT = LocationEntry("The Undercroft")
THISTLEFOLD = LocationEntry("Thistlefold")
WEST_RANGES = LocationEntry("West Ranges")
