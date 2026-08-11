# The single place to maintain lore text (location notes; monster/fauna/flora
# descriptions) for entities that already exist in the database.
# update_description() requires the named entity to already be linked to a
# story via data-entry.py — it only sets the notes/description column, never
# creates or links entities.
#
# Do not add notes=/description= values inline in data-entry.py; add or
# update the entry here instead.

import sys

sys.path.insert(0, "src/data")
from db import Database

db = Database("src/data/fablore.db")

# update_description() raises ValueError when the named entity does not exist. Because
# this file is a flat sequence of top-level calls with no error handling, an uncaught
# raise aborts the interpreter on that line and silently skips every call below it — so
# a single stale name (left behind by a rename or a duplicate-row cleanup) can disable
# most of the file without anything obviously failing. Collect failures instead, so a
# bad entry costs only itself, then report them together and exit non-zero.
#
# validate_data.py checks these targets statically, which is what should catch a stale
# name first; this is the backstop for when the script is run directly.
_failures: list[tuple[str, str, str]] = []
_update_description = db.update_description


def _collecting_update_description(entity_type: str, name: str, text: str) -> None:
    """Apply a description, recording rather than raising when the entity is missing."""
    try:
        _update_description(entity_type, name, text)
    except ValueError as exc:
        _failures.append((entity_type, name, str(exc)))


db.update_description = _collecting_update_description

# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------

db.update_description(
    "monster",
    "Dregs",
    "Humanoid figures with bloated, rotting bodies; their faces a mass of melted,"
    " discoloured skin, dripping the length of their bony, twisted limbs.",
)
db.update_description(
    "monster",
    "Glutgorr",
    "Mountain of Meat. A giant grown from a multitude of willing bodies."
    " A singular aberrant baby born from a thousand mothers.",
)
db.update_description(
    "monster",
    "Puppeteer",
    "A repulsive creature emerged through the opening, resembling a mass of human bodies"
    " held together by some monstrous cancer, an enormous eye in its center above a slavering mouth.",
)
db.update_description(
    "monster",
    "Ravenir",
    "Ever-hungry creatures the Old Ones sculpt from the stolen flesh of Rathe's living,"
    " consuming corpses to multiply; no two are ever alike.",
)
db.update_description(
    "monster",
    "Shadowrealm Walker",
    "Huge stilt-legged predators of i'Arathael, slow to anger, resembling praying mantises.",
)

# ---------------------------------------------------------------------------
# Fauna
# ---------------------------------------------------------------------------

