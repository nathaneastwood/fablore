"""Canonical character definitions — the one place each character is described.

``character_id`` is a hash of the name (``registry_ids.lore_character_id``), so a
second ``CharacterEntry`` literal for the same character elsewhere would not update this
row, it would compete with it: ``kind``/``status`` preserve-on-empty, and two
non-empty values race on module import order. Define each character once, here.

Story modules reference these as ``people.NAME``. See ``entries/catalogue/__init__.py``
for the split between this package, ``entries/*.py`` and ``descriptions.py``.
"""

from __future__ import annotations

from db import CharacterEntry

from entries.catalogue import kinds as kind

ACHLYS_HAG_OF_MOJIRE = CharacterEntry("Achlys, hag of Mojire", kinds=kind.HUMAN, epithets=("hag of Mojire",))
AEGIS_THE_SHIELD_OF_LIGHT = CharacterEntry(
    "Aegis, the Shield of Light",
    kinds=kind.HERALD,
    epithets=("the Shield of Light", "Archangel of Protection"),
)
ABSOLON = CharacterEntry("Absolon", epithets=("god of the great deep",))


ADU = CharacterEntry("Adu")
AELIUS = CharacterEntry("Aelius", kinds=kind.HUMAN, status="Dead")
AIOS = CharacterEntry(
    "Aios",
    kinds=kind.HUMAN,
    status="Alive",
    kin=(("boltyn", "father", "main-story/monarch/sworn-to-protect.md"),),
)
AKUO = CharacterEntry("Akuo", kinds=kind.HUMAN)
ALKA_BIGGUNS = CharacterEntry("Alka Bigguns", kinds=kind.HUMAN, epithets=("Don of Coppertown",))
AMBER = CharacterEntry("Amber", kinds=kind.HUMAN, status="Alive")
AUDACITY = CharacterEntry("λud@c!ty")
ALIF = CharacterEntry("Alif", kinds=kind.HUMAN, status="Alive")
ALOSYN = CharacterEntry("Alosyn", kinds=kind.HUMAN)
AMIR = CharacterEntry(
    "Amir",
    kinds=kind.HUMAN,
    kin=(("kassai", "child", "main-story/heavy-hitters/bloodied-sands.md"),),
)
AMIRA_SURANA = CharacterEntry("Amira Surana")
ANARCH_ZEIR = CharacterEntry(
    "Anarch Zeir",
    kinds=kind.HUMAN,
    epithets=("First Anarch of L'Apocalypta",),
)
ANHE_KOTORI_WAVEBENDER = CharacterEntry("Anhe, Kotori Wavebender", kinds=kind.HUMAN)
APOSTATE = CharacterEntry("Apostate", kinds=kind.HUMAN)
ARBITER_MAGISTER_OF_JUSTICE = CharacterEntry("Arbiter, Magister of Justice")
ASTIER = CharacterEntry("Astier", kinds=kind.HUMAN)
ASTRA_MORENA = CharacterEntry("Astra Morena")
ASTREA_QUAZOR = CharacterEntry("Astrea Quazor", kinds=kind.HUMAN, status="Alive")
ATEIA = CharacterEntry("Ateia")
AUREA_CHAMPION_OF_THE_DAWN = CharacterEntry(
    "Aurea, Champion of the Dawn", kinds=kind.HUMAN, epithets=("Champion of the Dawn",)
)
AURELIUS = CharacterEntry("Aurelius", kinds=kind.HORSE)
AURIC_SEERESS = CharacterEntry("Auric Seeress", kinds=kind.HUMAN, status="Dead")
AVALON_MESSENGER_OF_THE_DAWN = CharacterEntry(
    "Avalon, Messenger of the Dawn",
    kinds=kind.HERALD,
    epithets=("Messenger of the Dawn", "Archangel of Rebirth"),
)
BAM_BAM = CharacterEntry("Bam Bam", kinds=kind.BRUTE)
BARON_DRIP = CharacterEntry("Baron Drip", kinds=kind.HUMAN)
BARON_THE_BUTCHER = CharacterEntry("Baron the Butcher", kinds=kind.HUMAN, status="Dead")
BARTON = CharacterEntry("Barton", kinds=kind.HUMAN)
BARTON_MOLE = CharacterEntry("Barton Mole", kinds=kind.HUMAN)
BARTRAND_THE_BLOODY = CharacterEntry("Bartrand the Bloody", kinds=kind.HUMAN)
BARUS_BOLDSTRIDE = CharacterEntry("Barus Boldstride", kinds=kind.HUMAN)
AZVOLAI = CharacterEntry("Azvolai", kinds=kind.DRAGON)
BATBITER = CharacterEntry("Batbiter")
BAZZ = CharacterEntry("Bazz", kinds=kind.HUMAN, status="Dead")
BEAK = CharacterEntry("Beak", kinds=kind.HUMAN)
BEEZY_THE_BRASH = CharacterEntry("Beezy the Brash", kinds=kind.HUMAN, status="Dead")
BELLONA_THE_WARTUNE_HERALD = CharacterEntry(
    "Bellona, the Wartune Herald",
    kinds=kind.HERALD,
    epithets=("the Wartune Herald", "Archangel of War"),
)
BISKI = CharacterEntry("Biski", kinds=kind.DOG)
BLASMOPHET = CharacterEntry("Blasmophet", kinds=kind.EMBRA, epithets=("the Soul Harvester",))
BLAVE = CharacterEntry("Blave", kinds=kind.HUMAN, status="Dead")
BLIND_BOGGY = CharacterEntry("Blind Boggy")
BLOODWORTH_GOLDMANE = CharacterEntry(
    "Bloodworth Goldmane",
    kin=(("lyath", "child", "heroes-of-rathe/lyath-about.md"),),
)
BOJANI = CharacterEntry("Bojani", kinds=kind.HUMAN, status="Dead")
BOO = CharacterEntry("Boo")
BRAUMEISTER_BALEN = CharacterEntry(
    "Braumeister Balen",
    kinds=kind.HUMAN,
    status="Alive",
    kin=(
        (
            "valda",
            "child",
            "main-story/mastery-pack-guardian/trouble-in-larinkmorth.md",
            "adoptive",
        ),
    ),
)
BREWMEISTER_MARV = CharacterEntry("Brewmeister Marv", kinds=kind.HUMAN)
BRUTUS_SUMMA_RUDIS = CharacterEntry("Brutus, Summa Rudis")
BUTCHER_JEK = CharacterEntry("Butcher Jek", kinds=kind.HUMAN)
BUTTONS = CharacterEntry("Buttons", kinds=kind.HUMAN, status="Alive")
CAGER = CharacterEntry("Cager", kinds=kind.HUMAN, status="Alive")
CAOIMHE = CharacterEntry("Caoimhe", kinds=kind.HUMAN, epithets=("Witch",))
CAPTAIN_BLUDGE = CharacterEntry("Captain Bludge")
CAPTAIN_COODER_OF_THE_SWIFTWATER_WARDEN_COODER = CharacterEntry(
    "Captain Cooder of the Swiftwater / Warden Cooder", kinds=kind.HUMAN
)
CAPTAIN_GRIT_JABIR = CharacterEntry("Captain Grit Jabir", kinds=kind.HUMAN)
CAPTAIN_JUKA = CharacterEntry("Captain Juka", kinds=kind.HUMAN)
CAPTAIN_KLOW = CharacterEntry("Captain Klow", kinds=kind.HUMAN)
CAPTAIN_MOODY = CharacterEntry("Captain Moody", kinds=kind.HUMAN, status="Dead")
CAPTAIN_RUE = CharacterEntry("Captain Rue", kinds=kind.HUMAN, status="Dead")
CAPTAIN_SHEVEZ = CharacterEntry("Captain Shevez")
CAPTAIN_VANEGULL = CharacterEntry("Captain Vanegull", kinds=kind.HUMAN)
CAREM_DUNFIRTH = CharacterEntry("Carem Dunfirth", status="Dead", epithets=("of the Scarborough Expedition",))
CARVA = CharacterEntry(
    "Carva",
    kinds=kind.HUMAN,
    status="Dead",
    kin=((BLAVE, "sibling", "main-story/outsiders/the-spiders-trap.md"),),
)
CAYLIN = CharacterEntry("Caylin", kinds=kind.HUMAN, status="Dead")
CAYLIN_S_MOTHER = CharacterEntry("Caylin's mother", kinds=kind.HUMAN, status="Dead")
CHANCELLOR_HELENA_PRIMAVERA = CharacterEntry("Chancellor Helena Primavera", kinds=kind.HUMAN)
CHANCELLOR_HYPATIA = CharacterEntry("Chancellor Hypatia", kinds=kind.HUMAN)
CHANCELLOR_YAMA = CharacterEntry("Chancellor Yama", kinds=kind.HUMAN)
CHARIS = CharacterEntry("Charis", kinds=kind.HUMAN)
CHARLOTTE = CharacterEntry("Charlotte", kinds=kind.ROBOT)
CHIARA_SUNCREST = CharacterEntry("Chiara Suncrest")
CHOWDER = CharacterEntry("Chowder", kinds=kind.ZOMBIE)
CHUM = CharacterEntry("Chum", kinds=kind.ZOMBIE, status="Dead")
CIRRUS = CharacterEntry("Cirrus", kinds=kind.HUMAN)
CLARA = CharacterEntry("Clara", kinds=kind.HUMAN)
COBBS = CharacterEntry("Cobbs", kinds=kind.HUMAN)
CORVA = CharacterEntry("Corva", kinds=kind.HUMAN, status="Dead", epithets=("Biomancer",))
COUNTESS_CAMILLA = CharacterEntry("Countess Camilla")
COX = CharacterEntry("Cox")
CUTTY = CharacterEntry("Cutty", kinds=kind.ZOMBIE, status="Dead")
DAIJO = CharacterEntry("Daijo", kinds=kind.HUMAN)
DANU_ASHENGUARD = CharacterEntry("Danu Ashenguard", kinds=kind.HUMAN)
DAN_LU_KOTORI_GALEWARDEN = CharacterEntry("Dan Lu, Kotori Galewarden", kinds=kind.HUMAN)
DARIAN = CharacterEntry("Darian", kinds=kind.HUMAN, status="Dead")
DARIUS = CharacterEntry("Darius", kinds=kind.HUMAN)
DARYAS_NIMBUS = CharacterEntry("Daryas Nimbus")
CROMAI = CharacterEntry("Cromai", kinds=kind.DRAGON)
DAVNIR = CharacterEntry(
    "Davnir",
    kinds=kind.ANCIENT,
    status="Dead",
    epithets=("Ancient of Earth", "Ancient of Earth and Lightning"),
)
DAXIUS = CharacterEntry(
    "Daxius",
    kinds=kind.HUMAN,
    status="Dead",
    kin=((DARIAN, "child", "short-stories/dusk-till-dawn/no-pain-no-gain.md"),),
)
DEMETRIOS = CharacterEntry("Demetrios", kinds=kind.BRUTE)
DENG = CharacterEntry("Deng")
DERVIN_MASTER_OF_BEASTS = CharacterEntry("Dervin, Master of Beasts", kinds=kind.HUMAN, epithets=("Master of Beasts",))
DHERIC = CharacterEntry(
    "Dheric",
    kinds=kind.HUMAN,
    status="Dead",
    kin=(
        (DARIAN, "father", "short-stories/dusk-till-dawn/no-pain-no-gain.md"),
        (DAXIUS, "grandparent", "short-stories/dusk-till-dawn/no-pain-no-gain.md"),
    ),
)
DOMINIA = CharacterEntry("Dominia", kinds=kind.DRAGON)
DRACONA_OPTIMAI = CharacterEntry("Dracona Optimai", kinds=kind.DRAGON)
DR_KREST_MORTIMER_THE_FIXER = CharacterEntry(
    "Dr. Krest Mortimer, 'The Fixer'",
    kinds=kind.HUMAN,
    epithets=("'The Fixer'",),
    short_names=("Mortimer",),
)
DR_WYVERSTONE = CharacterEntry("Dr. Wyverstone", kinds=kind.HUMAN)
DUKE_DREXEN = CharacterEntry("Duke Drexen", kinds=kind.HUMAN)
DUNRIC_VARGAS = CharacterEntry("Dunric Vargas", kinds=kind.HUMAN)
EBBA = CharacterEntry("Ebba", kinds=kind.HUMAN, status="Alive")
EFARIS_BRITTLEBONE = CharacterEntry("Efaris Brittlebone", kinds=kind.HUMAN)
EINAR = CharacterEntry("Einar", kinds=kind.HUMAN)
EIRINA = CharacterEntry(
    "Eirina",
    kinds=kind.HUMAN,
    status="Dead",
    kin=(
        ("boltyn", "spouse", "heroes-of-rathe/boltyn-about.md"),
        (AIOS, "child", "main-story/monarch/sworn-to-protect.md"),
    ),
)
ELDON_LOST_KNIGHT = CharacterEntry("Eldon, Lost Knight", kinds=kind.HUMAN, epithets=("Lost Knight",))
ELIAS_EDGECOMBE = CharacterEntry("Elias Edgecombe", kinds=kind.HUMAN)
EMEVIERE = CharacterEntry("Emeviere")
ENFORCER_EESHA = CharacterEntry("Enforcer Eesha", kinds=kind.HUMAN)
ERSEBET = CharacterEntry("Ersebet")
EUN = CharacterEntry("Eun", kinds=kind.HUMAN, status="Dead")
EXECUTIVE_SMYTE = CharacterEntry("Executive Smyte", kinds=kind.HUMAN)
FAI = CharacterEntry(
    "Fai",
    hero_slug="fai",
    kin=(("dromai", "sibling", "main-story/uprising/dragons-of-empire.md", "adoptive"),),
)
FARIN_THE_PORTER = CharacterEntry("Farin the Porter", kinds=kind.HUMAN)
FARRIS = CharacterEntry("Farris", kinds=kind.HUMAN)
FAYYAD = CharacterEntry("Fayyad", kinds=kind.HUMAN, status="Alive")
FELIX = CharacterEntry("Felix", kinds=kind.HUMAN)
FERAL = CharacterEntry("Feral", kinds=kind.HUMAN)
FIGHTMASTER_KOX = CharacterEntry("Fightmaster Kox", kinds=kind.GOBLIN)
FIGHTMASTER_RUSTY = CharacterEntry("Fightmaster Rusty", kinds=kind.DWARF)
FLANNIGAN = CharacterEntry("Flannigan", kinds=kind.HUMAN)
FLORENCE = CharacterEntry("Florence", kinds=kind.HUMAN, status="Alive")
FOREMAN_PEBB = CharacterEntry("Foreman Pebb")
FRANCESCA_ZINNIA = CharacterEntry("Francesca Zinnia", kinds=kind.HUMAN, status="Dead")
FREYA_ELDINGSTURM = CharacterEntry("Freya Eldingsturm")
FUGGER_GRIMES = CharacterEntry("Fugger Grimes")
FUMEI = CharacterEntry(
    "Fumei",
    kin=(
        (
            "nuu",
            "sibling",
            "main-story/part-the-mistveil/part-4-the-hare-and-the-snake.md",
            "adoptive",
        ),
    ),
)
FYANNA_REDMOOR = CharacterEntry(
    "Fyanna Redmoor",
    kinds=kind.HUMAN,
    kin=(("boltyn", "cousin", "heroes-of-rathe/boltyn-about.md"),),
)
GALAPHOR = CharacterEntry("Galaphor", kinds=kind.HUMAN, status="Dead")
FYENDAL = CharacterEntry("Fyendal")

