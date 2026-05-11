"""Story-centric API for ``stories.csv``, registry CSVs, and ``story-*.csv`` junctions.

``StoryKey`` is the Markdown path under ``src/`` (POSIX, ending in ``.md``): it is a
human-facing navigation hint and doubles as the input to :func:`registry_ids.story_id`.
``StoryId`` (``ST`` + hash) is the **only** stable relational key: every ``story-*.csv``
row stores ``StoryId``, not ``StoryKey``. If you move or rename a story file, update
``stories.csv`` and any tooling that still matched on path; preprocessors or other
consumers should join registries on ``StoryId`` and treat ``StoryKey`` as display or
link construction only.

Instantiate with a path under ``src/`` plus ``StoryType`` and ``Title``. If the story
is missing from ``stories.csv``, it is inserted with a deterministic ``StoryId``.
Existing stories load current junction links into :attr:`links`.

Use ``link_*`` methods to upsert registry rows (when applicable) and append
``(StoryId, entity id)`` junction rows without duplicates. ``link_location`` can
upsert ``regions.csv`` when you name a region. ``link_weapon`` / ``link_equipment``
resolve ``canonical_slug`` against the canonical weapon / equipment CSVs (same idea
as ``link_hero``).

Use :meth:`Story.remove` to drop this story from ``stories.csv`` and strip its rows
from ``story-*.csv`` junction files (optionally with ``dry_run=True`` to preview).

Paths are resolved relative to the repository root when needed.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from typing import IO, Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from npc_lore import (
    HEROES_CANONICAL_CSV_PATH,
    build_hero_match_keys,
    load_canonical_hero_names,
    read_npc_rows,
    row_name_matches_hero,
    write_npc_rows,
)
from pipe_csv_io import (
    REGENERATE_CREATE_STORIES_INDEX,
    REGENERATE_HEROES_CANONICAL,
    REGENERATE_STORY_CLASS,
    REGENERATE_STORY_JUNCTIONS,
    REGENERATE_STORY_REGISTRY,
    auto_gen_banner,
    read_pipe_csv,
    write_pipe_csv_autogen,
)
from registry_ids import (
    canonical_id,
    fauna_id_from_name,
    flora_id,
    food_drink_id,
    location_id,
    lore_character_id,
    monster_id,
    region_row_id,
    story_id as compute_story_id,
)

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DATA = ROOT / "src/data"

STORIES_PATH = DATA / "stories.csv"
WEAPONS_CANONICAL_CSV_PATH = DATA / "weapons-canonical.csv"
EQUIPMENT_CANONICAL_CSV_PATH = DATA / "equipment-canonical.csv"

# ``self.links`` keys, junction filenames under :data:`DATA`, and entity id column.
# Paths are **not** pre-bound so tests (and any runtime ``DATA`` reassignment) resolve correctly.
_STORY_JUNCTION_LINK_SPECS: tuple[tuple[str, str, str], ...] = (
    ("npcs", "story-npcs.csv", "CharacterId"),
    ("heroes", "story-heroes.csv", "CanonicalId"),
    ("locations", "story-locations.csv", "LocationId"),
    ("monsters", "story-monsters.csv", "MonsterId"),
    ("fauna", "story-fauna.csv", "FaunaId"),
    ("flora", "story-flora.csv", "FloraId"),
    ("food_drink", "story-food-drink.csv", "FoodDrinkId"),
    ("weapons", "story-weapons.csv", "CanonicalWeaponId"),
    ("equipment", "story-equipment.csv", "CanonicalEquipmentId"),
)

_MAX_REMOVE_PREVIEW_ROWS = 40


def story_key_from_path(markdown_path: str | Path) -> str:
    """Return ``StoryKey``: path relative to ``src/``, POSIX ``/``, ending in ``.md``.

    This string is for humans, URLs, and ``stories.csv`` lookup; junction CSVs join on
    :func:`registry_ids.story_id` instead.

    Args:
        markdown_path: Absolute or repo-relative path to a file under ``src/``.

    Returns:
        Normalized story key.

    Raises:
        ValueError: If the path is not under ``src/`` or does not end with ``.md``.
    """
    path = Path(markdown_path).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    try:
        rel = path.relative_to(SRC.resolve())
    except ValueError as exc:
        raise ValueError(f"Story path must be under {SRC}: {path}") from exc
    key = rel.as_posix()
    if not key.endswith(".md"):
        raise ValueError(f"Story path must be a .md file: {key}")
    return key


def _write_junction_pairs(
    path: Path,
    header: list[str],
    pairs: set[tuple[str, str]],
) -> None:
    """Write pipe CSV with banner, header, and sorted ``StoryId`` + entity id rows."""
    width = len(header)
    padded: list[list[str]] = []
    for row in sorted(pairs):
        r = list(row)
        while len(r) < width:
            r.append("")
        padded.append(r[:width])
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(auto_gen_banner(REGENERATE_STORY_JUNCTIONS))
        w = csv.writer(f, delimiter="|", lineterminator="\n")
        w.writerow(header)
        w.writerows(padded)


def _load_junction_pairs(
    path: Path, entity_col: str
) -> tuple[set[tuple[str, str]], dict[str, set[str]]]:
    """Return all ``(StoryId, entity id)`` pairs and map StoryId -> set of entity ids."""
    pairs: set[tuple[str, str]] = set()
    by_story: dict[str, set[str]] = {}
    fieldnames, rows = read_pipe_csv(path)
    if not fieldnames or "StoryId" not in fieldnames:
        return pairs, by_story
    if entity_col not in fieldnames:
        return pairs, by_story
    for row in rows:
        sid = (row.get("StoryId") or "").strip()
        eid = (row.get(entity_col) or "").strip()
        if sid and eid:
            pairs.add((sid, eid))
            by_story.setdefault(sid, set()).add(eid)
    return pairs, by_story


def _merge_junction_link(
    path: Path,
    header: list[str],
    entity_col: str,
    story_id_val: str,
    entity_id: str,
) -> None:
    """Upsert one story ↔ entity row (replace duplicate StoryId + entity id pair)."""
    pairs, _ = _load_junction_pairs(path, entity_col)
    pairs = {(a, b) for (a, b) in pairs if not (a == story_id_val and b == entity_id)}
    pairs.add((story_id_val, entity_id))
    _write_junction_pairs(path, header, pairs)


def _index_by_column(path: Path, key_column: str) -> dict[str, dict[str, str]]:
    """Build a lookup from primary-key column to row dict."""
    _, rows = read_pipe_csv(path)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        k = (row.get(key_column) or "").strip()
        if k:
            out[k] = row
    return out


def _junction_rows_for_story(
    path: Path, story_id_val: str, entity_col: str
) -> list[dict[str, str]]:
    """Return junction rows for ``story_id_val``, sorted by entity id."""
    _, rows = read_pipe_csv(path)
    matched = [
        r
        for r in rows
        if (r.get("StoryId") or "").strip() == story_id_val
        and (r.get(entity_col) or "").strip()
    ]
    return sorted(matched, key=lambda r: (r.get(entity_col) or "").lower())


def _trunc(text: str, max_len: int = 160) -> str:
    """Ellipsize long free text for terminal display."""
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def _write_pipe_csv_plain(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    *,
    regenerate_command: str | None = None,
) -> None:
    """Write pipe-delimited CSV; optional first-line auto-generation banner.

    Args:
        path: Destination path.
        fieldnames: Header column order.
        rows: Data rows as dicts keyed by field names.
        regenerate_command: When set, prepends :func:`pipe_csv_io.auto_gen_banner`
            with this instruction (same pattern as other generated CSVs).
    """
    with path.open("w", newline="", encoding="utf-8") as f:
        if regenerate_command:
            f.write(auto_gen_banner(regenerate_command))
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="|",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _partition_rows_by_column(
    rows: list[dict[str, str]],
    column: str,
    match: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Split rows into those whose ``column`` equals ``match`` and the rest."""
    removed: list[dict[str, str]] = []
    kept: list[dict[str, str]] = []
    for row in rows:
        if (row.get(column) or "").strip() == match:
            removed.append(row)
        else:
            kept.append(row)
    return removed, kept


