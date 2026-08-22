"""Domain API for the fablore database.

Primary entry point is :class:`Database`. Callers use :meth:`Database.upsert_story`
to register a story and declare all its entity links in one call. Supporting
dataclasses (:class:`NPCEntry`, :class:`LocationEntry`, etc.) capture per-entity
metadata with sensible defaults. Hero, weapon, and equipment lookups use
canonical slugs; all other entities are upserted by name.

Discovery helpers (:meth:`Database.print_heroes` etc.) list available slugs so
you never have to guess an identifier.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_heading_ids import (  # noqa: E402
    collect_heading_anchor_ids_from_path,
    format_fragment_suggestion,
)
from registry_ids import (  # noqa: E402
    fauna_id_from_name,
    flora_id,
    food_drink_id,
    group_id as _group_id,
    location_id as _location_id,
    lore_character_id,
    monster_id as _monster_id,
    profession_id as _profession_id,
    region_row_id,
    species_id as _species_id,
    story_id as _story_id,
    title_id as _title_id,
)
from text_utils import normalize_name  # noqa: E402

import db._queries as q  # noqa: E402
from db._connection import open_db  # noqa: E402
from db._seed import seed_from_csvs  # noqa: E402
import db._export as _export  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
DATA = ROOT / "src" / "data"


def _alias_pair(alias: "str | tuple[str, str]") -> tuple[str, str]:
    """Normalise a ``LocationEntry.aliases`` item to ``(alias, era)``.

    A bare string is an alias the lore does not date; the two-tuple form carries
    the era. Accepting both keeps the common case — one other name, no era — from
    paying for the rare one.
    """
    if isinstance(alias, str):
        return alias, ""
    name, era = alias
    return name, era


def _kin_triple(item: "tuple") -> "tuple[NPCEntry | str, str, str]":
    """Normalise an ``NPCEntry.kin`` item to ``(relative, relation, story_key)``.

    An item is a bare ``(relative, relation)`` pair — the common case, and the
    only shape the prompting case ("Their father is Bloodworth Goldmane")
    needs — or a ``(relative, relation, story_key)`` triple when that one fact
    is attested somewhere worth citing. Mirrors ``GroupEntry.members``'s
    optional ``(npc, story_key)`` pair, one field further because a kin fact
    needs a relation as well as a relative.
    """
    if len(item) == 3:
        return item
    relative, relation = item
    return relative, relation, ""


def _species_tuple(species: "SpeciesEntry | tuple[SpeciesEntry, ...] | None") -> "tuple[SpeciesEntry, ...]":
    """Normalise ``NPCEntry.species`` to a tuple.

    One species is the overwhelmingly common case and writes as a bare constant;
    two is rare enough that making every declaration wrap itself in a tuple would
    be a tax on 300 rows to serve one. The same call ``LocationEntry.aliases``
    makes for its ``(alias, era)`` form.
    """
    if species is None:
        return ()
    if isinstance(species, SpeciesEntry):
        return (species,)
    return tuple(species)


def _species_name(conn: sqlite3.Connection, species_id: str) -> str:
    """Return a stored species' display name, or its id if the row has gone."""
    row = conn.execute("SELECT name FROM species WHERE species_id = ?", [species_id]).fetchone()
    return row[0] if row else species_id


def _professions_tuple(
    professions: "ProfessionEntry | tuple[ProfessionEntry, ...] | None",
) -> "tuple[ProfessionEntry, ...]":
    """Normalise ``NPCEntry.professions`` to a tuple.

    Mirrors :func:`_species_tuple`: one profession is the common case and writes
    as a bare constant; a tuple is for the rare character with more than one.
    """
    if professions is None:
        return ()
    if isinstance(professions, ProfessionEntry):
        return (professions,)
    return tuple(professions)


def _profession_name(conn: sqlite3.Connection, profession_id: str) -> str:
    """Return a stored profession's display name, or its id if the row has gone."""
    row = conn.execute("SELECT name FROM professions WHERE profession_id = ?", [profession_id]).fetchone()
    return row[0] if row else profession_id


def _auto_world_key(region_name: str) -> str:
    """Derive ``world-of-rathe/<slug>.md`` from a region display name, or return ``""``."""
    slug = re.sub(r"^the\s+", "", region_name.strip(), flags=re.IGNORECASE)
    slug = slug.lower().replace(" ", "-")
    candidate = SRC / "world-of-rathe" / f"{slug}.md"
    return f"world-of-rathe/{slug}.md" if candidate.exists() else ""


# ---------------------------------------------------------------------------
# Input dataclasses
# ---------------------------------------------------------------------------


@dataclass
class NarratedVideoEntry:
    """A narrated reading of a story."""

    author: str
    source_link: str
    channel_link: str = ""


@dataclass(frozen=True)
class SpeciesEntry:
    """What a character is (R2) — a species, in one flat list.

    Frozen and catalogued for the same reason every other entity is: the id is a
    hash of the name at the call site, so a second literal for ``Human`` reuses
    this row rather than minting a second one. The real trap is a *changed*
    name — that mints a new row and strands the old one, the same as every
    other registry id.

    There is no ``kind`` column separating species from cosmological tier.
    Herald, Aesir, Ancient, Embra and Dragon sit beside Human and Dwarf, because
    the line between them is a reading of the lore rather than a fact the data
    can check, and a column nothing can validate is a column that drifts.
    """

    name: str
    aliases: tuple[str, ...] = ()
    """Other names this species answers to (R6), e.g. ``"Aesirs"`` for ``"Aesir"``.
    Plurals mostly: the supplement entries these replace carried them by hand, and
    English plurals are not mechanical enough to generate — ``Aesir`` takes an s,
    ``Chanek`` does not, and nothing in the prose writes ``Humans``."""


@dataclass(frozen=True)
class ProfessionEntry:
    """A trade many hold independently (R9) — Braumeister, shieldbearer.

    Three axes describe a body of people, and a profession is the one with no
    roster:

    - A **group** (``GroupEntry``) is a named body that acts as one — bounded,
      citable, so its roster lives on the catalogue entry.
    - A **title** (``TitleEntry``) is an office one person holds at a time —
      ordered holders, resolved through ``character_heroes``.
    - A **profession** is a trade many hold independently, with no roster at
      all. "Braumeisters are the elite of their trade" (``world-of-rathe/aria.md``)
      says what the trade is, not who is in it — "who is a Braumeister" is
      **unbounded and unsourceable**, which is exactly what a group's
      ``member_source`` exists to prevent. Forcing it into ``groups`` would put
      an uncitable membership in the one table built to refuse them.

    Frozen and catalogued for the same reason every other entity is: the id is
    a hash of the name at the call site (``registry_ids.profession_id``), so a
    second literal for ``Braumeister`` reuses this row rather than minting a
    second one. The real trap is a *changed* name — that mints a new row and
    strands the old one, the same as every other registry id.

    No ``aliases`` field and no ``profession_aliases`` table: unlike a species,
    no profession has yet needed a plural or a dated alternate name in the
    prose. Add the table when one does, not before.
    """

    name: str


@dataclass(frozen=True)
class NPCEntry:
    """A non-playable character to link to a story.

    Frozen because the canonical definition of each NPC lives in
    ``entries/catalogue/npcs.py`` and one instance is shared by every story that
    links it — a mutation would silently rewrite the entity for unrelated pages.
    """

    name: str
    species: "SpeciesEntry | tuple[SpeciesEntry, ...] | None" = None
    """What this character is (R2). One :class:`SpeciesEntry`, or a tuple where the
    lore says two — Scooba is a ``Zombie`` and a ``Dog``, which the free-text
    column this replaces could only write as the single value ``"Zombie Dog"``.

    Replace-semantic, like the rosters and the alias tables: ``None`` and ``()``
    both mean this character has no recorded species, and both will clear one that
    is stored. That is a change from the column, where an omitted value meant
    "preserve" — 32 rows carried a species no declaration named, and every one of
    them had to be written into the catalogue before the switch."""
    professions: "ProfessionEntry | tuple[ProfessionEntry, ...] | None" = None
    """Trades this character holds (R9): ``NPCEntry("Balen", professions=prof.BRAUMEISTER)``.
    One :class:`ProfessionEntry`, or a tuple where the lore names more than one.

    **Replace-semantic, like ``species`` and unlike ``status``/``hero_slug``.**
    ``species`` and ``status`` sit next to each other on this dataclass following
    *opposite* contracts — ``status=""`` preserves, an omitted ``species`` is a
    deletion — so this docstring says which one ``professions`` follows: the
    ``species`` contract. ``None`` and ``()`` both mean this character has no
    recorded profession, and both clear one that is stored; ``character_professions``
    is a junction, and a junction states the complete set.

    Raises ``ValueError`` for a repeated profession on one entry — naming it —
    the same guard shape ``GroupEntry.member_pairs()``, ``_resolve_title_holders`` and
    ``_resolve_kin_relatives`` all use: two entries naming the same profession
    would otherwise resolve differently on the write path (``INSERT OR IGNORE``
    keeps the first) than on a preview that diffed a dict (last wins).

    **A hero's profession goes here too, and there is no hero-shaped second
    path** (the user's call, 2026-08-22). A hero is the game-side row — a
    canonical slug and the cards printed for it — while a character is the
    lore-side person, and a trade is a fact about the person. So
    ``heroes_canonical`` joins through ``character_heroes`` to read it, rather
    than carrying its own copy. Kano is a hero and a Lord Wizard with no
    ``NPCEntry`` of his own; the way to say so is ``NPCEntry("Kano",
    hero_slug="kano", professions=prof.LORD_WIZARD)``, which migration 12 built
    ``hero_slug`` for. The same reasoning applies to ``species`` and ``kin``."""
    status: str = ""
    """Leave empty to preserve an existing NPC's status; new NPCs default to ``"Unknown"``."""
    other_characters_story_key: str = ""
    epithets: tuple[str, ...] = ()
    """Styles the character is given (R4): ``"the Wartune Herald"``, ``"Archangel of
    War"``. ``name`` is untouched — these are the names *besides* the display name,
    which is why a character may hold several where the comma-glued form held one."""
    short_names: tuple[str, ...] = ()
    """The same character in fewer words: ``"Mortimer"`` for
    ``"Dr. Krest Mortimer, 'The Fixer'"``. Stored alongside the epithets under
    ``kind='short-name'`` — both are match strings, and only the wording of a
    tooltip needs to tell them apart."""
    hero_slug: str = ""
    """Declares that this NPC *is* that playable hero (identity spine, migration
    12): ``NPCEntry("Fightmaster Kox", hero_slug="kox")`` makes this NPC's row
    the hero's character row, writing ``character_heroes``.

    Preserves on empty, like ``status`` and unlike ``species``: ``""`` means
    "leave whatever is stored" rather than "this NPC is not a hero". There is
    deliberately no way to clear an identity claim through a declaration — a
    person does not stop having been a hero.

    Raises ``ValueError`` for an unknown slug, the same way a slug in
    ``characters=`` does, and when two different NPCs in one call claim the
    same slug — the shape of
    the guard in ``GroupEntry.member_pairs()``, which raises on a repeated NPC for
    the same reason: the write and the preview would otherwise resolve the
    clash differently and neither would say so."""
    kin: "tuple[tuple[NPCEntry | str, str] | tuple[NPCEntry | str, str, str], ...]" = ()
    """Kinship facts (R8): ``((relative, relation), ...)`` pairs, or
    ``(relative, relation, story_key)`` triples when one fact is attested
    somewhere worth citing (see :func:`_kin_triple`). ``relative`` is an
    :class:`NPCEntry` or a canonical hero slug string, resolved through
    ``character_heroes`` exactly as ``TitleEntry.hero_holders`` resolves one —
    after migration 12 both a hero and an NPC land in the same ``characters``
    row, so one column, and one type here, holds either::

        NPCEntry("Lyath", kin=((npc.BLOODWORTH_GOLDMANE, "father"), ("victor", "sibling")))

    ``relation`` is a closed vocabulary, checked in ``validate_data.py`` rather
    than here (the same split ``status`` and epithet ``kind`` follow):
    ``father``, ``mother``, ``parent``, ``sibling``, ``spouse``, ``child``.
    ``parent``/``child`` exist alongside the gendered pair because a page may
    state a parent without saying which — the data should not have to guess.

    One row per stated fact — declaring Lyath's father as Bloodworth writes
    **only** that row. Nothing here writes "Bloodworth's child is Lyath"; the
    query layer derives it (``db._queries.select_character_kin_both_directions``),
    because a fact stored twice could disagree with itself and nothing would
    say which half was right.

    **Replace-semantic**, like ``species`` and unlike ``status``/``hero_slug``:
    ``kin=()`` clears whatever kin is stored for this character.
    ``character_kin`` is a junction, not a scalar column, and this codebase's
    rule for a junction is that a declaration states the complete set (see
    ``species``'s docstring for the same reasoning applied to a different
    field). The alternative — preserving on empty, as ``hero_slug`` does
    because an identity claim should never un-happen — does not fit a kin fact
    the way it fits an identity claim: kinship is read off a page and a
    correction to what was read (a mis-transcribed relation, a merged
    duplicate) has to be able to remove a row, not just add better ones beside
    the wrong one forever with no way to retract it.

    Raises ``ValueError`` for a repeated ``(relative, relation)`` pair —
    naming the same person as a relative under the same relation twice,
    including once as an :class:`NPCEntry` and once as a hero slug, the same
    hazard ``GroupEntry.member_pairs()`` and ``TitleEntry``'s holder resolution
    guard against — for an unknown hero slug, and for a character named as
    their own relative."""


@dataclass(frozen=True)
class RegionEntry:
    """A world region to link to a story (upserted into regions table).

    Frozen and shared — see :class:`NPCEntry`; the constants live in
    ``entries/catalogue/regions.py``.
    """

    name: str
    world_of_rathe_story_key: str = ""


@dataclass(frozen=True)
class LocationEntry:
    """A location to link to a story (upserted into locations table).

    Frozen and shared — see :class:`NPCEntry`; the constants live in
    ``entries/catalogue/locations.py``. This one matters most: ``location_id``
    hashes ``name`` *and* ``region``, so a per-call-site edit to either does not
    update the row, it mints a second one.
    """

    name: str
    region: str = ""
    """Display name of the region — resolved to ``RegionId`` internally."""
    notes: str = ""
    lore_fragment: str = ""
    """mdBook heading anchor id for deep links, e.g. ``"grand-bazaar"``."""
    world_of_rathe_story_key: str = ""
    """Only needed when creating a new region via this location."""
    parent: "LocationEntry | None" = None
    """Enclosing location (R7). **Containment only** — X is *inside* Y. Proximity
    ("area next to Candlehold") is not containment and stays prose in ``notes``;
    the two read identically in the data, which is why the split was reviewed row
    by row rather than migrated. See ``plans/location-containment-review.csv``."""
    aliases: tuple[str | tuple[str, str], ...] = ()
    """Other names for this same place (R6). A bare string, or ``(alias, era)``
    where the lore dates the name — ``("Fedhari", "Dhani")``. This row stays
    canonical and every alias resolves to it, so the Lore Graph draws one node
    where it used to draw three."""


@dataclass(frozen=True)
class MonsterEntry:
    """A monster to link to a story (upserted into monsters table).

    Frozen and shared — the constants live in ``entries/catalogue/monsters.py``.
    """

    name: str
    description: str = ""


@dataclass(frozen=True)
class FaunaEntry:
    """A fauna entry to link to a story (upserted into fauna table).

    Frozen and shared — the constants live in ``entries/catalogue/fauna.py``.
    """

    name: str
    description: str = ""


