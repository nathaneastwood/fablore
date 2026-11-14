#!/usr/bin/env python3
"""mdBook preprocessor: generate set/arc hub content on designated hub pages.

Replaces ``<!-- fablore-sets-hub:start --> … <!-- fablore-sets-hub:end -->``
markers on three hub pages:

  flavour/intro.md          → grid of set cards, each linking to its flavour page
  short-stories/README.md   → arc sections listing stories grouped by set
  main-story/the-land-of-rathe.md → arc sections listing stories grouped by set

Reads ``story-arcs.csv`` and ``sets.csv`` for arc metadata (name, release date,
image).  Chapter order follows the book's SUMMARY.md order via a first-pass
traversal of the book sections JSON.
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
    SECTIONS,
    arc_display_name,
    arc_id,
    arc_image,
    arc_raw_date,
    arc_of,
    arc_release_date,
    chapter_path,
    replace_marked_block,
    iter_chapters,
    load_arcs,
    load_sets,
    relative_href,
    run,
)

MARK_START = "<!-- fablore-sets-hub:start -->"
MARK_END = "<!-- fablore-sets-hub:end -->"

# Hub pages this preprocessor handles, keyed by chapter path: every arc section's hub.
_HUB_PAGES = {s.hub_page: s.key for s in SECTIONS if s.has_arcs and s.hub_page}

# Hub pages themselves should not appear in the arc story lists.
_HUB_SKIP = frozenset(_HUB_PAGES)


def _arc_release_date(slug: str, arcs: dict, sets: dict) -> str:
    # The hubs show only the upstream release date; unlike the Sets index
    # (mdbook_set_index) they do not fall back to the arc's SortDate.
    return arc_release_date(slug, arcs, sets, sort_date_fallback=False)


# ---------------------------------------------------------------------------
# Pass 1: collect chapters
# ---------------------------------------------------------------------------

Chapter = dict  # {"name": str, "path": str}


def _collect(
    sections: list,
    flavour: list[Chapter],
    story_arcs: dict[str, OrderedDict[str, list[Chapter]]],
) -> None:
    """Walk book sections and bucket chapters into flavour / main-story / short-stories."""
    for ch in iter_chapters(sections):
        path = chapter_path(ch)
        if not path:
            continue
        if path in _HUB_SKIP:
            continue
        arc = arc_of(path)
        if arc and arc[0] == "flavour":
            # The flavour hub lists pages; each card reads its slug off the path.
            flavour.append({"name": ch.get("name", ""), "path": path})

        elif arc:
            section, slug = arc
            story_arcs[section].setdefault(slug, []).append({"name": ch.get("name", ""), "path": path})

        elif path.startswith("short-stories/") and path.count("/") == 1:
            # Flat page like kassais-diary.md — its own pseudo-arc. Only this hub
            # does this: arc_of, and so the Sets index, put such a page in no arc.
            slug = path.split("/")[1].removesuffix(".md")
            story_arcs["short-stories"].setdefault(slug, []).append({"name": ch.get("name", ""), "path": path})


# ---------------------------------------------------------------------------
# Pass 2: build HTML
# ---------------------------------------------------------------------------


def _card_grid_html(
    hub_src: str,
    chapters: list[Chapter],
    arcs: dict,
    sets: dict,
) -> str:
    """Card grid for the flavour hub — one card per set page."""
    cards: list[str] = []
    for ch in chapters:
        path = ch["path"]
        slug = path.split("/")[-1].removesuffix(".md")
        name = html.escape(ch["name"] or arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = arc_image(slug, arcs)
        href = html.escape(relative_href(hub_src, path))

        img_html = ""
        if image:
            img_html = f'<img src="{html.escape(image)}" alt="" ' f'loading="lazy" width="600" height="337">\n  '

        date_html = f'\n    <span class="sets-hub-card-date">{html.escape(date)}</span>' if date else ""

        cards.append(
            f'<a class="sets-hub-card" href="{href}">\n'
            f"  {img_html}"
            f'  <div class="sets-hub-card-info">\n'
            f'    <span class="sets-hub-card-name">{name}</span>'
            f"{date_html}\n"
            f"  </div>\n"
            f"</a>"
        )

    inner = "\n".join(cards)
    return f'<div class="sets-hub-grid">\n{inner}\n</div>'


def _arc_card_grid_html(
    hub_src: str,
    arc_map: OrderedDict[str, list[Chapter]],
    arcs: dict,
    sets: dict,
) -> str:
    """Card grid for digital-tiles hub — one card per arc, linking to its single page."""
    cards: list[str] = []
    for slug, chapters in sorted(arc_map.items(), key=lambda kv: arc_raw_date(kv[0], arcs, sets)):
        if not chapters:
            continue
        first = chapters[0]
        name = html.escape(arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = arc_image(slug, arcs)
        href = html.escape(relative_href(hub_src, first["path"]))

        img_html = ""
        if image:
            img_html = f'<img src="{html.escape(image)}" alt="" ' f'loading="lazy" width="600" height="337">\n  '

        date_html = f'\n    <span class="sets-hub-card-date">{html.escape(date)}</span>' if date else ""

        cards.append(
            f'<a class="sets-hub-card" href="{href}">\n'
            f"  {img_html}"
            f'  <div class="sets-hub-card-info">\n'
            f'    <span class="sets-hub-card-name">{name}</span>'
            f"{date_html}\n"
            f"  </div>\n"
            f"</a>"
        )

    inner = "\n".join(cards)
    return f'<div class="sets-hub-grid">\n{inner}\n</div>'


def _arc_sections_html(
    hub_src: str,
    arc_map: OrderedDict[str, list[Chapter]],
    arcs: dict,
    sets: dict,
) -> str:
    """Arc sections for main-story / short-stories hub pages."""
    sections: list[str] = []
    for slug, chapters in sorted(arc_map.items(), key=lambda kv: arc_raw_date(kv[0], arcs, sets)):
        name = html.escape(arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = arc_image(slug, arcs)
        anchor = arc_id(slug)

        header_parts = [f'<span class="arc-section-name">{name}</span>']
        if date:
            header_parts.append(f'<span class="arc-section-date">{html.escape(date)}</span>')
        header = "\n    ".join(header_parts)

        img_html = ""
        if image:
            img_html = (
                f'  <img class="arc-section-image" src="{html.escape(image)}" '
                f'alt="" loading="lazy" width="600" height="337">\n'
            )

        story_items: list[str] = []
        for ch in chapters:
            path = ch["path"]
            title = html.escape(ch["name"] or path.split("/")[-1].removesuffix(".md"))
            href = html.escape(relative_href(hub_src, path))
            story_items.append(f'<li><a href="{href}">{title}</a></li>')

        stories_inner = "\n      ".join(story_items)
        sections.append(
            f'<section class="arc-section" id="{anchor}">\n'
            f'  <div class="arc-section-header">\n'
            f"    {header}\n"
            f"  </div>\n"
            f"{img_html}"
            f'  <ul class="arc-story-list">\n'
            f"      {stories_inner}\n"
            f"  </ul>\n"
            f"</section>"
        )

    return "\n\n".join(sections)


def _inject_hub(content: str, inner_html: str) -> str:
    """Replace or insert the sets-hub block (idempotent)."""
    return replace_marked_block(content, MARK_START, MARK_END, inner_html)


# ---------------------------------------------------------------------------
# Main walk
# ---------------------------------------------------------------------------


def _inject_hubs(
    sections: list,
    flavour_chapters: list[Chapter],
    story_arcs: dict[str, OrderedDict],
    arcs: dict,
    sets: dict,
) -> None:
    for ch in iter_chapters(sections):
        path = chapter_path(ch)
        if not path:
            continue
        hub_type = _HUB_PAGES.get(path)
        if hub_type:
            if hub_type == "flavour":
                inner = _card_grid_html(path, flavour_chapters, arcs, sets)
            elif hub_type == "digital-tiles":
                inner = _arc_card_grid_html(path, story_arcs["digital-tiles"], arcs, sets)
            else:
                inner = _arc_sections_html(path, story_arcs[hub_type], arcs, sets)
            ch["content"] = _inject_hub(ch.get("content") or "", inner)


def _process(items: list, src_root: Path) -> None:
    data_dir = src_root / "data"
    arcs = load_arcs(data_dir)
    sets = load_sets(data_dir)

    flavour_chapters: list[Chapter] = []
    story_arcs: dict[str, OrderedDict] = {
        "main-story": OrderedDict(),
        "short-stories": OrderedDict(),
        "digital-tiles": OrderedDict(),
    }

    _collect(items, flavour_chapters, story_arcs)
    _inject_hubs(items, flavour_chapters, story_arcs, arcs, sets)


def main() -> None:
    run(_process)


if __name__ == "__main__":
    main()