GALCIA = CharacterEntry(
    "Galcia",
    kinds=kind.ANCIENT,
    status="Dead",
    epithets=("Ancient of Ice",),
)
GAWAIN = CharacterEntry("Gawain", kinds=kind.HUMAN)
GENERAL_CHUL = CharacterEntry("General Chul", kinds=kind.HUMAN)
GENERAL_EKODA = CharacterEntry("General Ekoda", kinds=kind.HUMAN)
GENERAL_KODA = CharacterEntry("General Koda", kinds=kind.HUMAN, status="Dead")
GENERAL_NAKAMI = CharacterEntry("General Nakami", kinds=kind.HUMAN)
GENERAL_RIKU = CharacterEntry("General Riku", kinds=kind.HUMAN, status="Dead")
GENERAL_UMADESU = CharacterEntry("General Umadesu", kinds=kind.HUMAN, status="Dead", short_names=("Umadesu",))
GENERAL_YAMATOKA = CharacterEntry("General Yamatoka", kinds=kind.HUMAN, status="Alive")
GIANTSLAYER_CRIX = CharacterEntry("Giantslayer Crix", kinds=kind.HUMAN)
GOVERNOR_PRACTISS = CharacterEntry("Governor Practiss", kinds=kind.HUMAN)
GAVIN = CharacterEntry("Gavin")
GRAHAM_THE_GALLANT = CharacterEntry("Graham the Gallant", kinds=kind.HUMAN)
GRANDMASTER_LI = CharacterEntry("Grandmaster Li", kinds=kind.HUMAN)
GRAND_MAGISTER_THE_ADAMANT = CharacterEntry("Grand Magister, the Adamant", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_BELOVED = CharacterEntry("Grand Magister, the Beloved", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_DEVOUT = CharacterEntry("Grand Magister, the Devout", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_RADIANT = CharacterEntry("Grand Magister, the Radiant", kinds=kind.HUMAN)
GRAND_MAGISTER_THE_STEADFAST = CharacterEntry("Grand Magister, The Steadfast", kinds=kind.HUMAN)
GRANNIE_SANDLAR = CharacterEntry("Grannie Sandlar", kinds=kind.HUMAN)
GRAVES = CharacterEntry("Graves", kinds=kind.HUMAN, status="Dead")
GREENBIRD = CharacterEntry("Greenbird", kinds=kind.HUMAN)
GROTA = CharacterEntry("Grota", kinds=kind.HUMAN, status="Alive")
GUDO_MISTWARD_PILGRIM = CharacterEntry("Gudo, Mistward Pilgrim", kinds=kind.HUMAN)
HANK = CharacterEntry("Hank", kinds=kind.HUMAN, status="Alive")
HARLAND = CharacterEntry("Harland")
HAROLD_HONEYSETT = CharacterEntry("Harold Honeysett", kinds=kind.HUMAN)
HELX = CharacterEntry("Helx")
HIGHTARN = CharacterEntry("Hightarn", status="Dead")
HILDEGUN = CharacterEntry(
    "Hildegun",
    kinds=kind.HUMAN,
    kin=((EINAR, "child", "main-story/mastery-pack-guardian/trouble-in-larinkmorth.md"),),
)
HIREI = CharacterEntry("Hirei", kinds=kind.HUMAN)
HISATO = CharacterEntry(
    "Hisato",
    kinds=kind.HUMAN,
    kin=(("uzuri", "child", "main-story/outsiders/its-just-business.md"),),
)
HOG = CharacterEntry("Hog", kinds=kind.HUMAN)
HUXLEY = CharacterEntry("Huxley", kinds=kind.HUMAN)
HYRINTH = CharacterEntry("Hyrinth")
INFERNAI = CharacterEntry("Infernai", kinds=kind.AESIR, epithets=("Aesir of Flames",))
INQUISITOR_ARICIA = CharacterEntry("Inquisitor Aricia")
IRUNAMEABH = CharacterEntry("Írunaméabh")
ISEN = CharacterEntry("Isen", kinds=kind.ANCIENT, epithets=("Ancient of Earth and Ice",))
JACKDAW = CharacterEntry("Jackdaw", kinds=kind.HUMAN)
JAPE = CharacterEntry("Jape", kinds=kind.HUMAN, status="Alive")
JEEVES = CharacterEntry("Jeeves", kinds=kind.HUMAN)
JEMJANG = CharacterEntry("Jemjang", kinds=kind.HUMAN, status="Dead")
JEROVE = CharacterEntry("Jerove", kinds=kind.HUMAN, epithets=("the Fleshbinder",))
JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS = CharacterEntry("Jezabelle, Everfest Healer and Allsorts", kinds=kind.HUMAN)
JIGSAW = CharacterEntry("Jigsaw", kinds=kind.HUMAN, status="Alive")
JING = CharacterEntry(
    "Jing",
    kinds=kind.HUMAN,
    status="Alive",
    kin=(("ira", "sibling", "main-story/crucible-of-war/edge-of-autumn.md"),),
)
JIRO_HENSHU = CharacterEntry("Jiro Henshu", kinds=kind.HUMAN)
JUICE = CharacterEntry("Juice", kinds=kind.HUMAN)
JULES_TEKLOVOSSEN = CharacterEntry(
    "Jules Teklovossen",
    kinds=kind.HUMAN,
    status="Alive",
    hero_slug="teklovossen",
    short_names=("Teklovossen",),
)
KALSHARPE = CharacterEntry("Kalsharpe", kinds=kind.HUMAN)
KARALYN = CharacterEntry("Karalyn")
KARL = CharacterEntry("Karl")
KAYAT = CharacterEntry("Kayat", status="Dead")
KAYSIN = CharacterEntry("Kaysin")
KAZUO = CharacterEntry("Kazuo", kinds=kind.HUMAN)
KELPIE = CharacterEntry("Kelpie", kinds=kind.ZOMBIE)
KIEN = CharacterEntry("Kien", kinds=kind.HUMAN, status="Dead")
KIRIGAMI = CharacterEntry("Kirigami")
KNUCKLES = CharacterEntry("Knuckles", kinds=kind.HUMAN, status="Dead")
KOSSEN = CharacterEntry("Kossen", kinds=kind.HUMAN)
KOUKI = CharacterEntry("Kouki", kinds=kind.HUMAN)
KOVA = CharacterEntry("Kova", status="Alive")
KYLE = CharacterEntry("Kyle", kinds=kind.HUMAN)
KYLORIA = CharacterEntry("Kyloria", kinds=kind.DRAGON)
LADY_BARTHIMONT = CharacterEntry(
    "Lady Barthimont",
    kinds=kind.HUMAN,
    status="Dead",
    short_names=("Barthimont",),
)
LADY_VERA_SUTCLIFFE = CharacterEntry("Lady Vera Sutcliffe", kinds=kind.HUMAN)
LEANDER = CharacterEntry("Leander", kinds=kind.HUMAN)
LENA_BELLE = CharacterEntry("Lena Belle", kinds=kind.HUMAN)
LEONA = CharacterEntry("Leona")
LETO = CharacterEntry("Leto", kinds=kind.HUMAN)
LIEUTENANT_LI = CharacterEntry("Lieutenant Li", kinds=kind.HUMAN)
LIEUTENANT_TIMAEUS = CharacterEntry("Lieutenant Timaeus", kinds=kind.HUMAN)
LIEUTENANT_YAMADA = CharacterEntry("Lieutenant Yamada", kinds=kind.HUMAN, status="Dead")
LILJA = CharacterEntry("Lilja", kinds=kind.HUMAN)
LIMPIT = CharacterEntry("Limpit", kinds=kind.ZOMBIE, status="Dead")
LINNEA_MISTRESS_OF_MALADY = CharacterEntry(
    "Linnea, Mistress of Malady", kinds=kind.HUMAN, epithets=("Mistress of Malady",)
)
LISHU_CRIMSON_HAZE_VIGILANTE = CharacterEntry("Lishu, Crimson Haze Vigilante", kinds=kind.HUMAN)
LORD_BARTHIMONT = CharacterEntry(
    "Lord Barthimont",
    kinds=kind.HUMAN,
    kin=((LADY_BARTHIMONT, "spouse", "other-characters/lady-barthimont.md"),),
)
LORD_MERCHANT_SAVAI = CharacterEntry("Lord Merchant Savai", kinds=kind.HUMAN, status="Dead")
LORD_SABUTO = CharacterEntry("Lord Sabuto", kinds=kind.HUMAN)
LORD_SUTCLIFFE = CharacterEntry("Lord Sutcliffe", kinds=kind.HUMAN, status="Unknown")
LORD_WIZARD_AKIHIKO = CharacterEntry("Lord Wizard Akihiko", kinds=kind.HUMAN, status="Dead")
LORD_WIZARD_CHIYO = CharacterEntry(
    "Lord Wizard Chiyo",
    status="Dead",
    kin=(("emperor", "cousin", "main-story/arcane-rising/from-the-ashes.md"),),
)
LUCA_ARENA_CICERONE = CharacterEntry("Luca, Arena Cicerone", kinds=kind.HUMAN, status="Alive")
LUCILLA_THE_SETTING_SUN = CharacterEntry("Lucilla the Setting Sun")
MABON = CharacterEntry("Mabon", kinds=kind.HUMAN)
MADAME_FUSE = CharacterEntry("Madame Fuse", kinds=kind.HUMAN, status="Alive")
MADAM_ROUGE = CharacterEntry("Madam Rouge", kinds=kind.HUMAN, status="Dead")
MAD_SIV = CharacterEntry("Mad Siv")
MAELA_ISULFV = CharacterEntry("Maela Isulfv", short_names=("Isulvf",))
MARA = CharacterEntry("Māra")

MAELA_FAIRMIND = CharacterEntry("Maela Fairmind")
MAELA_ONE_EYE = CharacterEntry("Maela One-eye")
MAELA_SHARENA = CharacterEntry("Maela Sharena")
MAGISTRATE_CHEN = CharacterEntry("Magistrate Chen", kinds=kind.HUMAN)
MAGNUS_THE_VIGILANT = CharacterEntry("Magnus the Vigilant", kinds=kind.HUMAN)
MAGPIE = CharacterEntry("Magpie", kinds=kind.HUMAN, status="Alive")
MARBLES = CharacterEntry("Marbles", kinds=kind.MEEP)
MARCUS = CharacterEntry("Marcus", kinds=kind.HUMAN)
MARCUS_MAULER_MONROE = CharacterEntry("Marcus 'Mauler' Monroe", kinds=kind.HUMAN, status="Alive")
MARROW = CharacterEntry("Marrow", status="Alive")
MASTER_MORITA_ART_OF_THE_HAND = CharacterEntry("Master Morita, Art of the Hand", kinds=kind.HUMAN, status="Alive")
MASTER_SAORI = CharacterEntry("Master Saori", kinds=kind.HUMAN, status="Alive")
MASTER_TAKUMI = CharacterEntry("Master Takumi", kinds=kind.HUMAN, status="Alive")
MASTER_UDO = CharacterEntry("Master Udo", kinds=kind.HUMAN)
MAXWELL = CharacterEntry("Maxwell", kinds=kind.HUMAN)
MEAZE_BANZE = CharacterEntry("Meaze Banze", kinds=kind.HUMAN, status="Alive")
MELDRICK_SUDDS = CharacterEntry("Meldrick Sudds", kinds=kind.HUMAN, status="Alive")
MELTEN_WICK = CharacterEntry("Melten Wick", kinds=kind.HUMAN, status="Alive")
MERLEN_RIVERA = CharacterEntry("Merlen Rivera", kinds=kind.HUMAN)
METIS_ARCHANGEL_OF_TENACITY = CharacterEntry(
    "Metis, Archangel of Tenacity",
    kinds=kind.HERALD,
    epithets=("Archangel of Tenacity",),
)
MIKAEL = CharacterEntry("Mikael", kinds=kind.HUMAN)
MIKU = CharacterEntry("Miku", kinds=kind.HUMAN)
MINAKO = CharacterEntry("Minako", kinds=kind.HUMAN)
MINERVA_THEMIS = CharacterEntry(
    "Minerva Themis",
    kinds=kind.HUMAN,
    status="Dead",
    other_characters_story_key="other-characters/minerva-themis.md",
    short_names=("Minerva",),
)
MERCURIUS = CharacterEntry(
    "Mercurius",
    kinds=kind.HUMAN,
    status="Dead",
    kin=((MINERVA_THEMIS, "sibling", "other-characters/minerva-themis.md"),),
)
MIN_OF_THE_FOREST_OF_FLAMES = CharacterEntry(
    "Min of the Forest of Flames",
    kinds=kind.HUMAN,
    kin=(
        ("fai", "child", "main-story/uprising/fires-of-rebellion.md"),
        ("dromai", "child", "main-story/uprising/betrayal.md", "adoptive"),
    ),
)
MIRAGAI = CharacterEntry("Miragai", kinds=kind.DRAGON)
MISS_Q = CharacterEntry("Miss Q")
MISTRESS_IKARU = CharacterEntry("Mistress Ikaru", kinds=kind.HUMAN)
MITE = CharacterEntry("Mite", kinds=kind.HUMAN)
MO = CharacterEntry("Mo", kinds=kind.HUMAN)
MOLLY_THE_MOP = CharacterEntry("Molly the Mop", kinds=kind.HUMAN, status="Alive")
MOLOCA = CharacterEntry("Moloca")
MORAY = CharacterEntry("Moray", kinds=kind.HUMAN)
MORAY_LE_FAY = CharacterEntry("Moray Le Fay", kinds=kind.ZOMBIE)
MORGAN = CharacterEntry("Morgan", kinds=kind.HUMAN)
MORGA_GRINNING_BOAR_CANTINA_BARMAID = CharacterEntry("Morga, Grinning Boar Cantina Barmaid", kinds=kind.HUMAN)
MUTINOUS_MAGGIE = CharacterEntry("Mutinous Maggie", kinds=kind.HUMAN)
NAILBIT_NARI = CharacterEntry("Nailbit Nari", kinds=kind.HUMAN)
NARAKIR = CharacterEntry("Narakir", kinds=kind.WELKIN)
NASRETH = CharacterEntry("Nasreth", kinds=kind.EMBRA, epithets=("the Soul Harrower",))
NEKRIA = CharacterEntry("Nekria", kinds=kind.DRAGON)
NESTUS = CharacterEntry("Nestus")
NIALL = CharacterEntry("Niall", kinds=kind.HUMAN, epithets=("the Arcanist",))
NING_KOTORI_MOONSEEKER = CharacterEntry("Ning, Kotori Moonseeker", kinds=kind.HUMAN)
NJERI = CharacterEntry(
    "Njeri",
    kinds=kind.HUMAN,
    kin=(("uzuri", "child", "main-story/outsiders/its-just-business.md"),),
)
NOCETES = CharacterEntry("Nocetes", epithets=("God of death",))
ONE_EYE = CharacterEntry("One Eye", kinds=kind.HUMAN, status="Alive")
OTMAR = CharacterEntry("Otmar", kinds=kind.HUMAN)
OUVIA = CharacterEntry("Ouvia", kinds=kind.DRAGON)
OVERSEER_CRICHTON = CharacterEntry("Overseer Crichton", kinds=kind.HUMAN, status="Dead")
ORIEN = CharacterEntry("Orien", status="Alive")
OZRIM = CharacterEntry("Ozrim", kinds=kind.ROSETTA)
PALLAS = CharacterEntry("Pallas", kinds=kind.HUMAN)
PEARL_SANDHRI = CharacterEntry("Pearl Sandhri", kinds=kind.HUMAN, status="Alive")
PELORUS = CharacterEntry("Pelorus", kinds=kind.HUMAN, status="Alive")
PHAELIN = CharacterEntry(
    "Phaelin",
    kinds=kind.HUMAN,
    status="Dead",
    epithets=("purveyor of coal and rice",),
)
PINWHEEL = CharacterEntry("Pinwheel", kinds=kind.HUMAN, status="Dead")
POLLY_CRANKA = CharacterEntry("Polly Cranka", kinds=kind.PARROT, status="Alive")
PROFESSOR_MIN = CharacterEntry("Professor Min", kinds=kind.HUMAN)
PROSPECTOR_COGMIRE = CharacterEntry("Prospector Cogmire", kinds=kind.HUMAN)
QUARREL = CharacterEntry("Quarrel", kinds=kind.HUMAN, status="Alive")
QUEEN_OF_CANDLEHOLD = CharacterEntry("Celvera", kinds=kind.ROSETTA, status="Dead", epithets=("Queen of Candlehold",))
QUENTON = CharacterEntry("Quenton", status="Dead")
RAGNAR_FROSTHELM = CharacterEntry("Ragnar Frosthelm", kinds=kind.HUMAN)
RAVEN = CharacterEntry("Raven", kinds=kind.AESIR, epithets=("Aesir of Chaos",))
RAY_STINGEYE = CharacterEntry("Ray Stingeye", kinds=kind.HUMAN)
REINA_SPIRIT_CALLER = CharacterEntry("Reina, Spirit Caller", kinds=kind.HUMAN, epithets=("Spirit Caller",))
REX_BIGGUN = CharacterEntry("Rex Biggun", kinds=kind.HUMAN)
REZ = CharacterEntry("Rez", kinds=kind.HUMAN)
REZNYR_ELDINGSTURM = CharacterEntry("Reznyr Eldingsturm")
RICKY_ROYCE = CharacterEntry("Ricky Royce", kinds=kind.HUMAN)
RIGGERMORTIS = CharacterEntry("Riggermortis", kinds=kind.ZOMBIE, status="Dead")
RIGO = CharacterEntry("Rigo", kinds=kind.ROBOT, status="Unknown")
RUK_UTAN = CharacterEntry("Ruk'utan", kinds=kind.BRUTE, status="Alive", epithets=("Chief",))
RUPIUS_AURIC_SCROLLMASTER = CharacterEntry("Rupius, Auric Scrollmaster", kinds=kind.HUMAN)
RYO = CharacterEntry("Ryo", kinds=kind.HUMAN)
SADA = CharacterEntry("Sada", status="Alive")
SALVADOR_STALLION = CharacterEntry("Salvador Stallion")
SANDY_SHOO = CharacterEntry("Sandy Shoo", kinds=kind.HUMAN)
SANI = CharacterEntry(
    "Sani",
    kin=(("dromai", "child", "main-story/uprising/dragons-of-empire.md"),),
)

SANNI = CharacterEntry("Sanni", kinds=kind.HUMAN)
SATSUKI = CharacterEntry("Satsuki", kinds=kind.HUMAN, status="Alive")
SAYASHI_CARA = CharacterEntry("Sayashi Cara", kinds=kind.HUMAN)
SCOOBA = CharacterEntry("Scooba", kinds=(kind.ZOMBIE, kind.DOG))
SEKEM_ARCHANGEL_OF_RAVAGES = CharacterEntry(
    "Sekem, Archangel of Ravages",
    kinds=kind.HERALD,
    epithets=("Archangel of Ravages",),
)
SEPTUS = CharacterEntry("Septus")
SERAPHINA = CharacterEntry("Seraphina", kinds=kind.HUMAN)
SETO_OF_MIHARU = CharacterEntry("Seto of Miharu", kinds=kind.HUMAN, status="Alive")
SHAYA_SANDSCOUR = CharacterEntry("Shaya Sandscour")
SHELLY = CharacterEntry("Shelly", kinds=kind.ZOMBIE, status="Dead")
SHIO = CharacterEntry("Shio", kinds=kind.HUMAN)
SHIRO = CharacterEntry("Shiro", kinds=kind.HUMAN, status="Alive")
SIDRIZ = CharacterEntry("Sidriz")
SILKA = CharacterEntry("Silka", kinds=kind.HUMAN, status="Alive")
SILVERHAIR = CharacterEntry("Silverhair")

SKYNDA_FEYSCOUT = CharacterEntry("Skynda Feyscout")
SLAB = CharacterEntry("Slab", kinds=kind.HUMAN, status="Alive")
SLAPSTICK_SAL = CharacterEntry("Slapstick Sal")
SLINGER = CharacterEntry("Slinger", kinds=kind.HUMAN, status="Alive")
SOL = CharacterEntry("Sol", kinds=kind.AESIR, epithets=("Aesir of Light",))
SOREN = CharacterEntry("Soren", kinds=kind.HUMAN)
SPEAKEASY = CharacterEntry("Speakeasy")
SPOKES = CharacterEntry("Spokes", kinds=kind.HUMAN)
SQUIDGE = CharacterEntry("Squidge", kinds=kind.HUMAN, status="Dead")
STICKY_FINGERS = CharacterEntry("Sticky Fingers", kinds=kind.OCTOPUS, status="Alive")
SUMIRE = CharacterEntry("Sumire", kinds=kind.HUMAN)
SURAJ_THE_ORACLE = CharacterEntry("Suraj the Oracle", kinds=kind.HUMAN)
SURAYA_ARCHANGEL_OF_KNOWLEDGE = CharacterEntry(
    "Suraya, Archangel of Knowledge",
    kinds=kind.HERALD,
    epithets=("Archangel of Knowledge", "Archangel of Erudition", "Arcane Herald"),
)
SWABBIE = CharacterEntry("Swabbie", kinds=kind.ZOMBIE)
SWILLER_SALTBEARD = CharacterEntry("Swiller Saltbeard", kinds=kind.HUMAN)
SYBERYS = CharacterEntry("Syberys")
SYNTHEA_TEKLO = CharacterEntry("Synthea Teklo", kinds=kind.HUMAN)
SYNVERI = CharacterEntry("Synveri", kinds=kind.HUMAN)
TAKA = CharacterEntry("Taka", kinds=kind.HUMAN, status="Alive")
TARA_VANGELD = CharacterEntry(
    "Tara VanGeld",
    kinds=kind.DWARF,
    kin=(("lyath", "child", "heroes-of-rathe/lyath-about.md"),),
)
TASHA_OF_DESHVAHAN = CharacterEntry("Tasha of Deshvahan")
TASKMASTER_PYRION = CharacterEntry("Taskmaster Pyrion", kinds=kind.HUMAN)
TEMPLAR_TIMAERUS = CharacterEntry("Templar Timaerus", kinds=kind.HUMAN)
TETZUO = CharacterEntry("Tetzuo", kinds=kind.HUMAN, status="Alive")
THANUELLA = CharacterEntry("Thanuella")
THAWNE = CharacterEntry("Thawne", kinds=kind.DWARF)

THEBASTO_MAGISTER_OF_DEFENSE = CharacterEntry("Thebasto, Magister of Defense", kinds=kind.HUMAN, status="Alive")
THEMAI = CharacterEntry("Themai", kinds=kind.DRAGON)
THEMIS_KEEPER_OF_THE_SCALES = CharacterEntry(
    "Themis, Keeper of the Scales",
    kinds=kind.HERALD,
    epithets=("Keeper of the Scales", "Archangel of Judgment", "Archangel of Justice"),
)
THEODORE_HAMILTON_SCARBOROUGH = CharacterEntry("Theodore Hamilton Scarborough", kinds=kind.HUMAN)
THE_AMBASSADOR = CharacterEntry("The Ambassador", kinds=kind.HUMAN)
THE_EMPRESS = CharacterEntry("The Empress", kinds=kind.HUMAN)
THE_HARVESTER = CharacterEntry("The Harvester", kinds=kind.HUMAN)
THE_LIBRARIAN = CharacterEntry(
    "The Librarian",
    other_characters_story_key="other-characters/the-librarian.md",
    short_names=("Librarian",),
    hero_slug="the-librarian",
)
THIROUX = CharacterEntry(
    "Thiroux",
    kinds=kind.HUMAN,
    kin=(("dash", "child", "short-stories/roll-of-honour/dash.md"),),
)
THUK = CharacterEntry("Thuk", kinds=kind.BRUTE)
TIRIL = CharacterEntry("Tiril", kinds=kind.HUMAN)
TOGARK_THE_WRANGLER = CharacterEntry("Togark the Wrangler", kinds=kind.HUMAN, status="Dead")
TOHIRO_ETERNAL_SCRIBE = CharacterEntry("Tohiro, Eternal Scribe", kinds=kind.HUMAN)
TOMASS = CharacterEntry(
    "Tomass",
    kinds=kind.HUMAN,
    kin=(
        (EINAR, "sibling", "main-story/mastery-pack-guardian/trouble-in-larinkmorth.md"),
        (HILDEGUN, "mother", "main-story/mastery-pack-guardian/trouble-in-larinkmorth.md"),
    ),
)
TOMELTAI = CharacterEntry("Tomeltai", kinds=kind.DRAGON)
TORVAI = CharacterEntry(
    "Torvai",
    kin=(("dromai", "child", "main-story/uprising/dragons-of-empire.md"),),
)

TOROJA_OF_ISHIGAKI = CharacterEntry("Toroja of Ishigaki", kinds=kind.HUMAN, status="Dead")
URSUR = CharacterEntry("Ursur", kinds=kind.EMBRA, epithets=("the Soul Reaper",))
VAIL_THE_VAGRANT = CharacterEntry("Vail the Vagrant", kinds=kind.HUMAN)
VALERIA = CharacterEntry("Valeria", kinds=kind.HUMAN)
VALGARD_HOARFROST = CharacterEntry("Valgard Hoarfrost", kinds=kind.HUMAN)
VANIK_SILVERTOOTH = CharacterEntry("Vanik Silvertooth")
VERA = CharacterEntry("Vera", kinds=kind.HUMAN)
VIATOR = CharacterEntry("Viator", kinds=kind.HUMAN)
VICTORIA_ARCHANGEL_OF_TRIUMPH = CharacterEntry(
    "Victoria, Archangel of Triumph",
    kinds=kind.HERALD,
    epithets=("Archangel of Triumph",),
)
VIDYA_WILLOWMERE = CharacterEntry("Vidya Willowmere")
VITUS = CharacterEntry("Vitus", kinds=kind.HUMAN)
VYHARA_CLOUDBURST = CharacterEntry("Vyhara Cloudburst")
VYNSERAKAI = CharacterEntry("Vynserakai", kinds=kind.DRAGON)
WAILER = CharacterEntry("Wailer", kinds=kind.ZOMBIE, status="Dead")
WENDRYN = CharacterEntry("Wendryn", kinds=kind.HUMAN, status="Dead")
WHEELER = CharacterEntry("Wheeler", kinds=kind.HUMAN, status="Alive")
WHISPER = CharacterEntry("Whisper")
WHISPERS_OF_XERYS = CharacterEntry("Whispers of Xerys")
WHITETAIL = CharacterEntry("Whitetail", kinds=kind.HUMAN, status="Alive")
WIDOW = CharacterEntry("Widow", kinds=kind.HUMAN, status="Alive")
WIDOW_JOHANA = CharacterEntry("Widow Johana", kinds=kind.HUMAN)
WYNVARIN = CharacterEntry("Wynvarin", kinds=kind.HUMAN)
XATHARI = CharacterEntry(
    "Xathari",
    status="Dead",
    epithets=("the Dracai spymaster", "Spymaster Xathari"),
)

XAINE_RUNESCRIBE = CharacterEntry("Xaine, Runescribe", kinds=kind.HUMAN, status="Dead")
XILIN = CharacterEntry(
    "Xilin",
    kinds=kind.HUMAN,
    status="Dead",
    kin=(
        ("ira", "sibling", "main-story/crucible-of-war/edge-of-autumn.md"),
        (JING, "sibling", "main-story/crucible-of-war/edge-of-autumn.md"),
    ),
)
XIN = CharacterEntry("Xin", kinds=kind.HUMAN)
YARIN = CharacterEntry("Yarin", kinds=kind.HUMAN)
YUNKAI = CharacterEntry("Yunkai", kinds=kind.HUMAN)
YENDURAI = CharacterEntry("Yendurai", kinds=kind.DRAGON)
YVOR = CharacterEntry(
    "Yvor",
    kinds=kind.ANCIENT,
    status="Dead",
    epithets=(
        "Ancient of Lightning",
        "Ancient of Lightning and Ice",
        "Ancient of Thunder and Ice",
    ),
)
