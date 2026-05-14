#!/usr/bin/env python3
"""One-off migration: extract inline hero links from story markdown files.

For each story file listed in stories.csv:
  1. Find every [text](url) where the url resolves to a hero lore page.
  2. Replace the link with just the text.
  3. Record the (story_id, canonical_id) pair.

Then insert those pairs into story_heroes (INSERT OR IGNORE, so existing
data is preserved) and regenerate story-heroes.csv.

Usage:
    python3 src/data/migrate_hero_links.py           # apply changes
    python3 src/data/migrate_hero_links.py --dry-run # report only
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from hero_overrides import HERO_SLUG_LORE_FILE_OVERRIDES  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402
from db._connection import open_db  # noqa: E402
import db._export as _export  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DATA = SRC / "data"
DB_PATH = DATA / "fablore.db"
CSV_DIR = DATA / "csv"

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def _build_hero_reverse_map() -> dict[str, str]:
    """Return {src-relative-POSIX-path -> canonical_id} for every hero lore file."""
    _, rows = read_pipe_csv(CSV_DIR / "heroes-canonical.csv")
    result: dict[str, str] = {}
    for row in rows:
        cid = (row.get("CanonicalId") or "").strip()
        slug = (row.get("CanonicalSlug") or "").strip()
        if not cid or not slug:
            continue
        # Honour the same overrides that mdbook_related uses.
        override = HERO_SLUG_LORE_FILE_OVERRIDES.get(slug)
        if override:
            candidates = [override]
        else:
            candidates = [
                f"heroes-of-rathe/{slug}-about.md",
                f"heroes-of-rathe/{slug}.md",
            ]
        for candidate in candidates:
            if (SRC / candidate).is_file():
                result[candidate] = cid
                # Also match the .html variant (some old links use .html).
                result[candidate.replace(".md", ".html")] = cid
                break
    return result


def _resolve_link_path(story_key: str, raw_url: str) -> str | None:
    """Resolve a markdown URL relative to a story file into a src-relative POSIX path.

    Returns None for external URLs, bare anchors, or paths that escape src/.
    """
    if raw_url.startswith(("http://", "https://", "~", "#")):
        return None
    url_no_frag = raw_url.split("#")[0]
    if not url_no_frag:
        return None
    story_dir = Path(story_key).parent
    raw_resolved = story_dir / url_no_frag
    # Normalise without hitting the filesystem.
    normalised = Path(os.path.normpath(raw_resolved)).as_posix()
    # Guard against paths that escaped src/.
    if normalised.startswith(".."):
        return None
    return normalised


def _process_file(
    story_key: str,
    story_id: str,
    src_root: Path,
    reverse_map: dict[str, str],
    dry_run: bool,
) -> set[str]:
    """Process one story file; return set of canonical_ids found.

    Modifies the file in place unless dry_run is True.
    """
    file_path = src_root / story_key
    if not file_path.is_file():
        print(f"  SKIP (file not found): {story_key}", file=sys.stderr)
        return set()

    original = file_path.read_text(encoding="utf-8")
    found: set[str] = set()
    replacements: list[tuple[str, str]] = []  # (original_match, replacement_text)

    for m in LINK_RE.finditer(original):
        link_text = m.group(1)
        raw_url = m.group(2)
        src_rel = _resolve_link_path(story_key, raw_url)
        if src_rel is None:
            continue
        canonical_id = reverse_map.get(src_rel)
        if canonical_id is None:
            continue
        found.add(canonical_id)
        replacements.append((m.group(0), link_text))

    if not replacements:
        return found

    updated = original
    for original_match, plain_text in replacements:
        updated = updated.replace(original_match, plain_text, 1)

    if dry_run:
        for original_match, plain_text in replacements:
            print(f"  [{story_key}] would replace: {original_match!r} -> {plain_text!r}")
    else:
        file_path.write_text(updated, encoding="utf-8")

    return found


def main(dry_run: bool = False) -> None:
    reverse_map = _build_hero_reverse_map()
    print(f"Hero lore files indexed: {len(reverse_map)}")

    _, story_rows = read_pipe_csv(CSV_DIR / "stories.csv")
    story_index = {
        (r.get("StoryKey") or "").strip(): (r.get("StoryId") or "").strip()
        for r in story_rows
        if (r.get("StoryKey") or "").strip() and (r.get("StoryId") or "").strip()
    }

    all_pairs: list[tuple[str, str]] = []  # (story_id, canonical_id)
    files_modified = 0

    for story_key, story_id in sorted(story_index.items()):
        found = _process_file(story_key, story_id, SRC, reverse_map, dry_run)
        if found:
            files_modified += 1
            for cid in found:
                all_pairs.append((story_id, cid))

    print(f"\nStory files with hero links: {files_modified}")
    print(f"Total (story, hero) pairs extracted: {len(all_pairs)}")

    if dry_run:
        print("\n[dry-run] No changes written.")
        return

    conn = open_db(DB_PATH)
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO story_heroes (story_id, canonical_id) VALUES (?, ?)",
            all_pairs,
        )
    inserted = conn.execute("SELECT changes()").fetchone()[0]
    print(f"DB rows inserted: {len(all_pairs)} attempted (INSERT OR IGNORE)")

    _export.export_story_junctions(conn, DATA)
    conn.close()
    print(f"Exported story-heroes.csv -> {CSV_DIR / 'story-heroes.csv'}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
