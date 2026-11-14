#!/usr/bin/env python3
"""mdBook preprocessor: inject breadcrumb navigation before each chapter heading.

Reads ``story-arcs.csv`` and ``sets.csv`` to resolve arc display names for
arc-grouped sections (main-story, short-stories).  For flat sections the
breadcrumb is two levels: Section › Page.  For arc-grouped sections with a
subfolder it is three levels: Section › Arc › Page.

Breadcrumbs are injected before the first heading and are idempotent.
"""

from __future__ import annotations

import fnmatch
import html
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import arc_display_name, iter_chapters, load_arcs, load_sets, relative_href, run  # noqa: E402

MARK_START = "<!-- fablore-breadcrumb:start -->"
MARK_END = "<!-- fablore-breadcrumb:end -->"

# (path_prefix, section_label, hub_src_path, has_arc_subfolders, skip_paths)
# A skip_paths entry may be a glob (fnmatch), e.g. every hero page.
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
            # Hero pages open with a full-width banner; a trail above it only crowds it.
            "heroes-of-rathe/*-about.md",
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
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in skip_set):
            return

        rel = path[len(prefix) :]  # e.g. "02-arcane-rising/cards-on-the-table.md"
        parts = rel.split("/")

        hub_href = relative_href(path, hub_src)
        items: list[tuple[str | None, str]] = [(hub_href, label)]

        if has_arc and len(parts) >= 2:
            arc_slug = parts[0]
            items.append((None, arc_display_name(arc_slug, arcs, sets)))

        page_title = (ch.get("name") or "").strip()
        if not page_title:
            page_title = parts[-1].removesuffix(".md").replace("-", " ").title()
        items.append((None, page_title))

        if len(items) > 1:
            ch["content"] = _inject_at_top(ch.get("content") or "", _build_breadcrumb(items))
        return


def _walk(sections: list, arcs: dict, sets: dict) -> None:
    for ch in iter_chapters(sections):
        _process_chapter(ch, arcs, sets)


def main() -> None:
    def process(items: list, src_root: Path) -> None:
        data_dir = src_root / "data"
        _walk(items, load_arcs(data_dir), load_sets(data_dir))

    run(process)


if __name__ == "__main__":
    main()
