#!/usr/bin/env python3
"""One-off migration: extract inline archive/world-of-rathe links from story files.

For each story file listed in stories.csv:
  1. Find every [text](url) where the url resolves to an archive/world-of-rathe page.
  2. Replace the link with just the text.
  3. If the archive segment maps to a known region, record the (story_id, region_id) pair.

Links to unrecognised segments (e.g. 'deathmatch', 'rathe.md') are still stripped
but do not generate a region relationship.

Then insert those pairs into story_regions (INSERT OR IGNORE) and regenerate
story-regions.csv.

Usage:
    python3 src/data/migrate_region_links.py           # apply changes
    python3 src/data/migrate_region_links.py --dry-run # report only
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402
from db._connection import open_db  # noqa: E402
import db._export as _export  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DATA = SRC / "data"
DB_PATH = DATA / "fablore.db"
CSV_DIR = DATA / "csv"

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
ARCHIVE_PREFIX = "archive/world-of-rathe/"


def _build_segment_to_region_id() -> dict[str, str]:
    """Return {archive-folder-segment -> region_id} derived from regions.csv.

    The segment is the basename (without extension) of WorldOfRatheStoryKey,
    which matches the archive/world-of-rathe subfolder name.
    e.g. 'world-of-rathe/volcor.md' -> segment 'volcor' -> RG8e23bdd8e8
    """
    _, rows = read_pipe_csv(CSV_DIR / "regions.csv")
    result: dict[str, str] = {}
    for row in rows:
        rid = (row.get("RegionId") or "").strip()
        wk = (row.get("WorldOfRatheStoryKey") or "").strip()
        if not rid or not wk:
            continue
        segment = Path(wk).stem  # e.g. 'volcor', 'savage-lands', 'pits'
        result[segment] = rid
    return result


def _resolve_link_path(story_key: str, raw_url: str) -> str | None:
    """Resolve a markdown URL to a src-relative POSIX path, or None to skip."""
    if raw_url.startswith(("http://", "https://", "~", "#")):
        return None
    url_no_frag = raw_url.split("#")[0]
    if not url_no_frag:
        return None
    story_dir = Path(story_key).parent
    raw_resolved = story_dir / url_no_frag
    normalised = Path(os.path.normpath(raw_resolved)).as_posix()
    if normalised.startswith(".."):
        return None
    return normalised


def _archive_segment(src_rel_path: str) -> str | None:
    """Return the region folder segment from an archive/world-of-rathe path, or None."""
    if not src_rel_path.startswith(ARCHIVE_PREFIX):
        return None
    rest = src_rel_path[len(ARCHIVE_PREFIX):]
    # rest is either '{segment}/file.md' or 'rathe.md' (top-level file)
    segment = rest.split("/")[0]
    # If it still contains a dot it's a top-level file like 'rathe.md', not a folder.
    if "." in segment:
        return segment.split(".")[0]  # return 'rathe' so callers can log it
    return segment


def _process_file(
    story_key: str,
    story_id: str,
    src_root: Path,
    segment_to_region: dict[str, str],
    dry_run: bool,
) -> set[str]:
    """Process one story file; return set of region_ids found.

    Modifies the file in place unless dry_run is True.
    """
    file_path = src_root / story_key
    if not file_path.is_file():
        print(f"  SKIP (file not found): {story_key}", file=sys.stderr)
        return set()

    original = file_path.read_text(encoding="utf-8")
    found: set[str] = set()
    # (original_match, plain_text, segment)
    replacements: list[tuple[str, str, str]] = []

    for m in LINK_RE.finditer(original):
        link_text = m.group(1)
        raw_url = m.group(2)
        src_rel = _resolve_link_path(story_key, raw_url)
        if src_rel is None:
            continue
        segment = _archive_segment(src_rel)
        if segment is None:
            continue
        region_id = segment_to_region.get(segment)
        if region_id:
            found.add(region_id)
        replacements.append((m.group(0), link_text, segment))

    if not replacements:
        return found

    if dry_run:
        for original_match, plain_text, segment in replacements:
            region_id = segment_to_region.get(segment)
            note = f"region={region_id}" if region_id else f"no region for '{segment}'"
            print(f"  [{story_key}] {original_match!r} -> {plain_text!r}  ({note})")
        return found

    updated = original
    for original_match, plain_text, _ in replacements:
        updated = updated.replace(original_match, plain_text, 1)

    if updated != original:
        file_path.write_text(updated, encoding="utf-8")

    return found


def main(dry_run: bool = False) -> None:
    segment_to_region = _build_segment_to_region_id()
    print(f"Region segments indexed: {len(segment_to_region)}")
    print(f"  {list(segment_to_region.keys())}")

    _, story_rows = read_pipe_csv(CSV_DIR / "stories.csv")
    story_index = {
        (r.get("StoryKey") or "").strip(): (r.get("StoryId") or "").strip()
        for r in story_rows
        if (r.get("StoryKey") or "").strip() and (r.get("StoryId") or "").strip()
    }

    all_pairs: list[tuple[str, str]] = []
    files_modified = 0

    for story_key, story_id in sorted(story_index.items()):
        found = _process_file(story_key, story_id, SRC, segment_to_region, dry_run)
        if found:
            files_modified += 1
            for rid in found:
                all_pairs.append((story_id, rid))

    print(f"\nStory files with region links: {files_modified}")
    print(f"Total (story, region) pairs extracted: {len(all_pairs)}")

    if dry_run:
        print("\n[dry-run] No changes written.")
        return

    conn = open_db(DB_PATH)
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO story_regions (story_id, region_id) VALUES (?, ?)",
            all_pairs,
        )

    _export.export_story_junctions(conn, DATA)
    conn.close()
    print(f"Exported story-regions.csv -> {CSV_DIR / 'story-regions.csv'}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
