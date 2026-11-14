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

from mdbook_common import (  # noqa: E402
    SECTIONS,
    arc_display_name,
    arc_of,
    chapter_path,
    iter_chapters,
    load_arcs,
    load_sets,
    normalise_page_path,
    relative_href,
    run,
)

MARK_START = "<!-- fablore-breadcrumb:start -->"
MARK_END = "<!-- fablore-breadcrumb:end -->"

# (path_prefix, section_label, hub_page, arc_crumb, skip_paths), one per section
# with a label. A skip_paths entry may be a glob (fnmatch), e.g. every hero page.
# arc_crumb is off for flavour: arc_of puts its pages in an arc, but the page is
# the arc (its filename), so a middle crumb would repeat the page title.
_TRAILS: tuple[tuple[str, str, str, bool, frozenset[str]], ...] = tuple(
    (
        s.prefix,
        s.label,
        s.hub_page,
        s.has_arcs and not s.arcs_in_filenames,
        frozenset({s.hub_page, *(normalise_page_path(p) for p in s.no_breadcrumb)}),
    )
    for s in SECTIONS
    if s.label and s.hub_page
)


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
    path = chapter_path(ch)
    if not path:
        return

    for prefix, label, hub_src, arc_crumb, skip_set in _TRAILS:
        if not path.startswith(prefix):
            continue
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in skip_set):
            return

        rel = path[len(prefix) :]  # e.g. "02-arcane-rising/cards-on-the-table.md"
        parts = rel.split("/")

        hub_href = relative_href(path, hub_src)
        items: list[tuple[str | None, str]] = [(hub_href, label)]

        arc = arc_of(path) if arc_crumb else None
        if arc:
            items.append((None, arc_display_name(arc[1], arcs, sets)))

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