@dataclass(frozen=True)
class FloraEntry:
    """A flora entry to link to a story (upserted into flora table).

    Frozen and shared — the constants live in ``entries/catalogue/flora.py``.
    """

    name: str
    description: str = ""


@dataclass(frozen=True)
class FoodDrinkEntry:
    """A food or drink item to link to a story (upserted into food_and_drink table).

    Frozen and shared — the constants live in ``entries/catalogue/food_drink.py``.
    ``food_drink_id`` hashes ``"name|kind"``, so ``kind`` is part of the identity
    the way a location's ``region`` is: change it at one call site and you get a
    second row, not an edited one.
    """

    name: str
    kind: str
    """Type category, e.g. ``"Drink"`` or ``"Food"``."""


@dataclass(frozen=True)
class GroupEntry:
    """A group — house, clan, guild, order, troupe — with its roster.

    Frozen and shared; the constants live in ``entries/catalogue/groups.py``.
    ``group_id`` hashes ``name`` alone, so a second spelling mints a second row.

    This class is the one departure from "the catalogue holds identity only".
    Membership is declared **here, on the group**, because "Tara VanGeld is a
    VanGeld" is a world fact with no page to hang from — there is no story whose
    registration would assert it. Mentions stay on the story, via
    ``upsert_story(groups=[...])``. Both are needed and they answer different
    questions: the roster answers "who belongs", the mention answers "which pages
    name this group". See D1 in ``plans/character-groups-schema-options.md``.

    Import direction is one-way — ``catalogue/groups.py`` imports
    ``catalogue/npcs.py``, never the reverse — so no cycle is possible.
    """

    name: str
    kind: str = ""
    """Free text: ``"clan"``, ``"house"``, ``"guild"``, ``"order"``, ``"troupe"``."""
    members: tuple["NPCEntry | str | tuple[NPCEntry | str, str]", ...] = ()
    """The roster (R1). A tuple, because the dataclass is frozen and hashable.

    An item is a **person** — an :class:`NPCEntry` or a canonical hero slug
    string — or a ``(person, story_key)`` pair when that one membership is
    attested somewhere other than ``member_source``. One field holds both kinds
    because after migration 12 a hero and an NPC are rows of the same
    ``characters`` table, and migration 18 gave them one junction to sit in;
    the ``NPCEntry | str`` item type is the one ``NPCEntry.kin`` and
    ``upsert_story``'s ``characters=`` already use for the same reason.

    The pair exists because ``The Maela`` needed it. Eleven of the twelve rosters
    that cite a source were read off a single page that lists the whole roster —
    ``flavour/super-slam.md`` names the guilds, ``lyath-about.md`` names the
    family. The Maela is not like that: five seers named across four different
    flavour pages, and no page that lists them as a roster. One string for the
    group could only be right for one of them. A hero member could not carry
    that pair while the hero roster was a bare tuple of slugs; it can now, and
    that documented asymmetry is gone rather than merely narrowed.

    An unknown hero slug raises, exactly as it does in ``characters=``.
    """
    parent: "GroupEntry | None" = None
    """Enclosing group, e.g. a Super Slam guild inside the clan it draws from."""
    location: "LocationEntry | None" = None
    """Only when the group is *also* a place — Teklo Industries, a company and a
    works. Most groups leave this empty; a group is not a place."""
    member_source: str = ""
    """Optional story key citing the roster (D2). The **default** for every member
    that does not carry its own key in ``members``; a group whose members are
    each attested somewhere different leaves this empty and pairs them instead."""
    aliases: tuple[str, ...] = ()
    """Other names the group answers to (R6), e.g. ``"Mendacity"`` for
    ``"Mendacity Media"``. Without these the tooltip matcher only finds the full
    canonical name, which is how bare "Mendacity" lost its tooltip in stage 2."""
    lore_story_key: str = ""
    """Story key of the page this group is **documented** on, e.g.
    ``"world-of-rathe/solana.md"``. Not where the group lives — a group moves,
    and most carry no region at all. A location reaches its page by walking
    ``region_id`` to ``regions.world_of_rathe_story_key``; a group has no region
    to walk, so it carries the page itself."""
    lore_fragment: str = ""
    """Heading anchor on ``lore_story_key``, e.g. ``"the-hand-of-sol"``. Validated
    against the real headings on that page, exactly as location fragments are."""

    def member_pairs(self) -> list[tuple["NPCEntry | str", str]]:
        """The roster as ``(person, story_key)`` pairs, with the default applied.

        The one place that unpacks the optional pair, so every caller reads a
        roster the same shape whether or not a membership cites its own page.
        ``person`` is whatever the declaration gave — an :class:`NPCEntry` or a
        hero slug string; resolving either to a ``character_id`` needs the
        database and therefore happens in
        :meth:`Database._resolve_group_members`, not here.

        Named ``member_pairs`` rather than ``members`` only because ``members``
        is now the field.

        Raises:
            ValueError: if one person appears twice **under the same
                declaration form** — the same NPC name twice, or the same slug
                twice. The pair made this reachable and the two paths resolve it
                differently: ``group_characters`` is keyed
                ``(group_id, character_id)`` and written with
                ``INSERT OR IGNORE``, so the write keeps the **first** citation,
                while the preview builds a dict and reports the **last**. Neither
                raises, so a roster naming someone twice would be previewed as one
                page and stored as another. Guarded here rather than in either
                path, so both fail the same way.

                A slug and an :class:`NPCEntry` naming *one* person is the other
                half of the same clash, and it cannot be seen from here — it
                needs ``character_heroes``. ``_resolve_group_members`` raises on
                it, so this class stays a pure frozen dataclass with no database
                of its own.
        """
        pairs: list[tuple["NPCEntry | str", str]] = []
        seen: dict[str, str] = {}
        for item in self.members:
            if isinstance(item, tuple):
                person, source = item
            else:
                person, source = item, self.member_source
            key = person if isinstance(person, str) else person.name
            if key in seen:
                raise ValueError(
                    f"{self.name!r} names {key!r} twice in members "
                    f"(citing {seen[key] or '(none)'!r} and {source or '(none)'!r}). "
                    "A membership is one row; cite the page that attests it once."
                )
            seen[key] = source
            pairs.append((person, source))
        return pairs


@dataclass(frozen=True)
class TitleEntry:
    """An office — Grand Magister, Dracai of Aether, Soothsayer — with its holders.

    Frozen and shared; the constants will live in ``entries/catalogue/titles.py``
    (a later task fills them in — this class only builds the surface). ``title_id``
    hashes ``name`` alone, like :class:`GroupEntry`'s ``group_id``.

    This is the second place ``entries/catalogue/`` holds a relationship rather
    than identity alone — :class:`GroupEntry` is the first, for the same reason
    given there: "Kano held the Dracai of Aether" is a world fact with no page to
    hang it from, so no ``upsert_story()`` call could assert it on its own.
    Mentions stay on the story, via ``upsert_story(titles=[...])``.

    ``hero_holders`` takes canonical hero slugs and resolves them through
    ``character_heroes`` rather than through a second junction table. That is
    the first thing migration 12's identity spine makes possible: a hero and an
    NPC can land in the *same* ``title_holders.character_id`` column, because a
    hero and an NPC are now rows of the same ``characters`` table.
    ``GroupEntry`` reached the same shape in migration 18, one ``members``
    field feeding ``group_characters``; ``TitleEntry`` was built after the
    merge and never needed a hero half at all.

    Holders are **replace-semantic**, like a group roster: a short holder list
    replaces the stored one, so a dropped holder is a silent deletion. The dry
    run reports a ``REMOVED`` line for exactly this reason — see
    ``GroupEntry.member_pairs()`` and ``_show_group_changes`` for the precedent.
    """

    name: str
    group: "GroupEntry | None" = None
    """The body this office belongs to, if any: ``Dracai of Aether`` hangs off
    the Dracai; ``Soothsayer`` hangs off nothing."""
    npc_holders: tuple[tuple["NPCEntry", int, str], ...] = ()
    """``(npc, ordinal, story_key)`` triples. ``ordinal`` records a succession
    where the lore gives one (Grand Magister 1-5) and is ``0`` where it does
    not — it is not unique, and several holders may share one (the Dracai, held
    concurrently). ``story_key`` cites the page that attests the holder."""
    hero_holders: tuple[tuple[str, int, str], ...] = ()
    """``(hero_slug, ordinal, story_key)`` triples, resolved through
    ``character_heroes``. An unknown slug raises, the same as a slug in
    ``characters=`` and ``NPCEntry.hero_slug``."""


# ---------------------------------------------------------------------------
# StoryRecord
# ---------------------------------------------------------------------------


