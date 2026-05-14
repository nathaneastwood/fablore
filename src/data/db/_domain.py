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
from dataclasses import dataclass, field
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
    canonical_id as _canonical_id,
    fauna_id_from_name,
    flora_id,
    food_drink_id,
    location_id as _location_id,
    lore_character_id,
    monster_id as _monster_id,
    region_row_id,
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


@dataclass
class NPCEntry:
    """A non-playable character to link to a story."""
    name: str
    species: str = "Unknown"
    status: str = "Unknown"


@dataclass
class RegionEntry:
    """A world region to link to a story (upserted into regions table)."""
    name: str
    world_of_rathe_story_key: str = ""


@dataclass
class LocationEntry:
    """A location to link to a story (upserted into locations table)."""
    name: str
    region: str = ""
    """Display name of the region — resolved to ``RegionId`` internally."""
    notes: str = ""
    lore_fragment: str = ""
    """mdBook heading anchor id for deep links, e.g. ``"grand-bazaar"``."""
    world_of_rathe_story_key: str = ""
    """Only needed when creating a new region via this location."""


@dataclass
class MonsterEntry:
    """A monster to link to a story (upserted into monsters table)."""
    name: str
    description: str = ""


@dataclass
class FaunaEntry:
    """A fauna entry to link to a story (upserted into fauna table)."""
    name: str
    description: str = ""


@dataclass
class FloraEntry:
    """A flora entry to link to a story (upserted into flora table)."""
    name: str
    description: str = ""


