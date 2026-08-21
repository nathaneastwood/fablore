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
ABSOLON = NPCEntry("Absolon", epithets=("god of the great deep",))
"""A Dhani deity, and **not a species row** — gods are a role, not a kind of being
(the user's call, 2026-08-21), so both gods reach the generated page through
``grp.DHANI_DEITIES`` instead. The epithet keeps the page's own lower-case "god",
as ``hag of Mojire`` and ``the Shield of Light`` keep theirs.

Reachable only because stage 5 added ``entries/world_of_rathe.py``: he is named as
a god on ``world-of-rathe/high-seas.md:125`` alone. The eight mentions on the
already-declared ``captain-bones-and-the-city-of-gold.md`` are all the Kuraghan
flagship ``Absolon's Dream``, never the god."""


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
ANARCH_ZEIR = NPCEntry(
    "Anarch Zeir",
    species=sp.HUMAN,
    epithets=("First Anarch of L'Apocalypta",),
)
"""``Anarch`` is already in the display name; the epithet is the full title, from
``flavour/compendium-of-rathe.md:76`` — "Zeir, First Anarch of L'Apocalypta"
(PEN277). He is the sole member of ``grp.L_APOCALYPTA``'s roster."""
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
AZVOLAI = NPCEntry("Azvolai", species=sp.DRAGON)
"""One of the eleven dragons stage 5 gave a row (2026-08-21). They were the bulk
of the fourteen names in ``src/data/md/character-groups.md`` that had no database
row of any kind, while ``sp.DRAGON`` held only Miragai.

The hand-written file also carried ``Pronounciation`` and ``Phonetic`` columns for
each. Those are **dropped** rather than migrated (the user's call): ``npcs`` is the
one registry with no prose column, and the identical table already lives at
``archive/world-of-rathe/volcor/welcome-to-volcor.md:19-35`` — verified cell for
cell, "Pronounciation" typo included, only the male-table row order differing."""
BATBITER = NPCEntry("Batbiter")
BAZZ = NPCEntry("Bazz", species=sp.HUMAN, status="Deceased")
BEEZY_THE_BRASH = NPCEntry("Beezy the Brash", species=sp.HUMAN, status="Dead")
BELLONA_THE_WARTUNE_HERALD = NPCEntry(
    "Bellona, the Wartune Herald",
    species=sp.HERALD,
    epithets=("the Wartune Herald", "Archangel of War"),
)
BISKI = NPCEntry("Biski", species=sp.DOG)
BLASMOPHET = NPCEntry("Blasmophet", species=sp.EMBRA, epithets=("the Soul Harvester",))
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
CROMAI = NPCEntry("Cromai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
DAVNIR = NPCEntry(
    "Davnir",
    species=sp.ANCIENT,
    status="Deceased",
    epithets=("Ancient of Earth", "Ancient of Earth and Lightning"),
)
"""Two epithets, both attested, kept the way ``THEMIS_KEEPER_OF_THE_SCALES`` keeps
three (the user's call, 2026-08-21). ``world-of-rathe/aria.md:167`` lists him
alongside his siblings as "Davnir, Ancient of Earth"; ``main-story/tales-of-aria/
amongst-the-brambles.md:9`` writes "Davnir, Ancient of Earth and Lightning". The
hand-written character-groups.md carried only the second, so the form aria.md uses
matched no tooltip."""
DAXIUS = NPCEntry("Daxius", species=sp.HUMAN, status="Dead")
DEMETRIOS = NPCEntry("Demetrios", species=sp.BRUTE)
DERVIN_MASTER_OF_BEASTS = NPCEntry("Dervin, Master of Beasts", species=sp.HUMAN, epithets=("Master of Beasts",))
DHERIC = NPCEntry("Dheric", species=sp.HUMAN, status="Deceased")
DOMINIA = NPCEntry("Dominia", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
DRACONA_OPTIMAI = NPCEntry("Dracona Optimai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
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
FYENDAL = NPCEntry("Fyendal")
"""Named only by a card title — "Fyendal's Fighting Spirit" (UPR194) — whose
flavour line, "The old ways are not forgotten.", does not mention him. Included on
the user's call (2026-08-21), under the same reading that lets the twelve dragons
in from ``Invoke <name>`` titles.

No species and no status: nothing on the page says anything about him. The only
other trace of the name in the registry is the equipment ``Fyendal's Spring
Tunic``, which this page does not name."""

GALCIA = NPCEntry(
    "Galcia",
    species=sp.ANCIENT,
    status="Deceased",
    epithets=("Ancient of Ice",),
)
"""The one Ancient whose epithet the pages and character-groups.md agree on."""
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
all until stage 4 needed every species declared somewhere. Stage 7 collapses the
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
ISEN = NPCEntry("Isen", species=sp.ANCIENT, epithets=("Ancient of Earth and Ice",))
"""**The epithet is on the user's authority, not a page** (2026-08-21). Every other
Ancient's epithet is quoted somewhere; this one is quoted nowhere. Isen himself is
attested — ``main-story/everfest/a-grand-adventure.md:197`` has a wayfarer say
"I've heard legends of the Ancients, Yvor, Davnir, Isen..." — but that line gives
no title, and ``world-of-rathe/aria.md:39`` says only that "Isen stood upon the
mountain's summit and crafted the Isen Ranges with earth and aether", which is the
reading "Earth and Ice" came from rather than an attestation of it.

No ``status``, deliberately. Davnir, Yvor and Galcia are all ``Deceased`` and it
would be easy to assume the fourth; no page says so, and "nobody said" is not a
fact about a character."""
JACKDAW = NPCEntry("Jackdaw", species=sp.HUMAN)
JEEVES = NPCEntry("Jeeves", species=sp.HUMAN)
JEMJANG = NPCEntry("Jemjang", species=sp.HUMAN, status="Dead")
JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS = NPCEntry("Jezabelle, Everfest Healer and Allsorts", species=sp.HUMAN)
JIGSAW = NPCEntry("Jigsaw", species=sp.HUMAN, status="Alive")
JING = NPCEntry("Jing", species=sp.HUMAN, status="Alive")
JUICE = NPCEntry("Juice", species=sp.HUMAN)
JULES_TEKLOVOSSEN = NPCEntry("Jules Teklovossen", species=sp.HUMAN, status="Alive")
KALSHARPE = NPCEntry("Kalsharpe", species=sp.HUMAN)
KARALYN = NPCEntry("Karalyn")
"""Was the last ``npcs.csv`` row with no constant at all — reachable from no
declaration, so nothing could write to it. Found 2026-08-20 by the stage 4 review
and closed by registering ``flavour/compendium-of-rathe.md``, which is the only
page that names her: "Two worlds, one story, written in the alphabets of Aether
and Aesir." — Aetherscribe Karalyn (PEN113). ``Aetherscribe`` is a profession and
waits for R9; her species is unattested, and the retired column said ``Unknown``,
which is not a fact about a character."""
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
KYLORIA = NPCEntry("Kyloria", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
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
LORD_WIZARD_AKIHIKO = NPCEntry("Lord Wizard Akihiko", species=sp.HUMAN, status="Deceased")
"""Kano's mentor, and the Lord Wizard who oversees the Trial of Embers.

Named on three arcane-rising pages and given a row only now, on the same finding
that turned up ``the-phoenix-and-the-dragon.md``: ``playing-with-fire.md`` runs the
trial through him, ``smoke-and-mirrors.md`` has him attack Kano and die of the
parasite that was already killing him, and ``from-the-ashes.md`` makes his corpse
the evidence. **None of the three is declared**, so nothing reaches this constant
yet and no declaration writes it.

Named with the title to match ``LORD_WIZARD_CHIYO`` rather than fixing one of a
pair; both are D5 renames and go to stage 7 together.

``Deceased`` where Chiyo beside him reads ``Dead`` (the user's call, 2026-08-21).
The two words mean the same thing and the column holds both, along with ``Gone``,
``Just a head`` and ``Spider-bot assistant to Jules Teklovossen`` — free text doing
the job of prose. Stage 11."""
LORD_WIZARD_CHIYO = NPCEntry("Lord Wizard Chiyo", status="Dead")
LUCA_ARENA_CICERONE = NPCEntry("Luca, Arena Cicerone", species=sp.HUMAN, status="Alive")
LUCILLA_THE_SETTING_SUN = NPCEntry("Lucilla the Setting Sun")
MABON = NPCEntry("Mabon", species=sp.HUMAN)
MADAM_ROUGE = NPCEntry("Madam Rouge", species=sp.HUMAN, status="Dead")
MAD_SIV = NPCEntry("Mad Siv")
MAELA_ISULFV = NPCEntry("Maela Isulfv", short_names=("Isulvf",))
"""``Isulvf`` and ``Isulfv`` are the same seer (the user's call, 2026-08-21) — the
spellings are letter-transpositions and both are Aria seers.
``main-story/everfest/a-grand-adventure.md`` calls him "Isulvf, the oldest and
wisest seer in the whole village" of Volthaven; ``flavour/omens-of-the-third-age.md``
and the Omens tiles page credit quotes to "Maela Isulfv".

Recorded as a ``short-name`` rather than fixed, because deciding which spelling is
the typo is a rename and renames are stage 7. Both forms reach one tooltip
meanwhile, which is the part that would otherwise be lost. Without this, registering
a-grand-adventure.md would have minted a second row for one person — the near-
duplicate hazard the registration rules exist to catch."""
MARA = NPCEntry("Māra")
"""One of Lexi's troupe in ``main-story/everfest/a-grand-adventure.md`` — "the
aspiring magician Māra - who has a flair for the dramatic". No species: the page
never says, and the macron is part of the name as printed."""

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
NASRETH = NPCEntry("Nasreth", species=sp.EMBRA, epithets=("the Soul Harrower",))
NEKRIA = NPCEntry("Nekria", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
NESTUS = NPCEntry("Nestus")
NING_KOTORI_MOONSEEKER = NPCEntry("Ning, Kotori Moonseeker", species=sp.HUMAN)
NJERI = NPCEntry("Njeri", species=sp.HUMAN)
NOCETES = NPCEntry("Nocetes", epithets=("God of death",))
"""A Dhani deity — see ``ABSOLON`` on why gods are a group and not a species.

**The epithet is on the user's authority, not a page** (2026-08-21), kept as
``character-groups.md`` wrote it. The pages all use a different construction:
"thralls of Nocetes, death god of the Dhani" (``world-of-rathe/high-seas.md:143``)
and "the Dhani death god Nocetes"
(``main-story/high-seas/captain-bones-and-the-city-of-gold.md:67``). Unlike
Absolon, Nocetes *is* reachable without the new module — captain-bones names the
god outright rather than a ship.

``captain-bones...:205`` writes "This was Nocetes' gift, and her curse", the only
line that genders the deity."""
ONE_EYE = NPCEntry("One Eye", species=sp.HUMAN, status="Alive")
OTMAR = NPCEntry("Otmar", species=sp.HUMAN)
OUVIA = NPCEntry("Ouvia", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
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
SANI = NPCEntry("Sani")
"""Dromai's mother, "Sani of the Sandfolk"
(``main-story/uprising/dragons-of-empire.md``), murdered before Dromai could walk
and appearing in the story only as a mirage the enemy illusionists summon. No
species: half of Dromai's parentage is the point of the story and neither half is
given as a species anywhere."""

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
SILVERHAIR = NPCEntry("Silverhair")
"""The rebel leader Fai carries off the hill in
``main-story/uprising/dragons-of-empire.md``. **A name, on the user's call
(2026-08-21)** — the page introduces her as "a silver-haired woman" and later "the
silver-haired rebel", but uses the bare word as a name in between: "Silverhair barks
orders", "she whips Silverhair off her feet". No other page in the repository names
her, so nothing corroborates the reading either way."""

SKYNDA_FEYSCOUT = NPCEntry("Skynda Feyscout")
SLAPSTICK_SAL = NPCEntry("Slapstick Sal")
SLINGER = NPCEntry("Slinger", species=sp.HUMAN, status="Alive")
SOL = NPCEntry("Sol", species=sp.AESIR, epithets=("Aesir of Light",))
"""The epithet is never written "Sol, Aesir of Light" — both attestations use it
as a standalone title for him: "subservience to the Aesir of Light"
(``summaries/war-of-the-monarch-pt-1.md:5``) and "the power perhaps to consume
even the Aesir of Light" (``main-story/usurp-the-shadow-throne/letters-from-the-beyond.md:79``)."""
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
THAWNE = NPCEntry("Thawne", species=sp.DWARF)
"""One of Lexi's troupe in ``main-story/everfest/a-grand-adventure.md`` — "the gruff
dwarven blacksmith Thawne"; the species is stated in that line. Blacksmith is a
profession and waits for R9."""

THEBASTO_MAGISTER_OF_DEFENSE = NPCEntry("Thebasto, Magister of Defense", species=sp.HUMAN, status="Alive")
THEMAI = NPCEntry("Themai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
THEMIS_KEEPER_OF_THE_SCALES = NPCEntry(
    "Themis, Keeper of the Scales",
    species=sp.HERALD,
    epithets=("Keeper of the Scales", "Archangel of Judgment", "Archangel of Justice"),
)
"""Three epithets for two titles, and that is deliberate (the user's call,
2026-08-20). ``Archangel of Judgment`` is the form character-groups.md and the
card text carry; ``compendium-of-rathe.md:34`` credits the same character as
"Themis, Archangel of Justice". Both are attested in those exact words, so both
are match strings rather than one being corrected into the other."""
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
TOMELTAI = NPCEntry("Tomeltai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
TORVAI = NPCEntry("Torvai")
"""Dromai's father, "Torvai the Dracai"
(``main-story/uprising/dragons-of-empire.md``), and by Dromai's account "betrayed by
love". Also named on ``fires-of-rebellion.md`` and ``the-phoenix-and-the-dragon.md``,
neither of which is declared, so this row starts with one link of a possible three."""

TOROJA_OF_ISHIGAKI = NPCEntry("Toroja of Ishigaki", species=sp.HUMAN, status="Dead")
URSUR = NPCEntry("Ursur", species=sp.EMBRA, epithets=("the Soul Reaper",))
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
VYNSERAKAI = NPCEntry("Vynserakai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
WAILER = NPCEntry("Wailer", species=sp.ZOMBIE, status="Dead")
WENDRYN = NPCEntry("Wendryn", species=sp.HUMAN, status="Deceased")
WHEELER = NPCEntry("Wheeler", species=sp.HUMAN, status="Alive")
WHISPERS_OF_XERYS = NPCEntry("Whispers of Xerys")
WHITETAIL = NPCEntry("Whitetail", species=sp.HUMAN, status="Alive")
WIDOW_JOHANA = NPCEntry("Widow Johana", species=sp.HUMAN)
WYNVARIN = NPCEntry("Wynvarin", species=sp.HUMAN)
XATHARI = NPCEntry(
    "Xathari",
    status="Deceased",
    epithets=("the Dracai spymaster", "Spymaster Xathari"),
)
"""The Dracai spymaster who found Dromai and raised her to the court, whose
"firesight allows him to read the flames like a map".

**Two epithets, from three forms** (the user's call, 2026-08-21). The pages write
the title three ways and only two of them are worth a row:

- ``the Dracai spymaster`` — ``dragons-of-empire.md:37``, "wonders the Dracai
  spymaster". Kept first: it is the fullest form and the one that says *whose*
  spymaster he is.
- ``Spymaster Xathari`` — ``tidings-in-the-light.md:85``, "she copied the words of
  Spymaster Xathari until his untimely demise". Title-plus-name, the construction
  ``Chancellor Hypatia`` and ``Lord Wizard Chiyo`` are filed under. That page has
  no declaration, so this form is attested and unlinked.
- ``The spymaster`` bare — ``betrayal.md:43,51`` and
  ``the-phoenix-and-the-dragon.md:3,19``. **No row**: on its own it is a common
  noun that would match any spymaster in the archive.

**Named on six pages**, not the five this said until 2026-08-21. The list left out
``main-story/uprising/the-phoenix-and-the-dragon.md``, which names him eight times
and is the page he dies on — his largest appearance by some distance, and the only
one that gives him dialogue. It has no declaration at all.

The six, and where each stands: ``dragons-of-empire.md`` and ``betrayal.md``
declared him from the day the row was minted, not the one the old wording claimed;
``ember-in-the-ash.md`` and ``emperor-the-one-emperor.md`` both carried a
``# TODO: needs catalogue constant — Spymaster Xathari`` waiting for exactly this
row and now name him; ``the-phoenix-and-the-dragon.md`` and
``tidings-in-the-light.md`` have no declaration.

So four of six connect, and the two that do not are undeclared pages rather than
declarations missing a name. The catalogue covers the pages that have declarations,
not the pages that exist.

``Deceased`` as of 2026-08-21 (the user's call), where the row read ``Unknown``
before. ``the-phoenix-and-the-dragon.md:57`` has Dromai's dragon swallow him whole
on the page, and ``tidings-in-the-light.md:85`` writes "until his untimely demise".
Registering the page he dies on is what made the status answerable."""

XAINE_RUNESCRIBE = NPCEntry("Xaine, Runescribe", species=sp.HUMAN, status="Dead")
XILIN = NPCEntry("Xilin", species=sp.HUMAN, status="Dead")
XIN = NPCEntry("Xin", species=sp.HUMAN)
YARIN = NPCEntry("Yarin", species=sp.HUMAN)
YUNKAI = NPCEntry("Yunkai", species=sp.HUMAN)
YENDURAI = NPCEntry("Yendurai", species=sp.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
YVOR = NPCEntry(
    "Yvor",
    species=sp.ANCIENT,
    status="Deceased",
    epithets=(
        "Ancient of Lightning",
        "Ancient of Lightning and Ice",
        "Ancient of Thunder and Ice",
    ),
)
"""**Three** epithets, all attested, the way ``THEMIS_KEEPER_OF_THE_SCALES`` carries
three. ``world-of-rathe/aria.md`` writes "Yvor, Ancient of Lightning" twice (:167,
:175); ``archive/world-of-rathe/aria/the-land-of-legends.md:25`` writes "the Ancient
of Lightning and Ice, Yvor"; and
``main-story/tales-of-aria/wonders-of-the-wayfarer.md:7`` writes "Yvor, the mighty
Ancient of Thunder and Ice", which ``main-story/everfest/a-grand-adventure.md:47``
repeats.

The third was found a step after the first two were agreed, by reading a page being
registered rather than the file being replaced (2026-08-21, the user's call).
``character-groups.md`` carried only ``Ancient of Lightning and Ice`` — the one form
of the three whose sole source is an archive page."""
