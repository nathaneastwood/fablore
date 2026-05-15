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

MARK_START = "<!-- fablore-sets-hub:start -->"
MARK_END = "<!-- fablore-sets-hub:end -->"

# Hub pages this preprocessor handles, keyed by src-relative path.
# mdBook rewrites README.md → index.md in the chapter path field, so both forms are listed.
_HUB_PAGES = {
    "flavour/intro.md": "flavour",
    "short-stories/README.md": "short-stories",
    "short-stories/index.md": "short-stories",
    "main-story/the-land-of-rathe.md": "main-story",
    "digital-tiles/README.md": "digital-tiles",
    "digital-tiles/index.md": "digital-tiles",
}

# Hub pages themselves should not appear in the arc story lists.
_HUB_SKIP = frozenset(_HUB_PAGES)


def _load_arcs(data_dir: Path) -> dict[str, dict[str, str]]:
    _, rows = read_pipe_csv(data_dir / "csv" / "story-arcs.csv")
    return {r["Slug"]: r for r in rows if r.get("Slug")}


def _load_sets(data_dir: Path) -> dict[str, dict[str, str]]:
    _, rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    return {r["SetId"]: r for r in rows if r.get("SetId")}


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
    """Derive an HTML anchor ID from an arc slug."""
    name = re.sub(r"^\d+-", "", slug)
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")


def _relative_href(from_src: str, to_src: str) -> str:
    return Path(
        os.path.relpath(Path(to_src), start=Path(from_src).parent)
    ).as_posix()


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
                    flavour.append({"name": ch.get("name", ""), "path": path})

                elif section in ("main-story", "short-stories", "digital-tiles") and len(parts) >= 3:
                    arc_slug = parts[1]
                    story_arcs[section].setdefault(arc_slug, []).append(
                        {"name": ch.get("name", ""), "path": path}
                    )

                elif section == "short-stories" and len(parts) == 2:
                    # Flat page like kassais-diary.md — its own pseudo-arc
                    slug = parts[1].removesuffix(".md")
                    story_arcs["short-stories"].setdefault(slug, []).append(
                        {"name": ch.get("name", ""), "path": path}
                    )

        _collect(ch.get("sub_items") or [], flavour, story_arcs)


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
        name = html.escape(ch["name"] or _arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = _arc_image(slug, arcs)
        href = html.escape(_relative_href(hub_src, path))

        img_html = ""
        if image:
            img_html = (
                f'<img src="{html.escape(image)}" alt="" '
                f'loading="lazy" width="600" height="337">\n  '
            )

        date_html = (
            f'\n    <span class="sets-hub-card-date">{html.escape(date)}</span>'
            if date
            else ""
        )

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
    for slug, chapters in sorted(arc_map.items()):
        if not chapters:
            continue
        first = chapters[0]
        name = html.escape(_arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = _arc_image(slug, arcs)
        href = html.escape(_relative_href(hub_src, first["path"]))

        img_html = ""
        if image:
            img_html = (
                f'<img src="{html.escape(image)}" alt="" '
                f'loading="lazy" width="600" height="337">\n  '
            )

        date_html = (
            f'\n    <span class="sets-hub-card-date">{html.escape(date)}</span>'
            if date
            else ""
        )

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
    for slug, chapters in sorted(arc_map.items()):
        name = html.escape(_arc_display_name(slug, arcs, sets))
        date = _arc_release_date(slug, arcs, sets)
        image = _arc_image(slug, arcs)
        anchor = _arc_id(slug)

        header_parts = [f'<span class="arc-section-name">{name}</span>']
        if date:
            header_parts.append(
                f'<span class="arc-section-date">{html.escape(date)}</span>'
            )
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
            href = html.escape(_relative_href(hub_src, path))
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
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        return pre.rstrip() + "\n\n" + block + "\n\n" + post.lstrip()
    return content.rstrip() + "\n\n" + block + "\n"


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
    for item in sections:
        if not isinstance(item, dict) or "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path_raw = (ch.get("path") or "").strip()
        if path_raw:
            path = Path(path_raw).as_posix()
            hub_type = _HUB_PAGES.get(path)
            if hub_type:
                if hub_type == "flavour":
                    inner = _card_grid_html(path, flavour_chapters, arcs, sets)
                elif hub_type == "digital-tiles":
                    inner = _arc_card_grid_html(path, story_arcs["digital-tiles"], arcs, sets)
                else:
                    inner = _arc_sections_html(path, story_arcs[hub_type], arcs, sets)
                ch["content"] = _inject_hub(ch.get("content") or "", inner)

        _inject_hubs(
            ch.get("sub_items") or [],
            flavour_chapters,
            story_arcs,
            arcs,
            sets,
        )


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

    flavour_chapters: list[Chapter] = []
    story_arcs: dict[str, OrderedDict] = {
        "main-story": OrderedDict(),
        "short-stories": OrderedDict(),
        "digital-tiles": OrderedDict(),
    }

    _collect(book.get("sections") or [], flavour_chapters, story_arcs)
    _inject_hubs(book.get("sections") or [], flavour_chapters, story_arcs, arcs, sets)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
