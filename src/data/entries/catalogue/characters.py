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
"""A Dhani deity, and **not a kind row** — gods are a role, not a kind of being
(the user's call, 2026-08-21), so both gods reach the generated page through
``grp.DHANI_DEITIES`` instead. The epithet keeps the page's own lower-case "god",
as ``hag of Mojire`` and ``the Shield of Light`` keep theirs.

Reachable only because stage 5 added ``entries/world_of_rathe.py``: he is named as
a god on ``world-of-rathe/high-seas.md:125`` alone. The eight mentions on the
already-declared ``captain-bones-and-the-city-of-gold.md`` are all the Kuraghan
flagship ``Absolon's Dream``, never the god."""


AELIUS = CharacterEntry("Aelius", kinds=kind.HUMAN, status="Dead")
AESIR_OF_FLAMES = CharacterEntry("Aesir of Flames", kinds=kind.AESIR)
AIOS = CharacterEntry("Aios", kinds=kind.HUMAN, status="Alive")
AKUO = CharacterEntry("Akuo", kinds=kind.HUMAN)
AUDACITY = CharacterEntry("λud@c!ty")
"""The Foundry's operator. metrix.md:201 says nobody knows "their real name,
face, or if they're a single person or a collective of dissidents operating
under a shared alias" — hence no kind and no status."""
ALIF = CharacterEntry("Alif", kinds=kind.HUMAN, status="Alive")
ALOSYN = CharacterEntry("Alosyn", kinds=kind.HUMAN)
AMIR = CharacterEntry("Amir", kinds=kind.HUMAN)
AMIRA_SURANA = CharacterEntry("Amira Surana")
ANARCH_ZEIR = CharacterEntry(
    "Anarch Zeir",
    kinds=kind.HUMAN,
    epithets=("First Anarch of L'Apocalypta",),
)
"""``Anarch`` is already in the display name; the epithet is the full title, from
``flavour/compendium-of-rathe.md:76`` — "Zeir, First Anarch of L'Apocalypta"
(PEN277). He is the sole member of ``grp.L_APOCALYPTA``'s roster."""
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
BARON_THE_BUTCHER = CharacterEntry("Baron the Butcher", kinds=kind.HUMAN, status="Dead")
BARTON = CharacterEntry("Barton", kinds=kind.HUMAN)
BARTRAND_THE_BLOODY = CharacterEntry("Bartrand the Bloody", kinds=kind.HUMAN)
BARUS_BOLDSTRIDE = CharacterEntry("Barus Boldstride", kinds=kind.HUMAN)
AZVOLAI = CharacterEntry("Azvolai", kinds=kind.DRAGON)
"""One of the eleven dragons stage 5 gave a row (2026-08-21). They were the bulk
of the fourteen names in ``src/data/md/character-groups.md`` that had no database
row of any kind, while ``kind.DRAGON`` held only Miragai.

The hand-written file also carried ``Pronounciation`` and ``Phonetic`` columns for
each. Those are **dropped** rather than migrated (the user's call): ``npcs`` is the
one registry with no prose column, and the identical table already lives at
``archive/world-of-rathe/volcor/welcome-to-volcor.md:19-35`` — verified cell for
cell, "Pronounciation" typo included, only the male-table row order differing."""
BATBITER = CharacterEntry("Batbiter")
BAZZ = CharacterEntry("Bazz", kinds=kind.HUMAN, status="Dead")
BEEZY_THE_BRASH = CharacterEntry("Beezy the Brash", kinds=kind.HUMAN, status="Dead")
BELLONA_THE_WARTUNE_HERALD = CharacterEntry(
    "Bellona, the Wartune Herald",
    kinds=kind.HERALD,
    epithets=("the Wartune Herald", "Archangel of War"),
)
BISKI = CharacterEntry("Biski", kinds=kind.DOG)
BLASMOPHET = CharacterEntry("Blasmophet", kinds=kind.EMBRA, epithets=("the Soul Harvester",))
BLIND_BOGGY = CharacterEntry("Blind Boggy")
BLOODWORTH_GOLDMANE = CharacterEntry("Bloodworth Goldmane")
BOJANI = CharacterEntry("Bojani", kinds=kind.HUMAN, status="Dead")
BOO = CharacterEntry("Boo")
BRAUMEISTER_BALEN = CharacterEntry("Braumeister Balen", kinds=kind.HUMAN, status="Alive")
BREWMEISTER_MARV = CharacterEntry("Brewmeister Marv", kinds=kind.HUMAN)
BRUTUS_SUMMA_RUDIS = CharacterEntry("Brutus, Summa Rudis")
BUTCHER_JEK = CharacterEntry("Butcher Jek", kinds=kind.HUMAN)
BUTTONS = CharacterEntry("Buttons", kinds=kind.HUMAN, status="Alive")
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
CAYLIN = CharacterEntry("Caylin", kinds=kind.HUMAN, status="Dead")
CAYLIN_S_MOTHER = CharacterEntry("Caylin's mother", kinds=kind.HUMAN, status="Dead")
CHANCELLOR_HELENA_PRIMAVERA = CharacterEntry("Chancellor Helena Primavera", kinds=kind.HUMAN)
CHANCELLOR_HYPATIA = CharacterEntry("Chancellor Hypatia", kinds=kind.HUMAN)
CHARIS = CharacterEntry("Charis", kinds=kind.HUMAN)
CHARLOTTE = CharacterEntry("Charlotte", kinds=kind.ROBOT)
"""A robot, not a dog (the user's call, 2026-08-25, read off the card art).
metrix.md:91 calls her "his trusty (and rusty) pet junkyard dogg" — *rusty* is
the tell, and `Dogg` was a kind of one member that recorded what she looks like
rather than what she is."""
CHIARA_SUNCREST = CharacterEntry("Chiara Suncrest")
CHOWDER = CharacterEntry("Chowder", kinds=kind.ZOMBIE)
CHUM = CharacterEntry("Chum", kinds=kind.ZOMBIE, status="Dead")
CIRRUS = CharacterEntry("Cirrus", kinds=kind.HUMAN)
COBBS = CharacterEntry("Cobbs", kinds=kind.HUMAN)
COUNTESS_CAMILLA = CharacterEntry("Countess Camilla")
COX = CharacterEntry("Cox")
CUTTY = CharacterEntry("Cutty", kinds=kind.ZOMBIE, status="Dead")
DANU_ASHENGUARD = CharacterEntry("Danu Ashenguard", kinds=kind.HUMAN)
DAN_LU_KOTORI_GALEWARDEN = CharacterEntry("Dan Lu, Kotori Galewarden", kinds=kind.HUMAN)
DARIAN = CharacterEntry("Darian", kinds=kind.HUMAN, status="Dead")
DARIUS = CharacterEntry("Darius", kinds=kind.HUMAN)
DARYAS_NIMBUS = CharacterEntry("Daryas Nimbus")
CROMAI = CharacterEntry("Cromai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
DAVNIR = CharacterEntry(
    "Davnir",
    kinds=kind.ANCIENT,
    status="Dead",
    epithets=("Ancient of Earth", "Ancient of Earth and Lightning"),
)
"""Two epithets, both attested, kept the way ``THEMIS_KEEPER_OF_THE_SCALES`` keeps
three (the user's call, 2026-08-21). ``world-of-rathe/aria.md:167`` lists him
alongside his siblings as "Davnir, Ancient of Earth"; ``main-story/tales-of-aria/
amongst-the-brambles.md:9`` writes "Davnir, Ancient of Earth and Lightning". The
hand-written character-groups.md carried only the second, so the form aria.md uses
matched no tooltip."""
DAXIUS = CharacterEntry("Daxius", kinds=kind.HUMAN, status="Dead")
DEMETRIOS = CharacterEntry("Demetrios", kinds=kind.BRUTE)
DERVIN_MASTER_OF_BEASTS = CharacterEntry("Dervin, Master of Beasts", kinds=kind.HUMAN, epithets=("Master of Beasts",))
DHERIC = CharacterEntry("Dheric", kinds=kind.HUMAN, status="Dead")
DOMINIA = CharacterEntry("Dominia", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
DRACONA_OPTIMAI = CharacterEntry("Dracona Optimai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
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
EIRINA = CharacterEntry("Eirina", kinds=kind.HUMAN, status="Dead")
ELDON_LOST_KNIGHT = CharacterEntry("Eldon, Lost Knight", kinds=kind.HUMAN, epithets=("Lost Knight",))
ELIAS_EDGECOMBE = CharacterEntry("Elias Edgecombe", kinds=kind.HUMAN)
EMEVIERE = CharacterEntry("Emeviere")
ENFORCER_EESHA = CharacterEntry("Enforcer Eesha", kinds=kind.HUMAN)
ERSEBET = CharacterEntry("Ersebet")
EUN = CharacterEntry("Eun", kinds=kind.HUMAN, status="Dead")
EXECUTIVE_SMYTE = CharacterEntry("Executive Smyte", kinds=kind.HUMAN)
FARIN_THE_PORTER = CharacterEntry("Farin the Porter", kinds=kind.HUMAN)
FARRIS = CharacterEntry("Farris", kinds=kind.HUMAN)
FAYYAD = CharacterEntry("Fayyad", kinds=kind.HUMAN, status="Alive")
FELIX = CharacterEntry("Felix", kinds=kind.HUMAN)
FERAL = CharacterEntry("Feral", kinds=kind.HUMAN)
FIGHTMASTER_KOX = CharacterEntry("Fightmaster Kox", kinds=kind.GOBLIN)
FIGHTMASTER_RUSTY = CharacterEntry("Fightmaster Rusty", kinds=kind.DWARF)
FLANNIGAN = CharacterEntry("Flannigan", kinds=kind.HUMAN)
FOREMAN_PEBB = CharacterEntry("Foreman Pebb")
FREYA_ELDINGSTURM = CharacterEntry("Freya Eldingsturm")
FUGGER_GRIMES = CharacterEntry("Fugger Grimes")
FYANNA_REDMOOR_BOLTYN_S_COUSIN = CharacterEntry("Fyanna Redmoor, Boltyn's cousin", kinds=kind.HUMAN)
GALAPHOR = CharacterEntry("Galaphor", kinds=kind.HUMAN, status="Dead")
FYENDAL = CharacterEntry("Fyendal")
"""Named only by a card title — "Fyendal's Fighting Spirit" (UPR194) — whose
flavour line, "The old ways are not forgotten.", does not mention him. Included on
the user's call (2026-08-21), under the same reading that lets the twelve dragons
in from ``Invoke <name>`` titles.

No kind and no status: nothing on the page says anything about him. The only
other trace of the name in the registry is the equipment ``Fyendal's Spring
Tunic``, which this page does not name."""

GALCIA = CharacterEntry(
    "Galcia",
    kinds=kind.ANCIENT,
    status="Dead",
    epithets=("Ancient of Ice",),
)
"""The one Ancient whose epithet the pages and character-groups.md agree on."""
GAWAIN = CharacterEntry("Gawain", kinds=kind.HUMAN)
GENERAL_CHUL = CharacterEntry("General Chul", kinds=kind.HUMAN)
GENERAL_EKODA = CharacterEntry("General Ekoda", kinds=kind.HUMAN)
GENERAL_NAKAMI = CharacterEntry("General Nakami", kinds=kind.HUMAN)
GENERAL_RIKU = CharacterEntry("General Riku", kinds=kind.HUMAN, status="Dead")
GENERAL_YAMATOKA = CharacterEntry("General Yamatoka", kinds=kind.HUMAN, status="Alive")
GIANTSLAYER_CRIX = CharacterEntry("Giantslayer Crix", kinds=kind.HUMAN)
GOVERNOR_PRACTISS = CharacterEntry("Governor Practiss", kinds=kind.HUMAN)
GAVIN = CharacterEntry("Gavin")
"""Named once, at krest-mortimer.md:39 — he owes Mortimer a favour. Kind and
status are left to default rather than guessed."""
GRAHAM_THE_GALLANT = CharacterEntry("Graham the Gallant", kinds=kind.HUMAN)
GRANDMASTER_LI = CharacterEntry("Grandmaster Li", kinds=kind.HUMAN)
GRAND_MAGISTER_THE_ADAMANT = CharacterEntry("Grand Magister, the Adamant", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_BELOVED = CharacterEntry("Grand Magister, the Beloved", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_DEVOUT = CharacterEntry("Grand Magister, the Devout", kinds=kind.HUMAN, status="Assumed Dead")
GRAND_MAGISTER_THE_RADIANT = CharacterEntry("Grand Magister, the Radiant", kinds=kind.HUMAN)
GRAND_MAGISTER_THE_STEADFAST = CharacterEntry("Grand Magister, The Steadfast", kinds=kind.HUMAN)
"""Five rows for one office, and the case drift on ``The Steadfast`` makes it six
spellings' worth of hash. Adamant and Beloved had npcs.csv rows and no constant at
all until stage 4 needed every kind declared somewhere. Stage 7 collapses the
five into one title with five holders; until then they are five characters."""
GREENBIRD = CharacterEntry("Greenbird", kinds=kind.HUMAN)
GROTA = CharacterEntry("Grota", kinds=kind.HUMAN, status="Alive")
GUDO_MISTWARD_PILGRIM = CharacterEntry("Gudo, Mistward Pilgrim", kinds=kind.HUMAN)
HANK = CharacterEntry("Hank", kinds=kind.HUMAN, status="Alive")
HARLAND = CharacterEntry("Harland")
HAROLD_HONEYSETT = CharacterEntry("Harold Honeysett", kinds=kind.HUMAN)
HELX = CharacterEntry("Helx")
HIGHTARN = CharacterEntry("Hightarn", status="Dead")
HILDEGUN = CharacterEntry("Hildegun", kinds=kind.HUMAN)
HIREI = CharacterEntry("Hirei", kinds=kind.HUMAN)
HISATO = CharacterEntry("Hisato", kinds=kind.HUMAN)
HOG = CharacterEntry("Hog", kinds=kind.HUMAN)
HUXLEY = CharacterEntry("Huxley", kinds=kind.HUMAN)
HYRINTH = CharacterEntry("Hyrinth")
INQUISITOR_ARICIA = CharacterEntry("Inquisitor Aricia")
IRUNAMEABH = CharacterEntry("Írunaméabh")
ISEN = CharacterEntry("Isen", kinds=kind.ANCIENT, epithets=("Ancient of Earth and Ice",))
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
JACKDAW = CharacterEntry("Jackdaw", kinds=kind.HUMAN)
JEEVES = CharacterEntry("Jeeves", kinds=kind.HUMAN)
JEMJANG = CharacterEntry("Jemjang", kinds=kind.HUMAN, status="Dead")
JEZABELLE_EVERFEST_HEALER_AND_ALLSORTS = CharacterEntry("Jezabelle, Everfest Healer and Allsorts", kinds=kind.HUMAN)
JIGSAW = CharacterEntry("Jigsaw", kinds=kind.HUMAN, status="Alive")
JING = CharacterEntry("Jing", kinds=kind.HUMAN, status="Alive")
JUICE = CharacterEntry("Juice", kinds=kind.HUMAN)
JULES_TEKLOVOSSEN = CharacterEntry(
    "Jules Teklovossen",
    kinds=kind.HUMAN,
    status="Alive",
    hero_slug="teklovossen",
    short_names=("Teklovossen",),
)
"""One person, not two. The card name is the short one and the lore name is the
full one, so the hero row and the prose row were two `characters` rows for a
man who is both. `hero_slug` folds them onto one `character_id`; `Teklovossen`
becomes the short-name it always was."""
KALSHARPE = CharacterEntry("Kalsharpe", kinds=kind.HUMAN)
KARALYN = CharacterEntry("Karalyn")
"""Was the last ``npcs.csv`` row with no constant at all — reachable from no
declaration, so nothing could write to it. Found 2026-08-20 by the stage 4 review
and closed by registering ``flavour/compendium-of-rathe.md``, which is the only
page that names her: "Two worlds, one story, written in the alphabets of Aether
and Aesir." — Aetherscribe Karalyn (PEN113). ``Aetherscribe`` is a profession and
waits for R9; her kind is unattested, and the retired column said ``Unknown``,
which is not a fact about a character."""
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
KYLE = CharacterEntry("Kyle", kinds=kind.HUMAN)
KYLORIA = CharacterEntry("Kyloria", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
LADY_BARTHIMONT = CharacterEntry(
    "Lady Barthimont",
    kinds=kind.HUMAN,
    status="Dead",
    short_names=("Barthimont",),
)
LADY_VERA_SUTCLIFFE = CharacterEntry("Lady Vera Sutcliffe", kinds=kind.HUMAN)
LENA_BELLE = CharacterEntry("Lena Belle", kinds=kind.HUMAN)
LEONA = CharacterEntry("Leona")
LIEUTENANT_LI = CharacterEntry("Lieutenant Li", kinds=kind.HUMAN)
LIEUTENANT_TIMAEUS = CharacterEntry("Lieutenant Timaeus", kinds=kind.HUMAN)
LIEUTENANT_YAMADA = CharacterEntry("Lieutenant Yamada", kinds=kind.HUMAN, status="Dead")
LILJA = CharacterEntry("Lilja", kinds=kind.HUMAN)
LIMPIT = CharacterEntry("Limpit", kinds=kind.ZOMBIE, status="Dead")
LINNEA_MISTRESS_OF_MALADY = CharacterEntry(
    "Linnea, Mistress of Malady", kinds=kind.HUMAN, epithets=("Mistress of Malady",)
)
LISHU_CRIMSON_HAZE_VIGILANTE = CharacterEntry("Lishu, Crimson Haze Vigilante", kinds=kind.HUMAN)
LORD_MERCHANT_SAVAI = CharacterEntry("Lord Merchant Savai", kinds=kind.HUMAN, status="Dead")
LORD_SABUTO = CharacterEntry("Lord Sabuto", kinds=kind.HUMAN)
LORD_SUTCLIFFE = CharacterEntry("Lord Sutcliffe", kinds=kind.HUMAN, status="Unknown")
LORD_WIZARD_AKIHIKO = CharacterEntry("Lord Wizard Akihiko", kinds=kind.HUMAN, status="Dead")
"""Kano's mentor, and the Lord Wizard who oversees the Trial of Embers.

Named on three arcane-rising pages and given a row only now, on the same finding
that turned up ``the-phoenix-and-the-dragon.md``: ``playing-with-fire.md`` runs the
trial through him, ``smoke-and-mirrors.md`` has him attack Kano and die of the
parasite that was already killing him, and ``from-the-ashes.md`` makes his corpse
the evidence. **None of the three is declared**, so nothing reaches this constant
yet and no declaration writes it.

Named with the title to match ``LORD_WIZARD_CHIYO`` rather than fixing one of a
pair; both are D5 renames and go to stage 7 together.

Read ``Deceased`` here until migration 12, where ``Chiyo`` beside him already read
``Dead`` — the two words meant the same thing and the column held both, along
with ``Gone``, ``Just a head`` and ``Spider-bot assistant to Jules
Teklovossen``: free text doing the job of prose. ``status`` is now a closed
five-value vocabulary (``Unknown``, ``Alive``, ``Dead``, ``Assumed Dead``,
``Missing``); the two sentence-shaped values folded to ``Unknown`` for now —
the sentence belongs in the ``summary`` column a later stage adds."""
LORD_WIZARD_CHIYO = CharacterEntry("Lord Wizard Chiyo", status="Dead")
LUCA_ARENA_CICERONE = CharacterEntry("Luca, Arena Cicerone", kinds=kind.HUMAN, status="Alive")
LUCILLA_THE_SETTING_SUN = CharacterEntry("Lucilla the Setting Sun")
MABON = CharacterEntry("Mabon", kinds=kind.HUMAN)
MADAM_ROUGE = CharacterEntry("Madam Rouge", kinds=kind.HUMAN, status="Dead")
MAD_SIV = CharacterEntry("Mad Siv")
MAELA_ISULFV = CharacterEntry("Maela Isulfv", short_names=("Isulvf",))
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
MARA = CharacterEntry("Māra")
"""One of Lexi's troupe in ``main-story/everfest/a-grand-adventure.md`` — "the
aspiring magician Māra - who has a flair for the dramatic". No kind: the page
never says, and the macron is part of the name as printed."""

MAELA_FAIRMIND = CharacterEntry("Maela Fairmind")
MAELA_ONE_EYE = CharacterEntry("Maela One-eye")
MAELA_SHARENA = CharacterEntry("Maela Sharena")
MAGISTRATE_CHEN = CharacterEntry("Magistrate Chen", kinds=kind.HUMAN)
MAGNUS_THE_VIGILANT = CharacterEntry("Magnus the Vigilant", kinds=kind.HUMAN)
MAGPIE = CharacterEntry("Magpie", kinds=kind.HUMAN, status="Alive")
MARBLES = CharacterEntry("Marbles", kinds=kind.MEEP)
MARCUS = CharacterEntry("Marcus", kinds=kind.HUMAN)
MARCUS_MAULER_MONROE = CharacterEntry("Marcus 'Mauler' Monroe", kinds=kind.HUMAN, status="Alive")
MASTER_MORITA_ART_OF_THE_HAND = CharacterEntry("Master Morita, Art of the Hand", kinds=kind.HUMAN, status="Alive")
MASTER_SAORI = CharacterEntry("Master Saori", kinds=kind.HUMAN, status="Alive")
MASTER_TAKUMI = CharacterEntry("Master Takumi", kinds=kind.HUMAN, status="Alive")
MASTER_UDO = CharacterEntry("Master Udo", kinds=kind.HUMAN)
MAXWELL = CharacterEntry("Maxwell", kinds=kind.HUMAN)
MELDRICK_SUDDS = CharacterEntry("Meldrick Sudds", kinds=kind.HUMAN, status="Alive")
MERLEN_RIVERA = CharacterEntry("Merlen Rivera", kinds=kind.HUMAN)
METIS_ARCHANGEL_OF_TENACITY = CharacterEntry(
    "Metis, Archangel of Tenacity",
    kinds=kind.HERALD,
    epithets=("Archangel of Tenacity",),
)
MIKAEL = CharacterEntry("Mikael", kinds=kind.HUMAN)
MIKU = CharacterEntry("Miku", kinds=kind.HUMAN)
MINERVA_THEMIS = CharacterEntry(
    "Minerva Themis",
    kinds=kind.HUMAN,
    status="Dead",
    other_characters_story_key="other-characters/minerva-themis.md",
    short_names=("Minerva",),
)
MIN_OF_THE_FOREST_OF_FLAMES = CharacterEntry("Min of the Forest of Flames", kinds=kind.HUMAN)
MIRAGAI = CharacterEntry("Miragai", kinds=kind.DRAGON)
MISS_Q = CharacterEntry("Miss Q")
MOLLY_THE_MOP = CharacterEntry("Molly the Mop", kinds=kind.HUMAN, status="Alive")
MOLOCA = CharacterEntry("Moloca")
MORAY = CharacterEntry("Moray", kinds=kind.HUMAN)
MORAY_LE_FAY = CharacterEntry("Moray Le Fay", kinds=kind.ZOMBIE)
MORGAN = CharacterEntry("Morgan", kinds=kind.HUMAN)
MORGA_GRINNING_BOAR_CANTINA_BARMAID = CharacterEntry("Morga, Grinning Boar Cantina Barmaid", kinds=kind.HUMAN)
"""No epithet. The glued tail is a place plus a job — the ``Grinning Boar Cantina``
locations row and the profession ``Barmaid`` — so both halves wait for R9 rather
than being read as a style she is known by."""
MUTINOUS_MAGGIE = CharacterEntry("Mutinous Maggie", kinds=kind.HUMAN)
NAILBIT_NARI = CharacterEntry("Nailbit Nari", kinds=kind.HUMAN)
NARAKIR = CharacterEntry("Narakir", kinds=kind.WELKIN)
NASRETH = CharacterEntry("Nasreth", kinds=kind.EMBRA, epithets=("the Soul Harrower",))
NEKRIA = CharacterEntry("Nekria", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
NESTUS = CharacterEntry("Nestus")
NING_KOTORI_MOONSEEKER = CharacterEntry("Ning, Kotori Moonseeker", kinds=kind.HUMAN)
NJERI = CharacterEntry("Njeri", kinds=kind.HUMAN)
NOCETES = CharacterEntry("Nocetes", epithets=("God of death",))
"""A Dhani deity — see ``ABSOLON`` on why gods are a group and not a kind.

**The epithet is on the user's authority, not a page** (2026-08-21), kept as
``character-groups.md`` wrote it. The pages all use a different construction:
"thralls of Nocetes, death god of the Dhani" (``world-of-rathe/high-seas.md:143``)
and "the Dhani death god Nocetes"
(``main-story/high-seas/captain-bones-and-the-city-of-gold.md:67``). Unlike
Absolon, Nocetes *is* reachable without the new module — captain-bones names the
god outright rather than a ship.

``captain-bones...:205`` writes "This was Nocetes' gift, and her curse", the only
line that genders the deity."""
ONE_EYE = CharacterEntry("One Eye", kinds=kind.HUMAN, status="Alive")
OTMAR = CharacterEntry("Otmar", kinds=kind.HUMAN)
OUVIA = CharacterEntry("Ouvia", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
OVERSEER_CRICHTON = CharacterEntry("Overseer Crichton", kinds=kind.HUMAN, status="Dead")
OZRIM = CharacterEntry("Ozrim", kinds=kind.ROSETTA)
PALLAS = CharacterEntry("Pallas", kinds=kind.HUMAN)
PEARL_SANDHRI = CharacterEntry("Pearl Sandhri", kinds=kind.HUMAN, status="Alive")
PELORUS = CharacterEntry("Pelorus", kinds=kind.HUMAN, status="Alive")
PINWHEEL = CharacterEntry("Pinwheel", kinds=kind.HUMAN, status="Dead")
POLLY_CRANKA = CharacterEntry("Polly Cranka", kinds=kind.PARROT, status="Alive")
PROFESSOR_MIN = CharacterEntry("Professor Min", kinds=kind.HUMAN)
PROSPECTOR_COGMIRE = CharacterEntry("Prospector Cogmire", kinds=kind.HUMAN)
QUARREL = CharacterEntry("Quarrel", kinds=kind.HUMAN, status="Alive")
QUEEN_OF_CANDLEHOLD = CharacterEntry("Queen of Candlehold", kinds=kind.ROSETTA)
RAGNAR_FROSTHELM = CharacterEntry("Ragnar Frosthelm", kinds=kind.HUMAN)
RAVEN_AESIR_OF_CHAOS = CharacterEntry("Raven, Aesir of Chaos", kinds=kind.AESIR, epithets=("Aesir of Chaos",))
RAY_STINGEYE = CharacterEntry("Ray Stingeye", kinds=kind.HUMAN)
REINA_SPIRIT_CALLER = CharacterEntry("Reina, Spirit Caller", kinds=kind.HUMAN, epithets=("Spirit Caller",))
REX_BIGGUN = CharacterEntry("Rex Biggun", kinds=kind.HUMAN)
REZ = CharacterEntry("Rez", kinds=kind.HUMAN)
REZNYR_ELDINGSTURM = CharacterEntry("Reznyr Eldingsturm")
RICKY_ROYCE = CharacterEntry("Ricky Royce", kinds=kind.HUMAN)
RIGGERMORTIS = CharacterEntry("Riggermortis", kinds=kind.ZOMBIE, status="Dead")
RIGO = CharacterEntry("Rigo", kinds=kind.ROBOT, status="Unknown")
RUPIUS_AURIC_SCROLLMASTER = CharacterEntry("Rupius, Auric Scrollmaster", kinds=kind.HUMAN)
SADA = CharacterEntry("Sada", status="Alive")
SALVADOR_STALLION = CharacterEntry("Salvador Stallion")
SANDY_SHOO = CharacterEntry("Sandy Shoo", kinds=kind.HUMAN)
SANI = CharacterEntry("Sani")
"""Dromai's mother, "Sani of the Sandfolk"
(``main-story/uprising/dragons-of-empire.md``), murdered before Dromai could walk
and appearing in the story only as a mirage the enemy illusionists summon. No
kind: half of Dromai's parentage is the point of the story and neither half is
given as a kind anywhere."""

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
SHELLY = CharacterEntry("Shelly", kinds=kind.ZOMBIE, status="Dead")
SHIO = CharacterEntry("Shio", kinds=kind.HUMAN)
SHIRO = CharacterEntry("Shiro", kinds=kind.HUMAN, status="Alive")
SIDRIZ = CharacterEntry("Sidriz")
SILVERHAIR = CharacterEntry("Silverhair")
"""The rebel leader Fai carries off the hill in
``main-story/uprising/dragons-of-empire.md``. **A name, on the user's call
(2026-08-21)** — the page introduces her as "a silver-haired woman" and later "the
silver-haired rebel", but uses the bare word as a name in between: "Silverhair barks
orders", "she whips Silverhair off her feet". No other page in the repository names
her, so nothing corroborates the reading either way."""

SKYNDA_FEYSCOUT = CharacterEntry("Skynda Feyscout")
SLAPSTICK_SAL = CharacterEntry("Slapstick Sal")
SLINGER = CharacterEntry("Slinger", kinds=kind.HUMAN, status="Alive")
SOL = CharacterEntry("Sol", kinds=kind.AESIR, epithets=("Aesir of Light",))
"""The epithet is never written "Sol, Aesir of Light" — both attestations use it
as a standalone title for him: "subservience to the Aesir of Light"
(``summaries/war-of-the-monarch-pt-1.md:5``) and "the power perhaps to consume
even the Aesir of Light" (``main-story/usurp-the-shadow-throne/letters-from-the-beyond.md:79``)."""
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
TARA_VANGELD = CharacterEntry("Tara VanGeld", kinds=kind.DWARF)
TASHA_OF_DESHVAHAN = CharacterEntry("Tasha of Deshvahan")
TASKMASTER_PYRION = CharacterEntry("Taskmaster Pyrion", kinds=kind.HUMAN)
TEMPLAR_TIMAERUS = CharacterEntry("Templar Timaerus", kinds=kind.HUMAN)
TETZUO = CharacterEntry("Tetzuo", kinds=kind.HUMAN, status="Alive")
THANUELLA = CharacterEntry("Thanuella")
THAWNE = CharacterEntry("Thawne", kinds=kind.DWARF)
"""One of Lexi's troupe in ``main-story/everfest/a-grand-adventure.md`` — "the gruff
dwarven blacksmith Thawne"; the kind is stated in that line. Blacksmith is a
profession and waits for R9."""

THEBASTO_MAGISTER_OF_DEFENSE = CharacterEntry("Thebasto, Magister of Defense", kinds=kind.HUMAN, status="Alive")
THEMAI = CharacterEntry("Themai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
THEMIS_KEEPER_OF_THE_SCALES = CharacterEntry(
    "Themis, Keeper of the Scales",
    kinds=kind.HERALD,
    epithets=("Keeper of the Scales", "Archangel of Judgment", "Archangel of Justice"),
)
"""Three epithets for two titles, and that is deliberate (the user's call,
2026-08-20). ``Archangel of Judgment`` is the form character-groups.md and the
card text carry; ``compendium-of-rathe.md:34`` credits the same character as
"Themis, Archangel of Justice". Both are attested in those exact words, so both
are match strings rather than one being corrected into the other."""
THEODORE_HAMILTON_SCARBOROUGH = CharacterEntry("Theodore Hamilton Scarborough", kinds=kind.HUMAN)
THE_BASTION = CharacterEntry("The Bastion")
THE_HARVESTER = CharacterEntry("The Harvester", kinds=kind.HUMAN)
THE_LIBRARIAN = CharacterEntry(
    "The Librarian",
    other_characters_story_key="other-characters/the-librarian.md",
    short_names=("Librarian",),
    hero_slug="the-librarian",
)
"""X01: The Librarian is also a playable hero — the two rows were the same
person at two points in time (a title relation, deferred to stage 7), and the
identity spine (migration 12) dissolves the split: the hero and the ordinary character now
share one character row, keyed the same way they always hashed to the same
``lore_character_id``. See ``step-into-the-light.md`` in ``main_story.py``."""
THIROUX = CharacterEntry("Thiroux", kinds=kind.HUMAN)
THUK = CharacterEntry("Thuk", kinds=kind.BRUTE)
TIRIL = CharacterEntry("Tiril", kinds=kind.HUMAN)
TOGARK_THE_WRANGLER = CharacterEntry("Togark the Wrangler", kinds=kind.HUMAN, status="Dead")
TOHIRO_ETERNAL_SCRIBE = CharacterEntry("Tohiro, Eternal Scribe", kinds=kind.HUMAN)
TOMASS = CharacterEntry("Tomass", kinds=kind.HUMAN)
TOMELTAI = CharacterEntry("Tomeltai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
TORVAI = CharacterEntry("Torvai")
"""Dromai's father, "Torvai the Dracai"
(``main-story/uprising/dragons-of-empire.md``), and by Dromai's account "betrayed by
love". Also named on ``fires-of-rebellion.md`` and ``the-phoenix-and-the-dragon.md``,
neither of which is declared, so this row starts with one link of a possible three."""

TOROJA_OF_ISHIGAKI = CharacterEntry("Toroja of Ishigaki", kinds=kind.HUMAN, status="Dead")
URSUR = CharacterEntry("Ursur", kinds=kind.EMBRA, epithets=("the Soul Reaper",))
VAIL_THE_VAGRANT = CharacterEntry("Vail the Vagrant", kinds=kind.HUMAN)
VALERIA = CharacterEntry("Valeria", kinds=kind.HUMAN)
VALGARD_HOARFROST = CharacterEntry("Valgard Hoarfrost", kinds=kind.HUMAN)
VANIK_SILVERTOOTH = CharacterEntry("Vanik Silvertooth")
VERA = CharacterEntry("Vera", kinds=kind.HUMAN)
VICTORIA_ARCHANGEL_OF_TRIUMPH = CharacterEntry(
    "Victoria, Archangel of Triumph",
    kinds=kind.HERALD,
    epithets=("Archangel of Triumph",),
)
VIDYA_WILLOWMERE = CharacterEntry("Vidya Willowmere")
VITUS = CharacterEntry("Vitus", kinds=kind.HUMAN)
VYHARA_CLOUDBURST = CharacterEntry("Vyhara Cloudburst")
VYNSERAKAI = CharacterEntry("Vynserakai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
WAILER = CharacterEntry("Wailer", kinds=kind.ZOMBIE, status="Dead")
WENDRYN = CharacterEntry("Wendryn", kinds=kind.HUMAN, status="Dead")
WHEELER = CharacterEntry("Wheeler", kinds=kind.HUMAN, status="Alive")
WHISPERS_OF_XERYS = CharacterEntry("Whispers of Xerys")
WHITETAIL = CharacterEntry("Whitetail", kinds=kind.HUMAN, status="Alive")
WIDOW_JOHANA = CharacterEntry("Widow Johana", kinds=kind.HUMAN)
WYNVARIN = CharacterEntry("Wynvarin", kinds=kind.HUMAN)
XATHARI = CharacterEntry(
    "Xathari",
    status="Dead",
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

XAINE_RUNESCRIBE = CharacterEntry("Xaine, Runescribe", kinds=kind.HUMAN, status="Dead")
XILIN = CharacterEntry("Xilin", kinds=kind.HUMAN, status="Dead")
XIN = CharacterEntry("Xin", kinds=kind.HUMAN)
YARIN = CharacterEntry("Yarin", kinds=kind.HUMAN)
YUNKAI = CharacterEntry("Yunkai", kinds=kind.HUMAN)
YENDURAI = CharacterEntry("Yendurai", kinds=kind.DRAGON)
"""See ``AZVOLAI`` — one of the eleven, and the same note applies."""
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
