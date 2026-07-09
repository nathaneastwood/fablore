#!/usr/bin/env python3
"""mdBook preprocessor: generate the Browse Stories page.

Finds the chapter at ``browse.md`` and replaces the
``<!-- fablore-browse:start --> … <!-- fablore-browse:end -->`` marker block
with an inline ``<script>`` containing the stories index and the filter UI shell.

Lore-reference types (archive, heroes-of-rathe, other-characters, weapons,
equipment) are excluded from the index so the page only shows narrative content.
Stories are sorted newest-first by publication date, then alphabetically.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-browse:start -->"
MARK_END = "<!-- fablore-browse:end -->"

_BROWSE_SRC_PATH = "browse.md"

_TYPE_LABELS: dict[str, str] = {
    "main-story": "Main Story",
    "short-stories": "Short Story",
    "world-of-rathe": "World of Rathe",
    "flavour": "Flavour Text",
    "digital-tiles": "Digital Tile",
}

_SKIP_TYPES: frozenset[str] = frozenset(
    {
        "archive",
        "heroes-of-rathe",
        "other-characters",
        "weapons",
        "equipment",
    }
)


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    _, rs = read_pipe_csv(path)
    return rs


def build_index(data_dir: Path) -> dict:
    """Build the browse index from CSV junction tables."""
    stories_by_id: dict[str, dict] = {}
    for r in _rows(data_dir / "csv" / "stories.csv"):
        sid = (r.get("StoryId") or "").strip()
        key = (r.get("StoryKey") or "").strip()
        stype = (r.get("StoryType") or "").strip()
        title = (r.get("Title") or "").strip()
        date = (r.get("PublicationDate") or "").strip()
        if not sid or not key or stype in _SKIP_TYPES or not title:
            continue
        url = key[:-3] + ".html" if key.endswith(".md") else key
        stories_by_id[sid] = {
            "t": title,
            "u": url,
            "k": stype,
            "h": [],
            "r": [],
            "_d": date,
        }

    hero_name: dict[str, str] = {}
    for r in _rows(data_dir / "csv" / "heroes-canonical.csv"):
        cid = (r.get("CanonicalId") or "").strip()
        name = (r.get("CanonicalHero") or "").strip()
        if cid and name:
            hero_name[cid] = name

    region_name: dict[str, str] = {}
    for r in _rows(data_dir / "csv" / "regions.csv"):
        rid = (r.get("RegionId") or "").strip()
        name = (r.get("RegionName") or "").strip()
        if rid and name:
            region_name[rid] = name

    for r in _rows(data_dir / "csv" / "story-heroes.csv"):
        sid = (r.get("StoryId") or "").strip()
        cid = (r.get("CanonicalId") or "").strip()
        if sid in stories_by_id and cid in hero_name:
            name = hero_name[cid]
            if name not in stories_by_id[sid]["h"]:
                stories_by_id[sid]["h"].append(name)

    for r in _rows(data_dir / "csv" / "story-regions.csv"):
        sid = (r.get("StoryId") or "").strip()
        rid = (r.get("RegionId") or "").strip()
        if sid in stories_by_id and rid in region_name:
            name = region_name[rid]
            if name not in stories_by_id[sid]["r"]:
                stories_by_id[sid]["r"].append(name)

    dated = [s for s in stories_by_id.values() if s["_d"]]
    undated = [s for s in stories_by_id.values() if not s["_d"]]
    dated.sort(key=lambda s: s["_d"], reverse=True)
    undated.sort(key=lambda s: s["t"].lower())
    stories = dated + undated

    for s in stories:
        del s["_d"]

    present_heroes: set[str] = set()
    for s in stories:
        present_heroes.update(s["h"])

    present_regions: set[str] = set()
    for s in stories:
        present_regions.update(s["r"])

    present_types: set[str] = {s["k"] for s in stories}
    types_list = [
        {"k": k, "l": v} for k, v in _TYPE_LABELS.items() if k in present_types
    ]

    return {
        "stories": stories,
        "heroes": sorted(present_heroes),
        "regions": sorted(present_regions),
        "types": types_list,
    }


def build_browse_html(index: dict) -> str:
    data_json = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    return (
        f"<script>window.FABLORE_BROWSE={data_json};</script>\n"
        '<div id="browse-app" class="browse-app">\n'
        '  <div class="browse-filters">\n'
        '    <div class="browse-filter-group">\n'
        '      <span class="browse-filter-label">Type</span>\n'
        '      <div class="browse-pills" id="browse-type-pills"></div>\n'
        "    </div>\n"
        '    <div class="browse-filter-group">\n'
        '      <span class="browse-filter-label">Region</span>\n'
        '      <div class="browse-pills" id="browse-region-pills"></div>\n'
        "    </div>\n"
        '    <div class="browse-filter-group">\n'
        '      <span class="browse-filter-label">Hero</span>\n'
        '      <div class="browse-hero-widget" id="browse-hero-widget">\n'
        '        <div class="browse-hero-field" id="browse-hero-field">\n'
        '          <div class="browse-hero-chips" id="browse-hero-chips"></div>\n'
        '          <input type="text" id="browse-hero-input" class="browse-hero-input"'
        ' placeholder="Search heroes…" autocomplete="off" />\n'
        "        </div>\n"
        '        <ul class="browse-hero-dropdown" id="browse-hero-dropdown" hidden></ul>\n'
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        '  <p id="browse-count" class="browse-count"></p>\n'
        '  <ul id="browse-results" class="browse-results"></ul>\n'
        "</div>"
    )


def inject_into_content(content: str, inner_html: str) -> str:
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
        return pre.rstrip() + "\n\n" + block + post
    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + f"{MARK_START}\n{inner_html}\n{MARK_END}\n"


def walk_and_process(sections: list, index: dict) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path == _BROWSE_SRC_PATH:
                ch["content"] = inject_into_content(
                    ch.get("content") or "",
                    build_browse_html(index),
                )
            walk_and_process(ch.get("sub_items") or [], index)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()
    data_dir = src_root / "data"

    index = build_index(data_dir)

    stories_json = json.dumps(
        [{"t": s["t"], "u": s["u"]} for s in index["stories"]],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    stories_json_path = src_root / "stories.json"
    try:
        existing = stories_json_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    if existing != stories_json:
        stories_json_path.write_text(stories_json, encoding="utf-8")

    walk_and_process(book.get("items") or [], index)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
