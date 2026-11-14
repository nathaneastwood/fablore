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
import sys
from collections import OrderedDict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import (  # noqa: E402
    arc_display_name,
    arc_id,
    arc_image,
    arc_raw_date,
    arc_release_date,
    iter_chapters,
    load_arcs,
    load_sets,
    relative_href,
    run,
)

MARK_START = "<!-- fablore-set-index:start -->"
MARK_END = "<!-- fablore-set-index:end -->"

_INDEX_PAGES = frozenset({"sets/README.md", "sets/index.md"})

_HUB_SKIP = frozenset(
    {
        "sets/README.md",
        "sets/index.md",
        "flavour/intro.md",
        "short-stories/README.md",
        "short-stories/index.md",
        "main-story/the-land-of-rathe.md",
        "digital-tiles/README.md",
        "digital-tiles/index.md",
    }
)

_SECTION_LABELS = {
    "main-story": "Main Story",
    "flavour": "Flavour Text",
    "short-stories": "Short Stories",
    "digital-tiles": "Digital Tiles",
}

_SECTION_ORDER = ("main-story", "flavour", "short-stories", "digital-tiles")

Chapter = dict


# ---------------------------------------------------------------------------
# Pass 1: collect chapters
# ---------------------------------------------------------------------------


def _collect(
    sections: list,
    content: dict[str, OrderedDict[str, list[Chapter]]],
) -> None:
    for ch in iter_chapters(sections):
        path_raw = (ch.get("path") or "").strip()
        if not path_raw:
            continue
        path = Path(path_raw).as_posix()
        if path in _HUB_SKIP:
            continue
        parts = path.split("/")
        section = parts[0]

        if section == "flavour" and len(parts) == 2:
            slug = parts[1].removesuffix(".md")
            content["flavour"].setdefault(slug, []).append({"name": ch.get("name", ""), "path": path})

        elif section in ("main-story", "short-stories", "digital-tiles") and len(parts) >= 3:
            arc_slug = parts[1]
            content[section].setdefault(arc_slug, []).append({"name": ch.get("name", ""), "path": path})


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

    # An arc earns a place here once it has either an upstream SetId or a
    # hand-maintained SortDate — the latter covers sets announced but not yet
    # published to the game API, plus recurring product lines that never get
    # a SetId of their own (Armory Decks, Mastery Packs).
    arc_slugs = sorted(
        (s for s in all_slugs if arcs.get(s, {}).get("SetId") or arcs.get(s, {}).get("SortDate")),
        key=lambda slug: arc_raw_date(slug, arcs, sets),
    )

    sections_html: list[str] = []
    for slug in arc_slugs:
        name = html.escape(arc_display_name(slug, arcs, sets))
        date = arc_release_date(slug, arcs, sets, sort_date_fallback=True)
        image = arc_image(slug, arcs)
        anchor = arc_id(slug)

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
            f"  {img_html}"
            f'  <div class="set-index-meta">{meta_inner}</div>\n'
            f"</div>\n"
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
                href = html.escape(relative_href(hub_src, path))
                items.append(f'<li><a href="{href}">{title}</a></li>')
            items_inner = "\n        ".join(items)
            group_parts.append(
                f'<div class="set-index-group">\n'
                f'  <span class="set-index-group-label">{label}</span>\n'
                f'  <ul class="arc-story-list">\n'
                f"    {items_inner}\n"
                f"  </ul>\n"
                f"</div>"
            )

        if not group_parts:
            continue

        groups_inner = "\n".join(group_parts)
        sections_html.append(
            f'<section class="set-index-section" id="{anchor}">\n'
            f"{header_html}"
            f'<div class="set-index-links">\n{groups_inner}\n</div>\n'
            f"</section>"
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
    for ch in iter_chapters(sections):
        path_raw = (ch.get("path") or "").strip()
        path = Path(path_raw).as_posix() if path_raw else ""
        if path in _INDEX_PAGES:
            inner = _set_index_html(path, content, arcs, sets)
            ch["content"] = _inject_index(ch.get("content") or "", inner)


def _process(items: list, src_root: Path) -> None:
    data_dir = src_root / "data"
    arcs = load_arcs(data_dir)
    sets = load_sets(data_dir)

    content: dict[str, OrderedDict] = {
        "main-story": OrderedDict(),
        "short-stories": OrderedDict(),
        "flavour": OrderedDict(),
        "digital-tiles": OrderedDict(),
    }

    _collect(items, content)
    _inject_pages(items, content, arcs, sets)


def main() -> None:
    run(_process)


if __name__ == "__main__":
    main()