@dataclass
class FoodDrinkEntry:
    """A food or drink item to link to a story (upserted into food_and_drink table)."""
    name: str
    kind: str
    """Type category, e.g. ``"Drink"`` or ``"Food"``."""


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
            npcs=[NPCEntry("Guard Captain", species="Human")],
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
        self.conn = open_db(self._path)
        # Auto-seed when the database is empty
        count = self.conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        if count == 0 and self._path != Path(":memory:"):
            seed_from_csvs(self.conn, self._data_dir)

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
        """Return ``[{"name": …, "species": …, "status": …}]`` for all NPCs."""
        rows = q.select_all_npcs(self.conn)
        return [{"name": r["name"], "species": r["species"], "status": r["status"]}
                for r in rows]

    def print_npcs(self, *, file: IO[str] | None = None) -> None:
        """Pretty-print all NPCs with species and status."""
        self._print_table(self.list_npcs(), ["name", "species", "status"], file=file)

    def list_locations(self) -> list[dict[str, str]]:
        """Return ``[{"name": …, "region": …, "notes": …, "lore_fragment": …}]`` for all locations."""
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
        npcs: list[NPCEntry] | None = None,
        locations: list[LocationEntry] | None = None,
        regions: list[RegionEntry] | None = None,
        monsters: list[MonsterEntry] | None = None,
        fauna: list[FaunaEntry] | None = None,
        flora: list[FloraEntry] | None = None,
        food_drink: list[FoodDrinkEntry] | None = None,
        weapons: list[str] | None = None,
        equipment: list[str] | None = None,
        dry_run: bool = False,
    ) -> StoryRecord:
        """Register or update a story and declare its linked entities.

        Entity link parameters follow **replace semantics**:

        - ``None`` (default) — leave existing links of this type unchanged.
        - ``[]`` — remove all links of this type.
        - ``[...]`` — replace all links of this type with exactly this list.

        Args:
            path: Path to the ``*.md`` file under ``src/``.
            story_type: First ``src/`` path segment (e.g. ``"main-story"``).
            title: Human-readable title for the story.
            authors: Author credits (free text, comma-separated suggested).
            artists: Illustration credits (free text).
            source_link: Canonical source URL.
            publication_date: ISO date string e.g. ``"2025-07-12"``.
            thumbnail_image_link: Public URL for a thumbnail image.
            narrated_videos: Narrated video entries; ``None`` = leave unchanged.
            heroes: Canonical hero slugs (see :meth:`print_heroes`).
            npcs: NPC entries; strings in a future shorthand are not supported —
                use :class:`NPCEntry` directly.
            locations: Location entries.
            regions: Region entries (for stories that reference a region but no
                specific location within it).
            monsters: Monster entries.
            fauna: Fauna entries.
            flora: Flora entries.
            food_drink: Food and drink entries.
            weapons: Canonical weapon slugs (see :meth:`print_weapons`).
            equipment: Canonical equipment slugs (see :meth:`print_equipment`).
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
                npcs=npcs,
                locations=locations,
                regions=regions,
                monsters=monsters,
                fauna=fauna,
                flora=flora,
                food_drink=food_drink,
                weapon_ids=weapon_ids,
                equip_ids=equip_ids,
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
                    self.conn, story_id,
                    [(v.author, v.source_link) for v in narrated_videos],
                )
            if hero_ids is not None:
                q.set_story_junction(self.conn, story_id, "story_heroes", "canonical_id", hero_ids)
            if npcs is not None:
                npc_ids = self._upsert_npcs(npcs)
                q.set_story_junction(self.conn, story_id, "story_npcs", "character_id", npc_ids)
            if regions is not None:
                region_ids = self._upsert_regions(regions)
                q.set_story_junction(self.conn, story_id, "story_regions", "region_id", region_ids)
            if locations is not None:
                location_ids = self._upsert_locations(locations)
                q.set_story_junction(self.conn, story_id, "story_locations", "location_id", location_ids)
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
                q.set_story_junction(self.conn, story_id, "story_food_drink", "food_drink_id", fd_ids)
            if weapon_ids is not None:
                q.set_story_junction(self.conn, story_id, "story_weapons", "canonical_weapon_id", weapon_ids)
            if equip_ids is not None:
                q.set_story_junction(self.conn, story_id, "story_equipment", "canonical_equipment_id", equip_ids)

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
            return {"dry_run": dry_run, "story_key": story_key, "story_id": None,
                    "junctions": {}, "story_deleted": False}

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
            ("Heroes", "story_heroes", "canonical_id",
             "heroes_canonical", "canonical_id", "canonical_hero"),
            ("NPCs", "story_npcs", "character_id",
             "npcs", "character_id", "name"),
            ("Locations", "story_locations", "location_id",
             "locations", "location_id", "name"),
            ("Regions", "story_regions", "region_id",
             "regions", "region_id", "region_name"),
            ("Monsters", "story_monsters", "monster_id",
             "monsters", "monster_id", "name"),
            ("Fauna", "story_fauna", "fauna_id",
             "fauna", "fauna_id", "name"),
            ("Flora", "story_flora", "flora_id",
             "flora", "flora_id", "name"),
            ("Food & Drink", "story_food_drink", "food_drink_id",
             "food_and_drink", "food_drink_id", "name"),
            ("Weapons", "story_weapons", "canonical_weapon_id",
             "weapons_canonical", "canonical_weapon_id", "canonical_weapon"),
            ("Equipment", "story_equipment", "canonical_equipment_id",
             "equipment_canonical", "canonical_equipment_id", "canonical_equipment"),
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
                    f"Unknown weapon canonical slug: {slug!r}. "
                    "Call db.print_weapons() to see available slugs."
                )
            ids.append(row["canonical_weapon_id"])
        return ids

    def _resolve_equipment(self, slugs: list[str]) -> list[str]:
        ids: list[str] = []
        for slug in slugs:
            row = q.select_equipment_by_slug(self.conn, slug.strip())
            if row is None:
                raise ValueError(
                    f"Unknown equipment canonical slug: {slug!r}. "
                    "Call db.print_equipment() to see available slugs."
                )
            ids.append(row["canonical_equipment_id"])
        return ids

    def _upsert_npcs(self, entries: list[NPCEntry]) -> list[str]:
        # Guard against accidentally storing playable heroes as NPCs
        hero_names: set[str] = {
            normalize_name(r["name"]) for r in q.select_all_heroes_canonical(self.conn)
        }
        ids: list[str] = []
        for e in entries:
            norm = normalize_name(e.name)
            if norm in hero_names:
                raise ValueError(
                    f"Refusing NPC link for playable hero name: {e.name!r}"
                )
            cid = lore_character_id(e.name)
            q.upsert_npc(self.conn, character_id=cid, name=e.name,
                         species=e.species, status=e.status)
            ids.append(cid)
        return ids

    def _upsert_regions(self, entries: list[RegionEntry]) -> list[str]:
        ids: list[str] = []
        for e in entries:
            rid = region_row_id(e.name)
            wk = e.world_of_rathe_story_key or _auto_world_key(e.name)
            q.upsert_region(self.conn, region_id=rid, region_name=e.name,
                            world_of_rathe_story_key=wk)
            ids.append(rid)
        return ids

    def _upsert_locations(self, entries: list[LocationEntry]) -> list[str]:
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
            q.upsert_location(
                self.conn,
                location_id=lid,
                name=e.name,
                region_id=eff_region,
                notes=e.notes,
                lore_fragment=frag,
            )
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
                NarratedVideoEntry(author=v["author"], source_link=v["source_link"])
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
        npcs: list[NPCEntry] | None,
        locations: list[LocationEntry] | None,
        regions: list[RegionEntry] | None,
        monsters: list[MonsterEntry] | None,
        fauna: list[FaunaEntry] | None,
        flora: list[FloraEntry] | None,
        food_drink: list[FoodDrinkEntry] | None,
        weapon_ids: list[str] | None,
        equip_ids: list[str] | None,
        file: IO[str] | None = None,
    ) -> StoryRecord:
        import sys as _sys
        out = file or _sys.stdout

        existing = q.select_story_by_key(self.conn, story_key)
        op = "UPDATE" if existing else "INSERT"

        out.write(f"DRY RUN — {op} story\n")
        out.write(f"  StoryKey: {story_key}\n")
        out.write(f"  StoryId:  {story_id}\n")
        out.write(f"  Title:    {title}\n")
        out.write(f"  Type:     {story_type}\n")
        if authors:
            out.write(f"  Authors:  {authors}\n")
        if artists:
            out.write(f"  Artists:  {artists}\n")
        if publication_date:
            out.write(f"  Date:     {publication_date}\n")
        if source_link:
            out.write(f"  Source:   {source_link}\n")

        if narrated_videos is not None:
            out.write(f"  NarratedVideos: {len(narrated_videos)} entries\n")

        def _show_links(label: str, ids_or_entries: list | None) -> None:
            if ids_or_entries is None:
                return
            out.write(f"  {label}: {len(ids_or_entries)} link(s)\n")
            for item in ids_or_entries:
                if isinstance(item, str):
                    out.write(f"    + {item}\n")
                else:
                    out.write(f"    + {getattr(item, 'name', str(item))}\n")

        _show_links("Heroes", hero_ids)
        _show_links("NPCs", npcs)
        _show_links("Locations", locations)
        _show_links("Regions", regions)
        _show_links("Monsters", monsters)
        _show_links("Fauna", fauna)
        _show_links("Flora", flora)
        _show_links("Food & Drink", food_drink)
        _show_links("Weapons", weapon_ids)
        _show_links("Equipment", equip_ids)

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
