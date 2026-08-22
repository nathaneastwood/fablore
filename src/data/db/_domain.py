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
    region_row_id,
    species_id as _species_id,
    story_id as _story_id,
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
    status: str = ""
    """Leave empty to preserve an existing NPC's status; new NPCs default to ``"Unknown"``."""
    other_characters_story_key: str = ""
    fragment: str = ""
    """mdBook heading anchor id for a deep link into the story page, e.g. ``"morlock-hill"``."""
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

    Raises ``ValueError`` for an unknown slug, the same way ``heroes=`` does,
    and when two different NPCs in one call claim the same slug — the shape of
    the guard in ``GroupEntry.members()``, which raises on a repeated NPC for
    the same reason: the write and the preview would otherwise resolve the
    clash differently and neither would say so."""


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
    npc_members: tuple["NPCEntry | tuple[NPCEntry, str]", ...] = ()
    """NPC roster (R1). A tuple, because the dataclass is frozen and hashable.

    An item is an :class:`NPCEntry`, or an ``(NPCEntry, story_key)`` pair when
    that one membership is attested somewhere other than ``member_source``.

    The pair exists because ``The Maela`` needed it. Eleven of the twelve rosters
    that cite a source were read off a single page that lists the whole roster —
    ``flavour/super-slam.md`` names the guilds, ``lyath-about.md`` names the
    family. The Maela is not like that: five seers named across four different
    flavour pages, and no page that lists them as a roster. One string for the
    group could only be right for one of them.

    Hero rosters take no pair. ``hero_members`` is slugs, no hero roster needs
    one yet, and an untested second path is worse than a documented asymmetry —
    it is listed in stage 11.
    """
    hero_members: tuple[str, ...] = ()
    """Canonical hero slugs in the roster. Validated on upsert."""
    parent: "GroupEntry | None" = None
    """Enclosing group, e.g. a Super Slam guild inside the clan it draws from."""
    location: "LocationEntry | None" = None
    """Only when the group is *also* a place — Teklo Industries, a company and a
    works. Most groups leave this empty; a group is not a place."""
    member_source: str = ""
    """Optional story key citing the roster (D2). The **default** for every member
    that does not carry its own key in ``npc_members``; a group whose members are
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

    def members(self) -> list[tuple["NPCEntry", str]]:
        """The NPC roster as ``(npc, story_key)`` pairs, with the default applied.

        The one place that unpacks the optional pair, so every caller reads a
        roster the same shape whether or not a membership cites its own page.

        Raises:
            ValueError: if one NPC appears twice in the roster. The pair made this
                reachable and the two paths resolve it differently: ``group_npcs``
                is keyed ``(group_id, character_id)`` and written with
                ``INSERT OR IGNORE``, so the write keeps the **first** citation,
                while the preview builds a dict and reports the **last**. Neither
                raises, so a roster naming someone twice would be previewed as one
                page and stored as another. Guarded here rather than in either
                path, so both fail the same way.
        """
        pairs: list[tuple["NPCEntry", str]] = []
        seen: dict[str, str] = {}
        for item in self.npc_members:
            if isinstance(item, tuple):
                npc, source = item
            else:
                npc, source = item, self.member_source
            if npc.name in seen:
                raise ValueError(
                    f"{self.name!r} names {npc.name!r} twice in npc_members "
                    f"(citing {seen[npc.name] or '(none)'!r} and {source or '(none)'!r}). "
                    "A membership is one row; cite the page that attests it once."
                )
            seen[npc.name] = source
            pairs.append((npc, source))
        return pairs


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
            heroes=["boltyn"],
            npcs=[NPCEntry("Guard Captain", species=SpeciesEntry("Human"))],
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
        heroes: list[str] | None = None,
        hero_fragments: dict[str, str] | None = None,
        npcs: list[NPCEntry] | None = None,
        locations: list[LocationEntry] | None = None,
        regions: list[RegionEntry] | None = None,
        monsters: list[MonsterEntry] | None = None,
        fauna: list[FaunaEntry] | None = None,
        flora: list[FloraEntry] | None = None,
        food_drink: list[FoodDrinkEntry] | None = None,
        weapons: list[str] | None = None,
        equipment: list[str] | None = None,
        groups: list[GroupEntry] | None = None,
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
            heroes: Canonical hero slugs (see :meth:`print_heroes`).
            hero_fragments: Optional ``{slug: fragment}`` map giving a heading
                anchor id within the story for each hero, e.g.
                ``{"dorinthea": "morlock-hill-dtd209"}``.
            npcs: NPC entries; strings in a future shorthand are not supported —
                use :class:`NPCEntry` directly. Omit ``status`` to preserve
                whatever an existing NPC row already has; only pass it when this
                story is the evidence for the value. ``species`` does **not**
                preserve — it is replace-semantic, so an omitted one is a
                deletion.
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
            dry_run: Print a diff and return the record without writing anything.

        Returns:
            :class:`StoryRecord` reflecting the final state of the story.

        Raises:
            ValueError: If an unknown hero / weapon / equipment slug is given,
                or if a ``lore_fragment`` cannot be resolved to a heading on disk.
        """
        story_key = _story_key_from_path(path)
        story_id = _story_id(story_key)

        # Resolve hero ids eagerly so we fail fast before writing anything.
        hero_ids = self._resolve_heroes(heroes) if heroes is not None else None
        if hero_ids is not None:
            self._validate_hero_fragments(story_key, heroes or [], hero_ids, hero_fragments or {})
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
                hero_ids=hero_ids,
                hero_fragments=hero_fragments,
                npcs=npcs,
                locations=locations,
                regions=regions,
                monsters=monsters,
                fauna=fauna,
                flora=flora,
                food_drink=food_drink,
                weapon_ids=weapon_ids,
                equip_ids=equip_ids,
                groups=groups,
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
            if hero_ids is not None:
                frags = hero_fragments or {}
                entries = [(cid, frags.get(slug, "")) for slug, cid in zip(heroes or [], hero_ids)]
                q.set_story_heroes(self.conn, story_id, entries)
            if npcs is not None:
                npc_entries = self._upsert_npcs(npcs)
                q.set_story_npcs(self.conn, story_id, npc_entries)
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
            (
                "Heroes",
                "story_heroes",
                "canonical_id",
                "heroes_canonical",
                "canonical_id",
                "canonical_hero",
            ),
            ("NPCs", "story_npcs", "character_id", "characters", "character_id", "name"),
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
                ``"group"`` or ``"species"``.
            name: Display name of the entity (must already exist in the database).
            description: Short lore summary. ``"location"``, ``"group"`` and
                ``"species"`` set the ``notes`` field; the others set ``description``.

        A group must already have a row before its summary can land here, and a row
        is only created by a story declaration naming it. Six catalogue constants
        have no row yet for exactly that reason, so re-point the declaration before
        adding the note rather than the other way round.

        A species row is created by an NPC carrying it, with one deliberate
        exception: ``species.csv`` is a registry seeded on its own, so ``Chanek``
        keeps a row although no NPC is one yet.

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
            elif entity_type in _TABLE_MAP:
                table, id_col, id_fn = _TABLE_MAP[entity_type]
                entity_id = id_fn(name)
                rows = q.update_entity_description(self.conn, table, id_col, entity_id, description)
                if rows == 0:
                    raise ValueError(f"{entity_type.capitalize()} not found: {name!r}")
            else:
                raise ValueError(
                    f"Unknown entity type: {entity_type!r}. "
                    "Use 'monster', 'fauna', 'flora', 'location', 'group', or 'species'."
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
            "npc": ("characters", "character_id", "story_npcs", lore_character_id),
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

    def _validate_hero_fragments(
        self,
        story_key: str,
        slugs: list[str],
        hero_ids: list[str],  # noqa: ARG002 — reserved for future per-hero path lookup
        frags: dict[str, str],
    ) -> None:
        if not frags:
            return
        md_path = (SRC / story_key).resolve()
        if not md_path.is_file():
            return
        ids_on_page: set[str] | None = None
        for slug in slugs:
            frag = frags.get(slug, "")
            if not frag:
                continue
            if ids_on_page is None:
                ids_on_page = collect_heading_anchor_ids_from_path(md_path)
            if frag not in ids_on_page:
                rel = md_path.relative_to(SRC).as_posix()
                raise ValueError(
                    f"Hero fragment {frag!r} for slug {slug!r} not found in {rel}. "
                    f"Known ids: {format_fragment_suggestion(ids_on_page)}"
                )

    def _upsert_npcs(self, entries: list[NPCEntry]) -> list[tuple[str, str]]:
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
            if e.hero_slug:
                # Same shape as the guard in GroupEntry.members(): the write
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
            ids.append((cid, e.fragment))
        return ids

    def _upsert_species(self, entries: "tuple[SpeciesEntry, ...]") -> list[str]:
        """Upsert each species row and return its ids, in declared order."""
        ids: list[str] = []
        for e in entries:
            sid = _species_id(e.name)
            q.upsert_species(self.conn, species_id=sid, name=e.name)
            q.set_species_aliases(self.conn, sid, list(e.aliases))
            ids.append(sid)
        return ids

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

        # Unconditional, both of them. ``set_group_members`` is replace-semantic —
        # it deletes the stored rows before inserting — and an emptied roster is a
        # deletion the declaration asked for, not a no-op. Guarding these calls on a
        # truthy roster made an emptied one silently keep its rows while the dry run
        # went on printing a REMOVED line for them.
        roster = entry.members()
        npc_ids = self._upsert_npcs([npc for npc, _source in roster])
        q.set_group_members(
            self.conn,
            gid,
            "group_npcs",
            "character_id",
            # Zip, not `entry.member_source`: `_upsert_npcs` returns ids in the
            # order it was given, which is the order `members()` produced, so a
            # membership that cites its own page keeps it.
            [(cid, source) for (cid, _frag), (_npc, source) in zip(npc_ids, roster)],
        )
        hero_ids = self._resolve_heroes(list(entry.hero_members))
        q.set_group_members(
            self.conn,
            gid,
            "group_heroes",
            "canonical_id",
            [(hid, entry.member_source) for hid in hero_ids],
        )
        q.set_group_aliases(self.conn, gid, list(entry.aliases))
        return gid

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
        hero_ids: list[str] | None,
        hero_fragments: dict[str, str] | None = None,
        npcs: list[NPCEntry] | None,
        locations: list[LocationEntry] | None,
        regions: list[RegionEntry] | None,
        monsters: list[MonsterEntry] | None,
        fauna: list[FaunaEntry] | None,
        flora: list[FloraEntry] | None,
        food_drink: list[FoodDrinkEntry] | None,
        weapon_ids: list[str] | None,
        equip_ids: list[str] | None,
        groups: list[GroupEntry] | None = None,
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

        _show_links_diff(
            "Heroes",
            hero_ids,
            [hero_id_to_slug.get(hid, hid) for hid in (hero_ids or [])],
            "story_heroes",
            "canonical_id",
            hero_id_to_slug,
        )
        if hero_ids is not None and existing:
            # set_story_heroes() replaces (canonical_id, fragment) pairs wholesale, so a
            # declaration that lists heroes without a matching hero_fragments= blanks
            # every curated anchor. Membership is unchanged in that case, so the
            # membership diff above stays silent — this is the only warning.
            old_frags = q.select_story_hero_fragments(self.conn, story_id)
            new_frags = hero_fragments or {}
            frag_lines: list[str] = []
            for cid in hero_ids:
                slug = hero_id_to_slug.get(cid, cid)
                was = old_frags.get(cid, "")
                now = new_frags.get(slug, "")
                if was == now:
                    continue
                if was and not now:
                    frag_lines.append(f"    ~ {slug}: fragment {was!r} -> cleared")
                elif not was:
                    frag_lines.append(f"    ~ {slug}: fragment -> {now!r}")
                else:
                    frag_lines.append(f"    ~ {slug}: fragment {was!r} -> {now!r}")
            if frag_lines:
                changed = True
                out.write("  Hero fragments:\n")
                out.write("\n".join(frag_lines) + "\n")
        elif hero_fragments:
            out.write(f"  HeroFragments: {hero_fragments}\n")
        _show_links_diff(
            "NPCs",
            npcs,
            [e.name for e in (npcs or [])],
            "story_npcs",
            "character_id",
            npc_id_to_name,
        )
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
            _, reach_locations, _, _ = _reachable_entities()
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
        _reach_cache: list[tuple[list, list, list, list[str]]] = []

        def _reachable_entities() -> tuple[list, list, list, list[str]]:
            """Return every NPC, location, group and region name this declaration would write.

            The kwargs are not the whole list. ``_upsert_one_group`` walks into
            ``parent``, ``location`` and ``npc_members``, and ``_upsert_locations``
            walks into ``parent`` — each of those writes the entity's alternate
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

            Memoised. Six of the report blocks below need this walk and the
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

            def walk_npc(entry) -> None:
                seen_npc.setdefault(entry.name, entry)

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
                for member, _source in entry.members():
                    walk_npc(member)

            for entry in npcs or []:
                walk_npc(entry)
            for entry in locations or []:
                walk_location(entry)
            for entry in groups or []:
                walk_group(entry)
            for entry in regions or []:
                seen_region.setdefault(entry.name, None)
            _reach_cache.append(
                (
                    list(seen_npc.values()),
                    list(seen_loc.values()),
                    list(seen_grp.values()),
                    list(seen_region.keys()),
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
            reach_npcs, reach_locations, reach_groups, _reach_regions = _reachable_entities()

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
            "new row: nothing to overwrite" — and ``_show_links_diff("NPCs")``
            only walks the ``npcs`` kwarg, not the reachable set. An NPC
            introduced purely through a group roster, carrying no species, no
            epithets and no short names, has nothing left to surface it in the
            alternate-names diff either, so it was created in total silence
            under a group line reading "N members". This is that creation's
            only announcement.
            """
            nonlocal changed
            reach_npcs, _, _, _ = _reachable_entities()
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
            (``_reachable_entities()``), not the ``npcs`` kwarg — a claim made
            through a group roster must be visible here too, exactly like a
            species or an epithet reached the same way.
            """
            nonlocal changed
            reach_npcs, _, _, _ = _reachable_entities()
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
        # Reachable, not the `npcs` kwarg: `_upsert_one_group` writes `status` and
        # `other_characters_story_key` for roster NPCs too, via `_upsert_npcs`, so
        # an overwrite reached only through a group roster must be shown here —
        # Monster/Fauna/Flora stay on their own kwargs below, since none of them
        # is reachable through a group.
        reach_npcs_for_attrs, _, _, _ = _reachable_entities()
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
            _, reach_locations, _, reach_region_names = _reachable_entities()
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
            like a story junction, so a short ``npc_members`` silently drops people.

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
            _, _, reach_groups, _ = _reachable_entities()
            if not reach_groups:
                return
            lines: list[str] = []
            for entry in reach_groups:
                gid = _group_id(entry.name)
                row = group_rows.get(gid)
                if row is None:
                    roster = len(entry.npc_members) + len(entry.hero_members)
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
                for table, id_col, wanted in (
                    ("group_npcs", "character_id", [(lore_character_id(m.name), src) for m, src in entry.members()]),
                    ("group_heroes", "canonical_id", [(h, entry.member_source) for h in entry.hero_members]),
                ):
                    # No guard. A declaration that names no members is asking for an
                    # empty roster, and the write path honours that, so the preview
                    # has to report the deletion. A group that has no stored members
                    # either produces no lines below, which is the quiet case this
                    # once tried to buy with a `continue`.
                    stored = dict(q.select_group_members(self.conn, gid, table, id_col))
                    if table == "group_heroes" and wanted:
                        slugs, sources = [h for h, _s in wanted], [s for _h, s in wanted]
                        wanted_map = dict(zip(self._resolve_heroes(slugs), sources))
                    else:
                        wanted_map = dict(wanted)
                    added, removed = set(wanted_map) - set(stored), set(stored) - set(wanted_map)
                    # The citation is a stored column, so a membership that keeps
                    # its row and changes the page it cites is a write. Comparing
                    # id sets alone made that invisible, which is how the per-member
                    # source could have landed unannounced.
                    resourced = sorted(i for i in set(wanted_map) & set(stored) if wanted_map[i] != stored[i])
                    if added:
                        lines.append(f"    + {entry.name}: {len(added)} member(s) added to {table}")
                    if removed:
                        lines.append(f"    - {entry.name}: {len(removed)} member(s) REMOVED from {table}")
                    for mid in resourced:
                        old_src = stored[mid] or "(none)"
                        who = npc_id_to_name.get(mid, mid) if table == "group_npcs" else mid
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
