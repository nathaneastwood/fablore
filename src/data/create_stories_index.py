"""Build the stories spine and empty junction tables (first-run bootstrap).

Writes ``stories.csv``: one row per ``*.md`` file under the lore content roots
below ``src/``. ``StoryKey`` is the path relative to ``src/`` (POSIX-style): a
navigation / file identity string, not the foreign key in junction tables.

``StoryId`` is deterministic: ``ST`` + 10 hex chars from SHA-256 of ``StoryKey``.
All ``story-*.csv`` rows use ``StoryId`` to reference a story; consumers that join
lore data should use ``StoryId`` and reserve ``StoryKey`` for URLs or labels.
``Title`` is taken from the existing ``stories.csv`` row when it differs from the
auto-generated filename-stem title (so manual overrides survive); otherwise it is
from the first Markdown ``#`` H1 in the file, or else title-cased from the filename stem.

Junction CSVs (``story-*.csv``) are created **only if they do not already exist**,
with header rows only, so you can fill them manually without the script wiping data.
Re-running this script refreshes ``stories.csv`` from the filesystem scan only.

Content roots (each becomes the ``StoryType`` prefix = first path segment):
``archive`` (world-of-rathe archive pages), ``digital-tiles``, ``flavour``,
``equipment``, ``heroes-of-rathe``, ``main-story``, ``other-characters``,
``short-stories``, ``weapons``, ``world-of-rathe``.
"""

from __future__ import annotations

import csv
import hashlib
import re
import string
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import (
    REGENERATE_CREATE_STORIES_INDEX,
    REGENERATE_STORY_JUNCTIONS,
    auto_gen_banner,
    read_pipe_csv,
    write_pipe_matrix_autogen,
)

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

STORIES_CSV_PATH = DATA / "stories.csv"

JUNCTION_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("story-npcs.csv", ("StoryId", "CharacterId")),
    ("story-heroes.csv", ("StoryId", "CanonicalId")),
    ("story-locations.csv", ("StoryId", "LocationId")),
    ("story-weapons.csv", ("StoryId", "CanonicalWeaponId")),
    ("story-equipment.csv", ("StoryId", "CanonicalEquipmentId")),
    ("story-flora.csv", ("StoryId", "FloraId")),
    ("story-fauna.csv", ("StoryId", "FaunaId")),
    ("story-food-drink.csv", ("StoryId", "FoodDrinkId")),
    ("story-monsters.csv", ("StoryId", "MonsterId")),
)


def story_id(story_key: str) -> str:
    """Compute deterministic ``StoryId`` from ``StoryKey``.

    ``story-*.csv`` rows reference this id, not the path string.

    Args:
        story_key: Path relative to ``src/`` ending in ``.md``.

    Returns:
        String ``ST`` + first 10 hex chars of SHA-256 of UTF-8 ``story_key``.
    """
    digest = hashlib.sha256(story_key.encode("utf-8")).hexdigest()[:10]
    return f"ST{digest}"


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


def load_existing_story_titles(stories_path: Path) -> dict[str, str]:
    """Load non-empty ``Title`` values keyed by ``StoryKey`` from ``stories.csv``.

    Args:
        stories_path: Path to ``stories.csv``.

    Returns:
        Map of story key to title; missing file or columns yields an empty dict.
    """
    if not stories_path.is_file():
        return {}
    fieldnames, rows = read_pipe_csv(stories_path)
    if "StoryKey" not in fieldnames or "Title" not in fieldnames:
        return {}
    out: dict[str, str] = {}
    for row in rows:
        key = (row.get("StoryKey") or "").strip()
        title = (row.get("Title") or "").strip()
        if key and title:
            out[key] = title
    return out


def discover_story_keys() -> list[tuple[str, str, str]]:
    """Scan ``STORY_ROOTS`` under ``src/`` for ``*.md`` files.

    Returns:
        Sorted list of ``(story_key, story_type, title)`` tuples where
        ``story_type`` is the first path segment (root folder name). ``title`` is
        the existing ``Title`` from ``stories.csv`` when it differs from the
        filename-stem placeholder (so hand-curated titles survive); otherwise it is
        inferred from the file's first H1 or the filename stem.
    """
    existing_titles = load_existing_story_titles(STORIES_CSV_PATH)
    found: set[str] = set()
    for root in STORY_ROOTS:
        base = SRC / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(SRC).as_posix()
            found.add(rel)

    rows: list[tuple[str, str, str]] = []
    for story_key in sorted(found):
        story_type = story_key.split("/", 1)[0]
        preserved = existing_titles.get(story_key, "").strip()
        auto_stem_title = title_from_filename_stem(Path(story_key).stem)
        if preserved and preserved != auto_stem_title:
            title = preserved
        else:
            title = infer_story_title(SRC / story_key)
        rows.append((story_key, story_type, title))
    return rows


def write_stories_csv(rows: list[tuple[str, str, str]]) -> None:
    """Overwrite ``stories.csv`` with ids and keys for discovered stories.

    Args:
        rows: Output of :func:`discover_story_keys`.
    """
    out: list[tuple[str, str, str, str]] = []
    for story_key, story_type, title in rows:
        out.append((story_id(story_key), story_key, story_type, title))

    write_pipe_matrix_autogen(
        STORIES_CSV_PATH,
        ["StoryId", "StoryKey", "StoryType", "Title"],
        out,
        regenerate_command=REGENERATE_CREATE_STORIES_INDEX,
    )


def ensure_junction_headers() -> None:
    """Create each ``story-*.csv`` with banner + header only if the file does not exist.

    Does not overwrite populated junction files.
    """
    for filename, fieldnames in JUNCTION_SPECS:
        path = DATA / filename
        if path.exists():
            continue
        with path.open("w", newline="", encoding="utf-8") as f:
            f.write(auto_gen_banner(REGENERATE_STORY_JUNCTIONS))
            w = csv.writer(f, delimiter="|", lineterminator="\n")
            w.writerow(fieldnames)


def main() -> None:
    """Scan ``src/`` lore trees, write ``stories.csv``, seed empty junction files.

    Raises:
        FileNotFoundError: If ``src/`` is missing.
    """
    if not SRC.is_dir():
        raise FileNotFoundError(f"Missing src directory: {SRC}")
    rows = discover_story_keys()
    write_stories_csv(rows)
    ensure_junction_headers()
    print(f"Wrote {len(rows)} rows to {STORIES_CSV_PATH.relative_to(ROOT)}")
    for filename, _ in JUNCTION_SPECS:
        path = DATA / filename
        n_lines = sum(1 for _ in path.open(encoding="utf-8"))
        print(f"  {filename}: {n_lines} line(s)")


if __name__ == "__main__":
    main()
