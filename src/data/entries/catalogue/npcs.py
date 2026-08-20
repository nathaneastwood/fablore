"""Canonical NPC definitions — the one place each character is described.

``character_id`` is a hash of the name (``registry_ids.lore_character_id``), so a
second ``NPCEntry`` literal for the same character elsewhere would not update this
row, it would compete with it: ``species``/``status`` preserve-on-empty, and two
non-empty values race on module import order. Define each NPC once, here.

Story modules reference these as ``npc.NAME``. See ``entries/catalogue/__init__.py``
for the split between this package, ``entries/*.py`` and ``descriptions.py``.
"""

from __future__ import annotations

from db import NPCEntry
from entries.catalogue import species as sp


ACHLYS_HAG_OF_MOJIRE = NPCEntry("Achlys, hag of Mojire", species=sp.HUMAN, epithets=("hag of Mojire",))
AEGIS_THE_SHIELD_OF_LIGHT = NPCEntry(
    "Aegis, the Shield of Light",
    species=sp.HERALD,
    epithets=("the Shield of Light", "Archangel of Protection"),
)
AELIUS = NPCEntry("Aelius", species=sp.HUMAN, status="Dead")
AESIR_OF_FLAMES = NPCEntry("Aesir of Flames", species=sp.AESIR)
AIOS = NPCEntry("Aios", species=sp.HUMAN, status="Alive")
AKUO = NPCEntry("Akuo", species=sp.HUMAN)
AUDACITY = NPCEntry("λud@c!ty")
"""The Foundry's operator. metrix.md:201 says nobody knows "their real name,
face, or if they're a single person or a collective of dissidents operating
under a shared alias" — hence no species and no status."""
ALIF = NPCEntry("Alif", species=sp.HUMAN, status="Alive")
ALOSYN = NPCEntry("Alosyn", species=sp.HUMAN)
AMIR = NPCEntry("Amir", species=sp.HUMAN)
AMIRA_SURANA = NPCEntry("Amira Surana")
ANARCH_ZEIR = NPCEntry("Anarch Zeir", species=sp.HUMAN)
ANHE_KOTORI_WAVEBENDER = NPCEntry("Anhe, Kotori Wavebender", species=sp.HUMAN)
APOSTATE = NPCEntry("Apostate", species=sp.HUMAN)
ARBITER_MAGISTER_OF_JUSTICE = NPCEntry("Arbiter, Magister of Justice")
ASTIER = NPCEntry("Astier", species=sp.HUMAN)
ASTRA_MORENA = NPCEntry("Astra Morena")
ASTREA_QUAZOR = NPCEntry("Astrea Quazor", species=sp.HUMAN, status="Alive")
ATEIA = NPCEntry("Ateia")
AUREA_CHAMPION_OF_THE_DAWN = NPCEntry(
    "Aurea, Champion of the Dawn", species=sp.HUMAN, epithets=("Champion of the Dawn",)
)
AURELIUS = NPCEntry("Aurelius", species=sp.HORSE)
AURIC_SEERESS = NPCEntry("Auric Seeress", species=sp.HUMAN, status="Deceased")
AVALON_MESSENGER_OF_THE_DAWN = NPCEntry(
    "Avalon, Messenger of the Dawn",
    species=sp.HERALD,
    epithets=("Messenger of the Dawn", "Archangel of Rebirth"),
)
BAM_BAM = NPCEntry("Bam Bam", species=sp.BRUTE)
BARON_THE_BUTCHER = NPCEntry("Baron the Butcher", species=sp.HUMAN, status="Dead")
BARTON = NPCEntry("Barton", species=sp.HUMAN)
BARTRAND_THE_BLOODY = NPCEntry("Bartrand the Bloody", species=sp.HUMAN)
BARUS_BOLDSTRIDE = NPCEntry("Barus Boldstride", species=sp.HUMAN)
BATBITER = NPCEntry("Batbiter")
BAZZ = NPCEntry("Bazz", species=sp.HUMAN, status="Deceased")
BEEZY_THE_BRASH = NPCEntry("Beezy the Brash", species=sp.HUMAN, status="Dead")
BELLONA_THE_WARTUNE_HERALD = NPCEntry(
    "Bellona, the Wartune Herald",
    species=sp.HERALD,
    epithets=("the Wartune Herald", "Archangel of War"),
)
BISKI = NPCEntry("Biski", species=sp.DOG)
BLASMOPHET = NPCEntry("Blasmophet", species=sp.EMBRA)
BLIND_BOGGY = NPCEntry("Blind Boggy")
BLOODWORTH_GOLDMANE = NPCEntry("Bloodworth Goldmane")
BOJANI = NPCEntry("Bojani", species=sp.HUMAN, status="Dead")
BOO = NPCEntry("Boo")
BRAUMEISTER_BALEN = NPCEntry("Braumeister Balen", species=sp.HUMAN, status="Alive")
BREWMEISTER_MARV = NPCEntry("Brewmeister Marv", species=sp.HUMAN)
BRUTUS_SUMMA_RUDIS = NPCEntry("Brutus, Summa Rudis")
BUTCHER_JEK = NPCEntry("Butcher Jek", species=sp.HUMAN)
BUTTONS = NPCEntry("Buttons", species=sp.HUMAN, status="Alive")
CAPTAIN_BLUDGE = NPCEntry("Captain Bludge")
CAPTAIN_COODER_OF_THE_SWIFTWATER_WARDEN_COODER = NPCEntry(
    "Captain Cooder of the Swiftwater / Warden Cooder", species=sp.HUMAN
)
CAPTAIN_GRIT_JABIR = NPCEntry("Captain Grit Jabir", species=sp.HUMAN)
CAPTAIN_JUKA = NPCEntry("Captain Juka", species=sp.HUMAN)
CAPTAIN_KLOW = NPCEntry("Captain Klow", species=sp.HUMAN)
CAPTAIN_MOODY = NPCEntry("Captain Moody", species=sp.HUMAN, status="Dead")
CAPTAIN_RUE = NPCEntry("Captain Rue", species=sp.HUMAN, status="Deceased")
CAPTAIN_SHEVEZ = NPCEntry("Captain Shevez")
CAPTAIN_VANEGULL = NPCEntry("Captain Vanegull", species=sp.HUMAN)
CAYLIN = NPCEntry("Caylin", species=sp.HUMAN, status="Dead")
CAYLIN_S_MOTHER = NPCEntry("Caylin's mother", species=sp.HUMAN, status="Dead")
CHANCELLOR_HELENA_PRIMAVERA = NPCEntry("Chancellor Helena Primavera", species=sp.HUMAN)
CHANCELLOR_HYPATIA = NPCEntry("Chancellor Hypatia", species=sp.HUMAN)
CHARIS = NPCEntry("Charis", species=sp.HUMAN)
CHARLOTTE = NPCEntry("Charlotte", species=sp.DOGG)
CHIARA_SUNCREST = NPCEntry("Chiara Suncrest")
CHOWDER = NPCEntry("Chowder", species=sp.ZOMBIE)
CHUM = NPCEntry("Chum", species=sp.ZOMBIE, status="Dead")
CIRRUS = NPCEntry("Cirrus", species=sp.HUMAN)
COBBS = NPCEntry("Cobbs", species=sp.HUMAN)
COUNTESS_CAMILLA = NPCEntry("Countess Camilla")
COX = NPCEntry("Cox")
CUTTY = NPCEntry("Cutty", species=sp.ZOMBIE, status="Dead")
DANU_ASHENGUARD = NPCEntry("Danu Ashenguard", species=sp.HUMAN)
DAN_LU_KOTORI_GALEWARDEN = NPCEntry("Dan Lu, Kotori Galewarden", species=sp.HUMAN)
DARIAN = NPCEntry("Darian", species=sp.HUMAN, status="Dead")
DARIUS = NPCEntry("Darius", species=sp.HUMAN)
DARYAS_NIMBUS = NPCEntry("Daryas Nimbus")
DAVNIR = NPCEntry("Davnir", species=sp.ANCIENT, status="Deceased")
DAXIUS = NPCEntry("Daxius", species=sp.HUMAN, status="Dead")
DEMETRIOS = NPCEntry("Demetrios", species=sp.BRUTE)
DERVIN_MASTER_OF_BEASTS = NPCEntry("Dervin, Master of Beasts", species=sp.HUMAN, epithets=("Master of Beasts",))
DHERIC = NPCEntry("Dheric", species=sp.HUMAN, status="Deceased")
DR_KREST_MORTIMER_THE_FIXER = NPCEntry(
    "Dr. Krest Mortimer, 'The Fixer'",
    species=sp.HUMAN,
    epithets=("'The Fixer'",),
    short_names=("Mortimer",),
)
DR_WYVERSTONE = NPCEntry("Dr. Wyverstone", species=sp.HUMAN)
DUKE_DREXEN = NPCEntry("Duke Drexen", species=sp.HUMAN)
DUNRIC_VARGAS = NPCEntry("Dunric Vargas", species=sp.HUMAN)
EBBA = NPCEntry("Ebba", species=sp.HUMAN, status="Alive")
EFARIS_BRITTLEBONE = NPCEntry("Efaris Brittlebone", species=sp.HUMAN)
EINAR = NPCEntry("Einar", species=sp.HUMAN)
EIRINA = NPCEntry("Eirina", species=sp.HUMAN, status="Deceased")
ELDON_LOST_KNIGHT = NPCEntry("Eldon, Lost Knight", species=sp.HUMAN, epithets=("Lost Knight",))
ELIAS_EDGECOMBE = NPCEntry("Elias Edgecombe", species=sp.HUMAN)
EMEVIERE = NPCEntry("Emeviere")
ENFORCER_EESHA = NPCEntry("Enforcer Eesha", species=sp.HUMAN)
ERSEBET = NPCEntry("Ersebet")
EUN = NPCEntry("Eun", species=sp.HUMAN, status="Deceased")
EXECUTIVE_SMYTE = NPCEntry("Executive Smyte", species=sp.HUMAN)
FARIN_THE_PORTER = NPCEntry("Farin the Porter", species=sp.HUMAN)
FARRIS = NPCEntry("Farris", species=sp.HUMAN)
FAYYAD = NPCEntry("Fayyad", species=sp.HUMAN, status="Alive")
FELIX = NPCEntry("Felix", species=sp.HUMAN)
FERAL = NPCEntry("Feral", species=sp.HUMAN)
FIGHTMASTER_KOX = NPCEntry("Fightmaster Kox", species=sp.GOBLIN)
FIGHTMASTER_RUSTY = NPCEntry("Fightmaster Rusty", species=sp.DWARF)
FLANNIGAN = NPCEntry("Flannigan", species=sp.HUMAN)
FOREMAN_PEBB = NPCEntry("Foreman Pebb")
FREYA_ELDINGSTURM = NPCEntry("Freya Eldingsturm")
FUGGER_GRIMES = NPCEntry("Fugger Grimes")
FYANNA_REDMOOR_BOLTYN_S_COUSIN = NPCEntry("Fyanna Redmoor, Boltyn's cousin", species=sp.HUMAN)
GALAPHOR = NPCEntry("Galaphor", species=sp.HUMAN, status="Deceased")
GALCIA = NPCEntry("Galcia", species=sp.ANCIENT, status="Deceased")
GAWAIN = NPCEntry("Gawain", species=sp.HUMAN)
GENERAL_CHUL = NPCEntry("General Chul", species=sp.HUMAN)
GENERAL_EKODA = NPCEntry("General Ekoda", species=sp.HUMAN)
GENERAL_NAKAMI = NPCEntry("General Nakami", species=sp.HUMAN)
GENERAL_RIKU = NPCEntry("General Riku", species=sp.HUMAN, status="Dead")
GENERAL_YAMATOKA = NPCEntry("General Yamatoka", species=sp.HUMAN, status="Alive")
GIANTSLAYER_CRIX = NPCEntry("Giantslayer Crix", species=sp.HUMAN)
GOVERNOR_PRACTISS = NPCEntry("Governor Practiss", species=sp.HUMAN)
GAVIN = NPCEntry("Gavin")
"""Named once, at krest-mortimer.md:39 — he owes Mortimer a favour. Species and
status are left to default rather than guessed."""
GRAHAM_THE_GALLANT = NPCEntry("Graham the Gallant", species=sp.HUMAN)
GRANDMASTER_LI = NPCEntry("Grandmaster Li", species=sp.HUMAN)
GRAND_MAGISTER_THE_ADAMANT = NPCEntry("Grand Magister, the Adamant", species=sp.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_BELOVED = NPCEntry("Grand Magister, the Beloved", species=sp.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_DEVOUT = NPCEntry("Grand Magister, the Devout", species=sp.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_RADIANT = NPCEntry("Grand Magister, the Radiant", species=sp.HUMAN)
GRAND_MAGISTER_THE_STEADFAST = NPCEntry("Grand Magister, The Steadfast", species=sp.HUMAN)
"""Five rows for one office, and the case drift on ``The Steadfast`` makes it six
spellings' worth of hash. Adamant and Beloved had npcs.csv rows and no constant at
all until stage 4 needed every species declared somewhere. Stage 6 collapses the
five into one title with five holders; until then they are five NPCs."""
GREENBIRD = NPCEntry("Greenbird", species=sp.HUMAN)
GROTA = NPCEntry("Grota", species=sp.HUMAN, status="Alive")
GUDO_MISTWARD_PILGRIM = NPCEntry("Gudo, Mistward Pilgrim", species=sp.HUMAN)
HANK = NPCEntry("Hank", species=sp.HUMAN, status="Alive")
HARLAND = NPCEntry("Harland")
HAROLD_HONEYSETT = NPCEntry("Harold Honeysett", species=sp.HUMAN)
HELX = NPCEntry("Helx")
HIGHTARN = NPCEntry("Hightarn", status="Dead")
HILDEGUN = NPCEntry("Hildegun", species=sp.HUMAN)
HIREI = NPCEntry("Hirei", species=sp.HUMAN)
HISATO = NPCEntry("Hisato", species=sp.HUMAN)
HOG = NPCEntry("Hog", species=sp.HUMAN)
HUXLEY = NPCEntry("Huxley", species=sp.HUMAN)
HYRINTH = NPCEntry("Hyrinth")
INQUISITOR_ARICIA = NPCEntry("Inquisitor Aricia")
IRUNAMEABH = NPCEntry("Írunaméabh")
JACKDAW = NPCEntry("Jackdaw", species=sp.HUMAN)
JEEVES = NPCEntry("Jeeves", species=sp.HUMAN)
JEMJANG = NPCEntry("Jemjang", species=sp.HUMAN, status="Dead")
JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS = NPCEntry("Jezabelle, Everfest Healer and Allsorts", species=sp.HUMAN)
JIGSAW = NPCEntry("Jigsaw", species=sp.HUMAN, status="Alive")
JING = NPCEntry("Jing", species=sp.HUMAN, status="Alive")
JUICE = NPCEntry("Juice", species=sp.HUMAN)
JULES_TEKLOVOSSEN = NPCEntry("Jules Teklovossen", species=sp.HUMAN, status="Alive")
KALSHARPE = NPCEntry("Kalsharpe", species=sp.HUMAN)
KARL = NPCEntry("Karl")
KAYAT = NPCEntry("Kayat", status="Dead")
KAYSIN = NPCEntry("Kaysin")
KAZUO = NPCEntry("Kazuo", species=sp.HUMAN)
KELPIE = NPCEntry("Kelpie", species=sp.ZOMBIE)
KIEN = NPCEntry("Kien", species=sp.HUMAN, status="Deceased")
KIRIGAMI = NPCEntry("Kirigami")
KNUCKLES = NPCEntry("Knuckles", species=sp.HUMAN, status="Dead")
KOSSEN = NPCEntry("Kossen", species=sp.HUMAN)
KOUKI = NPCEntry("Kouki", species=sp.HUMAN)
KYLE = NPCEntry("Kyle", species=sp.HUMAN)
LADY_BARTHIMONT = NPCEntry(
    "Lady Barthimont",
    species=sp.HUMAN,
    status="Deceased",
    short_names=("Barthimont",),
)
LADY_VERA_SUTCLIFFE = NPCEntry("Lady Vera Sutcliffe", species=sp.HUMAN)
LENA_BELLE = NPCEntry("Lena Belle", species=sp.HUMAN)
LEONA = NPCEntry("Leona")
LIEUTENANT_LI = NPCEntry("Lieutenant Li", species=sp.HUMAN)
LIEUTENANT_TIMAEUS = NPCEntry("Lieutenant Timaeus", species=sp.HUMAN)
LIEUTENANT_YAMADA = NPCEntry("Lieutenant Yamada", species=sp.HUMAN, status="Dead")
LILJA = NPCEntry("Lilja", species=sp.HUMAN)
LIMPIT = NPCEntry("Limpit", species=sp.ZOMBIE, status="Dead")
LINNEA_MISTRESS_OF_MALADY = NPCEntry("Linnea, Mistress of Malady", species=sp.HUMAN, epithets=("Mistress of Malady",))
LISHU_CRIMSON_HAZE_VIGILANTE = NPCEntry("Lishu, Crimson Haze Vigilante", species=sp.HUMAN)
LORD_MERCHANT_SAVAI = NPCEntry("Lord Merchant Savai", species=sp.HUMAN, status="Dead")
LORD_SABUTO = NPCEntry("Lord Sabuto", species=sp.HUMAN)
LORD_SUTCLIFFE = NPCEntry("Lord Sutcliffe", species=sp.HUMAN, status="Just a head")
LORD_WIZARD_CHIYO = NPCEntry("Lord Wizard Chiyo", status="Dead")
LUCA_ARENA_CICERONE = NPCEntry("Luca, Arena Cicerone", species=sp.HUMAN, status="Alive")
LUCILLA_THE_SETTING_SUN = NPCEntry("Lucilla the Setting Sun")
MABON = NPCEntry("Mabon", species=sp.HUMAN)
MADAM_ROUGE = NPCEntry("Madam Rouge", species=sp.HUMAN, status="Dead")
MAD_SIV = NPCEntry("Mad Siv")
MAELA_ISULFV = NPCEntry("Maela Isulfv")
MAELA_FAIRMIND = NPCEntry("Maela Fairmind")
MAELA_ONE_EYE = NPCEntry("Maela One-eye")
MAELA_SHARENA = NPCEntry("Maela Sharena")
MAGISTRATE_CHEN = NPCEntry("Magistrate Chen", species=sp.HUMAN)
MAGNUS_THE_VIGILANT = NPCEntry("Magnus the Vigilant", species=sp.HUMAN)
MAGPIE = NPCEntry("Magpie", species=sp.HUMAN, status="Alive")
MARBLES = NPCEntry("Marbles", species=sp.MEEP)
MARCUS = NPCEntry("Marcus", species=sp.HUMAN)
MARCUS_MAULER_MONROE = NPCEntry("Marcus 'Mauler' Monroe", species=sp.HUMAN, status="Alive")
MASTER_MORITA_ART_OF_THE_HAND = NPCEntry("Master Morita, Art of the Hand", species=sp.HUMAN, status="Alive")
MASTER_SAORI = NPCEntry("Master Saori", species=sp.HUMAN, status="Alive")
MASTER_TAKUMI = NPCEntry("Master Takumi", species=sp.HUMAN, status="Alive")
MASTER_UDO = NPCEntry("Master Udo", species=sp.HUMAN)
MAXWELL = NPCEntry("Maxwell", species=sp.HUMAN)
MELDRICK_SUDDS = NPCEntry("Meldrick Sudds", species=sp.HUMAN, status="Alive")
MERLEN_RIVERA = NPCEntry("Merlen Rivera", species=sp.HUMAN)
METIS_ARCHANGEL_OF_TENACITY = NPCEntry(
    "Metis, Archangel of Tenacity",
    species=sp.HERALD,
    epithets=("Archangel of Tenacity",),
)
MIKAEL = NPCEntry("Mikael", species=sp.HUMAN)
MIKU = NPCEntry("Miku", species=sp.HUMAN)
MINERVA_THEMIS = NPCEntry(
    "Minerva Themis",
    species=sp.HUMAN,
    status="Deceased",
    other_characters_story_key="other-characters/minerva-themis.md",
    short_names=("Minerva",),
)
MIN_OF_THE_FOREST_OF_FLAMES = NPCEntry("Min of the Forest of Flames", species=sp.HUMAN)
MIRAGAI = NPCEntry("Miragai", species=sp.DRAGON)
MISS_Q = NPCEntry("Miss Q")
MOLLY_THE_MOP = NPCEntry("Molly the Mop", species=sp.HUMAN, status="Alive")
MOLOCA = NPCEntry("Moloca")
MORAY = NPCEntry("Moray", species=sp.HUMAN)
MORAY_LE_FAY = NPCEntry("Moray Le Fay", species=sp.ZOMBIE)
MORGAN = NPCEntry("Morgan", species=sp.HUMAN)
MORGA_GRINNING_BOAR_CANTINA_BARMAID = NPCEntry("Morga, Grinning Boar Cantina Barmaid", species=sp.HUMAN)
"""No epithet. The glued tail is a place plus a job — the ``Grinning Boar Cantina``
locations row and the profession ``Barmaid`` — so both halves wait for R9 rather
than being read as a style she is known by."""
MUTINOUS_MAGGIE = NPCEntry("Mutinous Maggie", species=sp.HUMAN)
NAILBIT_NARI = NPCEntry("Nailbit Nari", species=sp.HUMAN)
NARAKIR = NPCEntry("Narakir", species=sp.WELKIN)
NASRETH = NPCEntry("Nasreth", species=sp.EMBRA)
NESTUS = NPCEntry("Nestus")
NING_KOTORI_MOONSEEKER = NPCEntry("Ning, Kotori Moonseeker", species=sp.HUMAN)
NJERI = NPCEntry("Njeri", species=sp.HUMAN)
ONE_EYE = NPCEntry("One Eye", species=sp.HUMAN, status="Alive")
OTMAR = NPCEntry("Otmar", species=sp.HUMAN)
OVERSEER_CRICHTON = NPCEntry("Overseer Crichton", species=sp.HUMAN, status="Dead")
OZRIM = NPCEntry("Ozrim", species=sp.ROSETTA)
PALLAS = NPCEntry("Pallas", species=sp.HUMAN)
PEARL_SANDHRI = NPCEntry("Pearl Sandhri", species=sp.HUMAN, status="Alive")
PELORUS = NPCEntry("Pelorus", species=sp.HUMAN, status="Alive")
PINWHEEL = NPCEntry("Pinwheel", species=sp.HUMAN, status="Deceased")
POLLY_CRANKA = NPCEntry("Polly Cranka", species=sp.PARROT, status="Alive")
PROFESSOR_MIN = NPCEntry("Professor Min", species=sp.HUMAN)
PROSPECTOR_COGMIRE = NPCEntry("Prospector Cogmire", species=sp.HUMAN)
QUARREL = NPCEntry("Quarrel", species=sp.HUMAN, status="Alive")
QUEEN_OF_CANDLEHOLD = NPCEntry("Queen of Candlehold", species=sp.ROSETTA)
RAGNAR_FROSTHELM = NPCEntry("Ragnar Frosthelm", species=sp.HUMAN)
RAVEN_AESIR_OF_CHAOS = NPCEntry("Raven, Aesir of Chaos", species=sp.AESIR, epithets=("Aesir of Chaos",))
RAY_STINGEYE = NPCEntry("Ray Stingeye", species=sp.HUMAN)
REINA_SPIRIT_CALLER = NPCEntry("Reina, Spirit Caller", species=sp.HUMAN, epithets=("Spirit Caller",))
REX_BIGGUN = NPCEntry("Rex Biggun", species=sp.HUMAN)
REZ = NPCEntry("Rez", species=sp.HUMAN)
REZNYR_ELDINGSTURM = NPCEntry("Reznyr Eldingsturm")
RICKY_ROYCE = NPCEntry("Ricky Royce", species=sp.HUMAN)
RIGGERMORTIS = NPCEntry("Riggermortis", species=sp.ZOMBIE, status="Dead")
RIGO = NPCEntry("Rigo", species=sp.ROBOT, status="Spider-bot assistant to Jules Teklovossen")
RUPIUS_AURIC_SCROLLMASTER = NPCEntry("Rupius, Auric Scrollmaster", species=sp.HUMAN)
SADA = NPCEntry("Sada", status="Alive")
SALVADOR_STALLION = NPCEntry("Salvador Stallion")
SANDY_SHOO = NPCEntry("Sandy Shoo", species=sp.HUMAN)
SANNI = NPCEntry("Sanni", species=sp.HUMAN)
SATSUKI = NPCEntry("Satsuki", species=sp.HUMAN, status="Alive")
SAYASHI_CARA = NPCEntry("Sayashi Cara", species=sp.HUMAN)
SCOOBA = NPCEntry("Scooba", species=(sp.ZOMBIE, sp.DOG))
SEKEM_ARCHANGEL_OF_RAVAGES = NPCEntry(
    "Sekem, Archangel of Ravages",
    species=sp.HERALD,
    epithets=("Archangel of Ravages",),
)
SEPTUS = NPCEntry("Septus")
SERAPHINA = NPCEntry("Seraphina", species=sp.HUMAN)
SETO_OF_MIHARU = NPCEntry("Seto of Miharu", species=sp.HUMAN, status="Alive")
SHELLY = NPCEntry("Shelly", species=sp.ZOMBIE, status="Dead")
SHIO = NPCEntry("Shio", species=sp.HUMAN)
SHIRO = NPCEntry("Shiro", species=sp.HUMAN, status="Alive")
SIDRIZ = NPCEntry("Sidriz")
SKYNDA_FEYSCOUT = NPCEntry("Skynda Feyscout")
SLAPSTICK_SAL = NPCEntry("Slapstick Sal")
SLINGER = NPCEntry("Slinger", species=sp.HUMAN, status="Alive")
SOL = NPCEntry("Sol", species=sp.AESIR)
SOREN = NPCEntry("Soren", species=sp.HUMAN)
SPEAKEASY = NPCEntry("Speakeasy")
SPOKES = NPCEntry("Spokes", species=sp.HUMAN)
SQUIDGE = NPCEntry("Squidge", species=sp.HUMAN, status="Dead")
STICKY_FINGERS = NPCEntry("Sticky Fingers", species=sp.OCTOPUS, status="Alive")
SUMIRE = NPCEntry("Sumire", species=sp.HUMAN)
SURAJ_THE_ORACLE = NPCEntry("Suraj the Oracle", species=sp.HUMAN)
SURAYA_ARCHANGEL_OF_KNOWLEDGE = NPCEntry(
    "Suraya, Archangel of Knowledge",
    species=sp.HERALD,
    epithets=("Archangel of Knowledge", "Archangel of Erudition", "Arcane Herald"),
)
SWABBIE = NPCEntry("Swabbie", species=sp.ZOMBIE)
SWILLER_SALTBEARD = NPCEntry("Swiller Saltbeard", species=sp.HUMAN)
SYBERYS = NPCEntry("Syberys")
SYNTHEA_TEKLO = NPCEntry("Synthea Teklo", species=sp.HUMAN)
SYNVERI = NPCEntry("Synveri", species=sp.HUMAN)
TAKA = NPCEntry("Taka", species=sp.HUMAN, status="Alive")
TARA_VANGELD = NPCEntry("Tara VanGeld", species=sp.DWARF)
TASHA_OF_DESHVAHAN = NPCEntry("Tasha of Deshvahan")
TASKMASTER_PYRION = NPCEntry("Taskmaster Pyrion", species=sp.HUMAN)
TEMPLAR_TIMAERUS = NPCEntry("Templar Timaerus", species=sp.HUMAN)
TETZUO = NPCEntry("Tetzuo", species=sp.HUMAN, status="Alive")
THANUELLA = NPCEntry("Thanuella")
THEBASTO_MAGISTER_OF_DEFENSE = NPCEntry("Thebasto, Magister of Defense", species=sp.HUMAN, status="Alive")
THEMIS_KEEPER_OF_THE_SCALES = NPCEntry(
    "Themis, Keeper of the Scales",
    species=sp.HERALD,
    epithets=("Keeper of the Scales", "Archangel of Judgment"),
)
THEODORE_HAMILTON_SCARBOROUGH = NPCEntry("Theodore Hamilton Scarborough", species=sp.HUMAN)
THE_BASTION = NPCEntry("The Bastion")
THE_HARVESTER = NPCEntry("The Harvester", species=sp.HUMAN)
THE_LIBRARIAN = NPCEntry(
    "The Librarian",
    other_characters_story_key="other-characters/the-librarian.md",
    short_names=("Librarian",),
)
THIROUX = NPCEntry("Thiroux", species=sp.HUMAN)
THUK = NPCEntry("Thuk", species=sp.BRUTE)
TIRIL = NPCEntry("Tiril", species=sp.HUMAN)
TOGARK_THE_WRANGLER = NPCEntry("Togark the Wrangler", species=sp.HUMAN, status="Deceased")
TOHIRO_ETERNAL_SCRIBE = NPCEntry("Tohiro, Eternal Scribe", species=sp.HUMAN)
TOMASS = NPCEntry("Tomass", species=sp.HUMAN)
TOROJA_OF_ISHIGAKI = NPCEntry("Toroja of Ishigaki", species=sp.HUMAN, status="Dead")
URSUR = NPCEntry("Ursur", species=sp.EMBRA)
VAIL_THE_VAGRANT = NPCEntry("Vail the Vagrant", species=sp.HUMAN)
VALERIA = NPCEntry("Valeria", species=sp.HUMAN)
VALGARD_HOARFROST = NPCEntry("Valgard Hoarfrost", species=sp.HUMAN)
VANIK_SILVERTOOTH = NPCEntry("Vanik Silvertooth")
VERA = NPCEntry("Vera", species=sp.HUMAN)
VICTORIA_ARCHANGEL_OF_TRIUMPH = NPCEntry(
    "Victoria, Archangel of Triumph",
    species=sp.HERALD,
    epithets=("Archangel of Triumph",),
)
VIDYA_WILLOWMERE = NPCEntry("Vidya Willowmere")
VITUS = NPCEntry("Vitus", species=sp.HUMAN)
VYHARA_CLOUDBURST = NPCEntry("Vyhara Cloudburst")
WAILER = NPCEntry("Wailer", species=sp.ZOMBIE, status="Dead")
WENDRYN = NPCEntry("Wendryn", species=sp.HUMAN, status="Deceased")
WHEELER = NPCEntry("Wheeler", species=sp.HUMAN, status="Alive")
WHISPERS_OF_XERYS = NPCEntry("Whispers of Xerys")
WHITETAIL = NPCEntry("Whitetail", species=sp.HUMAN, status="Alive")
WIDOW_JOHANA = NPCEntry("Widow Johana", species=sp.HUMAN)
WYNVARIN = NPCEntry("Wynvarin", species=sp.HUMAN)
XAINE_RUNESCRIBE = NPCEntry("Xaine, Runescribe", species=sp.HUMAN, status="Dead")
XILIN = NPCEntry("Xilin", species=sp.HUMAN, status="Dead")
XIN = NPCEntry("Xin", species=sp.HUMAN)
YARIN = NPCEntry("Yarin", species=sp.HUMAN)
YUNKAI = NPCEntry("Yunkai", species=sp.HUMAN)
YVOR = NPCEntry("Yvor", species=sp.ANCIENT, status="Deceased")
