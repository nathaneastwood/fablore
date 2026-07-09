#!/usr/bin/env python3
"""mdBook preprocessor: inject breadcrumb navigation before each chapter heading.

Reads ``story-arcs.csv`` and ``sets.csv`` to resolve arc display names for
arc-grouped sections (main-story, short-stories).  For flat sections the
breadcrumb is two levels: Section › Page.  For arc-grouped sections with a
subfolder it is three levels: Section › Arc › Page.

Breadcrumbs are injected before the first heading and are idempotent.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-breadcrumb:start -->"
MARK_END = "<!-- fablore-breadcrumb:end -->"

# (path_prefix, section_label, hub_src_path, has_arc_subfolders, skip_paths)
_SECTIONS = [
    (
        "main-story/",
        "Main Story",
        "main-story/the-land-of-rathe.md",
        True,
        {"main-story/the-land-of-rathe.md", "main-story/README.md"},
    ),
    (
        "short-stories/",
        "Short Stories",
        "short-stories/index.md",
        True,
        {"short-stories/README.md", "short-stories/index.md"},
    ),
    (
        "flavour/",
        "Flavour Text",
        "flavour/intro.md",
        False,
        {"flavour/intro.md"},
    ),
    (
        "heroes-of-rathe/",
        "Heroes of Rathe",
        "heroes-of-rathe/heroes-of-rathe.md",
        False,
        {
            "heroes-of-rathe/heroes-of-rathe.md",
            "heroes-of-rathe/professions-of-rathe.md",
            "heroes-of-rathe/other.md",
        },
    ),
    (
        "world-of-rathe/",
        "World of Rathe",
        "world-of-rathe/rathe.md",
        False,
        {"world-of-rathe/rathe.md"},
    ),
    (
        "weapons/",
        "Weapons",
        "weapons/armed-to-the-teeth.md",
        False,
        {"weapons/armed-to-the-teeth.md"},
    ),
    (
        "equipment/",
        "Equipment",
        "equipment/in-the-fires-of-the-forge.md",
        False,
        {"equipment/in-the-fires-of-the-forge.md"},
    ),
    (
        "languages/",
        "Languages",
        "languages/intro.md",
        False,
        {"languages/intro.md"},
    ),
    (
        "other-characters/",
        "Other Characters",
        "other-characters/index.md",
        False,
        {"other-characters/README.md", "other-characters/index.md"},
    ),
    (
        "summaries/",
        "Main Story Summaries",
        "summaries/index.md",
        False,
        {"summaries/README.md", "summaries/index.md"},
    ),
    (
        "digital-tiles/",
        "Digital Tiles",
        "digital-tiles/index.md",
        True,
        {"digital-tiles/README.md", "digital-tiles/index.md"},
    ),
]


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
    # Fallback: prettify slug ("02-arcane-rising" → "Arcane Rising")
    name = re.sub(r"^\d+-", "", slug)
    return name.replace("-", " ").title()


def _relative_href(chapter_src: str, target_src: str) -> str:
    return Path(
        os.path.relpath(Path(target_src), start=Path(chapter_src).parent)
    ).as_posix()


def _build_breadcrumb(items: list[tuple[str | None, str]]) -> str:
    """Build the breadcrumb HTML from a list of (href_or_None, label) pairs."""
    lis: list[str] = []
    last = len(items) - 1
    for i, (href, label) in enumerate(items):
        escaped = html.escape(label)
        if i == last:
            lis.append(f'<li><span aria-current="page">{escaped}</span></li>')
        elif href:
            lis.append(f'<li><a href="{html.escape(href)}">{escaped}</a></li>')
        else:
            lis.append(f"<li><span>{escaped}</span></li>")
    inner = "\n    ".join(lis)
    return (
        f"{MARK_START}\n"
        f'<nav class="breadcrumb" aria-label="Breadcrumb">\n'
        f"  <ol>\n    {inner}\n  </ol>\n"
        f"</nav>\n"
        f"{MARK_END}"
    )


def _inject_at_top(content: str, breadcrumb_html: str) -> str:
    # Remove any existing breadcrumb block first (idempotency)
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        content = pre.rstrip("\n") + "\n" + post.lstrip("\n")

    return breadcrumb_html + "\n\n" + content.lstrip("\n")


def _process_chapter(
    ch: dict,
    arcs: dict[str, dict],
    sets: dict[str, dict],
) -> None:
    path_raw = (ch.get("path") or "").strip()
    if not path_raw:
        return
    path = Path(path_raw).as_posix()

    for prefix, label, hub_src, has_arc, skip_set in _SECTIONS:
        if not path.startswith(prefix):
            continue
        if path in skip_set:
            return

        rel = path[len(prefix) :]  # e.g. "02-arcane-rising/cards-on-the-table.md"
        parts = rel.split("/")

        hub_href = _relative_href(path, hub_src)
        items: list[tuple[str | None, str]] = [(hub_href, label)]

        if has_arc and len(parts) >= 2:
            arc_slug = parts[0]
            items.append((None, _arc_display_name(arc_slug, arcs, sets)))

        page_title = (ch.get("name") or "").strip()
        if not page_title:
            page_title = parts[-1].removesuffix(".md").replace("-", " ").title()
        items.append((None, page_title))

        if len(items) > 1:
            ch["content"] = _inject_at_top(
                ch.get("content") or "", _build_breadcrumb(items)
            )
        return


def _walk(sections: list, arcs: dict, sets: dict) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            _process_chapter(ch, arcs, sets)
            _walk(ch.get("sub_items") or [], arcs, sets)


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

    _walk(book.get("items") or [], arcs, sets)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
