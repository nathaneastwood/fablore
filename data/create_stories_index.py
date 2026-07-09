"""Build the stories spine and empty junction tables (first-run bootstrap).

Scans ``*.md`` files under the lore content roots below ``src/``, UPSERTs each
story into the SQLite database, then exports the DB back to CSV.

``StoryKey`` is the path relative to ``src/`` (POSIX-style): a navigation / file
identity string, not the foreign key in junction tables.

``StoryId`` is deterministic: ``ST`` + 10 hex chars from SHA-256 of ``StoryKey``.
All ``story-*.csv`` rows use ``StoryId`` to reference a story; consumers that join
lore data should use ``StoryId`` and reserve ``StoryKey`` for URLs or labels.
``Title`` is taken from the existing DB row when it differs from the auto-generated
filename-stem title (so manual overrides survive); otherwise it is from the first
Markdown ``#`` H1 in the file, or else title-cased from the filename stem.

Junction CSVs (``story-*.csv``) are regenerated from the DB on every run; their
content is authoritative in the DB, not in the CSV files.

Content roots (each becomes the ``StoryType`` prefix = first path segment):
``archive`` (world-of-rathe archive pages), ``digital-tiles``, ``flavour``,
``equipment``, ``heroes-of-rathe``, ``main-story``, ``other-characters``,
``short-stories``, ``weapons``, ``world-of-rathe``.
"""

from __future__ import annotations

import re
import string
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from registry_ids import story_id as _story_id

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DATA = ROOT / "src/data"

STORY_ROOTS = (
    "archive",
    "digital-tiles",
    "flavour",
    "equipment",
    "heroes-of-rathe",
    "main-story",
    "other-characters",
    "short-stories",
    "weapons",
    "world-of-rathe",
)

_H1_LINE = re.compile(r"^\s*#\s+(.+?)\s*$")


def _strip_heading_anchor(title: str) -> str:
    """Remove trailing mdBook-style ``{#anchor}`` from a heading inner string."""
    return re.sub(r"\s*\{#[^}]+\}\s*$", "", title).strip()


def _strip_wrapping_emphasis(title: str) -> str:
    """Remove a single layer of ``**`` or ``*`` wrapping if it spans the whole title."""
    t = title.strip()
    m = re.fullmatch(r"\*\*(.+)\*\*", t)
    if m:
        return m.group(1).strip()
    m = re.fullmatch(r"\*(.+)\*", t)
    if m:
        return m.group(1).strip()
    return t


def title_from_filename_stem(stem: str) -> str:
    """Title-case a slug stem (hyphens and underscores become spaces).

    Args:
        stem: Filename without extension (e.g. ``a-lost-tome``).

    Returns:
        Human-readable title (e.g. ``A Lost Tome``).
    """
    if not stem:
        return ""
    return string.capwords(stem.replace("-", " ").replace("_", " ").strip())


def first_h1_title_from_markdown(text: str) -> str | None:
    """Return inner text of the first ATX H1 (``# ...``), or None if absent.

    Skips blank lines. Lines starting with ``##`` are ignored (not H1). Strips
    trailing ``{#anchor}`` and simple bold/italic wrappers around the whole title.

    Args:
        text: Full Markdown file body.

    Returns:
        Stripped title string, or ``None`` if no suitable H1 was found.
    """
    for line in text.splitlines()[:400]:
        if not line.strip():
            continue
        m = _H1_LINE.match(line)
        if m:
            inner = _strip_heading_anchor(m.group(1))
            inner = _strip_wrapping_emphasis(inner)
            if inner:
                return inner
            continue
        if line.lstrip().startswith("#"):
            continue
    return None


def infer_story_title(md_path: Path) -> str:
    """Pick a display title from ``md_path`` (H1, else filename stem).

    Args:
        md_path: Absolute or repo-relative path to a Markdown file.

    Returns:
        Non-empty title string.
    """
    stem = md_path.stem
    if not md_path.is_file():
        return title_from_filename_stem(stem)
    try:
        raw = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return title_from_filename_stem(stem)
    h1 = first_h1_title_from_markdown(raw)
    if h1:
        return h1
    return title_from_filename_stem(stem)


def discover_story_keys(
    existing: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Scan ``STORY_ROOTS`` under ``SRC`` for ``*.md`` files.

    Args:
        existing: Map of ``story_key`` → row dict (DB column names, lowercase)
            for stories already in the DB.  Used to preserve manually-entered
            metadata such as ``title``, ``authors``, etc.  Pass ``None`` or ``{}``
            to infer everything fresh from the filesystem.

    Returns:
        Sorted list of row dicts with lowercase keys matching DB column names
        (``story_id``, ``story_key``, ``story_type``, ``title``, ``authors``,
        ``artists``, ``source_link``, ``publication_date``,
        ``thumbnail_image_link``).
    """
    if existing is None:
        existing = {}

    found: set[str] = set()
    for root in STORY_ROOTS:
        base = SRC / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(SRC).as_posix()
            found.add(rel)

    rows: list[dict[str, str]] = []
    for story_key in sorted(found):
        story_type = story_key.split("/", 1)[0]
        old = existing.get(story_key, {})

        preserved_title = (old.get("title") or "").strip()
        auto_stem_title = title_from_filename_stem(Path(story_key).stem)
        if preserved_title and preserved_title != auto_stem_title:
            title = preserved_title
        else:
            title = infer_story_title(SRC / story_key)

        rows.append(
            {
                "story_id": _story_id(story_key),
                "story_key": story_key,
                "story_type": story_type,
                "title": title,
                "authors": old.get("authors", ""),
                "artists": old.get("artists", ""),
                "source_link": old.get("source_link", ""),
                "publication_date": old.get("publication_date", ""),
                "thumbnail_image_link": old.get("thumbnail_image_link", ""),
            }
        )
    return rows


def main() -> None:
    """Scan ``src/`` lore trees, UPSERT into DB, export to CSV.

    Raises:
        FileNotFoundError: If ``src/`` is missing.
    """
    if not SRC.is_dir():
        raise FileNotFoundError(f"Missing src directory: {SRC}")

    from db import Database
    import db._queries as q

    database = Database(DATA / "fablore.db")

    existing = {
        row["story_key"]: dict(row) for row in q.select_all_stories(database.conn)
    }

    rows = discover_story_keys(existing)

    with database.conn:
        for row in rows:
            q.upsert_story(database.conn, **row)

    database.export_to_csv()
    print(f"Upserted {len(rows)} stories into DB and exported to CSV")


if __name__ == "__main__":
    main()