@dataclass
class StoryRecord:
    """Immutable snapshot of a story row; back-references ``Database`` for mutation."""

    story_id: str
    story_key: str
    story_type: str
    title: str
    authors: str
    artists: str
    source_link: str
    publication_date: str
    thumbnail_image_link: str
    narrated_videos: list[NarratedVideoEntry]
    _db: "Database"

    def display(self, *, file: IO[str] | None = None) -> None:
        """Print a human-readable summary of this story and its linked entities."""
        self._db.display_story(self.story_key, file=file)

    def remove(self, *, dry_run: bool = False) -> dict[str, Any]:
        """Remove this story and all its junction rows.

        Args:
            dry_run: If ``True``, print what would be deleted without writing.

        Returns:
            Report dict matching :meth:`Database.remove_story`.
        """
        return self._db.remove_story(self.story_key, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


class Database:
    """Runtime interface to the fablore SQLite database.

    Instantiate with :class:`Database` for normal use (auto-seeds from CSVs
    when empty) or :meth:`from_csv` to force a full reseed.

    Args:
        path: Path to ``fablore.db``; use ``":memory:"`` for tests.
        data_dir: Override the ``src/data/`` directory (defaults to the
            repository root resolved from this file's location).

    Example::

        db = Database("src/data/fablore.db")
        db.print_heroes()  # show available slugs
        r = db.upsert_story(
            "src/main-story/foo.md",
            story_type="main-story",
            title="Foo",
            characters=["boltyn", NPCEntry("Guard Captain", species=SpeciesEntry("Human"))],
        )
        r.display()
    """

    def __init__(
        self,
        path: str | Path,
        data_dir: Path | None = None,
    ) -> None:
        self._path = Path(path)
        self._data_dir = data_dir or DATA
        self._last_dry_run_changed = False
        self.conn = open_db(self._path)
        # Auto-seed when the database is empty, or when a migration has emptied a
        # derived game-data table that only the CSVs can repopulate (migration 7
        # rebuilds both printings tables to widen their primary key).
        if self._path != Path(":memory:") and self._needs_seed():
            seed_from_csvs(self.conn, self._data_dir)

    def _needs_seed(self) -> bool:
        for table in ("stories", "equipment_printings", "weapons_printings", "species", "character_heroes"):
            if self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0:
                return True
        return False

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        data_dir: Path | None = None,
    ) -> "Database":
        """Open (or create) the database and force a reseed from CSVs.

        Existing rows are not overwritten (``INSERT OR IGNORE`` semantics).
        Use this after manually editing a CSV to synchronise the database.
        """
        db = cls.__new__(cls)
        db._path = Path(path)
        db._data_dir = data_dir or DATA
        db._last_dry_run_changed = False
        db.conn = open_db(db._path)
        seed_from_csvs(db.conn, db._data_dir)
        return db

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------

    def list_heroes(self) -> list[dict[str, str]]:
        """Return ``[{"slug": …, "name": …}]`` for all canonical heroes."""
        rows = q.select_all_heroes_canonical(self.conn)
        return [{"slug": r["canonical_slug"], "name": r["canonical_hero"]} for r in rows]

    def list_weapons(self) -> list[dict[str, str]]:
        """Return ``[{"slug": …, "name": …}]`` for all canonical weapons."""
        rows = q.select_all_weapons_canonical(self.conn)
        return [{"slug": r["canonical_slug"], "name": r["canonical_weapon"]} for r in rows]

    def list_equipment(self) -> list[dict[str, str]]:
        """Return ``[{"slug": …, "name": …}]`` for all canonical equipment."""
        rows = q.select_all_equipment_canonical(self.conn)
        return [{"slug": r["canonical_slug"], "name": r["canonical_equipment"]} for r in rows]

    def list_regions(self) -> list[dict[str, str]]:
        """Return region dicts with ``region_id``, ``region_name``, ``world_of_rathe_story_key``."""
        rows = q.select_all_regions(self.conn)
        return [dict(r) for r in rows]

    def print_heroes(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print canonical hero slugs and display names."""
        self._print_table(self.list_heroes(), ["slug", "name"], file=file)

    def print_weapons(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print canonical weapon slugs and display names."""
        self._print_table(self.list_weapons(), ["slug", "name"], file=file)

    def print_equipment(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print canonical equipment slugs and display names."""
        self._print_table(self.list_equipment(), ["slug", "name"], file=file)

    def print_regions(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print region names and their lore page keys."""
        self._print_table(
            self.list_regions(),
            ["region_name", "world_of_rathe_story_key"],
            file=file,
        )

    def list_npcs(self) -> list[dict[str, str]]:
        """Return ``[{"name": …, "species": …, "status": …}]`` for all NPCs.

        ``species`` is joined from ``npc_species`` and comma-joined for display,
        so Scooba reads ``"Zombie, Dog"``. It is a rendering of the junction, not
        a column — nothing writes back through it.
        """
        names = {r["species_id"]: r["name"] for r in q.select_all_species(self.conn)}
        joined: dict[str, list[str]] = {}
        for cid, sid in self.conn.execute("SELECT character_id, species_id FROM npc_species ORDER BY sort_order"):
            joined.setdefault(cid, []).append(names.get(sid, sid))
        rows = q.select_all_npcs(self.conn)
        return [
            {
                "name": r["name"],
                "species": ", ".join(joined.get(r["character_id"], [])),
                "status": r["status"],
            }
            for r in rows
        ]

    def print_npcs(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print all NPCs with species and status."""
        self._print_table(self.list_npcs(), ["name", "species", "status"], file=file)

    def list_species(self) -> list[dict[str, str]]:
        """Return ``[{"name": …, "notes": …}]`` for all species."""
        return [{"name": r["name"], "notes": r["notes"]} for r in q.select_all_species(self.conn)]

    def list_locations(self) -> list[dict[str, str]]:
        """Return location dicts with ``name``, ``region``, ``notes``, ``lore_fragment``."""
        rows = q.select_all_locations(self.conn)
        region_map = {r["region_id"]: r["region_name"] for r in q.select_all_regions(self.conn)}
        return [
            {
                "name": r["name"],
                "region": region_map.get(r["region_id"], ""),
                "notes": r["notes"],
                "lore_fragment": r["lore_fragment"],
            }
            for r in rows
        ]

    def print_locations(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print all locations with their region."""
        self._print_table(self.list_locations(), ["name", "region", "lore_fragment"], file=file)

    @staticmethod
    def _print_table(rows: list[dict], cols: list[str], *, file: IO[str] | None = None) -> None:
        import sys as _sys

        out = file or _sys.stdout
        if not rows:
            out.write("(none)\n")
            return
        widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
        header = "  ".join(c.ljust(widths[c]) for c in cols)
        out.write(header + "\n")
        out.write("  ".join("-" * widths[c] for c in cols) + "\n")
        for row in rows:
            out.write("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in cols) + "\n")

    # ------------------------------------------------------------------
    # Story management
    # ------------------------------------------------------------------

    @property
    def last_dry_run_changed(self) -> bool:
        """Whether the most recent ``upsert_story(dry_run=True)`` found a change.

        Set on every dry run, and never by a real write. A caller replaying many
        declarations reads it to decide whether the preview it just captured is
        worth showing — the preview text alone cannot be distinguished from a
        no-op without parsing it.
        """
        return self._last_dry_run_changed

    def upsert_story(
        self,
        path: str | Path,
        story_type: str,
        title: str,
        authors: str = "",
        artists: str = "",
        source_link: str = "",
        publication_date: str = "",
        thumbnail_image_link: str = "",
        narrated_videos: list[NarratedVideoEntry] | None = None,
        *,
        characters: "list[NPCEntry | str] | None" = None,
        fragments: dict[str, str] | None = None,
        locations: list[LocationEntry] | None = None,
        regions: list[RegionEntry] | None = None,
        monsters: list[MonsterEntry] | None = None,
        fauna: list[FaunaEntry] | None = None,
        flora: list[FloraEntry] | None = None,
        food_drink: list[FoodDrinkEntry] | None = None,
        weapons: list[str] | None = None,
        equipment: list[str] | None = None,
        groups: list[GroupEntry] | None = None,
        titles: list[TitleEntry] | None = None,
        dry_run: bool = False,
    ) -> StoryRecord:
        """Register or update a story and declare its linked entities.

        Entity link parameters follow **replace semantics**:

        - ``None`` (default) — leave existing links of this type unchanged.
        - ``[]`` — remove all links of this type.
        - ``[...]`` — replace all links of this type with exactly this list.

        Args:
            path: Path to the ``*.md`` file under ``src/``.
            story_type: First ``src/`` path segment. Must be one of
                ``"archive"``, ``"digital-tiles"``, ``"equipment"``,
                ``"flavour"``, ``"heroes-of-rathe"``, ``"main-story"``,
                ``"other-characters"``, ``"short-stories"``, ``"summaries"``,
                ``"weapons"``, ``"world-of-rathe"``.
            title: Human-readable title for the story.
            authors: Author credits (free text, comma-separated suggested).
            artists: Illustration credits (free text).
            source_link: Canonical source URL.
            publication_date: ISO date string e.g. ``"2025-07-12"``.
            thumbnail_image_link: Public URL for a thumbnail image.
            narrated_videos: Narrated video entries; ``None`` = leave unchanged.
            characters: A mixed list of canonical hero slugs (see
                :meth:`print_heroes`) and :class:`NPCEntry` instances — a hero
                is not a different kind of thing any more, it is a character
                that happens to have a row in ``character_heroes``, so one
                parameter names both. A slug is resolved through
                ``character_heroes`` to a ``character_id`` (minting the
                identity link if this is the first time the hero has one — the
                same gap-fill ``_upsert_one_title`` does for a hero holder) and
                raises ``ValueError`` if unknown, exactly as the old
                ``heroes=`` did. An :class:`NPCEntry` resolves through the same
                path :class:`NPCEntry` always has — omit ``status`` to preserve
                whatever an existing NPC row already has; only pass it when
                this story is the evidence for the value. ``species`` does
                **not** preserve — it is replace-semantic, so an omitted one is
                a deletion. Both land in the same ``story_characters`` row, a
                plain replace-semantic junction parameter like every other one:
                ``None`` leaves the story's character links unchanged, ``[]``
                removes them all, ``[...]`` makes the stored set exactly this
                list.

                **A slug and an ``NPCEntry`` naming the same person in one
                list raises**, naming the story, both origins and the shared
                ``character_id`` — the same guard shape
                ``GroupEntry.member_pairs()`` and ``_resolve_title_holders`` use for
                a repeated member. A story used to be able to name one person
                through ``heroes=`` and again through ``npcs=`` and have them
                collapse to one row; that only worked because they were two
                lists with different jobs. Within one ``characters=`` list a
                repeat is a mistake, not a merge.
            fragments: Optional ``{key: anchor}`` map giving a heading anchor id
                within the story for a hero or an NPC, e.g.
                ``{"dorinthea": "morlock-hill-dtd209", "Guard Captain": "intro"}``.
                A key is a canonical hero slug or an NPC display name declared
                in ``characters=`` for this same call — a key matching no one
                declared this call raises.
            locations: Location entries.
            regions: Region entries (for stories that reference a region but no
                specific location within it).
            monsters: Monster entries.
            fauna: Fauna entries.
            flora: Flora entries.
            food_drink: Food and drink entries.
            weapons: Canonical weapon slugs (see :meth:`print_weapons`).
            equipment: Canonical equipment slugs (see :meth:`print_equipment`).
            groups: Group entries this page *mentions* (R5). This does not say
                who belongs — membership is declared on the group itself, in
                ``entries/catalogue/groups.py``. Upserting a group here also
                upserts its roster, so a page can introduce a group without a
                separate pass.
            titles: Title entries this page *mentions* (R5). Like ``groups``,
                this does not say who held the office — holders are declared on
                the title itself, in ``entries/catalogue/titles.py``. Upserting
                a title here also upserts its holders.
            dry_run: Print a diff and return the record without writing anything.

        Returns:
            :class:`StoryRecord` reflecting the final state of the story.

        Raises:
            ValueError: If an unknown hero / weapon / equipment slug is given,
                or if a ``lore_fragment`` cannot be resolved to a heading on disk.
        """
        story_key = _story_key_from_path(path)
        story_id = _story_id(story_key)

        # Resolve characters eagerly so we fail fast before writing anything —
        # an unknown hero slug or a person named twice (once as a slug, once
        # as an NPCEntry) must not get partway through a write first.
        if characters is not None:
            self._resolve_characters(story_key, characters)
        if fragments:
            self._validate_fragments(story_key, characters, fragments)
        weapon_ids = self._resolve_weapons(weapons) if weapons is not None else None
        equip_ids = self._resolve_equipment(equipment) if equipment is not None else None

        if dry_run:
            return self._dry_run_upsert(
                story_key=story_key,
                story_id=story_id,
                story_type=story_type,
                title=title,
                authors=authors,
                artists=artists,
                source_link=source_link,
                publication_date=publication_date,
                thumbnail_image_link=thumbnail_image_link,
                narrated_videos=narrated_videos,
                characters=characters,
                fragments=fragments,
                locations=locations,
                regions=regions,
                monsters=monsters,
                fauna=fauna,
                flora=flora,
                food_drink=food_drink,
                weapon_ids=weapon_ids,
                equip_ids=equip_ids,
                groups=groups,
                titles=titles,
            )

        with self.conn:
            q.upsert_story(
                self.conn,
                story_id=story_id,
                story_key=story_key,
                story_type=story_type,
                title=title,
                authors=authors,
                artists=artists,
                source_link=source_link,
                publication_date=publication_date,
                thumbnail_image_link=thumbnail_image_link,
            )
            if narrated_videos is not None:
                q.set_narrated_videos(
                    self.conn,
                    story_id,
                    [(v.author, v.source_link, v.channel_link) for v in narrated_videos],
                )
            if characters is not None:
                self._write_story_characters(story_id, story_key, characters, fragments or {})
            if regions is not None:
                region_ids = self._upsert_regions(regions)
                q.set_story_junction(self.conn, story_id, "story_regions", "region_id", region_ids)
            if locations is not None:
                location_ids = self._upsert_locations(locations)
                q.set_story_junction(
                    self.conn,
                    story_id,
                    "story_locations",
                    "location_id",
                    location_ids,
                )
            if monsters is not None:
                monster_ids = self._upsert_monsters(monsters)
                q.set_story_junction(self.conn, story_id, "story_monsters", "monster_id", monster_ids)
            if fauna is not None:
                fauna_ids = self._upsert_fauna(fauna)
                q.set_story_junction(self.conn, story_id, "story_fauna", "fauna_id", fauna_ids)
            if flora is not None:
                flora_ids = self._upsert_flora(flora)
                q.set_story_junction(self.conn, story_id, "story_flora", "flora_id", flora_ids)
            if food_drink is not None:
                fd_ids = self._upsert_food_drink(food_drink)
                q.set_story_junction(
                    self.conn,
                    story_id,
                    "story_food_drink",
                    "food_drink_id",
                    fd_ids,
                )
            if weapon_ids is not None:
                q.set_story_junction(
                    self.conn,
                    story_id,
                    "story_weapons",
                    "canonical_weapon_id",
                    weapon_ids,
                )
            if equip_ids is not None:
                q.set_story_junction(
                    self.conn,
                    story_id,
                    "story_equipment",
                    "canonical_equipment_id",
                    equip_ids,
                )
            if groups is not None:
                group_ids = self._upsert_groups(groups)
                q.set_story_junction(self.conn, story_id, "story_groups", "group_id", group_ids)
            if titles is not None:
                title_ids = self._upsert_titles(titles)
                q.set_story_junction(self.conn, story_id, "story_titles", "title_id", title_ids)

        # Write-through: regenerate affected CSVs so git stays in sync.
        _export.export_stories(self.conn, self._data_dir)
        _export.export_registry_tables(self.conn, self._data_dir)
        _export.export_story_junctions(self.conn, self._data_dir)

        return self._load_record(story_id)

    def get_story(self, path: str | Path) -> StoryRecord | None:
        """Return the :class:`StoryRecord` for this path, or ``None`` if not registered."""
        story_key = _story_key_from_path(path)
        row = q.select_story_by_key(self.conn, story_key)
        if row is None:
            return None
        return self._load_record(row["story_id"])

    def remove_story(
        self,
        path: str | Path,
        *,
        dry_run: bool = False,
        file: IO[str] | None = None,
    ) -> dict[str, Any]:
        """Remove a story and all its junction rows.

        Args:
            path: Path to the ``*.md`` file (used to locate the story).
            dry_run: Print report and return counts without modifying the database.
            file: Output stream for the report (default ``sys.stdout``).

        Returns:
            ``{"dry_run": bool, "story_key": str, "story_id": str,
               "junctions": {table: count}, "story_deleted": bool}``
        """
        import sys as _sys

        out = file or _sys.stdout
        story_key = _story_key_from_path(path)
        row = q.select_story_by_key(self.conn, story_key)
        if row is None:
            out.write(f"Story not found: {story_key}\n")
            return {
                "dry_run": dry_run,
                "story_key": story_key,
                "story_id": None,
                "junctions": {},
                "story_deleted": False,
            }

        story_id = row["story_id"]
        junction_counts = q.count_story_junctions(self.conn, story_id)
        total_junctions = sum(junction_counts.values())

        label = "DRY RUN — no files modified\n" if dry_run else "Removed story data\n"
        out.write(label)
        out.write(f"StoryKey: {story_key}\nStoryId:  {story_id}\n\n")
        if total_junctions:
            for table, n in junction_counts.items():
                if n:
                    out.write(f"  {table}: {n} link(s) to delete\n")
            out.write("\n")
        else:
            out.write("  (no junction links)\n\n")

        if dry_run:
            return {
                "dry_run": True,
                "story_key": story_key,
                "story_id": story_id,
                "junctions": junction_counts,
                "story_deleted": False,
            }

        with self.conn:
            q.delete_story(self.conn, story_id)

        _export.export_stories(self.conn, self._data_dir)
        _export.export_story_junctions(self.conn, self._data_dir)

        return {
            "dry_run": False,
            "story_key": story_key,
            "story_id": story_id,
            "junctions": junction_counts,
            "story_deleted": True,
        }

    def display_story(self, path: str | Path, *, file: IO[str] | None = None) -> None:
        """Print a human-readable summary of a story and its linked entities."""
        import sys as _sys

        out = file or _sys.stdout
        story_key = _story_key_from_path(path)
        row = q.select_story_by_key(self.conn, story_key)
        if row is None:
            out.write(f"Story not found: {story_key}\n")
            return

        story_id = row["story_id"]
        out.write(f"Title:    {row['title']}\n")
        out.write(f"StoryKey: {row['story_key']}\n")
        out.write(f"StoryId:  {story_id}\n")
        out.write(f"Type:     {row['story_type']}\n")
        if row["authors"]:
            out.write(f"Authors:  {row['authors']}\n")
        if row["artists"]:
            out.write(f"Artists:  {row['artists']}\n")
        if row["publication_date"]:
            out.write(f"Date:     {row['publication_date']}\n")
        if row["source_link"]:
            out.write(f"Source:   {row['source_link']}\n")

        videos = q.select_narrated_videos(self.conn, story_id)
        if videos:
            out.write("Narrated:\n")
            for v in videos:
                out.write(f"  • {v['author']} — {v['source_link']}\n")
        out.write("\n")

        self._display_junctions(story_id, out)

    def _display_junctions(self, story_id: str, out: IO[str]) -> None:
        sections = [
            # Heroes and NPCs merged (migration 17) — one junction, keyed on
            # character_id, reaches both, so one section lists both.
            ("Characters", "story_characters", "character_id", "characters", "character_id", "name"),
            (
                "Locations",
                "story_locations",
                "location_id",
                "locations",
                "location_id",
                "name",
            ),
            (
                "Regions",
                "story_regions",
                "region_id",
                "regions",
                "region_id",
                "region_name",
            ),
            (
                "Monsters",
                "story_monsters",
                "monster_id",
                "monsters",
                "monster_id",
                "name",
            ),
            ("Fauna", "story_fauna", "fauna_id", "fauna", "fauna_id", "name"),
            ("Flora", "story_flora", "flora_id", "flora", "flora_id", "name"),
            (
                "Food & Drink",
                "story_food_drink",
                "food_drink_id",
                "food_and_drink",
                "food_drink_id",
                "name",
            ),
            (
                "Weapons",
                "story_weapons",
                "canonical_weapon_id",
                "weapons_canonical",
                "canonical_weapon_id",
                "canonical_weapon",
            ),
            (
                "Equipment",
                "story_equipment",
                "canonical_equipment_id",
                "equipment_canonical",
                "canonical_equipment_id",
                "canonical_equipment",
            ),
        ]
        for label, junction, jid_col, registry, rid_col, name_col in sections:
            out.write(f"{label}\n")
            rows = self.conn.execute(
                f"SELECT r.{name_col} FROM {junction} j "
                f"JOIN {registry} r ON j.{jid_col} = r.{rid_col} "
                f"WHERE j.story_id = ? ORDER BY r.{name_col}",
                [story_id],
            ).fetchall()
            if rows:
                for r in rows:
                    out.write(f"  • {r[0]}\n")
            else:
                out.write("  (none)\n")
            out.write("\n")

    # ------------------------------------------------------------------
    # Description management
    # ------------------------------------------------------------------

    def update_description(self, entity_type: str, name: str, description: str) -> None:
        """Set or update the tooltip description for an entity.

        Args:
            entity_type: One of ``"monster"``, ``"fauna"``, ``"flora"``, ``"location"``,
                ``"group"``, ``"species"``, ``"title"`` or ``"profession"``.
            name: Display name of the entity (must already exist in the database).
            description: Short lore summary. ``"location"``, ``"group"``,
                ``"species"``, ``"title"`` and ``"profession"`` set the ``notes``
                field; the others set ``description``.

        A group must already have a row before its summary can land here, and a row
        is only created by a story declaration naming it. Six catalogue constants
        have no row yet for exactly that reason, so re-point the declaration before
        adding the note rather than the other way round.

        A species row is created by an NPC carrying it, with one deliberate
        exception: ``species.csv`` is a registry seeded on its own, so ``Chanek``
        keeps a row although no NPC is one yet. A profession row is created the
        same way species is — by a character carrying it, through
        ``NPCEntry(professions=…)`` — with no ``Chanek``-style exception, since
        nothing has attested a profession with no one holding it yet.

        Raises:
            ValueError: If ``entity_type`` is unrecognised or the named entity does not exist.
        """
        _TABLE_MAP = {
            "monster": ("monsters", "monster_id", _monster_id),
            "fauna": ("fauna", "fauna_id", fauna_id_from_name),
            "flora": ("flora", "flora_id", flora_id),
        }
        with self.conn:
            if entity_type == "location":
                rows = q.update_location_notes(self.conn, name, description)
                if rows == 0:
                    raise ValueError(f"Location not found: {name!r}")
            elif entity_type == "group":
                rows = q.update_group_notes(self.conn, _group_id(name), description)
                if rows == 0:
                    raise ValueError(f"Group not found: {name!r}")
            elif entity_type == "species":
                rows = q.update_species_notes(self.conn, _species_id(name), description)
                if rows == 0:
                    raise ValueError(f"Species not found: {name!r}")
            elif entity_type == "character":
                rows = q.update_character_summary(self.conn, lore_character_id(name), description)
                if rows == 0:
                    raise ValueError(f"Character not found: {name!r}")
            elif entity_type == "title":
                rows = q.update_title_notes(self.conn, _title_id(name), description)
                if rows == 0:
                    raise ValueError(f"Title not found: {name!r}")
            elif entity_type == "profession":
                rows = q.update_profession_notes(self.conn, _profession_id(name), description)
                if rows == 0:
                    raise ValueError(f"Profession not found: {name!r}")
            elif entity_type in _TABLE_MAP:
                table, id_col, id_fn = _TABLE_MAP[entity_type]
                entity_id = id_fn(name)
                rows = q.update_entity_description(self.conn, table, id_col, entity_id, description)
                if rows == 0:
                    raise ValueError(f"{entity_type.capitalize()} not found: {name!r}")
            else:
                raise ValueError(
                    f"Unknown entity type: {entity_type!r}. "
                    "Use 'monster', 'fauna', 'flora', 'location', 'group', 'species', "
                    "'title', 'profession' or 'character'."
                )
        _export.export_registry_tables(self.conn, self._data_dir)

    def set_location_parent(self, name: str, parent_name: str) -> None:
        """Record that ``name`` sits *inside* ``parent_name`` (R7).

        Containment is a property of the place, not of any page that mentions it,
        so it is written here — by name, over whatever is already in the database —
        rather than from a story declaration. ``LocationEntry.parent`` exists and
        works, but a declaration only runs for a location some story names, and
        five of the nineteen reviewed containments involve places no declaration
        touches. Same split as ``notes``: the field exists on the entry class, and
        ``descriptions.py`` owns the column.

        **Containment only.** Proximity is not containment — "area next to
        Candlehold" deliberately says *not in* Candlehold — and stays prose in
        ``notes``. The two are indistinguishable in the data, so the split was
        made by review, not by rule: see ``plans/location-containment-review.csv``.

        Args:
            name: Display name of the enclosed location. Must already exist.
            parent_name: Display name of the enclosing location. Must already exist.

        Raises:
            ValueError: If either location is missing, if they are the same row,
                or if the link would close a cycle.
        """

        def _one(label: str, wanted: str):
            ids = q.select_location_ids_by_name(self.conn, wanted)
            if not ids:
                raise ValueError(f"{label} not found: {wanted!r}")
            if len(ids) > 1:
                raise ValueError(f"{label} {wanted!r} matches {len(ids)} rows; resolve the duplicate first")
            return q.select_location_by_id(self.conn, ids[0])

        child = _one("Location", name)
        parent = _one("Parent location", parent_name)
        if child["location_id"] == parent["location_id"]:
            raise ValueError(f"A location cannot contain itself: {name!r}")

        # Walk up from the proposed parent; meeting the child means a cycle.
        seen, node = {child["location_id"]}, parent
        while node is not None:
            if node["location_id"] in seen and node["location_id"] != parent["location_id"]:
                break
            if node["parent_location_id"] == child["location_id"]:
                raise ValueError(f"Containment cycle: {parent_name!r} is already inside {name!r}")
            seen.add(node["location_id"])
            nxt = node["parent_location_id"]
            node = q.select_location_by_id(self.conn, nxt) if nxt else None

        with self.conn:
            q.set_parent(
                self.conn,
                "locations",
                "location_id",
                "parent_location_id",
                child["location_id"],
                parent["location_id"],
            )
        _export.export_registry_tables(self.conn, self._data_dir)

    def delete_entity(self, entity_type: str, name: str) -> None:
        """Delete a lore registry row by name, refusing if any story still links it.

        For cleaning up orphaned duplicate rows (e.g. a misspelled name left
        behind after a story's ``upsert_story()`` call was corrected to the
        right spelling). Never repoints links itself — link the story to the
        surviving row first (re-run ``upsert_story()`` with the corrected
        name), confirm the duplicate has zero story references, then call
        this to remove it.

        The common case for ``"npc"`` is a character promoted to a playable
        hero: dropping their :class:`NPCEntry` removes the story *link* but
        leaves the registry row behind, and the orphan survives every export.

        Args:
            entity_type: One of ``"monster"``, ``"fauna"``, ``"flora"``,
                ``"npc"``, or ``"location"``.
            name: Display name of the entity to delete.

        Raises:
            ValueError: If ``entity_type`` is unrecognised, no row matches
                ``name``, or the entity is still referenced by any story
                (listed junction tables and counts are included in the
                message so the caller knows what to repoint first).
        """
        _JUNCTION_MAP = {
            "monster": ("monsters", "monster_id", "story_monsters", _monster_id),
            "fauna": ("fauna", "fauna_id", "story_fauna", fauna_id_from_name),
            "flora": ("flora", "flora_id", "story_flora", flora_id),
            "npc": ("characters", "character_id", "story_characters", lore_character_id),
        }
        with self.conn:
            if entity_type == "location":
                entity_ids = q.select_location_ids_by_name(self.conn, name)
                if not entity_ids:
                    raise ValueError(f"Location not found: {name!r}")
                linked = {
                    eid: q.count_entity_story_links(self.conn, "story_locations", "location_id", eid)
                    for eid in entity_ids
                }
                still_linked = {eid: n for eid, n in linked.items() if n > 0}
                if still_linked:
                    raise ValueError(
                        f"Cannot delete location {name!r}: still referenced by story_locations "
                        f"(location_id -> story count: {still_linked}). Repoint those story links "
                        "to the row you're keeping first."
                    )
                for eid in entity_ids:
                    q.delete_entity_row(self.conn, "locations", "location_id", eid)
            elif entity_type in _JUNCTION_MAP:
                table, id_col, junction_table, id_fn = _JUNCTION_MAP[entity_type]
                entity_id = id_fn(name)
                linked = q.count_entity_story_links(self.conn, junction_table, id_col, entity_id)
                if linked:
                    raise ValueError(
                        f"Cannot delete {entity_type} {name!r}: still referenced by "
                        f"{linked} row(s) in {junction_table}. Repoint those story links first."
                    )
                rows = q.delete_entity_row(self.conn, table, id_col, entity_id)
                if rows == 0:
                    raise ValueError(f"{entity_type.capitalize()} not found: {name!r}")
            else:
                raise ValueError(
                    f"Unknown entity type: {entity_type!r}. " "Use 'monster', 'fauna', 'flora', 'npc', or 'location'."
                )
        _export.export_registry_tables(self.conn, self._data_dir)

    # ------------------------------------------------------------------
    # Export / dump
    # ------------------------------------------------------------------

    def export_to_csv(self, data_dir: Path | None = None) -> None:
        """Regenerate all CSV files in ``data_dir/csv/`` from the database."""
        _export.export_all(self.conn, data_dir or self._data_dir)

    def dump_to_json(self, out_dir: Path) -> None:
        """Write one ``<table>.json`` per table into ``out_dir``."""
        _export.dump_to_json(self.conn, out_dir)

    # ------------------------------------------------------------------
    # Internal entity resolution / upsert helpers
    # ------------------------------------------------------------------

    def _resolve_heroes(self, slugs: list[str]) -> list[str]:
        ids: list[str] = []
        for slug in slugs:
            row = q.select_hero_by_slug(self.conn, slug.strip())
            if row is None:
                known = ", ".join(r["slug"] for r in self.list_heroes()[:20])
                raise ValueError(
                    f"Unknown hero canonical slug: {slug!r}. "
                    f"Call db.print_heroes() to see available slugs. "
                    f"First 20: {known}"
                )
            ids.append(row["canonical_id"])
        return ids

    def _resolve_weapons(self, slugs: list[str]) -> list[str]:
        ids: list[str] = []
        for slug in slugs:
            row = q.select_weapon_by_slug(self.conn, slug.strip())
            if row is None:
                raise ValueError(
                    f"Unknown weapon canonical slug: {slug!r}. " "Call db.print_weapons() to see available slugs."
                )
            ids.append(row["canonical_weapon_id"])
        return ids

    def _resolve_equipment(self, slugs: list[str]) -> list[str]:
        ids: list[str] = []
        for slug in slugs:
            row = q.select_equipment_by_slug(self.conn, slug.strip())
            if row is None:
                raise ValueError(
                    f"Unknown equipment canonical slug: {slug!r}. " "Call db.print_equipment() to see available slugs."
                )
            ids.append(row["canonical_equipment_id"])
        return ids

    def _validate_fragments(
        self,
        story_key: str,
        characters: "list[NPCEntry | str] | None",
        frags: dict[str, str],
    ) -> None:
        """Validate ``fragments={key: anchor}`` before any write.

        A key must match exactly one of: a hero slug or an NPC display name
        declared in *this* call's ``characters=`` — ``characters=None``
        declares no one, so every key raises in that case. Raises on a key
        matching both a slug and an NPC name (ambiguous) or neither (typo, or
        naming someone not declared this call). Every non-empty anchor is then
        checked against the real headings on the story's page, as before.
        """
        if not frags:
            return
        hero_slugs = {c for c in (characters or []) if isinstance(c, str)}
        npc_names = {c.name for c in (characters or []) if not isinstance(c, str)}
        for key in frags:
            in_hero = key in hero_slugs
            in_npc = key in npc_names
            if in_hero and in_npc:
                raise ValueError(
                    f"fragments key {key!r} names both a declared hero slug and a declared NPC "
                    f"for {story_key!r}; give the NPC a different display name or drop one "
                    "declaration."
                )
            if not in_hero and not in_npc:
                raise ValueError(
                    f"fragments key {key!r} matches no hero slug or NPC name declared for "
                    f"{story_key!r} in this call."
                )

        md_path = (SRC / story_key).resolve()
        if not md_path.is_file():
            return
        ids_on_page: set[str] | None = None
        for key, frag in frags.items():
            if not frag:
                continue
            if ids_on_page is None:
                ids_on_page = collect_heading_anchor_ids_from_path(md_path)
            if frag not in ids_on_page:
                rel = md_path.relative_to(SRC).as_posix()
                raise ValueError(
                    f"Fragment {frag!r} for {key!r} not found in {rel}. "
                    f"Known ids: {format_fragment_suggestion(ids_on_page)}"
                )

    def _upsert_npcs(self, entries: list[NPCEntry], _seen: "frozenset[str]" = frozenset()) -> list[str]:
        # Guard against accidentally storing playable heroes as NPCs — unless the
        # entry itself claims the identity via hero_slug (NPCEntry.hero_slug),
        # which is the NPC saying "yes, I know, I am that hero".
        hero_names: set[str] = {normalize_name(r["canonical_hero"]) for r in q.select_all_heroes_canonical(self.conn)}
        ids: list[tuple[str, str]] = []
        seen_slugs: dict[str, str] = {}
        for e in entries:
            norm = normalize_name(e.name)
            if norm in hero_names and not e.hero_slug:
                raise ValueError(f"Refusing NPC link for playable hero name: {e.name!r}")
            cid = lore_character_id(e.name)
            q.upsert_npc(
                self.conn,
                character_id=cid,
                name=e.name,
                status=e.status,
                other_characters_story_key=e.other_characters_story_key,
            )
            # Replace-semantic and unconditional, like the group rosters. The
            # catalogue is the single definition of an NPC, so an empty tuple is a
            # declaration that this character answers to no other name.
            q.set_npc_epithets(
                self.conn,
                cid,
                [(n, "epithet") for n in e.epithets] + [(n, "short-name") for n in e.short_names],
            )
            q.set_npc_species(self.conn, cid, self._upsert_species(_species_tuple(e.species)))
            # Professions (R9). Resolves and raises on a repeated profession
            # before any downstream write — mirrors kin's use of
            # _resolve_kin_relatives just below.
            q.set_character_professions(
                self.conn, cid, self._upsert_professions(e.name, _professions_tuple(e.professions))
            )
            if e.hero_slug:
                # Same shape as the guard in GroupEntry.member_pairs(): the write
                # (character_heroes.canonical_id is the primary key, so it would
                # keep the first) and a preview that reported the last would
                # otherwise resolve a doubled claim two different ways, and
                # neither would raise. Guarded here so both fail the same way.
                if e.hero_slug in seen_slugs:
                    raise ValueError(
                        f"hero_slug {e.hero_slug!r} claimed by both {seen_slugs[e.hero_slug]!r} and "
                        f"{e.name!r}. An identity claim is one row; give the hero only one NPC."
                    )
                seen_slugs[e.hero_slug] = e.name
                canonical_id = self._resolve_heroes([e.hero_slug])[0]
                q.set_character_hero(self.conn, canonical_id, cid)

            # Kin (R8). Resolves and raises before any downstream write —
            # mirrors _upsert_one_title's use of _resolve_title_holders.
            resolved_kin = self._resolve_kin_relatives(e)

            if e.name not in _seen:
                # NPC relatives named in .kin need a character row of their own
                # before character_kin.relative_id can reference them — mirrors
                # the group roster's / title holder's _upsert_npcs call.
                #
                # Guarded by _seen (this recursion's own visited set, not a
                # cross-call cache) so two people who each name the other as
                # kin — siblings, spouses — do not recurse forever. That is
                # ordinary domain data, not a cycle error, unlike a location's
                # or group's parent chain, so it is skipped rather than raised.
                next_seen = _seen | {e.name}
                kin_relatives = [
                    relative
                    for relative, _relation, _story_key in (_kin_triple(item) for item in e.kin)
                    if not isinstance(relative, str)
                ]
                if kin_relatives:
                    self._upsert_npcs(kin_relatives, next_seen)
                # Hero-slug relatives need a character_heroes row too. An
                # existing link always wins; this only fills a gap — the same
                # INSERT-OR-IGNORE contract _self_heal_character_heroes uses at
                # seed time, mirroring _upsert_one_title's hero holder block.
                for relative, _relation, _story_key in (_kin_triple(item) for item in e.kin):
                    if isinstance(relative, str):
                        canonical_id = self._resolve_heroes([relative])[0]
                        if not q.select_character_id_for_hero(self.conn, canonical_id):
                            row = self.conn.execute(
                                "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
                                [canonical_id],
                            ).fetchone()
                            hero_name = row["canonical_hero"] if row else ""
                            new_cid = lore_character_id(hero_name)
                            q.upsert_npc(self.conn, character_id=new_cid, name=hero_name)
                            q.set_character_hero(self.conn, canonical_id, new_cid)

            q.set_character_kin(
                self.conn,
                cid,
                [(rid, relation, story_key) for rid, relation, story_key, _origin in resolved_kin],
            )
            ids.append(cid)
        return ids

    def _resolve_characters(
        self, story_key: str, characters: "list[NPCEntry | str]"
    ) -> "list[tuple[str, str, NPCEntry | str]]":
        """Resolve ``characters=`` to ``(character_id, origin, item)`` triples, read-only.

        Read-only, so the dry-run preview can call this too — mirrors
        :meth:`_resolve_kin_relatives` and :meth:`_resolve_title_holders`. A
        slug resolves via :meth:`_predict_hero_character_id` (never
        :meth:`_ensure_hero_character_id`, which writes); an
        :class:`NPCEntry` resolves via a bare ``lore_character_id`` hash of
        its name.

        Raises:
            ValueError: for an unknown hero slug (via :meth:`_resolve_heroes`),
                or when the same person is named twice in this one list — as
                two slugs, two ``NPCEntry`` instances, or once each way —
                naming the story, both origins and the shared ``character_id``.
                A story used to be able to name one person through ``heroes=``
                and again through ``npcs=`` and have the two collapse into one
                row; that only worked because they were two lists with
                different jobs. Within one ``characters=`` list a repeat is a
                mistake, the same shape ``GroupEntry.member_pairs()`` and
                ``_resolve_title_holders`` guard against for a repeated member.
        """
        resolved: list[tuple[str, str, "NPCEntry | str"]] = []
        seen: dict[str, str] = {}
        for item in characters:
            if isinstance(item, str):
                canonical_id = self._resolve_heroes([item])[0]
                cid = self._predict_hero_character_id(canonical_id)
                origin = f"hero {item!r}"
            else:
                cid = lore_character_id(item.name)
                origin = f"NPC {item.name!r}"
            if cid in seen:
                raise ValueError(
                    f"{story_key!r} names {seen[cid]} and {origin} in characters=, but both "
                    f"resolve to the same person (character_id {cid!r}). A story link is one "
                    "row; name this person once."
                )
            seen[cid] = origin
            resolved.append((cid, origin, item))
        return resolved

    def _write_story_characters(
        self,
        story_id: str,
        story_key: str,
        characters: "list[NPCEntry | str]",
        frags: dict[str, str],
    ) -> None:
        """Write ``characters=`` into the ``story_characters`` junction.

        Plain replace-semantic junction parameter, like every other one: the
        stored set becomes exactly this list. A slug resolves through
        ``character_heroes`` to a ``character_id``, minting the identity link
        if this is the first time the hero has one
        (:meth:`_ensure_hero_character_id`); an :class:`NPCEntry` resolves
        through :meth:`_upsert_npcs`. Both land in the same
        ``story_characters`` row.

        :meth:`_resolve_characters` raises before any write here if the same
        person is named twice — once as a slug and once as an
        :class:`NPCEntry`, or twice the same way — naming the story, both
        origins and the shared ``character_id``.
        """
        self._resolve_characters(story_key, characters)

        npc_items = [c for c in characters if not isinstance(c, str)]
        npc_ids = dict(zip((e.name for e in npc_items), self._upsert_npcs(npc_items)))

        merged: dict[str, str] = {}
        for item in characters:
            if isinstance(item, str):
                canonical_id = self._resolve_heroes([item])[0]
                cid = self._ensure_hero_character_id(canonical_id)
                merged[cid] = frags.get(item, "")
            else:
                cid = npc_ids[item.name]
                merged[cid] = frags.get(item.name, "")

        q.set_story_characters(self.conn, story_id, list(merged.items()))

    def _upsert_species(self, entries: "tuple[SpeciesEntry, ...]") -> list[str]:
        """Upsert each species row and return its ids, in declared order."""
        ids: list[str] = []
        for e in entries:
            sid = _species_id(e.name)
            q.upsert_species(self.conn, species_id=sid, name=e.name)
            q.set_species_aliases(self.conn, sid, list(e.aliases))
            ids.append(sid)
        return ids

    def _resolve_professions(self, owner_name: str, entries: "tuple[ProfessionEntry, ...]") -> list[tuple[str, str]]:
        """Resolve a tuple of :class:`ProfessionEntry` to ``(profession_id, name)`` pairs.

        Read-only, so the dry-run preview can call this too — mirrors
        :meth:`_resolve_kin_relatives` and :meth:`_resolve_title_holders`.
        Unlike ``species`` (which never guards a repeat — ``INSERT OR IGNORE``
        just collapses it in silence), a profession raises on a repeat within
        ``entries``, the same guard shape ``GroupEntry.member_pairs()``,
        ``_resolve_title_holders`` and ``_resolve_kin_relatives`` all use: two
        entries naming the same profession would otherwise resolve differently
        on the write path (``INSERT OR IGNORE`` keeps the first) than on a
        preview that diffed a dict (last wins).

        Args:
            owner_name: The character or hero slug this tuple belongs to, named
                in the error.
            entries: The tuple to resolve, already normalised by
                :func:`_professions_tuple`.

        Raises:
            ValueError: if two entries resolve to the same ``profession_id``.
        """
        resolved: list[tuple[str, str]] = []
        seen: dict[str, str] = {}
        for p in entries:
            pid = _profession_id(p.name)
            if pid in seen:
                raise ValueError(
                    f"{owner_name!r} names profession {p.name!r} twice "
                    f"(as {seen[pid]!r} and {p.name!r}). A profession claim is one row; state it once."
                )
            seen[pid] = p.name
            resolved.append((pid, p.name))
        return resolved

    def _upsert_professions(self, owner_name: str, entries: "tuple[ProfessionEntry, ...]") -> list[str]:
        """Upsert each profession row and return its ids, in declared order.

        Raises before writing anything if two entries in ``entries`` name the
        same profession — see :meth:`_resolve_professions`, which this calls
        first.
        """
        resolved = self._resolve_professions(owner_name, entries)
        for pid, name in resolved:
            q.upsert_profession(self.conn, profession_id=pid, name=name)
        return [pid for pid, _name in resolved]

    def _upsert_regions(self, entries: list[RegionEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            rid = region_row_id(e.name)
            wk = e.world_of_rathe_story_key or _auto_world_key(e.name)
            q.upsert_region(
                self.conn,
                region_id=rid,
                region_name=e.name,
                world_of_rathe_story_key=wk,
            )
            ids.append(rid)
        return ids

    def _upsert_locations(self, entries: list[LocationEntry], _seen: tuple[str, ...] = ()) -> list[str]:
        ids: list[str] = []
        for e in entries:
            eff_region = ""
            if e.region:
                eff_region = region_row_id(e.region)
                wk = e.world_of_rathe_story_key or _auto_world_key(e.region)
                q.upsert_region(
                    self.conn,
                    region_id=eff_region,
                    region_name=e.region,
                    world_of_rathe_story_key=wk,
                )
            elif not e.region and not q.region_id_exists(self.conn, ""):
                eff_region = ""

            # Validate lore_fragment against on-disk headings
            frag = e.lore_fragment.strip().lstrip("#")
            if frag and eff_region:
                region_row = q.select_region_by_id(self.conn, eff_region)
                wk = (region_row["world_of_rathe_story_key"] if region_row else "") or ""
                if wk:
                    md_path = (SRC / Path(wk)).resolve()
                    if md_path.is_file():
                        ids_on_page = collect_heading_anchor_ids_from_path(md_path)
                        if frag not in ids_on_page:
                            rel = md_path.relative_to(SRC).as_posix()
                            raise ValueError(
                                f"LoreFragment {frag!r} not found in {rel}. "
                                f"Known ids: {format_fragment_suggestion(ids_on_page)}"
                            )

            lid = _location_id(e.name, eff_region)
            if lid in _seen:
                raise ValueError(f"Cycle in LocationEntry.parent involving {e.name!r}")
            parent_id = ""
            if e.parent is not None:
                parent_id = self._upsert_locations([e.parent], (*_seen, lid))[0]
            q.upsert_location(
                self.conn,
                location_id=lid,
                name=e.name,
                region_id=eff_region,
                notes=e.notes,
                lore_fragment=frag,
                parent_location_id=parent_id,
            )
            q.set_location_aliases(self.conn, lid, [_alias_pair(a) for a in e.aliases])
            ids.append(lid)
        return ids

    def _upsert_monsters(self, entries: list[MonsterEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            mid = _monster_id(e.name)
            q.upsert_monster(self.conn, monster_id=mid, name=e.name, description=e.description)
            ids.append(mid)
        return ids

    def _upsert_fauna(self, entries: list[FaunaEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            fid = fauna_id_from_name(e.name)
            q.upsert_fauna(self.conn, fauna_id=fid, name=e.name, description=e.description)
            ids.append(fid)
        return ids

    def _upsert_flora(self, entries: list[FloraEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            fid = flora_id(e.name)
            q.upsert_flora(self.conn, flora_id=fid, name=e.name, description=e.description)
            ids.append(fid)
        return ids

    def _upsert_groups(self, entries: list[GroupEntry]) -> list[str]:
        """Upsert each group, its parent chain, its location and its roster.

        Returns the ids in call order. Parents are written first so the foreign
        key always resolves; a cycle in ``parent`` raises rather than looping.
        """
        ids: list[str] = []
        for e in entries:
            ids.append(self._upsert_one_group(e))
        return ids

    def _upsert_one_group(self, entry: GroupEntry, _seen: tuple[str, ...] = ()) -> str:
        gid = _group_id(entry.name)
        if gid in _seen:
            chain = " -> ".join([*_seen, entry.name])
            raise ValueError(f"Cycle in GroupEntry.parent: {chain}")

        parent_id = ""
        if entry.parent is not None:
            parent_id = self._upsert_one_group(entry.parent, (*_seen, gid))

        loc_id = ""
        if entry.location is not None:
            loc_id = self._upsert_locations([entry.location])[0]

        q.upsert_group(
            self.conn,
            group_id=gid,
            name=entry.name,
            kind=entry.kind,
            parent_group_id=parent_id,
            location_id=loc_id,
            lore_story_key=entry.lore_story_key,
            lore_fragment=entry.lore_fragment,
        )

        # Unconditional. ``set_group_members`` is replace-semantic — it deletes
        # the stored rows before inserting — and an emptied roster is a deletion
        # the declaration asked for, not a no-op. Guarding this call on a truthy
        # roster made an emptied one silently keep its rows while the dry run
        # went on printing a REMOVED line for them.
        #
        # Raises on a person named twice before anything is written.
        resolved = self._resolve_group_members(entry)

        # NPC member rows must exist before group_characters.character_id can
        # reference them; a hero member's row is minted by
        # _ensure_hero_character_id inside the resolver. Mirrors the title
        # holder's _upsert_npcs call.
        self._upsert_npcs([person for person, _source in entry.member_pairs() if not isinstance(person, str)])

        q.set_group_members(
            self.conn,
            gid,
            "group_characters",
            "character_id",
            [(cid, source) for cid, source, _origin in resolved],
        )
        q.set_group_aliases(self.conn, gid, list(entry.aliases))
        return gid

    def _resolve_group_members(self, entry: GroupEntry) -> list[tuple[str, str, str]]:
        """Resolve every roster member to ``(character_id, story_key, origin)``.

        Writes only the identity link a hero member needs
        (:meth:`_ensure_hero_character_id`); the NPC rows themselves are
        upserted by the caller. :meth:`_dry_run_group_members` is the read-only
        twin the preview uses.

        Raises:
            ValueError: when two members resolve to the same ``character_id`` —
                the clash :meth:`GroupEntry.member_pairs` cannot see, because a
                hero slug and an :class:`NPCEntry` naming one person only
                collide once ``character_heroes`` joins them. Same guard shape
                as :meth:`_resolve_characters` and :meth:`_resolve_title_holders`.
        """
        resolved: list[tuple[str, str, str]] = []
        seen: dict[str, str] = {}
        for person, source in entry.member_pairs():
            if isinstance(person, str):
                cid = self._ensure_hero_character_id(self._resolve_heroes([person])[0])
                origin = f"hero {person!r}"
            else:
                cid = lore_character_id(person.name)
                origin = f"NPC {person.name!r}"
            if cid in seen:
                raise ValueError(
                    f"{entry.name!r} names {seen[cid]} and {origin} in members, but both "
                    f"resolve to the same person (character_id {cid!r}). A membership is "
                    "one row; name this person once."
                )
            seen[cid] = origin
            resolved.append((cid, source, origin))
        return resolved

    def _dry_run_group_members(self, entry: GroupEntry) -> list[tuple[str, str, str]]:
        """Read-only twin of :meth:`_resolve_group_members`, for the preview.

        Identical except that a hero member resolves through
        :meth:`_predict_hero_character_id`, which reads, rather than
        :meth:`_ensure_hero_character_id`, which mints. The two agree on every
        input: both return the stored ``character_heroes`` link when there is
        one and the ``lore_character_id`` hash of the canonical hero name when
        there is not, which is precisely the id the write path would mint. Same
        split ``_resolve_characters`` uses for ``characters=``.
        """
        resolved: list[tuple[str, str, str]] = []
        seen: dict[str, str] = {}
        for person, source in entry.member_pairs():
            if isinstance(person, str):
                cid = self._predict_hero_character_id(self._resolve_heroes([person])[0])
                origin = f"hero {person!r}"
            else:
                cid = lore_character_id(person.name)
                origin = f"NPC {person.name!r}"
            if cid in seen:
                raise ValueError(
                    f"{entry.name!r} names {seen[cid]} and {origin} in members, but both "
                    f"resolve to the same person (character_id {cid!r}). A membership is "
                    "one row; name this person once."
                )
            seen[cid] = origin
            resolved.append((cid, source, origin))
        return resolved

    def _predict_hero_character_id(self, canonical_id: str) -> str:
        """Return the ``character_id`` a hero resolves to via ``character_heroes``.

        Reads only. When no ``character_heroes`` row exists yet, predicts the id
        self-healing would mint at seed time — ``lore_character_id`` of the
        hero's ``canonical_hero`` name — without writing anything, so a dry run
        can preview a hero holder before any row for them exists.
        """
        existing = q.select_character_id_for_hero(self.conn, canonical_id)
        if existing:
            return existing
        row = self.conn.execute(
            "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
            [canonical_id],
        ).fetchone()
        hero_name = row["canonical_hero"] if row else ""
        return lore_character_id(hero_name)

    def _ensure_hero_character_id(self, canonical_id: str) -> str:
        """Return the ``character_id`` a hero resolves to, minting the identity link if missing.

        Writes, unlike :meth:`_predict_hero_character_id`: mirrors
        ``_upsert_one_title``'s hero-holder gap-fill and
        ``_self_heal_character_heroes``'s seed-time contract — INSERT OR IGNORE
        throughout, so an existing ``character_heroes`` row always wins and this
        only ever fills a gap. Called from ``upsert_story``'s ``characters=``
        write path (:meth:`_write_story_characters`) so a hero named for the
        first time still gets a ``characters`` row for ``story_characters``
        to reference.
        """
        existing = q.select_character_id_for_hero(self.conn, canonical_id)
        if existing:
            return existing
        row = self.conn.execute(
            "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
            [canonical_id],
        ).fetchone()
        hero_name = row["canonical_hero"] if row else ""
        new_cid = lore_character_id(hero_name)
        q.upsert_npc(self.conn, character_id=new_cid, name=hero_name)
        q.set_character_hero(self.conn, canonical_id, new_cid)
        return new_cid

    def _resolve_kin_relatives(self, entry: NPCEntry) -> list[tuple[str, str, str, str]]:
        """Resolve every kin fact on ``entry`` to ``(relative_id, relation, story_key, origin)``.

        Read-only, so the dry-run preview can call this too — mirrors
        :meth:`_resolve_title_holders`. A relative may be named as an
        :class:`NPCEntry` or a hero slug, and migration 12's identity spine
        means both can resolve to the same ``character_id``, so the same
        person named twice under the same relation, once each way, must be
        caught as a repeat before either write happens. Keyed on
        ``(relative_id, relation)`` rather than ``relative_id`` alone, because
        ``character_kin`` is keyed on all three columns — unlike
        ``title_holders``, the same relative legitimately appears twice under
        two different relations.

        Raises:
            ValueError: for a repeated ``(relative_id, relation)`` pair, an
                unknown hero slug (via :meth:`_resolve_heroes`), a character
                named as their own relative, or a relation outside
                :data:`~db._queries.KIN_INVERSE`.

        The relation is checked *here*, unlike ``status`` and
        ``npc_epithets.kind``, which are left to ``validate_data.py``. Those
        two are only ever read back as text, so a typo is a wrong label until
        the next hook run. ``relation`` is different: it is used as a key into
        ``KIN_INVERSE`` to derive the other end of the fact, so a bad value
        raises ``KeyError`` inside a query — during an ``mdbook build``, long
        before a pre-commit hook would see the CSV. The vocabulary is
        ``KIN_INVERSE``'s own keys rather than a second list, so the check and
        the derivation cannot disagree.
        """
        own_cid = lore_character_id(entry.name)
        resolved: list[tuple[str, str, str, str]] = []
        seen: dict[tuple[str, str], str] = {}
        for item in entry.kin:
            relative, relation, story_key = _kin_triple(item)
            if relation not in q.KIN_INVERSE:
                raise ValueError(
                    f"{entry.name!r} states an unknown kin relation {relation!r}. "
                    f"Use one of {sorted(q.KIN_INVERSE)}."
                )
            if isinstance(relative, str):
                canonical_id = self._resolve_heroes([relative])[0]
                rid = self._predict_hero_character_id(canonical_id)
                origin = f"hero_slug {relative!r}"
            else:
                rid = lore_character_id(relative.name)
                origin = relative.name
            if rid == own_cid:
                raise ValueError(
                    f"{entry.name!r} cannot be their own relative (named as {origin}, relation {relation!r})"
                )
            key = (rid, relation)
            if key in seen:
                raise ValueError(
                    f"{entry.name!r} names {seen[key]!r} and {origin} as {relation!r} twice "
                    f"(character_id {rid!r}). A kin fact is one row; state it once."
                )
            seen[key] = origin
            resolved.append((rid, relation, story_key, origin))
        return resolved

    def _resolve_title_holders(self, entry: TitleEntry) -> list[tuple[str, int, str, str]]:
        """Resolve every holder to ``(character_id, ordinal, story_key, origin)``.

        Read-only, so the dry-run preview can call this too. Raises when two
        holders resolve to the same ``character_id`` — ``title_holders`` is keyed
        ``(title_id, character_id)``, the same hazard ``GroupEntry.member_pairs()``
        guards for a repeated NPC, extended here to a person named once as an NPC
        and once as a hero slug: the case migration 12's identity spine makes
        reachable, since both now resolve into the same ``characters`` row.
        """
        resolved: list[tuple[str, int, str, str]] = []
        seen: dict[str, str] = {}
        for npc_entry, ordinal, story_key in entry.npc_holders:
            cid = lore_character_id(npc_entry.name)
            origin = npc_entry.name
            if cid in seen:
                raise ValueError(
                    f"{entry.name!r} names {seen[cid]!r} and {origin!r} as the same title holder "
                    f"(character_id {cid!r}). A holder is one row; give this person one entry."
                )
            seen[cid] = origin
            resolved.append((cid, ordinal, story_key, origin))
        for slug, ordinal, story_key in entry.hero_holders:
            canonical_id = self._resolve_heroes([slug])[0]
            cid = self._predict_hero_character_id(canonical_id)
            origin = f"hero_slug {slug!r}"
            if cid in seen:
                raise ValueError(
                    f"{entry.name!r} names {seen[cid]!r} and {origin} as the same title holder "
                    f"(character_id {cid!r}). A holder is one row; give this person one entry."
                )
            seen[cid] = origin
            resolved.append((cid, ordinal, story_key, origin))
        return resolved

    def _upsert_titles(self, entries: list[TitleEntry]) -> list[str]:
        """Upsert each title, its group and its holders. Returns ids in call order."""
        return [self._upsert_one_title(e) for e in entries]

    def _upsert_one_title(self, entry: TitleEntry) -> str:
        tid = _title_id(entry.name)

        group_id_val = ""
        if entry.group is not None:
            group_id_val = self._upsert_one_group(entry.group)

        q.upsert_title(self.conn, title_id=tid, name=entry.name, group_id=group_id_val)

        # Raises on a repeated holder before anything downstream writes.
        resolved = self._resolve_title_holders(entry)

        # NPC holder rows must exist before title_holders.character_id can
        # reference them — mirrors the group roster's _upsert_npcs call.
        self._upsert_npcs([npc for npc, _ordinal, _source in entry.npc_holders])

        # Hero holder rows must exist too. An existing character_heroes link
        # always wins; this only fills a gap, the same INSERT-OR-IGNORE
        # contract _self_heal_character_heroes uses at seed time — so a title
        # naming a hero with no character row yet still resolves cleanly.
        for slug, _ordinal, _source in entry.hero_holders:
            canonical_id = self._resolve_heroes([slug])[0]
            if not q.select_character_id_for_hero(self.conn, canonical_id):
                row = self.conn.execute(
                    "SELECT canonical_hero FROM heroes_canonical WHERE canonical_id = ?",
                    [canonical_id],
                ).fetchone()
                hero_name = row["canonical_hero"] if row else ""
                new_cid = lore_character_id(hero_name)
                q.upsert_npc(self.conn, character_id=new_cid, name=hero_name)
                q.set_character_hero(self.conn, canonical_id, new_cid)

        q.set_title_holders(
            self.conn,
            tid,
            [(cid, ordinal, story_key) for cid, ordinal, story_key, _origin in resolved],
        )
        return tid

    def _upsert_food_drink(self, entries: list[FoodDrinkEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            fid = food_drink_id(e.name, e.kind)
            q.upsert_food_drink(self.conn, food_drink_id=fid, name=e.name, type_=e.kind)
            ids.append(fid)
        return ids

    def _load_record(self, story_id: str) -> StoryRecord:
        row = q.select_story_by_id(self.conn, story_id)
        if row is None:
            raise RuntimeError(f"Story disappeared after write: {story_id!r}")
        videos = q.select_narrated_videos(self.conn, story_id)
        return StoryRecord(
            story_id=row["story_id"],
            story_key=row["story_key"],
            story_type=row["story_type"],
            title=row["title"],
            authors=row["authors"],
            artists=row["artists"],
            source_link=row["source_link"],
            publication_date=row["publication_date"],
            thumbnail_image_link=row["thumbnail_image_link"],
            narrated_videos=[
                NarratedVideoEntry(
                    author=v["author"],
                    source_link=v["source_link"],
                    channel_link=v["channel_link"],
                )
                for v in videos
            ],
            _db=self,
        )

    # ------------------------------------------------------------------
    # dry_run helper
    # ------------------------------------------------------------------

    def _dry_run_upsert(
        self,
        *,
        story_key: str,
        story_id: str,
        story_type: str,
        title: str,
        authors: str,
        artists: str,
        source_link: str,
        publication_date: str,
        thumbnail_image_link: str,
        narrated_videos: list[NarratedVideoEntry] | None,
        characters: "list[NPCEntry | str] | None" = None,
        fragments: dict[str, str] | None = None,
        locations: list[LocationEntry] | None,
        regions: list[RegionEntry] | None,
        monsters: list[MonsterEntry] | None,
        fauna: list[FaunaEntry] | None,
        flora: list[FloraEntry] | None,
        food_drink: list[FoodDrinkEntry] | None,
        weapon_ids: list[str] | None,
        equip_ids: list[str] | None,
        groups: list[GroupEntry] | None = None,
        titles: list[TitleEntry] | None = None,
        file: IO[str] | None = None,
    ) -> StoryRecord:
        import sys as _sys

        out = file or _sys.stdout

        existing = q.select_story_by_key(self.conn, story_key)
        op = "UPDATE" if existing else "INSERT"

        # Recorded on the instance as last_dry_run_changed so a caller running
        # many declarations can tell a real diff from a no-op and stay silent
        # about the rest. An INSERT is a change by definition.
        changed = not existing
        self._last_dry_run_changed = changed

        out.write(f"DRY RUN — {op} story\n")
        out.write(f"  StoryKey: {story_key}\n")
        out.write(f"  StoryId:  {story_id}\n")

        scalar_fields: list[tuple[str, str, str]] = [
            ("title", "Title", title),
            ("story_type", "Type", story_type),
            ("authors", "Authors", authors),
            ("artists", "Artists", artists),
            ("publication_date", "Date", publication_date),
            ("source_link", "Source", source_link),
            ("thumbnail_image_link", "Thumb", thumbnail_image_link),
        ]

        if existing:
            added: list[str] = []
            removed: list[str] = []
            for db_col, label, new_val in scalar_fields:
                old_val = existing[db_col] or ""
                if old_val == new_val:
                    continue
                if old_val and not new_val:
                    removed.append(f"    - {label}: {old_val!r}")
                elif not old_val:
                    added.append(f"    + {label}: {new_val!r}")
                else:
                    added.append(f"    + {label}: {new_val!r}  (was: {old_val!r})")
            if added:
                changed = True
                out.write("  Added / changed:\n")
                out.write("\n".join(added) + "\n")
            if removed:
                changed = True
                out.write("  Cleared:\n")
                out.write("\n".join(removed) + "\n")
            if not added and not removed:
                out.write("  (story row: no scalar field changes)\n")
        else:
            for _, label, val in scalar_fields:
                if val:
                    out.write(f"  {label}: {val}\n")

        if narrated_videos is not None:
            # set_narrated_videos() deletes and re-inserts the whole set, so a bare
            # count reads identically for a no-op and for a total replacement.
            incoming_videos = [(v.author, v.source_link) for v in narrated_videos]
            stored_videos = (
                [(r["author"], r["source_link"]) for r in q.select_narrated_videos(self.conn, story_id)]
                if existing
                else []
            )
            if incoming_videos != stored_videos:
                changed = True
                out.write("  NarratedVideos:\n")
                for author, link in stored_videos:
                    if (author, link) not in incoming_videos:
                        out.write(f"    - {author} ({link})\n")
                for author, link in incoming_videos:
                    if (author, link) not in stored_videos:
                        out.write(f"    + {author} ({link})\n")
            else:
                out.write(f"  NarratedVideos: {len(narrated_videos)} entries (unchanged)\n")

        # Build id → display name maps so diffs show readable slugs/names
        hero_id_to_slug = {r["canonical_id"]: r["canonical_slug"] for r in q.select_all_heroes_canonical(self.conn)}
        weapon_id_to_slug = {
            r["canonical_weapon_id"]: r["canonical_slug"] for r in q.select_all_weapons_canonical(self.conn)
        }
        equip_id_to_slug = {
            r["canonical_equipment_id"]: r["canonical_slug"] for r in q.select_all_equipment_canonical(self.conn)
        }
        npc_rows = {r["character_id"]: r for r in q.select_all_npcs(self.conn)}
        monster_rows = {r["monster_id"]: r for r in q.select_all_monsters(self.conn)}
        fauna_rows = {r["fauna_id"]: r for r in q.select_all_fauna(self.conn)}
        flora_rows = {r["flora_id"]: r for r in q.select_all_flora(self.conn)}
        npc_id_to_name = {r["character_id"]: r["name"] for r in q.select_all_npcs(self.conn)}
        loc_id_to_name = {r["location_id"]: r["name"] for r in q.select_all_locations(self.conn)}
        region_id_to_name = {r["region_id"]: r["region_name"] for r in q.select_all_regions(self.conn)}
        monster_id_to_name = {r["monster_id"]: r["name"] for r in q.select_all_monsters(self.conn)}
        fauna_id_to_name = {r["fauna_id"]: r["name"] for r in q.select_all_fauna(self.conn)}
        flora_id_to_name = {r["flora_id"]: r["name"] for r in q.select_all_flora(self.conn)}
        food_id_to_name = {r["food_drink_id"]: r["name"] for r in q.select_all_food_drink(self.conn)}
        group_rows = {r["group_id"]: r for r in q.select_all_groups(self.conn)}
        group_id_to_name = {r["group_id"]: r["name"] for r in q.select_all_groups(self.conn)}
        title_rows = {r["title_id"]: r for r in q.select_all_titles(self.conn)}
        title_id_to_name = {r["title_id"]: r["name"] for r in q.select_all_titles(self.conn)}

        def _show_links_diff(
            label: str,
            incoming: list | None,
            incoming_names: list[str],
            junction_table: str,
            junction_id_col: str,
            id_to_name: dict[str, str],
        ) -> None:
            nonlocal changed
            if incoming is None:
                return  # None = leave unchanged
            incoming_set = set(incoming_names)
            if existing:
                existing_ids = q.select_story_junction(self.conn, story_id, junction_table, junction_id_col)
                existing_set = {id_to_name.get(eid, eid) for eid in existing_ids}
                link_added = sorted(incoming_set - existing_set)
                link_removed = sorted(existing_set - incoming_set)
                if link_added or link_removed:
                    changed = True
                    out.write(f"  {label}:\n")
                    for name in link_added:
                        out.write(f"    + {name}\n")
                    for name in link_removed:
                        out.write(f"    - {name}\n")
            else:
                if incoming_names:
                    out.write(f"  {label}:\n")
                    for name in sorted(incoming_names):
                        out.write(f"    + {name}\n")

        # Heroes and NPCs merged (migration 17) into one story_characters
        # junction, and stage 6b's heroes=/npcs= two-kwarg surface merged
        # (2026-08-22) into the one characters= list this mirrors. Plain
        # replace-semantic preview like every other junction: no partition,
        # nothing carried over from the old state. Read-only —
        # _resolve_characters calls _predict_hero_character_id and a bare
        # lore_character_id hash, never _ensure_hero_character_id /
        # _upsert_npcs, since a preview must not write. It also raises here,
        # before any diff below, if the same person is named twice.
        if characters is not None:
            old_char_state = q.select_story_character_fragments(self.conn, story_id) if existing else {}
            hero_id_to_hero_name = {
                r["canonical_id"]: r["canonical_hero"] for r in q.select_all_heroes_canonical(self.conn)
            }

            new_char_state: dict[str, str] = {}
            char_display_name: dict[str, str] = {}

            for cid, _origin, item in self._resolve_characters(story_key, characters):
                if isinstance(item, str):
                    canonical_id = self._resolve_heroes([item])[0]
                    new_char_state[cid] = (fragments or {}).get(item, "")
                    char_display_name[cid] = hero_id_to_hero_name.get(canonical_id, item)
                else:
                    new_char_state[cid] = (fragments or {}).get(item.name, "")
                    char_display_name[cid] = item.name

            old_char_names = {npc_id_to_name.get(cid, cid) for cid in old_char_state}
            new_char_names = {char_display_name.get(cid, npc_id_to_name.get(cid, cid)) for cid in new_char_state}
            if existing:
                added = sorted(new_char_names - old_char_names)
                removed = sorted(old_char_names - new_char_names)
                if added or removed:
                    changed = True
                    out.write("  Characters:\n")
                    for name in added:
                        out.write(f"    + {name}\n")
                    for name in removed:
                        out.write(f"    - {name}\n")
            elif new_char_names:
                out.write("  Characters:\n")
                for name in sorted(new_char_names):
                    out.write(f"    + {name}\n")

            if existing:
                # A declaration that repeats membership without repeating a
                # fragment blanks it — set_story_characters() replaces
                # (character_id, fragment) rows wholesale. Membership is
                # unchanged in that case, so the diff above stays silent —
                # this is the only warning.
                frag_lines: list[str] = []
                for cid, now in new_char_state.items():
                    was = old_char_state.get(cid, "")
                    if was == now:
                        continue
                    label = char_display_name.get(cid, npc_id_to_name.get(cid, cid))
                    if was and not now:
                        frag_lines.append(f"    ~ {label}: fragment {was!r} -> cleared")
                    elif not was:
                        frag_lines.append(f"    ~ {label}: fragment -> {now!r}")
                    else:
                        frag_lines.append(f"    ~ {label}: fragment {was!r} -> {now!r}")
                if frag_lines:
                    changed = True
                    out.write("  Character fragments:\n")
                    out.write("\n".join(frag_lines) + "\n")
            elif fragments:
                out.write(f"  Fragments: {fragments}\n")
        _show_links_diff(
            "Locations",
            locations,
            [e.name for e in (locations or [])],
            "story_locations",
            "location_id",
            loc_id_to_name,
        )

        def _show_location_changes() -> None:
            """Report location rows this declaration would fork or re-attribute.

            ``location_id`` is a hash of ``name|region_id``, so changing a
            location's region does not edit the row — it mints a second one and
            strands the first. The membership diff above compares display names,
            which are identical before and after, so it stays silent. Without
            this block the preview shows a clean no-op for a row-orphaning change.

            Walks the **reachable** locations, not the ``locations`` kwarg.
            ``_upsert_one_group`` writes ``group.location`` and ``_upsert_locations``
            writes ``location.parent`` through the same call, so either can fork a
            row exactly as a top-level entry does. A ``groups=`` declaration with
            no ``locations=`` at all must still be checked, so the guard below
            drops the old ``locations is None`` shortcut and gates only on the
            story already existing — forking is a property of the row, not of
            which kwarg named it.
            """
            nonlocal changed
            if not existing:
                return
            _, reach_locations, _, _, _ = _reachable_entities()
            if not reach_locations:
                return
            lines: list[str] = []
            for entry in reach_locations:
                eff_region = region_row_id(entry.region) if entry.region else ""
                new_id = _location_id(entry.name, eff_region)
                # A global scan, not one scoped to this story's own linked rows:
                # a group's location is never linked through story_locations at
                # all, so scoping to that junction would make this a no-op for
                # exactly the case this walk exists to catch.
                superseded = [lid for lid, name in loc_id_to_name.items() if name == entry.name and lid != new_id]
                if superseded:
                    old_id = superseded[0]
                    old_row = q.select_location_by_id(self.conn, old_id)
                    old_region = ""
                    if old_row is not None and old_row["region_id"]:
                        old_region = region_id_to_name.get(old_row["region_id"], old_row["region_id"])
                    lines.append(
                        f"    ~ {entry.name}: region {old_region or '(none)'!r} -> {entry.region or '(none)'!r}"
                    )
                    lines.append(f"      NEW ROW {old_id} -> {new_id}; the old row is orphaned, not updated")
                    continue

                # Same row: report the columns this declaration would overwrite.
                # notes and lore_fragment both preserve-on-empty, so an omitted
                # value is not a change and must not be reported as one.
                row = q.select_location_by_id(self.conn, new_id)
                if row is None:
                    continue
                for field, incoming in (("notes", entry.notes), ("lore_fragment", entry.lore_fragment)):
                    stored = row[field] or ""
                    if not incoming or incoming == stored:
                        continue
                    lines.append(f"    ~ {entry.name}: {field} {stored or '(none)'!r} -> {incoming!r}")
            if lines:
                changed = True
                out.write("  Location rows:\n")
                out.write("\n".join(lines) + "\n")

        # Single-slot memo for _reachable_entities(); see its docstring.
        _reach_cache: list[tuple[list, list, list, list[str], list]] = []

        def _reachable_entities() -> tuple[list, list, list, list[str], list]:
            """Return every NPC, location, group, region name and title this
            declaration would write.

            The kwargs are not the whole list. ``_upsert_one_group`` walks into
            ``parent``, ``location`` and ``members``, ``_upsert_locations``
            walks into ``parent``, and ``_upsert_one_title`` walks into ``group``
            and ``npc_holders`` — each of those writes the entity's alternate
            names just as a top-level one does. Reporting only the kwargs would
            leave a nested change applying in silence, which is the exact shape
            this preview exists to catch: Ozrim and Maela Fairmind are reachable
            through a group roster and through nothing else.

            Region names are gathered the same way: from the ``regions`` kwarg,
            and from every reachable location's ``.region`` string — ``LocationEntry``
            names a region as a bare string, and ``_upsert_locations`` writes that
            region's row (including its ``world_of_rathe_story_key``) whether or
            not any ``RegionEntry`` ever names it.

            The seen sets double as the cycle guard. ``_upsert_locations`` and
            ``_upsert_one_group`` raise on a cycle, but they raise during the
            *write*, and this runs first.

            Memoised. Several of the report blocks below need this walk and the
            kwargs cannot change between them, so recomputing it each time only
            re-walked the same rosters. The cache is per-preview, living as long
            as the enclosing call.
            """
            if _reach_cache:
                return _reach_cache[0]
            seen_npc: dict[str, Any] = {}
            seen_loc: dict[tuple[str, str], Any] = {}
            seen_grp: dict[str, Any] = {}
            seen_region: dict[str, None] = {}
            seen_title: dict[str, Any] = {}

            def walk_npc(entry) -> None:
                # Guard first, then recurse: an NPC's kin relatives may name
                # each other back (siblings, spouses), and _upsert_npcs skips
                # re-processing an already-seen name for the same reason —
                # this is ordinary domain data, not a cycle to raise on.
                if entry.name in seen_npc:
                    return
                seen_npc[entry.name] = entry
                for item in entry.kin:
                    relative, _relation, _story_key = _kin_triple(item)
                    if not isinstance(relative, str):
                        walk_npc(relative)

            def walk_location(entry) -> None:
                key = (entry.name, entry.region)
                if key in seen_loc:
                    return
                seen_loc[key] = entry
                if entry.region:
                    seen_region.setdefault(entry.region, None)
                if entry.parent is not None:
                    walk_location(entry.parent)

            def walk_group(entry) -> None:
                if entry.name in seen_grp:
                    return
                seen_grp[entry.name] = entry
                if entry.parent is not None:
                    walk_group(entry.parent)
                if entry.location is not None:
                    walk_location(entry.location)
                for member, _source in entry.member_pairs():
                    if not isinstance(member, str):
                        walk_npc(member)

            def walk_title(entry) -> None:
                if entry.name in seen_title:
                    return
                seen_title[entry.name] = entry
                if entry.group is not None:
                    walk_group(entry.group)
                for npc_entry, _ordinal, _source in entry.npc_holders:
                    walk_npc(npc_entry)

            for entry in characters or []:
                if not isinstance(entry, str):
                    walk_npc(entry)
            for entry in locations or []:
                walk_location(entry)
            for entry in groups or []:
                walk_group(entry)
            for entry in regions or []:
                seen_region.setdefault(entry.name, None)
            for entry in titles or []:
                walk_title(entry)
            _reach_cache.append(
                (
                    list(seen_npc.values()),
                    list(seen_loc.values()),
                    list(seen_grp.values()),
                    list(seen_region.keys()),
                    list(seen_title.values()),
                )
            )
            return _reach_cache[0]

        def _show_alternate_name_changes() -> None:
            """Report epithet and alias rows this declaration would add or remove.

            These are replace-semantic like the group rosters, so a name dropped
            from a declaration is a deletion. That is precisely the change the
            preview used to be blind to — ``member_source`` moved silently for a
            whole session before anyone noticed — so every one of the three tables
            is diffed here rather than trusted, over every entity the write path
            reaches rather than over the kwargs alone.
            """
            nonlocal changed
            lines: list[str] = []
            reach_npcs, reach_locations, reach_groups, _reach_regions, _reach_titles = _reachable_entities()

            for entry in reach_npcs:
                cid = lore_character_id(entry.name)
                # Species is replace-semantic too, and it is the one that used to
                # preserve — 32 rows carried a value no declaration named, so a
                # missing species= reads as a deletion where it once read as
                # silence. That reversal is exactly what has to be visible.
                stored_sp = [_species_name(self.conn, sid) for sid in q.select_npc_species(self.conn, cid)]
                wanted_sp = [x.name for x in _species_tuple(entry.species)]
                for name in sorted(set(wanted_sp) - set(stored_sp)):
                    lines.append(f"    + {entry.name}: species {name!r}")
                for name in sorted(set(stored_sp) - set(wanted_sp)):
                    lines.append(f"    - {entry.name}: species {name!r} REMOVED")

                for sp in _species_tuple(entry.species):
                    sid = _species_id(sp.name)
                    stored_al = set(q.select_species_aliases(self.conn, sid))
                    wanted_al = set(sp.aliases)
                    for alias in sorted(wanted_al - stored_al):
                        lines.append(f"    + {sp.name}: alias {alias!r}")
                    for alias in sorted(stored_al - wanted_al):
                        lines.append(f"    - {sp.name}: alias {alias!r} REMOVED")

                # Professions (R9), reported the same shape as species just
                # above — walked over reach_npcs, not the characters= kwarg, so a
                # profession reached only through a group roster or a title
                # holder is visible here too. _resolve_professions raises on a
                # repeated profession on this entry, on the preview path too,
                # before any diff below is computed — the same guard the write
                # path applies via _upsert_professions.
                resolved_prof = self._resolve_professions(entry.name, _professions_tuple(entry.professions))
                stored_prof = [
                    _profession_name(self.conn, pid) for pid in q.select_character_professions(self.conn, cid)
                ]
                wanted_prof = [name for _pid, name in resolved_prof]
                for name in sorted(set(wanted_prof) - set(stored_prof)):
                    lines.append(f"    + {entry.name}: profession {name!r}")
                for name in sorted(set(stored_prof) - set(wanted_prof)):
                    lines.append(f"    - {entry.name}: profession {name!r} REMOVED")

                stored = set(q.select_npc_epithets(self.conn, cid))
                wanted = {(n, "epithet") for n in entry.epithets} | {(n, "short-name") for n in entry.short_names}
                for name, kind in sorted(wanted - stored):
                    lines.append(f"    + {entry.name}: {kind} {name!r}")
                for name, kind in sorted(stored - wanted):
                    lines.append(f"    - {entry.name}: {kind} {name!r} REMOVED")

            for entry in reach_locations:
                lid = _location_id(entry.name, region_row_id(entry.region) if entry.region else "")
                stored = set(q.select_location_aliases(self.conn, lid))
                wanted = {_alias_pair(a) for a in entry.aliases}
                for alias, era in sorted(wanted - stored):
                    lines.append(f"    + {entry.name}: alias {alias!r}" + (f" (era {era!r})" if era else ""))
                for alias, era in sorted(stored - wanted):
                    lines.append(f"    - {entry.name}: alias {alias!r} REMOVED")

            for entry in reach_groups:
                gid = _group_id(entry.name)
                stored = set(q.select_group_aliases(self.conn, gid))
                wanted = set(entry.aliases)
                for alias in sorted(wanted - stored):
                    lines.append(f"    + {entry.name}: alias {alias!r}")
                for alias in sorted(stored - wanted):
                    lines.append(f"    - {entry.name}: alias {alias!r} REMOVED")

            if lines:
                changed = True
                out.write("  Alternate names:\n")
                out.write("\n".join(lines) + "\n")

        _show_alternate_name_changes()

        def _show_npc_creations() -> None:
            """Report a reachable NPC that has no stored row yet.

            ``_show_attr_changes`` skips a row that does not exist —
            "new row: nothing to overwrite" — and the Characters diff above
            only walks the ``characters=`` kwarg, not the reachable set. An NPC
            introduced purely through a group roster, carrying no species, no
            epithets and no short names, has nothing left to surface it in the
            alternate-names diff either, so it was created in total silence
            under a group line reading "N members". This is that creation's
            only announcement.
            """
            nonlocal changed
            reach_npcs, _, _, _, _ = _reachable_entities()
            lines: list[str] = []
            for entry in reach_npcs:
                if npc_rows.get(lore_character_id(entry.name)) is None:
                    lines.append(f"    + {entry.name}")
            if lines:
                changed = True
                out.write("  New NPCs:\n")
                out.write("\n".join(lines) + "\n")

        _show_npc_creations()

        def _show_hero_slug_changes() -> None:
            """Report a character_heroes link a ``hero_slug`` claim would write.

            ``hero_slug`` preserves on empty and writes ``character_heroes`` as a
            side effect of ``_upsert_npcs``, so this walks the **reachable** NPCs
            (``_reachable_entities()``), not the ``characters=`` kwarg — a claim made
            through a group roster must be visible here too, exactly like a
            species or an epithet reached the same way.
            """
            nonlocal changed
            reach_npcs, _, _, _, _ = _reachable_entities()
            lines: list[str] = []
            for entry in reach_npcs:
                if not entry.hero_slug:
                    continue
                hero_row = q.select_hero_by_slug(self.conn, entry.hero_slug)
                if hero_row is None:
                    continue  # unknown slug: the real write raises via _resolve_heroes
                canonical_id = hero_row["canonical_id"]
                cid = lore_character_id(entry.name)
                stored_character_id = q.select_character_id_for_hero(self.conn, canonical_id)
                if stored_character_id == cid:
                    continue
                if stored_character_id:
                    was = npc_id_to_name.get(stored_character_id, stored_character_id)
                    lines.append(f"    ~ {entry.name}: hero_slug {entry.hero_slug!r} {was!r} -> {entry.name!r}")
                else:
                    lines.append(f"    + {entry.name}: hero_slug {entry.hero_slug!r} -> character_heroes")
            if lines:
                changed = True
                out.write("  character_heroes:\n")
                out.write("\n".join(lines) + "\n")

        _show_hero_slug_changes()

        def _show_kin_changes() -> None:
            """Report ``character_kin`` rows a kin declaration would add or remove.

            Replace-semantic, like species and the epithet tables: an omitted
            kin fact is a deletion, not a preserved value (see ``NPCEntry.kin``'s
            docstring for the reasoning). Walks the **reachable** NPCs
            (``_reachable_entities()``), not the ``characters=`` kwarg, for the same
            reason ``_show_hero_slug_changes`` does — a kin fact declared on an
            NPC reached only through a group roster must not be invisible here.

            Resolves through ``_resolve_kin_relatives``, which raises on a
            repeated ``(relative, relation)`` pair, an unknown hero slug, or a
            self-relative claim — on this preview path too, before any diff is
            computed, so a bad declaration fails the same way here as it would
            on the real write.
            """
            nonlocal changed
            reach_npcs, _, _, _, _ = _reachable_entities()
            lines: list[str] = []
            for entry in reach_npcs:
                cid = lore_character_id(entry.name)
                resolved = self._resolve_kin_relatives(entry)
                origin_by_key = {(rid, relation): origin for rid, relation, _sk, origin in resolved}
                wanted_map = {(rid, relation): sk for rid, relation, sk, _origin in resolved}
                stored_map = {(rid, relation): sk for rid, relation, sk in q.select_character_kin(self.conn, cid)}
                added = set(wanted_map) - set(stored_map)
                removed = set(stored_map) - set(wanted_map)
                resourced = sorted(k for k in set(wanted_map) & set(stored_map) if wanted_map[k] != stored_map[k])
                for rid, relation in sorted(added):
                    who = origin_by_key.get((rid, relation), npc_id_to_name.get(rid, rid))
                    lines.append(f"    + {entry.name}: {relation} {who!r}")
                for rid, relation in sorted(removed):
                    who = npc_id_to_name.get(rid, rid)
                    lines.append(f"    - {entry.name}: {relation} {who!r} REMOVED")
                for rid, relation in resourced:
                    who = npc_id_to_name.get(rid, rid)
                    lines.append(
                        f"    ~ {entry.name}: {relation} {who!r} source "
                        f"{stored_map[(rid, relation)] or '(none)'!r} -> {wanted_map[(rid, relation)] or '(none)'!r}"
                    )
            if lines:
                changed = True
                out.write("  Kin:\n")
                out.write("\n".join(lines) + "\n")

        _show_kin_changes()

        def _show_attr_changes(
            label: str,
            entries: list | None,
            id_fn: Any,
            rows_by_id: dict[str, Any],
            fields: tuple[str, ...],
        ) -> None:
            """Report registry columns this declaration would overwrite.

            Every one of these columns preserves-on-empty, so an omitted value
            leaves the stored one alone and is not a change. Reporting it as a
            clear would be a false alarm, which trains the reader to skim past
            the section — so only a non-empty, differing value is shown.
            """
            nonlocal changed
            if entries is None or not existing:
                return
            lines: list[str] = []
            for entry in entries:
                row = rows_by_id.get(id_fn(entry.name))
                if row is None:
                    continue  # new row: nothing to overwrite
                for field in fields:
                    incoming = getattr(entry, field, "") or ""
                    stored = row[field] or ""
                    if not incoming or incoming == stored:
                        continue
                    lines.append(f"    ~ {entry.name}: {field} {stored or '(none)'!r} -> {incoming!r}")
            if lines:
                changed = True
                out.write(f"  {label} rows:\n")
                out.write("\n".join(lines) + "\n")

        def _show_food_drink_changes() -> None:
            """Warn when a kind change forks a row, as ``food_drink_id`` hashes name|kind."""
            nonlocal changed
            if food_drink is None or not existing:
                return
            linked_ids = q.select_story_junction(self.conn, story_id, "story_food_drink", "food_drink_id")
            lines: list[str] = []
            for entry in food_drink:
                new_id = food_drink_id(entry.name, entry.kind)
                superseded = [fid for fid in linked_ids if food_id_to_name.get(fid) == entry.name and fid != new_id]
                if not superseded:
                    continue
                lines.append(f"    ~ {entry.name}: kind -> {entry.kind!r}")
                lines.append(f"      NEW ROW {superseded[0]} -> {new_id}; the old row is orphaned, not updated")
            if lines:
                changed = True
                out.write("  Food & Drink rows:\n")
                out.write("\n".join(lines) + "\n")

        _show_location_changes()
        # Reachable, not the `characters=` kwarg: `_upsert_one_group` writes `status` and
        # `other_characters_story_key` for roster NPCs too, via `_upsert_npcs`, so
        # an overwrite reached only through a group roster must be shown here —
        # Monster/Fauna/Flora stay on their own kwargs below, since none of them
        # is reachable through a group.
        reach_npcs_for_attrs, _, _, _, _ = _reachable_entities()
        _show_attr_changes(
            "NPC",
            reach_npcs_for_attrs,
            lore_character_id,
            npc_rows,
            ("status", "other_characters_story_key"),
        )
        _show_attr_changes("Monster", monsters, _monster_id, monster_rows, ("description",))
        _show_attr_changes("Fauna", fauna, fauna_id_from_name, fauna_rows, ("description",))
        _show_attr_changes("Flora", flora, flora_id, flora_rows, ("description",))

        def _show_region_changes() -> None:
            """Report a region's world_of_rathe_story_key being overwritten in place.

            A region named only as a ``LocationEntry(region="…")`` string is
            written by ``_upsert_locations`` exactly the way an explicit
            ``RegionEntry`` is — including its own ``_auto_world_key`` fallback —
            so it is walked here too via ``_reachable_entities()``'s region
            names, or the overwrite applies in silence on a page that never
            names the region directly.
            """
            nonlocal changed
            if not existing:
                return
            _, reach_locations, _, reach_region_names, _ = _reachable_entities()
            if not reach_region_names:
                return
            # Last-wins, matching write order: the real upsert_story() writes
            # `regions` via `_upsert_regions` before `locations` via
            # `_upsert_locations`, so a location's region key overwrites an
            # explicit RegionEntry naming the same region.
            incoming_by_name: dict[str, str] = {}
            for entry in regions or []:
                incoming_by_name[entry.name] = entry.world_of_rathe_story_key or _auto_world_key(entry.name)
            for loc in reach_locations:
                if loc.region:
                    incoming_by_name[loc.region] = loc.world_of_rathe_story_key or _auto_world_key(loc.region)
            lines: list[str] = []
            for name in sorted(reach_region_names):
                rid = region_row_id(name)
                row = q.select_region_by_id(self.conn, rid)
                if row is None:
                    continue
                incoming = incoming_by_name.get(name, "")
                stored = row["world_of_rathe_story_key"] or ""
                if not incoming or incoming == stored:
                    continue
                lines.append(f"    ~ {name}: world_of_rathe_story_key {stored or '(none)'!r} -> {incoming!r}")
            if lines:
                changed = True
                out.write("  Region rows:\n")
                out.write("\n".join(lines) + "\n")

        _show_food_drink_changes()
        _show_region_changes()
        _show_links_diff(
            "Regions",
            regions,
            [e.name for e in (regions or [])],
            "story_regions",
            "region_id",
            region_id_to_name,
        )
        _show_links_diff(
            "Monsters",
            monsters,
            [e.name for e in (monsters or [])],
            "story_monsters",
            "monster_id",
            monster_id_to_name,
        )
        _show_links_diff(
            "Fauna",
            fauna,
            [e.name for e in (fauna or [])],
            "story_fauna",
            "fauna_id",
            fauna_id_to_name,
        )
        _show_links_diff(
            "Flora",
            flora,
            [e.name for e in (flora or [])],
            "story_flora",
            "flora_id",
            flora_id_to_name,
        )
        _show_links_diff(
            "Food & Drink",
            food_drink,
            [e.name for e in (food_drink or [])],
            "story_food_drink",
            "food_drink_id",
            food_id_to_name,
        )
        _show_links_diff(
            "Weapons",
            weapon_ids,
            [weapon_id_to_slug.get(wid, wid) for wid in (weapon_ids or [])],
            "story_weapons",
            "canonical_weapon_id",
            weapon_id_to_slug,
        )
        _show_links_diff(
            "Equipment",
            equip_ids,
            [equip_id_to_slug.get(eid, eid) for eid in (equip_ids or [])],
            "story_equipment",
            "canonical_equipment_id",
            equip_id_to_slug,
        )

        def _show_group_changes() -> None:
            """Report roster and attribute changes a group declaration would write.

            The roster is the part worth previewing: membership is replace-semantic
            like a story junction, so a short ``members`` silently drops people.

            Walks the **reachable** groups, not the ``groups`` kwarg. Until
            2026-08-21 it iterated the kwarg, so a group reached only as another
            group's ``parent`` was invisible here in every respect — its creation,
            its roster and its scalars alike — while ``_show_alternate_name_changes``
            walked the same chain and reported its aliases. Stage 5's Super Slam
            hierarchy is what surfaced it: declaring twelve guilds would have
            created four stable rows, twelve parent links and three patron
            memberships, and printed one line about an alias.
            """
            nonlocal changed
            _, _, reach_groups, _, _ = _reachable_entities()
            if not reach_groups:
                return
            lines: list[str] = []
            for entry in reach_groups:
                gid = _group_id(entry.name)
                row = group_rows.get(gid)
                # Resolved before the new-group branch, not inside the diff
                # below it: a roster naming one person as a slug and as an
                # NPCEntry raises here, and a *new* group never reaches the
                # diff, so leaving this until then let the write raise on a
                # clash the preview had just reported as fine. The count is the
                # resolved one for the same reason — it is the number of rows
                # that would be written, which len(entry.members) is not once
                # two items can name one person.
                wanted_map = {cid: src for cid, src, _origin in self._dry_run_group_members(entry)}
                if row is None:
                    roster = len(wanted_map)
                    parent = f", parent={entry.parent.name!r}" if entry.parent is not None else ""
                    lines.append(
                        f"    + {entry.name} (new group, kind={entry.kind or '(none)'!r}{parent}, {roster} members)"
                    )
                    continue
                # Every scalar `upsert_group` writes from a plain string on the
                # entry. `kind` alone was previewed until 2026-08-20, so a group
                # gaining its documentation page changed the DB and printed
                # nothing — the same shape as the roster bug stage 3 fixed.
                #
                # `parent_group_id` joined them 2026-08-21. The stage 11 note that
                # left it out said it and `location_id` "both need resolving rather
                # than reading, and resolving a location writes" — true of the
                # location, false of the parent. `_group_id` is a pure hash of the
                # name, so a parent resolves without touching the database, and the
                # two were only ever grouped because they sit side by side on the
                # entry. `location_id` genuinely does write and stays out.
                parent_name = entry.parent.name if entry.parent is not None else ""
                for field, incoming in (
                    ("kind", entry.kind),
                    ("parent_group_id", _group_id(parent_name) if parent_name else ""),
                    ("lore_story_key", entry.lore_story_key),
                    ("lore_fragment", entry.lore_fragment),
                ):
                    stored = row[field] or ""
                    if incoming and incoming != stored:
                        # A group id says nothing to a reader. Render both ends of
                        # a parent change by name, falling back to the id for a
                        # parent that does not exist yet in this same run.
                        if field == "parent_group_id":
                            was = group_id_to_name.get(stored, stored) if stored else "(none)"
                            now = group_id_to_name.get(incoming, parent_name)
                            lines.append(f"    ~ {entry.name}: parent {was!r} -> {now!r}")
                        else:
                            lines.append(f"    ~ {entry.name}: {field} {stored or '(none)'!r} -> {incoming!r}")
                # One roster table since migration 18, so one added/removed
                # line rather than the pair this printed while a hero member
                # and an NPC member lived in different junctions.
                #
                # No guard. A declaration that names no members is asking for an
                # empty roster, and the write path honours that, so the preview
                # has to report the deletion. A group that has no stored members
                # either produces no lines below, which is the quiet case this
                # once tried to buy with a `continue`.
                stored = dict(q.select_group_members(self.conn, gid, "group_characters", "character_id"))
                added, removed = set(wanted_map) - set(stored), set(stored) - set(wanted_map)
                # The citation is a stored column, so a membership that keeps
                # its row and changes the page it cites is a write. Comparing
                # id sets alone made that invisible, which is how the per-member
                # source could have landed unannounced.
                resourced = sorted(i for i in set(wanted_map) & set(stored) if wanted_map[i] != stored[i])
                if added:
                    lines.append(f"    + {entry.name}: {len(added)} member(s) added to group_characters")
                if removed:
                    lines.append(f"    - {entry.name}: {len(removed)} member(s) REMOVED from group_characters")
                for mid in resourced:
                    old_src = stored[mid] or "(none)"
                    who = npc_id_to_name.get(mid, mid)
                    lines.append(f"    ~ {entry.name}: {who} source {old_src!r} -> {wanted_map[mid] or '(none)'!r}")
            if lines:
                changed = True
                out.write("  Group rows:\n")
                out.write("\n".join(lines) + "\n")

        _show_group_changes()
        _show_links_diff(
            "Groups",
            groups,
            [e.name for e in (groups or [])],
            "story_groups",
            "group_id",
            group_id_to_name,
        )

        def _show_title_changes() -> None:
            """Report holder and scalar changes a title declaration would write.

            Mirrors ``_show_group_changes``: holders are replace-semantic like a
            group roster, so a short holder list silently drops people, and the
            preview must say so. Unlike a group, a title has one holder table
            rather than two (``title_holders`` covers NPCs and heroes alike,
            migration 12's identity spine), so there is one added/removed line
            per title rather than one per table.

            Walks the **reachable** titles, not the ``titles`` kwarg, for the
            same reason ``_show_group_changes`` walks reachable groups — a title
            reached only through another entity must not be invisible here.
            """
            nonlocal changed
            _, _, _, _, reach_titles = _reachable_entities()
            if not reach_titles:
                return
            lines: list[str] = []
            for entry in reach_titles:
                tid = _title_id(entry.name)
                row = title_rows.get(tid)
                group_name = entry.group.name if entry.group is not None else ""
                incoming_group_id = _group_id(group_name) if group_name else ""

                # Raises here too, on the preview path — before the new/existing
                # branch below, so a doubled holder on a brand-new title fails
                # the same way it would on the real write, rather than being
                # skipped by the "nothing to diff yet" shortcut.
                resolved = self._resolve_title_holders(entry)

                if row is None:
                    n_holders = len(entry.npc_holders) + len(entry.hero_holders)
                    grp = f", group={group_name!r}" if group_name else ""
                    lines.append(f"    + {entry.name} (new title{grp}, {n_holders} holder(s))")
                    continue
                stored_group = row["group_id"] or ""
                if incoming_group_id and incoming_group_id != stored_group:
                    was = group_id_to_name.get(stored_group, stored_group) if stored_group else "(none)"
                    now = group_id_to_name.get(incoming_group_id, group_name)
                    lines.append(f"    ~ {entry.name}: group {was!r} -> {now!r}")

                wanted_map = {cid: (ordinal, story_key) for cid, ordinal, story_key, _origin in resolved}
                stored_map = {
                    cid: (ordinal, story_key) for cid, ordinal, story_key in q.select_title_holders(self.conn, tid)
                }
                added = set(wanted_map) - set(stored_map)
                removed = set(stored_map) - set(wanted_map)
                resourced = sorted(
                    cid for cid in set(wanted_map) & set(stored_map) if wanted_map[cid] != stored_map[cid]
                )
                if added:
                    lines.append(f"    + {entry.name}: {len(added)} holder(s) added to title_holders")
                if removed:
                    lines.append(f"    - {entry.name}: {len(removed)} holder(s) REMOVED from title_holders")
                for cid in resourced:
                    who = npc_id_to_name.get(cid, cid)
                    old_ordinal, old_source = stored_map[cid]
                    new_ordinal, new_source = wanted_map[cid]
                    lines.append(
                        f"    ~ {entry.name}: {who} ordinal {old_ordinal} -> {new_ordinal}, "
                        f"source {old_source or '(none)'!r} -> {new_source or '(none)'!r}"
                    )
            if lines:
                changed = True
                out.write("  Title rows:\n")
                out.write("\n".join(lines) + "\n")

        _show_title_changes()
        _show_links_diff(
            "Titles",
            titles,
            [e.name for e in (titles or [])],
            "story_titles",
            "title_id",
            title_id_to_name,
        )

        self._last_dry_run_changed = changed
        out.write("\n(no changes written)\n")

        # Return a StoryRecord reflecting the would-be state
        if existing:
            return self._load_record(existing["story_id"])

        videos = narrated_videos or []
        return StoryRecord(
            story_id=story_id,
            story_key=story_key,
            story_type=story_type,
            title=title,
            authors=authors,
            artists=artists,
            source_link=source_link,
            publication_date=publication_date,
            thumbnail_image_link=thumbnail_image_link,
            narrated_videos=list(videos),
            _db=self,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _story_key_from_path(path: str | Path) -> str:
    """Return ``StoryKey``: path relative to ``src/``, POSIX, ending in ``.md``."""
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    try:
        rel = p.relative_to(SRC.resolve())
    except ValueError as exc:
        raise ValueError(f"Story path must be under {SRC}: {p}") from exc
    key = rel.as_posix()
    if not key.endswith(".md"):
        raise ValueError(f"Story path must be a .md file: {key}")
    return key