db.update_description(
    "fauna",
    "Apophis",
    "A large serpent with barbed scales, which can be found lurking within larger bodies of magma,"
    " storing energy and lying in wait. These creatures move with Volcor's lava flows, moving through"
    " the magma to feast on those caught in the flow's path. While they can occasionally be found on"
    " land, they move much more slowly, and are thus vulnerable to attack.",
)
db.update_description(
    "fauna",
    "Azeri",
    "The Azeri are elusive and mysterious, lingering in the innermost depths of the Savage Lands.",
)
db.update_description("fauna", "Blindseal", "Blubbery.")
db.update_description("fauna", "Cursed Dhani Warriors", "Scorpion tails, claws and human head.")
db.update_description("fauna", "Cyanatu", "A rare sea snake.")
db.update_description("fauna", "Desert Fox", "The creature's mouth warped by two large boar-like tusks.")
db.update_description("fauna", "Flare Deer", "Its scent glands swollen with massive oozing growths.")
db.update_description("fauna", "Giant Drift Stingers", "Scorpion.")
db.update_description("fauna", "Gossamhares", "Skittish creatures.")
db.update_description("fauna", "Gupler", "Moon-shaped.")
db.update_description("fauna", "Hoikers", "Giant, acid-spitting scallops.")
db.update_description(
    "fauna",
    "Hydra",
    "A sea creature with boat-sized flippers, three heads and perhaps as large as three whales, end on end.",
)
db.update_description(
    "fauna",
    "Kaie'o",
    "Small, quick creatures once common across Aria's fields, prized for their soft fur;"
    " their sudden disappearance from the plains was an early sign of the Fractal Scar's unrest.",
)
db.update_description("fauna", "Kneecapper Crustacean", "They have foot-long pincers.")
db.update_description(
    "fauna",
    "Longma",
    "Despite their vague resemblance, longma are larger than the mounts used by Solana, ink-black in"
    " colour and covered in a dense coat of fur that helps to protect them from embers. Longma store"
    " heat within their bodies as a source of energy, smoke escaping their nostrils with every exhale."
    " These hardy creatures are excellent for long-distance travel, able to withstand the heat of"
    " Volcor's landscape.",
)
db.update_description(
    "fauna",
    "Morrows",
    "These tiny wisps are artificially created by the wizards of Volcor; puffs of smoke brought to life"
    " by a breath of aether. Once formed, they subsist entirely on embers, flitting to and fro amongst"
    " the fiery landscape.",
)
db.update_description(
    "fauna",
    "Na'shari",
    "A large beast with a crystalline hide, the na'shari has skin harder than most forms of metal."
    " In spite of its tough appearance, this creature is known for its docile and friendly nature."
    " Its round eyes and fuzzy tail make the creature incredibly popular with children, who often flock"
    " to na'shari in hopes of playing with the creature.",
)
db.update_description("fauna", "Raciki", "Shapeshifting, fluffy canine.")
db.update_description(
    "fauna",
    "Ryoki",
    "These are small creatures, similar in appearance to fish, that inhabit the lava streams and rivers"
    " of Volcor. Despite the immense heat, these creatures thrive in the extreme conditions, lurking"
    " beneath the glowing surface of the magma. While their scales are almost black, their 'fins' catch"
    " alight when they break the surface of the lava, leaping from stream to stream.",
)
db.update_description(
    "fauna",
    "Sailorbane Coral",
    "A predatory species, Sailorbane Coral grows from the rocky banks of channels,"
    " remaining submerged to conceal its presence.",
)
db.update_description(
    "fauna",
    "Ank'is",
    "The crystalline creature does not bleed. It shatters. Its teeth are harder than stone, with"
    " serrated edges and a needle-like tip to tear through flesh. Its limbs are long and thin, with"
    " sharp points to allow it to grip onto most surfaces, and scale the difficult terrain of the"
    " Savage Lands.",
)
db.update_description(
    "fauna",
    "Brawnhide",
    "A giant, furred beast with long, thick canines, and small, dark eyes.",
)
db.update_description(
    "fauna",
    "Cesari",
    "Majestic, iridescent creatures of Aria that move through the air with a spectral, coiling grace,"
    " a sight familiar to those raised amongst the animal acts of the Valdur.",
)
db.update_description(
    "fauna",
    "Fianna",
    "Tall creature, with long flowing tails, tough skin, and massive antlers crowning the top of" " their head.",
)
db.update_description(
    "fauna",
    "Meep",
    "Tiny, mischievous creatures recognised by their long limbs and tails, and colourful feather crests.",
)
db.update_description("fauna", "Sawmaw", "Triple-finned.")
db.update_description(
    "fauna",
    "Siren",
    "Enchanting merfolk who lure sailors with song and beauty —"
    " gifts please them, but poor offerings may cost you dearly.",
)
db.update_description(
    "fauna",
    "Skera",
    "One of the Savage Lands' most skilled predators, almost completely nocturnal, relying on the"
    " darkness to mask their movements while stalking prey. Their four eyes allow them to hunt in"
    " the dark.",
)
db.update_description(
    "fauna",
    "Vitr'eo",
    "A majestic creature with a thick mane, crowned with a series of large crystals that grow out"
    " from the top of its skull.",
)
db.update_description(
    "fauna",
    "Vuurlin",
    "A large bird of prey that flies at a high altitude, only descending to roost or to attack"
    " vulnerable prey. When in flight, the tips of their feathers catch alight, creating flames that"
    " streak behind them as they soar through the sky. They're reliable messengers, and are often used"
    " by the royal court and the many generals of Volcor, due to the vuurlin's keen intelligence and"
    " powerful wings.",
)
db.update_description(
    "fauna",
    "Welkin",
    "A wyvern species native to Aria. At first glance, the welkin resembles large, winged lizards."
    " They have a leathery skin that, like the chameleon, changes color with variations in the Flow.",
)

# ---------------------------------------------------------------------------
# Flora
# ---------------------------------------------------------------------------

