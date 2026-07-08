#!/usr/bin/env python3
"""mdBook preprocessor: generate the Sets index page.

Replaces ``<!-- fablore-set-index:start --> … <!-- fablore-set-index:end -->``
markers on ``sets/README.md``.

For each arc with a SetId (a real game set), emits a section containing links
to its content across main-story, flavour, short-stories, and digital-tiles,
ordered by the numeric prefix of the arc slug.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-set-index:start -->"
MARK_END = "<!-- fablore-set-index:end -->"

_INDEX_PAGES = frozenset({"sets/README.md", "sets/index.md"})

_HUB_SKIP = frozenset({
    "sets/README.md",
    "sets/index.md",
    "flavour/intro.md",
    "short-stories/README.md",
    "short-stories/index.md",
    "main-story/the-land-of-rathe.md",
    "digital-tiles/README.md",
    "digital-tiles/index.md",
})

_SECTION_LABELS = {
    "main-story": "Main Story",
    "flavour": "Flavour Text",
    "short-stories": "Short Stories",
    "digital-tiles": "Digital Tiles",
}

_SECTION_ORDER = ("main-story", "flavour", "short-stories", "digital-tiles")

Chapter = dict


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def _load_arcs(data_dir: Path) -> dict[str, dict[str, str]]:
    _, rows = read_pipe_csv(data_dir / "csv" / "story-arcs.csv")
    return {r["Slug"]: r for r in rows if r.get("Slug")}


def _load_sets(data_dir: Path) -> dict[str, dict[str, str]]:
    _, rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    return {r["SetId"]: r for r in rows if r.get("SetId")}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _arc_display_name(slug: str, arcs: dict, sets: dict) -> str:
    arc = arcs.get(slug, {})
    if arc.get("DisplayName"):
        return arc["DisplayName"]
    set_id = arc.get("SetId", "")
    if set_id and set_id in sets:
        return sets[set_id]["SetName"]
    name = re.sub(r"^\d+-", "", slug)
    return name.replace("-", " ").title()


def _arc_release_date(slug: str, arcs: dict, sets: dict) -> str:
    arc = arcs.get(slug, {})
    set_id = arc.get("SetId", "")
    if not set_id or set_id not in sets:
        return ""
    raw = sets[set_id].get("InitialReleaseDate", "")
    if not raw:
        return ""
    try:
        dt = datetime.strptime(raw.split("T")[0], "%Y-%m-%d")
        return f"{dt.day} {dt.strftime('%B %Y')}"
    except ValueError:
        return raw


def _arc_image(slug: str, arcs: dict) -> str:
    return (arcs.get(slug) or {}).get("ImageLink", "")


def _arc_id(slug: str) -> str:
    name = re.sub(r"^\d+-", "", slug)
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")


def _relative_href(from_src: str, to_src: str) -> str:
    return Path(
        os.path.relpath(Path(to_src), start=Path(from_src).parent)
    ).as_posix()


# ---------------------------------------------------------------------------
# Pass 1: collect chapters
# ---------------------------------------------------------------------------

def _collect(
    sections: list,
    content: dict[str, OrderedDict[str, list[Chapter]]],
) -> None:
    for item in sections:
        if not isinstance(item, dict) or "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path_raw = (ch.get("path") or "").strip()
        if path_raw:
            path = Path(path_raw).as_posix()
            if path not in _HUB_SKIP:
                parts = path.split("/")
                section = parts[0]

                if section == "flavour" and len(parts) == 2:
                    slug = parts[1].removesuffix(".md")
                    content["flavour"].setdefault(slug, []).append(
                        {"name": ch.get("name", ""), "path": path}
                    )

                elif section in ("main-story", "short-stories", "digital-tiles") and len(parts) >= 3:
                    arc_slug = parts[1]
                    content[section].setdefault(arc_slug, []).append(
                        {"name": ch.get("name", ""), "path": path}
                    )

        _collect(ch.get("sub_items") or [], content)


# ---------------------------------------------------------------------------
# Pass 2: build HTML
# ---------------------------------------------------------------------------

def _set_index_html(
    hub_src: str,
    content: dict[str, OrderedDict],
    arcs: dict,
    sets: dict,
) -> str:
    all_slugs: set[str] = set()
    for sec_map in content.values():
        all_slugs.update(sec_map.keys())

    def _release_sort_key(slug: str) -> str:
        set_id = arcs.get(slug, {}).get("SetId", "")
        return sets.get(set_id, {}).get("InitialReleaseDate", "") or ""

    arc_slugs = sorted(
        (s for s in all_slugs if arcs.get(s, {}).get("SetId")),
        key=_release_sort_key,
    )

    sections_html: list[str] = []
    for slug in arc_slugs:
        name = html.escape(_arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = _arc_image(slug, arcs)
        anchor = _arc_id(slug)

        img_html = ""
        if image:
            img_html = (
                f'<img class="set-index-image" src="{html.escape(image)}" '
                f'alt="" loading="lazy" width="600" height="337">\n'
            )

        meta_inner = f'<span class="set-index-name">{name}</span>'
        if date:
            meta_inner += f'\n  <span class="set-index-date">{html.escape(date)}</span>'

        header_html = (
            f'<div class="set-index-header">\n'
            f'  {img_html}'
            f'  <div class="set-index-meta">{meta_inner}</div>\n'
            f'</div>\n'
        )

        group_parts: list[str] = []
        for sec in _SECTION_ORDER:
            chapters = content[sec].get(slug, [])
            if not chapters:
                continue
            label = _SECTION_LABELS[sec]
            items = []
            for ch in chapters:
                path = ch["path"]
                title = html.escape(ch["name"] or path.split("/")[-1].removesuffix(".md"))
                href = html.escape(_relative_href(hub_src, path))
                items.append(f'<li><a href="{href}">{title}</a></li>')
            items_inner = "\n        ".join(items)
            group_parts.append(
                f'<div class="set-index-group">\n'
                f'  <span class="set-index-group-label">{label}</span>\n'
                f'  <ul class="arc-story-list">\n'
                f'    {items_inner}\n'
                f'  </ul>\n'
                f'</div>'
            )

        if not group_parts:
            continue

        groups_inner = "\n".join(group_parts)
        sections_html.append(
            f'<section class="set-index-section" id="{anchor}">\n'
            f'{header_html}'
            f'<div class="set-index-links">\n{groups_inner}\n</div>\n'
            f'</section>'
        )

    return "\n\n".join(sections_html)


def _inject_index(content: str, inner_html: str) -> str:
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        return pre.rstrip() + "\n\n" + block + "\n\n" + post.lstrip()
    return content.rstrip() + "\n\n" + block + "\n"


# ---------------------------------------------------------------------------
# Main walk
# ---------------------------------------------------------------------------

def _inject_pages(
    sections: list,
    content: dict[str, OrderedDict],
    arcs: dict,
    sets: dict,
) -> None:
    for item in sections:
        if not isinstance(item, dict) or "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path_raw = (ch.get("path") or "").strip()
        if path_raw:
            path = Path(path_raw).as_posix()
            if path in _INDEX_PAGES:
                inner = _set_index_html(path, content, arcs, sets)
                ch["content"] = _inject_index(ch.get("content") or "", inner)

        _inject_pages(ch.get("sub_items") or [], content, arcs, sets)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    data_dir = (root / src_rel).resolve() / "data"

    arcs = _load_arcs(data_dir)
    sets = _load_sets(data_dir)

    content: dict[str, OrderedDict] = {
        "main-story": OrderedDict(),
        "short-stories": OrderedDict(),
        "flavour": OrderedDict(),
        "digital-tiles": OrderedDict(),
    }

    _collect(book.get("items") or [], content)
    _inject_pages(book.get("items") or [], content, arcs, sets)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
