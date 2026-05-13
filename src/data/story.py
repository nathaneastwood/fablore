"""Story-centric API for ``stories.csv``, registry CSVs, and ``story-*.csv`` junctions.

``StoryKey`` is the Markdown path under ``src/`` (POSIX, ending in ``.md``): it is a
human-facing navigation hint and doubles as the input to :func:`registry_ids.story_id`.
``StoryId`` (``ST`` + hash) is the **only** stable relational key: every ``story-*.csv``
row stores ``StoryId``, not ``StoryKey``. If you move or rename a story file, update
``stories.csv`` and any tooling that still matched on path; preprocessors or other
consumers should join registries on ``StoryId`` and treat ``StoryKey`` as display or
link construction only.

Instantiate with a path under ``src/`` plus ``StoryType`` and ``Title``. Optional
metadata fields are written to ``stories.csv``: ``Authors``, ``Illustrators``,
``SourceLink``, ``PublicationDate``, ``ThumbnailImageLink``, and
``NarratedVideos`` (JSON list of ``{"author","url"}``). If the story is missing
from ``stories.csv``, it is inserted with a deterministic ``StoryId``. Existing
stories load current junction links into :attr:`links`.

Use ``link_*`` methods to upsert registry rows (when applicable) and append
``(StoryId, entity id)`` junction rows without duplicates. ``link_location`` can
upsert ``regions.csv`` when you name a region, and optionally set ``LoreFragment`` on
``locations.csv`` (heading id for deep links into ``WorldOfRatheStoryKey`` pages).
``link_weapon`` / ``link_equipment``
resolve ``canonical_slug`` against the canonical weapon / equipment CSVs (same idea
as ``link_hero``).

Use :meth:`Story.remove` to drop this story from ``stories.csv`` and strip its rows
from ``story-*.csv`` junction files (optionally with ``dry_run=True`` to preview).

Paths are resolved relative to the repository root when needed.
"""

from __future__ import annotations

import csv
import json
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
from mdbook_heading_ids import require_valid_lore_fragment  # noqa: E402

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

_STORY_FIELDNAMES: tuple[str, ...] = (
    "StoryId",
    "StoryKey",
    "StoryType",
    "Title",
    "Authors",
    "Illustrators",
    "SourceLink",
    "PublicationDate",
    "ThumbnailImageLink",
    "NarratedVideos",
)

_LOCATION_CSV_FIELDNAMES: tuple[str, ...] = (
    "LocationId",
    "Name",
    "RegionId",
    "Notes",
    "LoreFragment",
)


def _ensure_location_csv_fieldnames_rows(
    fieldnames: list[str], rows: list[dict[str, str]]
) -> tuple[list[str], list[dict[str, str]]]:
    """Ensure ``locations.csv`` dict rows include ``LoreFragment`` and stable column order."""
    std = list(_LOCATION_CSV_FIELDNAMES)
    tail = [c for c in fieldnames if c and c not in std]
    out_fn = std + tail
    for row in rows:
        for c in out_fn:
            row.setdefault(c, "")
    return out_fn, rows


def _normalize_lore_fragment(raw: str) -> str:
    """Strip whitespace and a leading ``#`` from a heading fragment for HTML ``id``."""
    return (raw or "").strip().lstrip("#")


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


def _normalize_story_fieldnames_rows(
    fieldnames: list[str], rows: list[dict[str, str]]
) -> tuple[list[str], list[dict[str, str]]]:
    """Ensure ``stories.csv`` has metadata columns in a stable order."""
    std = list(_STORY_FIELDNAMES)
    tail = [c for c in fieldnames if c and c not in std]
    out_fn = std + tail
    for row in rows:
        for c in out_fn:
            row.setdefault(c, "")
    return out_fn, rows