def _format_row_preview(fieldnames: list[str], row: dict[str, str]) -> str:
    """Single-line pipe preview for terminal output."""
    return "|".join((row.get(k) or "").strip() for k in fieldnames)


class Story:
    """Register or load a story and link entities via junction CSVs."""

    def __init__(
        self,
        markdown_path: str | Path,
        story_type: str,
        title: str,
        *,
        run_validate: bool = False,
    ) -> None:
        """Ensure ``stories.csv`` has this story and load junction ids for it.

        Args:
            markdown_path: Path to the ``*.md`` file under ``src/``.
            story_type: First path segment under ``src/`` for this file (e.g. ``main-story``).
                Must match ``validate_data.ALLOWED_STORY_TYPES`` so ``stories.csv`` passes validation.
            title: Human-readable title stored in ``stories.csv``.
            run_validate: If True, run ``validate_data.py`` after updating ``stories.csv``.
        """
        self.story_key = story_key_from_path(markdown_path)
        self.story_type = story_type.strip()
        self.title = title.strip()
        self.story_id = compute_story_id(self.story_key)

        self.links: dict[str, set[str]] = {
            "npcs": set(),
            "heroes": set(),
            "locations": set(),
            "monsters": set(),
            "fauna": set(),
            "flora": set(),
            "food_drink": set(),
            "weapons": set(),
            "equipment": set(),
        }

        self._ensure_story_row(run_validate=run_validate)
        self._load_links()

    def _ensure_story_row(self, *, run_validate: bool) -> None:
        fieldnames, rows = read_pipe_csv(STORIES_PATH)
        if not fieldnames:
            fieldnames = ["StoryId", "StoryKey", "StoryType", "Title"]
        by_key = {(r.get("StoryKey") or "").strip(): r for r in rows}
        if self.story_key in by_key:
            row = by_key[self.story_key]
            row["StoryType"] = self.story_type
            row["Title"] = self.title
            row["StoryId"] = self.story_id
        else:
            rows.append(
                {
                    "StoryId": self.story_id,
                    "StoryKey": self.story_key,
                    "StoryType": self.story_type,
                    "Title": self.title,
                }
            )
        rows.sort(key=lambda r: (r.get("StoryKey") or ""))
        write_pipe_csv_autogen(
            STORIES_PATH,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_CREATE_STORIES_INDEX,
        )
        if run_validate:
            self.validate()

    def _load_links(self) -> None:
        sid = self.story_id
        for key, fname, col in _STORY_JUNCTION_LINK_SPECS:
            _, by_story = _load_junction_pairs(DATA / fname, col)
            self.links[key] = set(by_story.get(sid, set()))

    def display(self, *, file: IO[str] | None = None) -> None:
        """Print a human-readable summary of this story and linked entities.

        Joins junction rows for :attr:`story_id` to registry CSVs (names,
        descriptions, and each location's ``Notes`` field from ``locations.csv`` when
        set). Reloads data from disk so output matches committed CSVs.

        Args:
            file: Text stream to write to (default ``sys.stdout``).
        """
        out = file if file is not None else sys.stdout
        sid = self.story_id
        lines: list[str] = [
            f"Title:    {self.title}",
            f"StoryKey: {self.story_key}",
            f"StoryId:  {sid}",
            f"Type:     {self.story_type}",
            "",
        ]

        npc_by_id = _index_by_column(DATA / "npcs.csv", "CharacterId")
        hero_by_id = _index_by_column(HEROES_CANONICAL_CSV_PATH, "CanonicalId")
        loc_by_id = _index_by_column(DATA / "locations.csv", "LocationId")
        region_by_id = _index_by_column(DATA / "regions.csv", "RegionId")
        monster_by_id = _index_by_column(DATA / "monsters.csv", "MonsterId")
        fauna_by_id = _index_by_column(DATA / "fauna.csv", "FaunaId")
        flora_by_id = _index_by_column(DATA / "flora.csv", "FloraId")
        food_by_id = _index_by_column(DATA / "food-and-drink.csv", "FoodDrinkId")
        weapon_by_id = _index_by_column(WEAPONS_CANONICAL_CSV_PATH, "CanonicalWeaponId")
        equipment_by_id = _index_by_column(
            EQUIPMENT_CANONICAL_CSV_PATH, "CanonicalEquipmentId"
        )

        # --- NPCs
        lines.append("NPCs")
        jnpc = _junction_rows_for_story(DATA / "story-npcs.csv", sid, "CharacterId")
        if not jnpc:
            lines.append("  (none)")
        else:
            for jr in jnpc:
                cid = (jr.get("CharacterId") or "").strip()
                row = npc_by_id.get(cid, {})
                name = (row.get("Name") or cid).strip()
                spec = (row.get("Species") or "").strip()
                stat = (row.get("Status") or "").strip()
                meta = ", ".join(p for p in (spec, stat) if p) or "—"
                lines.append(f"  • {name} ({meta})")
        lines.append("")

        # --- Heroes (canonical)
        lines.append("Heroes")
        jh = _junction_rows_for_story(DATA / "story-heroes.csv", sid, "CanonicalId")
        if not jh:
            lines.append("  (none)")
        else:
            for jr in jh:
                hid = (jr.get("CanonicalId") or "").strip()
                row = hero_by_id.get(hid, {})
                disp = (row.get("CanonicalHero") or "").strip() or hid
                slug = (row.get("CanonicalSlug") or "").strip()
                slug_part = f" [{slug}]" if slug else ""
                lines.append(f"  • {disp}{slug_part}")
        lines.append("")

        # --- Locations
        lines.append("Locations")
        jl = _junction_rows_for_story(DATA / "story-locations.csv", sid, "LocationId")
        if not jl:
            lines.append("  (none)")
        else:
            for jr in jl:
                lid = (jr.get("LocationId") or "").strip()
                row = loc_by_id.get(lid, {})
                name = (row.get("Name") or "").strip() or lid
                rid = (row.get("RegionId") or "").strip()
                rname = (region_by_id.get(rid, {}) or {}).get("RegionName", "").strip()
                region_part = f" — region: {rname} ({rid})" if rid else ""
                loc_notes = (row.get("Notes") or "").strip()
                notes_part = f" — { _trunc(loc_notes, 100)}" if loc_notes else ""
                lines.append(f"  • {name}{region_part}{notes_part}")
        lines.append("")

        # --- Monsters
        lines.append("Monsters")
        jm = _junction_rows_for_story(DATA / "story-monsters.csv", sid, "MonsterId")
        if not jm:
            lines.append("  (none)")
        else:
            for jr in jm:
                mid = (jr.get("MonsterId") or "").strip()
                row = monster_by_id.get(mid, {})
                name = (row.get("Name") or "").strip() or mid
                desc = (row.get("Description") or "").strip()
                desc_part = f": {_trunc(desc)}" if desc else ""
                lines.append(f"  • {name}{desc_part}")
        lines.append("")

        # --- Fauna
        lines.append("Fauna")
        jfa = _junction_rows_for_story(DATA / "story-fauna.csv", sid, "FaunaId")
        if not jfa:
            lines.append("  (none)")
        else:
            for jr in jfa:
                fid = (jr.get("FaunaId") or "").strip()
                row = fauna_by_id.get(fid, {})
                name = (row.get("Name") or "").strip() or fid
                desc = (row.get("Description") or "").strip()
                desc_part = f": {_trunc(desc)}" if desc else ""
                lines.append(f"  • {name}{desc_part}")
        lines.append("")

        # --- Flora
        lines.append("Flora")
        jfl = _junction_rows_for_story(DATA / "story-flora.csv", sid, "FloraId")
        if not jfl:
            lines.append("  (none)")
        else:
            for jr in jfl:
                fid = (jr.get("FloraId") or "").strip()
                row = flora_by_id.get(fid, {})
                name = (row.get("Name") or "").strip() or fid
                desc = (row.get("Description") or "").strip()
                desc_part = f": {_trunc(desc)}" if desc else ""
                lines.append(f"  • {name}{desc_part}")
        lines.append("")

        # --- Food & drink
        lines.append("Food & drink")
        jfd = _junction_rows_for_story(DATA / "story-food-drink.csv", sid, "FoodDrinkId")
        if not jfd:
            lines.append("  (none)")
        else:
            for jr in jfd:
                fdid = (jr.get("FoodDrinkId") or "").strip()
                row = food_by_id.get(fdid, {})
                name = (row.get("Name") or "").strip() or fdid
                kind = (row.get("Type") or "").strip()
                kind_part = f" ({kind})" if kind else ""
                lines.append(f"  • {name}{kind_part}")
        lines.append("")

        # --- Weapons (canonical)
        lines.append("Weapons")
        jw = _junction_rows_for_story(DATA / "story-weapons.csv", sid, "CanonicalWeaponId")
        if not jw:
            lines.append("  (none)")
        else:
            for jr in jw:
                wid = (jr.get("CanonicalWeaponId") or "").strip()
                row = weapon_by_id.get(wid, {})
                disp = (row.get("CanonicalWeapon") or "").strip() or wid
                slug = (row.get("CanonicalSlug") or "").strip()
                slug_part = f" [{slug}]" if slug else ""
                lines.append(f"  • {disp}{slug_part}")
        lines.append("")

        # --- Equipment (canonical)
        lines.append("Equipment")
        je = _junction_rows_for_story(
            DATA / "story-equipment.csv", sid, "CanonicalEquipmentId"
        )
        if not je:
            lines.append("  (none)")
        else:
            for jr in je:
                eid = (jr.get("CanonicalEquipmentId") or "").strip()
                row = equipment_by_id.get(eid, {})
                disp = (row.get("CanonicalEquipment") or "").strip() or eid
                slug = (row.get("CanonicalSlug") or "").strip()
                slug_part = f" [{slug}]" if slug else ""
                lines.append(f"  • {disp}{slug_part}")
        lines.append("")

        out.write("\n".join(lines) + "\n")

    #: Alias for :meth:`display`.
    view = display

    def validate(self) -> int:
        """Run ``validate_data.py``; return exit code."""
        vd = DATA / "validate_data.py"
        rc = subprocess.run([sys.executable, str(vd)], cwd=str(ROOT))
        return rc.returncode

    def remove(
        self,
        *,
        dry_run: bool = False,
        run_validate: bool = False,
        file: IO[str] | None = None,
    ) -> dict[str, Any]:
        """Remove this story from ``stories.csv`` and all ``story-*.csv`` junction rows.

        Deletes every junction row whose ``StoryId`` matches :attr:`story_id` and
        removes the ``stories.csv`` row for :attr:`story_key`. Does **not** delete
        the markdown file under ``src/``.

        Args:
            dry_run: If True, print a report and return counts without modifying files.
            run_validate: If True, run :meth:`validate` after a successful non-dry run.
            file: Text stream for the report (default ``sys.stdout``).

        Returns:
            Dict with ``dry_run``, ``story_key``, ``story_id``, and ``files``: filename
            -> ``{"removed_count": int, "removed_rows": list[dict[str, str]]}``.
        """
        out = file if file is not None else sys.stdout
        sid = self.story_id
        sk = self.story_key

        files_report: dict[str, dict[str, Any]] = {}

        # --- stories.csv (match StoryKey)
        s_fieldnames, s_rows = read_pipe_csv(STORIES_PATH)
        if not s_fieldnames:
            s_fieldnames = ["StoryId", "StoryKey", "StoryType", "Title"]
        s_removed, s_kept = _partition_rows_by_column(s_rows, "StoryKey", sk)
        files_report["stories.csv"] = {
            "removed_count": len(s_removed),
            "removed_rows": s_removed,
        }

        # --- StoryId junctions
        for _, fname, _ in _STORY_JUNCTION_LINK_SPECS:
            jpath = DATA / fname
            name = fname
            fn, rows = read_pipe_csv(jpath)
            removed, kept = _partition_rows_by_column(rows, "StoryId", sid)
            files_report[name] = {
                "removed_count": len(removed),
                "removed_rows": removed,
                "_kept_rows": kept,
                "_fieldnames": fn,
            }

        headline = (
            "DRY RUN — no files modified\n" if dry_run else "Removed story data\n"
        )
        out.write(headline)
        out.write(f"StoryKey: {sk}\nStoryId:  {sid}\n\n")

        shown_any = False
        for fname in sorted(files_report.keys()):
            entry = files_report[fname]
            n = entry["removed_count"]
            if n == 0:
                continue
            shown_any = True
            out.write(f"{fname}: {n} row(s)\n")
            rows_rm: list[dict[str, str]] = entry["removed_rows"]
            fnames = (
                s_fieldnames
                if fname == "stories.csv"
                else (entry.get("_fieldnames") or [])
            )
            preview_cap = _MAX_REMOVE_PREVIEW_ROWS
            for i, row in enumerate(rows_rm):
                if i >= preview_cap:
                    out.write(f"  … {len(rows_rm) - preview_cap} more row(s)\n")
                    break
                out.write(f"  - {_format_row_preview(fnames, row)}\n")
            out.write("\n")

        if not shown_any:
            out.write(
                "(No matching rows — story may already be absent from data files.)\n\n"
            )

        clean_report: dict[str, Any] = {
            "dry_run": dry_run,
            "story_key": sk,
            "story_id": sid,
            "files": {
                fn: {
                    "removed_count": files_report[fn]["removed_count"],
                    "removed_rows": files_report[fn]["removed_rows"],
                }
                for fn in files_report
            },
        }

        if dry_run:
            return clean_report

        total_removed = sum(entry["removed_count"] for entry in files_report.values())
        if total_removed == 0:
            return clean_report

        # Persist junction files first, then ``stories.csv`` (bannered).
        for _, fname, _ in _STORY_JUNCTION_LINK_SPECS:
            jpath = DATA / fname
            name = fname
            entry = files_report[name]
            if entry["removed_count"] == 0:
                continue
            fn = entry["_fieldnames"]
            kept = entry["_kept_rows"]
            if fn:
                _write_pipe_csv_plain(
                    jpath, fn, kept, regenerate_command=REGENERATE_STORY_JUNCTIONS
                )

        if len(s_removed) > 0:
            write_pipe_csv_autogen(
                STORIES_PATH,
                s_fieldnames,
                s_kept,
                regenerate_command=REGENERATE_STORY_CLASS,
            )

        self.links = {k: set() for k in self.links}
        if run_validate:
            self.validate()

        return clean_report

    # --- Registry + junction helpers -------------------------------------------------

    def link_npc(
        self,
        name: str,
        *,
        species: str = "Unknown",
        status: str = "Unknown",
    ) -> str:
        """Upsert ``npcs.csv`` and ``story-npcs.csv``.

        Returns:
            ``CharacterId``.
        """
        hero_keys = build_hero_match_keys(load_canonical_hero_names(HEROES_CANONICAL_CSV_PATH))
        if row_name_matches_hero(name, hero_keys):
            raise ValueError(f"Refusing NPC link for playable hero name: {name!r}")

        cid = lore_character_id(name)
        mob_rows = read_npc_rows()
        existing = next((r for r in mob_rows if r["CharacterId"] == cid), None)
        if existing is None:
            mob_rows.append(
                {
                    "CharacterId": cid,
                    "Name": name.strip(),
                    "Species": species.strip(),
                    "Status": status.strip(),
                }
            )
        write_npc_rows(mob_rows)

        _merge_junction_link(
            DATA / "story-npcs.csv",
            ["StoryId", "CharacterId"],
            "CharacterId",
            self.story_id,
            cid,
        )
        self.links["npcs"].add(cid)
        return cid

    def link_hero(self, *, canonical_slug: str | None = None) -> str:
        """Link an existing canonical hero by ``CanonicalSlug``. Returns ``CanonicalId``."""
        if not canonical_slug or not canonical_slug.strip():
            raise ValueError("canonical_slug is required")
        slug = canonical_slug.strip()
        fieldnames, rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)
        cid = ""
        for row in rows:
            if (row.get("CanonicalSlug") or "").strip() == slug:
                cid = (row.get("CanonicalId") or "").strip()
                break
        if not cid:
            raise ValueError(f"Unknown CanonicalSlug: {slug!r}")
        _merge_junction_link(
            DATA / "story-heroes.csv",
            ["StoryId", "CanonicalId"],
            "CanonicalId",
            self.story_id,
            cid,
        )
        self.links["heroes"].add(cid)
        return cid

    def add_canonical_hero(self, canonical_slug: str, canonical_hero: str) -> str:
        """Insert or update a row in ``heroes-canonical.csv`` and link this story.

        ``CanonicalId`` is recomputed from ``canonical_slug`` (same rule as
        ``create_heroes_csv``). This method does **not** run ``create_heroes_csv.py``.

        Note:
            Prints a reminder to run ``create_heroes_csv.py``. After adding or changing
            a canonical hero, run ``python3 src/data/create_heroes_csv.py`` when you need
            ``heroes-game.csv``, ``heroes-printings.csv``, ``classes.csv`` / ``talents.csv``, or other
            outputs regenerated from card data.
        """
        slug = canonical_slug.strip()
        display = canonical_hero.strip()
        if not slug or not display:
            raise ValueError("canonical_slug and canonical_hero are required")
        hid = canonical_id(slug)
        fieldnames, rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)
        if not fieldnames:
            fieldnames = ["CanonicalId", "CanonicalSlug", "CanonicalHero"]
        found = False
        for row in rows:
            if (row.get("CanonicalSlug") or "").strip() == slug:
                row["CanonicalId"] = hid
                row["CanonicalHero"] = display
                found = True
                break
        if not found:
            rows.append(
                {"CanonicalId": hid, "CanonicalSlug": slug, "CanonicalHero": display}
            )
        rows.sort(key=lambda r: (r.get("CanonicalSlug") or "").lower())
        write_pipe_csv_autogen(
            HEROES_CANONICAL_CSV_PATH,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_HEROES_CANONICAL,
        )

        _merge_junction_link(
            DATA / "story-heroes.csv",
            ["StoryId", "CanonicalId"],
            "CanonicalId",
            self.story_id,
            hid,
        )
        self.links["heroes"].add(hid)
        print(
            "Reminder: regenerate hero game CSVs from card data when needed:\n"
            "  python3 src/data/create_heroes_csv.py"
        )
        return hid

    def link_monster(self, name: str, description: str = "") -> str:
        """Upsert ``monsters.csv`` and ``story-monsters.csv``."""
        mid = monster_id(name)
        fn = ["MonsterId", "Name", "Description"]
        fieldnames, rows = read_pipe_csv(DATA / "monsters.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("MonsterId") or "").strip() == mid:
                row["Name"] = name.strip()
                row["Description"] = description.strip()
                found = True
                break
        if not found:
            rows.append(
                {"MonsterId": mid, "Name": name.strip(), "Description": description.strip()}
            )
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            DATA / "monsters.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

        _merge_junction_link(
            DATA / "story-monsters.csv",
            ["StoryId", "MonsterId"],
            "MonsterId",
            self.story_id,
            mid,
        )
        self.links["monsters"].add(mid)
        return mid

    def link_fauna(self, name: str, description: str = "") -> str:
        """Upsert ``fauna.csv`` and ``story-fauna.csv``."""
        fid = fauna_id_from_name(name)
        fn = ["FaunaId", "Name", "Description"]
        fieldnames, rows = read_pipe_csv(DATA / "fauna.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("FaunaId") or "").strip() == fid:
                row["Name"] = name.strip()
                row["Description"] = description.strip()
                found = True
                break
        if not found:
            rows.append(
                {"FaunaId": fid, "Name": name.strip(), "Description": description.strip()}
            )
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            DATA / "fauna.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

        _merge_junction_link(
            DATA / "story-fauna.csv",
            ["StoryId", "FaunaId"],
            "FaunaId",
            self.story_id,
            fid,
        )
        self.links["fauna"].add(fid)
        return fid

    def link_flora(self, name: str, description: str = "") -> str:
        """Upsert ``flora.csv`` and ``story-flora.csv``."""
        fid = flora_id(name)
        fn = ["FloraId", "Name", "Description"]
        fieldnames, rows = read_pipe_csv(DATA / "flora.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("FloraId") or "").strip() == fid:
                row["Name"] = name.strip()
                row["Description"] = description.strip()
                found = True
                break
        if not found:
            rows.append(
                {"FloraId": fid, "Name": name.strip(), "Description": description.strip()}
            )
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            DATA / "flora.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

        _merge_junction_link(
            DATA / "story-flora.csv",
            ["StoryId", "FloraId"],
            "FloraId",
            self.story_id,
            fid,
        )
        self.links["flora"].add(fid)
        return fid

    def link_food_drink(self, name: str, food_type: str) -> str:
        """Upsert ``food-and-drink.csv`` and ``story-food-drink.csv``."""
        fdid = food_drink_id(name, food_type)
        fn = ["FoodDrinkId", "Name", "Type"]
        fieldnames, rows = read_pipe_csv(DATA / "food-and-drink.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("FoodDrinkId") or "").strip() == fdid:
                row["Name"] = name.strip()
                row["Type"] = food_type.strip()
                found = True
                break
        if not found:
            rows.append(
                {"FoodDrinkId": fdid, "Name": name.strip(), "Type": food_type.strip()}
            )
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            DATA / "food-and-drink.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

        _merge_junction_link(
            DATA / "story-food-drink.csv",
            ["StoryId", "FoodDrinkId"],
            "FoodDrinkId",
            self.story_id,
            fdid,
        )
        self.links["food_drink"].add(fdid)
        return fdid

    def _upsert_region_registry_row(
        self,
        region_id: str,
        region_name: str,
        world_of_rathe_story_key: str,
    ) -> None:
        """Upsert one row in ``regions.csv`` for a named region."""
        rid = region_id.strip()
        rn = region_name.strip()
        wk = world_of_rathe_story_key.strip()
        fn = ["RegionId", "RegionName", "WorldOfRatheStoryKey"]
        fieldnames, rows = read_pipe_csv(DATA / "regions.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("RegionId") or "").strip() == rid:
                row["RegionName"] = rn
                if wk:
                    row["WorldOfRatheStoryKey"] = wk
                found = True
                break
        if not found:
            rows.append(
                {
                    "RegionId": rid,
                    "RegionName": rn,
                    "WorldOfRatheStoryKey": wk,
                }
            )
        rows.sort(key=lambda r: (r.get("RegionName") or "").lower())
        write_pipe_csv_autogen(
            DATA / "regions.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

    def link_location(
        self,
        name: str,
        region_id: str = "",
        *,
        region_name: str = "",
        world_of_rathe_story_key: str = "",
        location_notes: str = "",
    ) -> str:
        """Upsert ``locations.csv``, optionally ``regions.csv``, and ``story-locations.csv``.

        A location may omit a region (unknown): leave ``region_id`` and ``region_name``
        unset. When the region is known, pass ``region_name`` to upsert ``regions.csv``
        (deterministic ``RegionId`` via :func:`registry_ids.region_row_id`) and set the
        location's ``RegionId``. Pass ``region_id`` alone only if that id already exists
        in ``regions.csv``. If both ``region_id`` and ``region_name`` are set, they must
        agree (``region_id`` must equal ``region_row_id(region_name)``).

        Args:
            name: Location display name.
            region_id: Existing ``RegionId`` when not passing ``region_name``.
            region_name: When set, upserts ``regions.csv`` and defines the location's region.
            world_of_rathe_story_key: Optional ``WorldOfRatheStoryKey`` when upserting by name.
            location_notes: Optional ``Notes`` on ``locations.csv``.

        Returns:
            ``LocationId`` for this name and resolved region (possibly empty region).
        """
        rn = region_name.strip()
        ri = region_id.strip()
        wk = world_of_rathe_story_key.strip()

        if rn:
            computed = region_row_id(rn)
            if ri and computed != ri:
                raise ValueError(
                    f"region_id {ri!r} does not match region_name {rn!r} "
                    f"(expected RegionId {computed!r})"
                )
            eff_region = computed
            self._upsert_region_registry_row(eff_region, rn, wk)
        elif ri:
            _rfn, reg_rows = read_pipe_csv(DATA / "regions.csv")
            reg_ids = {(r.get("RegionId") or "").strip() for r in reg_rows}
            if ri not in reg_ids:
                raise ValueError(
                    f"region_id {ri!r} not in regions.csv; pass region_name=... to create it."
                )
            eff_region = ri
        else:
            eff_region = ""

        rid = location_id(name, eff_region)
        fn = ["LocationId", "Name", "RegionId", "Notes"]
        fieldnames, rows = read_pipe_csv(DATA / "locations.csv")
        if not fieldnames:
            fieldnames = fn
        found = False
        for row in rows:
            if (row.get("LocationId") or "").strip() == rid:
                row["Name"] = name.strip()
                row["RegionId"] = eff_region
                row["Notes"] = location_notes.strip()
                found = True
                break
        if not found:
            rows.append(
                {
                    "LocationId": rid,
                    "Name": name.strip(),
                    "RegionId": eff_region,
                    "Notes": location_notes.strip(),
                }
            )
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            DATA / "locations.csv",
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )

        _merge_junction_link(
            DATA / "story-locations.csv",
            ["StoryId", "LocationId"],
            "LocationId",
            self.story_id,
            rid,
        )
        self.links["locations"].add(rid)
        return rid

    def link_weapon(self, *, canonical_slug: str | None = None) -> str:
        """Link an existing canonical weapon by ``CanonicalSlug``.

        Returns:
            ``CanonicalWeaponId`` written to ``story-weapons.csv``.
        """
        if not canonical_slug or not canonical_slug.strip():
            raise ValueError("canonical_slug is required")
        slug = canonical_slug.strip()
        _, rows = read_pipe_csv(WEAPONS_CANONICAL_CSV_PATH)
        wid = ""
        for row in rows:
            if (row.get("CanonicalSlug") or "").strip() == slug:
                wid = (row.get("CanonicalWeaponId") or "").strip()
                break
        if not wid:
            raise ValueError(f"Unknown weapon CanonicalSlug: {slug!r}")
        _merge_junction_link(
            DATA / "story-weapons.csv",
            ["StoryId", "CanonicalWeaponId"],
            "CanonicalWeaponId",
            self.story_id,
            wid,
        )
        self.links["weapons"].add(wid)
        return wid

    def link_equipment(self, *, canonical_slug: str | None = None) -> str:
        """Link an existing canonical equipment card by ``CanonicalSlug``.

        Returns:
            ``CanonicalEquipmentId`` written to ``story-equipment.csv``.
        """
        if not canonical_slug or not canonical_slug.strip():
            raise ValueError("canonical_slug is required")
        slug = canonical_slug.strip()
        _, rows = read_pipe_csv(EQUIPMENT_CANONICAL_CSV_PATH)
        eid = ""
        for row in rows:
            if (row.get("CanonicalSlug") or "").strip() == slug:
                eid = (row.get("CanonicalEquipmentId") or "").strip()
                break
        if not eid:
            raise ValueError(f"Unknown equipment CanonicalSlug: {slug!r}")
        _merge_junction_link(
            DATA / "story-equipment.csv",
            ["StoryId", "CanonicalEquipmentId"],
            "CanonicalEquipmentId",
            self.story_id,
            eid,
        )
        self.links["equipment"].add(eid)
        return eid


def main() -> None:
    """Minimal demo / smoke: ``python3 src/data/story.py`` prints resolved StoryKey."""
    import argparse

    p = argparse.ArgumentParser(description="Resolve StoryKey from a path (debug helper).")
    p.add_argument("markdown_path", help="Path to a .md file under src/")
    args = p.parse_args()
    print(story_key_from_path(args.markdown_path))


if __name__ == "__main__":
    main()