db.update_description("flora", "Blissberry Bush", "Produces small delicious berry fruits.")
db.update_description(
    "flora",
    "Haldor",
    "A large, slow-growing tree of the Savage Lands whose thick root warren shelters ground-dwelling creatures.",
)
db.update_description(
    "flora",
    "Jacaranda",
    "Branches like insectile limbs, each adorned with the body of a firefinch, pierced through the heart.",
)

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

db.update_description("location", "Aldevyr", "A village in Aria.")
db.update_description(
    "location",
    "Amphitheatre",
    "In the city proper, a space for ceremonies, public events and proclamations.",
)
db.update_description("location", "Deshvahan", "A city in Volcor.")
db.update_description(
    "location",
    "Dimenxxional Gateway",
    "The Demonastery's bridge to i'Arathael, through which monstrous hordes are drawn forth into" " Rathe.",
)
db.update_description(
    "location",
    "East Rise",
    "The majority of this Metrix sector is devoted to parks and entertainment complexes.",
)
db.update_description(
    "location",
    "Hand of Sol",
    "Solana's order of knights, who defend the city from outside threats.",
)
db.update_description(
    "location",
    "Ikaru",
    "One of the prestigious houses of Misteria; the House of Blossoms.",
)
db.update_description(
    "location",
    "The Flow",
    "A wild, unpredictable force of nature in Aria, the Flow shapes the landscape around it as it" " ebbs and flows.",
)
db.update_description(
    "location",
    "The Foundry",
    "An independent radio station, one of the few in Metrix that remains free of Mendacity control.",
)
db.update_description(
    "location",
    "The Korshem",
    "A massive tree at the heart of Aria that shelters all who live amongst its leaves.",
)
db.update_description(
    "location",
    "Mount Heroic",
    "A mountain which towers above the forests of eastern Aria.",
)
db.update_description(
    "location",
    "Mt. Isen",
    "Ageless mountain watching over Larinkmorth, untouched by the Flow; from its summit"
    " Isen is said to have crafted the Isen Ranges. Also recorded as Isen's Peak.",
)
db.update_description(
    "location",
    "Trōpal-Dhani",
    "A legendary city said to have survived the Dhani empire's collapse, hiding its lost magic and"
    " treasures in the most perilous ruins.",
)
db.update_description(
    "location",
    "Aldengrove",
    "One of the Third Age's three bastions - Aldengrove to sustain the Rathenfolk,"
    " Valahai to empower them, and Isenloft to guard them all.",
)
db.update_description("location", "Ankomeido", "Home to the misfits and malcontents of Misteria.")
db.update_description(
    "location",
    "Anvilheim",
    "Home of Rathe's finest architects and smiths, who raised the Auric Keep and forged"
    " Shyldverk's arcanite gate; now lost, but not forgotten.",
)
db.update_description(
    "location",
    "Arcane Hall",
    "Cavernous testing chamber within the Auric Keep, converted into the laboratory where"
    " the Aetherscribes built Oscilio.",
)
db.update_description("location", "Arcturos", "Where Oscilio was embedded.")
db.update_description("location", "Ashvahan", "Capital of Volcor.")
db.update_description(
    "location",
    "Astral Bridge",
    "An arcane span manifested by the Voltaris Gem, anchoring Shyldverk in Enion to the"
    " Auric Keep in the Nebulus Rift.",
)
db.update_description("location", "Audra", "Village.")
db.update_description(
    "location",
    "Aui's Scales Strongholds",
    "Locations where things are concealed from the public.",
)
db.update_description(
    "location",
    "Auric Keep",
    "Citadel of learning the Aetherscribes built at the heart of Valahai; cast into the"
    " Nebulus Rift by the Ancients' cataclysm and later reconnected to Enion by the Astral Bridge.",
)
db.update_description("location", "Barthimont Manor", "In the Northern Realms.")
db.update_description("location", "Barton's House", "Information Dealer.")
db.update_description(
    "location",
    "Blackjack's Tavern",
    "Bounty Hunting Hub, owned by Greenbird. Neutral Ground.",
)
db.update_description("location", "Blackrock Quarries", "In the north of Volcor.")
db.update_description("location", "Blasmophet's Domain", "Separate plane.")
db.update_description("location", "Blockhead Territory", "An entire sector of The Maw.")
db.update_description(
    "location",
    "Candlelight Clearing",
    "Where the Rosetta of old had once gathered to garden, share poetry, and sing.",
)
db.update_description(
    "location",
    "Ceremonial Chamber",
    "In the city proper, location of the Awakening ceremony.",
)
db.update_description("location", "Charred Range", "Mountains separating Solana and Volcor.")
db.update_description("location", "Chrome Caverns", "The desert's edge.")
db.update_description("location", "Coralysi", "Home of the merfolk. Floating gardens.")
db.update_description("location", "Death's Knell", "The Ocean.")
db.update_description(
    "location",
    "Demonastery",
    "Mansion with specific rooms per resident; it moves, accessible by invitation.",
)
db.update_description(
    "location",
    "Eighth Precinct",
    "Enforcer station, down the street from the Iron Hall.",
)
db.update_description(
    "location",
    "Enion",
    "Armory of the ancients and training ground of champions.",
)
db.update_description(
    "location",
    "Entrance Hall",
    "Location of the portal to íArathael, home of Whisper the stained glass window.",
)
db.update_description("location", "Fardreyas", "Village.")
db.update_description(
    "location",
    "Forward Camps",
    "Home to merchants, traders, adventurers, and mercenaries.",
)
db.update_description("location", "Fractal Scar", "Site of the Battle of Fractal Scar.")
db.update_description(
    "location",
    "Freakshow Territory",
    "Deep in the Pits, composed of abandoned mineshafts.",
)
db.update_description("location", "Golden Chariot", "Inn in the city proper, owned by Minerva.")
db.update_description("location", "Golden Port", "Built in the ruins of the Dhani Empire.")
db.update_description("location", "Gougemoor", "The edge of the Savage Lands.")
db.update_description("location", "Grayhollow", "Kuraghan safe port.")
db.update_description("location", "Hazeltown", "Village.")
db.update_description("location", "Highloft Inn", "Inn on Skybreaker.")
db.update_description(
    "location",
    "Iron Hall",
    "The seat of power for Metrix's municipal government.",
)
db.update_description("location", "Ironsong Forge", "In the city proper.")
db.update_description(
    "location",
    "Isen Ranges",
    "The mountain range dividing western Aria from the rest of Rathe, said to have been"
    " crafted by Isen from earth and aether; Valahai was founded behind it and Isenloft"
    " guards its only pass.",
)
db.update_description(
    "location",
    "Isenloft",
    "Mighty citadel amidst the Isen Ranges guarding the only passage into Aria; frozen at"
    " the Third Age's end, and thawing once more in recent times.",
)
db.update_description(
    "location",
    "Jawbreaker Territory",
    "No official territory with the exception of some houses on the water.",
)
db.update_description("location", "Kyloria's Lair", "Deep beneath the Pits.")
db.update_description("location", "Legendarium", "Part of the Everfest Carnival.")
db.update_description(
    "location",
    "Library of Illumination",
    "In the city proper, a public library cared for by the members of the Light of Sol.",
)
db.update_description("location", "Might n' Mead", "Where Valda grew up and works.")
db.update_description("location", "Morlock Hill", "Site of the Battle of Morlock Hill.")
db.update_description(
    "location",
    "Mugenshi Village",
    "Hidden village in the Mugenshi Gorge, led by Katsu.",
)
db.update_description("location", "Nasu-ka Teahouse", "Nuu's teahouse by Mistcloak Lake.")
db.update_description(
    "location",
    "Neverest",
    "Cursed tarns on the Shadowrealm's jagged heights, holding wells of " "necromantic potential Malice draws upon.",
)
db.update_description(
    "location",
    "Numbskull Territory",
    "Cave network lined with skulls, resembling a catacomb.",
)
db.update_description("location", "Overseer Crichton's Mansion", "Situated in The Maw.")
db.update_description("location", "Pirate's Perch", "Filled with jungle.")
db.update_description("location", "Rhinar's Territory", "Void of other brutes.")
db.update_description("location", "Rosario Hills", "Orphanage parent company.")
db.update_description("location", "Rotwood", "Area next to Candlehold.")
db.update_description("location", "Ryōsōzan Peaks", "Owned by Nuu.")
db.update_description("location", "Seethe", "A river.")
db.update_description(
    "location",
    "Shadowrealm",
    "A desolate expanse within i'Arathael, home to the Shadowrealm Walkers and traversed by"
    " Demonastery expeditions.",
)
db.update_description(
    "location",
    "Shyldverk",
    "Arcanite-forged gatehouse guarding the aetheric moat and the bridge to the Auric Keep;"
    " a surviving fragment of old Valahai.",
)
db.update_description(
    "location",
    "Solana",
    "Holy city-state at the heart of Rathe, built by pilgrims of Sol and governed by the Order of the Light.",
)
db.update_description("location", "Sori 16", "Location of The Leaf House.")
db.update_description(
    "location",
    "Southmaw",
    "Southmaw Asylum is a laboratory of horrors where the orphaned and discarded of the Pits beneath Metrix are subjected to nightmarish experiments.",
)
db.update_description("location", "Sunvale", "Village.")
db.update_description(
    "location",
    "The Abyss",
    "The most sacred site in the Shadowrealm, guarded by Baalghor. No expedition to its outer"
    " reaches has ever returned.",
)
db.update_description("location", "The Badlands", "Borders the Savage Lands.")
db.update_description("location", "The Beyond", "Separate realm.")
db.update_description("location", "The Drop", "A bar owned by Uzuri.")
db.update_description(
    "location",
    "The Golden Fields",
    "Beyond the outer walls are grand golden fields, numerous villages and towns under the"
    " protection and guidance of Solana.",
)
db.update_description("location", "The Golden Gnome", "Part of the Everfest Carnival.")
db.update_description(
    "location",
    "The Great Gates",
    "These eight paths lead through the city to the Solarium.",
)
db.update_description("location", "The Leaf House", "Restaurant run by Jemjang.")
db.update_description(
    "location",
    "The Maela",
    "Part of the Everfest Carnival, home to fortune tellers, seers, oracles, enchantresses," " and conjurers.",
)
db.update_description("location", "The Northern Realms", "Region of Solana.")
db.update_description("location", "The Oasis", "Water from Misteria, lava from Mt. Volcor.")
db.update_description(
    "location",
    "The Plazas",
    "Connect the outer city sectors, a space to gather and hear news.",
)
db.update_description("location", "The Registry", "Information Center.")
db.update_description(
    "location",
    "The Silvaris",
    "A series of beautiful public gardens surrounding the inner sanctum of Solana.",
)
db.update_description("location", "The Solarium", "The inner sanctum, home to the Light of Sol.")
db.update_description(
    "location",
    "The Valdur",
    "Part of the Everfest Carnival, known for strongmen acts and work with animals.",
)
db.update_description("location", "The Venarium", "Room filled with plants.")
db.update_description(
    "location",
    "The Vitiate Gateway",
    "Last of the 9 portals connecting Rathe to íArathael.",
)
db.update_description("location", "Throne Glade", "Area next to Candlehold.")
db.update_description(
    "location",
    "Torched Territory",
    "Marked with trigger-sensitive flamethrowers, fire traps, lava pits, and plenty of explosives.",
)
db.update_description("location", "Underdog Cafe", "In Coppertown.")
db.update_description(
    "location",
    "Valahai",
    "Fortress city founded on the plains of Enion, the Rathenfolk's last bastion against"
    " the Old Ones, overrun and shattered in the Third Age.",
)
db.update_description(
    "location",
    "Volthaven",
    "Snow-dusted village drifting through the skies of Enion, born from the storm where"
    " Yvor fell; home of Lexi and Aurora, its passage guarded by Wayfarers.",
)
db.update_description(
    "location",
    "Yvor's Peak",
    "Statue of Yvor located here, doorway to an armory.",
)
db.update_description(
    "location",
    "i'Arathael",
    "Separate plane accessed via a portal in the Demonastery, home of the Old Ones.",
)
db.update_description(
    "location",
    "The Shadow Crypts",
    "Dim halls within the Demonastery where a black mold containing warped microcosms of shifting light grows.",
)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

if _failures:
    print(f"descriptions.py: {len(_failures)} description(s) could not be applied:", file=sys.stderr)
    for _entity_type, _name, _message in _failures:
        print(f"  {_entity_type} {_name!r}: {_message}", file=sys.stderr)
    print(
        "\nEvery other description was applied. A missing entity usually means the name here is "
        "stale — check the spelling against the CSV, or register the entity in data-entry.py first.",
        file=sys.stderr,
    )
    sys.exit(1)