def _serialize_narrated_videos(narrated_videos: list[dict[str, str]] | None) -> str:
    """Encode narrated video metadata as compact JSON.

    The serialized form is a JSON array of objects with ``author`` and ``url`` keys,
    stored in ``stories.csv`` ``NarratedVideos``.
    """
    if narrated_videos is None:
        return ""
    normalized: list[dict[str, str]] = []
    for entry in narrated_videos:
        author = (entry.get("author") or "").strip()
        url = (entry.get("url") or "").strip()
        if not author or not url:
            raise ValueError(
                "Each narrated video entry must include non-empty 'author' and 'url'."
            )
        normalized.append({"author": author, "url": url})
    return json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))


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
        authors: str = "",
        illustrators: str = "",
        source_link: str = "",
        publication_date: str = "",
        thumbnail_image_link: str = "",
        *,
        narrated_videos: list[dict[str, str]] | None = None,
        run_validate: bool = False,
    ) -> None:
        """Ensure ``stories.csv`` has this story and load junction ids for it.

        Args:
            markdown_path: Path to the ``*.md`` file under ``src/``.
            story_type: First path segment under ``src/`` for this file (e.g. ``main-story``).
                Must match ``validate_data.ALLOWED_STORY_TYPES`` so ``stories.csv`` passes validation.
            title: Human-readable title stored in ``stories.csv``.
            authors: Story author credits (free text; comma-separated suggested).
            illustrators: Illustration credits (free text; comma-separated suggested).
            source_link: Canonical source URL for the story.
            publication_date: Publication date string (e.g. ``2025-07-12``).
            thumbnail_image_link: Public URL for a thumbnail image.
            narrated_videos: Optional list of ``{"author": "...", "url": "..."}`` rows.
            run_validate: If True, run ``validate_data.py`` after updating ``stories.csv``.
        """
        self.story_key = story_key_from_path(markdown_path)
        self.story_type = story_type.strip()
        self.title = title.strip()
        self.authors = authors.strip()
        self.illustrators = illustrators.strip()
        self.source_link = source_link.strip()
        self.publication_date = publication_date.strip()
        self.thumbnail_image_link = thumbnail_image_link.strip()
        self.narrated_videos = _serialize_narrated_videos(narrated_videos)
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
        fieldnames, rows = _normalize_story_fieldnames_rows(fieldnames, rows)
        by_key = {(r.get("StoryKey") or "").strip(): r for r in rows}
        if self.story_key in by_key:
            row = by_key[self.story_key]
            row["StoryType"] = self.story_type
            row["Title"] = self.title
            row["StoryId"] = self.story_id
            row["Authors"] = self.authors
            row["Illustrators"] = self.illustrators
            row["SourceLink"] = self.source_link
            row["PublicationDate"] = self.publication_date
            row["ThumbnailImageLink"] = self.thumbnail_image_link
            row["NarratedVideos"] = self.narrated_videos
        else:
            rows.append(
                {
                    "StoryId": self.story_id,
                    "StoryKey": self.story_key,
                    "StoryType": self.story_type,
                    "Title": self.title,
                    "Authors": self.authors,
                    "Illustrators": self.illustrators,
                    "SourceLink": self.source_link,
                    "PublicationDate": self.publication_date,
                    "ThumbnailImageLink": self.thumbnail_image_link,
                    "NarratedVideos": self.narrated_videos,
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
        for label, junction_file, id_column, registry_path, formatter in (
            self._display_sections()
        ):
            lines.append(label)
            jrows = _junction_rows_for_story(DATA / junction_file, sid, id_column)
            if not jrows:
                lines.append("  (none)")
            else:
                registry = _index_by_column(registry_path, id_column)
                for jr in jrows:
                    eid = (jr.get(id_column) or "").strip()
                    lines.append(f"  • {formatter(registry.get(eid, {}), eid)}")
            lines.append("")
        out.write("\n".join(lines) + "\n")

    def _display_sections(self) -> list[tuple[str, str, str, Path, Any]]:
        """Per-section spec for :meth:`display`: ``(label, junction, id_col, registry, fmt)``."""
        region_by_id = _index_by_column(DATA / "regions.csv", "RegionId")

        def fmt_npc(row: dict[str, str], eid: str) -> str:
            name = (row.get("Name") or eid).strip()
            species = (row.get("Species") or "").strip()
            status = (row.get("Status") or "").strip()
            meta = ", ".join(p for p in (species, status) if p) or "—"
            return f"{name} ({meta})"

        def fmt_canonical(display_col: str) -> Any:
            def _fmt(row: dict[str, str], eid: str) -> str:
                disp = (row.get(display_col) or "").strip() or eid
                slug = (row.get("CanonicalSlug") or "").strip()
                return f"{disp} [{slug}]" if slug else disp

            return _fmt

        def fmt_location(row: dict[str, str], eid: str) -> str:
            name = (row.get("Name") or "").strip() or eid
            rid = (row.get("RegionId") or "").strip()
            rname = (region_by_id.get(rid, {}) or {}).get("RegionName", "").strip()
            region_part = f" — region: {rname} ({rid})" if rid else ""
            notes = (row.get("Notes") or "").strip()
            notes_part = f" — {_trunc(notes, 100)}" if notes else ""
            return f"{name}{region_part}{notes_part}"

        def fmt_named_with_description(row: dict[str, str], eid: str) -> str:
            name = (row.get("Name") or "").strip() or eid
            desc = (row.get("Description") or "").strip()
            return f"{name}: {_trunc(desc)}" if desc else name

        def fmt_food_drink(row: dict[str, str], eid: str) -> str:
            name = (row.get("Name") or "").strip() or eid
            kind = (row.get("Type") or "").strip()
            return f"{name} ({kind})" if kind else name

        return [
            ("NPCs", "story-npcs.csv", "CharacterId", DATA / "npcs.csv", fmt_npc),
            ("Heroes", "story-heroes.csv", "CanonicalId", HEROES_CANONICAL_CSV_PATH, fmt_canonical("CanonicalHero")),
            ("Locations", "story-locations.csv", "LocationId", DATA / "locations.csv", fmt_location),
            ("Monsters", "story-monsters.csv", "MonsterId", DATA / "monsters.csv", fmt_named_with_description),
            ("Fauna", "story-fauna.csv", "FaunaId", DATA / "fauna.csv", fmt_named_with_description),
            ("Flora", "story-flora.csv", "FloraId", DATA / "flora.csv", fmt_named_with_description),
            ("Food & drink", "story-food-drink.csv", "FoodDrinkId", DATA / "food-and-drink.csv", fmt_food_drink),
            ("Weapons", "story-weapons.csv", "CanonicalWeaponId", WEAPONS_CANONICAL_CSV_PATH, fmt_canonical("CanonicalWeapon")),
            ("Equipment", "story-equipment.csv", "CanonicalEquipmentId", EQUIPMENT_CANONICAL_CSV_PATH, fmt_canonical("CanonicalEquipment")),
        ]

    #: Alias for :meth:`display`.
    view = display

    def validate(self) -> list[str]:
        """Run data validation; return the list of alert messages (empty when clean).

        Each alert is also printed to ``stderr`` (``ALERT:`` prefix) for parity
        with running ``validate_data.py`` directly.
        """
        from validate_data import collect_alerts

        alerts = collect_alerts()
        for msg in alerts:
            print(f"ALERT: {msg}", file=sys.stderr)
        return alerts

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
        s_fieldnames, s_rows = _normalize_story_fieldnames_rows(s_fieldnames, s_rows)
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

    def _link_canonical_by_slug(
        self,
        *,
        canonical_slug: str | None,
        canonical_path: Path,
        canonical_id_column: str,
        junction_filename: str,
        links_key: str,
        slug_error_label: str,
    ) -> str:
        """Look up an existing canonical row by ``CanonicalSlug`` and add a junction edge."""
        if not canonical_slug or not canonical_slug.strip():
            raise ValueError("canonical_slug is required")
        slug = canonical_slug.strip()
        _, rows = read_pipe_csv(canonical_path)
        found_id = ""
        for row in rows:
            if (row.get("CanonicalSlug") or "").strip() == slug:
                found_id = (row.get(canonical_id_column) or "").strip()
                break
        if not found_id:
            raise ValueError(f"Unknown {slug_error_label}CanonicalSlug: {slug!r}")
        _merge_junction_link(
            DATA / junction_filename,
            ["StoryId", canonical_id_column],
            canonical_id_column,
            self.story_id,
            found_id,
        )
        self.links[links_key].add(found_id)
        return found_id

    def _upsert_named_registry_link(
        self,
        *,
        entity_id: str,
        name: str,
        extra_column: str,
        extra_value: str,
        registry_filename: str,
        id_column: str,
        junction_filename: str,
        links_key: str,
    ) -> str:
        """Upsert a ``{Id, Name, <extra_column>}`` registry row and add a junction edge."""
        registry_path = DATA / registry_filename
        fieldnames, rows = read_pipe_csv(registry_path)
        if not fieldnames:
            fieldnames = [id_column, "Name", extra_column]
        name_v = name.strip()
        extra_v = extra_value.strip()
        found = False
        for row in rows:
            if (row.get(id_column) or "").strip() == entity_id:
                row["Name"] = name_v
                row[extra_column] = extra_v
                found = True
                break
        if not found:
            rows.append({id_column: entity_id, "Name": name_v, extra_column: extra_v})
        rows.sort(key=lambda r: (r.get("Name") or "").lower())
        write_pipe_csv_autogen(
            registry_path,
            fieldnames,
            rows,
            regenerate_command=REGENERATE_STORY_REGISTRY,
        )
        _merge_junction_link(
            DATA / junction_filename,
            ["StoryId", id_column],
            id_column,
            self.story_id,
            entity_id,
        )
        self.links[links_key].add(entity_id)
        return entity_id

    def link_hero(self, *, canonical_slug: str | None = None) -> str:
        """Link an existing canonical hero by ``CanonicalSlug``. Returns ``CanonicalId``."""
        return self._link_canonical_by_slug(
            canonical_slug=canonical_slug,
            canonical_path=HEROES_CANONICAL_CSV_PATH,
            canonical_id_column="CanonicalId",
            junction_filename="story-heroes.csv",
            links_key="heroes",
            slug_error_label="",
        )

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
        return self._upsert_named_registry_link(
            entity_id=monster_id(name),
            name=name,
            extra_column="Description",
            extra_value=description,
            registry_filename="monsters.csv",
            id_column="MonsterId",
            junction_filename="story-monsters.csv",
            links_key="monsters",
        )

    def link_fauna(self, name: str, description: str = "") -> str:
        """Upsert ``fauna.csv`` and ``story-fauna.csv``."""
        return self._upsert_named_registry_link(
            entity_id=fauna_id_from_name(name),
            name=name,
            extra_column="Description",
            extra_value=description,
            registry_filename="fauna.csv",
            id_column="FaunaId",
            junction_filename="story-fauna.csv",
            links_key="fauna",
        )

    def link_flora(self, name: str, description: str = "") -> str:
        """Upsert ``flora.csv`` and ``story-flora.csv``."""
        return self._upsert_named_registry_link(
            entity_id=flora_id(name),
            name=name,
            extra_column="Description",
            extra_value=description,
            registry_filename="flora.csv",
            id_column="FloraId",
            junction_filename="story-flora.csv",
            links_key="flora",
        )

    def link_food_drink(self, name: str, food_type: str) -> str:
        """Upsert ``food-and-drink.csv`` and ``story-food-drink.csv``."""
        return self._upsert_named_registry_link(
            entity_id=food_drink_id(name, food_type),
            name=name,
            extra_column="Type",
            extra_value=food_type,
            registry_filename="food-and-drink.csv",
            id_column="FoodDrinkId",
            junction_filename="story-food-drink.csv",
            links_key="food_drink",
        )

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
        lore_fragment: str | None = None,
    ) -> str:
        """Upsert ``locations.csv``, optionally ``regions.csv``, and ``story-locations.csv``.

        A location may omit a region (unknown): leave ``region_id`` and ``region_name``
        unset. When the region is known, pass ``region_name`` to upsert ``regions.csv``
        (deterministic ``RegionId`` via :func:`registry_ids.region_row_id`) and set the
        location's ``RegionId``. Pass ``region_id`` alone only if that id already exists
        in ``regions.csv``. If both ``region_id`` and ``region_name`` are set, they must
        agree (``region_id`` must equal ``region_row_id(region_name)``).

        ``LoreFragment`` stores the HTML heading id (no ``#``) on the region's
        ``WorldOfRatheStoryKey`` page—for example ``enion`` for ``### Enion`` in
        ``aria.md``, so Related cards can link to ``aria.md#enion``. Pass
        ``lore_fragment=...`` to set or change it; pass ``lore_fragment=""`` to clear;
        omit the argument to leave the existing value unchanged when updating a row.

        Args:
            name: Location display name.
            region_id: Existing ``RegionId`` when not passing ``region_name``.
            region_name: When set, upserts ``regions.csv`` and defines the location's region.
            world_of_rathe_story_key: Optional ``WorldOfRatheStoryKey`` when upserting by name.
            location_notes: Optional ``Notes`` on ``locations.csv``.
            lore_fragment: Optional heading id for deep links (``None`` = leave as-is).

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

        if lore_fragment is not None:
            frag_chk = _normalize_lore_fragment(lore_fragment)
            if frag_chk:
                require_valid_lore_fragment(
                    src_root=SRC,
                    regions_csv=DATA / "regions.csv",
                    region_id=eff_region,
                    lore_fragment=frag_chk,
                )

        rid = location_id(name, eff_region)
        fieldnames, rows = read_pipe_csv(DATA / "locations.csv")
        fieldnames, rows = _ensure_location_csv_fieldnames_rows(fieldnames, rows)
        found = False
        for row in rows:
            if (row.get("LocationId") or "").strip() == rid:
                row["Name"] = name.strip()
                row["RegionId"] = eff_region
                row["Notes"] = location_notes.strip()
                if lore_fragment is not None:
                    row["LoreFragment"] = _normalize_lore_fragment(lore_fragment)
                found = True
                break
        if not found:
            new_row: dict[str, str] = {
                "LocationId": rid,
                "Name": name.strip(),
                "RegionId": eff_region,
                "Notes": location_notes.strip(),
                "LoreFragment": (
                    _normalize_lore_fragment(lore_fragment)
                    if lore_fragment is not None
                    else ""
                ),
            }
            for c in fieldnames:
                if c not in new_row:
                    new_row[c] = ""
            rows.append(new_row)
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
        return self._link_canonical_by_slug(
            canonical_slug=canonical_slug,
            canonical_path=WEAPONS_CANONICAL_CSV_PATH,
            canonical_id_column="CanonicalWeaponId",
            junction_filename="story-weapons.csv",
            links_key="weapons",
            slug_error_label="weapon ",
        )

    def link_equipment(self, *, canonical_slug: str | None = None) -> str:
        """Link an existing canonical equipment card by ``CanonicalSlug``.

        Returns:
            ``CanonicalEquipmentId`` written to ``story-equipment.csv``.
        """
        return self._link_canonical_by_slug(
            canonical_slug=canonical_slug,
            canonical_path=EQUIPMENT_CANONICAL_CSV_PATH,
            canonical_id_column="CanonicalEquipmentId",
            junction_filename="story-equipment.csv",
            links_key="equipment",
            slug_error_label="equipment ",
        )


def main() -> None:
    """Minimal demo / smoke: ``python3 src/data/story.py`` prints resolved StoryKey."""
    import argparse

    p = argparse.ArgumentParser(description="Resolve StoryKey from a path (debug helper).")
    p.add_argument("markdown_path", help="Path to a .md file under src/")
    args = p.parse_args()
    print(story_key_from_path(args.markdown_path))


if __name__ == "__main__":
    main()
