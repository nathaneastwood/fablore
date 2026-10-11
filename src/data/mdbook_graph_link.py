#!/usr/bin/env python3
"""mdBook preprocessor: link each page to its own node in the Lore Graph.

Without this the graph is reachable only from the table of contents, so nobody
reading a hero or region page ever finds it. Every chapter that *is* a node in
the graph gets one link:

    <!-- fablore-graph-link:start --> … <!-- fablore-graph-link:end -->

pointing at ``graph.html#<slug>``, which opens the graph with that node selected.
Pages with a story card (``mdbook_story_meta``) get it inline in the card's links
row, at ``GRAPH_SLOT``; any other page gets a line of its own.

Kept separate from ``mdbook_related.py`` on purpose. That preprocessor computes
the same joins for its Related Lore cards, but it is large and load-bearing;
appending one link does not justify editing it. The two can be merged later if
the duplicated CSV reads ever show up in build times.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout. Supports ``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_graph import build_graph, page_graph_targets  # noqa: E402
from mdbook_story_meta import GRAPH_SLOT  # noqa: E402
from mdbook_story_meta import MARK_END as STORY_META_END  # noqa: E402

MARK_START = "<!-- fablore-graph-link:start -->"
MARK_END = "<!-- fablore-graph-link:end -->"

_GRAPH_SRC_PATH = "graph.md"


def relative_graph_href(chapter_src_path: str, slug: str) -> str:
    """Return an href from a chapter to ``graph.html#slug``.

    mdBook renders each chapter at its own depth, so the link has to climb back
    to the book root rather than assume a flat layout.
    """
    depth = len(Path(chapter_src_path).as_posix().split("/")) - 1
    prefix = "../" * depth
    return f"{prefix}graph.html#{slug}"


def build_link_html(chapter_src_path: str, node: dict) -> str:
    """Return the one-line link block for a chapter that has a graph node."""
    href = relative_graph_href(chapter_src_path, node["sl"])
    return (
        '<p class="lore-graph-backlink">'
        f'<a href="{html.escape(href)}">'
        f"See {html.escape(node['n'])} in the Lore Graph</a></p>"
    )


def build_card_link_html(chapter_src_path: str, node: dict) -> str:
    """Return the compact link that sits in the story card's links row."""
    href = relative_graph_href(chapter_src_path, node["sl"])
    return (
        f'<a class="story-card-graph" href="{html.escape(href)}" '
        f'title="See {html.escape(node["n"])} in the Lore Graph">'
        '<i class="fas fa-diagram-project" aria-hidden="true"></i> Lore Graph</a>'
    )


def inject_into_slot(content: str, inner_html: str) -> str:
    """Put the link in the story card's slot, inline with the other links.

    The slot comment stays put and the link follows it, so a rebuild strips
    the old link and finds the slot again.
    """
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        content = pre + post
    return content.replace(GRAPH_SLOT, f"{GRAPH_SLOT}{MARK_START}{inner_html}{MARK_END}", 1)


def inject_into_content(content: str, inner_html: str) -> str:
    """Put the backlink directly beneath the share sheet.

    ``mdbook_story_meta`` renders the metadata card and share buttons in a block
    just under the page's H1, so its end marker is where the link belongs — the
    graph is a way of navigating the archive, and it sits with the other
    navigation rather than buried above Related Lore. Pages with no share sheet
    (``book.toml`` runs this after ``story-meta``, so its absence is real, not a
    matter of ordering) fall back to the end of the page.

    Replaces any previous block, so re-running the build never stacks links up.
    """
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"

    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        content = pre.rstrip("\n") + post

    if STORY_META_END in content:
        head, marker, tail = content.partition(STORY_META_END)
        return f"{head}{marker}\n\n{block}\n\n{tail.lstrip()}"

    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + f"{block}\n"


def walk_and_process(sections: list, targets: dict[str, dict]) -> None:
    """Append the backlink to every chapter that maps to a node."""
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path = (ch.get("path") or "").strip()
        node = targets.get(Path(path).as_posix()) if path else None
        # Never on the graph page itself — it would link to where you already are.
        if node and path != _GRAPH_SRC_PATH:
            content = ch.get("content") or ""
            if GRAPH_SLOT in content:
                ch["content"] = inject_into_slot(content, build_card_link_html(path, node))
            else:
                ch["content"] = inject_into_content(content, build_link_html(path, node))
        walk_and_process(ch.get("sub_items") or [], targets)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()

    graph = build_graph(src_root / "data", src_root)
    walk_and_process(book.get("items") or [], page_graph_targets(graph))

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
